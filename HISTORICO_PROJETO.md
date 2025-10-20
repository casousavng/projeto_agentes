# 📚 Histórico do Projeto - Simulação de Tráfego SPADE

Este documento consolida toda a evolução do projeto, decisões técnicas, problemas resolvidos e lições aprendidas.

---

## 🎯 Objetivos Alcançados

### Objetivo Principal
Criar um modelo de testes que utilize **Python + SPADE + Prosody + TraCI + SUMO** para simular tráfego urbano com agentes inteligentes.

### Componentes Implementados

#### ✅ 1. Infraestrutura XMPP
- **Prosody Server**: Rodando em Docker container
- **Porta**: 5222 (XMPP)
- **Domínio**: localhost
- **Registro de agentes**: Via `prosodyctl`

#### ✅ 2. Agentes SPADE
Implementados 4 tipos de agentes:

1. **TrafficLight Agent** (24 agentes)
   - Controla semáforos em intersecções
   - Lógica inteligente baseada em densidade de tráfego
   - Comunicação com agentes vizinhos
   - Estados: Verde, Amarelo, Vermelho

2. **Car Agent**
   - Busca rotas ótimas entre origem e destino
   - Respeita semáforos e limites de velocidade
   - Comportamento realista de tráfego

3. **Ambulance Agent**
   - Modo urgência com prioridade
   - Solicita abertura de semáforos
   - Velocidade aumentada

4. **Pedestrian Agent**
   - Atravessa ruas em faixas de pedestres
   - Aguarda sinal verde

#### ✅ 3. Simulação SUMO
- **Rede**: Grid 8x8 (64 nós, 112 arestas)
- **Cenário**: `scenarios/grid_8x8/`
- **Interface**: TraCI (Python ↔ SUMO)
- **Tipos de vias**: Highway, Arterial, Collector, Local
- **GUI**: Via X11 no macOS M1

#### ✅ 4. Teste de Viagem Completa
- **Arquivo**: `test_journey.py`
- **Duração**: 166.3 segundos simulados
- **Distância**: 1.97 km
- **Origem**: Nó 0 (canto noroeste)
- **Destino**: Nó 63 (canto sudeste)
- **Resultado**: ✅ Sucesso - carro chegou ao destino

#### ✅ 5. Coleta de Dados
- **Database**: SQLite (`simulation_data.db`)
- **Snapshots**: 167 (coletados a cada 10 steps = 1s)
- **Tabelas**: 
  - `simulation_snapshots`
  - `vehicles`
  - `traffic_lights`
  - `network_topology`
  - `statistics`
- **Tamanho**: 496 KB

#### ✅ 6. Visualização Pygame
- **Arquivo**: `visualize_pygame.py`
- **Resolução**: 1400x900 pixels
- **FPS**: 10 (ajustável)
- **Recursos**:
  - Renderização 2D da cidade 8x8
  - Animação de semáforos (verde/amarelo/vermelho)
  - Veículos coloridos por tipo
  - Controles interativos (Play/Pause, velocidade, navegação)
  - Sidebar com estatísticas em tempo real
  - Barra de progresso
  - Legenda visual

---

## 🏗️ Arquitetura do Sistema

### Camadas da Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                  Visualização Pygame                    │
│              (visualize_pygame.py)                      │
│  - Renderização 2D                                      │
│  - Controles interativos                                │
│  - Interface gráfica                                    │
└─────────────────────────────────────────────────────────┘
                         ▲
                         │ Lê dados
                         │
┌─────────────────────────────────────────────────────────┐
│              Banco de Dados SQLite                      │
│            (simulation_data.db)                         │
│  - Snapshots da simulação                               │
│  - Histórico de veículos                                │
│  - Estados de semáforos                                 │
│  - Estatísticas agregadas                               │
└─────────────────────────────────────────────────────────┘
                         ▲
                         │ Coleta dados
                         │
┌─────────────────────────────────────────────────────────┐
│           Simulação SPADE + SUMO                        │
│              (test_journey.py)                          │
│  - Agentes SPADE (comunicação XMPP)                     │
│  - SUMO (simulação de tráfego)                          │
│  - TraCI (interface Python ↔ SUMO)                      │
│  - DataCollector (persistência)                         │
└─────────────────────────────────────────────────────────┘
                         ▲
                         │ Comunicação
                         │
┌─────────────────────────────────────────────────────────┐
│            Servidor Prosody XMPP                        │
│              (Docker container)                         │
│  - Protocolo: XMPP                                      │
│  - Porta: 5222                                          │
│  - Domínio: localhost                                   │
└─────────────────────────────────────────────────────────┘
```

### Fluxo de Dados

1. **Simulação** (test_journey.py):
   - Inicia Prosody Docker
   - Registra agentes XMPP
   - Cria agentes SPADE (semáforos, carros)
   - Inicia SUMO com TraCI
   - Coleta dados a cada step
   - Salva snapshots no SQLite

2. **Armazenamento** (simulation_data.db):
   - Persiste estado completo da simulação
   - 167 snapshots (steps 10-1670)
   - Permite replay independente

3. **Visualização** (visualize_pygame.py):
   - Lê snapshots do banco
   - Renderiza cidade, semáforos, veículos
   - Permite controle de velocidade e navegação
   - Totalmente desacoplado da simulação

---

## 🔧 Problemas Resolvidos

### 1. TraCI Connection Issues (Docker + macOS M1)
**Problema**: Conexão TraCI fechava imediatamente ao tentar usar SUMO via Docker.

**Causa**: 
- SUMO em Docker termina antes de TraCI conectar
- Timing issues entre container e host
- X11 forwarding complexo no macOS M1

**Solução**: 
- ✅ **SUMO Local**: Instalação nativa do SUMO no macOS
- ✅ **Coleta Offline**: Separar simulação de visualização
- ✅ **SQLite Replay**: Gravar dados para replay posterior

### 2. Thread Safety no DataCollector
**Problema**: `sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread`

**Causa**: Conexão SQLite criada no `__init__` não funcionava em threads diferentes (SPADE usa asyncio).

**Solução**:
```python
def _get_connection(self):
    """Lazy connection pattern - thread-safe"""
    thread_id = threading.get_ident()
    if thread_id not in self._connections:
        self._connections[thread_id] = sqlite3.connect(self.db_path)
    return self._connections[thread_id]
```

### 3. Visualização Web (Flask + Canvas)
**Problema**: 
- WebSocket overhead
- JavaScript assíncrono complexo
- 3 linguagens diferentes (Python/HTML/JS)
- Canvas vazio, sem dados renderizados
- Timing issues entre backend e frontend

**Tentativas**:
1. ❌ Flask + SocketIO + Canvas HTML5
2. ❌ Reconstrução completa do frontend
3. ❌ Múltiplas correções de sincronização

**Solução Final**: 
✅ **Pygame** - Visualização nativa em Python
- Performance superior
- Loop de renderização direto
- Controles nativos de teclado
- Debugging simplificado
- Uma única linguagem

### 4. Formato de Dados Inconsistente
**Problema**: Backend enviava arrays mas frontend esperava objetos.

**Solução**:
- Padronização: Sempre usar arrays para `vehicles` e `traffic_lights`
- Documentação clara da estrutura de dados
- Type hints nos métodos

---

## 📊 Rede 8x8 - Especificações

### Topologia
```
Nós: 64 (grid 8x8)
Arestas: 112 (bidirecionais)
Distância entre nós: ~200m
Área total: ~1.6km × 1.6km
```

### Tipos de Vias

| Tipo | Velocidade Máx | Prioridade | Cor (visualização) |
|------|----------------|------------|--------------------|
| Highway | 80 km/h | Alta | Vermelho |
| Arterial | 60 km/h | Média-Alta | Laranja |
| Collector | 50 km/h | Média | Verde |
| Local | 30 km/h | Baixa | Cinza |

### Semáforos
- **Total**: 24 agentes (intersecções principais)
- **Lógica**: Inteligente baseada em densidade
- **Ciclo**: Adaptativo (não fixo)
- **Comunicação**: XMPP entre semáforos vizinhos

---

## 🚀 Como Usar o Sistema

### 1. Pré-requisitos
```bash
# Python 3.9+
python --version

# Ambiente virtual
python -m venv venv
source venv/bin/activate  # macOS/Linux

# Dependências
pip install -r requirements.txt
```

### 2. Iniciar Prosody (Docker)
```bash
# Iniciar container
docker run -d --name prosody -p 5222:5222 prosody/prosody

# Verificar status
docker ps | grep prosody
```

### 3. Executar Simulação
```bash
# Coletar dados da simulação
python test_journey.py

# Resultado: simulation_data.db (167 snapshots)
```

### 4. Visualizar com Pygame
```bash
# Abrir visualização interativa
python visualize_pygame.py

# Controles:
# ESPAÇO - Play/Pause
# ←→ - Navegar frames
# ↑↓ - Ajustar velocidade
# R - Reiniciar
# Q - Sair
```

---

## 📁 Estrutura do Projeto

```
projeto_agentes/
│
├── agents/                      # Agentes SPADE
│   ├── __init__.py
│   ├── base_agent.py           # Classe base
│   ├── traffic_light.py        # Semáforos inteligentes
│   ├── car.py                  # Carros normais
│   ├── ambulance.py            # Ambulâncias (urgência)
│   └── pedestrian.py           # Pedestres
│
├── config/                      # Configurações
│   ├── __init__.py
│   └── simulation_config.py    # Parâmetros da simulação
│
├── scenarios/                   # Cenários SUMO
│   └── grid_8x8/               # Rede 8x8
│       ├── network.net.xml     # Topologia da rede
│       ├── routes.rou.xml      # Rotas de veículos
│       ├── simulation.sumocfg  # Configuração SUMO
│       └── gui-settings.xml    # Configurações da GUI
│
├── scripts/                     # Scripts auxiliares
│   ├── setup_prosody.sh        # Setup do Prosody
│   ├── register_agents.sh      # Registro de agentes
│   └── cleanup.sh              # Limpeza do ambiente
│
├── utils/                       # Utilitários
│   ├── __init__.py
│   ├── data_collector.py       # SQLite wrapper
│   ├── routing.py              # Algoritmos de rota
│   └── xmpp_manager.py         # Gerenciamento XMPP
│
├── test_journey.py              # 🎯 Teste principal (viagem A→B)
├── collect_simulation_data.py   # Coleta de dados standalone
├── visualize_pygame.py          # 🎮 Visualização Pygame
│
├── simulation_data.db           # 💾 Banco de dados (167 snapshots)
├── requirements.txt             # Dependências Python
├── README.md                    # Documentação principal
└── HISTORICO_PROJETO.md         # Este arquivo
```

---

## 🎓 Lições Aprendidas

### 1. Separação de Preocupações
**Decisão correta**: Desacoplar simulação de visualização via SQLite.

**Benefícios**:
- Simulação pode rodar sem GUI (headless)
- Visualização pode ser desenvolvida independentemente
- Dados persistidos permitem análises posteriores
- Replay ilimitado sem re-simular

### 2. Escolha de Tecnologia para Visualização
**Tentativa inicial**: Flask + WebSocket + HTML Canvas
**Problema**: Overhead de comunicação, complexidade multi-linguagem

**Solução final**: Pygame
**Por quê funciona**:
- Performance nativa (sem rede)
- Simplicidade (uma linguagem)
- Controle total sobre renderização
- Debugging direto no Python

### 3. Thread Safety em Ambientes Assíncronos
SPADE usa asyncio, mas SQLite não é thread-safe por padrão.

**Padrão implementado**: Lazy connection per thread
```python
self._connections = {}  # Dict[thread_id, Connection]
```

### 4. Dados Estruturados
Sempre documentar e padronizar estruturas de dados:
```python
snapshot = {
    'step': int,
    'vehicles': [{'id': str, 'x': float, 'y': float, ...}],
    'traffic_lights': [{'id': str, 'state': str, 'x': float, ...}],
    'stats': {'total_vehicles': int, 'avg_speed': float, ...}
}
```

---

## 📈 Métricas da Simulação

### Teste de Viagem (test_journey.py)

| Métrica | Valor |
|---------|-------|
| **Duração total** | 166.3 segundos |
| **Distância percorrida** | 1.97 km |
| **Velocidade média** | ~43 km/h |
| **Nós visitados** | 15 nós |
| **Semáforos respeitados** | 8 semáforos |
| **Steps simulados** | 1,664 |
| **Snapshots coletados** | 167 |

### Performance

| Componente | Métrica |
|------------|---------|
| **SPADE Agents** | 24 traffic lights ativos |
| **SUMO Simulation** | 60 FPS (real-time) |
| **Data Collection** | 10 snapshots/segundo |
| **SQLite Write** | ~3 KB/snapshot |
| **Pygame Rendering** | 10-60 FPS (ajustável) |

---

## 🔮 Possíveis Extensões Futuras

### 1. Análise de Dados
- [ ] Estatísticas agregadas (tempo de espera, congestionamento)
- [ ] Comparação de diferentes estratégias de semáforos
- [ ] Machine Learning para otimização de rotas

### 2. Novos Agentes
- [ ] Ônibus com paradas fixas
- [ ] Bicicletas com faixas dedicadas
- [ ] Caminhões com restrições de horário

### 3. Cenários Complexos
- [ ] Rede real (importar de OpenStreetMap)
- [ ] Eventos (acidentes, obras, fechamento de vias)
- [ ] Padrões de tráfego por hora do dia

### 4. Visualização Avançada
- [ ] Heatmap de congestionamento
- [ ] Replay com controle de timeline
- [ ] Exportação para vídeo (GIF/MP4)
- [ ] Dashboard web de análise (Dash/Streamlit)

### 5. Comunicação V2V/V2I
- [ ] Veículos autônomos negociando ultrapassagens
- [ ] Comboios de veículos (platooning)
- [ ] Alerta de acidentes à frente

---

## 📚 Referências Técnicas

### Frameworks e Bibliotecas
- **SPADE**: https://spade-mas.readthedocs.io/
- **SUMO**: https://eclipse.dev/sumo/
- **TraCI**: https://sumo.dlr.de/docs/TraCI.html
- **Pygame**: https://www.pygame.org/
- **Prosody**: https://prosody.im/

### Protocolos
- **XMPP**: https://xmpp.org/
- **FIPA ACL**: http://www.fipa.org/specs/fipa00061/

### Documentação do Projeto
- **README.md**: Guia rápido de uso
- **HISTORICO_PROJETO.md**: Este documento (histórico completo)
- **scenarios/grid_8x8/README.md**: Detalhes da rede 8x8

---

## 🏆 Conclusão

Este projeto demonstrou com sucesso a viabilidade de simular tráfego urbano usando agentes inteligentes (SPADE) integrados com um simulador de tráfego realista (SUMO).

### Principais Conquistas:
✅ Arquitetura multiagente funcional
✅ Comunicação XMPP entre agentes
✅ Integração SPADE ↔ SUMO via TraCI
✅ Coleta e persistência de dados
✅ Visualização interativa em Pygame
✅ Sistema modular e extensível

### Aprendizados Chave:
- Importância do desacoplamento (simulação vs visualização)
- Thread safety em ambientes assíncronos
- Escolha de tecnologia adequada ao problema
- Valor de dados persistidos para análise

O sistema está pronto para ser estendido com novos tipos de agentes, cenários mais complexos e análises avançadas de tráfego.

---

**Última atualização**: 20 de outubro de 2025
**Versão do Projeto**: 1.0 - Pygame Visualization
**Status**: ✅ Funcional e documentado
