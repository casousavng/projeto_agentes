# Sistema de Roteamento Inteligente com Comunicação entre Agentes

## 🎯 Problema Resolvido

**Antes**: O veículo A->B sempre seguia a mesma rota (canto superior esquerdo → canto superior direito → canto inferior direito), ignorando:
- Congestionamento em tempo real
- Estados futuros dos semáforos
- Informações de outros veículos
- Pesos dinâmicos das ruas

**Agora**: O veículo A->B usa **roteamento dinâmico adaptativo** considerando TODOS os fatores em tempo real.

---

## 🚦 Melhorias Implementadas

### 1. **46 Semáforos Espalhados** (antes: 30)
- Cobertura completa do mapa
- Temporizadores únicos e aleatórios para cada semáforo
- Estados iniciais variados (alguns verdes, outros vermelhos)

**Localização**:
- 4 cantos (estratégicos)
- 12 bordas superiores/inferiores
- 12 bordas laterais
- 18 interseções internas

### 2. **Previsão de Estado Futuro de Semáforos**
O veículo journey (A->B) **olha para o futuro** ao calcular rotas!

```python
def predict_traffic_light_state(node_id, steps_ahead=10)
```

**Como funciona**:
- Simula o ciclo do semáforo 10-15 steps à frente
- Se prevê que estará vermelho quando chegar → evita essa rota
- Se prevê que estará verde → prioriza essa rota

**Penalidades ajustadas**:
- Semáforo verde previsto: 1.0x (sem penalidade)
- Semáforo amarelo previsto: 1.3x
- Semáforo vermelho previsto: 2.5x (menor que atual pois pode mudar)

### 3. **Comunicação entre Agentes** 🗣️
Veículos agora **compartilham informações** sobre condições de tráfego!

```python
def report_traffic(vehicle, edge_id, delay)
```

**Sistema de Reportes**:
- Cada veículo reporta o **delay** (tempo de espera) em cada aresta
- Reportes são agregados: `{edge_id: {'delay': total, 'reports_count': N}}`
- **Decay temporal**: Informações antigas perdem 20% de relevância a cada 20 steps
- Outros veículos consultam esses reportes para evitar ruas problemáticas

**Penalidades por Reportes**:
- Delay > 50: penalidade 2.5x
- Delay > 30: penalidade 2.0x
- Delay > 15: penalidade 1.5x
- Delay > 5: penalidade 1.2x
- Delay baixo: sem penalidade

### 4. **Cálculo de Peso Dinâmico Multi-Fatorial**

```python
def get_dynamic_weight(edge_id, is_journey=False, look_ahead_steps=15)
```

**Fatores considerados**:
1. **Peso base da rua** (highway 1.0, main 1.5, secondary 2.5, residential 3.0)
2. **Semáforos** (previsão futura para journey, estado atual para outros)
3. **Congestionamento** (número de veículos na aresta)
4. **Reportes de tráfego** (delays reportados por outros agentes)

**Fórmula**:
```
peso_final = peso_base × penalidade_semaforo × penalidade_congestionamento × penalidade_reportes
```

### 5. **Recálculo Frequente para Veículo A->B**
- **Veículos normais**: 10% de chance de recalcular rota a cada nó
- **Veículo A->B (journey)**: **40% de chance** → reage 4x mais rápido a mudanças!

### 6. **Rastreamento de Desempenho**
Cada veículo rastreia:
- `total_travel_time`: Tempo total de viagem
- `current_edge_id`: Aresta atual (para reportar ao finalizar)
- `waiting_time`: Tempo parado em semáforos

**Console mostra**:
```
Veiculo v0 chegou ao destino! Tempo: 1005 steps
Veiculo v52 recalculou rota! 8 -> 5 nos (economia: 3 nos)
```

---

## 🧠 Algoritmo A* Adaptativo

### **Antes** (Determinístico):
```python
edge_weight = base_weight × semaphore_penalty × congestion_penalty
```

### **Agora** (Multi-Critério):
```python
# Para veículo journey (A->B)
edge_weight = base_weight 
            × predict_semaphore(+15 steps)  # Olhar futuro
            × congestion_penalty            # Tráfego atual
            × traffic_reports_penalty       # Info de outros veículos
```

---

## 📊 Comportamento Esperado

### **Rota Adaptativa**:
1. **Início**: Veículo A->B calcula melhor rota considerando semáforos futuros
2. **Durante viagem**: 
   - A cada nó, 40% chance de recalcular
   - Evita ruas com muitos veículos (comunicação)
   - Desvia de semáforos que prevê estarem vermelhos
3. **Resultado**: Rota pode mudar dinamicamente, **não é sempre a mesma**!

### **Diferença entre Veículos**:
- **Carros normais** (azul): Reagem ao estado atual (10% recálculo)
- **Ambulâncias** (vermelho): Ignoram semáforos, velocidade 80 km/h
- **Veículo A->B** (verde): **Prevê futuro + escuta outros + recalcula 40%**

---

## 🎮 Como Testar

1. **Inicie**: `python live_dynamic_traffic.py`
2. **Pressione S**: Inicia simulação
3. **Observe o veículo verde A->B**:
   - Tamanho maior (16px) com anéis brilhantes
   - Label "A->B" em branco
   - **Procure por mensagens de recálculo** no console

4. **Teste congestionamento**:
   - Pressione **V** várias vezes (spawnar carros)
   - Veja o veículo A->B **desviar** de ruas congestionadas

5. **Verifique estatísticas**:
   - "Congestionado": Número de arestas com 2+ veículos
   - "Semáforos": 46 ativos

---

## 🔍 Logs Importantes

```bash
# Criação do veículo journey
*** Criando veiculo principal A->B (VERDE) ***
Veiculo criado: v0 journey rota: 15 nos

# Recálculo inteligente (mostra economia)
Veiculo v0 recalculou rota! 12 -> 8 nos (economia: 4 nos)

# Chegada com tempo total
Veiculo v0 chegou ao destino! Tempo: 1005 steps
```

---

## 🚀 Vantagens do Sistema

1. **Rotas nunca iguais**: Semáforos aleatórios + congestionamento dinâmico
2. **Reação inteligente**: Prevê semáforos futuros em vez de só reagir
3. **Colaboração**: Veículos compartilham informações de tráfego
4. **Eficiência**: Veículo A->B otimiza tempo total, não só distância
5. **Realismo**: Simula comportamento de GPS moderno (Waze, Google Maps)

---

## 📈 Estatísticas de Simulação

| Métrica | Antes | Agora |
|---------|-------|-------|
| Semáforos | 30 | **46** |
| Recálculo A->B | 30% | **40%** |
| Fatores considerados | 2 | **4** |
| Previsão semáforo | ❌ Não | ✅ Sim (15 steps) |
| Comunicação agentes | ❌ Não | ✅ Sim (reportes) |
| Decay temporal | ❌ Não | ✅ Sim (20% a cada 20 steps) |

---

## 🎯 Conclusão

O veículo A->B agora usa um **sistema de roteamento multi-agente cooperativo** que:
- ✅ Prevê estados futuros (semáforos)
- ✅ Escuta reportes de outros veículos
- ✅ Considera congestionamento em tempo real
- ✅ Recalcula rotas frequentemente (40%)
- ✅ Otimiza tempo total, não só distância

**Resultado**: Rotas variadas e otimizadas em cada simulação!
