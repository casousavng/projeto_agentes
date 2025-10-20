# -*- coding: utf-8 -*-
"""
Simulador principal - versão Docker SUMO
Conecta SPADE com SUMO rodando em Docker via TraCI
"""
import traci
import asyncio
import os
import sys
import logging
from config import simulation_config
from agents import TrafficLightAgent, CarAgent, AmbulanceAgent, PedestrianAgent
from utils import XMPPAgentManager, RouteOptimizer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TrafficSimulation:
    """Controlador principal da simulação"""
    
    def __init__(self, use_docker=False):
        self.traci_conn = None
        self.agents = []
        self.xmpp_manager = XMPPAgentManager()
        self.route_optimizer = None
        self.use_docker = use_docker
        
    def connect_to_sumo(self, host="localhost", port=8813, retries=10):
        """Conectar a um SUMO já rodando (Docker ou local)"""
        logger.info(f"Conectando ao SUMO em {host}:{port}...")
        
        for attempt in range(retries):
            try:
                traci.init(port)
                self.traci_conn = traci
                self.route_optimizer = RouteOptimizer(self.traci_conn)
                logger.info("✅ Conectado ao SUMO com sucesso")
                return True
            except Exception as e:
                if attempt < retries - 1:
                    logger.warning(f"Tentativa {attempt + 1}/{retries} falhou: {e}")
                    import time
                    time.sleep(2)
                else:
                    logger.error(f"❌ Não foi possível conectar ao SUMO: {e}")
                    return False
        return False
        
    def start_sumo(self):
        """Iniciar SUMO localmente (apenas se não usar Docker)"""
        if self.use_docker:
            logger.info("Modo Docker: assumindo que SUMO já está rodando")
            return self.connect_to_sumo()
            
        logger.info("Iniciando SUMO localmente...")
        
        # Verificar se arquivo de configuração existe
        if not os.path.exists(simulation_config.SUMO_CONFIG):
            logger.error(f"Arquivo de configuração não encontrado: {simulation_config.SUMO_CONFIG}")
            return False
            
        # Configurar comando SUMO
        if simulation_config.SUMO_GUI:
            sumo_binary = "sumo-gui"
        else:
            sumo_binary = "sumo"
            
        sumo_cmd = [
            sumo_binary,
            "-c", simulation_config.SUMO_CONFIG,
            "--step-length", str(simulation_config.SUMO_STEP_LENGTH),
            "--remote-port", str(simulation_config.SUMO_PORT)
        ]
        
        try:
            # Iniciar SUMO via TraCI
            traci.start(sumo_cmd)
            self.traci_conn = traci
            self.route_optimizer = RouteOptimizer(self.traci_conn)
            logger.info("SUMO iniciado com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao iniciar SUMO: {e}")
            logger.info("💡 Dica: Tente usar o modo Docker com --docker")
            return False
            
    def register_xmpp_agents(self):
        """Registrar agentes no Prosody"""
        logger.info("Registrando agentes no Prosody...")
        
        agent_configs = []
        
        # Semáforos
        for i in range(simulation_config.NUM_TRAFFIC_LIGHTS):
            agent_configs.append({
                'username': f'trafficlight_{i}',
                'password': simulation_config.DEFAULT_PASSWORD
            })
            
        # Carros
        for i in range(simulation_config.NUM_CARS):
            agent_configs.append({
                'username': f'car_{i}',
                'password': simulation_config.DEFAULT_PASSWORD
            })
            
        # Ambulâncias
        for i in range(simulation_config.NUM_AMBULANCES):
            agent_configs.append({
                'username': f'ambulance_{i}',
                'password': simulation_config.DEFAULT_PASSWORD
            })
            
        # Pedestres
        for i in range(simulation_config.NUM_PEDESTRIANS):
            agent_configs.append({
                'username': f'pedestrian_{i}',
                'password': simulation_config.DEFAULT_PASSWORD
            })
            
        # Registrar todos
        results = self.xmpp_manager.register_multiple_agents(agent_configs)
        
        success_count = sum(1 for r in results if r['success'])
        logger.info(f"{success_count}/{len(results)} agentes registrados")
        
    async def create_agents(self):
        """Criar instâncias dos agentes SPADE"""
        logger.info("Criando agentes SPADE...")
        
        # Obter lista de semáforos do SUMO
        tl_ids = self.traci_conn.trafficlight.getIDList() if self.traci_conn else []
        
        # Criar semáforos
        for i, tl_id in enumerate(tl_ids[:simulation_config.NUM_TRAFFIC_LIGHTS]):
            jid = f"trafficlight_{i}@{simulation_config.XMPP_SERVER}"
            agent = TrafficLightAgent(
                jid,
                simulation_config.DEFAULT_PASSWORD,
                tl_id,
                self.traci_conn
            )
            self.agents.append(agent)
            await agent.start()
            logger.info(f"Semáforo {tl_id} criado")
            
        # Criar carros
        edges = self.traci_conn.edge.getIDList() if self.traci_conn else []
        for i in range(simulation_config.NUM_CARS):
            jid = f"car_{i}@{simulation_config.XMPP_SERVER}"
            vehicle_id = f"car_{i}"
            
            # Selecionar origem e destino aleatórios
            if len(edges) >= 2:
                origin = edges[i % len(edges)]
                destination = edges[(i + len(edges)//2) % len(edges)]
            else:
                origin = destination = edges[0] if edges else "edge0"
                
            agent = CarAgent(
                jid,
                simulation_config.DEFAULT_PASSWORD,
                vehicle_id,
                origin,
                destination,
                self.traci_conn
            )
            self.agents.append(agent)
            await agent.start()
            
            # Adicionar veículo ao SUMO
            if self.traci_conn:
                try:
                    route_id = f"route_{i}"
                    self.traci_conn.route.add(route_id, [origin, destination])
                    self.traci_conn.vehicle.add(vehicle_id, route_id)
                    logger.info(f"Carro {vehicle_id} criado: {origin} -> {destination}")
                except Exception as e:
                    logger.error(f"Erro ao adicionar veículo {vehicle_id}: {e}")
                    
        # Criar ambulâncias
        for i in range(simulation_config.NUM_AMBULANCES):
            jid = f"ambulance_{i}@{simulation_config.XMPP_SERVER}"
            vehicle_id = f"ambulance_{i}"
            
            if len(edges) >= 2:
                origin = edges[(i + 1) % len(edges)]
                destination = edges[(i + len(edges)//3) % len(edges)]
            else:
                origin = destination = edges[0] if edges else "edge0"
                
            # Metade das ambulâncias em modo urgência
            urgent_mode = (i % 2 == 0)
                
            agent = AmbulanceAgent(
                jid,
                simulation_config.DEFAULT_PASSWORD,
                vehicle_id,
                origin,
                destination,
                urgent_mode,
                self.traci_conn
            )
            self.agents.append(agent)
            await agent.start()
            
            # Adicionar ao SUMO
            if self.traci_conn:
                try:
                    route_id = f"route_amb_{i}"
                    self.traci_conn.route.add(route_id, [origin, destination])
                    self.traci_conn.vehicle.add(vehicle_id, route_id, typeID="emergency")
                    logger.info(f"Ambulância {vehicle_id} criada (urgência: {urgent_mode})")
                except Exception as e:
                    logger.error(f"Erro ao adicionar ambulância {vehicle_id}: {e}")
                    
        logger.info(f"Total de {len(self.agents)} agentes criados")
        
    async def run_simulation(self, duration=1000):
        """
        Executar simulação
        
        Args:
            duration: Duração em steps do SUMO
        """
        logger.info(f"Iniciando simulação (duração: {duration} steps)...")
        
        step = 0
        try:
            while step < duration and self.traci_conn:
                # Avançar um step no SUMO
                self.traci_conn.simulationStep()
                
                # Log a cada 100 steps
                if step % 100 == 0:
                    vehicle_count = self.traci_conn.vehicle.getIDCount()
                    logger.info(f"Step {step}: {vehicle_count} veículos na simulação")
                    
                step += 1
                await asyncio.sleep(0.01)  # Pequeno delay para não sobrecarregar
                
        except KeyboardInterrupt:
            logger.info("Simulação interrompida pelo usuário")
        except Exception as e:
            logger.error(f"Erro durante simulação: {e}")
        finally:
            logger.info("Finalizando simulação...")
            await self.cleanup()
            
    async def cleanup(self):
        """Limpar recursos"""
        logger.info("Encerrando agentes...")
        
        # Parar todos os agentes SPADE
        for agent in self.agents:
            try:
                await agent.stop()
            except Exception as e:
                logger.error(f"Erro ao parar agente: {e}")
                
        # Fechar conexão TraCI
        if self.traci_conn:
            try:
                traci.close()
                logger.info("Conexão TraCI fechada")
            except Exception as e:
                logger.error(f"Erro ao fechar TraCI: {e}")


async def main():
    """Função principal"""
    import sys
    
    # Verificar se deve usar Docker
    use_docker = "--docker" in sys.argv
    
    if use_docker:
        logger.info("🐳 Modo Docker ativado")
        logger.info("Execute: ./scripts/run_sumo_docker.sh")
        logger.info("Aguardando 5 segundos para SUMO iniciar...")
        await asyncio.sleep(5)
    
    simulation = TrafficSimulation(use_docker=use_docker)
    
    # Iniciar SUMO
    if not simulation.start_sumo():
        logger.error("Falha ao iniciar SUMO. Encerrando.")
        logger.info("\n💡 Soluções:")
        logger.info("1. Use modo Docker: python main_docker.py --docker")
        logger.info("2. Veja TROUBLESHOOTING.md para resolver problema xerces-c")
        return
        
    # Registrar agentes no Prosody
    simulation.register_xmpp_agents()
    
    # Aguardar um momento para garantir que o Prosody processou os registros
    await asyncio.sleep(2)
    
    # Criar agentes SPADE
    await simulation.create_agents()
    
    # Executar simulação
    await simulation.run_simulation(duration=500)
    
    logger.info("Simulação concluída!")


if __name__ == "__main__":
    asyncio.run(main())
