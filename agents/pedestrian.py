"""
Agente Pedestre - atravessa ruas
"""
from spade.behaviour import CyclicBehaviour
import asyncio
from .base_agent import BaseTrafficAgent


class WalkingBehaviour(CyclicBehaviour):
    """Comportamento de caminhada"""
    
    async def run(self):
        """Ciclo de caminhada"""
        if not self.agent.traci or not self.agent.person_id:
            await asyncio.sleep(1)
            return
            
        try:
            # Obter posição atual
            position = self.agent.traci.person.getPosition(self.agent.person_id)
            road_id = self.agent.traci.person.getRoadID(self.agent.person_id)
            
            # Verificar se chegou ao destino
            if road_id == self.agent.destination:
                self.agent.logger.info(f"Pedestre {self.agent.person_id} chegou ao destino!")
                self.kill()
                return
                
            # Aguardar semáforo se necessário
            await self.wait_for_pedestrian_signal()
            
        except Exception as e:
            self.agent.logger.error(f"Erro durante caminhada: {e}")
            
        await asyncio.sleep(2)
        
    async def wait_for_pedestrian_signal(self):
        """Aguardar sinal de pedestre"""
        # Verificar estado dos semáforos de pedestres próximos
        # Implementar lógica de travessia segura
        pass


class PedestrianAgent(BaseTrafficAgent):
    """Agente pedestre"""
    
    def __init__(self, jid, password, person_id, origin, destination, traci_connection=None):
        super().__init__(jid, password, traci_connection)
        self.person_id = person_id
        self.origin = origin
        self.destination = destination
        
    async def register_behaviours(self):
        """Registrar comportamentos do pedestre"""
        walking_behaviour = WalkingBehaviour()
        self.add_behaviour(walking_behaviour)
