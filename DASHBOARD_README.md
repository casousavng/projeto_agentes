# Dashboard de Métricas em Tempo Real

O `dashboard_metrics.py` é um monitor independente que apresenta métricas da simulação em tempo real, sem alterar o código principal.

## 📊 Funcionalidades

- **Latência de recálculo A\***: Média, mínimo e máximo em ms
- **Custos de rota**: Comparação entre rotas originais e recalculadas
- **Penalizações**: Semáforos e tráfego agregados
- **Atualização automática**: Refresh configurável (padrão: 2s)
- **Dois modos de visualização**:
  - **Avançado** (com `rich`): Layout colorido e organizado
  - **Básico** (fallback): Texto simples sem dependências

## 🚀 Como Usar

### 1. Instalar dependências (opcional mas recomendado)

```zsh
pip install rich
```

Se não instalar `rich`, o dashboard funciona em modo texto básico.

### 2. Executar a simulação

```zsh
python live_dynamic_spade.py
```

### 3. Em outro terminal, lançar o dashboard

```zsh
python dashboard_metrics.py
```

Ou com parâmetros personalizados:

```zsh
# Atualizar a cada 1 segundo
python dashboard_metrics.py --refresh 1.0

# Usar pasta diferente
python dashboard_metrics.py --metrics-dir caminho/para/metrics
```

## ⌨️ Controlos

- **Ctrl+C**: Sair do dashboard

## 📂 Requisitos

- A pasta `metrics/` deve existir com os ficheiros CSV gerados pela simulação:
  - `recalc_latency.csv`
  - `route_costs.csv`
  - `semaphore_penalty.csv`
  - `traffic_penalty.csv`
  - `summary.csv` (opcional)

## 🎨 Modos de Visualização

### Modo Avançado (com `rich`)
- Layout em painel dividido
- Tabelas coloridas e formatadas
- Atualização suave em ecrã completo
- Indicadores visuais (emojis, cores)

### Modo Básico (sem `rich`)
- Texto simples em terminal
- Limpa o ecrã a cada atualização
- Funciona em qualquer ambiente Python

## 🔧 Opções da Linha de Comandos

```
--refresh SECONDS    Intervalo de atualização em segundos (padrão: 2.0)
--metrics-dir DIR    Pasta com os ficheiros CSV (padrão: metrics)
```

## 💡 Exemplo de Uso Completo

Terminal 1 (simulação):
```zsh
source venv/bin/activate
python live_dynamic_spade.py
```

Terminal 2 (dashboard):
```zsh
source venv/bin/activate
python dashboard_metrics.py --refresh 1.5
```

## ⚠️ Notas

- O dashboard **não modifica** nenhum ficheiro da simulação
- É completamente independente e pode ser executado/encerrado a qualquer momento
- Se a pasta `metrics/` não existir, o dashboard aguarda até que seja criada
- Os dados são lidos diretamente dos CSV, sem interferir com a escrita
