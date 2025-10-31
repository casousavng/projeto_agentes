#!/usr/bin/env python3
"""
Teste direto de conexão com Prosody
Baseado no exemplo que funciona
"""
import asyncio
from spade import agent
import spade

class TestAgent(agent.Agent):
    async def setup(self):
        print(f"✅ Agente {self.jid} conectado com sucesso!")

async def main():
    print("🧪 Testando conexão direta com Prosody...")
    print("=" * 60)
    
    # Teste 1: Coordinator (auto-registra se não existir)
    print("\n1️⃣  Testando coordinator@localhost...")
    try:
        coord = TestAgent("coordinator@localhost", "coordinatorpass")
        await coord.start(auto_register=True)  # Registra automaticamente se não existir
        print("   ✅ Coordinator conectou!")
        await asyncio.sleep(1)
        await coord.stop()
    except Exception as e:
        print(f"   ❌ Coordinator falhou: {e}")
    
    # Teste 2: Vehicle (auto-registra se não existir)
    print("\n2️⃣  Testando vehicle_0@localhost...")
    try:
        vehicle = TestAgent("vehicle_0@localhost", "vehicle0pass")
        await vehicle.start(auto_register=True)  # Registra automaticamente se não existir
        print("   ✅ Vehicle_0 conectou!")
        await asyncio.sleep(1)
        await vehicle.stop()
    except Exception as e:
        print(f"   ❌ Vehicle_0 falhou: {e}")
    
    # Teste 3: Traffic Light (auto-registra se não existir)
    print("\n3️⃣  Testando tl_0_0@localhost...")
    try:
        tl = TestAgent("tl_0_0@localhost", "tl00pass")
        await tl.start(auto_register=True)  # Registra automaticamente se não existir
        print("   ✅ TL_0_0 conectou!")
        await asyncio.sleep(1)
        await tl.stop()
    except Exception as e:
        print(f"   ❌ TL_0_0 falhou: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Teste concluído!")

if __name__ == "__main__":
    spade.run(main())
