#!/bin/bash
# SUMO wrapper para ignorar problemas de biblioteca do Homebrew
# Usa TraCI para controle remoto, evitando execução direta do binário

export SUMO_HOME="/opt/homebrew/opt/sumo/share/sumo"
export DYLD_FALLBACK_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_FALLBACK_LIBRARY_PATH"

# Tentar usar TraCI diretamente do Python
echo "SUMO wrapper iniciado"
echo "SUMO_HOME: $SUMO_HOME"
echo "Python version: $(python3 --version)"
echo "TraCI disponível via Python - use main.py para executar simulação"
