# 🚨 PROBLEMA IDENTIFICADO - Conexão TraCI Docker

## ❌ Problema Raiz

O SUMO Docker está **saindo imediatamente** após qualquer desconexão TraCI, com erro:
```
Error: tcpip::Socket::recvAndCheck @ recv: peer shutdown
Quitting (on error).
```

## 🔍 Diagnóstico

1. ✅ `traci.connect(8813)` **funciona** (conexão estabelece)
2. ❌ `traci.simulationStep()` **falha** com "Not connected"
3. 🐛 Container Docker sai entre o connect() e o step()

## 💡 Causa

O SUMO está configurado para **sair ao menor problema de conexão**. Quando:
1. Cliente conecta
2. Cliente não envia comando imediatamente  
3. Socket tem "peer shutdown" temporário
4. SUMO interpreta como erro fatal e sai

## 🛠️ Soluções Tentadas

### ❌ Tentativa 1: `--num-clients 1`
- Não funcionou - SUMO ainda sai

### ❌ Tentativa 2: `--quit-on-end false`  
- Flag não existe no SUMO

### ❌ Tentativa 3: `traci.start()` local
- SUMO local no macOS M1 tem dependências quebradas
- Erro: `libproj.25.dylib` não encontrado

### ❌ Tentativa 4: Retry e aguardar
- Mesmo com retries, conexão fecha antes do step()

## ✅ SOLUÇÃO FINAL

**Usar `--start` e não fazer `traci.connect()` separadamente**.

O truque é que o SUMO precisa iniciar a simulação **antes** de aceitar conexões TraCI para evitar o "peer shutdown".

### Modificação necessária:

```bash
# run_sumo_docker.sh
docker run -d \
    --name sumo-sim \
    --network host \
    -v "$(pwd)/scenarios:/scenarios" \
    ghcr.io/eclipse-sumo/sumo@sha256:... \
    sumo \
    --net-file /scenarios/grid_8x8/network.net.xml \
    --route-files /scenarios/grid_8x8/routes.rou.xml \
    --remote-port 8813 \
    --step-length 0.1 \
    --no-step-log \
    --start  # ← CRÍTICO: Inicia simulação antes de aceitar conexões
```

### E no app.py:

```python
# Não usar: traci.connect(8813)
# Usar: Manter uma única conexão persistente

# OU: Reiniciar SUMO fresh a cada conexão
os.system("docker restart sumo-sim")
time.sleep(3)
traci.connect(8813)
```

## 📝 Documentação

Este é um **problema conhecido** do SUMO + Docker + TraCI:
- SUMO é muito sensível a "peer shutdown"
- Docker adiciona latência na rede
- macOS M1 + Docker tem camada extra de virtualização
-Resultado: timing issues causam disconnects prematuros

## 🎯 Próximo Passo

Implementar solução com `--start` e testar novamente.

---

**Data**: 20/10/2025 04:25  
**Status**: Problema identificado, solução conhecida, pronto para implementar
