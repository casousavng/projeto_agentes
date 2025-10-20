# 🚦 Simulação de Tráfego Multiagente

Sistema de simulação de tráfego urbano usando agentes inteligentes com **SPADE**, **SUMO** e **Prosody XMPP**.

## 📋 Visão Geral

Este projeto implementa uma simulação de tráfego onde diferentes tipos de agentes (semáforos, carros, ambulâncias e pedestres) interagem em um ambiente urbano virtual. Os agentes se comunicam via protocolo XMPP e coordenam suas ações para otimizar o fluxo de tráfego.

### 🎯 Objetivos

- **Carros**: Encontrar rotas ótimas entre pontos A e B
- **Ambulâncias**: Prioridade em modo urgência
- **Semáforos**: Controle adaptativo de intersecções
- **Pedestres**: Travessia segura de ruas

## 🛠️ Tecnologias

- **Python 3.9+**: Linguagem principal
- **SPADE**: Framework de agentes multiagente baseado em XMPP
- **Prosody**: Servidor XMPP em Docker
- **SUMO**: Simulador de tráfego urbano
- **TraCI**: Interface Python para controlar SUMO
- **X11**: Interface gráfica (macOS M1)

## 📁 Estrutura do Projeto

```
projeto_agentes/
├── agents/                 # Agentes SPADE
│   ├── base_agent.py      # Classe base para todos os agentes
│   ├── traffic_light.py   # Agente semáforo
│   ├── car.py             # Agente carro
│   ├── ambulance.py       # Agente ambulância
│   └── pedestrian.py      # Agente pedestre
├── config/                 # Configurações
│   └── simulation_config.py
├── scenarios/              # Cenários SUMO
│   └── simple_grid/       # Grid 3x3 com semáforos
│       ├── network.net.xml
│       ├── routes.rou.xml
│       └── simulation.sumocfg
├── scripts/                # Scripts auxiliares
│   ├── setup_prosody.sh   # Configurar Prosody
│   ├── setup_venv.sh      # Configurar ambiente Python
│   ├── run_simulation.sh  # Executar simulação
│   └── cleanup.sh         # Limpar recursos
├── utils/                  # Utilitários
│   ├── routing.py         # Otimização de rotas
│   └── xmpp_manager.py    # Gerenciamento de agentes XMPP
├── main.py                 # Simulador principal
├── requirements.txt        # Dependências Python
├── .env.example           # Template de variáveis de ambiente
└── README.md              # Esta documentação
```

## 🚀 Instalação (macOS M1)

### 1. Pré-requisitos

#### Docker Desktop
```bash
# Baixar e instalar Docker Desktop para Mac M1
# https://www.docker.com/products/docker-desktop
```

#### SUMO
```bash
# Instalar SUMO via Homebrew
brew tap dlr-ts/sumo
brew install sumo

# Verificar instalação
sumo --version
```

#### XQuartz (para GUI do SUMO)
```bash
# Instalar XQuartz
brew install --cask xquartz

# Após instalação, fazer logout e login novamente
# Configurar XQuartz para permitir conexões de rede
# XQuartz > Preferences > Security > "Allow connections from network clients"
```

#### Python 3.9+
```bash
# Verificar versão
python3 --version

# Se necessário, instalar via Homebrew
brew install python@3.9
```

### 2. Configurar Projeto

#### Clone ou navegue até o diretório do projeto
```bash
cd /Users/andresousa/Desktop/Inteligencia\ Artificial/Armazenamento\ Local/projeto_agentes
```

#### Tornar scripts executáveis
```bash
chmod +x scripts/*.sh
```

### 3. Configurar Prosody XMPP Server

```bash
# Executar script de configuração
./scripts/setup_prosody.sh
```

Isso irá:
- ✅ Iniciar container Docker com Prosody
- ✅ Configurar servidor XMPP em localhost:5222
- ✅ Preparar ambiente para registro de agentes

### 4. Configurar Ambiente Python

```bash
# Criar ambiente virtual e instalar dependências
./scripts/setup_venv.sh

# Ativar ambiente virtual
source venv/bin/activate
```

### 5. Configurar Variáveis de Ambiente

```bash
# Copiar template
cp .env.example .env

# Editar conforme necessário
nano .env
```

## 🎮 Executar Simulação

### Modo Simples (GUI)

```bash
# Com GUI do SUMO (requer X11)
./scripts/run_simulation.sh
```

### Modo Manual

```bash
# 1. Ativar ambiente virtual
source venv/bin/activate

# 2. Executar simulação
python main.py
```

### Com X11 no macOS M1

```bash
# 1. Iniciar XQuartz
open -a XQuartz

# 2. Em um terminal XQuartz, executar:
export DISPLAY=:0
./scripts/run_simulation.sh
```

## 🔧 Configuração

### Parâmetros da Simulação (.env)

```bash
# Servidor XMPP
XMPP_SERVER=localhost
XMPP_PORT=5222

# SUMO
SUMO_GUI=True              # True para GUI, False para headless
SUMO_STEP_LENGTH=0.1       # Duração de cada step (segundos)
SUMO_PORT=8813             # Porta TraCI

# Número de agentes
NUM_TRAFFIC_LIGHTS=4
NUM_CARS=10
NUM_AMBULANCES=2
NUM_PEDESTRIANS=5
```

### Criar Novos Cenários SUMO

#### Usando netedit (GUI)
```bash
netedit
```

#### Gerar rede em grade automaticamente
```bash
netgenerate --grid \
    --grid.number=5 \
    --default.lanenumber=2 \
    --output-file=scenarios/my_scenario/network.net.xml
```

## 👥 Tipos de Agentes

### 🚦 TrafficLightAgent
- Controla semáforos em intersecções
- Responde a requisições de prioridade
- Alterna fases ciclicamente

### 🚗 CarAgent
- Calcula rota ótima de A para B
- Monitora condições de tráfego
- Evita congestionamentos

### 🚑 AmbulanceAgent
- Herda comportamentos de CarAgent
- Modo urgência com prioridade
- Solicita abertura de semáforos

### 🚶 PedestrianAgent
- Atravessa ruas com segurança
- Respeita sinais de pedestre
- Calcula trajetos a pé

## 📊 Monitoramento

### Logs
```bash
# Logs são exibidos no console durante a execução
# Para salvar em arquivo:
python main.py > logs/simulation.log 2>&1
```

### Métricas SUMO
O SUMO gera automaticamente:
- `tripinfo.xml`: Informações de viagens
- `summary.xml`: Resumo da simulação

## 🧪 Testes

### Testar Registro de Agentes

```bash
# Registrar agente manualmente no Prosody
docker exec -it prosody prosodyctl register test_agent localhost senha123

# Verificar agentes registrados
docker exec -it prosody prosodyctl list localhost
```

### Testar Conexão SUMO

```bash
# Abrir SUMO GUI manualmente
sumo-gui -c scenarios/simple_grid/simulation.sumocfg
```

## 🐛 Troubleshooting

### SUMO não inicia
```bash
# Verificar se SUMO está no PATH
which sumo

# Adicionar ao PATH (zsh)
echo 'export PATH="/opt/homebrew/opt/sumo/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### X11 não funciona
```bash
# Verificar DISPLAY
echo $DISPLAY

# Configurar manualmente
export DISPLAY=:0

# Permitir conexões localhost
xhost + localhost
```

### Prosody não conecta
```bash
# Verificar se container está rodando
docker ps | grep prosody

# Ver logs do Prosody
docker logs prosody

# Reiniciar Prosody
./scripts/setup_prosody.sh
```

### Erro de importação SPADE
```bash
# Verificar ambiente virtual ativado
which python

# Reinstalar dependências
pip install --upgrade -r requirements.txt
```

## 🧹 Limpeza

```bash
# Limpar recursos e arquivos temporários
./scripts/cleanup.sh
```

## 📚 Recursos Adicionais

- [SPADE Documentation](https://spade-mas.readthedocs.io/)
- [SUMO Documentation](https://sumo.dlr.de/docs/)
- [TraCI Documentation](https://sumo.dlr.de/docs/TraCI.html)
- [Prosody Documentation](https://prosody.im/doc)

## 📝 Exemplos de Uso

### Adicionar Novo Tipo de Agente

```python
# Em agents/my_agent.py
from .base_agent import BaseTrafficAgent
from spade.behaviour import CyclicBehaviour

class MyAgentBehaviour(CyclicBehaviour):
    async def run(self):
        # Implementar lógica
        pass

class MyAgent(BaseTrafficAgent):
    async def register_behaviours(self):
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
