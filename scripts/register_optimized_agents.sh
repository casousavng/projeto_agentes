#!/bin/bash

# Script para registrar agentes otimizados (5 veículos + 12 semáforos)
# Uso: ./scripts/register_optimized_agents.sh

echo "🔧 Registrando agentes SPADE otimizados no Prosody..."
echo "=================================================="
echo ""

# 1. Coordinator
echo "📡 Registrando CoordinatorAgent..."
docker exec -it prosody prosodyctl register coordinator localhost coordinatorpass 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ coordinator@localhost"
else
    echo "   ⚠️  coordinator@localhost já existe"
fi
echo ""

# 2. Veículos (5 agentes: v0-v4)
echo "🚗 Registrando VehicleAgents (5)..."
for i in {0..4}; do
    docker exec -it prosody prosodyctl register vehicle_${i} localhost vehicle${i}pass 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "   ✅ vehicle_${i}@localhost"
    else
        echo "   ⚠️  vehicle_${i}@localhost já existe"
    fi
done
echo ""

# 3. Semáforos (12 agentes estratégicos)
echo "🚦 Registrando TrafficLightAgents (12)..."
traffic_lights=("0_0" "0_5" "5_0" "5_5" "1_1" "1_3" "2_2" "3_1" "3_3" "4_2" "4_4" "2_4")

for tl in "${traffic_lights[@]}"; do
    # Remover underscore para a senha
    tl_pass="tl${tl//_/}pass"
    docker exec -it prosody prosodyctl register tl_${tl} localhost ${tl_pass} 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "   ✅ tl_${tl}@localhost"
    else
        echo "   ⚠️  tl_${tl}@localhost já existe"
    fi
done

echo ""
echo "=================================================="
echo "✅ Registro completo!"
echo ""
echo "Total de agentes:"
echo "  - 1 CoordinatorAgent"
echo "  - 5 VehicleAgents (v0-v4)"
echo "  - 12 TrafficLightAgents (posições estratégicas)"
echo "  = 18 agentes total"
echo ""
echo "Para executar a simulação:"
echo "  source venv/bin/activate"
echo "  python live_dynamic_spade.py"
echo ""
