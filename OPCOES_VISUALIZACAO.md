# 🚀 Como Executar a Simulação LIVE

## 📌 Situação Atual

Você tem agora **3 opções** de visualização:

### Opção 1: **Replay com Dados Existentes** (✅ FUNCIONANDO)
```bash
python visualize_pygame.py
```
- ✅ Não precisa de SUMO
- ✅ 167 snapshots já coletados
- ✅ Funciona imediatamente
- ✅ Controle total (pause, velocidade, navegação)

---

### Opção 2: **Simulação LIVE** (⚙️ REQUER SETUP)
```bash
python live_simulation_pygame.py
```
- ✨ **Ruas duplas bonitas** (nova feature)
- 🔴 Requer SUMO instalado localmente
- 🔴 Requer dependências (proj, gdal, etc)

---

## 🛠️ Setup para Simulação LIVE

Se quiser usar a simulação LIVE com as ruas bonitas, siga estes passos:

### 1. Instalar SUMO via Homebrew

```bash
# Instalar SUMO
brew install sumo

# Verificar instalação
sumo --version
# Deve mostrar: Eclipse SUMO sumo Version 1.x.x

# Adicionar ao PATH (adicione ao ~/.zshrc)
export SUMO_HOME="/opt/homebrew/opt/sumo/share/sumo"
export PATH="/opt/homebrew/opt/sumo/bin:$PATH"

# Recarregar terminal
source ~/.zshrc
```

### 2. Testar SUMO

```bash
# Testar com o cenário grid_8x8
sumo -c scenarios/grid_8x8/simulation.sumocfg --start --quit-on-end
```

### 3. Executar Simulação LIVE

```bash
# Ativar ambiente
source venv/bin/activate

# Rodar
python live_simulation_pygame.py

# Apertar 'S' para iniciar
```

---

## 🎨 **RECOMENDAÇÃO**: Adaptar Replay para Ruas Duplas

Como a instalação do SUMO pode ser complexa, sugiro **adaptar o visualize_pygame.py** (que já funciona) para ter as ruas bonitas também!

Quer que eu faça isso? Vou:
1. Copiar `visualize_pygame.py` → `visualize_pygame_v2.py`
2. Adicionar a função `draw_dual_lane_road()` do live_simulation
3. Melhorar o visual sem quebrar nada

Dessa forma você terá o melhor dos dois mundos:
- ✅ Visualização que funciona (não precisa SUMO)
- ✅ Ruas duplas bonitas (visual melhorado)
- ✅ Todos os controles (pause, velocidade, navegação)

**Responda "sim" se quiser que eu crie essa versão melhorada!**

---

## 📊 Comparação das Opções

| Feature | visualize_pygame.py | live_simulation_pygame.py | visualize_pygame_v2.py |
|---------|---------------------|---------------------------|------------------------|
| **Funciona agora** | ✅ Sim | ❌ Requer setup | ✅ Sim |
| **Ruas bonitas** | ❌ Simples | ✅ Duplas | ✅ Duplas |
| **Precisa SUMO** | ❌ Não | ✅ Sim | ❌ Não |
| **Controles** | ✅ Completos | ⚠️ Básicos | ✅ Completos |
| **Performance** | ✅ Rápido | ⚠️ Depende SUMO | ✅ Rápido |
| **Dados** | 💾 SQLite | 🔴 Tempo real | 💾 SQLite |

---

## 💡 Resumo

**Para usar AGORA (recomendado)**:
```bash
python visualize_pygame.py
```

**Para ter ruas bonitas SEM instalar SUMO** (eu crio):
```bash
python visualize_pygame_v2.py  # (versão melhorada)
```

**Para simulação LIVE** (requer trabalho):
1. Instalar SUMO via Homebrew
2. Configurar PATH
3. Resolver dependências
4. Executar `live_simulation_pygame.py`

---

**Qual prefere? Eu recomendo criar a v2 melhorada! 🚀**
