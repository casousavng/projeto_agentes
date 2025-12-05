#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulacao Dinamica de Trafego com SPADE + Pygame
- Agentes SPADE reais (VehicleAgent, TrafficLightAgent, CoordinatorAgent, DisruptorAgent)
- Comunicacao XMPP via Prosody
- Visualizacao avancada com Pygame
- Roteamento inteligente A*
- Sistema de disrupção de vias (bloqueios aleatórios)

CONTROLES:
- ESPAÇO: Ativar/Desativar disrupção (3 ruas bloqueadas - ambos os sentidos)
- F11: Alternar tela cheia
- +/-: Ajustar velocidade da simulação
- ESC: Sair

FUNCIONALIDADE DE DISRUPÇÃO:
Ao pressionar ESPAÇO, o DisruptorAgent bloqueia aleatoriamente 3 RUAS da rede (6 arestas total).
Cada rua é bloqueada em AMBOS os sentidos (ida e volta) para simular bloqueio físico real.
Os veículos recalculam automaticamente suas rotas usando A* para evitar as vias bloqueadas.
As vias bloqueadas são exibidas em VERMELHO com um X no meio.
Pressione ESPAÇO novamente para remover os bloqueios.
"""

## TODO: Implementar logica de reroute dinamico para ambulancias
## TODO: Aprimorar interface Pygame (botões, sliders, etc.)
## TODO: Manual overide do estado de ação do agente semaforo via UI
## TODO: Estatísticas detalhadas de desempenho dos agentes
## TODO: ✅ CONCLUÍDO: Agente disruptor gerador de incidentes (ruas intrafegaveis) - impactando roteamento
## TODO: Melhorar visualizacao dos veiculos (setas, rotacao, etc.)
## TODO: Veiculos devem respeitar distancia minima entre si
## TODO: Primeiro veiculo a parar no semafro vermelho deve parar junto deste e nao longe dele


import pygame # type: ignore
import sys
import asyncio
import threading
import time
import random
import math
from typing import Dict, List, Optional

# Import dos agentes SPADE
from agents.spade_traffic_agents import VehicleAgent, TrafficLightAgent, CoordinatorAgent, DisruptorAgent

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
COLOR_VEHICLE_NORMAL = (59, 130, 246)  # Azul
COLOR_VEHICLE_JOURNEY = (147, 51, 234)  # ROXA para veículo A→B
COLOR_VEHICLE_AMBULANCE = (220, 38, 38)  # Vermelho
COLOR_LIGHT_GREEN = (16, 185, 129)
COLOR_LIGHT_YELLOW = (251, 191, 36)
COLOR_LIGHT_RED = (239, 68, 68)
COLOR_TEXT = (255, 255, 255)
COLOR_ACCENT = (102, 126, 234)
COLOR_DISTANCE_LABEL = (150, 150, 200)
COLOR_BLOCKED_ROAD = (200, 50, 50)  # Vermelho para vias bloqueadas

# Tipos de ruas e seus pesos (TODAS COM MESMA LARGURA - 2 faixas bem visíveis)
ROAD_TYPES = {
    'highway': {'speed_limit': 100, 'weight': 5.0, 'color': (100, 100, 100), 'width': 24},
    'main': {'speed_limit': 80, 'weight': 15.0, 'color': (85, 85, 85), 'width': 24},
    'secondary': {'speed_limit': 60, 'weight': 30.0, 'color': (70, 70, 70), 'width': 24},
    'residential': {'speed_limit': 40, 'weight': 50.0, 'color': (60, 60, 60), 'width': 24}
}

# Tamanho da grid (reduzido para 6x6)
GRID_SIZE = 6


class SPADETrafficSimulation:
    """Simulacao de trafego com agentes SPADE + visualizacao Pygame"""
    
    def __init__(self):
        pygame.init()
        
        # Configuração de tela com suporte a fullscreen
        self.is_fullscreen = False
        self.windowed_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        self.screen = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
        pygame.display.set_caption("SPADE Traffic Simulation - Comunicacao XMPP Real")
        
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.SysFont('Arial', 24, bold=True)
        self.font_stats = pygame.font.SysFont('Arial', 16, bold=True)
        self.font_label = pygame.font.SysFont('Arial', 12)
        # Fonte Unicode para símbolos simples
        self.font_symbols = pygame.font.SysFont('Arial Unicode MS,DejaVu Sans', 18)
        
        # Rede
        self.nodes = {}
        self.nodes_simple = {}  # {node_id: (x, y)} para agentes
        self.edges = {}
        self.edges_simple = {}  # {edge_id: {'from', 'to', 'weight'}} para agentes
        self.graph = {}
        self.load_network_with_weights()
        
        # Viewport
        self.viewport = self._calculate_viewport()
        
        # Agentes SPADE
        self.coordinator_agent = None
        self.disruptor_agent = None  # Agente disruptor
        self.vehicle_agents = []  # Lista de VehicleAgents
        self.traffic_light_agents = []  # Lista de TrafficLightAgents
        
        # IDs dos semaforos
        self.traffic_light_nodes = []
        self.create_traffic_light_list()
        
        # Estado da simulacao
        self.running = False
        self.asyncio_loop = None
        self.agent_thread = None
        
        # Controlo de velocidade global da simulacao
        self.speed_multiplier = 2.0  # Multiplicador de velocidade (2.0x a 5.0x) - AUMENTADO
        self.slider_dragging = False
        
        # Controlo de tempo para cálculo de espera
        self.last_update_time = time.time()
        
        # Estatisticas
        self.stats = {
            'step': 0,
            'total_vehicles': 15,  # 15 veículos (1 journey + 10 carros + 4 ambulâncias AMB)
            'journey_speed': 0,  # Velocidade atual do journey vehicle
            'journey_total_cost': 0,  # Custo total da rota (soma dos pesos das arestas)
            'journey_cost_traveled': 0,  # Custo acumulado das arestas percorridas
            'journey_travel_time': 0,  # Tempo de viagem (em segundos)
            'journey_start_time': None,  # Timestamp de início da viagem
            'journey_last_position': None  # Última posição para calcular distância percorrida
        }
        
        # Pontos A e B para journey vehicle
        self.point_a = "0_0"  # Canto superior esquerdo
        grid_max = GRID_SIZE - 1
        self.point_b = str(grid_max) + "_" + str(grid_max)  # Canto inferior direito
        
        print("🚀 Simulacao SPADE inicializada!")
        print("   Nos: " + str(len(self.nodes)))
        print("   Arestas: " + str(len(self.edges)))
        print("   Semaforos: " + str(len(self.traffic_light_nodes)))
    
    def load_network_with_weights(self):
        """Carrega rede 6x6 com pesos diferentes e GRID RETO"""
        base_spacing = 200  # Espaçamento uniforme
        
        # Criar nos SEM VARIAÇÃO (grid perfeitamente reto)
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                node_id = f"{row}_{col}"
                x = col * base_spacing + 50  # Margem - SEM variação
                y = row * base_spacing + 50  # SEM variação
                
                self.nodes[node_id] = {
                    'id': node_id,
                    'x': x,
                    'y': y,
                    'row': row,
                    'col': col
                }
                self.nodes_simple[node_id] = (x, y)
        
        # Criar arestas com pesos variados para cada tipo de rua
        edge_id = 0
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                from_id = f"{row}_{col}"
                
                # Horizontal
                if col < GRID_SIZE - 1:
                    to_id = f"{row}_{col + 1}"
                    from_node = self.nodes[from_id]
                    to_node = self.nodes[to_id]
                    dx = to_node['x'] - from_node['x']
                    dy = to_node['y'] - from_node['y']
                    real_distance = math.sqrt(dx * dx + dy * dy)
                    
                    # Tipo de rua (perimetricas = highway, internas variam)
                    if row == 0 or row == GRID_SIZE-1 or col == 0:
                        road_type = 'highway'
                    elif row == 2 or col == 2:
                        road_type = 'main'
                    elif row == 3:
                        road_type = 'secondary'
                    else:
                        road_type = 'residential'
                    
                    # Peso com variacao
                    base_weight = ROAD_TYPES[road_type]['weight']
                    weight = base_weight * random.uniform(0.8, 1.5)
                    
                    # Esquerda -> Direita
                    self.edges[edge_id] = {
                        'id': edge_id,
                        'from': from_id,
                        'to': to_id,
                        'type': road_type,
                        'weight': weight,
                        'distance': real_distance,
                        'speed_limit': ROAD_TYPES[road_type]['speed_limit']
                    }
                    self.edges_simple[edge_id] = {
                        'from': from_id,
                        'to': to_id,
                        'weight': weight
                    }
                    edge_id += 1
                    
                    # Direita -> Esquerda (dois sentidos)
                    self.edges[edge_id] = {
                        'id': edge_id,
                        'from': to_id,
                        'to': from_id,
                        'type': road_type,
                        'weight': weight,
                        'distance': real_distance,
                        'speed_limit': ROAD_TYPES[road_type]['speed_limit']
                    }
                    self.edges_simple[edge_id] = {
                        'from': to_id,
                        'to': from_id,
                        'weight': weight
                    }
                    edge_id += 1
                
                # Vertical
                if row < GRID_SIZE - 1:
                    to_id = f"{row + 1}_{col}"
                    from_node = self.nodes[from_id]
                    to_node = self.nodes[to_id]
                    dx = to_node['x'] - from_node['x']
                    dy = to_node['y'] - from_node['y']
                    real_distance = math.sqrt(dx * dx + dy * dy)
                    
                    if col == 0 or col == GRID_SIZE-1 or row == 0:
                        road_type = 'highway'
                    elif col == 2 or row == 2:
                        road_type = 'main'
                    elif col == 3:
                        road_type = 'secondary'
                    else:
                        road_type = 'residential'
                    
                    base_weight = ROAD_TYPES[road_type]['weight']
                    weight = base_weight * random.uniform(0.8, 1.5)
                    
                    # Cima -> Baixo
                    self.edges[edge_id] = {
                        'id': edge_id,
                        'from': from_id,
                        'to': to_id,
                        'type': road_type,
                        'weight': weight,
                        'distance': real_distance,
                        'speed_limit': ROAD_TYPES[road_type]['speed_limit']
                    }
                    self.edges_simple[edge_id] = {
                        'from': from_id,
                        'to': to_id,
                        'weight': weight
                    }
                    edge_id += 1
                    
                    # Baixo -> Cima (dois sentidos)
                    self.edges[edge_id] = {
                        'id': edge_id,
                        'from': to_id,
                        'to': from_id,
                        'type': road_type,
                        'weight': weight,
                        'distance': real_distance,
                        'speed_limit': ROAD_TYPES[road_type]['speed_limit']
                    }
                    self.edges_simple[edge_id] = {
                        'from': to_id,
                        'to': from_id,
                        'weight': weight
                    }
                    edge_id += 1
        
        # Construir grafo
        self.build_graph()
    
    def build_graph(self):
        """Constroi grafo de adjacencia para A*"""
        self.graph = {node_id: [] for node_id in self.nodes}
        
        for edge in self.edges.values():
            from_id = edge['from']
            to_id = edge['to']
            self.graph[from_id].append((to_id, edge['id']))
    
    def create_traffic_light_list(self):
        """Define lista de nos com semaforos (10 cruzamentos × 2 direções = 20 semáforos)"""
        # Apenas 10 cruzamentos estratégicos
        self.traffic_light_nodes = [
            # Cantos principais (4)
            "1_1", "1_4", "4_1", "4_4",
            # Internos críticos (6)
            "2_2", "2_3", "3_2", "3_3", "1_3", "3_1"
        ]
        
        # Criar configurações para pares de semáforos (H + V)
        # Com offset visual para não ficarem sobrepostos
        self.traffic_light_configs = []
        for node_id in self.traffic_light_nodes:
            # Horizontal (controla tráfego leste-oeste) - deslocado ACIMA do nó
            self.traffic_light_configs.append({
                'node_id': node_id,
                'orientation': 'horizontal',
                'jid': f"tl_{node_id}_h@localhost",
                'paired_jid': f"tl_{node_id}_v@localhost",
                'offset_x': 0,      # Sem offset horizontal
                'offset_y': -25     # 25px ACIMA do nó
            })
            # Vertical (controla tráfego norte-sul) - deslocado À ESQUERDA do nó
            self.traffic_light_configs.append({
                'node_id': node_id,
                'orientation': 'vertical',
                'jid': f"tl_{node_id}_v@localhost",
                'paired_jid': f"tl_{node_id}_h@localhost",
                'offset_x': -25,    # 25px À ESQUERDA do nó
                'offset_y': 0       # Sem offset vertical
            })
    
    def _calculate_viewport(self):
        """Calcula area visivel do mapa"""
        if not self.nodes:
            return {'min_x': 0, 'max_x': 1400, 'min_y': 0, 'max_y': 900, 'scale': 1.0}
        
        all_x = [n['x'] for n in self.nodes.values()]
        all_y = [n['y'] for n in self.nodes.values()]
        
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        
        # Adicionar margem
        margin = 50
        min_x -= margin
        max_x += margin
        min_y -= margin
        max_y += margin
        
        # Calcular escala usando dimensões atuais da tela
        screen_width, screen_height = self.screen.get_size()
        map_width = max_x - min_x
        map_height = max_y - min_y
        available_width = screen_width - SIDEBAR_WIDTH - 40
        available_height = screen_height - 40
        
        scale = min(available_width / map_width, available_height / map_height)
        
        return {
            'min_x': min_x,
            'max_x': max_x,
            'min_y': min_y,
            'max_y': max_y,
            'scale': scale
        }
    
    def world_to_screen(self, x, y):
        """Converte coordenadas do mundo para tela"""
        screen_x = 20 + (x - self.viewport['min_x']) * self.viewport['scale']
        screen_y = 20 + (y - self.viewport['min_y']) * self.viewport['scale']
        return int(screen_x), int(screen_y)
    
    def toggle_fullscreen(self):
        """Alterna entre modo tela cheia e janela"""
        self.is_fullscreen = not self.is_fullscreen
        
        if self.is_fullscreen:
            # Entrar em tela cheia
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            print("🖥️  Modo TELA CHEIA ativado (F11 para sair)")
        else:
            # Voltar para janela
            self.screen = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
            print("🪟  Modo JANELA ativado (F11 para tela cheia)")
        
        # Recalcular viewport para a nova resolução
        self.viewport = self._calculate_viewport()
    
    async def start_agents(self):
        """Inicia todos os agentes SPADE"""
        print("\n🚀 Iniciando agentes SPADE...")
        
        # 1. Iniciar Coordenador
        print("📡 Iniciando CoordinatorAgent...")
        self.coordinator_agent = CoordinatorAgent(
            "coordinator@localhost",
            "coordinator",  # Senha = nome do agente
            self.nodes_simple,
            self.edges_simple,
            self.graph
        )
        await self.coordinator_agent.start(auto_register=False)
        print("   ✅ CoordinatorAgent conectado ao Prosody")
        
        # 1.5. Iniciar Disruptor
        print("🚧 Iniciando DisruptorAgent...")
        self.disruptor_agent = DisruptorAgent(
            "disruptor@localhost",
            "disruptor",
            self.edges_simple
        )
        self.disruptor_agent.coordinator_jid = "coordinator@localhost"
        await self.disruptor_agent.start(auto_register=False)  # Requer registro prévio
        print("   ✅ DisruptorAgent conectado ao Prosody")
        
        await asyncio.sleep(0.5)
        
        # 2. Iniciar Semaforos (20 agentes: 10 cruzamentos × 2 direções)
        print(f"🚦 Iniciando {len(self.traffic_light_configs)} TrafficLightAgents (pares H+V)...")
        for config in self.traffic_light_configs:
            # Temporizadores RAPIDOS
            green_time = random.randint(5, 12)
            red_time = random.randint(5, 10)
            yellow_time = random.randint(1, 2)
            
            # Extrair username do JID (ex: "tl_0_0_h@localhost" -> "tl_0_0_h")
            username = config['jid'].split('@')[0]
            password = username  # Senha = nome do agente
            
            tl_agent = TrafficLightAgent(
                config['jid'],
                password,
                config['node_id'],
                config['orientation'],
                green_time,
                red_time,
                yellow_time,
                config['paired_jid'],
                config['offset_x'],  # Offset visual em X
                config['offset_y']   # Offset visual em Y
            )
            await tl_agent.start(auto_register=False)
            self.traffic_light_agents.append(tl_agent)
            await asyncio.sleep(0.02)
        
        print(f"   ✅ {len(self.traffic_light_agents)} TrafficLightAgents conectados (pares coordenados)")

        
        # Aguardar semaforos receberem posicoes
        await asyncio.sleep(0.5)
        
        # 3. Iniciar Veiculos (15 agentes: 1 journey + 10 carros + 4 AMB)
        print("🚗 Iniciando 15 VehicleAgents (11 carros + 4 AMB)...")
        
        # Veiculo 0: Journey vehicle ÚNICO (A -> B)
        v0 = VehicleAgent(
            "vehicle_0@localhost",
            "vehicle_0",
            "v0",
            self.point_a,
            self.point_b,
            'journey'
        )
        await v0.start(auto_register=False)
        self.vehicle_agents.append(v0)
        await asyncio.sleep(0.1)
        
        # Veiculos 1-10: 10 carros normais
        for i in range(1, 11):
            nodes_list = list(self.nodes.keys())
            start = random.choice(nodes_list)
            end = random.choice([n for n in nodes_list if n != start])
            
            username = f"vehicle_{i}"
            password = username
            
            v_agent = VehicleAgent(
                f"{username}@localhost",
                password,
                f"v{i}",
                start,
                end,
                'car'
            )
            await v_agent.start(auto_register=False)
            self.vehicle_agents.append(v_agent)
            await asyncio.sleep(0.1)
        
        print(f"   ✅ {len(self.vehicle_agents)} VehicleAgents conectados (carros)")
        
        # 4. Iniciar Ambulâncias (4 agentes AMB independentes)
        print("🚑 Iniciando 4 AmbulanceAgents (AMB)...")
        for i in range(4):
            nodes_list = list(self.nodes.keys())
            start = random.choice(nodes_list)
            end = random.choice([n for n in nodes_list if n != start])
            
            username = f"amb_{i}"
            password = username
            
            amb_agent = VehicleAgent(
                f"{username}@localhost",
                password,
                f"AMB{i}",
                start,
                end,
                'ambulance'
            )
            await amb_agent.start(auto_register=False)
            self.vehicle_agents.append(amb_agent)
            await asyncio.sleep(0.1)
        
        print(f"   ✅ Total: {len(self.vehicle_agents)} agentes de movimento")
        print(f"   🎯 1 journey vehicle (v0: A->B)")
        print(f"   🚗 10 carros normais (v1-v10)")
        print(f"   🚑 4 ambulâncias AMB (AMB0-AMB3)")
        
        print("")
        print("✅ Todos os agentes SPADE iniciados!")
        print("📡 Comunicacao XMPP via Prosody ativa")
        print(f"   🎯 1 journey vehicle (v0: A->B)")
        print(f"   � 4 ambulâncias AMB (AMB0-AMB3)")
        print(f"   🚗 10 carros normais (v1-v10)")
        print("\n✅ Todos os agentes SPADE iniciados!")
        print("📡 Comunicacao XMPP via Prosody ativa\n")
    
    async def stop_agents(self):
        """Para todos os agentes SPADE"""
        print("\n🛑 Parando agentes SPADE...")
        
        for vehicle in self.vehicle_agents:
            await vehicle.stop()
        
        for tl in self.traffic_light_agents:
            await tl.stop()
        
        if self.coordinator_agent:
            await self.coordinator_agent.stop()
        
        print("   ✅ Todos os agentes SPADE parados")
    
    def agent_loop(self):
        """Loop asyncio para agentes SPADE em thread separada"""
        self.asyncio_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.asyncio_loop)
        
        # Iniciar agentes
        self.asyncio_loop.run_until_complete(self.start_agents())
        
        # Manter loop rodando
        try:
            self.asyncio_loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.asyncio_loop.run_until_complete(self.stop_agents())
            self.asyncio_loop.close()
    
    def start(self):
        """Inicia a simulacao"""
        if self.running:
            return
        
        print("\n🎮 Iniciando simulacao...")
        self.running = True
        
        # Iniciar thread dos agentes SPADE
        self.agent_thread = threading.Thread(target=self.agent_loop, daemon=True)
        self.agent_thread.start()
        
        # Aguardar agentes iniciarem
        time.sleep(5)
        
        print("✅ Simulacao iniciada!")
    
    def stop(self):
        """Para a simulacao"""
        if not self.running:
            return
        
        print("\n🛑 Parando simulacao...")
        self.running = False
        
        # Parar loop asyncio
        if self.asyncio_loop:
            self.asyncio_loop.call_soon_threadsafe(self.asyncio_loop.stop)
        
        print("✅ Simulacao parada!")
    
    def update(self):
        """Atualiza estado da simulacao"""
        if not self.running:
            return
        
        self.stats['step'] += 1
        
        # Atualizar estatísticas do journey vehicle (vehicle_0)
        if len(self.vehicle_agents) > 0:
            journey_vehicle = self.vehicle_agents[0]
            self.stats['journey_speed'] = journey_vehicle.speed
            
            # Debug: mostrar status do veículo a cada 60 frames
            if self.stats['step'] % 60 == 0:
                print(f"📊 Journey Status: moving={journey_vehicle.moving}, route_index={journey_vehicle.route_index}, route_len={len(journey_vehicle.route) if journey_vehicle.route else 0}")
            
            # Iniciar cronômetro quando o veículo começa a se mover
            if self.stats['journey_start_time'] is None and journey_vehicle.moving:
                self.stats['journey_start_time'] = time.time()
                self.stats['journey_last_position'] = (journey_vehicle.x, journey_vehicle.y)
                print(f"⏱️  Cronômetro iniciado para Journey vehicle!")
            
            # Calcular tempo de viagem
            if self.stats['journey_start_time'] is not None and journey_vehicle.arrival_time is None:
                self.stats['journey_travel_time'] = time.time() - self.stats['journey_start_time']
            
            self.last_update_time = time.time()
            
            # Atualizar custo da rota do journey vehicle (peso das arestas)
            if hasattr(journey_vehicle, 'route_total_cost'):
                self.stats['journey_total_cost'] = journey_vehicle.route_total_cost
            if hasattr(journey_vehicle, 'route_cost_traveled'):
                self.stats['journey_cost_traveled'] = journey_vehicle.route_cost_traveled
    
    def draw_vehicle_icon(self, vehicle_type, size=16):
        """Desenha ícone de veículo como superfície"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        if vehicle_type == 'ambulance':
            # Ambulância: retângulo vermelho com cruz branca
            pygame.draw.rect(surface, (220, 38, 38), (0, 0, size, size))
            pygame.draw.rect(surface, (255, 255, 255), (size//2-2, 3, 4, size-6))  # Vertical
            pygame.draw.rect(surface, (255, 255, 255), (3, size//2-2, size-6, 4))  # Horizontal
            pygame.draw.rect(surface, (255, 255, 255), (0, 0, size, size), 2)  # Borda
        elif vehicle_type == 'journey':
            # Journey: retângulo roxo com "A→B"
            pygame.draw.rect(surface, (147, 51, 234), (0, 0, size, size))
            text = self.font_label.render("A", True, (255, 255, 255))
            surface.blit(text, (2, size//2 - 6))
            pygame.draw.rect(surface, (255, 255, 255), (0, 0, size, size), 2)
        else:
            # Carro normal: retângulo azul
            pygame.draw.rect(surface, (59, 130, 246), (0, 0, size, size))
            pygame.draw.rect(surface, (255, 255, 255), (0, 0, size, size), 2)
        
        # Seta indicando frente
        arrow_points = [
            (size - 2, size // 2),
            (size - 5, size // 2 - 2),
            (size - 5, size // 2 + 2)
        ]
        pygame.draw.polygon(surface, (255, 255, 255), arrow_points)
        
        return surface
    
    def draw(self):
        """Desenha a simulacao com ruas UNIFORMES de 2 faixas bem visíveis"""
        self.screen.fill(COLOR_BG)
        
        # Desenhar arestas UNIFORMES com 2 faixas bem definidas
        drawn_edges = set()  # Para evitar desenhar duas vezes a mesma aresta visual
        
        for edge in self.edges.values():
            from_node = self.nodes[edge['from']]
            to_node = self.nodes[edge['to']]
            edge_key = tuple(sorted([edge['from'], edge['to']]))
            
            # Desenhar apenas uma vez por par de nos
            if edge_key in drawn_edges:
                continue
            drawn_edges.add(edge_key)
            
            from_pos = self.world_to_screen(from_node['x'], from_node['y'])
            to_pos = self.world_to_screen(to_node['x'], to_node['y'])
            
            # Verificar se a via está bloqueada
            edge_id = edge['id']
            is_blocked = False
            if self.disruptor_agent and self.disruptor_agent.disruption_active:
                is_blocked = edge_id in self.disruptor_agent.blocked_edges
            
            # LARGURA UNIFORME para todas as ruas (16px = 2 faixas de 8px cada)
            road_width = 16
            
            if is_blocked:
                # Via bloqueada: desenhar em vermelho com X
                color = COLOR_BLOCKED_ROAD
                
                # 1. Desenhar borda preta externa (calçada)
                pygame.draw.line(self.screen, (30, 30, 30), from_pos, to_pos, road_width + 4)
                
                # 2. Desenhar rua bloqueada (vermelho)
                pygame.draw.line(self.screen, color, from_pos, to_pos, road_width)
                
                # 3. Desenhar X no meio da via
                mid_x = (from_pos[0] + to_pos[0]) // 2
                mid_y = (from_pos[1] + to_pos[1]) // 2
                x_size = 15
                pygame.draw.line(self.screen, (255, 255, 255), 
                               (mid_x - x_size, mid_y - x_size), 
                               (mid_x + x_size, mid_y + x_size), 3)
                pygame.draw.line(self.screen, (255, 255, 255), 
                               (mid_x - x_size, mid_y + x_size), 
                               (mid_x + x_size, mid_y - x_size), 3)
            else:
                # Via normal
                color = ROAD_TYPES[edge['type']]['color']
                
                # 1. Desenhar borda preta externa (calçada)
                pygame.draw.line(self.screen, (30, 30, 30), from_pos, to_pos, road_width + 4)
                
                # 2. Desenhar rua (asfalto cinza)
                pygame.draw.line(self.screen, color, from_pos, to_pos, road_width)
                
                # 3. Desenhar linha divisória central AMARELA (faixa dupla bem visível)
                pygame.draw.line(self.screen, COLOR_LANE_DIVIDER, from_pos, to_pos, 2)
            
            # 4. Desenhar linhas brancas nas bordas (marcação de faixa) - apenas se não bloqueada
            if not is_blocked:
                # Calcular vetor perpendicular para desenhar as bordas
                dx = to_pos[0] - from_pos[0]
                dy = to_pos[1] - from_pos[1]
                length = math.sqrt(dx*dx + dy*dy)
                if length > 0:
                    # Vetor perpendicular normalizado
                    perp_x = -dy / length
                    perp_y = dx / length
                    
                    # Deslocamento para as bordas (10px do centro para ruas de 24px)
                    offset = 10
                    
                    # Borda superior (linha branca)
                    border1_start = (from_pos[0] + perp_x * offset, from_pos[1] + perp_y * offset)
                    border1_end = (to_pos[0] + perp_x * offset, to_pos[1] + perp_y * offset)
                    pygame.draw.line(self.screen, (200, 200, 200), border1_start, border1_end, 1)
                    
                    # Borda inferior (linha branca)
                    border2_start = (from_pos[0] - perp_x * offset, from_pos[1] - perp_y * offset)
                    border2_end = (to_pos[0] - perp_x * offset, to_pos[1] - perp_y * offset)
                    pygame.draw.line(self.screen, (200, 200, 200), border2_start, border2_end, 1)
            
            # Mostrar peso da rua no meio (ou "BLOCKED" se bloqueada)
            mid_x = (from_pos[0] + to_pos[0]) // 2
            mid_y = (from_pos[1] + to_pos[1]) // 2
            
            if is_blocked:
                weight_text = "BLOCKED"
                text_color = (255, 255, 255)
            else:
                weight_text = f"{int(edge['weight'])}"
                text_color = COLOR_DISTANCE_LABEL
            
            weight_surface = self.font_label.render(weight_text, True, text_color)
            
            # Fundo semi-transparente para legibilidade
            text_rect = weight_surface.get_rect(center=(mid_x, mid_y))
            bg_rect = text_rect.inflate(4, 2)
            pygame.draw.rect(self.screen, (26, 26, 46, 200), bg_rect)
            self.screen.blit(weight_surface, text_rect)
        
        # Desenhar nos
        for node in self.nodes.values():
            pos = self.world_to_screen(node['x'], node['y'])
            pygame.draw.circle(self.screen, COLOR_NODE, pos, 5)
            pygame.draw.circle(self.screen, COLOR_TEXT, pos, 5, 1)
        
        # Desenhar marcadores A (verde GRANDE) e B (vermelho GRANDE)
        if self.point_a in self.nodes:
            a_node = self.nodes[self.point_a]
            a_pos = self.world_to_screen(a_node['x'], a_node['y'])
            pygame.draw.circle(self.screen, (0, 255, 0), a_pos, 20, 4)
            label_a = self.font_stats.render("A", True, (0, 255, 0))
            self.screen.blit(label_a, (a_pos[0] - 7, a_pos[1] - 10))
        
        if self.point_b in self.nodes:
            b_node = self.nodes[self.point_b]
            b_pos = self.world_to_screen(b_node['x'], b_node['y'])
            pygame.draw.circle(self.screen, (255, 0, 0), b_pos, 20, 4)
            label_b = self.font_stats.render("B", True, (255, 0, 0))
            self.screen.blit(label_b, (b_pos[0] - 7, b_pos[1] - 10))
        
        # Desenhar semaforos (usando posição visual com offset)
        for tl_agent in self.traffic_light_agents:
            if tl_agent.visual_x > 0 and tl_agent.visual_y > 0:
                # Usar posição visual (com offset)
                pos = self.world_to_screen(tl_agent.visual_x, tl_agent.visual_y)
                
                # Cor baseada no estado
                if tl_agent.state == 'green':
                    color = COLOR_LIGHT_GREEN
                elif tl_agent.state == 'yellow':
                    color = COLOR_LIGHT_YELLOW
                else:
                    color = COLOR_LIGHT_RED
                
                # Desenhar semáforo como RETÂNGULO para indicar orientação
                if tl_agent.orientation == 'horizontal':
                    # Horizontal: retângulo largo (16x10)
                    rect = pygame.Rect(pos[0] - 8, pos[1] - 5, 16, 10)
                    pygame.draw.rect(self.screen, color, rect, border_radius=3)
                    pygame.draw.rect(self.screen, COLOR_TEXT, rect, 2, border_radius=3)
                    # Label "H" dentro
                    label_h = self.font_label.render("H", True, (0, 0, 0))
                    self.screen.blit(label_h, (pos[0] - 4, pos[1] - 5))
                else:
                    # Vertical: retângulo alto (10x16)
                    rect = pygame.Rect(pos[0] - 5, pos[1] - 8, 10, 16)
                    pygame.draw.rect(self.screen, color, rect, border_radius=3)
                    pygame.draw.rect(self.screen, COLOR_TEXT, rect, 2, border_radius=3)
                    # Label "V" dentro
                    label_v = self.font_label.render("V", True, (0, 0, 0))
                    self.screen.blit(label_v, (pos[0] - 3, pos[1] - 5))
        
        # Desenhar veiculos como QUADRADOS ORIENTADOS
        for v_agent in self.vehicle_agents:
            if v_agent.x > 0 and v_agent.y > 0:
                pos = self.world_to_screen(v_agent.x, v_agent.y)
                
                # Calcular direção do veículo (baseado na rota)
                angle = 0
                if v_agent.route and len(v_agent.route) > v_agent.route_index + 1:
                    # Próximo nó na rota
                    next_node_id = v_agent.route[v_agent.route_index + 1]
                    if next_node_id in self.nodes:
                        next_node = self.nodes[next_node_id]
                        dx = next_node['x'] - v_agent.x
                        dy = next_node['y'] - v_agent.y
                        angle = math.degrees(math.atan2(dy, dx))
                
                # Desenhar ícone do veículo
                vehicle_icon = self.draw_vehicle_icon(v_agent.vehicle_type, size=16)
                
                # Rotacionar o ícone baseado na direção
                rotated_surface = pygame.transform.rotate(vehicle_icon, -angle)
                rotated_rect = rotated_surface.get_rect(center=pos)
                
                # Desenhar veículo rotacionado
                self.screen.blit(rotated_surface, rotated_rect.topleft)
                
                # Label especial para journey A→B
                if v_agent.vehicle_type == 'journey':
                    label_ab = self.font_stats.render("A→B", True, (255, 255, 255))
                    label_ab_bg = pygame.Surface((label_ab.get_width() + 6, label_ab.get_height() + 4))
                    label_ab_bg.fill((147, 51, 234))
                    label_ab_bg.set_alpha(200)
                    label_ab_bg.blit(label_ab, (3, 2))
                    self.screen.blit(label_ab_bg, (pos[0] - label_ab.get_width()//2 - 3, pos[1] - 28))
                
                # Label com ID
                label_id = self.font_label.render(v_agent.vehicle_id, True, COLOR_TEXT)
                self.screen.blit(label_id, (pos[0] + 12, pos[1] - 6))
        
        # Desenhar sidebar
        self.draw_sidebar()
        
        pygame.display.flip()
    
    def draw_speed_slider(self, x, y):
        """Desenha slider de controle de velocidade"""
        slider_width = 200
        slider_height = 10
        
        # Barra de fundo
        pygame.draw.rect(self.screen, (60, 60, 60), (x, y, slider_width, slider_height), border_radius=5)
        
        # Calcular posição do handle (2.0x a 5.0x) - AUMENTADO
        min_speed = 2.0
        max_speed = 5.0
        normalized = (self.speed_multiplier - min_speed) / (max_speed - min_speed)
        handle_x = x + int(normalized * slider_width)
        
        # Barra preenchida
        pygame.draw.rect(self.screen, COLOR_ACCENT, (x, y, handle_x - x, slider_height), border_radius=5)
        
        # Handle (circulo arrastável)
        pygame.draw.circle(self.screen, COLOR_ACCENT, (handle_x, y + slider_height // 2), 12)
        pygame.draw.circle(self.screen, COLOR_TEXT, (handle_x, y + slider_height // 2), 12, 2)
        
        # Armazenar posição do slider para detecção de clique
        self.slider_rect = pygame.Rect(x - 10, y - 10, slider_width + 20, 30)
        
        # Label de velocidade
        speed_text = self.font_label.render(f"{self.speed_multiplier:.1f}x", True, COLOR_TEXT)
        self.screen.blit(speed_text, (x + slider_width + 15, y - 5))
    
    def draw_speed_buttons(self, x, y):
        """Desenha botões +/- para controle de velocidade"""
        button_size = 30
        
        # Botão -
        minus_rect = pygame.Rect(x, y, button_size, button_size)
        pygame.draw.rect(self.screen, (60, 60, 80), minus_rect, border_radius=5)
        pygame.draw.rect(self.screen, COLOR_ACCENT, minus_rect, 2, border_radius=5)
        minus_text = self.font_title.render("-", True, COLOR_TEXT)
        self.screen.blit(minus_text, (x + 8, y + 2))
        self.minus_button_rect = minus_rect
        
        # Botão +
        plus_rect = pygame.Rect(x + button_size + 10, y, button_size, button_size)
        pygame.draw.rect(self.screen, (60, 60, 80), plus_rect, border_radius=5)
        pygame.draw.rect(self.screen, COLOR_ACCENT, plus_rect, 2, border_radius=5)
        plus_text = self.font_title.render("+", True, COLOR_TEXT)
        self.screen.blit(plus_text, (x + button_size + 17, y + 2))
        self.plus_button_rect = plus_rect
        
        # Label
        label = self.font_label.render("Ajustar velocidade", True, (180, 180, 180))
        self.screen.blit(label, (x + button_size * 2 + 20, y + 7))
    
    def update_speed_multiplier(self, delta):
        """Atualiza multiplicador de velocidade"""
        self.speed_multiplier = max(2.0, min(5.0, self.speed_multiplier + delta))  # Range: 2.0x a 5.0x
        # Aplicar aos agentes
        for v_agent in self.vehicle_agents:
            v_agent.update_speed_multiplier(self.speed_multiplier)
    
    def draw_sidebar(self):
        """Desenha barra lateral com estatisticas"""
        sidebar_x = WINDOW_WIDTH - SIDEBAR_WIDTH
        
        # Fundo
        pygame.draw.rect(self.screen, COLOR_SIDEBAR, (sidebar_x, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT))
        pygame.draw.line(self.screen, COLOR_ACCENT, (sidebar_x, 0), (sidebar_x, WINDOW_HEIGHT), 2)
        
        y_offset = 20
        
        # Titulo
        title = self.font_title.render("SPADE Traffic", True, COLOR_ACCENT)
        self.screen.blit(title, (sidebar_x + 20, y_offset))
        y_offset += 60
        
        # Estatisticas
        stats_title = self.font_stats.render("Estatisticas", True, COLOR_TEXT)
        self.screen.blit(stats_title, (sidebar_x + 20, y_offset))
        y_offset += 30
        
        stats_lines = [
            f"Step: {self.stats['step']}",
            f"",
            f"Veiculo Journey A->B:",
            f"  Velocidade: {self.stats['journey_speed']:.1f} px/s",
        ]
        
        # Adicionar informações de tempo
        travel_time = self.stats['journey_travel_time']
        
        # Formatar tempo de viagem (mm:ss)
        travel_mins = int(travel_time // 60)
        travel_secs = int(travel_time % 60)
        
        stats_lines.extend([
            f"  Tempo Total: {travel_mins:02d}:{travel_secs:02d}",
            f"",
            f"Agentes SPADE:",
            f"  Coordenador: 1",
            f"  Disruptor: 1",
            f"  Veiculos: {len(self.vehicle_agents)}",
            f"  Semaforos: {len(self.traffic_light_agents)}",
            f"  TOTAL: {2 + len(self.vehicle_agents) + len(self.traffic_light_agents)}"
        ])
        
        for line in stats_lines:
            text = self.font_label.render(line, True, COLOR_TEXT)
            self.screen.blit(text, (sidebar_x + 20, y_offset))
            y_offset += 20
        
        y_offset += 20
        
        # Controle de Velocidade
        speed_title = self.font_stats.render("Velocidade Global", True, COLOR_TEXT)
        self.screen.blit(speed_title, (sidebar_x + 20, y_offset))
        y_offset += 30
        
        # Desenhar slider
        self.draw_speed_slider(sidebar_x + 20, y_offset)
        y_offset += 50
        
        # Botoes +/-
        self.draw_speed_buttons(sidebar_x + 20, y_offset)
        y_offset += 50
        
        # Controles
        controls_title = self.font_stats.render("Controles", True, COLOR_TEXT)
        self.screen.blit(controls_title, (sidebar_x + 20, y_offset))
        y_offset += 30
        
        controls = [
            "ESPACO: Disrupção (bloqueios)",
            "F11: Tela cheia",
            "ESC: Sair",
            "+/-: Velocidade",
        ]
        
        for ctrl in controls:
            text = self.font_label.render(ctrl, True, COLOR_TEXT)
            self.screen.blit(text, (sidebar_x + 20, y_offset))
            y_offset += 20
        
        y_offset += 20
        
        # Estado de disrupção
        if self.disruptor_agent:
            disruption_title = self.font_stats.render("Estado de Disrupção", True, COLOR_TEXT)
            self.screen.blit(disruption_title, (sidebar_x + 20, y_offset))
            y_offset += 30
            
            if self.disruptor_agent.disruption_active:
                status_text = "ATIVO"
                status_color = (255, 100, 100)
                num_roads = len(self.disruptor_agent.blocked_edges) // 2  # Dividir por 2 pois cada rua tem 2 arestas
                blocked_text = f"Ruas bloqueadas: {num_roads} ({len(self.disruptor_agent.blocked_edges)} arestas)"
            else:
                status_text = "INATIVO"
                status_color = (100, 255, 100)
                blocked_text = "Todas as vias livres"
            
            status_surface = self.font_label.render(f"Status: {status_text}", True, status_color)
            self.screen.blit(status_surface, (sidebar_x + 20, y_offset))
            y_offset += 20
            
            blocked_surface = self.font_label.render(blocked_text, True, COLOR_TEXT)
            self.screen.blit(blocked_surface, (sidebar_x + 20, y_offset))
            y_offset += 30
        
        # Legenda
        legend_title = self.font_stats.render("Legenda", True, COLOR_TEXT)
        self.screen.blit(legend_title, (sidebar_x + 20, y_offset))
        y_offset += 30
        
        # Veiculos com ícones customizados
        icon_journey = self.draw_vehicle_icon('journey', size=16)
        self.screen.blit(icon_journey, (sidebar_x + 25, y_offset - 4))
        text = self.font_label.render("Veiculo Journey (A->B)", True, COLOR_TEXT)
        self.screen.blit(text, (sidebar_x + 50, y_offset))
        y_offset += 25
        
        icon_amb = self.draw_vehicle_icon('ambulance', size=16)
        self.screen.blit(icon_amb, (sidebar_x + 25, y_offset - 4))
        text = self.font_label.render("Ambulancia", True, COLOR_TEXT)
        self.screen.blit(text, (sidebar_x + 50, y_offset))
        y_offset += 25
        
        icon_car = self.draw_vehicle_icon('normal', size=16)
        self.screen.blit(icon_car, (sidebar_x + 25, y_offset - 4))
        text = self.font_label.render("Carro Normal", True, COLOR_TEXT)
        self.screen.blit(text, (sidebar_x + 50, y_offset))
        y_offset += 25
        
        # Semaforos
        pygame.draw.circle(self.screen, COLOR_LIGHT_GREEN, (sidebar_x + 30, y_offset + 5), 5)
        text = self.font_label.render("Semaforo Verde", True, COLOR_TEXT)
        self.screen.blit(text, (sidebar_x + 45, y_offset))
        y_offset += 20
        
        pygame.draw.circle(self.screen, COLOR_LIGHT_YELLOW, (sidebar_x + 30, y_offset + 5), 5)
        text = self.font_label.render("Semaforo Amarelo", True, COLOR_TEXT)
        self.screen.blit(text, (sidebar_x + 45, y_offset))
        y_offset += 20
        
        pygame.draw.circle(self.screen, COLOR_LIGHT_RED, (sidebar_x + 30, y_offset + 5), 5)
        text = self.font_label.render("Semaforo Vermelho", True, COLOR_TEXT)
        self.screen.blit(text, (sidebar_x + 45, y_offset))
    
    def run(self):
        """Loop principal"""
        print("\n" + "="*50)
        print("🚦 SPADE Traffic Simulation")
        print("   Agentes SPADE + Prosody XMPP + Pygame")
        print("="*50)
        print("\nIniciando simulacao...")
        
        self.start()
        
        running_main_loop = True
        while running_main_loop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running_main_loop = False
                elif event.type == pygame.VIDEORESIZE:
                    # Atualizar viewport quando a janela é redimensionada
                    if not self.is_fullscreen:
                        self.windowed_size = (event.w, event.h)
                        self.viewport = self._calculate_viewport()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running_main_loop = False
                    elif event.key == pygame.K_F11:
                        # F11 para alternar fullscreen
                        self.toggle_fullscreen()
                    elif event.key == pygame.K_SPACE:
                        # Toggle disrupção (ativar/desativar bloqueios)
                        if self.disruptor_agent:
                            self.disruptor_agent.toggle_disruption()
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        self.update_speed_multiplier(0.2)
                    elif event.key == pygame.K_MINUS:
                        self.update_speed_multiplier(-0.2)
                
                # Eventos do mouse para slider
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Botão esquerdo
                        mouse_pos = pygame.mouse.get_pos()
                        # Verificar clique no slider
                        if hasattr(self, 'slider_rect') and self.slider_rect.collidepoint(mouse_pos):
                            self.slider_dragging = True
                        # Verificar clique nos botões +/-
                        if hasattr(self, 'minus_button_rect') and self.minus_button_rect.collidepoint(mouse_pos):
                            self.update_speed_multiplier(-0.2)
                        if hasattr(self, 'plus_button_rect') and self.plus_button_rect.collidepoint(mouse_pos):
                            self.update_speed_multiplier(0.2)
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.slider_dragging = False
                
                elif event.type == pygame.MOUSEMOTION:
                    if self.slider_dragging and hasattr(self, 'slider_rect'):
                        mouse_x = pygame.mouse.get_pos()[0]
                        slider_x = WINDOW_WIDTH - SIDEBAR_WIDTH + 20
                        slider_width = 200
                        # Calcular nova velocidade baseada na posição do mouse (2.0x a 5.0x)
                        normalized = max(0, min(1, (mouse_x - slider_x) / slider_width))
                        min_speed = 2.0
                        max_speed = 5.0
                        new_speed = min_speed + normalized * (max_speed - min_speed)
                        self.speed_multiplier = new_speed
                        # Aplicar aos agentes
                        for v_agent in self.vehicle_agents:
                            v_agent.update_speed_multiplier(self.speed_multiplier)
            
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        # Cleanup
        self.stop()
        pygame.quit()
        sys.exit()


def main():
    """Funcao principal"""
    sim = SPADETrafficSimulation()
    sim.run()


if __name__ == "__main__":
    main()
