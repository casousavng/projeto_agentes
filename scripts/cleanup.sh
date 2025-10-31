#!/bin/bash
# Script para limpar recursos

echo "🧹 Limpando recursos da simulação..."

# Parar container Prosody
if docker ps -a | grep -q prosody; then
    echo "🛑 Parando Prosody..."
    docker stop prosody
    docker rm prosody
fi

# Limpar arquivos temporários do SUMO
echo "🗑️  Removendo arquivos temporários..."
find . -name "*.xml.gz" -delete
find . -name "tripinfo.xml" -delete
find . -name "summary.xml" -delete
find . -name "*.log" -delete

echo "✅ Limpeza concluída!"
