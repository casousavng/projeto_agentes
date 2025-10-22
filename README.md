# 🚦 Simulação de Tráfego Multiagente com SPADE# 🚦 Simulação de Tráfego Multiagente# 🚦 Simulação de Tráfego Multiagente



![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)

![SPADE](https://img.shields.io/badge/SPADE-4.1.0-green.svg)

![Pygame](https://img.shields.io/badge/Pygame-2.6.1-orange.svg)Sistema de simulação de tráfego urbano usando agentes inteligentes com **SPADE**, **SUMO** e visualização em **Pygame**.Sistema de simulação de tráfego urbano usando agentes inteligentes com **SPADE**, **SUMO** e **Prosody XMPP**.



Sistema de simulação de tráfego urbano usando agentes inteligentes com **SPADE**, **Prosody XMPP** e visualização em **Pygame**.



---![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)## 📋 Visão Geral



## 📋 Visão Geral![SPADE](https://img.shields.io/badge/SPADE-4.1.0-green.svg)



Este projeto implementa uma simulação de tráfego onde diferentes tipos de agentes (semáforos, carros e ambulâncias) interagem em um ambiente urbano virtual. Os agentes se comunicam via protocolo XMPP e coordenam suas ações para otimizar o fluxo de tráfego.![Pygame](https://img.shields.io/badge/Pygame-2.6.1-orange.svg)Este projeto implementa uma simulação de tráfego onde diferentes tipos de agentes (semáforos, carros, ambulâncias e pedestres) interagem em um ambiente urbano virtual. Os agentes se comunicam via protocolo XMPP e coordenam suas ações para otimizar o fluxo de tráfego.



### 🎯 Características Principais



✅ **36 agentes SPADE** comunicando via XMPP  ---### 🎯 Objetivos

✅ **20 semáforos coordenados** (10 intersecções × 2 orientações)  

✅ **Grid 6×6** com 36 nós e 120 arestas  

✅ **11 veículos + 4 ambulâncias** com roteamento inteligente  

✅ **Visualização Pygame** em tempo real  ## 📋 Visão Geral- **Carros**: Encontrar rotas ótimas entre pontos A e B

✅ **Ambulâncias com prioridade** (ignoram semáforos)  

✅ **Teleportação nas bordas** (circulação livre)  - **Ambulâncias**: Prioridade em modo urgência



---Este projeto implementa uma simulação completa de tráfego urbano onde:- **Semáforos**: Controle adaptativo de intersecções



## 🏗️ Arquitetura- **Pedestres**: Travessia segura de ruas



```- 🤖 **24 agentes de semáforos** controlam intersecções de forma inteligente

┌─────────────────────────────────────┐

│    Visualização Pygame              │- 🚗 **Veículos autônomos** navegam respeitando sinais e buscando rotas ótimas## 🛠️ Tecnologias

│    (live_dynamic_spade.py)          │

└─────────────────────────────────────┘- 💬 **Comunicação XMPP** permite coordenação entre agentes

              ↑ renderiza

┌─────────────────────────────────────┐- 🎮 **Visualização Pygame** renderiza a simulação em tempo real- **Python 3.9+**: Linguagem principal

│    Agentes SPADE                    │

│    (spade_traffic_agents.py)        │- 💾 **Dados persistidos** em SQLite para análise posterior- **SPADE**: Framework de agentes multiagente baseado em XMPP

│    • 1 CoordinatorAgent             │

│    • 20 TrafficLightAgents (H+V)    │- **Prosody**: Servidor XMPP em Docker

│    • 11 VehicleAgents               │

│    • 4 AmbulanceAgents              │### 🎯 Características Principais- **SUMO**: Simulador de tráfego urbano

└─────────────────────────────────────┘

              ↑ comunica via XMPP- **TraCI**: Interface Python para controlar SUMO

┌─────────────────────────────────────┐

│    Prosody XMPP Server              │✅ Arquitetura multiagente com SPADE  - **X11**: Interface gráfica (macOS M1)

│    (Docker container)               │

└─────────────────────────────────────┘✅ Rede urbana 8x8 (64 nós, 112 arestas)  

```

✅ Semáforos inteligentes com lógica adaptativa  ## 📁 Estrutura do Projeto

---

✅ Coleta automática de dados  

## 📁 Estrutura do Projeto

✅ Visualização interativa com controles  ```

```

projeto_agentes/✅ Replay de simulações sem re-executar  projeto_agentes/

│

├── 🎮 live_dynamic_spade.py        # Simulação principal├── agents/                 # Agentes SPADE

│

├── 🤖 agents/---│   ├── base_agent.py      # Classe base para todos os agentes

│   ├── __init__.py

│   └── spade_traffic_agents.py    # Todos os agentes SPADE│   ├── traffic_light.py   # Agente semáforo

│

├── 🛠️ scripts/## 🏗️ Arquitetura│   ├── car.py             # Agente carro

│   ├── setup_prosody.sh           # Configurar Prosody

│   └── register_10_paired_lights.sh # Registrar 20 semáforos│   ├── ambulance.py       # Agente ambulância

│

├── 📖 README.md                   # Esta documentação```│   └── pedestrian.py      # Agente pedestre

├── 📚 DOCUMENTATION.md            # Documentação completa consolidada

├── 📋 requirements.txt            # Dependências Python┌─────────────────────────────────────┐├── config/                 # Configurações

├── 🔐 .env.example                # Template de variáveis

└── 🗂️ venv/                       # Ambiente virtual│    Visualização Pygame              │  ← Você está aqui!│   └── simulation_config.py

```

│    (visualize_pygame.py)            │├── scenarios/              # Cenários SUMO

---

└─────────────────────────────────────┘│   └── simple_grid/       # Grid 3x3 com semáforos

## 🚀 Instalação Rápida

              ↑ lê│       ├── network.net.xml

### 1️⃣ Pré-requisitos

┌─────────────────────────────────────┐│       ├── routes.rou.xml

- **Python 3.9+**

- **Docker Desktop** (para Prosody XMPP)│    SQLite Database                  ││       └── simulation.sumocfg



```bash│    (simulation_data.db)             │  ← 167 snapshots prontos├── scripts/                # Scripts auxiliares

# Verificar versões

python3 --version└─────────────────────────────────────┘│   ├── setup_prosody.sh   # Configurar Prosody

docker --version

```              ↑ grava│   ├── setup_venv.sh      # Configurar ambiente Python



### 2️⃣ Clonar e Configurar┌─────────────────────────────────────┐│   ├── run_simulation.sh  # Executar simulação



```bash│    Simulação SPADE + SUMO           ││   └── cleanup.sh         # Limpar recursos

# Clone o repositório

git clone <repo-url>│    (test_journey.py)                │  ← Agentes inteligentes├── utils/                  # Utilitários

cd projeto_agentes

└─────────────────────────────────────┘│   ├── routing.py         # Otimização de rotas

# Criar e ativar ambiente virtual

python3 -m venv venv              ↑ comunica│   └── xmpp_manager.py    # Gerenciamento de agentes XMPP

source venv/bin/activate  # macOS/Linux

# venv\Scripts\activate   # Windows┌─────────────────────────────────────┐├── main.py                 # Simulador principal



# Instalar dependências│    Prosody XMPP Server              │├── requirements.txt        # Dependências Python

pip install -r requirements.txt

```│    (Docker container)               │  ← Mensagens entre agentes├── .env.example           # Template de variáveis de ambiente



### 3️⃣ Configurar Prosody XMPP└─────────────────────────────────────┘└── README.md              # Esta documentação



```bash``````

# Tornar script executável

chmod +x scripts/setup_prosody.sh



# Executar configuração---## 🚀 Instalação (macOS M1)

./scripts/setup_prosody.sh

```



Isso irá:## 🚀 Início Rápido### 1. Pré-requisitos

- ✅ Iniciar container Docker com Prosody

- ✅ Configurar servidor XMPP em `localhost:5222`

- ✅ Criar diretórios necessários

### 1️⃣ Pré-requisitos#### Docker Desktop

### 4️⃣ Registrar Agentes XMPP

```bash

```bash

# Tornar script executável```bash# Baixar e instalar Docker Desktop para Mac M1

chmod +x scripts/register_10_paired_lights.sh

# Python 3.9 ou superior# https://www.docker.com/products/docker-desktop

# Registrar 20 semáforos + veículos

./scripts/register_10_paired_lights.shpython --version```

```



---

# Docker (para Prosody XMPP)#### SUMO

## 🎮 Executar Simulação

docker --version```bash

```bash

# Ativar ambiente virtual# Instalar SUMO via Homebrew

source venv/bin/activate

# SUMO (opcional - apenas para nova simulação)brew tap dlr-ts/sumo

# Executar simulação

python live_dynamic_spade.py# Instalação: https://eclipse.dev/sumo/brew install sumo

```

```

### Controles

# Verificar instalação

| Tecla | Ação |

|-------|------|### 2️⃣ Instalaçãosumo --version

| `ESPAÇO` | Play / Pause |

| `+` / `-` | Ajustar velocidade (2x-5x) |```

| `ESC` / `Q` | Sair |

```bash

---

# Clone o repositório#### XQuartz (para GUI do SUMO)

## 🎨 O Que Você Verá

git clone <repo-url>```bash

### Interface Pygame

cd projeto_agentes# Instalar XQuartz

```

┌──────────────┬───────────────────────────────────────────┐brew install --cask xquartz

│              │                                           │

│  🎮 CONTROLE │                                           │# Crie e ative ambiente virtual

│              │        🗺️ Grid 6×6 (1200×1200px)         │

│  FPS: 30     │                                           │python -m venv venv# Após instalação, fazer logout e login novamente

│  Speed: 3.0x │         ━━━━━━━━━━━━━━━━                 │

│              │         ┃  🚗   ┃  🚙                     │source venv/bin/activate  # macOS/Linux# Configurar XQuartz para permitir conexões de rede

│  🚦 Lights   │         ━━━━🔴━━━━━━🟢━━                 │

│  └ 20 agents │              ↓   →                        │# venv\Scripts\activate   # Windows# XQuartz > Preferences > Security > "Allow connections from network clients"

│              │         ━━━━━━━━━━━━━━━━                 │

│  🚗 Vehicles │                                           │```

│  └ 11 cars   │         🚑 (ambulância)                   │

│  └ 4 AMBs    │                                           │# Instale dependências

│              │         ━━━━━━━━━━━━━━━━                 │

│  📍 Journey  │                                           │pip install -r requirements.txt#### Python 3.9+

│  v0: A→B     │                                           │

│  └ 45%       │                                           │``````bash

│              │                                           │

│  🗺️ LEGENDA  │                                           │# Verificar versão

│              │                                           │

│  🚗 Viagem   │                                           │### 3️⃣ Executar Visualização (Pygame)python3 --version

│  🚙 Carro    │                                           │

│  🚑 AMB      │                                           │

│              │                                           │

│  🟢 Verde    │                                           │**Opção A: Usar dados já coletados** (Recomendado)# Se necessário, instalar via Homebrew

│  🟡 Amarelo  │                                           │

│  🔴 Vermelho │                                           │brew install python@3.9

└──────────────┴───────────────────────────────────────────┘

``````bash```



### Elementos Visuais# Já existe simulation_data.db com 167 snapshots prontos!



- **Ruas**: Linhas cinzas com 2 faixas visíveis (24px largura)python visualize_pygame.py### 2. Configurar Projeto

- **Nós**: Pequenos círculos cinzas (intersecções)

- **Semáforos**: ```

  - 🟢 Verde = Passe

  - 🟡 Amarelo = Atenção#### Clone ou navegue até o diretório do projeto

  - 🔴 Vermelho = Pare

- **Veículos**:**Opção B: Coletar novos dados**```bash

  - 🟣 Roxo = Veículo de viagem (v0: A→B)

  - 🔵 Azul = Carros normais (v1-v10)cd /Users/andresousa/Desktop/Inteligencia\ Artificial/Armazenamento\ Local/projeto_agentes

  - 🔴 Vermelho = Ambulâncias (AMB0-AMB3)

```bash```

---

# 1. Iniciar Prosody

## 👥 Tipos de Agentes

docker run -d --name prosody -p 5222:5222 prosody/prosody#### Tornar scripts executáveis

### 🎯 CoordinatorAgent

- **1 instância**: `coordinator@localhost````bash

- Gerencia a rede de agentes

- Distribui informações de topologia# 2. Executar simulação (coleta dados automaticamente)chmod +x scripts/*.sh



### 🚦 TrafficLightAgentpython test_journey.py```

- **20 instâncias**: 10 pares H+V em intersecções estratégicas

- Alterna entre verde/amarelo/vermelho (8s/2s/8s)

- Coordenação: pares H+V nunca ambos verdes

- Comunicação: broadcast de estados via XMPP# 3. Visualizar### 3. Configurar Prosody XMPP Server

- Posicionamento visual:

  - Horizontal (H): 25px acima do nópython visualize_pygame.py

  - Vertical (V): 25px à esquerda do nó

``````bash

**Intersecções com semáforos:**

```# Executar script de configuração

Cantos: 1_1, 1_4, 4_1, 4_4

Centro: 2_2, 2_3, 3_2, 3_3### 🎮 Controles Pygame./scripts/setup_prosody.sh

Extras: 1_3, 3_1

``````



### 🚗 VehicleAgent| Tecla | Ação |

- **11 instâncias**: v0 (journey) + v1-v10 (carros normais)

- Roteamento A* para encontrar melhor caminho|-------|------|Isso irá:

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
