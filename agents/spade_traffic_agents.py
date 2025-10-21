#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agentes SPADE para Simulacao de Trafego
- VehicleAgent: Veiculo com roteamento A*
- TrafficLightAgent: Semaforo com estados dinamicos
- CoordinatorAgent: Coordenador central
"""

import asyncio
import json
import math
import heapq
import random
import time
from typing import Dict, List, Tuple, Optional
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour, PeriodicBehaviour
from spade.message import Message
from spade.template import Template


class VehicleAgent(Agent):
    """Agente Veiculo com roteamento inteligente"""
    
    def __init__(self, jid, password, vehicle_id, start_node, end_node, vehicle_type='car'):
        super().__init__(jid, password)
        self.vehicle_id = vehicle_id
        self.vehicle_type = vehicle_type  # 'car', 'ambulance', 'journey'
        self.start_node = start_node
        self.end_node = end_node
        
        # Estado visual (para Pygame)
        self.current_node = start_node
        self.target_node = None
        self.x = 0.0
        self.y = 0.0
        self.route = []
        self.route_index = 0
        
        # Parametros (VELOCIDADES AUMENTADAS 5x para journey, 4x para outros)
        if vehicle_type == 'journey':
            self.base_speed = 300  # Journey A->B é o mais rápido
        elif vehicle_type == 'ambulance':
            self.base_speed = 280
        else:  # car
            self.base_speed = 240
        
        self.speed = self.base_speed
        self.speed_multiplier = 1.0
        self.waiting_time = 0
        self.total_travel_time = 0
        self.moving = True
        self.arrival_time = None
        
        # Rastreamento de custo da rota (peso das arestas)
        self.route_total_cost = 0  # Custo total da rota planejada
        self.route_cost_traveled = 0  # Custo acumulado das arestas percorridas
        self.current_edge_cost = 0  # Custo da aresta atual
        self.edge_start_node = None  # Nó inicial da aresta atual
        
        # Dados da rede (serão recebidos do coordenador)
        self.nodes = {}
        self.edges = {}
        self.graph = {}
        self.traffic_reports = {}  # Cache local de reportes de trafego
        self.traffic_lights = {}   # Cache local de semaforos
        self.nearby_ambulances = {}  # Cache de ambulâncias próximas {ambulance_id: {'x': x, 'y': y, 'timestamp': time}}
        
    async def setup(self):
        """Configuracao inicial do agente"""
        print(f"VehicleAgent {self.vehicle_id} ({self.vehicle_type}) iniciado: {self.start_node} -> {self.end_node}")
        
        # Behaviour para movimento (MAIS RÁPIDO: 20 Hz)
        move_behaviour = self.MoveBehaviour(period=0.05)  # Reduzido de 0.1 para 0.05
        self.add_behaviour(move_behaviour)
        
        # Behaviour para receber mensagens (SEM TEMPLATE para aceitar TODAS)
        receive_behaviour = self.ReceiveMessagesBehaviour()
        self.add_behaviour(receive_behaviour)  # Sem template = aceita todas as mensagens
        
        # Behaviour para reportar trafego (menos frequente para economizar)
        report_behaviour = self.ReportTrafficBehaviour(period=3.0)  # Aumentado de 2.0 para 3.0
        self.add_behaviour(report_behaviour)
        
        # 🚑 AMBULÂNCIAS: Behaviour para broadcast de posição (prioridade)
        if self.vehicle_type == 'ambulance':
            ambulance_broadcast = self.AmbulanceBroadcastBehaviour(period=0.2)  # 5 vezes por segundo
            self.add_behaviour(ambulance_broadcast)
        
        # Behaviour para solicitar dados da rede (executar uma vez)
        request_behaviour = self.RequestNetworkBehaviour()
        self.add_behaviour(request_behaviour)
    
    def update_speed_multiplier(self, multiplier):
        """Atualiza multiplicador de velocidade dinamicamente"""
        self.speed_multiplier = multiplier
        self.speed = self.base_speed * multiplier
    
    class RequestNetworkBehaviour(OneShotBehaviour):
        """Behaviour para solicitar dados da rede inicial"""
        
        async def run(self):
            """Envia requisicao de dados ao coordenador"""
            msg = Message(to="coordinator@localhost")
            msg.set_metadata("performative", "request")
            msg.body = json.dumps({
                "type": "request_network",
                "vehicle_id": self.agent.vehicle_id
            })
            await self.send(msg)
    
    def calculate_route_astar(self, start, goal):
        """Algoritmo A* para calcular rota otima"""
        if not self.graph or start not in self.graph or goal not in self.graph:
            return []
        
        def heuristic(node1, node2):
            x1, y1 = self.nodes[node1]
            x2, y2 = self.nodes[node2]
            return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {node: float('inf') for node in self.graph}
        g_score[start] = 0
        f_score = {node: float('inf') for node in self.graph}
        f_score[start] = heuristic(start, goal)
        
        while open_set:
            current = heapq.heappop(open_set)[1]
            
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path = path[::-1]
                
                # Calcular custo total da rota (soma dos pesos das arestas)
                if len(path) > 0:
                    self.route_total_cost = g_score[goal]
                    self.route_cost_traveled = 0
                    self.edge_start_node = start
                
                return path
            
            for neighbor, edge_id in self.graph.get(current, []):
                # Peso base da aresta
                edge_weight = self.edges.get(edge_id, {}).get('weight', 100.0)
                
                # Adicionar penalidade por trafego
                if edge_id in self.traffic_reports:
                    delay = self.traffic_reports[edge_id].get('delay', 0)
                    edge_weight += delay * 5
                
                # Adicionar penalidade por semaforos vermelhos
                if neighbor in self.traffic_lights:
                    state = self.traffic_lights[neighbor].get('state', 'green')
                    if state == 'red':
                        edge_weight += 200
                    elif state == 'yellow':
                        edge_weight += 50
                
                tentative_g_score = g_score[current] + edge_weight
                
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        return []
    
    class MoveBehaviour(PeriodicBehaviour):
        """Behaviour para movimentacao do veiculo"""
        
        async def run(self):
            """Atualiza posicao do veiculo"""
            if not self.agent.moving or self.agent.arrival_time is not None:
                return
            
            # Se nao tem rota, calcular
            if not self.agent.route:
                self.agent.route = self.agent.calculate_route_astar(
                    self.agent.current_node,
                    self.agent.end_node
                )
                if self.agent.route:
                    self.agent.route_index = 0
                    self.agent.target_node = self.agent.route[0] if len(self.agent.route) > 0 else None
            
            # Mover ao longo da rota
            if self.agent.route and self.agent.route_index < len(self.agent.route):
                target_node = self.agent.route[self.agent.route_index]
                
                if target_node not in self.agent.nodes:
                    return
                
                target_x, target_y = self.agent.nodes[target_node]
                dx = target_x - self.agent.x
                dy = target_y - self.agent.y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance > 2:
                    # SISTEMA DE RESPEITO AOS SEMÁFOROS E PRIORIDADE DE AMBULÂNCIAS
                    should_stop = False
                    stop_reason = ""
                    
                    # 🚑 PRIORIDADE ABSOLUTA: Verificar se há ambulâncias próximas
                    if self.agent.vehicle_type != 'ambulance':
                        # Limpar ambulâncias antigas (mais de 1 segundo)
                        current_time = time.time()
                        self.agent.nearby_ambulances = {
                            amb_id: data for amb_id, data in self.agent.nearby_ambulances.items()
                            if current_time - data['timestamp'] < 1.0
                        }
                        
                        # Verificar se há ambulância próxima (raio de 150px)
                        for amb_id, amb_data in self.agent.nearby_ambulances.items():
                            amb_x = amb_data['x']
                            amb_y = amb_data['y']
                            dist_to_ambulance = math.sqrt((amb_x - self.agent.x)**2 + (amb_y - self.agent.y)**2)
                            
                            if dist_to_ambulance < 150:
                                # Ambulância próxima! CEDER PASSAGEM
                                should_stop = True
                                stop_reason = f"AMBULANCIA_{amb_id}"
                                if self.agent.waiting_time % 30 == 1:
                                    print(f"🚑 {self.agent.vehicle_id} CEDENDO PASSAGEM para {amb_id} (dist={dist_to_ambulance:.0f}px)")
                                break
                    
                    # 🚦 AMBULÂNCIAS IGNORAM SEMÁFOROS (modo urgência)
                    if not should_stop and self.agent.vehicle_type != 'ambulance':
                        # DETERMINAR DIREÇÃO DO MOVIMENTO (horizontal ou vertical)
                        # Se dx > dy, movimento é predominantemente HORIZONTAL (leste-oeste)
                        # Se dy > dx, movimento é predominantemente VERTICAL (norte-sul)
                        abs_dx = abs(dx)
                        abs_dy = abs(dy)
                        
                        # LÓGICA CORRETA:
                        # - Movimento HORIZONTAL → verifica semáforo VERTICAL (controla tráfego horizontal)
                        # - Movimento VERTICAL → verifica semáforo HORIZONTAL (controla tráfego vertical)
                        # Pense: semáforo "vertical" (barra vertical) bloqueia carros que vão horizontalmente
                        if abs_dx > abs_dy:
                            # Movimento horizontal → verifica semáforo vertical
                            light_orientation = 'vertical'
                        else:
                            # Movimento vertical → verifica semáforo horizontal
                            light_orientation = 'horizontal'
                        
                        # Criar chave para buscar o semáforo correto
                        light_key = f"{target_node}_{light_orientation}"
                        
                        # Verificar se existe semáforo com essa orientação nesse nó
                        if light_key in self.agent.traffic_lights:
                            light_data = self.agent.traffic_lights[light_key]
                            light_state = light_data.get('state', 'green')
                            light_x = light_data.get('x', 0)
                            light_y = light_data.get('y', 0)
                            
                            # Calcular distância até o semáforo
                            dist_to_light = math.sqrt((light_x - self.agent.x)**2 + (light_y - self.agent.y)**2)
                            
                            # Determinar direção do movimento para debug
                            movement_dir = 'horizontal' if abs_dx > abs_dy else 'vertical'
                            
                            # DEBUG: Log sempre que há semáforo
                            if self.agent.vehicle_id == 'v0':
                                print(f"🚦 DEBUG {self.agent.vehicle_id}: movimento={movement_dir}, verifica semáforo={light_key} ({light_orientation}), estado={light_state}, dist={dist_to_light:.0f}px")
                            
                            # 3 REGRAS DE PARADA (apenas para NÃO-ambulâncias):
                            # 1. VERMELHO: SEMPRE para a 60px de distância
                            if light_state == 'red' and dist_to_light < 60:
                                should_stop = True
                                stop_reason = f"RED_{light_orientation[0].upper()}"
                            
                            # 2. AMARELO: Para se estiver a menos de 40px (muito perto)
                            elif light_state == 'yellow' and dist_to_light < 40:
                                should_stop = True
                                stop_reason = f"YELLOW_CLOSE_{light_orientation[0].upper()}"
                            
                            # 3. VELOCIDADE ALTA + AMARELO: Para se vem muito rápido
                            elif light_state == 'yellow' and self.agent.speed > 250 and dist_to_light < 70:
                                should_stop = True
                                stop_reason = f"YELLOW_FAST_{light_orientation[0].upper()}"
                    
                    if should_stop:
                        # PARAR e incrementar tempo de espera
                        self.agent.waiting_time += 1
                        # Debug: mostrar porque parou
                        if self.agent.waiting_time % 20 == 1:  # Log a cada 20 frames
                            print(f"🛑 {self.agent.vehicle_id} PAROU: {stop_reason} no {target_node}")
                    else:
                        # MOVER em direção ao alvo
                        speed_factor = 0.1 * (self.agent.speed / 60.0)
                        self.agent.x += (dx / distance) * speed_factor
                        self.agent.y += (dy / distance) * speed_factor
                else:
                    # Chegou ao no
                    prev_node = self.agent.current_node
                    self.agent.current_node = target_node
                    self.agent.x = target_x
                    self.agent.y = target_y
                    self.agent.route_index += 1
                    
                    # Acumular custo da aresta percorrida (para journey vehicle)
                    if self.agent.vehicle_id == 'v0' and prev_node and self.agent.edge_start_node:
                        # Encontrar a aresta entre edge_start_node e current_node
                        for neighbor, edge_id in self.agent.graph.get(self.agent.edge_start_node, []):
                            if neighbor == target_node:
                                edge_data = self.agent.edges.get(edge_id, {})
                                edge_weight = edge_data.get('weight', 100.0)
                                self.agent.route_cost_traveled += edge_weight
                                break
                        # Atualizar para próxima aresta
                        self.agent.edge_start_node = target_node
                    
                    if self.agent.route_index >= len(self.agent.route):
                        # Chegou ao destino
                        
                        # APENAS o journey vehicle (vehicle_0) para ao chegar
                        if self.agent.vehicle_id == 'v0':
                            self.agent.arrival_time = self.agent.total_travel_time
                            self.agent.moving = False
                            
                            # Notificar coordenador
                            msg = Message(to="coordinator@localhost")
                            msg.set_metadata("performative", "inform")
                            msg.body = json.dumps({
                                "type": "arrival",
                                "vehicle_id": self.agent.vehicle_id,
                                "travel_time": self.agent.total_travel_time,
                                "waiting_time": self.agent.waiting_time
                            })
                            await self.send(msg)
                        else:
                            # Veículos normais: escolher NOVO DESTINO aleatório e continuar
                            nodes_list = list(self.agent.nodes.keys())
                            new_destination = random.choice([n for n in nodes_list if n != self.agent.current_node])
                            
                            # Recalcular rota para novo destino
                            self.agent.end_node = new_destination
                            self.agent.route = self.agent.calculate_route_astar(self.agent.current_node, new_destination)
                            
                            if self.agent.route:
                                self.agent.route_index = 0
                                self.agent.target_node = self.agent.route[0]
                                # print(f"🔄 {self.agent.vehicle_id} escolheu novo destino: {new_destination}")
                    else:
                        self.agent.target_node = self.agent.route[self.agent.route_index]
            
            self.agent.total_travel_time += 1
    
    class ReceiveMessagesBehaviour(CyclicBehaviour):
        """Behaviour para receber mensagens"""
        
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                try:
                    data = json.loads(msg.body)
                    msg_type = data.get('type')
                    
                    if msg_type == 'network_data':
                        # Receber dados da rede
                        self.agent.nodes = data.get('nodes', {})
                        edges_received = data.get('edges', {})
                        # Converter chaves de string para int se necessário
                        self.agent.edges = {}
                        for key, value in edges_received.items():
                            try:
                                self.agent.edges[int(key)] = value
                            except (ValueError, TypeError):
                                self.agent.edges[key] = value
                        self.agent.graph = data.get('graph', {})
                        
                        # Inicializar posicao
                        if self.agent.start_node in self.agent.nodes:
                            self.agent.x, self.agent.y = self.agent.nodes[self.agent.start_node]
                        
                        print(f"Vehicle {self.agent.vehicle_id} recebeu dados da rede")
                    
                    elif msg_type == 'traffic_report':
                        # Atualizar cache de trafego
                        edge_id = data.get('edge_id')
                        if edge_id:
                            self.agent.traffic_reports[edge_id] = data
                    
                    elif msg_type == 'light_state':
                        # Atualizar cache de semaforos (formato antigo do coordinator)
                        node_id = data.get('node_id')
                        if node_id:
                            self.agent.traffic_lights[node_id] = {
                                'state': data.get('state'),
                                'timer': data.get('timer')
                            }
                    
                    elif msg_type == 'traffic_light_update':
                        # ATUALIZAÇÃO DIRETA DO SEMÁFORO via XMPP (PRIORIDADE!)
                        node_id = data.get('node_id')
                        orientation = data.get('orientation', 'unknown')  # 'horizontal' ou 'vertical'
                        
                        if node_id:
                            position = data.get('position', {})
                            
                            # Criar chave única: node_id + orientação
                            light_key = f"{node_id}_{orientation}"
                            
                            # Armazenar estado do semáforo com orientação
                            self.agent.traffic_lights[light_key] = {
                                'state': data.get('state'),
                                'x': position.get('x', 0),
                                'y': position.get('y', 0),
                                'orientation': orientation,
                                'node_id': node_id
                            }
                            
                            # Debug: mostrar recepção com orientação
                            # print(f"🚦 {self.agent.vehicle_id} recebeu: {node_id}_{orientation[0].upper()} = {data.get('state')}")
                    
                    elif msg_type == 'recalculate_route':
                        # Forcar recalculo de rota
                        self.agent.route = []
                    
                    elif msg_type == 'ambulance_position':
                        # 🚑 RECEBER POSIÇÃO DE AMBULÂNCIA (PRIORIDADE!)
                        ambulance_id = data.get('ambulance_id')
                        if ambulance_id:
                            self.agent.nearby_ambulances[ambulance_id] = {
                                'x': data.get('x', 0),
                                'y': data.get('y', 0),
                                'current_node': data.get('current_node'),
                                'speed': data.get('speed', 0),
                                'timestamp': time.time()
                            }
                        
                except json.JSONDecodeError:
                    pass
    
    class ReportTrafficBehaviour(PeriodicBehaviour):
        """Behaviour para reportar condicoes de trafego"""
        
        async def run(self):
            """Reporta trafego na aresta atual"""
            if not self.agent.moving or self.agent.current_node not in self.agent.nodes:
                return
            
            # Construir edge_id
            if self.agent.route and self.agent.route_index < len(self.agent.route):
                current = self.agent.current_node
                next_node = self.agent.route[self.agent.route_index]
                edge_id = f"{current}-{next_node}"
                
                # Calcular delay baseado no tempo de espera
                delay = min(self.agent.waiting_time, 100)
                
                # Broadcast para todos os veiculos
                msg = Message(to="coordinator@localhost")
                msg.set_metadata("performative", "inform")
                msg.body = json.dumps({
                    "type": "traffic_report",
                    "vehicle_id": self.agent.vehicle_id,
                    "edge_id": edge_id,
                    "delay": delay,
                    "speed": self.agent.speed
                })
                await self.send(msg)
    
    class AmbulanceBroadcastBehaviour(PeriodicBehaviour):
        """Behaviour para ambulâncias enviarem broadcast de posição (PRIORIDADE)"""
        
        async def run(self):
            """Envia broadcast de posição para todos os veículos"""
            # Broadcast para todos os 11 carros normais (vehicle_0 a vehicle_10)
            for i in range(11):
                msg = Message(to=f"vehicle_{i}@localhost")
                msg.set_metadata("performative", "inform")
                msg.body = json.dumps({
                    "type": "ambulance_position",
                    "ambulance_id": self.agent.vehicle_id,
                    "x": self.agent.x,
                    "y": self.agent.y,
                    "current_node": self.agent.current_node,
                    "speed": self.agent.speed
                })
                await self.send(msg)
            
            # Broadcast para as outras ambulâncias também (AMB0-AMB3)
            for i in range(4):
                amb_jid = f"amb_{i}@localhost"
                if amb_jid != str(self.agent.jid):  # Não enviar para si mesmo
                    msg = Message(to=amb_jid)
                    msg.set_metadata("performative", "inform")
                    msg.body = json.dumps({
                        "type": "ambulance_position",
                        "ambulance_id": self.agent.vehicle_id,
                        "x": self.agent.x,
                        "y": self.agent.y,
                        "current_node": self.agent.current_node,
                        "speed": self.agent.speed
                    })
                    await self.send(msg)


class TrafficLightAgent(Agent):
    """Agente de semaforo que controla um cruzamento"""
    
    def __init__(self, jid, password, node_id, orientation='horizontal', green_time=10, red_time=10, yellow_time=3, paired_light=None, offset_x=0, offset_y=0):
        super().__init__(jid, password)
        self.node_id = node_id
        self.orientation = orientation  # 'horizontal' ou 'vertical'
        self.paired_light = paired_light  # JID do semáforo par (horizontal ↔ vertical)
        self.offset_x = offset_x  # Deslocamento visual em X
        self.offset_y = offset_y  # Deslocamento visual em Y
        
        # Estado inicial: horizontal começa verde, vertical vermelho
        if orientation == 'horizontal':
            self.state = 'green'
            self.timer = green_time
        else:
            self.state = 'red'
            self.timer = red_time
        
        self.green_time = green_time
        self.red_time = red_time
        self.yellow_time = yellow_time
        self.x = 0  # Posição base do nó
        self.y = 0  # Posição base do nó
        self.visual_x = 0  # Posição visual com offset
        self.visual_y = 0  # Posição visual com offset
        
        # Cache do estado do par (para coordenação)
        self.paired_state = None
    
    async def setup(self):
        """Configuracao inicial do semaforo"""
        print(f"TrafficLightAgent {self.node_id} iniciado")
        
        # Behaviour para ciclo de cores (MAIS RAPIDO - 0.5s)
        cycle_behaviour = self.LightCycleBehaviour(period=0.5)
        self.add_behaviour(cycle_behaviour)
        
        # Behaviour para receber mensagens
        receive_behaviour = self.ReceiveMessagesBehaviour()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(receive_behaviour, template)
        
        # Behaviour para solicitar posicao (executar uma vez)
        request_behaviour = self.RequestPositionBehaviour()
        self.add_behaviour(request_behaviour)
    
    class RequestPositionBehaviour(OneShotBehaviour):
        """Behaviour para solicitar posicao inicial"""
        
        async def run(self):
            """Envia requisicao de posicao ao coordenador"""
            msg = Message(to="coordinator@localhost")
            msg.set_metadata("performative", "request")
            msg.body = json.dumps({
                "type": "request_position",
                "node_id": self.agent.node_id
            })
            await self.send(msg)
    
    class LightCycleBehaviour(PeriodicBehaviour):
        """Behaviour para ciclo de estados do semaforo com coordenação"""
        
        async def run(self):
            """Atualiza estado do semaforo"""
            self.agent.timer -= 1
            
            old_state = self.agent.state
            
            if self.agent.timer <= 0:
                # Determina próximo estado
                next_state = None
                
                if self.agent.state == 'green':
                    next_state = 'yellow'
                    self.agent.timer = self.agent.yellow_time
                elif self.agent.state == 'yellow':
                    next_state = 'red'
                    self.agent.timer = self.agent.red_time
                elif self.agent.state == 'red':
                    # COORDENAÇÃO: verifica se o par está verde antes de mudar
                    if self.agent.paired_light and self.agent.paired_state == 'green':
                        # Par está verde! Não posso ir para verde
                        next_state = 'red'
                        self.agent.timer = 3  # Aguarda 3s e tenta novamente
                        agent_name = str(self.agent.jid).split('@')[0]
                        print(f"🚦 {agent_name} ({self.agent.orientation}) AGUARDANDO (par está VERDE)")
                    else:
                        # Par não está verde, posso ir para verde
                        next_state = 'green'
                        self.agent.timer = self.agent.green_time
                
                # Atualiza estado
                self.agent.state = next_state
                
                # BROADCAST DIRETO para TODOS os veículos quando muda de estado
                if old_state != self.agent.state:
                    # Enviar para todos os 11 carros (vehicle_0 a vehicle_10)
                    for i in range(11):
                        msg = Message(to=f"vehicle_{i}@localhost")
                        msg.set_metadata("performative", "inform")
                        msg.body = json.dumps({
                            "type": "traffic_light_update",
                            "node_id": self.agent.node_id,
                            "state": self.agent.state,
                            "position": {"x": self.agent.x, "y": self.agent.y},
                            "orientation": self.agent.orientation
                        })
                        await self.send(msg)
                    
                    # Enviar para as 4 ambulâncias AMB (amb_0 a amb_3)
                    for i in range(4):
                        msg = Message(to=f"amb_{i}@localhost")
                        msg.set_metadata("performative", "inform")
                        msg.body = json.dumps({
                            "type": "traffic_light_update",
                            "node_id": self.agent.node_id,
                            "state": self.agent.state,
                            "position": {"x": self.agent.x, "y": self.agent.y},
                            "orientation": self.agent.orientation
                        })
                        await self.send(msg)
                    
                    # NOTIFICA o semáforo par sobre mudança de estado
                    if self.agent.paired_light:
                        msg = Message(to=self.agent.paired_light)
                        msg.set_metadata("performative", "inform")
                        msg.body = json.dumps({
                            "type": "paired_light_update",
                            "from": str(self.agent.jid),
                            "state": self.agent.state,
                            "node_id": self.agent.node_id,
                            "orientation": self.agent.orientation
                        })
                        await self.send(msg)
            
            # Também enviar estado para coordenador
            msg = Message(to="coordinator@localhost")
            msg.set_metadata("performative", "inform")
            msg.body = json.dumps({
                "type": "light_state",
                "node_id": self.agent.node_id,
                "state": self.agent.state,
                "timer": self.agent.timer
            })
            await self.send(msg)
    
    class ReceiveMessagesBehaviour(CyclicBehaviour):
        """Behaviour para receber mensagens, incluindo updates do semáforo par"""
        
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                try:
                    data = json.loads(msg.body)
                    msg_type = data.get('type')
                    
                    if msg_type == 'position_data':
                        # Receber posicao base do no
                        self.agent.x = data.get('x', 0.0)
                        self.agent.y = data.get('y', 0.0)
                        # Calcular posição visual com offset
                        self.agent.visual_x = self.agent.x + self.agent.offset_x
                        self.agent.visual_y = self.agent.y + self.agent.offset_y
                        print(f"TrafficLight {self.agent.node_id} ({self.agent.orientation}) recebeu posicao: ({self.agent.x}, {self.agent.y}) -> visual ({self.agent.visual_x}, {self.agent.visual_y})")
                    
                    elif msg_type == 'paired_light_update':
                        # Atualização do estado do semáforo par
                        self.agent.paired_state = data.get('state')
                        # print(f"🔗 {self.agent.jid.localpart} ({self.agent.orientation}): par agora está {self.agent.paired_state}")
                    
                except json.JSONDecodeError:
                    pass


class CoordinatorAgent(Agent):
    """Agente Coordenador central"""
    
    def __init__(self, jid, password, nodes, edges, graph):
        super().__init__(jid, password)
        self.nodes = nodes
        self.edges = edges
        self.graph = graph
        self.vehicles = {}  # {vehicle_id: vehicle_agent_reference}
        self.traffic_lights = {}  # {node_id: traffic_light_agent_reference}
        self.traffic_reports = {}  # Cache de reportes
        self.light_states = {}  # Cache de estados dos semaforos
        self.statistics = {
            'total_arrivals': 0,
            'avg_travel_time': 0,
            'avg_waiting_time': 0
        }
    
    async def setup(self):
        """Configuracao inicial do coordenador"""
        print("CoordinatorAgent iniciado")
        
        # Behaviour para processar mensagens
        receive_behaviour = self.ReceiveMessagesBehaviour()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(receive_behaviour, template)
        
        # Behaviour para processar requests
        request_behaviour = self.RequestHandlerBehaviour()
        template_request = Template()
        template_request.set_metadata("performative", "request")
        self.add_behaviour(request_behaviour, template_request)
    
    def get_vehicle_state(self, vehicle_id):
        """Retorna estado de um veiculo (para Pygame)"""
        return self.vehicles.get(vehicle_id)
    
    def get_light_state(self, node_id):
        """Retorna estado de um semaforo (para Pygame)"""
        return self.light_states.get(node_id)
    
    class ReceiveMessagesBehaviour(CyclicBehaviour):
        """Behaviour para receber informes"""
        
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                try:
                    data = json.loads(msg.body)
                    msg_type = data.get('type')
                    
                    if msg_type == 'traffic_report':
                        # Armazenar reporte de trafego
                        edge_id = data.get('edge_id')
                        if edge_id:
                            self.agent.traffic_reports[edge_id] = data
                    
                    elif msg_type == 'light_state':
                        # Armazenar estado do semaforo
                        node_id = data.get('node_id')
                        if node_id:
                            self.agent.light_states[node_id] = {
                                'state': data.get('state'),
                                'timer': data.get('timer')
                            }
                    
                    elif msg_type == 'arrival':
                        # Processar chegada de veiculo
                        vehicle_id = data.get('vehicle_id')
                        travel_time = data.get('travel_time', 0)
                        waiting_time = data.get('waiting_time', 0)
                        
                        self.agent.statistics['total_arrivals'] += 1
                        # Atualizar medias
                        total = self.agent.statistics['total_arrivals']
                        self.agent.statistics['avg_travel_time'] = (
                            (self.agent.statistics['avg_travel_time'] * (total - 1) + travel_time) / total
                        )
                        self.agent.statistics['avg_waiting_time'] = (
                            (self.agent.statistics['avg_waiting_time'] * (total - 1) + waiting_time) / total
                        )
                        
                        print(f"Veiculo {vehicle_id} chegou! Tempo: {travel_time} steps")
                    
                except json.JSONDecodeError:
                    pass
    
    class RequestHandlerBehaviour(CyclicBehaviour):
        """Behaviour para responder a requisicoes"""
        
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                try:
                    data = json.loads(msg.body)
                    msg_type = data.get('type')
                    
                    if msg_type == 'request_network':
                        # Enviar dados da rede para veiculo
                        vehicle_id = data.get('vehicle_id')
                        reply = Message(to=str(msg.sender))
                        reply.set_metadata("performative", "inform")
                        reply.body = json.dumps({
                            "type": "network_data",
                            "nodes": self.agent.nodes,
                            "edges": self.agent.edges,
                            "graph": self.agent.graph
                        })
                        await self.send(reply)
                        print(f"Enviando dados da rede para {vehicle_id}")
                    
                    elif msg_type == 'request_position':
                        # Enviar posicao do no para semaforo
                        node_id = data.get('node_id')
                        if node_id in self.agent.nodes:
                            x, y = self.agent.nodes[node_id]
                            reply = Message(to=str(msg.sender))
                            reply.set_metadata("performative", "inform")
                            reply.body = json.dumps({
                                "type": "position_data",
                                "node_id": node_id,
                                "x": x,
                                "y": y
                            })
                            await self.send(reply)
                            print(f"Enviando posicao para semaforo {node_id}")
                    
                except json.JSONDecodeError:
                    pass
