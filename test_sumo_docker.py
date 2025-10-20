"""
Teste simples de conexão TraCI com SUMO Docker
"""
import traci
import time

print("🔌 Testando conexão TraCI com SUMO Docker...")

try:
    # Conectar ao SUMO rodando no Docker
    traci.init(port=8813)
    print("✅ Conectado ao SUMO com sucesso!")
    
    # Obter informações da simulação
    print(f"📊 Versão SUMO: {traci.getVersion()}")
    print(f"⏱️  Tempo inicial: {traci.simulation.getTime()}")
    
    # Obter lista de edges
    edges = traci.edge.getIDList()
    print(f"🛣️  Número de edges: {len(edges)}")
    print(f"📍 Edges: {edges[:5]}...")  # Primeiros 5
    
    # Dar alguns steps
    print("\n🚦 Executando 10 steps...")
    for i in range(10):
        traci.simulationStep()
        if i % 5 == 0:
            print(f"  Step {i}: tempo={traci.simulation.getTime()}")
    
    print("\n✅ Teste bem-sucedido!")
    
    traci.close()
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
