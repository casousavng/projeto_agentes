import asyncio
from spade.agent import Agent

class DummyAgent(Agent):
    async def setup(self):
        print(f"Agente {self.jid} iniciado!")

async def main():
    # JID e senha do usuário criado no Prosody
    dummy = DummyAgent("car_0@localhost", "car_0")
    print("Conectando o agente...")

    await dummy.start()  # Não use auto_register nem use_tls
    print("Agente conectado!")

    # Mantém o agente ativo por 10 segundos
    await asyncio.sleep(10)

    await dummy.stop()
    print("Agente parado.")

if __name__ == "__main__":
    asyncio.run(main())
