#!/bin/bash
# Script para rodar SUMO GUI em Docker no macOS com X11

echo "🖥️  Configurando SUMO GUI com Docker + X11..."

# Verificar se XQuartz está instalado
if ! command -v xhost &> /dev/null; then
    echo "❌ XQuartz não encontrado!"
    echo "📦 Instale com: brew install --cask xquartz"
    echo "🔄 Depois faça logout/login ou reinicie o Mac"
    echo ""
    echo "⚙️  Configuração necessária do XQuartz:"
    echo "   1. Abra XQuartz → Preferences → Security"
    echo "   2. Marque 'Allow connections from network clients'"
    echo "   3. Reinicie o XQuartz"
    exit 1
fi

# Verificar se X11 está rodando
if ! pgrep -x "Xquartz" > /dev/null; then
    echo "🚀 Iniciando XQuartz..."
    open -a XQuartz
    echo "⏳ Aguardando XQuartz iniciar..."
    sleep 5
fi

# Permitir conexões locais
echo "🔓 Permitindo conexões X11..."
xhost + localhost
xhost + 127.0.0.1

# Remover container antigo se existir
docker rm -f sumo-gui 2>/dev/null || true

# Usar host.docker.internal no macOS
DISPLAY_HOST="host.docker.internal:0"

# Executar SUMO GUI no Docker
echo "🚗 Iniciando SUMO GUI..."
docker run -d \
    --name sumo-gui \
    --add-host=host.docker.internal:host-gateway \
    -e DISPLAY=${DISPLAY_HOST} \
    -v "$(pwd)/scenarios:/scenarios" \
    ghcr.io/eclipse-sumo/sumo@sha256:1b200db7630e83d9e47994c72a650b97845651d3316b9ead6de2d6bc4cfd1be3 \
    sumo-gui \
    -c /scenarios/grid_8x8/simulation.sumocfg \
    --start \
    --quit-on-end false

echo ""
echo "✅ SUMO GUI iniciado!"
echo "🖼️  A janela deve aparecer no XQuartz"
echo ""
echo "📊 Comandos úteis:"
echo "  - Ver logs:     docker logs -f sumo-gui"
echo "  - Parar:        docker stop sumo-gui"
echo "  - Remover:      docker rm -f sumo-gui"
echo ""
echo "🔍 Veículo principal: car_journey (amarelo)"
echo "   Origem: n0_0 (canto inferior esquerdo)"
echo "   Destino: n7_7 (canto superior direito)"
