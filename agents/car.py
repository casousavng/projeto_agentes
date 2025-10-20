"""
Agente Carro - busca rotas ótimas
"""
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message
import asyncio
from .base_agent import BaseTrafficAgent


class RouteCalculationBehaviour(OneShotBehaviour):
    """Comportamento para calcular rota ótima"""
    
    async def run(self):
        """Calcular melhor rota de A para B"""
        if not self.agent.traci:
            return
            
        try:
            # Obter rota do SUMO
            route = self.agent.traci.simulation.findRoute(
                self.agent.origin,
                self.agent.destination
            )
            
            self.agent.current_route = route.edges
            self.agent.logger.info(
                f"Rota calculada: {len(route.edges)} segmentos, "
                f"tempo estimado: {route.travelTime:.2f}s"
            )
        except Exception as e:
            self.agent.logger.error(f"Erro ao calcular rota: {e}")


class DrivingBehaviour(CyclicBehaviour):
    """Comportamento de condução"""
    
    async def run(self):
        """Ciclo de condução"""
        if not self.agent.traci or not self.agent.vehicle_id:
            await asyncio.sleep(1)
            return
            
        try:
            # Verificar se chegou ao destino
            if self.agent.traci.vehicle.getRoadID(self.agent.vehicle_id) == self.agent.destination:
                self.agent.logger.info(f"Veículo {self.agent.vehicle_id} chegou ao destino!")
                self.kill()
                return
                
            # Obter informações do veículo
            speed = self.agent.traci.vehicle.getSpeed(self.agent.vehicle_id)
            position = self.agent.traci.vehicle.getPosition(self.agent.vehicle_id)
            
            # Verificar tráfego e ajustar velocidade
            await self.check_traffic_conditions()
            
        except Exception as e:
            self.agent.logger.error(f"Erro durante condução: {e}")
            
        await asyncio.sleep(1)
        
    async def check_traffic_conditions(self):
        """Verificar condições de tráfego"""
        # Aqui pode implementar lógica para:
        # - Detectar congestionamentos
        # - Recalcular rota se necessário
        # - Comunicar com outros agentes
        pass


class CarAgent(BaseTrafficAgent):
    """Agente carro"""
    
    def __init__(self, jid, password, vehicle_id, origin, destination, traci_connection=None):
        super().__init__(jid, password, traci_connection)
        self.vehicle_id = vehicle_id
        self.origin = origin
        self.destination = destination
        self.current_route = []
        
    async def register_behaviours(self):
        """Registrar comportamentos do carro"""
        # Primeiro calcular rota
        route_behaviour = RouteCalculationBehaviour()
        self.add_behaviour(route_behaviour)
        
        # Depois iniciar condução
        await asyncio.sleep(2)  # Aguardar cálculo da rota
        driving_behaviour = DrivingBehaviour()
        self.add_behaviour(driving_behaviour)
