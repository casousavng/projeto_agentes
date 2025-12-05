# 🚦 Simulação de Tráfego Multiagente com SPADE

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![SPADE](https://img.shields.io/badge/SPADE-4.1.0-green.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.6.1-orange.svg)

Sistema avançado de simulação de tráfego urbano usando **agentes inteligentes SPADE**, comunicação **XMPP via Prosody** e visualização em tempo real com **Pygame**.

---

## 📋 Visão Geral

Este projeto implementa uma simulação completa de tráfego onde **37 agentes autônomos** interagem em tempo real:

- 🤖 **1 CoordinatorAgent**: Gerencia a rede e coordena comunicação
- 🚧 **1 DisruptorAgent**: Sistema de bloqueio dinâmico de vias
- 🚗 **15 VehicleAgents**: 11 carros + 4 ambulâncias com roteamento inteligente
- 🚦 **20 TrafficLightAgents**: Controle coordenado de 10 intersecções (pares H+V)

### 🎯 Características Principais

✅ **Comunicação XMPP Real**: Todos os agentes comunicam via protocolo XMPP usando servidor Prosody  
✅ **Roteamento A***: Cálculo inteligente de rotas considerando bloqueios, semáforos e tráfego  
✅ **Loop Infinito A→B→A**: Veículos circulam continuamente entre pontos, recalculando rotas dinamicamente  
✅ **Sistema de Disrupção**: Bloqueio aleatório de 3 ruas (6 arestas bidirecionais) via ESPAÇO  
✅ **Prioridade de Ambulâncias**: Veículos de emergência respeitados no tráfego  
✅ **Coordenação de Semáforos**: Pares H+V sincronizados (nunca ambos verdes)  
✅ **Grid 6×6**: 36 nós, 120 arestas direcionais  
✅ **Visualização Pygame**: Interface em tempo real com controles interativos  
✅ **Fullscreen**: Suporte F11 para tela cheia  

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────┐
│    Visualização Pygame              │
│    (live_dynamic_spade.py)          │
│    • Renderização 30 FPS            │
│    • Controles interativos          │
│    • Estatísticas em tempo real     │
└─────────────────────────────────────┘
              ↑ renderiza
┌─────────────────────────────────────┐
│    Agentes SPADE                    │
│    (spade_traffic_agents.py)        │
│    • 1 CoordinatorAgent             │
│    • 1 DisruptorAgent               │
│    • 20 TrafficLightAgents (H+V)    │
│    • 11 VehicleAgents (carros)      │
│    • 4 VehicleAgents (ambulâncias)  │
└─────────────────────────────────────┘
              ↑ comunica via XMPP
┌─────────────────────────────────────┐
│    Prosody XMPP Server              │
│    (Docker container)               │
│    localhost:5222                   │
└─────────────────────────────────────┘
```

---

## 🛠️ Tecnologias

| Tecnologia | Versão | Propósito |
|------------|--------|-----------|
| **Python** | 3.9+ | Linguagem principal |
| **SPADE** | 4.1.0 | Framework multiagente baseado em XMPP |
| **Prosody** | Latest | Servidor XMPP (Docker) |
| **Pygame** | 2.6.1 | Visualização 2D em tempo real |
| **Docker** | Latest | Container para Prosody |

---

## 📁 Estrutura do Projeto

```
projeto_agentes/
│
├── 🎮 live_dynamic_spade.py        # Simulação principal
│
├── 🤖 agents/
│   ├── __init__.py
│   └── spade_traffic_agents.py    # Todos os agentes SPADE
│
├── 🛠️ scripts/
│   ├── setup_prosody.sh           # Configurar Prosody Docker
│   └── register_10_paired_lights.sh # Registrar 20 semáforos
│
├── 📋 requirements.txt            # Dependências Python
├── 📖 README.md                   # Esta documentação
└── 🗂️ venv/                       # Ambiente virtual
```

---

## 🚀 Instalação e Execução

### 1️⃣ Pré-requisitos

- **Python 3.9+**: `python3 --version`
- **Docker Desktop**: `docker --version`

### 2️⃣ Configurar Projeto

```bash
# Clone ou navegue até o diretório
cd projeto_agentes

# Crie e ative ambiente virtual
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Instale dependências
pip install -r requirements.txt
```

### 3️⃣ Configurar Prosody XMPP

```bash
# Tornar script executável
chmod +x scripts/setup_prosody.sh

# Executar configuração (inicia Docker container)
./scripts/setup_prosody.sh
```

Isso irá:
- ✅ Iniciar container Docker com Prosody
- ✅ Configurar servidor XMPP em `localhost:5222`
- ✅ Preparar ambiente para registro de agentes

### 4️⃣ Registrar Agentes XMPP

```bash
# Tornar script executável
chmod +x scripts/register_10_paired_lights.sh

# Registrar TODOS os agentes (37 total)
./scripts/register_10_paired_lights.sh
```

Registra:
- 1 coordinator@localhost
- 1 disruptor@localhost
- 11 vehicle_0@localhost até vehicle_10@localhost
- 4 amb_0@localhost até amb_3@localhost
- 20 semáforos (tl_X_X_h e tl_X_X_v)

### 5️⃣ Executar Simulação

```bash
# ⚠️ IMPORTANTE: SEMPRE ativar venv antes de executar!
source venv/bin/activate

# Executar simulação principal
python live_dynamic_spade.py
```

---

## 🎮 Controles

| Tecla | Ação |
|-------|------|
| **ESPAÇO** | 🚧 Ativar/Desativar disrupção (bloqueia 3 ruas aleatórias) |
| **F11** | 🖥️ Alternar tela cheia |
| **+** / **-** | ⚡ Ajustar velocidade da simulação (2x-5x) |
| **ESC** | 🚪 Sair |

---

## 🎨 Interface Pygame

### Elementos Visuais

```
┌──────────────┬───────────────────────────────────────────┐
│              │                                           │
│  📊 PAINEL   │                                           │
│              │        🗺️ Grid 6×6 (1200×1200px)         │
│  Step: 5432  │                                           │
│  Veículos: 1 │         ━━━━━━━━━━━━━━━━                 │
│              │         ┃  🚗   ┃  🚙   🚑                │
│  🎛️ SPEED    │         ━━━━🔴━━━━━━🟢━━                 │
│  [████████  ]│              ↓   →                        │
│    3.5x      │         ━━━━━━━━━━━━━━━━                 │
│              │         🚧 (via bloqueada)                │
│  👥 AGENTES  │         ━━━━━━━━━━━━━━━━                 │
│  Coord: 1    │                                           │
│  Disruptor:1 │         🟢 Verde  🟡 Amarelo  🔴 Vermelho │
│  Veículos:15 │                                           │
│  Semáf.: 20  │         🟣 Journey  🔵 Carro  🔴 AMB      │
│  TOTAL: 37   │                                           │
│              │                                           │
│  🚧 DISRUPTOR│         ━━━━━━━━━━━━━━━━                 │
│  Status:     │                                           │
│  ● ATIVO     │         Pressione ESPAÇO para            │
│  Ruas: 3     │         ativar/desativar bloqueios       │
│  Arestas: 6  │                                           │
└──────────────┴───────────────────────────────────────────┘
```

### Legenda de Cores

- **Ruas**:
  - 🌑 Cinza = Ruas normais (2 faixas visíveis)
  - 🔴 Vermelho com X = Vias bloqueadas pelo DisruptorAgent

- **Veículos**:
  - 🟣 Roxo = Veículo journey (v0: loop A→B→A)
  - 🔵 Azul = Carros normais (v1-v10)
  - 🔴 Vermelho = Ambulâncias (AMB0-AMB3)

- **Semáforos**:
  - 🟢 Verde = Passe (8 segundos)
  - 🟡 Amarelo = Atenção (2 segundos)
  - 🔴 Vermelho = Pare (8 segundos)

---

## 👥 Tipos de Agentes

### 🎯 CoordinatorAgent
- **JID**: `coordinator@localhost`
- **Função**: Gerencia rede, distribui topologia, coordena comunicação
- **Comunicação**: Responde solicitações de dados da rede

### 🚧 DisruptorAgent
- **JID**: `disruptor@localhost`
- **Função**: Sistema de bloqueio dinâmico de vias
- **Ativação**: Tecla ESPAÇO
- **Comportamento**:
  - Seleciona 3 RUAS aleatórias (evita perímetro)
  - Bloqueia AMBAS as direções (6 arestas total)
  - Broadcast via XMPP para todos os veículos
  - Vias bloqueadas aparecem VERMELHAS com X

### 🚦 TrafficLightAgent
- **20 instâncias**: 10 pares H+V em intersecções
- **Coordenação**: Pares H+V nunca ambos verdes simultaneamente
- **Ciclo**:
  - Verde: 8 segundos
  - Amarelo: 2 segundos
  - Vermelho: 8 segundos
- **Posicionamento**:
  - Horizontal (H): 25px acima do nó
  - Vertical (V): 25px à esquerda do nó
- **Intersecções**: 1_1, 1_4, 4_1, 4_4, 2_2, 2_3, 3_2, 3_3, 1_3, 3_1

### 🚗 VehicleAgent (Carros)
- **11 instâncias**: v0 (journey) + v1-v10 (carros normais)
- **Velocidade**: 240 px/s
- **Comportamento**:
  - **Loop Infinito A→B→A**: Ao chegar ao destino, troca origem/destino e recalcula rota
  - Roteamento A* considerando:
    - Bloqueios de vias (evita arestas bloqueadas)
    - Estado de semáforos (vermelho +200 peso, amarelo +50)
    - Tráfego dinâmico
  - Respeita semáforos:
    - Vermelho: para a 60px
    - Amarelo: para se próximo ou rápido
    - Verde: passa
  - Para para ambulâncias próximas (< 200px)
  - Direção correta: horizontal checa semáforo V, vertical checa H

### 🚑 VehicleAgent (Ambulâncias)
- **4 instâncias**: AMB0-AMB3
- **Velocidade**: 280 px/s (mais rápido)
- **Prioridade**: Veículos normais param quando detectam ambulância próxima
- **Comportamento**: Mesmo loop A→B→A e roteamento A*

---

## 🔄 Fluxo de Comunicação

### Inicialização
```
1. Prosody XMPP inicia (Docker)
2. CoordinatorAgent conecta
3. DisruptorAgent conecta
4. 20 TrafficLightAgents conectam (pares H+V)
5. 15 VehicleAgents conectam
6. Veículos solicitam dados da rede → Coordinator responde
7. Simulação inicia
```

### Disrupção de Vias (ESPAÇO)
```
Usuário pressiona ESPAÇO
    ↓
DisruptorAgent:
    - Seleciona 3 ruas aleatórias
    - Bloqueia 6 arestas (ambas direções)
    - Envia mensagem XMPP → CoordinatorAgent
    ↓
CoordinatorAgent:
    - Atualiza blocked_edges
    - Broadcast → TODOS os VehicleAgents
    ↓
VehicleAgents:
    - Recebem blocked_edges_update
    - Verificam se estão EM via bloqueada
    - Forçam recálculo de rota (A*)
    - Algoritmo A* IGNORA arestas bloqueadas
    ↓
Interface Pygame:
    - Renderiza vias bloqueadas em VERMELHO
    - Desenha X branco no centro das vias
    - Atualiza painel: "Status: ATIVO, Ruas: 3"
```

### Loop A→B→A
```
Veículo chega ao destino B
    ↓
VehicleAgent.MoveBehaviour:
    - Detecta route_index >= len(route)
    - Troca: temp = start_node; start_node = end_node; end_node = temp
    - Recalcula: route = calculate_route_astar(current_node, end_node)
    - Atualiza: route_index = 0, target_node = route[0]
    ↓
Veículo inicia viagem de volta B→A
    ↓
Processo repete infinitamente até fechar aplicação
```

---

## 🧠 Algoritmo A* com Bloqueios

```python
def calculate_route_astar(self, start, goal):
    """A* pathfinding que IGNORA vias bloqueadas"""
    open_set = [(0, start)]
    came_from = {}
    g_score = {start: 0}
    
    while open_set:
        current = heapq.heappop(open_set)[1]
        
        if current == goal:
            return reconstruct_path(came_from, current)
        
        for neighbor, edge_id in self.graph.get(current, []):
            # ✅ VERIFICAÇÃO CRÍTICA: Pular arestas bloqueadas
            if edge_id in self.blocked_edges:
                continue  # Ignora esta via completamente
            
            edge_weight = self.edges[edge_id]['weight']
            
            # Penalizar semáforos vermelhos
            if neighbor in self.traffic_lights:
                if self.traffic_lights[neighbor]['state'] == 'red':
                    edge_weight += 200
            
            tentative_g = g_score[current] + edge_weight
            
            if tentative_g < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score, neighbor))
    
    return []  # Sem rota disponível
```

---

## 🔧 Parâmetros Configuráveis

### Velocidades (agents/spade_traffic_agents.py)
```python
# VehicleAgent.__init__
self.base_speed = 240   # Carros: 240 px/s
self.base_speed = 280   # Ambulâncias: 280 px/s
```

### Ciclos de Semáforos
```python
# TrafficLightAgent.__init__
self.green_time = 8    # 8 segundos verde
self.yellow_time = 2   # 2 segundos amarelo
self.red_time = 8      # 8 segundos vermelho
```

### Número de Bloqueios
```python
# DisruptorAgent.activate_disruption
num_roads_to_block = 3  # 3 ruas = 6 arestas
```

---

## 🐛 Troubleshooting

### Problema: Pygame não abre janela
```bash
# macOS - Instalar suporte SDL
brew install sdl2 sdl2_image sdl2_mixer sdl2_ttf

# Linux - Instalar dependências
sudo apt-get install python3-pygame
```

### Problema: "XMPP connection failed"
```bash
# Verificar se Prosody está rodando
docker ps | grep prosody

# Ver logs do Prosody
docker logs prosody

# Reiniciar Prosody
docker restart prosody
# OU
./scripts/setup_prosody.sh
```

### Problema: Agentes não conectam
```bash
# Re-registrar todos os agentes
./scripts/register_10_paired_lights.sh

# Verificar agentes registrados
docker exec -it prosody prosodyctl list localhost
```

### Erro: "No module named 'spade'"
```bash
# ⚠️ SEMPRE ativar venv PRIMEIRO!
source venv/bin/activate

# Verificar ambiente
which python

# Reinstalar dependências
pip install --upgrade -r requirements.txt
```

### Problema: Sintaxe (f-strings não reconhecidas)
```bash
# ⚠️ REGRA DE OURO: SEMPRE ativar venv ANTES de executar!
source venv/bin/activate

# Verificar Python versão (deve ser 3.9+)
python --version
```

---

## 🧹 Limpeza e Manutenção

### Parar e Remover Prosody
```bash
docker stop prosody
docker rm prosody
```

### Limpar Cache Python
```bash
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

### Reinstalar Tudo
```bash
# Remover ambiente virtual
rm -rf venv/

# Recriar
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Reconfigurar Prosody
./scripts/setup_prosody.sh
./scripts/register_10_paired_lights.sh
```

---

## 📊 Métricas e Estatísticas

A sidebar em tempo real mostra:

- **Step**: Número de frames executados
- **Veículos**: 15 agentes de movimento (11 carros + 4 ambulâncias)
- **Semáforos**: 20 agentes (10 pares H+V)
- **Total Agentes**: 37 (1 coordinator + 1 disruptor + 15 vehicles + 20 lights)
- **Speed**: Multiplicador de velocidade (2.0x a 5.0x)
- **Disruptor**: Status (ATIVO/INATIVO), número de ruas e arestas bloqueadas

---

## 📈 Métricas e Avaliação (CSV)

O sistema coleta métricas automaticamente durante a simulação e exporta arquivos CSV para a pasta `metrics/`.

### Como gerar

```zsh
source venv/bin/activate
python live_dynamic_spade.py

# Ative bloqueios com ESPAÇO e aguarde recálculos
# Após encerrar, inspecione os arquivos:
ls metrics
```

### Arquivos gerados

- `metrics/recalc_latency.csv`: `vehicle_id, latency_ms`
  - Latência entre a receção de `blocked_edges_update` e a conclusão do A*.

- `metrics/route_costs.csv`: `vehicle_id, original_cost, new_cost, detour_factor`
  - Custo total da rota original vs nova e fator de desvio.

- `metrics/semaphore_penalty.csv`: `vehicle_id, base_cost, penalty_cost, penalty_share`
  - Parcela do custo atribuída aos semáforos.

- `metrics/traffic_penalty.csv`: `vehicle_id, base_cost, penalty_cost, penalty_share`
  - Parcela do custo atribuída ao tráfego reportado.

- `metrics/summary.csv`: `metric, value`
  - Agregados: média/p50/p95 de latência; média de detour; médias de shares de penalidades.

### Como funciona

- `VehicleAgent` mede latência após `blocked_edges_update` e custos ao fechar o ciclo A→B→A.
- `calculate_route_astar` separa custo base, penalidades de semáforo e de tráfego.
- `scripts/collect_metrics.py` escreve todos os CSVs e um `summary.csv` com estatísticas.

### Exemplo rápido

```zsh
python scripts/collect_metrics.py
cat metrics/summary.csv
```

### Limpeza

```zsh
rm -f metrics/*.csv
```

---

## 🎓 Conceitos SPADE Implementados

### 1. Agentes Autônomos
Cada agente herda de `spade.agent.Agent` e tem:
- **JID** (Jabber ID): Identificador único no servidor XMPP
- **Password**: Autenticação no Prosody
- **Behaviours**: Comportamentos assíncronos

### 2. Behaviours
- **CyclicBehaviour**: Loop infinito (ex: receber mensagens)
- **PeriodicBehaviour**: Executa a cada X segundos (ex: movimento)
- **OneShotBehaviour**: Executa uma única vez (ex: enviar mensagem)

### 3. Mensagens XMPP
```python
msg = Message(to="coordinator@localhost")
msg.set_metadata("performative", "inform")
msg.body = json.dumps({"type": "blocked_edges_update", "edges": [1,2,3]})
await self.send(msg)
```

### 4. Comunicação Assíncrona
- Todos os agentes recebem mensagens simultaneamente
- Broadcast permite notificar múltiplos agentes
- Sistema distribuído e escalável

---

## 🚀 Comandos Avançados

### Ver Todos os Agentes Registrados
```bash
docker exec -it prosody prosodyctl list localhost
```

### Logs do Prosody em Tempo Real
```bash
docker logs prosody -f
```

### Remover Todos os Agentes (Reset Completo)
```bash
docker exec -it prosody rm -rf /var/lib/prosody/localhost/accounts/*
./scripts/register_10_paired_lights.sh
```

### Executar com Logs Detalhados
```bash
python live_dynamic_spade.py 2>&1 | tee simulation.log
```

---

## 📚 Documentação Técnica

### Arquivos de Agentes

#### `agents/spade_traffic_agents.py` (1194 linhas)
Contém TODAS as classes de agentes:

- **VehicleAgent** (linhas 24-470)
  - `calculate_route_astar()`: A* com bloqueios
  - `is_edge_blocked()`: Verifica se aresta está bloqueada
  - `MoveBehaviour`: Movimento pixel-por-pixel
  - `ReceiveMessagesBehaviour`: Processa mensagens XMPP

- **TrafficLightAgent** (linhas 471-730)
  - `TrafficLightBehaviour`: Ciclo verde→amarelo→vermelho
  - `BroadcastStateBehaviour`: Broadcast estado via XMPP
  - Coordenação H+V com paired_jid

- **CoordinatorAgent** (linhas 731-1000)
  - `ReceiveRequestsBehaviour`: Responde solicitações de rede
  - Mantém blocked_edges centralizado
  - Broadcast de bloqueios para todos os veículos

- **DisruptorAgent** (linhas 1001-1194)
  - `activate_disruption()`: Seleciona 3 ruas
  - Agrupa arestas em pares bidirecionais
  - Filtra ruas do perímetro
  - Envia bloqueios via XMPP

#### `live_dynamic_spade.py` (1157 linhas)
Simulação principal com Pygame:

- Renderização 30 FPS
- Grid 6×6 (36 nós, 120 arestas)
- Sistema de semáforos visuais
- Controles interativos (ESPAÇO, F11, +/-)
- Sidebar com estatísticas
- Visualização de vias bloqueadas

---

## 🎉 Pronto para Usar!

Teste o sistema completo:

1. **Inicie Prosody**: `./scripts/setup_prosody.sh`
2. **Registre agentes**: `./scripts/register_10_paired_lights.sh`
3. **Ative venv**: `source venv/bin/activate` ⚠️ **IMPORTANTE!**
4. **Execute simulação**: `python live_dynamic_spade.py`
5. **Pressione ESPAÇO**: Para ativar bloqueios e ver veículos recalculando rotas
6. **Pressione F11**: Para tela cheia
7. **Use +/-**: Para ajustar velocidade

Divirta-se explorando o sistema multiagente! 🚗💨🚦

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Áreas de interesse:

- 🧠 Novos algoritmos de coordenação de semáforos
- 🚗 Novos tipos de agentes (ônibus, bicicletas, pedestres)
- 📊 Análises estatísticas avançadas
- 🎨 Melhorias na visualização
- 🗺️ Redes maiores ou topologias reais

---

## 📝 Licença

Este projeto é de código aberto para fins educacionais.

---

## ✨ Autor

**André Sousa** - Projeto de Inteligência Artificial

---

**Última atualização**: Dezembro 2025  
**Versão**: 3.0 - Sistema Completo com Loop A→B→A e Disrupção Bidirecional  
**Status**: ✅ Funcional e Documentado
