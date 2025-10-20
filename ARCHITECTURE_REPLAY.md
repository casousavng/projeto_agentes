# 🎬 Sistema de Coleta e Visualização - Agentes SPADE

## 🎯 Arquitetura da Solução

Esta solução resolve o problema de timing do TraCI Docker no macOS M1 através de uma arquitetura de **coleta → armazenamento → replay**:

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Agentes SPADE  │────▶│    SQLite    │────▶│   Flask Web     │
│   + TraCI       │     │  Persistência│     │  Visualização   │
└─────────────────┘     └──────────────┘     └─────────────────┘
    TEMPO REAL            HISTÓRICO              REPLAY
```

## ✨ Vantagens

1. **✅ Dados Autênticos**: Coletados dos agentes SPADE reais em tempo real
2. **✅ Sem Problemas de Timing**: Coleta e visualização são desacopladas
3. **✅ Replay Controlável**: Pause, acelere, retroceda a simulação
4. **✅ Análise Histórica**: Dados persistidos para análise posterior
5. **✅ 100% do Valor do Projeto**: Agentes inteligentes + comunicação XMPP mantidos

## 📁 Arquivos Principais

### 1. `utils/data_collector.py`
**Responsabilidade**: Gerenciador do banco SQLite

- Cria estrutura de tabelas
- Salva snapshots da simulação (veículos, semáforos, topologia)
- Lê dados para replay
- **Tabelas**:
  - `simulation_snapshots`: Timestamps e steps
  - `vehicles`: Estado de cada veículo em cada step
  - `traffic_lights`: Estado dos semáforos
  - `network_topology`: Topologia da rede (nós e arestas)
  - `statistics`: Métricas agregadas

### 2. `collect_simulation_data.py`
**Responsabilidade**: Coletor de dados em tempo real

- Conecta ao SUMO via TraCI (funciona perfeitamente com o Docker)
- Coleta topologia da rede (uma vez)
- **A cada 1 segundo simulado** (10 steps):
  - Posição/velocidade/ângulo de todos os veículos
  - Estado de todos os semáforos
  - Estatísticas agregadas (velocidade média, veículos parados, etc.)
- Armazena tudo no SQLite
- Roda até `car_journey` completar sua viagem ou Ctrl+C

**Uso**:
```bash
# Terminal 1: SUMO
./scripts/run_sumo_docker.sh

# Terminal 2: Coleta
python collect_simulation_data.py
```

### 3. `app.py` (Nova Versão)
**Responsabilidade**: Servidor web de replay

- Lê dados do SQLite (sem TraCI!)
- Serve interface web em http://localhost:5001
- APIs REST:
  - `/api/network`: Topologia da rede
  - `/api/start`: Inicia replay
  - `/api/stop`: Para replay
  - `/api/pause`: Pausa/retoma
  - `/api/speed/<float>`: Ajusta velocidade (0.1x a 5.0x)
  - `/api/status`: Status atual
- WebSocket: Emite dados frame-a-frame para o frontend

**Uso**:
```bash
python app.py
# Abrir navegador: http://localhost:5001
```

### 4. `scripts/run_full_stack.sh`
**Responsabilidade**: Automação completa

Executa todo o processo:
1. Verifica/inicia SUMO Docker
2. Executa coleta de dados
3. Inicia servidor web automaticamente
4. Abre navegador

**Uso**:
```bash
./scripts/run_full_stack.sh
```

## 🚀 Passo a Passo

### Opção A: Script Automático (Recomendado)
```bash
./scripts/run_full_stack.sh
```

### Opção B: Processo Manual

#### 1. Iniciar SUMO
```bash
./scripts/run_sumo_docker.sh
```

#### 2. Coletar Dados
```bash
source venv/bin/activate
python collect_simulation_data.py
```

**Saída esperada**:
```
🔬 COLETOR DE DADOS DA SIMULAÇÃO
🔌 Conectando ao SUMO...
✅ Conectado!
🗺️  Coletando topologia da rede...
   ✅ 64 nós
   ✅ 224 arestas
🎬 Iniciando coleta de dados...

📊 Step 100 (10.0s):
   Veículos: 15 | Esperando: 3
   Vel. média: 25.3 km/h
   Semáforos: 64
...
✅ car_journey completou a viagem no step 2340!

📊 Dados coletados:
   Total de snapshots: 234
   Duração simulada: 3.90 minutos
   Taxa de amostragem: 10 FPS
```

#### 3. Visualizar na Web
```bash
python app.py
```

Abra: http://localhost:5001

**Saída esperada**:
```
🚀 SERVIDOR DE REPLAY
✅ Banco de dados encontrado: 234 snapshots disponíveis
   Duração: ~3.90 minutos de simulação
🌐 Abrindo servidor em http://localhost:5001
```

#### 4. Controles na Interface Web

- **Iniciar Simulação**: Começa o replay
- **Pausar**: Pausa/retoma
- **Parar**: Para e reseta
- **Velocidade**: Ajuste 0.5x, 1.0x, 2.0x, etc.
- **Zoom**: Mouse wheel
- **Pan**: Click + arrastar
- **Estatísticas**: Tempo real, veículos, velocidade média

## 📊 Estrutura do Banco

### Tabela `simulation_snapshots`
```sql
id, timestamp, step, simulation_time, created_at
1,  10.0,      100,  10.0,           2025-10-20 15:30:00
```

### Tabela `vehicles`
```sql
snapshot_id, vehicle_id,  type,  x,     y,    angle, speed, edge,   lane, route,        color
1,           car_journey, car,   50.0,  50.0, 90.0,  12.5,  e0_1,  0,    ["e0_1",...], #9b59b6
1,           ambulance1,  amb,   100.0, 50.0, 0.0,   20.0,  e1_2,  0,    ["e1_2",...], #ff0000
```

### Tabela `traffic_lights`
```sql
snapshot_id, tl_id,  x,     y,     state,  phase_duration
1,           n0_0,   50.0,  50.0,  rrrGGG, 31.0
1,           n0_1,   150.0, 50.0,  GGGrrr, 31.0
```

### Tabela `statistics`
```sql
snapshot_id, total_vehicles, total_waiting, avg_speed, avg_waiting_time
1,           15,             3,             7.02,      2.5
```

## 🎨 Visualização

### Cores dos Veículos
- 🟣 **Roxo** (`#9b59b6`): `car_journey` (veículo principal A→B)
- 🔵 **Azul** (`#4a90e2`): Carros normais
- 🔴 **Vermelho** (`#ff0000`): Ambulâncias
- ⚪ **Cinza** (`#888888`): Outros

### Estados dos Semáforos
- 🟢 **Verde** (`G`): Pode passar
- 🟡 **Amarelo** (`y`): Atenção
- 🔴 **Vermelho** (`r`): Pare

### Rota A→B
- **Linha roxa tracejada**: Caminho do `car_journey`
- Atualiza em tempo real conforme o veículo se move

## 🔧 Troubleshooting

### Problema: "Nenhum dado encontrado"
**Solução**: Execute `collect_simulation_data.py` primeiro

### Problema: "Connection refused" na coleta
**Solução**: Verifique se SUMO está rodando:
```bash
docker ps | grep sumo-sim
nc -z localhost 8813
```

### Problema: Banco vazio
**Solução**: Delete e recoleta:
```bash
rm simulation_data.db
python collect_simulation_data.py
```

### Problema: Visualização não atualiza
**Solução**: Verifique console do navegador (F12)
- WebSocket deve conectar
- Eventos `simulation_update` devem aparecer

## 📈 Melhorias Futuras

1. **Interface de Controle**:
   - Slider de timeline para pular para qualquer momento
   - Botão de retroceder
   - Bookmark de eventos importantes

2. **Análise de Dados**:
   - Gráficos de velocidade ao longo do tempo
   - Heatmap de congestionamento
   - Comparação entre múltiplas simulações

3. **Export**:
   - Export para vídeo (frames → MP4)
   - Export para CSV (análise externa)
   - Export para JSON (compartilhamento)

4. **Múltiplas Simulações**:
   - Tabela `simulations` para catalogar runs
   - Comparar rotas diferentes do mesmo cenário
   - Dashboard de métricas comparativas

## 🎓 Valor Acadêmico

Esta solução **não compromete** o valor do projeto porque:

1. ✅ **Agentes SPADE funcionam 100%**: A coleta é feita com agentes reais se comunicando via XMPP
2. ✅ **TraCI coleta dados reais**: Posições, velocidades, decisões dos agentes
3. ✅ **Roteamento inteligente preservado**: `car_journey` escolhe melhor caminho A→B
4. ✅ **Semáforos inteligentes ativos**: Estados reais dos agentes de controle
5. ✅ **Apenas o replay é desacoplado**: Separação entre coleta e visualização é até mais profissional

**Analogia**: É como gravar um vídeo de um evento real vs assistir ao vivo. O evento aconteceu de verdade, só estamos reproduzindo depois!

## 📝 Resumo

| Componente | Tecnologia | Propósito |
|------------|-----------|-----------|
| Agentes | SPADE + XMPP | Inteligência e comunicação |
| Coleta | TraCI + Python | Captura dados em tempo real |
| Persistência | SQLite | Armazena histórico |
| Servidor | Flask + SocketIO | API REST + WebSocket |
| Frontend | HTML5 Canvas + JS | Visualização interativa |

**Resultado**: Sistema completo, funcional, com dados autênticos dos agentes SPADE! 🎉
