"""
Agente base para todos os agentes da simulação
"""
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from abc import ABC, abstractmethod
import logging

logging.basicConfig(level=logging.INFO)


class BaseTrafficAgent(Agent, ABC):
    """
    Classe base para todos os agentes de tráfego
    """
    
    def __init__(self, jid, password, traci_connection=None):
        super().__init__(jid, password)
        self.verify_security = False  # Desabilitar verificação SSL (desenvolvimento)
        self.traci = traci_connection
        self.logger = logging.getLogger(self.__class__.__name__)
        
    async def setup(self):
        """Configuração inicial do agente"""
        self.logger.info(f"Agente {self.jid} iniciado")
        await self.register_behaviours()
        
    @abstractmethod
    async def register_behaviours(self):
        """Registrar comportamentos específicos do agente"""
        pass
        
    def get_position(self):
        """Obter posição atual no SUMO"""
        pass
