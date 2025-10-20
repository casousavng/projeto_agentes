"""
Agente Semáforo - controla intersecções
"""
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import asyncio
from .base_agent import BaseTrafficAgent


class TrafficLightBehaviour(CyclicBehaviour):
    """Comportamento do semáforo"""
    
    def __init__(self, light_id, phase_duration=30):
        super().__init__()
        self.light_id = light_id
        self.phase_duration = phase_duration
        self.current_phase = 0
        self.priority_mode = False
        
    async def run(self):
        """Ciclo principal do semáforo"""
        # Verificar mensagens de prioridade (ambulâncias)
        msg = await self.receive(timeout=1)
        if msg:
            await self.handle_priority_request(msg)
            
        # Controlar fases do semáforo no SUMO
        if self.agent.traci:
            try:
                self.agent.traci.trafficlight.setPhase(
                    self.light_id, 
                    self.current_phase
                )
            except Exception as e:
                self.agent.logger.error(f"Erro ao controlar semáforo: {e}")
                
        await asyncio.sleep(self.phase_duration)
        
        # Alternar fase
        if not self.priority_mode:
            self.current_phase = (self.current_phase + 1) % 4
            
    async def handle_priority_request(self, msg):
        """Processar requisição de prioridade"""
        self.agent.logger.info(f"Requisição de prioridade recebida: {msg.body}")
        self.priority_mode = True
        self.current_phase = 0  # Verde para a direção prioritária
        await asyncio.sleep(10)  # Manter verde por 10s
        self.priority_mode = False


class TrafficLightAgent(BaseTrafficAgent):
    """Agente semáforo"""
    
    def __init__(self, jid, password, light_id, traci_connection=None):
        super().__init__(jid, password, traci_connection)
        self.light_id = light_id
        
    async def register_behaviours(self):
        """Registrar comportamento do semáforo"""
        behaviour = TrafficLightBehaviour(self.light_id)
        self.add_behaviour(behaviour)
