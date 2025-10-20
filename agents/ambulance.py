"""
Agente Ambulância - modo urgência com prioridade
"""
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import asyncio
from .car import CarAgent


class EmergencyBehaviour(CyclicBehaviour):
    """Comportamento de emergência"""
    
    async def run(self):
        """Ciclo de emergência"""
        if not self.agent.urgent_mode:
            await asyncio.sleep(1)
            return
            
        # Solicitar prioridade nos semáforos
        await self.request_traffic_light_priority()
        
        # Aumentar velocidade no SUMO
        if self.agent.traci and self.agent.vehicle_id:
            try:
                self.agent.traci.vehicle.setMaxSpeed(self.agent.vehicle_id, 25.0)
                self.agent.traci.vehicle.setColor(self.agent.vehicle_id, (255, 0, 0, 255))
            except Exception as e:
                self.agent.logger.error(f"Erro ao ajustar velocidade: {e}")
                
        await asyncio.sleep(5)
        
    async def request_traffic_light_priority(self):
        """Solicitar prioridade aos semáforos próximos"""
        # Obter semáforos próximos
        if not self.agent.traci or not self.agent.vehicle_id:
            return
            
        try:
            # Obter edge atual
            current_edge = self.agent.traci.vehicle.getRoadID(self.agent.vehicle_id)
            
            # Encontrar semáforos na rota
            for tl_id in self.agent.traci.trafficlight.getIDList():
                # Enviar mensagem XMPP para agente do semáforo
                msg = Message(to=f"trafficlight_{tl_id}@localhost")
                msg.body = f"PRIORITY_REQUEST:{self.agent.vehicle_id}"
                await self.send(msg)
                
                self.agent.logger.info(f"Prioridade solicitada ao semáforo {tl_id}")
                
        except Exception as e:
            self.agent.logger.error(f"Erro ao solicitar prioridade: {e}")


class AmbulanceAgent(CarAgent):
    """Agente ambulância com modo de urgência"""
    
    def __init__(self, jid, password, vehicle_id, origin, destination, 
                 urgent_mode=False, traci_connection=None):
        super().__init__(jid, password, vehicle_id, origin, destination, traci_connection)
        self.urgent_mode = urgent_mode
        
    async def register_behaviours(self):
        """Registrar comportamentos da ambulância"""
        # Comportamentos básicos de carro
        await super().register_behaviours()
        
        # Comportamento de emergência adicional
        if self.urgent_mode:
            emergency_behaviour = EmergencyBehaviour()
            self.add_behaviour(emergency_behaviour)
            
    def activate_urgent_mode(self):
        """Ativar modo de urgência"""
        self.urgent_mode = True
        self.logger.info("Modo de urgência ATIVADO")
        
    def deactivate_urgent_mode(self):
        """Desativar modo de urgência"""
        self.urgent_mode = False
        self.logger.info("Modo de urgência DESATIVADO")
