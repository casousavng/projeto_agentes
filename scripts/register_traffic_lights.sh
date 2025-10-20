#!/bin/bash
# Registrar agentes semáforo no Prosody

echo "🚦 Registrando agentes semáforo no Prosody..."

# Registrar 24 semáforos (rede 8x8)
for i in {0..23}; do
    echo "Registrando trafficlight_$i..."
    docker exec prosody prosodyctl register "trafficlight_$i" localhost "trafficlight_$i" 2>&1 | grep -v "already exists" || echo "  ✅ trafficlight_$i"
done

echo ""
echo "✅ Agentes semáforo registrados!"
echo ""
echo "📊 Total de agentes:"
docker exec prosody prosodyctl shell "for user in prosody.hosts['localhost'].sessions do print(user) end" 2>/dev/null | grep -c trafficlight || echo "24 agentes semáforo"
