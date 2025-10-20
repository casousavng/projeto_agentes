# 🌐 Traffic Simulation - Web Visualization

Visualização em tempo real da simulação de tráfego 8x8 com interface web interativa.

## 🎯 Features

### 🗺️ Visualização da Cidade
- ✅ Rede 8x8 completa (64 nós, 314 edges)
- ✅ 4 tipos de vias com cores diferentes:
  - 🔴 **Highway** (80 km/h) - Vermelho
  - 🟠 **Arterial** (60 km/h) - Laranja
  - 🟢 **Collector** (50 km/h) - Verde
  - ⚪ **Local** (30 km/h) - Cinza

### 🚗 Veículos em Tempo Real
- ✅ Posição e orientação dinâmica
- ✅ Velocidade instantânea
- ✅ Tipos diferenciados:
  - 🚕 **Viagem A→B** (amarelo) - Veículo principal
  - 🚙 **Tráfego** (azul) - Veículos secundários
  - 🚑 **Emergência** (vermelho) - Ambulâncias

### 🚦 Semáforos Inteligentes
- ✅ Estado em tempo real (Verde/Amarelo/Vermelho)
- ✅ Contagem de veículos esperando
- ✅ Visualização adaptativa por zoom

### 🛣️ Roteamento Dinâmico
- ✅ Exibe rota completa do veículo A→B
- ✅ Destaque visual da rota escolhida
- ✅ Considera tráfego, semáforos e distância
- ✅ Escolha inteligente de vias (prefere highways)

### 📊 Métricas em Tempo Real
- ✅ Número de veículos ativos
- ✅ Velocidade média da frota
- ✅ Veículos parados (tráfego)
- ✅ Tempo de simulação
- ✅ FPS (frames por segundo)

### 🎮 Controles Interativos
- ✅ **Pan**: Arraste com mouse para mover a câmera
- ✅ **Zoom**: Scroll do mouse para aproximar/afastar
- ✅ **Start/Stop**: Controle da simulação
- ✅ Auto-centralização ao iniciar

## 🚀 Como Usar

### Passo 1: Instalar Dependências
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Passo 2: Iniciar SUMO (Terminal 1)
```bash
./scripts/run_sumo_docker.sh
```

Aguarde a mensagem:
```
✅ SUMO rodando no container 'sumo-sim'
🔌 TraCI disponível na porta 8813
```

### Passo 3: Iniciar Aplicação Web (Terminal 2)
```bash
./scripts/run_web_app.sh
```

Ou manualmente:
```bash
source venv/bin/activate
python app.py
```

### Passo 4: Acessar Interface
Abra no navegador:
```
http://localhost:5000
```

### Passo 5: Iniciar Simulação
Na interface web:
1. Clique em **"▶️ Iniciar Simulação"**
2. Aguarde carregar a rede
3. Observe a simulação em tempo real!

## 🎨 Interface

### Sidebar Esquerdo
- **Controles**: Start/Stop
- **Estatísticas**: Métricas em tempo real
- **Legenda**: Cores de vias, veículos e semáforos

### Área Central
- **Canvas**: Visualização da simulação
- **Status Badge**: Estado da simulação (Rodando/Parado)
- **Info Panel**: Tempo simulado e FPS

### Interações
- **Arrastar**: Move a visualização
- **Scroll**: Zoom in/out
- **Auto-fit**: Centraliza automaticamente ao iniciar

## 🏗️ Arquitetura

### Backend (Flask + SocketIO)
```
app.py
├── API REST
│   ├── GET  /                  → Interface HTML
│   ├── POST /api/start         → Inicia simulação
│   ├── POST /api/stop          → Para simulação
│   ├── GET  /api/status        → Status atual
│   └── GET  /api/topology      → Rede 8x8
│
└── WebSocket
    ├── connection              → Cliente conecta
    ├── simulation_update       → Updates em tempo real
    └── disconnect              → Cliente desconecta
```

### Frontend (HTML5 Canvas + Socket.IO)
```
templates/index.html
├── Layout responsivo
├── Estatísticas sidebar
└── Canvas interativo

static/js/simulation.js
├── Renderização Canvas
├── Viewport controls (pan/zoom)
├── WebSocket client
└── Atualização em tempo real
```

### Fluxo de Dados
```
SUMO (TraCI:8813)
    ↓
app.py (Python)
    ↓ WebSocket
Browser (JavaScript)
    ↓ Canvas 2D
👁️ Visualização
```

## 📊 Exemplo de Output

### Console do Servidor
```
╔════════════════════════════════════════════════════════════╗
║     🚦 TRAFFIC SIMULATION WEB VISUALIZATION 🚗            ║
╚════════════════════════════════════════════════════════════╝

📡 Servidor Flask rodando em: http://localhost:5000
🔌 WebSocket ativo para atualizações em tempo real
⚡ TraCI conectando na porta: 8813

🔌 Conectando ao SUMO...
🗺️ Carregando topologia...
✅ Simulação iniciada!
🔌 Cliente conectado
```

### Interface Web
```
📊 Estatísticas
Step: 1234
Veículos: 16
Velocidade Média: 45.3 km/h
Parados: 2

Tempo Simulado: 2:03
FPS: 10
```

## 🎯 Features Implementadas

- [x] Visualização completa da rede 8x8
- [x] Renderização de veículos em movimento
- [x] Semáforos com estados em tempo real
- [x] Rota A→B destacada
- [x] Métricas de tráfego
- [x] Controles de pan/zoom
- [x] WebSocket para updates em tempo real
- [x] Interface responsiva
- [x] Legendas coloridas
- [x] Auto-centralização

## 🔧 Configuração Técnica

### Dependências Python
```python
flask>=2.3.0          # Web framework
flask-socketio>=5.3.0 # WebSocket support
python-socketio>=5.9.0
eventlet>=0.33.0      # Async server
traci>=1.14.0         # SUMO interface
```

### Dependências JavaScript
```html
Socket.IO Client 4.5.4 (CDN)
HTML5 Canvas API
```

### Portas Utilizadas
- **5000**: Flask web server
- **8813**: SUMO TraCI

## 🐛 Troubleshooting

### Erro: "Simulação não inicia"
✅ **Solução**: Verifique se SUMO está rodando
```bash
docker ps | grep sumo-sim
```

### Erro: "Connection refused"
✅ **Solução**: Reinicie o container SUMO
```bash
docker stop sumo-sim
./scripts/run_sumo_docker.sh
```

### Performance baixo (FPS < 5)
✅ **Solução**: Reduza o zoom ou feche outras tabs do navegador

### Visualização cortada
✅ **Solução**: Clique em "Iniciar Simulação" novamente para re-centralizar

## 🚀 Próximos Passos

- [ ] Filtros de visualização (mostrar/ocultar veículos)
- [ ] Gráficos de métricas históricas
- [ ] Replay de simulações gravadas
- [ ] Múltiplas câmeras/viewports
- [ ] Export de vídeo da simulação
- [ ] Heatmap de tráfego
- [ ] Comparação de rotas alternativas

## 📝 Notas Técnicas

### Performance
- **Update Rate**: 10 FPS (0.1s por step SUMO)
- **Canvas Size**: 1200x900px
- **Zoom Range**: 0.1x - 5.0x
- **WebSocket**: Comunicação bidirecional

### Rendering
- **Ordem de desenho**: Edges → Nodes → Traffic Lights → Vehicles
- **Cores adaptativas**: Por tipo de via e veículo
- **Shadow effects**: Semáforos com glow
- **Route overlay**: Rota A→B em roxo tracejado

---

**✨ Visualização Web Completa e Funcional!** 🎉
