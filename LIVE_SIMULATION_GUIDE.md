# 🎮 Simulação LIVE com Pygame - Guia de Uso

## 📋 Visão Geral

Este ficheiro (`live_simulation_pygame.py`) executa a simulação SPADE + SUMO **em tempo real** e renderiza no Pygame, com visual melhorado incluindo **ruas de dupla faixa**.

## 🆚 Diferenças dos Outros Ficheiros

| Ficheiro | Descrição | Dados |
|----------|-----------|-------|
| `test_journey.py` | Simulação SPADE + coleta dados | Grava em SQLite |
| `visualize_pygame.py` | Visualização de replay | Lê de SQLite |
| `live_simulation_pygame.py` | **Simulação + Visualização LIVE** | **Tempo real via TraCI** |

## ✨ Novidades Visuais

### Ruas de Dupla Faixa
As ruas agora são renderizadas com:
- **Duas faixas separadas** (ida e volta)
- **Linha divisória central** (tracejada amarela)
- **Bordas escuras** para definição
- **Cores diferentes** para cada faixa

```
   ╔═══════════════════════════╗
   ║  Faixa 1 (cinza claro)   ║
   ╠───────────────────────────╣  ← Linha divisória
   ║  Faixa 2 (cinza escuro)  ║
   ╚═══════════════════════════╝
```

## 🚀 Como Usar

### 1. Pré-requisitos

```bash
# SUMO instalado localmente (não Docker!)
sumo --version

# Prosody em Docker
docker ps | grep prosody
```

### 2. Executar

```bash
# Ativar ambiente
source venv/bin/activate

# Rodar simulação LIVE
python live_simulation_pygame.py
```

### 3. Controles

| Tecla | Ação |
|-------|------|
| `S` | **Start/Stop** simulação |
| `ESPAÇO` | **Pause/Resume** |
| `Q` | **Sair** |

## 🎯 Fluxo de Funcionamento

1. **Aperta `S`**:
   - Inicia container Prosody (se não estiver rodando)
   - Registra 24 agentes de semáforo no XMPP
   - Conecta ao SUMO via TraCI
   - Carrega topologia da rede (64 nós, 112 arestas)
   - Adiciona veículo `car_journey` (viagem A→B)
   - Inicia loop de simulação em thread separada

2. **Loop de Simulação** (10 FPS):
   - SUMO avança 1 step (0.1s)
   - TraCI coleta posições de veículos
   - TraCI coleta estados de semáforos
   - Pygame renderiza tudo em tempo real

3. **Aperta `ESPAÇO`**:
   - Pausa/Resume simulação

4. **Aperta `S` novamente ou `Q`**:
   - Para simulação
   - Fecha conexão TraCI
   - Fecha Pygame

## 🏗️ Arquitetura

```
┌─────────────────────────────────────┐
│      Pygame (Thread Principal)      │
│   - Renderização 10 FPS             │
│   - Interface gráfica               │
│   - Controles de teclado            │
└─────────────────────────────────────┘
              ↑
              │ Queue (dados)
              │
┌─────────────────────────────────────┐
│   Thread de Simulação (Separada)   │
│   - SPADE agents (futuro)           │
│   - SUMO via TraCI                  │
│   - Coleta dados em tempo real      │
└─────────────────────────────────────┘
              ↑
              │ TraCI
              │
┌─────────────────────────────────────┐
│          SUMO Simulation            │
│   - Física de veículos              │
│   - Controle de semáforos           │
└─────────────────────────────────────┘
```

## 🎨 Visual Melhorado

### Antes (visualize_pygame.py)
- Ruas simples: linha única cinza
- Sem diferenciação de faixas

### Agora (live_simulation_pygame.py)
- **Ruas duplas**: duas faixas separadas
- **Linha divisória**: amarela tracejada
- **Bordas**: contorno escuro
- **Realismo**: parece mapa real de ruas

## 📊 Dados em Tempo Real

O Pygame recebe dados atualizados a cada 0.1s:

```python
{
    'vehicles': [
        {
            'id': 'car_journey',
            'x': 245.6,
            'y': 128.3,
            'speed': 45.2,  # km/h
            'angle': 90.0,
            'type': 'journey'
        }
    ],
    'traffic_lights': [
        {
            'id': 'tl_1_1',
            'x': 200.0,
            'y': 200.0,
            'state': 'GGrrGGrr'  # G=verde, r=vermelho
        }
    ],
    'stats': {
        'step': 142,
        'total_vehicles': 1,
        'avg_speed': 45.2,
        'total_waiting': 0
    }
}
```

## 🐛 Troubleshooting

### Erro: "sumo: command not found"

```bash
# Instalar SUMO localmente
# macOS:
brew install sumo

# Linux:
sudo apt-get install sumo sumo-tools

# Verificar:
sumo --version
```

### Erro: "Cannot connect to TraCI"

```bash
# Verificar se SUMO está no PATH
which sumo

# Testar SUMO manualmente
sumo -c scenarios/grid_8x8/simulation.sumocfg --start --quit-on-end
```

### Erro: "Prosody connection failed"

```bash
# Iniciar Prosody manualmente
docker run -d --name prosody -p 5222:5222 prosody/prosody

# Verificar
docker ps | grep prosody
```

## 🔄 Comparação: Replay vs LIVE

### visualize_pygame.py (Replay)
✅ Não precisa SUMO rodando  
✅ Replay instantâneo  
✅ Navegar frames (←→)  
✅ Ajustar velocidade (0.25x-8x)  
❌ Dados pré-gravados (não modificável)  

### live_simulation_pygame.py (LIVE)
✅ Simulação em tempo real  
✅ Pode modificar parâmetros durante execução  
✅ Ver comportamento emergente  
✅ Ruas mais bonitas (dupla faixa)  
❌ Precisa SUMO instalado localmente  
❌ Mais lento (depende do SUMO)  

## 🎯 Próximos Passos

- [ ] Integrar agentes SPADE (semáforos inteligentes)
- [ ] Adicionar mais veículos dinâmicos
- [ ] Permitir intervenção manual (mudar semáforo)
- [ ] Exportar dados para análise posterior
- [ ] Adicionar heatmap de congestionamento

---

**Ficheiro**: `live_simulation_pygame.py`  
**Versão**: 1.0 - LIVE Simulation  
**Data**: Outubro 2025
