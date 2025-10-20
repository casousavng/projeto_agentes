# 🚦 Simulação de Tráfego Multiagente# 🚦 Simulação de Tráfego Multiagente



Sistema de simulação de tráfego urbano usando agentes inteligentes com **SPADE**, **SUMO** e visualização em **Pygame**.Sistema de simulação de tráfego urbano usando agentes inteligentes com **SPADE**, **SUMO** e **Prosody XMPP**.



![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)## 📋 Visão Geral

![SPADE](https://img.shields.io/badge/SPADE-4.1.0-green.svg)

![Pygame](https://img.shields.io/badge/Pygame-2.6.1-orange.svg)Este projeto implementa uma simulação de tráfego onde diferentes tipos de agentes (semáforos, carros, ambulâncias e pedestres) interagem em um ambiente urbano virtual. Os agentes se comunicam via protocolo XMPP e coordenam suas ações para otimizar o fluxo de tráfego.



---### 🎯 Objetivos



## 📋 Visão Geral- **Carros**: Encontrar rotas ótimas entre pontos A e B

- **Ambulâncias**: Prioridade em modo urgência

Este projeto implementa uma simulação completa de tráfego urbano onde:- **Semáforos**: Controle adaptativo de intersecções

- **Pedestres**: Travessia segura de ruas

- 🤖 **24 agentes de semáforos** controlam intersecções de forma inteligente

- 🚗 **Veículos autônomos** navegam respeitando sinais e buscando rotas ótimas## 🛠️ Tecnologias

- 💬 **Comunicação XMPP** permite coordenação entre agentes

- 🎮 **Visualização Pygame** renderiza a simulação em tempo real- **Python 3.9+**: Linguagem principal

- 💾 **Dados persistidos** em SQLite para análise posterior- **SPADE**: Framework de agentes multiagente baseado em XMPP

- **Prosody**: Servidor XMPP em Docker

### 🎯 Características Principais- **SUMO**: Simulador de tráfego urbano

- **TraCI**: Interface Python para controlar SUMO

✅ Arquitetura multiagente com SPADE  - **X11**: Interface gráfica (macOS M1)

✅ Rede urbana 8x8 (64 nós, 112 arestas)  

✅ Semáforos inteligentes com lógica adaptativa  ## 📁 Estrutura do Projeto

✅ Coleta automática de dados  

✅ Visualização interativa com controles  ```

✅ Replay de simulações sem re-executar  projeto_agentes/

├── agents/                 # Agentes SPADE

---│   ├── base_agent.py      # Classe base para todos os agentes

│   ├── traffic_light.py   # Agente semáforo

## 🏗️ Arquitetura│   ├── car.py             # Agente carro

│   ├── ambulance.py       # Agente ambulância

```│   └── pedestrian.py      # Agente pedestre

┌─────────────────────────────────────┐├── config/                 # Configurações

│    Visualização Pygame              │  ← Você está aqui!│   └── simulation_config.py

│    (visualize_pygame.py)            │├── scenarios/              # Cenários SUMO

└─────────────────────────────────────┘│   └── simple_grid/       # Grid 3x3 com semáforos

              ↑ lê│       ├── network.net.xml

┌─────────────────────────────────────┐│       ├── routes.rou.xml

│    SQLite Database                  ││       └── simulation.sumocfg

│    (simulation_data.db)             │  ← 167 snapshots prontos├── scripts/                # Scripts auxiliares

└─────────────────────────────────────┘│   ├── setup_prosody.sh   # Configurar Prosody

              ↑ grava│   ├── setup_venv.sh      # Configurar ambiente Python

┌─────────────────────────────────────┐│   ├── run_simulation.sh  # Executar simulação

│    Simulação SPADE + SUMO           ││   └── cleanup.sh         # Limpar recursos

│    (test_journey.py)                │  ← Agentes inteligentes├── utils/                  # Utilitários

└─────────────────────────────────────┘│   ├── routing.py         # Otimização de rotas

              ↑ comunica│   └── xmpp_manager.py    # Gerenciamento de agentes XMPP

┌─────────────────────────────────────┐├── main.py                 # Simulador principal

│    Prosody XMPP Server              │├── requirements.txt        # Dependências Python

│    (Docker container)               │  ← Mensagens entre agentes├── .env.example           # Template de variáveis de ambiente

└─────────────────────────────────────┘└── README.md              # Esta documentação

``````



---## 🚀 Instalação (macOS M1)



## 🚀 Início Rápido### 1. Pré-requisitos



### 1️⃣ Pré-requisitos#### Docker Desktop

```bash

```bash# Baixar e instalar Docker Desktop para Mac M1

# Python 3.9 ou superior# https://www.docker.com/products/docker-desktop

python --version```



# Docker (para Prosody XMPP)#### SUMO

docker --version```bash

# Instalar SUMO via Homebrew

# SUMO (opcional - apenas para nova simulação)brew tap dlr-ts/sumo

# Instalação: https://eclipse.dev/sumo/brew install sumo

```

# Verificar instalação

### 2️⃣ Instalaçãosumo --version

```

```bash

# Clone o repositório#### XQuartz (para GUI do SUMO)

git clone <repo-url>```bash

cd projeto_agentes# Instalar XQuartz

brew install --cask xquartz

# Crie e ative ambiente virtual

python -m venv venv# Após instalação, fazer logout e login novamente

source venv/bin/activate  # macOS/Linux# Configurar XQuartz para permitir conexões de rede

# venv\Scripts\activate   # Windows# XQuartz > Preferences > Security > "Allow connections from network clients"

```

# Instale dependências

pip install -r requirements.txt#### Python 3.9+

``````bash

# Verificar versão

### 3️⃣ Executar Visualização (Pygame)python3 --version



**Opção A: Usar dados já coletados** (Recomendado)# Se necessário, instalar via Homebrew

brew install python@3.9

```bash```

# Já existe simulation_data.db com 167 snapshots prontos!

python visualize_pygame.py### 2. Configurar Projeto

```

#### Clone ou navegue até o diretório do projeto

**Opção B: Coletar novos dados**```bash

cd /Users/andresousa/Desktop/Inteligencia\ Artificial/Armazenamento\ Local/projeto_agentes

```bash```

# 1. Iniciar Prosody

docker run -d --name prosody -p 5222:5222 prosody/prosody#### Tornar scripts executáveis

```bash

# 2. Executar simulação (coleta dados automaticamente)chmod +x scripts/*.sh

python test_journey.py```



# 3. Visualizar### 3. Configurar Prosody XMPP Server

python visualize_pygame.py

``````bash

# Executar script de configuração

### 🎮 Controles Pygame./scripts/setup_prosody.sh

```

| Tecla | Ação |

|-------|------|Isso irá:

| `ESPAÇO` | Play / Pause |- ✅ Iniciar container Docker com Prosody

| `←` `→` | Navegar frames (±10 steps) |- ✅ Configurar servidor XMPP em localhost:5222

| `↑` `↓` | Ajustar velocidade (0.25x a 8x) |- ✅ Preparar ambiente para registro de agentes

| `R` | Reiniciar do início |

| `Q` | Sair |### 4. Configurar Ambiente Python



---```bash

# Criar ambiente virtual e instalar dependências

## 📁 Estrutura do Projeto./scripts/setup_venv.sh



```# Ativar ambiente virtual

projeto_agentes/source venv/bin/activate

│```

├── 🤖 agents/                   # Agentes SPADE

│   ├── traffic_light.py        # Semáforos inteligentes### 5. Configurar Variáveis de Ambiente

│   ├── car.py                  # Carros normais

│   ├── ambulance.py            # Veículos de emergência```bash

│   └── pedestrian.py           # Pedestres# Copiar template

│cp .env.example .env

├── ⚙️  config/                  # Configurações

│   └── simulation_config.py    # Parâmetros da simulação# Editar conforme necessário

│nano .env

├── 🗺️  scenarios/               # Cenários SUMO```

│   └── grid_8x8/               # Rede urbana 8x8

│       ├── network.net.xml     # Topologia## 🎮 Executar Simulação

│       ├── routes.rou.xml      # Rotas

│       └── simulation.sumocfg  # Config SUMO### Modo Simples (GUI)

│

├── 🛠️  utils/                   # Utilitários```bash

│   ├── data_collector.py       # Persistência SQLite# Com GUI do SUMO (requer X11)

│   ├── routing.py              # Algoritmos de rota./scripts/run_simulation.sh

│   └── xmpp_manager.py         # Gerenciamento XMPP```

│

├── 🎯 test_journey.py           # Simulação principal### Modo Manual

├── 🎮 visualize_pygame.py       # Visualização Pygame

├── 💾 simulation_data.db        # Dados coletados (167 snapshots)```bash

│# 1. Ativar ambiente virtual

├── 📖 README.md                 # Este arquivosource venv/bin/activate

├── 📚 HISTORICO_PROJETO.md      # Documentação completa

└── 📋 requirements.txt          # Dependências Python# 2. Executar simulação

```python main.py

```

---

### Com X11 no macOS M1

## 🎨 O Que Você Verá

```bash

### Interface Pygame# 1. Iniciar XQuartz

open -a XQuartz

```

┌──────────────┬───────────────────────────────────────────┐# 2. Em um terminal XQuartz, executar:

│              │                                           │export DISPLAY=:0

│  🎮 Controls │                                           │./scripts/run_simulation.sh

│  📊 Stats    │                                           │```

│              │        🗺️ Mapa da Cidade 8x8            │

│  Step: 1234  │                                           │## 🔧 Configuração

│  Veículos: 1 │         ━━━━━━━━━━━━━━━━                 │

│  Vel: 45 km/h│         ┃  🚗   ┃                         │### Parâmetros da Simulação (.env)

│              │         ━━━━●━━━━━━━●━━                   │

│              │              🔴   🟢                       │```bash

│  🗺️ Legenda  │         ━━━━━━━━━━━━━━━━                 │# Servidor XMPP

│              │                                           │XMPP_SERVER=localhost

│  🚗 Viagem   │                                           │XMPP_PORT=5222

│  🚙 Tráfego  │                                           │

│  🚑 Urgência │                                           │# SUMO

│              │                                           │SUMO_GUI=True              # True para GUI, False para headless

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
