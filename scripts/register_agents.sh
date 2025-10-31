#!/bin/bash
# Script para registrar todos os agentes no Prosody
# Uso: ./scripts/register_agents.sh

echo "🔧 Registrando agentes no Prosody..."

# Verificar se Prosody está rodando
if ! docker ps | grep -q prosody; then
    echo "❌ Container Prosody não está rodando!"
    echo "Execute: docker start prosody"
    exit 1
fi

# Registrar semáforos
for i in {0..3}; do
    echo "Registrando traffic_light_$i..."
    docker exec prosody prosodyctl register "traffic_light_$i" localhost "traffic_light_$i" 2>&1 | grep -v "already registered" || true
done

# Registrar carros
for i in {0..9}; do
    echo "Registrando car_$i..."
    docker exec prosody prosodyctl register "car_$i" localhost "car_$i" 2>&1 | grep -v "already registered" || true
done

# Registrar ambulâncias
for i in {0..1}; do
    echo "Registrando ambulance_$i..."
    docker exec prosody prosodyctl register "ambulance_$i" localhost "ambulance_$i" 2>&1 | grep -v "already registered" || true
done

# Registrar pedestres
for i in {0..4}; do
    echo "Registrando pedestrian_$i..."
    docker exec prosody prosodyctl register "pedestrian_$i" localhost "pedestrian_$i" 2>&1 | grep -v "already registered" || true
done

echo "✅ Todos os agentes registrados!"
echo ""
echo "Convenção de senha: senha = nome do agente"
echo "Exemplo: car_0 -> JID: car_0@localhost, Senha: car_0"
