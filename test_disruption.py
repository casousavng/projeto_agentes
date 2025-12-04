#!/usr/bin/env python3
"""Script de teste para verificar comunicação de bloqueios"""

import asyncio
from agents.spade_traffic_agents import DisruptorAgent

async def test():
    # Criar DisruptorAgent
    edges = {i: {} for i in range(120)}  # Mock de edges
    
    disruptor = DisruptorAgent(
        "disruptor@localhost",
        "disruptor",
        edges
    )
    disruptor.coordinator_jid = "coordinator@localhost"
    
    await disruptor.start(auto_register=False)
    print("DisruptorAgent iniciado")
    
    await asyncio.sleep(2)
    
    # Ativar disrupção
    print("\n=== TESTE 1: Ativar disrupção ===")
    disruptor.activate_disruption()
    
    await asyncio.sleep(2)
    
    # Desativar disrupção
    print("\n=== TESTE 2: Desativar disrupção ===")
    disruptor.deactivate_disruption()
    
    await asyncio.sleep(2)
    
    # Toggle
    print("\n=== TESTE 3: Toggle (ativar) ===")
    disruptor.toggle_disruption()
    
    await asyncio.sleep(2)
    
    print("\n=== TESTE 4: Toggle (desativar) ===")
    disruptor.toggle_disruption()
    
    await asyncio.sleep(2)
    
    await disruptor.stop()
    print("\nTeste completo!")

if __name__ == "__main__":
    asyncio.run(test())
