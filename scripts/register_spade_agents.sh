#!/bin/bash
# Script para registrar agentes SPADE no Prosody
# Para live_dynamic_traffic.py com SPADE

set -e

echo "🚀 Registrando agentes SPADE no Prosody..."
echo ""

# Verificar se Prosody está rodando
if ! docker ps | grep -q prosody; then
    echo "❌ Erro: Prosody não está rodando!"
    echo "Execute: docker run -d --name prosody -p 5222:5222 -p 5280:5280 prosody/prosody"
    exit 1
fi

# Função para registrar agente
register_agent() {
    local agent=$1
    local password=$2
    echo "Registrando: $agent@localhost"
    docker exec -it prosody prosodyctl register "$agent" localhost "$password" 2>/dev/null || echo "  (agente já existe)"
}

# 1. Registrar Coordenador
echo "📡 1. Coordenador"
register_agent "coordinator" "coordinator123"
echo ""

# 2. Registrar Veículos (10 veículos)
echo "🚗 2. Veículos (10 agentes)"
for i in {0..9}; do
    register_agent "vehicle_$i" "vehicle${i}pass"
done
echo ""

# 3. Registrar Semáforos (46 semáforos)
echo "🚦 3. Semáforos (46 agentes)"
echo "   Registrando semáforos..."

# Lista dos 46 semáforos do live_dynamic_traffic.py
# Cantos
traffic_lights=(
    # Cantos
    "0_0" "0_7" "7_0" "7_7"
    # Bordas
    "0_2" "0_4" "0_6"
    "7_1" "7_3" "7_5"
    "2_0" "4_0" "6_0"
    "1_7" "3_7" "5_7"
    # Internos
    "1_1" "1_2" "1_3" "1_4" "1_5" "1_6"
    "2_1" "2_2" "2_3" "2_4" "2_5" "2_6"
    "3_1" "3_2" "3_3" "3_4" "3_5" "3_6"
    "4_1" "4_2" "4_3" "4_4" "4_5" "4_6"
    "5_1" "5_2" "5_3" "5_4" "5_5" "5_6"
    "6_1" "6_2" "6_3" "6_4" "6_5" "6_6"
)

for tl in "${traffic_lights[@]}"; do
    register_agent "tl_$tl" "tl${tl}pass"
done
echo ""

# Resumo
echo "✅ Registro completo!"
echo ""
echo "📊 Total de agentes registrados:"
echo "   • 1 Coordenador (coordinator@localhost)"
echo "   • 10 Veículos (vehicle_0 a vehicle_9@localhost)"
echo "   • 46 Semáforos (tl_*@localhost)"
echo "   • TOTAL: 57 agentes SPADE"
echo ""
echo "🔍 Para verificar os agentes:"
echo "   docker exec -it prosody ls /var/lib/prosody/localhost/accounts/"
echo ""
echo "🚀 Agora você pode executar: python live_dynamic_traffic.py"
