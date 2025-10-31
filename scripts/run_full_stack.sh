#!/bin/bash
# Script para coletar dados da simulação e iniciar visualização web

echo "========================================================================"
echo "🎬 COLETA DE DADOS + VISUALIZAÇÃO WEB"
echo "========================================================================"
echo ""
echo "Este script irá:"
echo "  1. Verificar se SUMO está rodando"
echo "  2. Coletar dados dos agentes SPADE via TraCI"
echo "  3. Armazenar em SQLite (simulation_data.db)"
echo "  4. Iniciar servidor web para visualização"
echo ""

# Ativar ambiente virtual
if [ -d "venv" ]; then
    echo "🐍 Ativando ambiente virtual..."
    source venv/bin/activate
else
    echo "❌ Ambiente virtual não encontrado!"
    echo "   Execute: ./scripts/setup_venv.sh"
    exit 1
fi

# Verificar se SUMO está rodando
echo ""
echo "🔍 Verificando se SUMO está rodando..."
if ! docker ps | grep -q sumo-sim; then
    echo "⚠️  SUMO não está rodando!"
    echo ""
    echo "Iniciando SUMO Docker..."
    ./scripts/run_sumo_docker.sh
    
    echo "⏳ Aguardando SUMO inicializar (5 segundos)..."
    sleep 5
fi

# Verificar se porta TraCI está acessível
if nc -z localhost 8813 2>/dev/null; then
    echo "✅ SUMO está rodando na porta 8813"
else
    echo "❌ Porta TraCI 8813 não está acessível!"
    echo "   Verifique se o SUMO iniciou corretamente:"
    echo "   docker logs sumo-sim"
    exit 1
fi

# Coletar dados
echo ""
echo "========================================================================"
echo "📊 FASE 1: COLETA DE DADOS DOS AGENTES SPADE"
echo "========================================================================"
echo ""
echo "A simulação irá rodar e coletar dados em tempo real..."
echo "Pressione Ctrl+C quando desejar parar a coleta"
echo ""

python collect_simulation_data.py

# Verificar se a coleta foi bem-sucedida
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Erro na coleta de dados!"
    echo "   Verifique os logs acima"
    exit 1
fi

# Verificar se o banco foi criado
if [ ! -f "simulation_data.db" ]; then
    echo ""
    echo "❌ Banco de dados não foi criado!"
    exit 1
fi

echo ""
echo "========================================================================"
echo "🌐 FASE 2: INICIANDO SERVIDOR WEB"
echo "========================================================================"
echo ""
echo "O servidor web irá reproduzir os dados coletados..."
echo "Abra seu navegador em: http://localhost:5001"
echo ""
echo "Pressione Ctrl+C para parar o servidor"
echo ""

python app.py
