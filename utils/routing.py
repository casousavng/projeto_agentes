"""
Utilidades para roteamento
"""
import numpy as np


class RouteOptimizer:
    """Otimizador de rotas"""
    
    def __init__(self, traci_connection):
        self.traci = traci_connection
        
    def find_optimal_route(self, origin, destination, avoid_congestion=True):
        """
        Encontrar rota ótima entre origem e destino
        
        Args:
            origin: Edge de origem
            destination: Edge de destino
            avoid_congestion: Evitar áreas congestionadas
            
        Returns:
            Lista de edges da rota
        """
        if not self.traci:
            return []
            
        try:
            # Obter rota básica do SUMO
            route = self.traci.simulation.findRoute(origin, destination)
            
            if avoid_congestion:
                # Analisar tráfego em cada segmento
                optimized_route = self._optimize_for_traffic(route.edges)
                return optimized_route
                
            return route.edges
            
        except Exception as e:
            print(f"Erro ao calcular rota: {e}")
            return []
            
    def _optimize_for_traffic(self, edges):
        """Otimizar rota baseado nas condições de tráfego"""
        # Implementar lógica de otimização
        # - Verificar ocupação de cada edge
        # - Buscar alternativas menos congestionadas
        return edges
        
    def estimate_travel_time(self, route):
        """Estimar tempo de viagem para uma rota"""
        if not self.traci or not route:
            return 0
            
        total_time = 0
        try:
            for edge in route:
                # Obter comprimento e velocidade permitida
                length = self.traci.edge.getLength(edge)
                max_speed = self.traci.edge.getMaxSpeed(edge)
                
                # Obter número de veículos
                vehicle_count = self.traci.edge.getLastStepVehicleNumber(edge)
                
                # Ajustar velocidade baseado no tráfego
                adjusted_speed = max_speed * (1 - min(vehicle_count * 0.1, 0.8))
                
                # Calcular tempo
                if adjusted_speed > 0:
                    total_time += length / adjusted_speed
                    
        except Exception as e:
            print(f"Erro ao estimar tempo: {e}")
            
        return total_time
        
    def get_alternative_routes(self, origin, destination, num_alternatives=3):
        """Obter rotas alternativas"""
        # Implementar busca de rotas alternativas
        routes = []
        
        # Por enquanto retorna apenas a rota principal
        main_route = self.find_optimal_route(origin, destination)
        if main_route:
            routes.append(main_route)
            
        return routes
