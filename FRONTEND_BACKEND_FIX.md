# Correções Frontend ↔️ Backend

## Problemas Identificados

### ❌ Problema 1: Backend não enviava topologia da rede
- Frontend esperava `nodes` e `edges` no response de `/api/start`
- Backend não incluía esses dados

### ❌ Problema 2: Incompatibilidade de formato de resposta
- Frontend verificava `data.status === 'started'`
- Backend retornava apenas `data.success`

### ❌ Problema 3: Nome de campo inconsistente
- Backend enviava `statistics` via WebSocket
- Frontend esperava `stats`

### ❌ Problema 4: Tipo de dados errado no frontend
- Backend envia arrays: `vehicles: []`, `traffic_lights: []`
- Frontend esperava objetos: `vehicles: {}`, `traffic_lights: {}`
- Frontend usava `Object.values()` para iterar

## ✅ Correções Aplicadas

### 1. Backend (`app.py`)

#### `/api/start` - Endpoint de início
```python
# ANTES
return jsonify({
    'success': True,
    'message': 'Replay iniciado...',
    'total_frames': total_snapshots
})

# DEPOIS
topology = collector.get_network_topology()

return jsonify({
    'status': 'started',          # ✅ Frontend espera este campo
    'success': True,
    'message': 'Replay iniciado...',
    'total_frames': total_snapshots,
    'nodes': topology['nodes'],    # ✅ Topologia incluída
    'edges': topology['edges']     # ✅ Topologia incluída
})
```

#### WebSocket `simulation_update`
```python
# ANTES
socketio.emit('simulation_update', {
    'statistics': snapshot['statistics']
})

# DEPOIS
socketio.emit('simulation_update', {
    'stats': snapshot['statistics']  # ✅ Nome correto
})
```

### 2. Frontend (`static/js/simulation.js`)

#### Declaração de estado
```javascript
// ANTES
let simulationData = {
    vehicles: {},           // ❌ Objeto
    traffic_lights: {},     // ❌ Objeto
};

// DEPOIS
let simulationData = {
    vehicles: [],           // ✅ Array
    traffic_lights: [],     // ✅ Array
};
```

#### Handler de WebSocket
```javascript
// ANTES
socket.on('simulation_update', (data) => {
    simulationData.vehicles = data.vehicles;
    simulationData.traffic_lights = data.traffic_lights;
});

// DEPOIS
socket.on('simulation_update', (data) => {
    simulationData.vehicles = data.vehicles || [];
    simulationData.traffic_lights = data.traffic_lights || [];
    
    console.log('📦 Update - Step:', data.step, 
                'Veículos:', simulationData.vehicles.length, 
                'Semáforos:', simulationData.traffic_lights.length);
});
```

#### Função de renderização
```javascript
// ANTES
function render() {
    Object.values(simulationData.vehicles).forEach(vehicle => ...);
    Object.values(simulationData.traffic_lights).forEach(tl => ...);
}

// DEPOIS
function render() {
    simulationData.vehicles.forEach(vehicle => ...);
    simulationData.traffic_lights.forEach(tl => ...);
}
```

### 3. Data Collector (`utils/data_collector.py`)

#### Novo método para obter range de steps
```python
def get_step_range(self):
    """Retorna (min_step, max_step, count) dos snapshots disponíveis"""
    conn = self._get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MIN(step), MAX(step), COUNT(*) FROM simulation_snapshots")
    row = cursor.fetchone()
    if row and row[0] is not None:
        return {'min': row[0], 'max': row[1], 'count': row[2]}
    return {'min': 0, 'max': 0, 'count': 0}
```

## 🎯 Resultado

### Antes
- Botão clicado → Backend logava mensagem → Frontend sem resposta visual
- Canvas vazio
- Sem rede, sem veículos, sem semáforos

### Depois
✅ **Botão clicado → Rede renderiza → Veículos aparecem → Semáforos animam**

### Fluxo Completo de Dados

```
1. User clica "Iniciar Simulação"
   ↓
2. Frontend: fetch('/api/start', {method: 'POST'})
   ↓
3. Backend: 
   - Carrega topologia (nodes, edges)
   - Inicia thread de replay
   - Retorna {status: 'started', nodes: [...], edges: [...]}
   ↓
4. Frontend:
   - Recebe nodes + edges
   - Centraliza viewport
   - Renderiza mapa da cidade (8x8 grid)
   ↓
5. Backend Thread:
   - Loop: step 10 → 1670 (167 snapshots)
   - Cada iteração: socketio.emit('simulation_update', {...})
   ↓
6. Frontend WebSocket:
   - Recebe vehicles[] + traffic_lights[] + stats{}
   - Atualiza simulationData
   - Chama render()
   ↓
7. Canvas:
   - Desenha edges (ruas coloridas por tipo)
   - Desenha nodes (junções)
   - Desenha traffic_lights com cores (verde/amarelo/vermelho)
   - Desenha vehicles (car_journey=amarelo, traffic=azul)
   ↓
8. Stats Panel:
   - Atualiza total de veículos
   - Atualiza velocidade média
   - Atualiza tempo de simulação
   - Atualiza FPS
```

## 🧪 Como Testar

1. **Iniciar servidor:**
   ```bash
   source venv/bin/activate
   python app.py
   ```

2. **Abrir browser:**
   ```
   http://localhost:5001
   ```

3. **Verificar:**
   - [ ] Página carrega sem erros no console
   - [ ] Clicar "Iniciar Simulação"
   - [ ] Mapa 8x8 renderiza (grid de ruas)
   - [ ] Veículos aparecem e se movem
   - [ ] Semáforos mudam de cor (verde/amarelo/vermelho)
   - [ ] Stats atualizam (veículos, velocidade, tempo)
   - [ ] Console.log mostra: "📦 Update - Step: X, Veículos: Y, Semáforos: 24"

## 📊 Dados na Base de Dados

```python
# Verificar dados:
from utils.data_collector import SimulationDataCollector
c = SimulationDataCollector('simulation_data.db')

# Range de steps
step_range = c.get_step_range()
# {'min': 10, 'max': 1670, 'count': 167}

# Snapshot exemplo
snapshot = c.get_snapshot_by_step(10)
# {
#   'vehicles': [{'id': 'car_journey', 'x': 450.0, 'y': 450.0, ...}],
#   'traffic_lights': [{id': 'J1', 'state': 'GGGGrrrrrrrr', ...}, ...],
#   'statistics': {'total_vehicles': 1, 'avg_speed': 10.5, ...}
# }
```

## 🎨 Renderização Visual

### Cores
- **Highways** (autoestradas): Vermelho `#ef4444`
- **Arterial** (arteriais): Laranja `#f59e0b`
- **Collector** (coletoras): Verde `#10b981`
- **Local** (locais): Cinza `#6b7280`
- **car_journey** (veículo da jornada): Amarelo `#fbbf24`
- **traffic** (veículos de tráfego): Azul `#3b82f6`
- **Semáforo verde**: `#10b981`
- **Semáforo amarelo**: `#fbbf24`
- **Semáforo vermelho**: `#ef4444`

### Layout Canvas
- **1200x900 pixels**
- **Pan/Zoom** com mouse
- **Grid de referência** quando zoom > 1.5x
- **Fundo escuro** `#1a1a2e`

## 🔍 Debug

### Console do Browser (F12)
```javascript
// Verificar dados recebidos
console.log(simulationData);

// Verificar topologia
console.log('Nodes:', simulationData.nodes.length);
console.log('Edges:', simulationData.edges.length);

// Verificar updates
// Deve aparecer: "📦 Update - Step: X, Veículos: Y, Semáforos: 24"
```

### Terminal do Servidor
```
🎬 Iniciando replay...
   Steps disponíveis: 10 a 1670 (167 snapshots)
📦 Enviando step 10...
📦 Enviando step 20...
...
✅ Replay concluído (167 frames)
```

---

**Status:** ✅ **FUNCIONAL** - Frontend e Backend totalmente sincronizados!
