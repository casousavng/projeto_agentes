"""
Teste do main.py SEM SUMO - apenas comunicação de agentes
"""
import asyncio
import logging
from config import simulation_config
from agents import TrafficLightAgent, CarAgent, AmbulanceAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Testar criação de agentes sem SUMO"""
    logger.info("🚀 Teste de Simulação (SEM SUMO)")
    logger.info("="*60)
    
    agents = []
    
    try:
        # Criar 2 semáforos
        logger.info("Criando semáforos...")
        for i in range(2):
            agent_name = f"traffic_light_{i}"
            jid = f"{agent_name}@{simulation_config.XMPP_SERVER}"
            agent = TrafficLightAgent(jid, agent_name, f"tl_{i}", None)
            await agent.start()
            agents.append(agent)
            logger.info(f"  ✅ {agent_name} conectado")
        
        # Criar 3 carros
        logger.info("Criando carros...")
        for i in range(3):
            agent_name = f"car_{i}"
            jid = f"{agent_name}@{simulation_config.XMPP_SERVER}"
            agent = CarAgent(jid, agent_name, f"car_{i}", "A", "B", None)
            await agent.start()
            agents.append(agent)
            logger.info(f"  ✅ {agent_name} conectado")
        
        # Criar 1 ambulância
        logger.info("Criando ambulância...")
        agent_name = "ambulance_0"
        jid = f"{agent_name}@{simulation_config.XMPP_SERVER}"
        agent = AmbulanceAgent(jid, agent_name, "amb_0", "A", "B", True, None)
        await agent.start()
        agents.append(agent)
        logger.info(f"  ✅ {agent_name} conectado")
        
        logger.info("="*60)
        logger.info(f"✅ SUCESSO! {len(agents)} agentes conectados e rodando!")
        logger.info("Monitorando por 15 segundos...")
        logger.info("="*60)
        
        # Manter rodando
        await asyncio.sleep(15)
        
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Parar agentes
        logger.info("\nEncerrando agentes...")
        for agent in agents:
            try:
                await agent.stop()
            except:
                pass
        logger.info("✅ Teste concluído!")


if __name__ == "__main__":
    asyncio.run(main())
