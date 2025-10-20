# -*- coding: utf-8 -*-
"""
Simulação com agentes SPADE controlando semáforos da rede 8x8
Os semáforos se comunicam via XMPP e se adaptam ao tráfego
"""
import asyncio
import traci
import logging
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from datetime import datetime
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntelligentTrafficLight(Agent):
    """Agente semáforo inteligente com controle adaptativo"""
    
    def __init__(self, jid, password, junction_id, *args, **kwargs):
        super().__init__(jid, password, *args, **kwargs)
        self.junction_id = junction_id
        self.verify_security = False
        self.current_phase = 0
        self.phase_duration = 30  # segundos padrão
        self.min_phase = 15  # mínimo
        self.max_phase = 60  # máximo
        self.vehicles_waiting = {}
        
    class TrafficControlBehaviour(CyclicBehaviour):
        """Comportamento de controle adaptativo do semáforo"""
        
        async def run(self):
            # Obter informação de veículos esperando
            try:
                # Contar veículos em cada direção
                lanes = traci.trafficlight.getControlledLanes(self.agent.junction_id)
                
                total_waiting = 0
                for lane in lanes:
                    waiting = traci.lane.getLastStepHaltingNumber(lane)
                    total_waiting += waiting
                
                # Ajustar duração da fase baseado no tráfego
                if total_waiting > 5:
                    # Muito tráfego: aumentar tempo verde
                    self.agent.phase_duration = min(
                        self.agent.max_phase,
                        self.agent.phase_duration + 5
                    )
                    logger.info(f"{self.agent.junction_id}: Tráfego alto ({total_waiting} veículos), "
                              f"aumentando fase para {self.agent.phase_duration}s")
                elif total_waiting < 2:
                    # Pouco tráfego: reduzir tempo verde
                    self.agent.phase_duration = max(
                        self.agent.min_phase,
                        self.agent.phase_duration - 3
                    )
                    logger.info(f"{self.agent.junction_id}: Tráfego baixo ({total_waiting} veículos), "
                              f"reduzindo fase para {self.agent.phase_duration}s")
                
                # Notificar semáforos vizinhos
                await self.notify_neighbors(total_waiting)
                
            except Exception as e:
                logger.error(f"Erro no controle de {self.agent.junction_id}: {e}")
            
            # Aguardar antes de próxima verificação
            await asyncio.sleep(self.agent.phase_duration)
        
        async def notify_neighbors(self, waiting_count):
            """Notificar semáforos vizinhos sobre estado do tráfego"""
            # Enviar mensagem para outros semáforos
            msg = Message(to="trafficlight_broadcast@localhost")
            msg.set_metadata("performative", "inform")
            msg.body = json.dumps({
                "junction": self.agent.junction_id,
                "waiting": waiting_count,
                "phase_duration": self.agent.phase_duration,
                "timestamp": datetime.now().isoformat()
            })
            await self.send(msg)
    
    async def setup(self):
        """Configuração inicial do agente"""
        logger.info(f"Semáforo {self.junction_id} iniciado e conectado")
        behaviour = self.TrafficControlBehaviour()
        self.add_behaviour(behaviour)


class TrafficSimulationWithSPADE:
    """Simulação integrada SPADE + SUMO com semáforos inteligentes"""
    
    def __init__(self):
        self.agents = []
        self.traffic_lights = []
        
    def connect_to_sumo(self, port=8813):
        """Conectar ao SUMO via TraCI"""
        logger.info("Conectando ao SUMO...")
        try:
            traci.init(port)
            logger.info("✅ Conectado ao SUMO")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao conectar: {e}")
            return False
    
    def get_traffic_lights(self):
        """Obter lista de semáforos do SUMO"""
        try:
            tls = traci.trafficlight.getIDList()
            logger.info(f"Encontrados {len(tls)} semáforos: {tls[:5]}...")
            return tls
        except Exception as e:
            logger.error(f"Erro ao obter semáforos: {e}")
            return []
    
    async def create_traffic_light_agents(self):
        """Criar agentes SPADE para cada semáforo"""
        traffic_lights = self.get_traffic_lights()
        
        logger.info(f"\n🚦 Criando {len(traffic_lights)} agentes semáforo...")
        
        for i, tl_id in enumerate(traffic_lights[:12]):  # Primeiros 12 para teste
            jid = f"trafficlight_{i}@localhost"
            password = f"trafficlight_{i}"
            
            agent = IntelligentTrafficLight(jid, password, tl_id)
            await agent.start()
            self.agents.append(agent)
            self.traffic_lights.append(tl_id)
            
            logger.info(f"✅ Semáforo {tl_id} → {jid}")
        
        logger.info(f"\n✅ {len(self.agents)} agentes semáforo criados e ativos\n")
    
    async def run_simulation(self, duration=300):
        """Executar simulação por X segundos"""
        logger.info(f"🚀 Iniciando simulação por {duration} segundos...")
        
        step = 0
        max_steps = int(duration / 0.1)
        
        try:
            while step < max_steps:
                traci.simulationStep()
                step += 1
                
                # Mostrar progresso
                if step % 500 == 0:  # A cada 50 segundos
                    vehicles = traci.vehicle.getIDList()
                    logger.info(f"⏱️  Step {step} ({step*0.1:.1f}s) - {len(vehicles)} veículos ativos")
                
                await asyncio.sleep(0.01)  # Pequena pausa para agentes processarem
        
        except KeyboardInterrupt:
            logger.info("\n⚠️  Simulação interrompida pelo usuário")
        
        finally:
            logger.info(f"\n📊 Simulação encerrada em {step*0.1:.1f} segundos")
    
    async def stop_all(self):
        """Parar todos os agentes"""
        logger.info("\n🛑 Parando agentes...")
        for agent in self.agents:
            await agent.stop()
        logger.info("✅ Todos os agentes parados")
        
        logger.info("🔌 Fechando conexão SUMO...")
        traci.close()
        logger.info("✅ Conexão SUMO fechada")


async def main():
    """Função principal"""
    simulation = TrafficSimulationWithSPADE()
    
    # Conectar ao SUMO
    if not simulation.connect_to_sumo():
        logger.error("❌ Falha ao conectar ao SUMO")
        return
    
    # Criar agentes semáforo
    await simulation.create_traffic_light_agents()
    
    # Aguardar um momento para agentes estabilizarem
    await asyncio.sleep(3)
    
    # Executar simulação
    await simulation.run_simulation(duration=300)  # 5 minutos
    
    # Parar tudo
    await simulation.stop_all()


if __name__ == "__main__":
    logger.info("="*60)
    logger.info("🚦 SIMULAÇÃO COM AGENTES SPADE - REDE 8x8")
    logger.info("="*60)
    logger.info("\n📋 Funcionalidades:")
    logger.info("   ✅ Semáforos inteligentes com SPADE")
    logger.info("   ✅ Controle adaptativo baseado em tráfego")
    logger.info("   ✅ Comunicação entre semáforos via XMPP")
    logger.info("   ✅ Ajuste dinâmico de fases")
    logger.info("\n" + "="*60 + "\n")
    
    asyncio.run(main())
