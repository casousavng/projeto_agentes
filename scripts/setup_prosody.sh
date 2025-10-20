#!/bin/bash
# Script para configurar o ambiente Prosody

echo "🚀 Configurando Prosody XMPP Server..."

# Verificar se Docker está rodando
if ! docker ps &> /dev/null; then
    echo "❌ Docker não está rodando. Por favor, inicie o Docker Desktop."
    exit 1
fi

# Parar e remover container existente (se houver)
echo "🔍 Verificando containers existentes..."
if docker ps -a | grep -q prosody; then
    echo "🗑️  Removendo container Prosody existente..."
    docker stop prosody 2>/dev/null
    docker rm prosody 2>/dev/null
fi

# Iniciar novo container Prosody
echo "📦 Iniciando container Prosody..."
docker run -d \
    --name prosody \
    -p 5222:5222 \
    -p 5269:5269 \
    -p 5280:5280 \
    prosody/prosody

# Aguardar Prosody inicializar
echo "⏳ Aguardando Prosody inicializar..."
sleep 5

# Verificar se container está rodando
if docker ps | grep -q prosody; then
    echo "✅ Prosody iniciado com sucesso!"
    echo ""
    echo "ℹ️  Informações do servidor:"
    echo "   - Host: localhost"
    echo "   - Porta: 5222"
    echo "   - Admin: http://localhost:5280/admin"
    echo ""
    echo "📝 Para registrar agentes manualmente:"
    echo "   docker exec -it prosody prosodyctl register <nome> localhost <senha>"
else
    echo "❌ Erro ao iniciar Prosody"
    exit 1
fi
