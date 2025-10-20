# 🚀 Guia Rápido de Início

Este guia mostra como executar a simulação rapidamente.

## ⚠️ IMPORTANTE: Problema xerces-c no macOS

O SUMO 1.20.0 instalado via Homebrew tem incompatibilidade com xerces-c 3.3.0.

### 🎯 Solução Rápida: Usar Docker

```bash
# 1. Iniciar SUMO em Docker
chmod +x scripts/run_sumo_docker.sh
./scripts/run_sumo_docker.sh

# 2. Em outro terminal, ativar venv e executar
source venv/bin/activate
python main_docker.py --docker
```

## ⚡ Início Rápido (Método Alternativo)

### 1️⃣ Configurar Prosody
```bash
./scripts/setup_prosody.sh
```

### 2️⃣ Ativar Ambiente Virtual
```bash
source venv/bin/activate
```

### 3️⃣ Executar Simulação (Docker)
```bash
# Terminal 1: Iniciar SUMO
./scripts/run_sumo_docker.sh

# Terminal 2: Executar simulação
python main_docker.py --docker
```

## 📝 Notas Importantes

### Python 3.14
O projeto foi configurado para funcionar com Python 3.14 usando a variável:
```bash
PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
```

Se tiver problemas, considere usar Python 3.11-3.13:
```bash
# Instalar Python 3.13 via Homebrew
brew install python@3.13

# Recriar ambiente virtual
rm -rf venv
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### SUMO no macOS M1

Se o SUMO não estiver no PATH:
```bash
# Adicionar ao ~/.zshrc
echo 'export PATH="/opt/homebrew/opt/sumo/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

Para usar GUI com X11:
```bash
# 1. Abrir XQuartz
open -a XQuartz

# 2. Em terminal XQuartz:
export DISPLAY=:0
python main.py
```

### Verificar Docker

```bash
# Ver se Prosody está rodando
docker ps | grep prosody

# Ver logs
docker logs prosody

# Reiniciar se necessário
docker restart prosody
```

## 🎯 Primeiros Passos

### Testar Registro de Agente

```bash
# Registrar agente de teste
docker exec -it prosody prosodyctl register test localhost senha123

# Listar agentes
docker exec -it prosody prosodyctl list localhost
```

### Modificar Número de Agentes

Edite `.env`:
```bash
NUM_TRAFFIC_LIGHTS=4
NUM_CARS=10
NUM_AMBULANCES=2
NUM_PEDESTRIANS=5
```

### Executar Sem GUI

Edite `.env`:
```bash
SUMO_GUI=False
```

## 📂 Estrutura Principais Arquivos

```
projeto_agentes/
├── main.py              # ⭐ Arquivo principal - EXECUTAR ESTE
├── .env                 # ⚙️ Configurações
├── agents/              # 🤖 Agentes SPADE
│   ├── car.py          # Carros
│   ├── ambulance.py    # Ambulâncias
│   ├── traffic_light.py # Semáforos
│   └── pedestrian.py   # Pedestres
└── scenarios/           # 🗺️ Cenários SUMO
    └── simple_grid/    # Grade 3x3
```

## 🔧 Personalização Rápida

### Criar Novo Tipo de Agente

```python
# agents/my_custom_agent.py
from .base_agent import BaseTrafficAgent
from spade.behaviour import CyclicBehaviour

class MyBehaviour(CyclicBehaviour):
    async def run(self):
        # Sua lógica aqui
        pass

class MyAgent(BaseTrafficAgent):
    async def register_behaviours(self):
        self.add_behaviour(MyBehaviour())
```

### Adicionar ao Main

```python
# Em main.py, adicionar no create_agents():
from agents import MyAgent

# Criar instâncias
agent = MyAgent(jid, password, ...)
await agent.start()
```

## 📊 Monitorar Simulação

A simulação gera logs no console:

```
INFO - TrafficSimulation - Iniciando SUMO...
INFO - TrafficLightAgent - Agente trafficlight_0@localhost iniciado
INFO - CarAgent - Veículo car_0 criado: edge1 -> edge5
INFO - Step 100: 8 veículos na simulação
```

## 🆘 Problemas Comuns

| Problema | Solução |
|----------|---------|
| `Import "spade" not found` | Ativar venv: `source venv/bin/activate` |
| `Docker not running` | Iniciar Docker Desktop |
| `SUMO not found` | Instalar: `brew install sumo` |
| `X11 não funciona` | Instalar XQuartz e configurar DISPLAY |
| `Prosody connection failed` | Verificar: `docker ps \| grep prosody` |

## 📚 Próximos Passos

1. ✅ Executar simulação básica
2. 📖 Ler `README.md` completo
3. 🔍 Explorar código dos agentes
4. 🛠️ Personalizar cenários SUMO
5. 🎨 Criar novos tipos de agentes
6. 📊 Analisar métricas geradas

## 🎓 Recursos de Aprendizagem

- **SPADE**: https://spade-mas.readthedocs.io/
- **SUMO**: https://sumo.dlr.de/docs/
- **TraCI**: https://sumo.dlr.de/docs/TraCI.html

---

**Dica**: Use `Ctrl+C` para parar a simulação a qualquer momento!
