"""
Script de teste simplificado - apenas SPADE sem SUMO
Testa comunicação entre agentes via XMPP
"""
import asyncio
import logging
from agents import TrafficLightAgent, CarAgent
from config import simulation_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_agents_communication():
    """Testa comunicação básica entre agentes"""
    logger.info("=== TESTE: Comunicação entre agentes SPADE ===")
    
    # Criar um semáforo
    tl_jid = f"traffic_light_0@{simulation_config.XMPP_SERVER}"
    tl_agent = TrafficLightAgent(
        tl_jid,
        "traffic_light_0",  # Senha = nome do agente
        "test_tl_0",
        None  # Sem TraCI
    )
    tl_agent.verify_security = False
    
    # Criar um carro
    car_jid = f"car_0@{simulation_config.XMPP_SERVER}"
    car_agent = CarAgent(
        car_jid,
        "car_0",  # Senha = nome do agente
        "test_car_0",
        "edge_start",
        "edge_end",
        None  # Sem TraCI
    )
    car_agent.verify_security = False
    
    try:
        # Iniciar agentes
        logger.info("Iniciando agentes...")
        await tl_agent.start(auto_register=False)  # Já registrados
        await car_agent.start(auto_register=False)
        
        # Aguardar um momento para estabelecer conexões
        await asyncio.sleep(3)
        
        logger.info("✅ Agentes iniciados com sucesso!")
        logger.info(f"  - Semáforo: {tl_jid}")
        logger.info(f"  - Carro: {car_jid}")
        
        # Manter rodando por 10 segundos
        logger.info("Monitorando por 10 segundos...")
        await asyncio.sleep(10)
        
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Parar agentes
        logger.info("Encerrando agentes...")
        await tl_agent.stop()
        await car_agent.stop()
        logger.info("Teste concluído!")


async def test_xmpp_connection():
    """Testa apenas conexão XMPP"""
    logger.info("=== TESTE: Conexão XMPP ===")
    
    from spade.agent import Agent
    
    class TestAgent(Agent):
        async def setup(self):
            logger.info(f"Agente {self.jid} conectado!")
    
    test_jid = f"traffic_light_0@{simulation_config.XMPP_SERVER}"
    agent = TestAgent(test_jid, "traffic_light_0")  # Senha = nome do agente
    
    # Desabilitar verificação SSL (apenas para desenvolvimento)
    agent.verify_security = False
    
    try:
        await agent.start(auto_register=False)  # Agente já registrado manualmente
        logger.info(f"✅ Conexão XMPP OK para {test_jid}")
        await asyncio.sleep(3)
    except Exception as e:
        logger.error(f"❌ Erro de conexão: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await agent.stop()


async def main():
    """Executar testes"""
    logger.info("\n" + "="*60)
    logger.info("  TESTES DE COMUNICAÇÃO MULTIAGENTE")
    logger.info("="*60 + "\n")
    
    # Teste 1: Conexão XMPP básica
    await test_xmpp_connection()
    
    await asyncio.sleep(2)
    
    # Teste 2: Comunicação entre agentes
    await test_agents_communication()
    
    logger.info("\n" + "="*60)
    logger.info("  TODOS OS TESTES CONCLUÍDOS")
    logger.info("="*60)


if __name__ == "__main__":
    asyncio.run(main())
