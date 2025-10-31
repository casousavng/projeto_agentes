# 🚦 Simulação de Tráfego Multiagente com SPADE# 🚦 Simulação de Tráfego Multiagente com SPADE# 🚦 Simulação de Tráfego Multiagente com SPADE# 🚦 Simulação de Tráfego Multiagente# 🚦 Simulação de Tráfego Multiagente



Sistema de simulação de tráfego urbano usando agentes inteligentes baseados em XMPP (SPADE framework) com visualização em tempo real via Pygame.



![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)Sistema de simulação de tráfego urbano usando agentes inteligentes baseados em XMPP (SPADE framework) com visualização em tempo real via Pygame.

![SPADE](https://img.shields.io/badge/SPADE-3.3.2-green.svg)

![Pygame](https://img.shields.io/badge/Pygame-2.6.1-orange.svg)



---![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)



## 📋 Índice![SPADE](https://img.shields.io/badge/SPADE-3.3.2-green.svg)

- [Visão Geral](#-visão-geral)

- [Tecnologias](#️-tecnologias)![Pygame](https://img.shields.io/badge/Pygame-2.6.1-orange.svg)![SPADE](https://img.shields.io/badge/SPADE-4.1.0-green.svg)

- [Arquitetura](#️-arquitetura)

- [Instalação](#-instalação)

- [Uso](#-uso)

- [Agentes](#-agentes)---![Pygame](https://img.shields.io/badge/Pygame-2.6.1-orange.svg)Sistema de simulação de tráfego urbano usando agentes inteligentes com **SPADE**, **SUMO** e visualização em **Pygame**.Sistema de simulação de tráfego urbano usando agentes inteligentes com **SPADE**, **SUMO** e **Prosody XMPP**.

- [Funcionalidades](#️-funcionalidades)

- [Estrutura do Projeto](#-estrutura-do-projeto)

- [Troubleshooting](#-troubleshooting)

## 📋 Índice

---

- [Visão Geral](#-visão-geral)

## 🎯 Visão Geral

- [Tecnologias](#️-tecnologias)Sistema de simulação de tráfego urbano usando agentes inteligentes com **SPADE**, **Prosody XMPP** e visualização em **Pygame**.

Este projeto implementa uma simulação completa de tráfego urbano onde:

- **36 agentes SPADE** comunicam via protocolo XMPP (Prosody server)- [Arquitetura](#️-arquitetura)

- **1 veículo Journey** (A→B) otimiza sua rota usando algoritmo A*

- **10 carros normais** circulam continuamente pela rede- [Instalação](#-instalação)

- **4 ambulâncias** têm prioridade absoluta no trânsito

- **20 semáforos coordenados** (10 pares horizontal + vertical)- [Uso](#-uso)

- **1 coordenador** gerencia o sistema

- [Agentes](#-agentes)---![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)## 📋 Visão Geral

### Características Principais

✅ Comunicação real via XMPP (Prosody server no Docker)  - [Funcionalidades](#️-funcionalidades)

✅ Pathfinding inteligente com A* considerando:

  - Pesos das arestas (distância das vias: 80-150)- [Estrutura do Projeto](#-estrutura-do-projeto)

  - Estado dos semáforos (vermelho +200, amarelo +50)

  - Congestionamento reportado por outros veículos  - [Troubleshooting](#-troubleshooting)

✅ Prioridade de ambulâncias (raio de 150px)  

✅ Semáforos coordenados em pares (horizontal + vertical alternam)  ## 📋 Visão Geral![SPADE](https://img.shields.io/badge/SPADE-4.1.0-green.svg)

✅ Visualização em tempo real com Pygame (1100×700px)  

✅ Estatísticas dinâmicas (velocidade, tempo, distância percorrida)  ---



---



## 🛠️ Tecnologias## 🎯 Visão Geral



### CoreEste projeto implementa uma simulação de tráfego onde diferentes tipos de agentes (semáforos, carros e ambulâncias) interagem em um ambiente urbano virtual. Os agentes se comunicam via protocolo XMPP e coordenam suas ações para otimizar o fluxo de tráfego.![Pygame](https://img.shields.io/badge/Pygame-2.6.1-orange.svg)Este projeto implementa uma simulação de tráfego onde diferentes tipos de agentes (semáforos, carros, ambulâncias e pedestres) interagem em um ambiente urbano virtual. Os agentes se comunicam via protocolo XMPP e coordenam suas ações para otimizar o fluxo de tráfego.

- **Python 3.9+** - Linguagem principal

- **SPADE 3.3.2** - Framework de agentes baseado em XMPPEste projeto implementa uma simulação completa de tráfego urbano onde:

- **Pygame 2.6.1** - Interface gráfica e visualização

- **Prosody XMPP** - Servidor de mensagens (via Docker)- **36 agentes SPADE** comunicam via protocolo XMPP (Prosody server)



### Bibliotecas- **1 veículo Journey** (A→B) otimiza sua rota usando algoritmo A*

- `asyncio` - Execução assíncrona dos agentes

- `heapq` - Implementação eficiente do A*- **10 carros normais** circulam continuamente pela rede### 🎯 Características Principais

- `json` - Serialização de mensagens XMPP

- `math` - Cálculos geométricos e distâncias- **4 ambulâncias** têm prioridade absoluta no trânsito



---- **20 semáforos coordenados** (10 pares horizontal + vertical)



## 🏗️ Arquitetura- **1 coordenador** gerencia o sistema



```✅ **36 agentes SPADE** comunicando via XMPP  ---### 🎯 Objetivos

┌─────────────────────────────────────────────────────┐

│           PROSODY XMPP SERVER (Docker)              │### Características Principais

│              localhost:5222                         │

└──────────────────┬──────────────────────────────────┘✅ Comunicação real via XMPP (Prosody server no Docker)  ✅ **20 semáforos coordenados** (10 intersecções × 2 orientações)  

                   │ XMPP Protocol

     ┌─────────────┼─────────────┐✅ Pathfinding inteligente com A* considerando:

     │             │             │

┌────▼─────┐ ┌────▼─────┐ ┌────▼──────┐  - Pesos das arestas (distância das vias: 80-150)✅ **Grid 6×6** com 36 nós e 120 arestas  

│Coordinator│ │ Vehicles │ │  Traffic  │

│  (1x)     │ │  (15x)   │ │ Lights(20)│  - Estado dos semáforos (vermelho +200, amarelo +50)

└───────────┘ └──────────┘ └───────────┘

     │             │             │  - Congestionamento reportado por outros veículos  ✅ **11 veículos + 4 ambulâncias** com roteamento inteligente  

     └─────────────┼─────────────┘

                   │✅ Prioridade de ambulâncias (raio de 150px)  

          ┌────────▼─────────┐

          │  PYGAME RENDER   │✅ Semáforos coordenados em pares (horizontal + vertical alternam)  ✅ **Visualização Pygame** em tempo real  ## 📋 Visão Geral- **Carros**: Encontrar rotas ótimas entre pontos A e B

          │  30 FPS Loop     │

          │  1100×700px      │✅ Visualização em tempo real com Pygame (1100×700px)  

          └──────────────────┘

```✅ Estatísticas dinâmicas (velocidade, tempo, distância percorrida)  ✅ **Ambulâncias com prioridade** (ignoram semáforos)  



### Fluxo de Dados

1. **Agentes SPADE** trocam mensagens JSON via Prosody XMPP

2. **Pygame** consulta estados dos agentes a cada frame (30 FPS)---✅ **Teleportação nas bordas** (circulação livre)  - **Ambulâncias**: Prioridade em modo urgência

3. **Semáforos** fazem broadcast de estados a cada 0.5s

4. **Ambulâncias** fazem broadcast de posições a cada 0.2s (5 Hz)

5. **Veículos** reportam congestionamento ao chegarem em arestas

## 🛠️ Tecnologias

---



## 📦 Instalação

### Core---Este projeto implementa uma simulação completa de tráfego urbano onde:- **Semáforos**: Controle adaptativo de intersecções

### Pré-requisitos

- **Python 3.9+** instalado- **Python 3.9+** - Linguagem principal

- **Docker** instalado e rodando

- **macOS/Linux** (testado em macOS M1 13")- **SPADE 3.3.2** - Framework de agentes baseado em XMPP



### Passo 1: Clonar o repositório- **Pygame 2.6.1** - Interface gráfica e visualização

```bash

git clone <repo-url>- **Prosody XMPP** - Servidor de mensagens (via Docker)## 🏗️ Arquitetura- **Pedestres**: Travessia segura de ruas

cd projeto_agentes

```



### Passo 2: Criar ambiente virtual### Bibliotecas Auxiliares

```bash

python3 -m venv venv- `asyncio` - Execução assíncrona dos agentes

source venv/bin/activate  # macOS/Linux

```- `heapq` - Implementação eficiente do A*```- 🤖 **24 agentes de semáforos** controlam intersecções de forma inteligente



### Passo 3: Instalar dependências- `json` - Serialização de mensagens XMPP

```bash

pip install -r requirements.txt- `math` - Cálculos geométricos e distâncias┌─────────────────────────────────────┐

```



### Passo 4: Iniciar Prosody XMPP Server

```bash---│    Visualização Pygame              │- 🚗 **Veículos autônomos** navegam respeitando sinais e buscando rotas ótimas## 🛠️ Tecnologias

docker run -d --name prosody -p 5222:5222 prosody/prosody

```



### Passo 5: Registrar agentes no Prosody## 🏗️ Arquitetura│    (live_dynamic_spade.py)          │

```bash

chmod +x scripts/register_all_agents.sh

./scripts/register_all_agents.sh

``````└─────────────────────────────────────┘- 💬 **Comunicação XMPP** permite coordenação entre agentes



---┌─────────────────────────────────────────────────────┐



## 🚀 Uso│           PROSODY XMPP SERVER (Docker)              │              ↑ renderiza



### Executar a Simulação│              localhost:5222                         │

```bash

source venv/bin/activate└──────────────────┬──────────────────────────────────┘┌─────────────────────────────────────┐- 🎮 **Visualização Pygame** renderiza a simulação em tempo real- **Python 3.9+**: Linguagem principal

python live_dynamic_spade.py

```                   │ XMPP Protocol



### Controles     ┌─────────────┼─────────────┐│    Agentes SPADE                    │

| Controle | Ação |

|----------|------|     │             │             │

| **ESC** | Fechar simulação |

| **Mouse Wheel** | Rolar sidebar (quando sobre ela) |┌────▼─────┐ ┌────▼─────┐ ┌────▼──────┐│    (spade_traffic_agents.py)        │- 💾 **Dados persistidos** em SQLite para análise posterior- **SPADE**: Framework de agentes multiagente baseado em XMPP

| **Slider** | Ajustar velocidade global (2.0x a 5.0x) |

| **Botões +/-** | Incrementar/decrementar velocidade |│Coordinator│ │ Vehicles │ │  Traffic  │



---│  (1x)     │ │  (15x)   │ │ Lights(20)││    • 1 CoordinatorAgent             │



## 🤖 Agentes└───────────┘ └──────────┘ └───────────┘



### 1. Coordenador (1 agente)     │             │             ││    • 20 TrafficLightAgents (H+V)    │- **Prosody**: Servidor XMPP em Docker

- **ID**: `coordinator@localhost`

- **Password**: `coord123`     └─────────────┼─────────────┘

- **Função**: Gerencia inicialização e distribui dados da rede

                   ││    • 11 VehicleAgents               │

### 2. Semáforos (20 agentes)

- **IDs**: `tl_{row}_{col}_{h|v}@localhost`          ┌────────▼─────────┐

- **Password**: `tl123`

- **Ciclo**: Verde (15s) → Amarelo (3s) → Vermelho (15s)          │  PYGAME RENDER   ││    • 4 AmbulanceAgents              │### 🎯 Características Principais- **SUMO**: Simulador de tráfego urbano

- **Localização**: 10 cruzamentos (1_1, 1_4, 4_1, 4_4, 2_2, 2_3, 3_2, 3_3, 1_3, 3_1)

          │  30 FPS Loop     │

### 3. Veículo Journey (1 agente)

- **ID**: `vehicle_0@localhost`          │  1100×700px      │└─────────────────────────────────────┘

- **Password**: `veh123`

- **Rota**: 0_0 (A) → 4_4 (B)          └──────────────────┘

- **Ícone**: 🔵 (círculo azul, 12px)

```              ↑ comunica via XMPP- **TraCI**: Interface Python para controlar SUMO

### 4. Carros Normais (10 agentes)

- **IDs**: `vehicle_1` a `vehicle_10@localhost`

- **Password**: `veh123`

- **Comportamento**: Circulação contínua### Fluxo de Dados┌─────────────────────────────────────┐

- **Ícone**: ⚪ (círculo branco, 12px)

1. **Agentes SPADE** trocam mensagens JSON via Prosody XMPP

### 5. Ambulâncias (4 agentes)

- **IDs**: `amb_0` a `amb_3@localhost`2. **Pygame** consulta estados dos agentes a cada frame (30 FPS)│    Prosody XMPP Server              │✅ Arquitetura multiagente com SPADE  - **X11**: Interface gráfica (macOS M1)

- **Password**: `amb123`

- **Prioridade**: 150px de raio3. **Semáforos** fazem broadcast de estados a cada 0.5s

- **Ícone**: 🔴 (círculo vermelho, 12px)

- **Velocidade**: 280 px/s (40% mais rápida)4. **Ambulâncias** fazem broadcast de posições a cada 0.2s (5 Hz)│    (Docker container)               │



---5. **Veículos** reportam congestionamento ao chegarem em arestas



## ⚙️ Funcionalidades└─────────────────────────────────────┘✅ Rede urbana 8x8 (64 nós, 112 arestas)  



### Algoritmo A* Inteligente---

```python

# Cálculo do peso dinâmico da aresta:```

edge_weight = base_weight  # 80-150 (tipo de via)

edge_weight += traffic_delay * 5  # Congestionamento## 📦 Instalação

edge_weight += 200 if semaphore == 'red' else 0

edge_weight += 50 if semaphore == 'yellow' else 0✅ Semáforos inteligentes com lógica adaptativa  ## 📁 Estrutura do Projeto

```

### Pré-requisitos

### Tipos de Vias

- **Python 3.9+** instalado---

| Tipo | Peso Base | Velocidade |

|------|-----------|------------|- **Docker** instalado e rodando

| Highway | 80 | 300 px/s |

| Main | 100 | 250 px/s |- **macOS/Linux** (testado em macOS M1 13")✅ Coleta automática de dados  

| Secondary | 120 | 200 px/s |

| Residential | 150 | 150 px/s |



### Prioridade de Ambulâncias### Passo 1: Clonar o repositório## 📁 Estrutura do Projeto

- Veículos param automaticamente a 150px de distância

- Broadcast de posição a cada 0.2 segundos```bash

- Cache com timeout de 1 segundo

git clone <repo-url>✅ Visualização interativa com controles  ```

---

cd projeto_agentes

## 📁 Estrutura do Projeto

``````

```

projeto_agentes/

├── agents/

│   ├── __init__.py### Passo 2: Criar ambiente virtualprojeto_agentes/✅ Replay de simulações sem re-executar  projeto_agentes/

│   └── spade_traffic_agents.py # ⭐ Todos os agentes SPADE

│```bash

├── config/

│   └── __init__.pypython3 -m venv venv│

│

├── scenarios/source venv/bin/activate  # macOS/Linux

│   └── grid_8x8/               # Referência SUMO

│```├── 🎮 live_dynamic_spade.py        # Simulação principal├── agents/                 # Agentes SPADE

├── scripts/

│   ├── register_all_agents.sh  # ⭐ Registra 36 agentes

│   ├── setup_prosody.sh        # Setup completo

│   └── cleanup.sh              # Limpa processos### Passo 3: Instalar dependências│

│

├── utils/```bash

│   └── __init__.py

│pip install -r requirements.txt├── 🤖 agents/---│   ├── base_agent.py      # Classe base para todos os agentes

├── live_dynamic_spade.py       # ⭐ ARQUIVO PRINCIPAL

├── requirements.txt            # ⭐ Dependências```

├── README.md                   # ⭐ Documentação

││   ├── __init__.py

├── test_spade_integration.py  # Teste XMPP

├── test_prosody_direct.py     # Teste Prosody### Passo 4: Iniciar Prosody XMPP Server

├── test_journey.py             # Teste Journey

│```bash│   └── spade_traffic_agents.py    # Todos os agentes SPADE│   ├── traffic_light.py   # Agente semáforo

├── .gitignore

├── .env.exampledocker run -d --name prosody -p 5222:5222 prosody/prosody

└── venv/                       # Não versionado

``````│



---



## 🐛 Troubleshooting### Passo 5: Registrar agentes no Prosody├── 🛠️ scripts/## 🏗️ Arquitetura│   ├── car.py             # Agente carro



### Erro: "Connection refused"```bash

```bash

# Verificar se Prosody está rodandochmod +x scripts/register_all_agents.sh│   ├── setup_prosody.sh           # Configurar Prosody

docker ps | grep prosody

./scripts/register_all_agents.sh

# Reiniciar

docker restart prosody```│   └── register_10_paired_lights.sh # Registrar 20 semáforos│   ├── ambulance.py       # Agente ambulância

```



### Erro: "Agent already registered"

```bash**Ou usar o script setup completo:**│

# Remover container

docker rm -f prosody```bash

docker run -d --name prosody -p 5222:5222 prosody/prosody

./scripts/register_all_agents.shchmod +x scripts/setup_prosody.sh├── 📖 README.md                   # Esta documentação```│   └── pedestrian.py      # Agente pedestre

```

./scripts/setup_prosody.sh

### Erro: "Import 'spade' could not be resolved"

```bash```├── 📚 DOCUMENTATION.md            # Documentação completa consolidada

source venv/bin/activate

pip install --upgrade -r requirements.txt

```

---├── 📋 requirements.txt            # Dependências Python┌─────────────────────────────────────┐├── config/                 # Configurações

---



## 📊 Métricas

## 🚀 Uso├── 🔐 .env.example                # Template de variáveis

### Sidebar Exibe:

```

Simulação:

  Step: 1234### Executar a Simulação└── 🗂️ venv/                       # Ambiente virtual│    Visualização Pygame              │  ← Você está aqui!│   └── simulation_config.py

  Total Veículos: 15

```bash

Veículo Journey A->B:

  Velocidade: 250.0 px/ssource venv/bin/activate```

  Tempo Total: 02:35

  Distância: 847.3python live_dynamic_spade.py



Agentes SPADE:```│    (visualize_pygame.py)            │├── scenarios/              # Cenários SUMO

  Coordenador: 1

  Veículos: 15

  Semáforos: 20

  TOTAL: 36### Controles---

```

| Controle | Ação |

### Sobre a Distância

- **Soma dos pesos das arestas percorridas**|----------|------|└─────────────────────────────────────┘│   └── simple_grid/       # Grid 3x3 com semáforos

- Cada aresta = peso 80-150 (tipo de via)

- Acumula quando completa uma aresta| **ESC** | Fechar simulação |

- Representa o custo da rota A*

| **Mouse Wheel** | Rolar sidebar (quando sobre ela) |## 🚀 Instalação Rápida

---

| **Slider** | Ajustar velocidade global (2.0x a 5.0x) |

## 🔧 Configuração

| **Botões +/-** | Incrementar/decrementar velocidade |              ↑ lê│       ├── network.net.xml

### Velocidade dos Veículos

```python

# live_dynamic_spade.py, linha ~35

ROAD_TYPES = {### Interface### 1️⃣ Pré-requisitos

    'highway': {'speed_limit': 300, 'weight': 80},

    'main': {'speed_limit': 250, 'weight': 100},

    ...

}```┌─────────────────────────────────────┐│       ├── routes.rou.xml

```

┌──────────────────────────────┬──────────────┐

### Ciclo dos Semáforos

```python│                              │  SIDEBAR     │- **Python 3.9+**

# agents/spade_traffic_agents.py

self.green_duration = 15  # segundos│  GRADE 5×5 (130px spacing)   │  (250px)     │

self.yellow_duration = 3

self.red_duration = 15│  ┌────┬────┬────┬────┬────┐  │              │- **Docker Desktop** (para Prosody XMPP)│    SQLite Database                  ││       └── simulation.sumocfg

```

│  │0_0 │0_1 │0_2 │0_3 │0_4 │  │ Estatísticas │

### Raio de Ambulâncias

```python│  ├────┼────┼────┼────┼────┤  │ - Step       │

# agents/spade_traffic_agents.py

if dist_to_ambulance < 150:  # pixels│  │1_0 │1_1 │1_2 │1_3 │1_4 │  │ - Veículos   │

    should_stop = True

```│  ├────┼────┼────┼────┼────┤  │              │```bash│    (simulation_data.db)             │  ← 167 snapshots prontos├── scripts/                # Scripts auxiliares



---│  │2_0 │2_1 │2_2 │2_3 │2_4 │  │ Journey A->B │



## 📝 Licença│  ├────┼────┼────┼────┼────┤  │ - Velocidade │# Verificar versões



Projeto educacional - Sistemas Multiagentes│  │3_0 │3_1 │3_2 │3_3 │3_4 │  │ - Tempo      │



---│  ├────┼────┼────┼────┼────┤  │ - Distância  │python3 --version└─────────────────────────────────────┘│   ├── setup_prosody.sh   # Configurar Prosody



## 👥 Autor│  │4_0 │4_1 │4_2 │4_3 │4_4 │  │              │



**André Sousa**  │  └────┴────┴────┴────┴────┘  │ Agentes SPADE│docker --version

Inteligência Artificial

│                              │ Controles    │

---

│  850×700px                   │ Legenda      │```              ↑ grava│   ├── setup_venv.sh      # Configurar ambiente Python

**Versão:** 2.0 (SPADE + Pygame)  

**Data:** 30 de Outubro de 2025  └──────────────────────────────┴──────────────┘

**Compatibilidade:** macOS M1 13", Linux, Windows

```



---### 2️⃣ Clonar e Configurar┌─────────────────────────────────────┐│   ├── run_simulation.sh  # Executar simulação



## 🤖 Agentes



### 1. Coordenador (1 agente)```bash│    Simulação SPADE + SUMO           ││   └── cleanup.sh         # Limpar recursos

- **ID**: `coordinator@localhost`

- **Password**: `coord123`# Clone o repositório

- **Função**: Gerencia inicialização do sistema

- **Comunicação**: Distribui dados da rede para todos os agentesgit clone <repo-url>│    (test_journey.py)                │  ← Agentes inteligentes├── utils/                  # Utilitários



### 2. Semáforos (20 agentes)cd projeto_agentes

- **IDs**: `tl_{row}_{col}_{h|v}@localhost`

- **Password**: `tl123`└─────────────────────────────────────┘│   ├── routing.py         # Otimização de rotas

- **Tipos**: 10 pares (horizontal + vertical)

- **Ciclo**: Verde (15s) → Amarelo (3s) → Vermelho (15s)# Criar e ativar ambiente virtual

- **Coordenação**: Pares alternados sincronizados

python3 -m venv venv              ↑ comunica│   └── xmpp_manager.py    # Gerenciamento de agentes XMPP

**Localização dos 10 cruzamentos:**

- Cantos: `1_1`, `1_4`, `4_1`, `4_4`source venv/bin/activate  # macOS/Linux

- Internos: `2_2`, `2_3`, `3_2`, `3_3`, `1_3`, `3_1`

# venv\Scripts\activate   # Windows┌─────────────────────────────────────┐├── main.py                 # Simulador principal

### 3. Veículo Journey (1 agente)

- **ID**: `vehicle_0@localhost` (v0)

- **Password**: `veh123`

- **Rota**: `0_0` (A) → `4_4` (B)# Instalar dependências│    Prosody XMPP Server              │├── requirements.txt        # Dependências Python

- **Comportamento**: Para ao chegar no destino

- **Ícone**: 🔵 (círculo azul, 12px)pip install -r requirements.txt

- **Estatísticas**:

  - Velocidade atual (px/s)```│    (Docker container)               │  ← Mensagens entre agentes├── .env.example           # Template de variáveis de ambiente

  - Tempo total (mm:ss)

  - Distância = soma dos pesos das arestas percorridas



### 4. Carros Normais (10 agentes)### 3️⃣ Configurar Prosody XMPP└─────────────────────────────────────┘└── README.md              # Esta documentação

- **IDs**: `vehicle_1` a `vehicle_10@localhost`

- **Password**: `veh123`

- **Comportamento**: Circulação contínua, novo destino aleatório

- **Ícone**: ⚪ (círculo branco, 12px)```bash``````

- **Velocidade base**: 200 px/s

# Tornar script executável

### 5. Ambulâncias (4 agentes)

- **IDs**: `amb_0` a `amb_3@localhost`chmod +x scripts/setup_prosody.sh

- **Password**: `amb123`

- **Prioridade**: Outros veículos param a 150px de distância

- **Broadcast**: Posição a cada 0.2s (5 Hz)

- **Ícone**: 🔴 (círculo vermelho, 12px)# Executar configuração---## 🚀 Instalação (macOS M1)

- **Velocidade**: 280 px/s (40% mais rápida)

./scripts/setup_prosody.sh

---

```

## ⚙️ Funcionalidades



### Algoritmo A* Inteligente

```pythonIsso irá:## 🚀 Início Rápido### 1. Pré-requisitos

# Cálculo do peso dinâmico da aresta:

edge_weight = base_weight  # 80-150 (tipo de via)- ✅ Iniciar container Docker com Prosody

edge_weight += traffic_delay * 5  # Penalidade por congestionamento

edge_weight += 200 if semaphore == 'red' else 0  # Semáforo vermelho- ✅ Configurar servidor XMPP em `localhost:5222`

edge_weight += 50 if semaphore == 'yellow' else 0  # Semáforo amarelo

```- ✅ Criar diretórios necessários



### Sistema de Prioridade de Ambulâncias### 1️⃣ Pré-requisitos#### Docker Desktop

```python

# Veículos checam ambulâncias próximas continuamente:### 4️⃣ Registrar Agentes XMPP

if distance_to_ambulance < 150:  # 150 pixels

    vehicle.stop()```bash

    reason = "AMBULANCIA_{ambulance_id}"

``````bash



### Tipos de Vias e Pesos Base# Tornar script executável```bash# Baixar e instalar Docker Desktop para Mac M1



| Tipo | Peso Base | Velocidade Limite | Uso |chmod +x scripts/register_10_paired_lights.sh

|------|-----------|-------------------|-----|

| Highway | 80 | 300 px/s | Avenidas principais |# Python 3.9 ou superior# https://www.docker.com/products/docker-desktop

| Main | 100 | 250 px/s | Ruas principais |

| Secondary | 120 | 200 px/s | Ruas secundárias |# Registrar 20 semáforos + veículos

| Residential | 150 | 150 px/s | Ruas residenciais |

./scripts/register_10_paired_lights.shpython --version```

*Peso final = base × random(0.8, 1.5) para variação realista*

```

### Lógica de Parada de Veículos



**Sistema de Prioridades** (do mais importante ao menos):

---

1. **Ambulância próxima** (< 150px) → **STOP IMEDIATO**

2. **Semáforo vermelho** (< 60px) → **STOP**# Docker (para Prosody XMPP)#### SUMO

3. **Semáforo amarelo próximo** (< 40px) → **STOP**

4. **Semáforo amarelo em alta velocidade** (> 250 px/s e < 70px) → **STOP**## 🎮 Executar Simulação



---docker --version```bash



## 📁 Estrutura do Projeto```bash



```# Ativar ambiente virtual# Instalar SUMO via Homebrew

projeto_agentes/

├── agents/source venv/bin/activate

│   ├── __init__.py

│   ├── base_agent.py           # Classe base abstrata# SUMO (opcional - apenas para nova simulação)brew tap dlr-ts/sumo

│   └── spade_traffic_agents.py # ⭐ Agentes principais

│# Executar simulação

├── config/

│   ├── __init__.pypython live_dynamic_spade.py# Instalação: https://eclipse.dev/sumo/brew install sumo

│   └── simulation_config.py    # Configurações globais

│```

├── scripts/

│   ├── register_all_agents.sh  # ⭐ Registra 36 agentes```

│   ├── setup_prosody.sh        # Inicia Docker + registra

│   └── cleanup.sh              # Limpa processos### Controles

│

├── utils/# Verificar instalação

│   ├── __init__.py

│   ├── routing.py              # Algoritmo A*| Tecla | Ação |

│   ├── data_collector.py       # Estatísticas

│   └── xmpp_manager.py         # Gerenciador XMPP|-------|------|### 2️⃣ Instalaçãosumo --version

│

├── live_dynamic_spade.py       # ⭐ ARQUIVO PRINCIPAL| `ESPAÇO` | Play / Pause |

├── requirements.txt            # ⭐ Dependências Python

├── README.md                   # ⭐ Esta documentação| `+` / `-` | Ajustar velocidade (2x-5x) |```

│

├── test_spade_integration.py  # Teste de conexão XMPP| `ESC` / `Q` | Sair |

├── test_prosody_direct.py     # Teste direto Prosody

│```bash

├── .gitignore

├── .env.example                # Variáveis de ambiente---

└── venv/                       # Ambiente virtual (não versionado)

```# Clone o repositório#### XQuartz (para GUI do SUMO)



---## 🎨 O Que Você Verá



## 🎨 Legenda Visualgit clone <repo-url>```bash



### Semáforos### Interface Pygame

- 🟢 **Verde** - Pode passar (15 segundos)

- 🟡 **Amarelo** - Atenção, vai fechar (3 segundos)cd projeto_agentes# Instalar XQuartz

- 🔴 **Vermelho** - STOP obrigatório (15 segundos)

```

### Veículos

- 🔵 **Círculo Azul** (12px) - Journey vehicle (A→B)┌──────────────┬───────────────────────────────────────────┐brew install --cask xquartz

- ⚪ **Círculo Branco** (12px) - Carros normais

- 🔴 **Círculo Vermelho** (12px) - Ambulâncias (prioridade)│              │                                           │



### Vias│  🎮 CONTROLE │                                           │# Crie e ative ambiente virtual

- **Linhas cinzas** (12px largura) - Estradas bidirecionais

- **Números amarelos** - Pesos das arestas (distância)│              │        🗺️ Grid 6×6 (1200×1200px)         │



---│  FPS: 30     │                                           │python -m venv venv# Após instalação, fazer logout e login novamente



## 🐛 Troubleshooting│  Speed: 3.0x │         ━━━━━━━━━━━━━━━━                 │



### Erro: "Connection refused"│              │         ┃  🚗   ┃  🚙                     │source venv/bin/activate  # macOS/Linux# Configurar XQuartz para permitir conexões de rede

```bash

# Verificar se Prosody está rodando│  🚦 Lights   │         ━━━━🔴━━━━━━🟢━━                 │

docker ps | grep prosody

│  └ 20 agents │              ↓   →                        │# venv\Scripts\activate   # Windows# XQuartz > Preferences > Security > "Allow connections from network clients"

# Reiniciar Prosody

docker restart prosody│              │         ━━━━━━━━━━━━━━━━                 │



# Se não existir, criar novo│  🚗 Vehicles │                                           │```

docker run -d --name prosody -p 5222:5222 prosody/prosody

```│  └ 11 cars   │         🚑 (ambulância)                   │



### Erro: "Agent already registered"│  └ 4 AMBs    │                                           │# Instale dependências

```bash

# Remover container e recriar│              │         ━━━━━━━━━━━━━━━━                 │

docker rm -f prosody

docker run -d --name prosody -p 5222:5222 prosody/prosody│  📍 Journey  │                                           │pip install -r requirements.txt#### Python 3.9+



# Registrar novamente│  v0: A→B     │                                           │

./scripts/register_all_agents.sh

```│  └ 45%       │                                           │``````bash



### Erro: "Import 'spade' could not be resolved"│              │                                           │

```bash

# Ativar ambiente virtual│  🗺️ LEGENDA  │                                           │# Verificar versão

source venv/bin/activate

│              │                                           │

# Reinstalar dependências

pip install --upgrade -r requirements.txt│  🚗 Viagem   │                                           │### 3️⃣ Executar Visualização (Pygame)python3 --version

```

│  🚙 Carro    │                                           │

### Simulação muito lenta

1. Ajustar multiplicador de velocidade (slider ou botões +/-)│  🚑 AMB      │                                           │

2. Fechar outros programas pesados

3. Verificar uso de CPU pelo Docker:│              │                                           │

   ```bash

   docker stats prosody│  🟢 Verde    │                                           │**Opção A: Usar dados já coletados** (Recomendado)# Se necessário, instalar via Homebrew

   ```

│  🟡 Amarelo  │                                           │

### Janela não cabe na tela

- Janela otimizada para **MacBook M1 13"** (1100×700px)│  🔴 Vermelho │                                           │brew install python@3.9

- Para monitores menores, editar `WINDOW_WIDTH` e `WINDOW_HEIGHT` em `live_dynamic_spade.py`

└──────────────┴───────────────────────────────────────────┘

---

``````bash```

## 📊 Métricas e Estatísticas



### Sidebar Exibe:

```### Elementos Visuais# Já existe simulation_data.db com 167 snapshots prontos!

Simulação:

  Step: 1234           # Frames executados

  Total Veículos: 15   # Sempre constante

- **Ruas**: Linhas cinzas com 2 faixas visíveis (24px largura)python visualize_pygame.py### 2. Configurar Projeto

Veículo Journey A->B:

  Velocidade: 250.0 px/s- **Nós**: Pequenos círculos cinzas (intersecções)

  Tempo Total: 02:35

  Distância: 847.3     # Soma dos pesos das arestas- **Semáforos**: ```



Agentes SPADE:  - 🟢 Verde = Passe

  Coordenador: 1

  Veículos: 15  - 🟡 Amarelo = Atenção#### Clone ou navegue até o diretório do projeto

  Semáforos: 20

  TOTAL: 36  - 🔴 Vermelho = Pare

```

- **Veículos**:**Opção B: Coletar novos dados**```bash

### Sobre a Distância

- **NÃO é distância em pixels**  - 🟣 Roxo = Veículo de viagem (v0: A→B)

- É a **soma dos pesos das arestas percorridas**

- Cada aresta tem peso baseado no tipo de via (80-150)  - 🔵 Azul = Carros normais (v1-v10)cd /Users/andresousa/Desktop/Inteligencia\ Artificial/Armazenamento\ Local/projeto_agentes

- Acumula apenas quando o veículo **completa** uma aresta (chega ao próximo nó)

- Representa o "custo" da rota escolhida pelo A*  - 🔴 Vermelho = Ambulâncias (AMB0-AMB3)



---```bash```



## 🔧 Configuração Avançada---



### Alterar Velocidade dos Veículos# 1. Iniciar Prosody

```python

# Em live_dynamic_spade.py, linha ~35## 👥 Tipos de Agentes

ROAD_TYPES = {

    'highway': {'speed_limit': 300, 'weight': 80},  # Modificar aquidocker run -d --name prosody -p 5222:5222 prosody/prosody#### Tornar scripts executáveis

    'main': {'speed_limit': 250, 'weight': 100},

    'secondary': {'speed_limit': 200, 'weight': 120},### 🎯 CoordinatorAgent

    'residential': {'speed_limit': 150, 'weight': 150}

}- **1 instância**: `coordinator@localhost````bash

```

- Gerencia a rede de agentes

### Alterar Ciclo dos Semáforos

```python- Distribui informações de topologia# 2. Executar simulação (coleta dados automaticamente)chmod +x scripts/*.sh

# Em agents/spade_traffic_agents.py, classe TrafficLightAgent

self.green_duration = 15  # segundos (verde)

self.yellow_duration = 3  # segundos (amarelo)

self.red_duration = 15    # segundos (vermelho)### 🚦 TrafficLightAgentpython test_journey.py```

```

- **20 instâncias**: 10 pares H+V em intersecções estratégicas

### Alterar Raio de Prioridade das Ambulâncias

```python- Alterna entre verde/amarelo/vermelho (8s/2s/8s)

# Em agents/spade_traffic_agents.py, MoveBehaviour

if dist_to_ambulance < 150:  # Modificar distância (pixels)- Coordenação: pares H+V nunca ambos verdes

    should_stop = True

```- Comunicação: broadcast de estados via XMPP# 3. Visualizar### 3. Configurar Prosody XMPP Server



### Alterar Tamanho da Janela- Posicionamento visual:

```python

# Em live_dynamic_spade.py, linhas 23-26  - Horizontal (H): 25px acima do nópython visualize_pygame.py

WINDOW_WIDTH = 1100   # Largura (padrão para macOS M1 13")

WINDOW_HEIGHT = 700   # Altura  - Vertical (V): 25px à esquerda do nó

SIDEBAR_WIDTH = 250   # Largura da sidebar

`````````bash



---**Intersecções com semáforos:**



## 📝 Licença```# Executar script de configuração



Este projeto foi desenvolvido para fins educacionais como parte de um projeto de **Sistemas Multiagentes**.Cantos: 1_1, 1_4, 4_1, 4_4



---Centro: 2_2, 2_3, 3_2, 3_3### 🎮 Controles Pygame./scripts/setup_prosody.sh



## 👥 AutorExtras: 1_3, 3_1



**André Sousa**  ``````

Curso de Inteligência Artificial  

Sistema de Tráfego Multiagente com SPADE



---### 🚗 VehicleAgent| Tecla | Ação |



**Última atualização:** 30 de Outubro de 2025  - **11 instâncias**: v0 (journey) + v1-v10 (carros normais)

**Versão:** 2.0 (SPADE + Pygame otimizado)  

**Compatibilidade:** macOS M1 13", Linux, Windows (com Docker)- Roteamento A* para encontrar melhor caminho|-------|------|Isso irá:


- Respeita semáforos:

  1. **Vermelho**: para a 60px| `ESPAÇO` | Play / Pause |- ✅ Iniciar container Docker com Prosody

  2. **Amarelo**: para se < 40px ou rápido demais

  3. **Verde**: passa| `←` `→` | Navegar frames (±10 steps) |- ✅ Configurar servidor XMPP em localhost:5222

- Direção correta: 

  - Movimento horizontal → verifica semáforo vertical| `↑` `↓` | Ajustar velocidade (0.25x a 8x) |- ✅ Preparar ambiente para registro de agentes

  - Movimento vertical → verifica semáforo horizontal

- Teleportação nas bordas (grid toroidal)| `R` | Reiniciar do início |

- Anti-stuck: teleporta após 200 frames parado

| `Q` | Sair |### 4. Configurar Ambiente Python

### 🚑 AmbulanceAgent

- **4 instâncias**: AMB0-AMB3

- Herda de VehicleAgent

- **Modo urgência**: ignora todos os semáforos---```bash

- Roteamento prioritário

# Criar ambiente virtual e instalar dependências

---

## 📁 Estrutura do Projeto./scripts/setup_venv.sh

## 🔧 Tecnologias



| Tecnologia | Versão | Propósito |

|------------|--------|-----------|```# Ativar ambiente virtual

| **Python** | 3.9+ | Linguagem principal |

| **SPADE** | 4.1.0 | Framework de agentes multiagente |projeto_agentes/source venv/bin/activate

| **Prosody** | Latest | Servidor XMPP (Docker) |

| **Pygame** | 2.6.1 | Visualização 2D em tempo real |│```



---├── 🤖 agents/                   # Agentes SPADE



## 🐛 Troubleshooting│   ├── traffic_light.py        # Semáforos inteligentes### 5. Configurar Variáveis de Ambiente



### Problema: Pygame não abre janela│   ├── car.py                  # Carros normais



```bash│   ├── ambulance.py            # Veículos de emergência```bash

# macOS - Instalar suporte SDL

brew install sdl2 sdl2_image sdl2_mixer sdl2_ttf│   └── pedestrian.py           # Pedestres# Copiar template



# Linux - Instalar dependências│cp .env.example .env

sudo apt-get install python3-pygame

```├── ⚙️  config/                  # Configurações



### Problema: XMPP connection failed│   └── simulation_config.py    # Parâmetros da simulação# Editar conforme necessário



```bash│nano .env

# Verificar se Prosody está rodando

docker ps | grep prosody├── 🗺️  scenarios/               # Cenários SUMO```



# Ver logs do Prosody│   └── grid_8x8/               # Rede urbana 8x8

docker logs prosody

│       ├── network.net.xml     # Topologia## 🎮 Executar Simulação

# Reiniciar Prosody

./scripts/setup_prosody.sh│       ├── routes.rou.xml      # Rotas

```

│       └── simulation.sumocfg  # Config SUMO### Modo Simples (GUI)

### Problema: Agentes não conectam

│

```bash

# Re-registrar agentes├── 🛠️  utils/                   # Utilitários```bash

./scripts/register_10_paired_lights.sh

│   ├── data_collector.py       # Persistência SQLite# Com GUI do SUMO (requer X11)

# Verificar agentes registrados

docker exec -it prosody prosodyctl list localhost│   ├── routing.py              # Algoritmos de rota./scripts/run_simulation.sh

```

│   └── xmpp_manager.py         # Gerenciamento XMPP```

### Erro de importação SPADE

│

```bash

# Verificar ambiente virtual ativado├── 🎯 test_journey.py           # Simulação principal### Modo Manual

which python

├── 🎮 visualize_pygame.py       # Visualização Pygame

# Reinstalar dependências

pip install --upgrade -r requirements.txt├── 💾 simulation_data.db        # Dados coletados (167 snapshots)```bash

```

│# 1. Ativar ambiente virtual

---

├── 📖 README.md                 # Este arquivosource venv/bin/activate

## 🧹 Limpeza

├── 📚 HISTORICO_PROJETO.md      # Documentação completa

```bash

# Parar e remover container Prosody└── 📋 requirements.txt          # Dependências Python# 2. Executar simulação

docker stop prosody

docker rm prosody```python main.py



# Limpar cache Python```

find . -type d -name "__pycache__" -exec rm -rf {} +

find . -type f -name "*.pyc" -delete---

```

### Com X11 no macOS M1

---

## 🎨 O Que Você Verá

## 📚 Documentação Adicional

```bash

Consulte o arquivo **[DOCUMENTATION.md](DOCUMENTATION.md)** para:

- Histórico completo do projeto### Interface Pygame# 1. Iniciar XQuartz

- Guias de integração SPADE

- Otimizações de semáforosopen -a XQuartz

- Detalhes de roteamento inteligente

- Comparação de scripts```

- Orientações técnicas

┌──────────────┬───────────────────────────────────────────┐# 2. Em um terminal XQuartz, executar:

---

│              │                                           │export DISPLAY=:0

## 🤝 Contribuindo

│  🎮 Controls │                                           │./scripts/run_simulation.sh

Contribuições são bem-vindas! Áreas de interesse:

│  📊 Stats    │                                           │```

- 🧠 Novos algoritmos de coordenação de semáforos

- 🚗 Novos tipos de agentes (ônibus, bicicletas, pedestres)│              │        🗺️ Mapa da Cidade 8x8            │

- 📊 Análises estatísticas avançadas

- 🎨 Melhorias na visualização│  Step: 1234  │                                           │## 🔧 Configuração

- 🗺️ Novos cenários (redes maiores, topologias reais)

│  Veículos: 1 │         ━━━━━━━━━━━━━━━━                 │

---

│  Vel: 45 km/h│         ┃  🚗   ┃                         │### Parâmetros da Simulação (.env)

## 📝 Licença

│              │         ━━━━●━━━━━━━●━━                   │

Este projeto é de código aberto para fins educacionais.

│              │              🔴   🟢                       │```bash

---

│  🗺️ Legenda  │         ━━━━━━━━━━━━━━━━                 │# Servidor XMPP

## ✨ Autor

│              │                                           │XMPP_SERVER=localhost

**André Sousa** - Projeto de Inteligência Artificial

│  🚗 Viagem   │                                           │XMPP_PORT=5222

---

│  🚙 Tráfego  │                                           │

**Nota**: Este é um projeto educacional para demonstração de sistemas multiagente aplicados a simulação de tráfego urbano.

│  🚑 Urgência │                                           │# SUMO

**Última atualização**: Outubro 2025  

**Status**: ✅ Funcional e otimizado  │              │                                           │SUMO_GUI=True              # True para GUI, False para headless

**Versão**: 2.0 - Coordinated Traffic Lights

│  🟢 Verde    │                                           │SUMO_STEP_LENGTH=0.1       # Duração de cada step (segundos)

│  🟡 Amarelo  │                                           │SUMO_PORT=8813             # Porta TraCI

│  🔴 Vermelho │                                           │

│              │                                           │# Número de agentes

│  [████████  ]│                                           │NUM_TRAFFIC_LIGHTS=4

│    80%       │                                           │NUM_CARS=10

└──────────────┴───────────────────────────────────────────┘NUM_AMBULANCES=2

```NUM_PEDESTRIANS=5

```

### Elementos Visuais

### Criar Novos Cenários SUMO

- **Ruas**: Linhas cinzas conectando intersecções

- **Nós**: Pequenos círculos cinzas (intersecções)#### Usando netedit (GUI)

- **Semáforos**: Círculos coloridos (🟢🟡🔴)```bash

- **Veículos**: netedit

  - 🚗 Amarelo = Viagem principal (car_journey)```

  - 🚙 Azul = Tráfego normal

  - 🚑 Vermelho = Emergência#### Gerar rede em grade automaticamente

```bash

---netgenerate --grid \

    --grid.number=5 \

## 📊 Dados da Simulação    --default.lanenumber=2 \

    --output-file=scenarios/my_scenario/network.net.xml

### Base de Dados (simulation_data.db)```



| Tabela | Descrição | Registros |## 👥 Tipos de Agentes

|--------|-----------|-----------|

| `simulation_snapshots` | Estados a cada segundo | 167 |### 🚦 TrafficLightAgent

| `vehicles` | Posições dos veículos | ~167 |- Controla semáforos em intersecções

| `traffic_lights` | Estados dos semáforos | ~4,008 |- Responde a requisições de prioridade

| `network_topology` | Topologia da rede | 1 |- Alterna fases ciclicamente

| `statistics` | Métricas agregadas | ~167 |

### 🚗 CarAgent

### Teste de Viagem Completo- Calcula rota ótima de A para B

- Monitora condições de tráfego

- **Origem**: Nó 0 (noroeste)- Evita congestionamentos

- **Destino**: Nó 63 (sudeste)

- **Distância**: 1.97 km### 🚑 AmbulanceAgent

- **Duração**: 166.3 segundos- Herda comportamentos de CarAgent

- **Velocidade média**: ~43 km/h- Modo urgência com prioridade

- **Semáforos**: 24 agentes ativos- Solicita abertura de semáforos

- **Status**: ✅ Sucesso

### 🚶 PedestrianAgent

---- Atravessa ruas com segurança

- Respeita sinais de pedestre

## 🔧 Tecnologias Utilizadas- Calcula trajetos a pé



| Tecnologia | Versão | Propósito |## 📊 Monitoramento

|------------|--------|-----------|

| **Python** | 3.9+ | Linguagem principal |### Logs

| **SPADE** | 4.1.0 | Framework de agentes |```bash

| **Prosody** | Latest | Servidor XMPP |# Logs são exibidos no console durante a execução

| **SUMO** | 1.24.0 | Simulador de tráfego |# Para salvar em arquivo:

| **TraCI** | 1.24.0 | Interface Python ↔ SUMO |python main.py > logs/simulation.log 2>&1

| **Pygame** | 2.6.1 | Visualização 2D |```

| **SQLite** | 3 | Persistência de dados |

### Métricas SUMO

---O SUMO gera automaticamente:

- `tripinfo.xml`: Informações de viagens

## 🎓 Conceitos Implementados- `summary.xml`: Resumo da simulação



### 1. Sistema Multiagente## 🧪 Testes

- **Agentes autônomos**: Cada semáforo decide independentemente

- **Comunicação**: Via protocolo XMPP (padrão FIPA)### Testar Registro de Agentes

- **Coordenação**: Semáforos vizinhos trocam informações

- **Objetivos**: Minimizar congestionamento```bash

# Registrar agente manualmente no Prosody

### 2. Simulação de Tráfego Realistadocker exec -it prosody prosodyctl register test_agent localhost senha123

- **SUMO**: Física de veículos realista

- **Tipos de vias**: Highway, Arterial, Collector, Local# Verificar agentes registrados

- **Limites de velocidade**: Respeitados pelos agentesdocker exec -it prosody prosodyctl list localhost

- **Lógica de ultrapassagem**: Implementada no SUMO```



### 3. Arquitetura Desacoplada### Testar Conexão SUMO

- **Separação**: Simulação ≠ Visualização

- **Benefício**: Rodar simulação sem GUI (headless)```bash

- **Análise**: Dados persistidos permitem análises posteriores# Abrir SUMO GUI manualmente

- **Replay**: Visualizar múltiplas vezes sem re-simularsumo-gui -c scenarios/simple_grid/simulation.sumocfg

```

---

## 🐛 Troubleshooting

## 📖 Documentação Adicional

### SUMO não inicia

- **[HISTORICO_PROJETO.md](HISTORICO_PROJETO.md)**: Evolução completa do projeto, problemas resolvidos, lições aprendidas```bash

- **[scenarios/grid_8x8/README.md](scenarios/grid_8x8/README.md)**: Detalhes da rede urbana 8x8# Verificar se SUMO está no PATH

which sumo

---

# Adicionar ao PATH (zsh)

## 🐛 Troubleshootingecho 'export PATH="/opt/homebrew/opt/sumo/bin:$PATH"' >> ~/.zshrc

source ~/.zshrc

### Problema: Pygame não abre janela```



```bash### X11 não funciona

# macOS - Instalar suporte SDL```bash

brew install sdl2 sdl2_image sdl2_mixer sdl2_ttf# Verificar DISPLAY

echo $DISPLAY

# Linux - Instalar dependências

sudo apt-get install python3-pygame# Configurar manualmente

```export DISPLAY=:0



### Problema: XMPP connection failed# Permitir conexões localhost

xhost + localhost

```bash```

# Verificar se Prosody está rodando

docker ps | grep prosody### Prosody não conecta

```bash

# Reiniciar container# Verificar se container está rodando

docker restart prosodydocker ps | grep prosody

```

# Ver logs do Prosody

### Problema: No such file 'simulation_data.db'docker logs prosody



```bash# Reiniciar Prosody

# Executar simulação para gerar dados./scripts/setup_prosody.sh

python test_journey.py```

```

### Erro de importação SPADE

---```bash

# Verificar ambiente virtual ativado

## 🤝 Contribuindowhich python



Contribuições são bem-vindas! Áreas de interesse:# Reinstalar dependências

pip install --upgrade -r requirements.txt

- 🧠 Novos algoritmos de coordenação de semáforos```

- 🚗 Novos tipos de agentes (ônibus, bicicletas)

- 📊 Análises estatísticas avançadas## 🧹 Limpeza

- 🎨 Melhorias na visualização

- 🗺️ Novos cenários (redes reais)```bash

# Limpar recursos e arquivos temporários

---./scripts/cleanup.sh

```

## 📝 Licença

## 📚 Recursos Adicionais

MIT License - veja arquivo LICENSE para detalhes.

- [SPADE Documentation](https://spade-mas.readthedocs.io/)

---- [SUMO Documentation](https://sumo.dlr.de/docs/)

- [TraCI Documentation](https://sumo.dlr.de/docs/TraCI.html)

## 👥 Autores- [Prosody Documentation](https://prosody.im/doc)



Projeto desenvolvido como demonstração de sistemas multiagente aplicados a tráfego urbano.## 📝 Exemplos de Uso



---### Adicionar Novo Tipo de Agente



## 🙏 Agradecimentos```python

# Em agents/my_agent.py

- **SPADE**: Framework excelente para agentes em Pythonfrom .base_agent import BaseTrafficAgent

- **SUMO**: Simulador de tráfego open-sourcefrom spade.behaviour import CyclicBehaviour

- **Pygame**: Biblioteca robusta para visualização 2D

- **Prosody**: Servidor XMPP leve e confiávelclass MyAgentBehaviour(CyclicBehaviour):

    async def run(self):

---        # Implementar lógica

        pass

**Última atualização**: Outubro 2025  

**Status**: ✅ Funcional e documentado  class MyAgent(BaseTrafficAgent):

**Versão**: 1.0 - Pygame Visualization    async def register_behaviours(self):

        behaviour = MyAgentBehaviour()
        self.add_behaviour(behaviour)
```

### Modificar Roteamento

```python
# Em utils/routing.py
def find_optimal_route(self, origin, destination):
    # Adicionar critérios de otimização
    # Ex: minimizar emissões, tempo, distância
    pass
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto é de código aberto para fins educacionais.

## ✨ Autor

André Sousa - Projeto de Inteligência Artificial

---

**Nota**: Este é um projeto educacional para demonstração de sistemas multiagente aplicados a simulação de tráfego urbano.
