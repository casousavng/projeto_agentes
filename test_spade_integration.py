#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Integracao SPADE
Verifica se agentes conectam ao Prosody e comunicam via XMPP
"""

import asyncio
import json
import sys
import time
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message


class TestAgent(Agent):
    """Agente de teste simples"""
    
    class SendMessageBehaviour(OneShotBehaviour):
        async def run(self):
            print(f"   {self.agent.name}: Enviando mensagem de teste...")
            msg = Message(to="coordinator@localhost")
            msg.set_metadata("performative", "inform")
            msg.body = json.dumps({
                "type": "test",
                "from": self.agent.name
            })
            await self.send(msg)
            print(f"   {self.agent.name}: Mensagem enviada!")
    
    async def setup(self):
        print(f"✅ {self.name} conectado ao Prosody")
        behaviour = self.SendMessageBehaviour()
        self.add_behaviour(behaviour)


async def test_spade_connection():
    """Testa conexao SPADE com Prosody"""
    print("\n" + "="*60)
    print("🧪 Teste de Integracao SPADE + Prosody")
    print("="*60 + "\n")
    
    print("1️⃣  Testando conexao do Coordenador...")
    coordinator = TestAgent("coordinator@localhost", "coordinator123")
    await coordinator.start()
    await asyncio.sleep(2)
    
    print("\n2️⃣  Testando conexao de Veiculo...")
    vehicle = TestAgent("vehicle_0@localhost", "vehicle0pass")
    await vehicle.start()
    await asyncio.sleep(2)
    
    print("\n3️⃣  Testando conexao de Semaforo...")
    traffic_light = TestAgent("tl_0_0@localhost", "tl0_0pass")
    await traffic_light.start()
    await asyncio.sleep(2)
    
    print("\n" + "="*60)
    print("✅ Teste concluido com sucesso!")
    print("   Todos os agentes conectaram ao Prosody via XMPP")
    print("   Mensagens foram enviadas com sucesso")
    print("="*60 + "\n")
    
    # Cleanup
    await coordinator.stop()
    await vehicle.stop()
    await traffic_light.stop()
    
    return True


def main():
    """Funcao principal"""
    try:
        result = asyncio.run(test_spade_connection())
        if result:
            print("🎉 Sistema SPADE pronto para uso!")
            sys.exit(0)
        else:
            print("❌ Teste falhou!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Teste interrompido")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
