#!/bin/bash

# Script para registrar 20 semáforos (10 pares H+V) no Prosody XMPP
# 10 cruzamentos estratégicos × 2 direções (horizontal + vertical) = 20 agentes

echo "🚦 Registrando 20 TrafficLightAgents (10 pares H+V estratégicos)..."

# Lista de 10 cruzamentos estratégicos
NODES=(
    "1_1" "1_4" "4_1" "4_4"        # Cantos principais (4)
    "2_2" "2_3" "3_2" "3_3"        # Internos críticos (4)
    "1_3" "3_1"                     # Internos extras (2)
)

# Registrar pares de semáforos para cada nó
for NODE in "${NODES[@]}"; do
    # Semáforo Horizontal
    AGENT_H="tl_${NODE}_h"
    PASSWORD_H="${AGENT_H}"
    
    echo "Registrando ${AGENT_H}@localhost..."
    docker exec -it prosody prosodyctl register "${AGENT_H}" localhost "${PASSWORD_H}" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "  ✅ ${AGENT_H} registrado com sucesso (HORIZONTAL)"
    else
        echo "  ⚠️  ${AGENT_H} já existe ou erro no registro"
    fi
    
    # Semáforo Vertical
    AGENT_V="tl_${NODE}_v"
    PASSWORD_V="${AGENT_V}"
    
    echo "Registrando ${AGENT_V}@localhost..."
    docker exec -it prosody prosodyctl register "${AGENT_V}" localhost "${PASSWORD_V}" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "  ✅ ${AGENT_V} registrado com sucesso (VERTICAL)"
    else
        echo "  ⚠️  ${AGENT_V} já existe ou erro no registro"
    fi
done

echo ""
echo "✅ Registro concluído! 20 semáforos registrados (10 pares H+V)"
echo "   📍 Posições estratégicas:"
echo "      - Cantos principais: 1_1, 1_4, 4_1, 4_4"
echo "      - Internos críticos: 2_2, 2_3, 3_2, 3_3, 1_3, 3_1"
echo "   🎨 Visualização:"
echo "      - Horizontal (H): retângulo largo acima do nó"
echo "      - Vertical (V): retângulo alto à esquerda do nó"
echo "   ✅ Coordenação: nunca ambos verdes simultaneamente"
