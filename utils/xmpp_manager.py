"""
Gerenciador de agentes XMPP
"""
import subprocess
import logging

logger = logging.getLogger(__name__)


class XMPPAgentManager:
    """Gerenciador para criar e registrar agentes no Prosody"""
    
    def __init__(self, container_name="prosody", domain="localhost"):
        self.container_name = container_name
        self.domain = domain
        
    def register_agent(self, username, password):
        """
        Registrar um agente no servidor Prosody
        
        Args:
            username: Nome do agente
            password: Senha do agente
            
        Returns:
            bool: True se registrado com sucesso
        """
        try:
            cmd = [
                "docker", "exec", "-it", self.container_name,
                "prosodyctl", "register", username, self.domain, password
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.info(f"Agente {username} registrado com sucesso")
                return True
            else:
                logger.error(f"Erro ao registrar {username}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout ao registrar {username}")
            return False
        except Exception as e:
            logger.error(f"Erro ao registrar {username}: {e}")
            return False
            
    def unregister_agent(self, username):
        """Remover registro de um agente"""
        try:
            cmd = [
                "docker", "exec", "-it", self.container_name,
                "prosodyctl", "deluser", f"{username}@{self.domain}"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.info(f"Agente {username} removido com sucesso")
                return True
            else:
                logger.warning(f"Aviso ao remover {username}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao remover {username}: {e}")
            return False
            
    def register_multiple_agents(self, agent_configs):
        """
        Registrar múltiplos agentes
        
        Args:
            agent_configs: Lista de dicionários com 'username' e 'password'
        """
        results = []
        for config in agent_configs:
            success = self.register_agent(
                config['username'],
                config['password']
            )
            results.append({
                'username': config['username'],
                'success': success
            })
        return results
