#!/bin/bash

# Script para registrar TODOS os agentes no Prosody XMPP
# - 1 Coordenador
# - 1 Disruptor
# - 15 Veículos
# - 20 Semáforos (10 pares H+V)

echo "🚀 Registrando TODOS os agentes no Prosody..."
echo ""

# 1. Coordenador
echo "📡 Registrando CoordinatorAgent..."
docker exec -it prosody prosodyctl register "coordinator" localhost "coordinator" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  ✅ coordinator@localhost registrado"
else
    echo "  ⚠️  coordinator@localhost já existe"
fi

# 2. Disruptor
echo "🚧 Registrando DisruptorAgent..."
docker exec -it prosody prosodyctl register "disruptor" localhost "disruptor" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  ✅ disruptor@localhost registrado"
else
    echo "  ⚠️  disruptor@localhost já existe"
fi

echo ""

# 3. Veículos (15 agentes: v0 a v14)
echo "🚗 Registrando 15 VehicleAgents..."
for i in {0..14}; do
    AGENT="vehicle_${i}"
    docker exec -it prosody prosodyctl register "${AGENT}" localhost "${AGENT}" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "  ✅ ${AGENT}@localhost registrado"
    else
        echo "  ⚠️  ${AGENT}@localhost já existe"
    fi
done

echo ""

# 4. Semáforos (20 agentes: 10 pares H+V)
echo "🚦 Registrando 20 TrafficLightAgents (10 pares H+V)..."

NODES=(
    "1_1" "1_4" "4_1" "4_4"        # Cantos principais (4)
    "2_2" "2_3" "3_2" "3_3"        # Internos críticos (4)
    "1_3" "3_1"                     # Internos extras (2)
)

for NODE in "${NODES[@]}"; do
    # Horizontal
    AGENT_H="tl_${NODE}_h"
    docker exec -it prosody prosodyctl register "${AGENT_H}" localhost "${AGENT_H}" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "  ✅ ${AGENT_H}@localhost registrado"
    else
        echo "  ⚠️  ${AGENT_H}@localhost já existe"
    fi
    
    # Vertical
    AGENT_V="tl_${NODE}_v"
    docker exec -it prosody prosodyctl register "${AGENT_V}" localhost "${AGENT_V}" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "  ✅ ${AGENT_V}@localhost registrado"
    else
        echo "  ⚠️  ${AGENT_V}@localhost já existe"
    fi
done

echo ""
echo "✅ Registro concluído!"
echo "   📊 Total de agentes:"
echo "      - 1 Coordenador"
echo "      - 1 Disruptor"
echo "      - 15 Veículos"
echo "      - 20 Semáforos"
echo "      ━━━━━━━━━━━━━━━"
echo "      = 37 agentes SPADE"
