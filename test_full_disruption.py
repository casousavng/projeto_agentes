#!/usr/bin/env python3
"""
Teste completo do sistema de disrupção
"""
import asyncio
import time
import sys
sys.path.insert(0, '.')

from agents.spade_traffic_agents import DisruptorAgent, CoordinatorAgent, VehicleAgent

async def main():
    # Dados de teste
    nodes = {
        "0_0": (50, 50),
        "0_1": (250, 50),
        "1_0": (50, 250),
        "1_1": (250, 250)
    }
    
    edges = {
        0: {"id": 0, "from": "0_0", "to": "0_1", "weight": 100},
        1: {"id": 1, "from": "0_1", "to": "0_0", "weight": 100},
        2: {"id": 2, "from": "0_0", "to": "1_0", "weight": 100},
        3: {"id": 3, "from": "1_0", "to": "0_0", "weight": 100},
        4: {"id": 4, "from": "0_1", "to": "1_1", "weight": 100},
        5: {"id": 5, "from": "1_1", "to": "0_1", "weight": 100},
        6: {"id": 6, "from": "1_0", "to": "1_1", "weight": 100},
        7: {"id": 7, "from": "1_1", "to": "1_0", "weight": 100},
    }
    
    graph = {
        "0_0": [("0_1", 0), ("1_0", 2)],
        "0_1": [("0_0", 1), ("1_1", 4)],
        "1_0": [("0_0", 3), ("1_1", 6)],
        "1_1": [("0_1", 5), ("1_0", 7)]
    }
    
    print("="*60)
    print("TESTE COMPLETO DO SISTEMA DE DISRUPÇÃO")
    print("="*60)
    
    # 1. Iniciar Coordenador
    print("\n1. Iniciando CoordinatorAgent...")
    coordinator = CoordinatorAgent(
        "coordinator@localhost",
        "coordinator",
        nodes, edges, graph
    )
    await coordinator.start(auto_register=False)
    await asyncio.sleep(1)
    print(f"   Coordenador conectado: {coordinator.is_alive()}")
    
    # 2. Iniciar Veículo
    print("\n2. Iniciando VehicleAgent v0...")
    vehicle = VehicleAgent(
        "vehicle_0@localhost",
        "vehicle_0",
        "v0",
        "0_0",
        "1_1",
        "car"
    )
    await vehicle.start(auto_register=False)
    await asyncio.sleep(2)  # Tempo para receber dados da rede
    print(f"   Veículo conectado: {vehicle.is_alive()}")
    print(f"   Veículo blocked_edges: {vehicle.blocked_edges}")
    
    # 3. Iniciar Disruptor
    print("\n3. Iniciando DisruptorAgent...")
    disruptor = DisruptorAgent(
        "disruptor@localhost",
        "disruptor",
        edges
    )
    disruptor.coordinator_jid = "coordinator@localhost"
    await disruptor.start(auto_register=False)
    await asyncio.sleep(1)
    print(f"   Disruptor conectado: {disruptor.is_alive()}")
    
    # 4. Verificar veículos registrados
    print("\n4. Veículos registrados no coordenador:")
    print(f"   {coordinator.vehicles}")
    
    # 5. Ativar disrupção
    print("\n5. ATIVANDO DISRUPÇÃO...")
    disruptor.toggle_disruption()
    
    # Aguardar a mensagem ser processada
    await asyncio.sleep(3)
    
    # 6. Verificar se o veículo recebeu
    print("\n6. VERIFICANDO RECEPÇÃO:")
    print(f"   Coordenador blocked_edges: {coordinator.blocked_edges}")
    print(f"   Veículo blocked_edges: {vehicle.blocked_edges}")
    
    # 7. Testar A* com bloqueio
    print("\n7. TESTANDO A* COM BLOQUEIO:")
    route_before = vehicle.calculate_route_astar("0_0", "1_1")
    print(f"   Rota calculada: {route_before}")
    
    # 8. Parar agentes
    print("\n8. Parando agentes...")
    await disruptor.stop()
    await vehicle.stop()
    await coordinator.stop()
    
    print("\n" + "="*60)
    print("TESTE COMPLETO!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
