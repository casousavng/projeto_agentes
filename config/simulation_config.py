"""
Configurações da simulação de tráfego
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Configurações XMPP
XMPP_SERVER = os.getenv("XMPP_SERVER", "localhost")
XMPP_PORT = int(os.getenv("XMPP_PORT", 5222))

# Configurações SUMO
SUMO_GUI = os.getenv("SUMO_GUI", "True").lower() == "true"
SUMO_STEP_LENGTH = float(os.getenv("SUMO_STEP_LENGTH", 0.1))
SUMO_PORT = int(os.getenv("SUMO_PORT", 8813))

# Configurações dos agentes
NUM_TRAFFIC_LIGHTS = int(os.getenv("NUM_TRAFFIC_LIGHTS", 4))
NUM_CARS = int(os.getenv("NUM_CARS", 10))
NUM_AMBULANCES = int(os.getenv("NUM_AMBULANCES", 2))
NUM_PEDESTRIANS = int(os.getenv("NUM_PEDESTRIANS", 5))

# Credenciais padrão (para testes - devem ser alteradas)
DEFAULT_PASSWORD = "senha123"

def get_agent_password(agent_name):
    """
    Retorna a senha do agente (convenção: senha = nome do agente)
    Ex: traffic_light_0 -> senha: traffic_light_0
    """
    return agent_name

# Cenário SUMO
SCENARIO_DIR = "scenarios/simple_grid"
NETWORK_FILE = f"{SCENARIO_DIR}/network.net.xml"
ROUTE_FILE = f"{SCENARIO_DIR}/routes.rou.xml"
SUMO_CONFIG = f"{SCENARIO_DIR}/simulation.sumocfg"
