#!/bin/bash
# Script para iniciar a aplicação web de visualização

echo "🚀 Iniciando Traffic Simulation Web Visualization"
echo "=================================================="
echo ""

# Verifica se venv está ativo
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment não ativo. Ativando..."
    source venv/bin/activate
fi

# Instala dependências se necessário
echo "📦 Verificando dependências..."
pip install -q flask flask-socketio python-socketio eventlet 2>/dev/null

echo ""
echo "✅ Dependências instaladas"
echo ""
echo "📡 Servidor Flask inicializando..."
echo "   URL: http://localhost:5000"
echo ""
echo "⚠️  ATENÇÃO: Certifique-se de que o SUMO está rodando!"
echo "   Execute em outro terminal:"
echo "   ./scripts/run_sumo_docker.sh"
echo ""
echo "=================================================="
echo ""

# Inicia a aplicação
python app.py
