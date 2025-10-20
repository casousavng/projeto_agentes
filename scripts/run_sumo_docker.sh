#!/bin/bash
# Script alternativo para SUMO via Docker

echo "🚦 Executando SUMO via Docker (solução alternativa xerces-c)"

# Verificar se Docker está rodando
if ! docker ps &> /dev/null; then
    echo "❌ Docker não está rodando. Por favor, inicie o Docker Desktop."
    exit 1
fi

# Criar rede SUMO via Docker se não existir
if ! docker network inspect sumo-network &> /dev/null; then
    echo "📡 Criando rede Docker para SUMO..."
    docker network create sumo-network
fi

# Parar container SUMO existente
if docker ps -a | grep -q sumo-sim; then
    echo "🛑 Parando container SUMO existente..."
    docker stop sumo-sim 2>/dev/null
    docker rm sumo-sim 2>/dev/null
fi

# Executar SUMO em container Docker
echo "🚀 Iniciando SUMO em Docker com rede 8x8..."
docker run -d \
    --name sumo-sim \
    --network host \
    -v "$(pwd)/scenarios:/scenarios" \
    ghcr.io/eclipse-sumo/sumo@sha256:1b200db7630e83d9e47994c72a650b97845651d3316b9ead6de2d6bc4cfd1be3 \
    sumo \
    --net-file /scenarios/grid_8x8/network.net.xml \
    --route-files /scenarios/grid_8x8/routes.rou.xml \
    --remote-port 8813 \
    --step-length 0.1 \
    --no-step-log

echo "✅ SUMO rodando em Docker na porta 8813"
echo "🗺️  Rede: grid_8x8 (64 nós)"
echo "🚗 Veículo: car_journey (n0_0 → n7_7)"
echo "Aguardando SUMO iniciar..."
sleep 3
echo ""
echo "Para ver logs:"
echo "  docker logs -f sumo-sim"
echo ""
echo "Para parar:"
echo "  docker stop sumo-sim"
