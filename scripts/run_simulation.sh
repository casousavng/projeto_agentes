#!/bin/bash
# Script para executar a simulação

echo "🚦 Iniciando Simulação de Tráfego Multiagente..."

# Verificar ambiente virtual
if [ ! -d "venv" ]; then
    echo "❌ Ambiente virtual não encontrado. Execute primeiro: ./scripts/setup_venv.sh"
    exit 1
fi

# Ativar ambiente virtual
source venv/bin/activate

# Verificar se Prosody está rodando
if ! docker ps | grep -q prosody; then
    echo "❌ Prosody não está rodando. Execute primeiro: ./scripts/setup_prosody.sh"
    exit 1
fi

# Verificar se SUMO está instalado
if ! command -v sumo &> /dev/null && ! command -v sumo-gui &> /dev/null; then
    echo "⚠️  SUMO não encontrado no PATH."
    echo "   Por favor, adicione SUMO ao PATH ou instale via Homebrew:"
    echo "   brew install sumo"
    exit 1
fi

# Criar .env se não existir
if [ ! -f ".env" ]; then
    echo "📝 Criando arquivo .env..."
    cp .env.example .env
fi

# Executar simulação
echo "▶️  Executando simulação..."
python main.py

echo ""
echo "✅ Simulação finalizada!"
