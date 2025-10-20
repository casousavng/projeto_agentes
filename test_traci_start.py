#!/usr/bin/env python3
"""
Script simples de teste - Inicia SUMO via TraCI local
"""
import traci
import sumolib
import sys
import os

print("🔬 TESTE COM TRACI.START()")
print("=" * 60)

# Caminho para os arquivos
sumo_config = "scenarios/grid_8x8/simulation.sumocfg"

if not os.path.exists(sumo_config):
    print(f"❌ Arquivo não encontrado: {sumo_config}")
    sys.exit(1)

print(f"\n1️⃣ Iniciando SUMO com arquivo: {sumo_config}")

# Tenta encontrar o executável SUMO
sumo_binary = sumolib.checkBinary('sumo')
print(f"   Executável: {sumo_binary}")

try:
    traci.start([
        sumo_binary,
        "-c", sumo_config,
        "--step-length", "0.1",
        "--no-step-log"
    ])
    print("✅ SUMO iniciado via TraCI!")
except Exception as e:
    print(f"❌ Erro ao iniciar: {e}")
    sys.exit(1)

print("\n2️⃣ Obtendo topologia...")
try:
    junctions = traci.junction.getIDList()
    edges = [e for e in traci.edge.getIDList() if not e.startswith(':')]
    print(f"✅ {len(junctions)} cruzamentos, {len(edges)} edges")
except Exception as e:
    print(f"❌ Erro: {e}")
    traci.close()
    sys.exit(1)

print("\n3️⃣ Executando 20 steps...")
try:
    for i in range(20):
        traci.simulationStep()
        vehicles = traci.vehicle.getIDList()
        if i % 5 == 0:
            print(f"   Step {i}: {len(vehicles)} veículos")
    print("✅ Steps executados com sucesso!")
except Exception as e:
    print(f"❌ Erro: {e}")
    traci.close()
    sys.exit(1)

print("\n4️⃣ Fechando...")
traci.close()
print("✅ Tudo funcionou!")
print("=" * 60)
