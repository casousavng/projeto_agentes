#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulacao Dinamica de Trafego com Roteamento Inteligente
- Ruas com pesos/distancias diferentes
- Algoritmo A* para roteamento dinamico
- Multiplos veiculos (carros e ambulancias)
- Semaforos dinamicos que influenciam rotas
- Recalculo de rotas em tempo real
"""

import pygame
import sys
import threading
import time
import subprocess
import random
import heapq
from queue import Queue
from typing import Dict, List, Tuple, Optional
import math

# Configuracoes Pygame
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
SIDEBAR_WIDTH = 300
FPS = 30

# Cores
COLOR_BG = (26, 26, 46)
COLOR_SIDEBAR = (15, 15, 30)
COLOR_ROAD_BORDER = (50, 50, 50)
COLOR_ROAD_LANE1 = (70, 70, 70)
COLOR_ROAD_LANE2 = (60, 60, 60)
COLOR_LANE_DIVIDER = (200, 200, 100)
COLOR_NODE = (100, 100, 100)
COLOR_VEHICLE_NORMAL = (59, 130, 246)
COLOR_VEHICLE_JOURNEY = (16, 185, 129)  # Verde para carro principal
COLOR_VEHICLE_AMBULANCE = (220, 38, 38)
COLOR_LIGHT_GREEN = (16, 185, 129)
COLOR_LIGHT_YELLOW = (251, 191, 36)
COLOR_LIGHT_RED = (239, 68, 68)
COLOR_TEXT = (255, 255, 255)
COLOR_ACCENT = (102, 126, 234)
COLOR_DISTANCE_LABEL = (150, 150, 200)

# Tipos de ruas e seus pesos
ROAD_TYPES = {
    'highway': {'speed_limit': 80, 'weight': 1.0, 'color': (90, 90, 90)},    # Rapida
    'main': {'speed_limit': 60, 'weight': 1.5, 'color': (70, 70, 70)},       # Principal
    'secondary': {'speed_limit': 40, 'weight': 2.5, 'color': (60, 60, 60)},  # Secundaria
    'residential': {'speed_limit': 30, 'weight': 3.0, 'color': (50, 50, 50)} # Residencial
}

class Vehicle:
    """Classe para representar um veiculo"""
    def __init__(self, vehicle_id, start_node, end_node, vehicle_type='car'):
        self.id = vehicle_id
        self.type = vehicle_type  # 'car', 'ambulance', 'journey'
        self.start_node = start_node
        self.end_node = end_node
        self.current_node = start_node
        self.target_node = None
        self.route = []
        self.route_index = 0
        self.x = 0
        self.y = 0
        self.speed = 80 if vehicle_type == 'ambulance' else 60 if vehicle_type == 'car' else 50
        self.waiting_time = 0
        self.total_travel_time = 0  # Tempo total de viagem
        self.current_edge_id = None  # Aresta atual
        
        # Cor baseada no tipo
        if vehicle_type == 'ambulance':
            self.color = COLOR_VEHICLE_AMBULANCE
        elif vehicle_type == 'journey':
            self.color = COLOR_VEHICLE_JOURNEY
        else:
            self.color = COLOR_VEHICLE_NORMAL
            
        self.arrival_time = None
        self.moving = True

class DynamicTrafficSimulation:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Simulacao Dinamica de Trafego com Roteamento Inteligente")
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.SysFont('Arial', 24, bold=True)
        self.font_stats = pygame.font.SysFont('Arial', 16, bold=True)
        self.font_label = pygame.font.SysFont('Arial', 12)
        
        # Rede com pesos
        self.nodes = {}
        self.edges = {}
        self.graph = {}  # Grafo para A*
        self.load_network_with_weights()
        
        # Viewport
        self.viewport = self._calculate_viewport()
        
        # Semaforos
        self.traffic_lights = {}
        self.create_traffic_lights()
        
        # Veiculos
        self.vehicles = []
        self.next_vehicle_id = 0
        self.journey_vehicle = None  # Veiculo principal A->B
        
        # Rastreamento de congestionamento (quantos veiculos por aresta)
        self.edge_traffic_count = {}  # {edge_id: count}
        
        # Sistema de comunicacao entre agentes (reportes de trafego)
        self.traffic_reports = {}  # {edge_id: {'delay': float, 'reports_count': int}}
        
        # Estatisticas
        self.stats = {
            'step': 0,
            'total_vehicles': 0,
            'active_vehicles': 0,
            'completed_trips': 0,
            'avg_trip_time': 0,
            'total_waiting': 0,
            'congested_edges': 0  # Arestas com congestionamento
        }
        
        # Estado
        self.running = False
        self.paused = False
        self.simulation_thread = None
        self.start_time = 0
        
        print("Simulacao inicializada!")
        print("Nos:", len(self.nodes))
        print("Arestas:", len(self.edges))
        print("Semaforos:", len(self.traffic_lights))
    
    def load_network_with_weights(self):
        """Carrega rede 8x8 com pesos diferentes nas ruas (distancias variam)"""
        base_spacing = 180
        
        # Criar nos com posicoes variadas (matriz torta)
        for row in range(8):
            for col in range(8):
                node_id = str(row) + "_" + str(col)
                
                # Adicionar variacao para simular mapa real (nao perfeitamente quadrado)
                x_variation = random.uniform(-15, 15)
                y_variation = random.uniform(-15, 15)
                
                self.nodes[node_id] = {
                    'id': node_id,
                    'x': col * base_spacing + x_variation,
                    'y': row * base_spacing + y_variation,
                    'row': row,
                    'col': col
                }
        
        # Criar arestas com pesos variados
        edge_id = 0
        for row in range(8):
            for col in range(8):
                from_id = str(row) + "_" + str(col)
                
                # Horizontal (esquerda -> direita e direita -> esquerda)
                if col < 7:
                    to_id = str(row) + "_" + str(col + 1)
                    
                    # Calcular distancia real entre nos
                    from_node = self.nodes[from_id]
                    to_node = self.nodes[to_id]
                    dx = to_node['x'] - from_node['x']
                    dy = to_node['y'] - from_node['y']
                    real_distance = math.sqrt(dx * dx + dy * dy)
                    
                    # Atribuir tipo de rua baseado na posicao
                    if row in [0, 7] or col in [0, 6]:  # Perifericas sao highways
                        road_type = 'highway'
                    elif row in [2, 5]:  # Algumas principais
                        road_type = 'main'
                    elif row in [3, 4]:  # Secundarias
                        road_type = 'secondary'
                    else:
                        road_type = 'residential'
                    
                    # Adicionar variacao aleatoria (+/- 20%)
                    base_weight = ROAD_TYPES[road_type]['weight']
                    weight = base_weight * random.uniform(0.8, 1.2)
                    
                    # Aresta da esquerda para direita
                    self.edges[edge_id] = {
                        'id': edge_id,
                        'from': from_id,
                        'to': to_id,
                        'type': road_type,
                        'weight': weight,
                        'distance': real_distance,
                        'speed_limit': ROAD_TYPES[road_type]['speed_limit']
                    }
                    edge_id += 1
                    
                    # Aresta da direita para esquerda (sentido oposto)
                    self.edges[edge_id] = {
                        'id': edge_id,
                        'from': to_id,
                        'to': from_id,
                        'type': road_type,
                        'weight': weight,
                        'distance': real_distance,
                        'speed_limit': ROAD_TYPES[road_type]['speed_limit']
                    }
                    edge_id += 1
                
                # Vertical (cima -> baixo e baixo -> cima)
                if row < 7:
                    to_id = str(row + 1) + "_" + str(col)
                    
                    # Calcular distancia real
                    from_node = self.nodes[from_id]
                    to_node = self.nodes[to_id]
                    dx = to_node['x'] - from_node['x']
                    dy = to_node['y'] - from_node['y']
                    real_distance = math.sqrt(dx * dx + dy * dy)
                    
                    if col in [0, 7] or row in [0, 6]:
                        road_type = 'highway'
                    elif col in [2, 5]:
                        road_type = 'main'
                    elif col in [3, 4]:
                        road_type = 'secondary'
                    else:
                        road_type = 'residential'
                    
                    base_weight = ROAD_TYPES[road_type]['weight']
                    weight = base_weight * random.uniform(0.8, 1.2)
                    
                    # Aresta de cima para baixo
                    self.edges[edge_id] = {
                        'id': edge_id,
                        'from': from_id,
                        'to': to_id,
                        'type': road_type,
                        'weight': weight,
                        'distance': real_distance,
                        'speed_limit': ROAD_TYPES[road_type]['speed_limit']
                    }
                    edge_id += 1
                    
                    # Aresta de baixo para cima
                    self.edges[edge_id] = {
                        'id': edge_id,
                        'from': to_id,
                        'to': from_id,
                        'type': road_type,
                        'weight': weight,
                        'distance': real_distance,
                        'speed_limit': ROAD_TYPES[road_type]['speed_limit']
                    }
                    edge_id += 1
        
        # Construir grafo para A*
        self.build_graph()
    
    def build_graph(self):
        """Constroi grafo de adjacencia para algoritmo A*"""
        self.graph = {node_id: [] for node_id in self.nodes}
        
        for edge in self.edges.values():
            from_id = edge['from']
            to_id = edge['to']
            weight = edge['weight']
            
            self.graph[from_id].append({
                'node': to_id,
                'weight': weight,
                'edge_id': edge['id']
            })
    
    def create_traffic_lights(self):
        """Cria semaforos espalhados pelo mapa com temporizadores diferentes"""
        # MUITO MAIS semaforos espalhados por todo o mapa (42 semaforos)
        tl_positions = [
            # Cantos
            (0, 0), (0, 7), (7, 0), (7, 7),
            # Bordas superiores e inferiores
            (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6),
            (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6),
            # Bordas laterais
            (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0),
            (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7),
            # Intersecoes internas principais
            (1, 1), (1, 3), (1, 5), (1, 6),
            (2, 2), (2, 4), (2, 5),
            (3, 1), (3, 3), (3, 4), (3, 6),
            (4, 2), (4, 4), (4, 5),
            (5, 1), (5, 2), (5, 5), (5, 6)
        ]
        
        for row, col in tl_positions:
            tl_id = str(row) + "_" + str(col)
            
            # Temporizadores aleatorios e diferentes para cada semaforo
            green_time = random.randint(15, 50)  # Verde: 15-50 steps
            red_time = random.randint(15, 45)    # Vermelho: 15-45 steps
            yellow_time = random.randint(2, 5)   # Amarelo: 2-5 steps
            
            # Estado inicial aleatorio
            initial_state = random.choice(['green', 'red'])
            
            self.traffic_lights[tl_id] = {
                'id': tl_id,
                'node_id': tl_id,
                'state': initial_state,
                'timer': 0,
                'green_time': green_time,
                'yellow_time': yellow_time,
                'red_time': red_time,
                'cycle_time': 0
            }
    
    def heuristic(self, node1_id, node2_id):
        """Heuristica euclidiana para A*"""
        n1 = self.nodes[node1_id]
        n2 = self.nodes[node2_id]
        dx = n1['x'] - n2['x']
        dy = n1['y'] - n2['y']
        return math.sqrt(dx * dx + dy * dy) / 180.0  # Normalizar
    
    def update_edge_traffic_counts(self):
        """Atualiza contagem de veiculos em cada aresta para detectar congestionamento"""
        self.edge_traffic_count = {}
        
        for vehicle in self.vehicles:
            if not vehicle.moving or vehicle.route_index >= len(vehicle.route) - 1:
                continue
            
            current_node = vehicle.current_node
            target_node = vehicle.target_node
            
            # Encontrar aresta correspondente
            for edge in self.edges.values():
                if edge['from'] == current_node and edge['to'] == target_node:
                    edge_id = edge['id']
                    if edge_id not in self.edge_traffic_count:
                        self.edge_traffic_count[edge_id] = 0
                    self.edge_traffic_count[edge_id] += 1
                    break
    
    def get_congestion_penalty(self, edge_id):
        """Calcula penalidade de congestionamento para uma aresta"""
        count = self.edge_traffic_count.get(edge_id, 0)
        
        if count == 0:
            return 1.0  # Sem congestionamento
        elif count == 1:
            return 1.2  # Leve
        elif count == 2:
            return 1.5  # Moderado
        elif count == 3:
            return 2.0  # Pesado
        else:
            return 3.0  # Muito pesado
    
    def predict_traffic_light_state(self, node_id, steps_ahead=10):
        """Prevê o estado do semáforo após X steps (olhar para o futuro)"""
        if node_id not in self.traffic_lights:
            return 'none'
        
        tl = self.traffic_lights[node_id]
        current_state = tl['state']
        cycle_time = tl['cycle_time']
        
        # Simular ciclo do semaforo
        time_remaining = cycle_time
        simulated_state = current_state
        
        for _ in range(steps_ahead):
            time_remaining += 1
            
            if simulated_state == 'green':
                if time_remaining >= tl['green_time']:
                    simulated_state = 'yellow'
                    time_remaining = 0
            elif simulated_state == 'yellow':
                if time_remaining >= tl['yellow_time']:
                    simulated_state = 'red'
                    time_remaining = 0
            elif simulated_state == 'red':
                if time_remaining >= tl['red_time']:
                    simulated_state = 'green'
                    time_remaining = 0
        
        return simulated_state
    
    def get_traffic_report_penalty(self, edge_id):
        """Obtem penalidade baseada em reportes de outros agentes"""
        if edge_id not in self.traffic_reports:
            return 1.0
        
        report = self.traffic_reports[edge_id]
        avg_delay = report['delay'] / max(report['reports_count'], 1)
        
        # Converter delay em penalidade (quanto maior o delay, maior a penalidade)
        if avg_delay > 50:
            return 2.5
        elif avg_delay > 30:
            return 2.0
        elif avg_delay > 15:
            return 1.5
        elif avg_delay > 5:
            return 1.2
        else:
            return 1.0
    
    def get_dynamic_weight(self, edge_id, is_journey=False, look_ahead_steps=15):
        """Calcula peso dinamico da aresta considerando semaforos E congestionamento E comunicacao"""
        edge = self.edges[edge_id]
        base_weight = edge['weight']
        
        # Penalidade por semaforo (olhar para o futuro para journey)
        semaphore_penalty = 1.0
        to_node = edge['to']
        if to_node in self.traffic_lights:
            if is_journey:
                # Veiculo journey prevê estado futuro do semaforo
                future_state = self.predict_traffic_light_state(to_node, look_ahead_steps)
                if future_state == 'red':
                    semaphore_penalty = 2.5  # Menor penalidade pois pode mudar
                elif future_state == 'yellow':
                    semaphore_penalty = 1.3
            else:
                # Outros veiculos olham estado atual
                tl = self.traffic_lights[to_node]
                if tl['state'] == 'red':
                    semaphore_penalty = 3.0
                elif tl['state'] == 'yellow':
                    semaphore_penalty = 1.5
        
        # Penalidade por congestionamento atual
        congestion_penalty = self.get_congestion_penalty(edge_id)
        
        # Penalidade por reportes de trafego de outros agentes
        report_penalty = self.get_traffic_report_penalty(edge_id)
        
        # Peso final considera TODOS os fatores
        final_weight = base_weight * semaphore_penalty * congestion_penalty * report_penalty
        
        return final_weight
    
    def find_route_astar(self, start_id, end_id, is_ambulance=False, is_journey=False):
        """Algoritmo A* para encontrar melhor rota com previsao e comunicacao"""
        if start_id == end_id:
            return [start_id]
        
        open_set = []
        heapq.heappush(open_set, (0, start_id))
        
        came_from = {}
        g_score = {node_id: float('inf') for node_id in self.nodes}
        g_score[start_id] = 0
        
        f_score = {node_id: float('inf') for node_id in self.nodes}
        f_score[start_id] = self.heuristic(start_id, end_id)
        
        while open_set:
            current = heapq.heappop(open_set)[1]
            
            if current == end_id:
                # Reconstruir caminho
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path
            
            for neighbor in self.graph[current]:
                neighbor_id = neighbor['node']
                edge_weight = neighbor['weight']
                
                # Ambulancia ignora semaforos
                if not is_ambulance:
                    # Veiculos journey usam previsao e comunicacao entre agentes
                    edge_weight = self.get_dynamic_weight(neighbor['edge_id'], is_journey=is_journey)
                else:
                    edge_weight *= 0.5  # Ambulancia mais rapida
                
                tentative_g = g_score[current] + edge_weight
                
                if tentative_g < g_score[neighbor_id]:
                    came_from[neighbor_id] = current
                    g_score[neighbor_id] = tentative_g
                    f_score[neighbor_id] = tentative_g + self.heuristic(neighbor_id, end_id)
                    heapq.heappush(open_set, (f_score[neighbor_id], neighbor_id))
        
        return None  # Sem rota
    
    def spawn_vehicle(self, vehicle_type='car', start_node=None, end_node=None):
        """Cria novo veiculo com origem e destino aleatorios ou especificos"""
        # Escolher nos aleatorios ou usar especificados
        node_ids = list(self.nodes.keys())
        
        if start_node is None:
            start_id = random.choice(node_ids)
        else:
            start_id = start_node
            
        if end_node is None:
            end_id = random.choice(node_ids)
            while start_id == end_id:
                end_id = random.choice(node_ids)
        else:
            end_id = end_node
        
        vehicle_id = "v" + str(self.next_vehicle_id)
        self.next_vehicle_id += 1
        
        vehicle = Vehicle(vehicle_id, start_id, end_id, vehicle_type)
        
        # Calcular rota inicial
        route = self.find_route_astar(
            start_id, 
            end_id, 
            is_ambulance=(vehicle_type == 'ambulance'),
            is_journey=(vehicle_type == 'journey')
        )
        if route:
            vehicle.route = route
            vehicle.route_index = 0
            vehicle.current_node = route[0]
            vehicle.target_node = route[1] if len(route) > 1 else route[0]
            
            # Posicao inicial
            start_node = self.nodes[start_id]
            vehicle.x = start_node['x']
            vehicle.y = start_node['y']
            
            self.vehicles.append(vehicle)
            self.stats['total_vehicles'] += 1
            
            print("Veiculo criado:", vehicle_id, vehicle_type, "rota:", len(route), "nos")
            return vehicle
        
        return None
    
    def update_traffic_lights(self):
        """Atualiza estado dos semaforos"""
        for tl in self.traffic_lights.values():
            tl['cycle_time'] += 1
            
            if tl['state'] == 'green':
                if tl['cycle_time'] >= tl['green_time']:
                    tl['state'] = 'yellow'
                    tl['cycle_time'] = 0
            elif tl['state'] == 'yellow':
                if tl['cycle_time'] >= tl['yellow_time']:
                    tl['state'] = 'red'
                    tl['cycle_time'] = 0
            elif tl['state'] == 'red':
                if tl['cycle_time'] >= tl['red_time']:
                    tl['state'] = 'green'
                    tl['cycle_time'] = 0
    
    def report_traffic(self, vehicle, edge_id, delay):
        """Veiculo reporta condicoes de trafego em uma aresta (comunicacao entre agentes)"""
        if edge_id not in self.traffic_reports:
            self.traffic_reports[edge_id] = {'delay': 0, 'reports_count': 0}
        
        self.traffic_reports[edge_id]['delay'] += delay
        self.traffic_reports[edge_id]['reports_count'] += 1
    
    def update_vehicle(self, vehicle):
        """Atualiza posicao de um veiculo"""
        vehicle.total_travel_time += 1  # Incrementar tempo de viagem
        
        if vehicle.route_index >= len(vehicle.route) - 1:
            # Chegou ao destino
            if not vehicle.arrival_time:
                vehicle.arrival_time = self.stats['step']
                trip_time = vehicle.arrival_time - 0  # Simplificado
                self.stats['completed_trips'] += 1
                print("Veiculo", vehicle.id, "chegou ao destino! Tempo:", vehicle.total_travel_time, "steps")
            vehicle.moving = False
            return
        
        # Posicao atual e alvo
        current_node = self.nodes[vehicle.current_node]
        target_node = self.nodes[vehicle.target_node]
        
        # Encontrar aresta atual para reportar trafego
        if vehicle.current_edge_id is None:
            for edge in self.edges.values():
                if edge['from'] == vehicle.current_node and edge['to'] == vehicle.target_node:
                    vehicle.current_edge_id = edge['id']
                    break
        
        # Calcular direcao
        dx = target_node['x'] - vehicle.x
        dy = target_node['y'] - vehicle.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < 5:  # Chegou ao proximo no
            # Reportar trafego da aresta que acabou de percorrer
            if vehicle.current_edge_id is not None:
                self.report_traffic(vehicle, vehicle.current_edge_id, vehicle.waiting_time)
                vehicle.current_edge_id = None  # Reset
            
            vehicle.route_index += 1
            if vehicle.route_index < len(vehicle.route):
                vehicle.current_node = vehicle.route[vehicle.route_index]
                if vehicle.route_index + 1 < len(vehicle.route):
                    vehicle.target_node = vehicle.route[vehicle.route_index + 1]
                    
                    # Recalcular rota dinamicamente considerando semaforos e congestionamento
                    # Veiculos journey recalculam MUITO mais frequentemente (40% chance)
                    # Outros veiculos recalculam menos (10% chance)
                    recalc_chance = 0.4 if vehicle.type == 'journey' else 0.1
                    
                    if vehicle.type != 'ambulance' and random.random() < recalc_chance:
                        new_route = self.find_route_astar(
                            vehicle.current_node,
                            vehicle.end_node,
                            is_ambulance=(vehicle.type == 'ambulance'),
                            is_journey=(vehicle.type == 'journey')
                        )
                        if new_route and len(new_route) < len(vehicle.route) - vehicle.route_index:
                            old_length = len(vehicle.route) - vehicle.route_index
                            vehicle.route = vehicle.route[:vehicle.route_index] + new_route
                            vehicle.target_node = vehicle.route[vehicle.route_index + 1]
                            print(f"Veiculo {vehicle.id} recalculou rota! {old_length} -> {len(new_route)} nos (economia: {old_length - len(new_route)})")
        else:
            # Mover em direcao ao alvo
            speed_pixels = vehicle.speed / 10.0  # Simplificado
            
            # Verificar semaforo
            can_move = True
            if vehicle.current_node in self.traffic_lights:
                tl = self.traffic_lights[vehicle.current_node]
                if tl['state'] == 'red' and vehicle.type != 'ambulance':
                    can_move = False
                    vehicle.waiting_time += 1
            
            if can_move:
                vehicle.x += (dx / distance) * speed_pixels
                vehicle.y += (dy / distance) * speed_pixels
                vehicle.waiting_time = 0
    
    def simulation_loop(self):
        """Loop principal da simulacao"""
        try:
            print("\nSimulacao iniciada!")
            self.start_time = time.time()
            
            # Criar veiculo principal (journey) do canto superior esquerdo ao inferior direito
            print("\n*** Criando veiculo principal A->B (VERDE) ***")
            self.journey_vehicle = self.spawn_vehicle('journey', start_node='0_0', end_node='7_7')
            if self.journey_vehicle:
                print(">>> Veiculo journey criado com sucesso! ID:", self.journey_vehicle.id)
                print(">>> Cor:", self.journey_vehicle.color)
                print(">>> Posicao inicial:", self.journey_vehicle.x, self.journey_vehicle.y)
            else:
                print("!!! ERRO: Veiculo journey NAO foi criado!")
            
            # Criar veiculos iniciais
            for i in range(3):
                self.spawn_vehicle('car')
            self.spawn_vehicle('ambulance')
            
            step = 0
            while self.running:
                if not self.paused:
                    step += 1
                    self.stats['step'] = step
                    
                    # Atualizar contagem de congestionamento ANTES de calcular rotas
                    self.update_edge_traffic_counts()
                    
                    # Decay dos reportes de trafego (informacoes antigas perdem relevancia)
                    if step % 20 == 0:
                        for edge_id in list(self.traffic_reports.keys()):
                            self.traffic_reports[edge_id]['delay'] *= 0.8  # 20% de decay
                            self.traffic_reports[edge_id]['reports_count'] = max(1, int(self.traffic_reports[edge_id]['reports_count'] * 0.8))
                    
                    # Atualizar semaforos a cada 5 steps (mais dinamico)
                    if step % 5 == 0:
                        self.update_traffic_lights()
                    
                    # Atualizar veiculos
                    active = 0
                    total_waiting = 0
                    for vehicle in self.vehicles:
                        if vehicle.moving:
                            self.update_vehicle(vehicle)
                            active += 1
                            total_waiting += vehicle.waiting_time
                    
                    self.stats['active_vehicles'] = active
                    self.stats['total_waiting'] = total_waiting
                    self.stats['congested_edges'] = len([c for c in self.edge_traffic_count.values() if c > 1])
                    
                    # Spawnar novos veiculos aleatoriamente
                    if step % 50 == 0 and len([v for v in self.vehicles if v.moving]) < 10:
                        vehicle_type = 'ambulance' if random.random() < 0.2 else 'car'
                        self.spawn_vehicle(vehicle_type)
                
                time.sleep(0.03)  # ~30 FPS
            
            print("Simulacao concluida!")
            
        except Exception as e:
            print("Erro na simulacao:", str(e))
            import traceback
            traceback.print_exc()
    
    def _calculate_viewport(self):
        """Calcula viewport para centralizar mapa"""
        if not self.nodes:
            return {'offsetX': 0, 'offsetY': 0, 'scale': 1.0}
        
        xs = [n['x'] for n in self.nodes.values()]
        ys = [n['y'] for n in self.nodes.values()]
        
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        width = max_x - min_x
        height = max_y - min_y
        
        canvas_width = WINDOW_WIDTH - SIDEBAR_WIDTH - 40
        canvas_height = WINDOW_HEIGHT - 40
        
        scale_x = canvas_width / width if width > 0 else 1
        scale_y = canvas_height / height if height > 0 else 1
        scale = min(scale_x, scale_y) * 0.85
        
        offset_x = SIDEBAR_WIDTH + 20 + (canvas_width - width * scale) / 2 - min_x * scale
        offset_y = 20 + (canvas_height - height * scale) / 2 - min_y * scale
        
        return {'offsetX': offset_x, 'offsetY': offset_y, 'scale': scale}
    
    def world_to_screen(self, x, y):
        """Converte coordenadas mundo -> tela"""
        screen_x = int(x * self.viewport['scale'] + self.viewport['offsetX'])
        screen_y = int(y * self.viewport['scale'] + self.viewport['offsetY'])
        return (screen_x, screen_y)
    
    def draw_dual_lane_road(self, from_pos, to_pos, road_type):
        """Desenha rua com duas faixas"""
        from_screen = self.world_to_screen(from_pos[0], from_pos[1])
        to_screen = self.world_to_screen(to_pos[0], to_pos[1])
        
        dx = to_screen[0] - from_screen[0]
        dy = to_screen[1] - from_screen[1]
        length = math.sqrt(dx * dx + dy * dy)
        
        if length == 0:
            return
        
        perp_x = -dy / length
        perp_y = dx / length
        
        lane_width = 3
        lane_offset = 2.5
        
        # Cor baseada no tipo de rua
        color = ROAD_TYPES[road_type]['color']
        
        # Duas faixas
        lane1_from = (int(from_screen[0] + perp_x * lane_offset),
                      int(from_screen[1] + perp_y * lane_offset))
        lane1_to = (int(to_screen[0] + perp_x * lane_offset),
                    int(to_screen[1] + perp_y * lane_offset))
        
        lane2_from = (int(from_screen[0] - perp_x * lane_offset),
                      int(from_screen[1] - perp_y * lane_offset))
        lane2_to = (int(to_screen[0] - perp_x * lane_offset),
                    int(to_screen[1] - perp_y * lane_offset))
        
        # Desenhar bordas
        pygame.draw.line(self.screen, COLOR_ROAD_BORDER, lane1_from, lane1_to, lane_width + 2)
        pygame.draw.line(self.screen, COLOR_ROAD_BORDER, lane2_from, lane2_to, lane_width + 2)
        
        # Desenhar faixas
        pygame.draw.line(self.screen, color, lane1_from, lane1_to, lane_width)
        pygame.draw.line(self.screen, color, lane2_from, lane2_to, lane_width)
        
        # Divisor tracejado
        segments = 10
        for i in range(segments):
            if i % 2 == 0:
                seg_from = (int(from_screen[0] + (to_screen[0] - from_screen[0]) * i / segments),
                           int(from_screen[1] + (to_screen[1] - from_screen[1]) * i / segments))
                seg_to = (int(from_screen[0] + (to_screen[0] - from_screen[0]) * (i + 1) / segments),
                         int(from_screen[1] + (to_screen[1] - from_screen[1]) * (i + 1) / segments))
                pygame.draw.line(self.screen, COLOR_LANE_DIVIDER, seg_from, seg_to, 1)
    
    def draw_network(self):
        """Desenha rede de ruas com distancias"""
        # Desenhar arestas
        drawn_pairs = set()
        for edge in self.edges.values():
            from_node = self.nodes[edge['from']]
            to_node = self.nodes[edge['to']]
            
            # Evitar desenhar duas vezes (ida e volta)
            pair = tuple(sorted([edge['from'], edge['to']]))
            if pair not in drawn_pairs:
                self.draw_dual_lane_road(
                    (from_node['x'], from_node['y']),
                    (to_node['x'], to_node['y']),
                    edge['type']
                )
                
                # Desenhar distancia no meio da aresta
                mid_x = (from_node['x'] + to_node['x']) / 2
                mid_y = (from_node['y'] + to_node['y']) / 2
                mid_screen = self.world_to_screen(mid_x, mid_y)
                
                # Mostrar distancia arredondada
                distance_text = str(int(edge['distance']))
                text = self.font_label.render(distance_text, True, COLOR_DISTANCE_LABEL)
                text_rect = text.get_rect(center=mid_screen)
                
                # Fundo semi-transparente para legibilidade
                bg_rect = text_rect.inflate(4, 2)
                s = pygame.Surface((bg_rect.width, bg_rect.height))
                s.set_alpha(180)
                s.fill(COLOR_BG)
                self.screen.blit(s, bg_rect)
                self.screen.blit(text, text_rect)
                
                drawn_pairs.add(pair)
        
        # Desenhar nos
        for node in self.nodes.values():
            pos = self.world_to_screen(node['x'], node['y'])
            pygame.draw.circle(self.screen, COLOR_NODE, pos, 4)
    
    def draw_traffic_lights(self):
        """Desenha semaforos"""
        for tl in self.traffic_lights.values():
            node = self.nodes[tl['node_id']]
            pos = self.world_to_screen(node['x'], node['y'])
            
            if tl['state'] == 'green':
                color = COLOR_LIGHT_GREEN
            elif tl['state'] == 'yellow':
                color = COLOR_LIGHT_YELLOW
            else:
                color = COLOR_LIGHT_RED
            
            pygame.draw.circle(self.screen, color, pos, 8)
            pygame.draw.circle(self.screen, (255, 255, 255), pos, 8, 2)
    
    def draw_vehicles(self):
        """Desenha veiculos com labels"""
        for vehicle in self.vehicles:
            if vehicle.moving:
                pos = self.world_to_screen(vehicle.x, vehicle.y)
                
                # Tamanho baseado no tipo (carro journey MUITO maior para destacar)
                if vehicle.type == 'ambulance':
                    size = 12
                elif vehicle.type == 'journey':
                    size = 16  # MUITO maior para destacar
                else:
                    size = 10
                
                # Desenhar circulo do veiculo
                pygame.draw.circle(self.screen, vehicle.color, pos, size)
                pygame.draw.circle(self.screen, (255, 255, 255), pos, size, 2)
                
                # Adicionar brilho extra para carro journey
                if vehicle.type == 'journey':
                    # Anel externo brilhante
                    pygame.draw.circle(self.screen, (100, 255, 150), pos, size + 3, 1)
                    pygame.draw.circle(self.screen, (50, 220, 100), pos, size + 6, 1)
                
                # Label com ID ou tipo
                if vehicle.type == 'ambulance':
                    label_text = "AMB"
                    label_color = (255, 255, 255)
                elif vehicle.type == 'journey':
                    label_text = "A->B"
                    label_color = (255, 255, 255)
                else:
                    label_text = vehicle.id[-2:]  # Ultimos 2 caracteres do ID
                    label_color = (200, 220, 255)
                
                label = self.font_label.render(label_text, True, label_color)
                label_rect = label.get_rect(center=(pos[0], pos[1] - 22))  # Mais acima para carro maior
                
                # Fundo semi-transparente
                bg_rect = label_rect.inflate(4, 2)
                s = pygame.Surface((bg_rect.width, bg_rect.height))
                s.set_alpha(200)
                s.fill((0, 0, 0))
                self.screen.blit(s, bg_rect)
                self.screen.blit(label, label_rect)
    
    def draw_sidebar(self):
        """Desenha sidebar com estatisticas"""
        pygame.draw.rect(self.screen, COLOR_SIDEBAR, (0, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT))
        
        y_pos = 20
        
        # Titulo
        title = self.font_title.render("Trafego Dinamico", True, COLOR_TEXT)
        self.screen.blit(title, (20, y_pos))
        y_pos += 50
        
        # Status
        if self.running:
            status = "PAUSADO" if self.paused else "RODANDO"
            color = (150, 150, 150) if self.paused else COLOR_LIGHT_GREEN
        else:
            status = "PARADO"
            color = (150, 150, 150)
        
        text = self.font_stats.render(status, True, color)
        self.screen.blit(text, (20, y_pos))
        y_pos += 40
        
        # Estatisticas
        pygame.draw.rect(self.screen, (30, 30, 50), (15, y_pos, SIDEBAR_WIDTH - 30, 240), border_radius=10)
        y_pos += 15
        
        stats_title = self.font_stats.render("Estatisticas", True, COLOR_ACCENT)
        self.screen.blit(stats_title, (25, y_pos))
        y_pos += 30
        
        items = [
            "Step: " + str(self.stats['step']),
            "Total: " + str(self.stats['total_vehicles']),
            "Ativos: " + str(self.stats['active_vehicles']),
            "Completos: " + str(self.stats['completed_trips']),
            "Esperando: " + str(self.stats['total_waiting']),
            "Semaforos: " + str(len(self.traffic_lights)),
            "Congestionado: " + str(self.stats['congested_edges'])
        ]
        
        for item in items:
            text = self.font_label.render(item, True, COLOR_TEXT)
            self.screen.blit(text, (25, y_pos))
            y_pos += 22
        
        y_pos += 20
        
        # Controles
        pygame.draw.rect(self.screen, (30, 30, 50), (15, y_pos, SIDEBAR_WIDTH - 30, 140), border_radius=10)
        y_pos += 15
        
        controls_title = self.font_stats.render("Controles", True, COLOR_ACCENT)
        self.screen.blit(controls_title, (25, y_pos))
        y_pos += 30
        
        controls = [
            "S - Start/Stop",
            "ESPACO - Pause",
            "V - Novo carro",
            "A - Nova ambulancia",
            "Q - Sair"
        ]
        for ctrl in controls:
            text = self.font_label.render(ctrl, True, COLOR_TEXT)
            self.screen.blit(text, (25, y_pos))
            y_pos += 22
        
        y_pos += 20
        
        # Legenda
        pygame.draw.rect(self.screen, (30, 30, 50), (15, y_pos, SIDEBAR_WIDTH - 30, 165), border_radius=10)
        y_pos += 15
        
        legend_title = self.font_stats.render("Legenda", True, COLOR_ACCENT)
        self.screen.blit(legend_title, (25, y_pos))
        y_pos += 30
        
        pygame.draw.circle(self.screen, COLOR_VEHICLE_JOURNEY, (35, y_pos + 7), 8)
        text = self.font_label.render("Carro A->B", True, COLOR_TEXT)
        self.screen.blit(text, (55, y_pos))
        y_pos += 25
        
        pygame.draw.circle(self.screen, COLOR_VEHICLE_NORMAL, (35, y_pos + 7), 8)
        text = self.font_label.render("Carro normal", True, COLOR_TEXT)
        self.screen.blit(text, (55, y_pos))
        y_pos += 25
        
        pygame.draw.circle(self.screen, COLOR_VEHICLE_AMBULANCE, (35, y_pos + 7), 8)
        text = self.font_label.render("Ambulancia", True, COLOR_TEXT)
        self.screen.blit(text, (55, y_pos))
        y_pos += 25
        
        pygame.draw.circle(self.screen, COLOR_LIGHT_GREEN, (35, y_pos + 7), 6)
        text = self.font_label.render("Verde", True, COLOR_TEXT)
        self.screen.blit(text, (55, y_pos))
        y_pos += 25
        
        pygame.draw.circle(self.screen, COLOR_LIGHT_RED, (35, y_pos + 7), 6)
        text = self.font_label.render("Vermelho", True, COLOR_TEXT)
        self.screen.blit(text, (55, y_pos))
    
    def render(self):
        """Renderiza frame"""
        self.screen.fill(COLOR_BG)
        self.draw_network()
        self.draw_traffic_lights()
        self.draw_vehicles()
        self.draw_sidebar()
        pygame.display.flip()
    
    def handle_events(self):
        """Processa eventos"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False
                elif event.key == pygame.K_s:
                    if not self.running:
                        self.start_simulation()
                    else:
                        self.stop_simulation()
                elif event.key == pygame.K_SPACE:
                    if self.running:
                        self.paused = not self.paused
                elif event.key == pygame.K_v:
                    if self.running:
                        self.spawn_vehicle('car')
                elif event.key == pygame.K_a:
                    if self.running:
                        self.spawn_vehicle('ambulance')
        
        return True
    
    def start_simulation(self):
        """Inicia simulacao"""
        if self.running:
            return
        
        print("\n" + "="*60)
        print("Iniciando simulacao dinamica...")
        print("="*60)
        
        self.running = True
        self.simulation_thread = threading.Thread(target=self.simulation_loop, daemon=True)
        self.simulation_thread.start()
    
    def stop_simulation(self):
        """Para simulacao"""
        print("Parando simulacao...")
        self.running = False
        if self.simulation_thread:
            self.simulation_thread.join(timeout=3)
    
    def run(self):
        """Loop principal"""
        running = True
        
        print("\n" + "="*60)
        print("CONTROLES:")
        print("  S - Start/Stop simulacao")
        print("  ESPACO - Pause/Resume")
        print("  V - Spawnar novo carro")
        print("  A - Spawnar ambulancia")
        print("  Q - Sair")
        print("="*60 + "\n")
        
        while running:
            running = self.handle_events()
            self.render()
            self.clock.tick(FPS)
        
        self.stop_simulation()
        pygame.quit()
        print("Visualizacao encerrada!")

def main():
    try:
        sim = DynamicTrafficSimulation()
        sim.run()
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuario")
        pygame.quit()
        sys.exit(0)
    except Exception as e:
        print("Erro:", str(e))
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)

if __name__ == '__main__':
    main()
