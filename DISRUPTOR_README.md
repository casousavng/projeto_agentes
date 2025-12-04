# 🚧 Sistema de Disrupção de Vias - Agente Disruptor

## ✅ Implementação Completa

O sistema de disrupção foi implementado com sucesso! O **DisruptorAgent** permite bloquear aleatoriamente 6 vias da rede, forçando os veículos a recalcular suas rotas.

## 🚀 Como Usar

### 1. Configurar o Prosody (primeira vez ou após reiniciar)

```bash
# Iniciar servidor Prosody
./scripts/setup_prosody.sh

# Registrar TODOS os agentes (incluindo o DisruptorAgent)
./scripts/register_all_agents.sh
```

### 2. Executar a Simulação

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Executar simulação
python3 live_dynamic_spade.py
```

### 3. Controles

| Tecla | Ação |
|-------|------|
| **ESPAÇO** | 🚧 Ativar/Desativar disrupção (bloqueia 6 vias aleatórias) |
| **P** | ⏯️ Pausar/Continuar simulação |
| **+/-** | ⚡ Ajustar velocidade da simulação |
| **ESC** | 🚪 Sair |

## 🎯 Funcionalidades

### 🚧 Disrupção de Vias
- Pressione **ESPAÇO** para ativar bloqueios
- 6 vias são selecionadas **aleatoriamente**
- Vias bloqueadas aparecem em **VERMELHO** com um **X branco**
- Todos os veículos recalculam rotas automaticamente (A*)

### 🚗 Roteamento Inteligente
- Algoritmo **A*** modificado ignora vias bloqueadas
- Veículos encontram **rotas alternativas** automaticamente
- Funciona para:
  - Carros normais (azul)
  - Ambulâncias (vermelho) 🚑
  - Veículo Journey A→B (roxo)

### 📊 Visualização
- **Vias normais**: Cinza com linha amarela central
- **Vias bloqueadas**: Vermelho com X branco
- **Painel lateral** mostra:
  - Estado: ATIVO/INATIVO
  - Número de vias bloqueadas

## 🔄 Fluxo de Comunicação

```
Usuário pressiona ESPAÇO
    ↓
DisruptorAgent bloqueia 6 vias aleatórias
    ↓
Envia mensagem XMPP → CoordinatorAgent
    ↓
CoordinatorAgent faz broadcast → Todos os VehicleAgents
    ↓
Veículos recalculam rotas (A* ignora vias bloqueadas)
    ↓
Interface Pygame atualiza (vias vermelhas)
```

## 🎨 Agentes SPADE

Total: **37 agentes**
- 1 CoordinatorAgent
- 1 **DisruptorAgent** (novo!)
- 15 VehicleAgents
- 20 TrafficLightAgents (10 pares H+V)

## 📝 Arquivos Modificados

1. **`agents/spade_traffic_agents.py`**
   - ✅ Adicionado `DisruptorAgent`
   - ✅ Atualizado `CoordinatorAgent` (blocked_edges, broadcast)
   - ✅ Atualizado `VehicleAgent` (A* modificado)

2. **`live_dynamic_spade.py`**
   - ✅ Integração do DisruptorAgent
   - ✅ Visualização de vias bloqueadas
   - ✅ Controles atualizados

3. **`scripts/register_all_agents.sh`** (novo!)
   - ✅ Registro automático de todos os agentes

## 🐛 Solução de Problemas

### Erro: "No appropriate login method"
```bash
# Solução: Registrar agentes no Prosody
./scripts/register_all_agents.sh
```

### Prosody não está rodando
```bash
# Verificar se Docker está ativo
docker ps

# Reiniciar Prosody
./scripts/setup_prosody.sh
```

### Agentes não conectam
```bash
# Verificar se agentes estão registrados
docker exec -it prosody prosodyctl listusers localhost

# Se necessário, re-registrar
./scripts/register_all_agents.sh
```

## 🎓 Detalhes Técnicos

### DisruptorAgent
- **JID**: `disruptor@localhost`
- **Função**: Gerenciar bloqueios de vias
- **Comunicação**: XMPP (Prosody)
- **Método**: `toggle_disruption()` - ativa/desativa bloqueios

### Algoritmo A* Modificado
```python
for neighbor, edge_id in self.graph.get(current, []):
    # Verificar se via está bloqueada
    if edge_id in self.blocked_edges:
        continue  # Pular esta aresta completamente
    # ... resto do algoritmo A*
```

## 🎉 Pronto!

Agora você pode testar o sistema de disrupção:
1. Execute a simulação
2. Pressione **ESPAÇO** para bloquear vias
3. Observe os veículos recalculando rotas
4. Pressione **ESPAÇO** novamente para liberar

Divirta-se! 🚗💨
