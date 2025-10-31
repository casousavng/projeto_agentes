#!/bin/bash

# Script para registrar 40 semáforos (pares H+V) no Prosody XMPP
# 20 cruzamentos × 2 direções (horizontal + vertical) = 40 agentes

echo "🚦 Registrando 40 TrafficLightAgents (pares H+V)..."

# Lista de cruzamentos (20 nós estratégicos)
NODES=(
    "0_0" "0_5" "5_0" "5_5"        # Cantos (4)
    "0_2" "0_3" "2_0" "3_0"        # Bordas (4)
    "5_2" "5_3" "2_5" "3_5"        # Bordas (4)
    "1_1" "1_3" "2_2" "2_3"        # Internos (4)
    "3_1" "3_3" "4_2" "4_4"        # Internos (4)
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
echo "✅ Registro concluído! 40 semáforos registrados (20 pares H+V)"
echo "   - Cada cruzamento tem 2 semáforos coordenados"
echo "   - HORIZONTAL: controla tráfego leste-oeste"
echo "   - VERTICAL: controla tráfego norte-sul"
echo "   - Coordenação: nunca ambos verdes simultaneamente"
