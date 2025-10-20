"""
Teste MINIMALISTA - Conexão XMPP direta
"""
import asyncio
from spade.agent import Agent

async def test():
    class SimpleAgent(Agent):
        async def setup(self):
            print(f"✅ {self.jid} conectado!")
    
    agent = SimpleAgent("testagent@localhost", "pass123")
    agent.verify_security = False  # Desabilitar SSL
    agent.client.disable_mechanism('SCRAM-SHA-512')
    agent.client.disable_mechanism('SCRAM-SHA-256')
    agent.client.disable_mechanism('SCRAM-SHA-1')
    
    try:
        await agent.start(auto_register=False)  # Usar credenciais existentes
        print("Agente rodando...")
        await asyncio.sleep(5)
        await agent.stop()
        print("✅ Teste bem-sucedido!")
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
