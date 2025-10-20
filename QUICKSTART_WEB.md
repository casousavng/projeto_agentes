# 🌐 GUIA RÁPIDO - Visualização Web

## 🚀 Início Rápido (2 Comandos)

### Terminal 1 - SUMO
```bash
./scripts/run_sumo_docker.sh
```

### Terminal 2 - Web App
```bash
./scripts/run_web_app.sh
```

### Browser
```
http://localhost:5000
```

Clique em **"▶️ Iniciar Simulação"** e pronto! 🎉

---

## 📋 O Que Você Vai Ver

### 🗺️ Mapa da Cidade
- **Rede 8x8** completa (64 cruzamentos, 314 ruas)
- **4 tipos de vias** com cores diferentes:
  - 🔴 Highway (80 km/h)
  - 🟠 Arterial (60 km/h)  
  - 🟢 Collector (50 km/h)
  - ⚪ Local (30 km/h)

### 🚗 Veículos em Movimento
- 🚕 **Amarelo**: Carro fazendo a jornada A→B (principal)
- 🚙 **Azul**: Tráfego normal (15 carros)
- 🚑 **Vermelho**: Ambulâncias (se houver)

### 🚦 Semáforos Inteligentes
- 🟢 Verde: Pode passar
- 🟡 Amarelo: Atenção
- 🔴 Vermelho: Pare
- **Número**: Veículos esperando

### 🛣️ Rota A→B
- **Linha tracejada roxa**: Caminho escolhido pelo carro amarelo
- Calculado dinamicamente considerando:
  - ✅ Distância entre pontos
  - ✅ Tipo de via (prefere highways)
  - ✅ Tráfego nos cruzamentos
  - ✅ Estado dos semáforos

---

## 🎮 Controles

| Ação | Como Fazer |
|------|-----------|
| **Mover câmera** | Arraste com o mouse |
| **Zoom in/out** | Scroll do mouse |
| **Iniciar** | Botão "▶️ Iniciar Simulação" |
| **Parar** | Botão "⏹️ Parar Simulação" |

---

## 📊 Métricas Exibidas

### Sidebar Esquerdo
- **Step**: Número do passo da simulação
- **Veículos**: Quantidade ativa na cidade
- **Velocidade Média**: Média da frota (km/h)
- **Parados**: Veículos com velocidade < 1 km/h

### Painel Inferior
- **Tempo Simulado**: Tempo real de simulação (MM:SS)
- **FPS**: Frames por segundo (qualidade da visualização)

---

## ✨ Features Especiais

### 🎯 Viagem A→B em Destaque
O **carro amarelo** é o protagonista:
- Vai do canto inferior esquerdo (A) ao superior direito (B)
- **Escolhe a melhor rota** baseado em:
  - Distância
  - Tipo de via
  - Tráfego
  - Semáforos

Observe como ele **prefere highways** (vias vermelhas) para chegar mais rápido!

### 🧠 Decisões Inteligentes

**Exemplo real da simulação**:
```
Origem (A): n0_0 (canto inferior esquerdo)
Destino (B): n7_7 (canto superior direito)

Rota escolhida:
1. Sobe pela coluna 0 (local 30km/h) até n3_0
2. Vira para highway na coluna 3 (80km/h) ← INTELIGENTE!
3. Acelera de 0 → 84.8 km/h na highway
4. Segue até n7_3
5. Vira para destino n7_7

Resultado:
✅ 1.97 km em 2:46 minutos
✅ Velocidade média: 42.5 km/h
✅ Apenas 1 parada (semáforo)
```

### 🚦 Semáforos Adaptativos
Os semáforos ajustam seu tempo baseado no tráfego:
- **Muito tráfego** (>5 carros esperando) → Verde fica +5s
- **Pouco tráfego** (<2 carros) → Verde reduz -3s
- Duração: 15s a 60s (dinâmico)

---

## 🎨 Visualização

### Zoom Inteligente
- **Zoom baixo** (visão geral):
  - Vê toda a cidade
  - Menos detalhes
  
- **Zoom alto** (detalhes):
  - Velocidade dos carros
  - Número de veículos esperando nos semáforos
  - Grid de referência

### Cores Significativas
| Elemento | Cor | Significado |
|----------|-----|-------------|
| Via vermelha | 🔴 | Highway - Mais rápida |
| Via laranja | 🟠 | Arterial - Rápida |
| Via verde | 🟢 | Collector - Média |
| Via cinza | ⚪ | Local - Lenta |
| Carro amarelo | 🟡 | Jornada A→B |
| Carro azul | 🔵 | Tráfego normal |
| Linha roxa | 🟣 | Rota planejada |

---

## 🔥 Experimente

### Observe Estes Comportamentos:

1. **Aceleração/Frenagem**
   - Carro amarelo acelera até 84 km/h na highway
   - Desacelera suavemente ao chegar em cruzamentos
   - Para completamente em semáforos vermelhos

2. **Escolha de Rota**
   - Compare a rota escolhida (linha roxa) com o caminho mais curto
   - Note como o carro **evita vias lentas** (cinzas)
   - Prefere **highways** mesmo que mais longas

3. **Interação com Tráfego**
   - Veja outros carros (azuis) circulando
   - Observe semáforos ficando vermelhos quando há fila
   - Tráfego influencia a velocidade média

4. **Semáforos Inteligentes**
   - Semáforos com muitos carros esperando (número alto)
   - Verde fica mais tempo em cruzamentos congestionados
   - Coordenação entre semáforos vizinhos

---

## 🐛 Problemas Comuns

### "Não consigo iniciar"
```bash
# Reinicie o SUMO
docker stop sumo-sim
./scripts/run_sumo_docker.sh
```

### "Visualização está vazia"
1. Verifique se SUMO está rodando: `docker ps | grep sumo`
2. Clique em "Iniciar Simulação" novamente

### "Tela congelou"
- Recarregue a página (F5)
- Ou clique em "Parar" e depois "Iniciar"

---

## 🎯 Exemplo Completo

### Passo a Passo para Ver a Magia Acontecer:

1. **Inicie SUMO** (Terminal 1)
   ```bash
   ./scripts/run_sumo_docker.sh
   ```
   Aguarde: `✅ SUMO rodando...`

2. **Inicie Web App** (Terminal 2)
   ```bash
   ./scripts/run_web_app.sh
   ```
   Aguarde: `Running on http://0.0.0.0:5000`

3. **Abra Browser**
   ```
   http://localhost:5000
   ```

4. **Inicie Simulação**
   - Clique no botão verde "▶️ Iniciar Simulação"
   - Aguarde 2-3 segundos (carregando rede)

5. **Observe!**
   - 🚕 Carro amarelo sai de n0_0
   - 🛣️ Linha roxa mostra a rota
   - 🚦 Semáforos mudando de cor
   - 📊 Estatísticas atualizando em tempo real
   - 🎯 Carro chega em n7_7 após ~2-3 minutos

6. **Interaja!**
   - Arraste para seguir o carro
   - Zoom para ver detalhes
   - Observe a velocidade em tempo real

---

## 🏆 Conquistas da Simulação

✅ **Rede Realista**: 8x8 com 4 tipos de vias  
✅ **Roteamento Inteligente**: Considera múltiplos fatores  
✅ **Visualização em Tempo Real**: 10 FPS via WebSocket  
✅ **Semáforos Adaptativos**: Ajustam baseado no tráfego  
✅ **Métricas Completas**: 9 indicadores diferentes  
✅ **Interface Moderna**: HTML5 Canvas interativo  
✅ **100% Funcional**: Do backend ao frontend  

---

**🎉 Aproveite a visualização da sua cidade inteligente!**
