#!/bin/bash

# Script para registrar TODOS os agentes SPADE no Prosody
# Formato: docker exec -it prosody prosodyctl register "username" localhost "password"
# Senha = Nome do agente

echo "🔧 Registrando TODOS os agentes SPADE no Prosody..."
echo "   Formato: username = password"
echo "=================================================="
echo ""

# 1. Coordinator
echo "📡 Registrando CoordinatorAgent..."
docker exec -it prosody prosodyctl register "coordinator" localhost "coordinator" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ coordinator@localhost (senha: coordinator)"
else
    echo "   ⚠️  coordinator@localhost já existe ou erro no registro"
fi
echo ""

# 2. Veículos (11 carros: vehicle_0 a vehicle_10)
echo "🚗 Registrando VehicleAgents (11 carros)..."
for i in {0..10}; do
    username="vehicle_${i}"
    password="${username}"  # Senha = nome do agente
    docker exec -it prosody prosodyctl register "${username}" localhost "${password}" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "   ✅ ${username}@localhost (senha: ${password})"
    else
        echo "   ⚠️  ${username}@localhost já existe ou erro no registro"
    fi
done
echo ""

# 3. Ambulâncias (4 AMB independentes: amb_0 a amb_3)
echo "🚑 Registrando AmbulanceAgents (4 AMB)..."
for i in {0..3}; do
    username="amb_${i}"
    password="${username}"  # Senha = nome do agente
    docker exec -it prosody prosodyctl register "${username}" localhost "${password}" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "   ✅ ${username}@localhost (senha: ${password})"
    else
        echo "   ⚠️  ${username}@localhost já existe ou erro no registro"
    fi
done
echo ""

# 4. Semáforos (20 agentes estratégicos - AUMENTADO!)
echo "🚦 Registrando TrafficLightAgents (20)..."
traffic_lights=("0_0" "0_5" "5_0" "5_5" "0_2" "0_3" "2_0" "3_0" "5_2" "5_3" "2_5" "3_5" "1_1" "1_3" "2_2" "2_3" "3_1" "3_3" "4_2" "4_4")

for tl in "${traffic_lights[@]}"; do
    username="tl_${tl}"
    password="${username}"  # Senha = nome do agente
    docker exec -it prosody prosodyctl register "${username}" localhost "${password}" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "   ✅ ${username}@localhost (senha: ${password})"
    else
        echo "   ⚠️  ${username}@localhost já existe ou erro no registro"
    fi
done

echo ""
echo "=================================================="
echo "✅ Registro completo!"
echo ""
echo "📊 Total de agentes registrados:"
echo "  - 1 CoordinatorAgent (coordinator)"
echo "  - 11 VehicleAgents (vehicle_0 a vehicle_10)"
echo "  - 4 AmbulanceAgents (amb_0 a amb_3)"
echo "  - 20 TrafficLightAgents (20 semáforos)"
echo "  = 36 agentes total"
echo ""
echo "🎯 Distribuição:"
echo "  - 1 Journey vehicle (v0: A->B)"
echo "  - 10 Carros normais (v1-v10)"
echo "  - 4 Ambulâncias AMB (AMB0-AMB3)"
echo "  - 20 Semáforos estratégicos"
echo ""
echo "🔑 Todas as senhas são iguais ao nome do agente"
echo "   Exemplo: vehicle_0 tem senha 'vehicle_0'"
echo ""
echo "▶️  Para executar a simulação:"
echo "   source venv/bin/activate"
echo "   python live_dynamic_spade.py"
echo ""
