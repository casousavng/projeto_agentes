#!/usr/bin/env python3
"""
Script de teste para diagnóstico da conexão SUMO + TraCI
"""
import traci
import time
import sys

print("🔬 TESTE DE DIAGNÓSTICO - SUMO + TraCI")
print("=" * 60)

# Pula o reinício - assume que SUMO já está rodando
print("\n1️⃣ Assumindo que SUMO já está rodando...")
print("   (Execute: ./scripts/run_sumo_docker.sh se necessário)")

print("\n2️⃣ Aguardando 2 segundos...")
time.sleep(2)

print("\n3️⃣ Tentando conectar ao TraCI...")
try:
    traci.connect(8813)
    print("✅ Conectado!")
except Exception as e:
    print(f"❌ Falha ao conectar: {e}")
    sys.exit(1)

print("\n4️⃣ Fazendo primeiro step...")
try:
    traci.simulationStep()
    print("✅ Step executado!")
except Exception as e:
    print(f"❌ Erro no step: {e}")
    traci.close()
    sys.exit(1)

print("\n5️⃣ Obtendo lista de cruzamentos...")
try:
    junctions = traci.junction.getIDList()
    print(f"✅ Encontrados {len(junctions)} cruzamentos")
    print(f"   Exemplos: {junctions[:5]}")
except Exception as e:
    print(f"❌ Erro: {e}")
    traci.close()
    sys.exit(1)

print("\n6️⃣ Obtendo lista de edges...")
try:
    edges = traci.edge.getIDList()
    # Filtra edges internas
    real_edges = [e for e in edges if not e.startswith(':')]
    print(f"✅ Encontradas {len(real_edges)} edges")
    print(f"   Exemplos: {real_edges[:5]}")
except Exception as e:
    print(f"❌ Erro: {e}")
    traci.close()
    sys.exit(1)

print("\n7️⃣ Obtendo posição de um cruzamento...")
try:
    if len(junctions) > 0:
        pos = traci.junction.getPosition(junctions[0])
        print(f"✅ Posição de {junctions[0]}: x={pos[0]}, y={pos[1]}")
except Exception as e:
    print(f"❌ Erro: {e}")
    traci.close()
    sys.exit(1)

print("\n8️⃣ Executando 10 steps...")
try:
    for i in range(10):
        traci.simulationStep()
        vehicles = traci.vehicle.getIDList()
        print(f"   Step {i+1}: {len(vehicles)} veículos")
except Exception as e:
    print(f"❌ Erro: {e}")
    traci.close()
    sys.exit(1)

print("\n9️⃣ Fechando conexão...")
traci.close()
print("✅ Conexão fechada")

print("\n" + "=" * 60)
print("✅ TODOS OS TESTES PASSARAM!")
print("   A conexão TraCI está funcionando corretamente.")
print("=" * 60)
