#!/bin/bash
# Script para rodar SUMO GUI localmente (se disponível) ou sem GUI

echo "🚗 Testando SUMO local..."

# Verificar se sumo-gui está disponível
if command -v sumo-gui &> /dev/null; then
    echo "✅ sumo-gui encontrado!"
    echo "🖼️  Iniciando SUMO GUI localmente..."
    
    cd scenarios/grid_8x8
    sumo-gui -c simulation.sumocfg --start --quit-on-end false &
    SUMO_PID=$!
    
    echo ""
    echo "✅ SUMO GUI rodando (PID: $SUMO_PID)"
    echo "🔍 Veículo principal: car_journey (amarelo)"
    echo "   Origem: n0_0 (canto inferior esquerdo)"
    echo "   Destino: n7_7 (canto superior direito)"
    echo ""
    echo "Para parar: kill $SUMO_PID"
    
elif command -v sumo &> /dev/null; then
    echo "⚠️  sumo-gui não encontrado, usando sumo sem GUI..."
    echo "🚀 Iniciando simulação..."
    
    cd scenarios/grid_8x8
    sumo -c simulation.sumocfg --remote-port 8813 --step-length 0.1 --no-step-log &
    SUMO_PID=$!
    
    echo ""
    echo "✅ SUMO rodando sem GUI (PID: $SUMO_PID)"
    echo "🔌 TraCI disponível na porta 8813"
    echo ""
    echo "Para visualizar, use:"
    echo "  python -c 'import traci; traci.init(8813); ...''"
    echo ""
    echo "Para parar: kill $SUMO_PID"
    
else
    echo "❌ SUMO não encontrado localmente!"
    echo ""
    echo "📦 Opções de instalação:"
    echo "   1. Homebrew: brew install sumo"
    echo "   2. Conda: conda install -c conda-forge sumo"
    echo "   3. Pip: pip install eclipse-sumo"
    echo ""
    echo "💡 Alternativa: Rodar sem GUI usando Docker"
    echo "   ./scripts/run_sumo_docker.sh (já configurado para grid_8x8)"
    exit 1
fi
