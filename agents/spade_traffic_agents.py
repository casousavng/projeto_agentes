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
        self.blocked_edges = set()  # Arestas bloqueadas pelo disruptor
        
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
        
        blocked_count = 0  # Contador de arestas bloqueadas
        
        while open_set:
            current = heapq.heappop(open_set)[1]
            
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path = path[::-1]
                
                # 🚧 VALIDAÇÃO CRÍTICA: Verificar se a rota contém arestas bloqueadas
                route_is_valid = True
                for i in range(len(path) - 1):
                    node_from = path[i]
                    node_to = path[i + 1]
                    
                    # Verificar se esta aresta está bloqueada
                    if node_from in self.graph:
                        for neighbor, edge_id in self.graph[node_from]:
                            if neighbor == node_to and edge_id in self.blocked_edges:
                                print(f"❌ A*: {self.vehicle_id} - ROTA INVÁLIDA! Contém aresta bloqueada {edge_id} ({node_from}->{node_to})")
                                route_is_valid = False
                                break
                    if not route_is_valid:
                        break
                
                # Se a rota contém bloqueios, retornar vazio (forçar novo cálculo)
                if not route_is_valid:
                    print(f"⛔ A*: {self.vehicle_id} - Rota rejeitada por conter vias bloqueadas")
                    return []
                
                # Calcular custo total da rota (soma dos pesos das arestas)
                if len(path) > 0:
                    self.route_total_cost = g_score[goal]
                    self.route_cost_traveled = 0
                    self.edge_start_node = start
                
                if blocked_count > 0:
                    print(f"🛤️  {self.vehicle_id}: Rota calculada evitando {blocked_count} vias bloqueadas")
                
                return path
            
            for neighbor, edge_id in self.graph.get(current, []):
                # 🚧 VERIFICAR SE A VIA ESTÁ BLOQUEADA - IGNORAR COMPLETAMENTE
                if edge_id in self.blocked_edges:
                    blocked_count += 1
                    # Log para debug (apenas primeiras vezes)
                    if blocked_count <= 3:
                        print(f"🚫 A*: {self.vehicle_id} pulou aresta bloqueada {edge_id} ({current}->{neighbor})")
                    continue  # Pular esta aresta completamente
                
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
        
        # Se chegou aqui, não há caminho disponível
        if blocked_count > 0:
            print(f"⛔ {self.vehicle_id}: Sem rota disponível! Bloqueios impediram acesso ao destino ({blocked_count} vias bloqueadas)")
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
                else:
                    # Não há rota disponível (possivelmente devido a bloqueios)
                    # Para veículos normais: escolher novo destino aleatório
                    if self.agent.vehicle_id != 'v0' and self.agent.vehicle_type != 'ambulance':
                        nodes_list = list(self.agent.nodes.keys())
                        available_nodes = [n for n in nodes_list if n != self.agent.current_node]
                        
                        if available_nodes:  # Verificar se há nós disponíveis
                            new_destination = random.choice(available_nodes)
                            print(f"🔄 {self.agent.vehicle_id}: Sem rota para {self.agent.end_node}. Tentando novo destino: {new_destination}")
                            self.agent.end_node = new_destination
                        else:
                            print(f"⚠️ {self.agent.vehicle_id}: Sem destinos alternativos disponíveis!")
                    # Journey vehicle e ambulâncias: aguardar (bloqueios podem ser temporários)
                    return
            
            # 🚧 VERIFICAR SE A ARESTA ATUAL ESTÁ BLOQUEADA
            if self.agent.route and self.agent.route_index < len(self.agent.route):
                current = self.agent.current_node
                next_node = self.agent.route[self.agent.route_index]
                
                # Encontrar o edge_id entre current e next_node
                if current in self.agent.graph:
                    for neighbor, edge_id in self.agent.graph[current]:
                        if neighbor == next_node:
                            # Verificar se está bloqueada
                            if edge_id in self.agent.blocked_edges:
                                print(f"🚫 {self.agent.vehicle_id}: via atual {current}->{next_node} (edge {edge_id}) está BLOQUEADA! Recalculando...")
                                self.agent.route = []  # Forçar recálculo
                                return
                            break
            
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
                    
                    # 🚧 VERIFICAÇÃO CRÍTICA: Antes de avançar, verificar se a PRÓXIMA aresta está bloqueada
                    if self.agent.route_index < len(self.agent.route):
                        next_target = self.agent.route[self.agent.route_index]
                        
                        # Verificar se a aresta entre current_node e next_target está bloqueada
                        if target_node in self.agent.graph:
                            for neighbor, edge_id in self.agent.graph[target_node]:
                                if neighbor == next_target:
                                    if edge_id in self.agent.blocked_edges:
                                        print(f"⛔ {self.agent.vehicle_id}: PRÓXIMA via {target_node}->{next_target} (edge {edge_id}) está BLOQUEADA!")
                                        print(f"⛔ {self.agent.vehicle_id}: Parando no nó {target_node} e recalculando...")
                                        self.agent.route = []  # Forçar recálculo completo
                                        return
                                    break
                    
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
            msg = await self.receive(timeout=0.1)  # Timeout reduzido para não bloquear
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
                    
                    elif msg_type == 'blocked_edges_update':
                        # 🚧 RECEBER ATUALIZAÇÃO DE VIAS BLOQUEADAS
                        blocked = data.get('blocked_edges', [])
                        old_count = len(self.agent.blocked_edges)
                        self.agent.blocked_edges = set(blocked)
                        
                        print(f"\n🚧 {self.agent.vehicle_id}: Atualização de bloqueios recebida")
                        print(f"🚧 {self.agent.vehicle_id}: Antes: {old_count} bloqueios")
                        print(f"🚧 {self.agent.vehicle_id}: Agora: {len(blocked)} bloqueios")
                        print(f"🚧 {self.agent.vehicle_id}: Bloqueios: {self.agent.blocked_edges}")
                        print(f"🚧 {self.agent.vehicle_id}: Forçando recálculo de rota...\n")
                        
                        # Forçar recálculo de rota
                        self.agent.route = []  # Força recálculo na próxima iteração
                        
                except json.JSONDecodeError:
                    print(f"❌ Erro ao decodificar JSON: {msg.body}")
                except Exception as e:
                    print(f"❌ Erro ao processar mensagem no veículo {self.agent.vehicle_id}: {e}")
    
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
            """Envia broadcast de posição via coordenador"""
            # Enviar para coordenador que vai distribuir
            msg = Message(to="coordinator@localhost")
            msg.set_metadata("performative", "inform")
            msg.body = json.dumps({
                "type": "ambulance_broadcast",
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
                
                # BROADCAST via coordenador quando muda de estado
                if old_state != self.agent.state:
                    # Enviar para o coordenador que vai distribuir para todos
                    msg = Message(to="coordinator@localhost")
                    msg.set_metadata("performative", "inform")
                    msg.body = json.dumps({
                        "type": "traffic_light_broadcast",
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
        self.blocked_edges = set()  # Conjunto de arestas bloqueadas pelo disruptor
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
                    
                    elif msg_type == 'traffic_light_broadcast':
                        # Receber broadcast de semáforo e distribuir para todos os veículos
                        for vehicle_jid in self.agent.vehicles.keys():
                            msg_reply = Message(to=vehicle_jid)
                            msg_reply.set_metadata("performative", "inform")
                            msg_reply.body = json.dumps({
                                "type": "traffic_light_update",
                                "node_id": data.get('node_id'),
                                "state": data.get('state'),
                                "position": data.get('position'),
                                "orientation": data.get('orientation')
                            })
                            await self.send(msg_reply)
                    
                    elif msg_type == 'ambulance_broadcast':
                        # Receber broadcast de ambulância e distribuir para todos os veículos
                        for vehicle_jid in self.agent.vehicles.keys():
                            msg_reply = Message(to=vehicle_jid)
                            msg_reply.set_metadata("performative", "inform")
                            msg_reply.body = json.dumps({
                                "type": "ambulance_position",
                                "ambulance_id": data.get('ambulance_id'),
                                "x": data.get('x'),
                                "y": data.get('y'),
                                "current_node": data.get('current_node'),
                                "speed": data.get('speed')
                            })
                            await self.send(msg_reply)
                    
                    elif msg_type == 'road_disruption':
                        # Receber notificação de vias bloqueadas
                        blocked = data.get('blocked_edges', [])
                        active = data.get('active', False)
                        
                        print(f"\n" + "="*80)
                        print(f"📡 COORDENADOR: Recebeu notificação de disrupção")
                        print(f"📡 COORDENADOR: {len(blocked)} vias bloqueadas, ativo={active}")
                        print(f"📡 COORDENADOR: Vias: {blocked}")
                        print(f"📡 COORDENADOR: {len(self.agent.vehicles)} veículos registrados")
                        print("="*80 + "\n")
                        
                        if active:
                            self.agent.blocked_edges = set(blocked)
                        else:
                            self.agent.blocked_edges = set()
                        
                        # Broadcast para todos os veículos (CORRIGIDO: passar blocked como argumento)
                        await self.agent.broadcast_blocked_edges(blocked)
                    
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
    
    async def broadcast_blocked_edges(self, blocked_edges):
        """Envia informação de bloqueios para todos os veículos usando behaviour"""
        print(f"\n📢 COORDENADOR: Iniciando broadcast de {len(blocked_edges)} bloqueios")
        print(f"📢 COORDENADOR: Para {len(self.vehicles)} veículos: {list(self.vehicles.keys())}")
        
        # Criar e adicionar behaviour para enviar mensagens
        behaviour = self.BroadcastBlockedEdgesBehaviour(
            list(self.vehicles.keys()), 
            blocked_edges
        )
        self.add_behaviour(behaviour)
    
    class BroadcastBlockedEdgesBehaviour(OneShotBehaviour):
        """Behaviour one-shot para broadcast de bloqueios"""
        
        def __init__(self, vehicle_jids, blocked_edges):
            super().__init__()
            self.vehicle_jids = vehicle_jids
            self.blocked_edges = blocked_edges
        
        async def run(self):
            for vehicle_jid in self.vehicle_jids:
                msg = Message(to=vehicle_jid)
                msg.set_metadata("performative", "inform")
                msg.body = json.dumps({
                    "type": "blocked_edges_update",
                    "blocked_edges": self.blocked_edges
                })
                await self.send(msg)
                print(f"📤 COORDENADOR: Mensagem enviada para {vehicle_jid}")
            print(f"📡 Broadcast de bloqueios enviado para {len(self.vehicle_jids)} veículos")
    
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
                        vehicle_jid = str(msg.sender)
                        
                        # Registrar veículo
                        self.agent.vehicles[vehicle_jid] = vehicle_id
                        
                        reply = Message(to=vehicle_jid)
                        reply.set_metadata("performative", "inform")
                        reply.body = json.dumps({
                            "type": "network_data",
                            "nodes": self.agent.nodes,
                            "edges": self.agent.edges,
                            "graph": self.agent.graph
                        })
                        await self.send(reply)
                        print(f"Enviando dados da rede para {vehicle_id} e registrando")
                    
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


class DisruptorAgent(Agent):
    """Agente Disruptor - Gera bloqueios aleatórios em vias"""
    
    def __init__(self, jid, password, edges):
        super().__init__(jid, password)
        self.edges = edges  # Lista de todas as arestas disponíveis
        self.blocked_edges = set()  # Conjunto de IDs de arestas bloqueadas
        self.coordinator_jid: Optional[str] = None
        self.disruption_active = False
        
    async def setup(self):
        """Configuração inicial do disruptor"""
        print("DisruptorAgent iniciado")
        
        # Armazenar referência ao event loop
        self.loop = asyncio.get_event_loop()
        
        # Behaviour para receber comandos
        receive_behaviour = self.ReceiveCommandsBehaviour()
        self.add_behaviour(receive_behaviour)
    
    def activate_disruption(self):
        """Ativa disrupção bloqueando 6 vias aleatórias (evitando vias críticas do perímetro)"""
        if not self.disruption_active:
            # Identificar vias do perímetro (menos críticas para bloquear)
            # Vias do perímetro conectam nós (0,0), (0,5), (5,0), (5,5)
            perimeter_nodes = {'0_0', '0_5', '5_0', '5_5'}
            
            # Filtrar vias que NÃO são do perímetro externo
            available_edges = []
            for edge_id, edge_data in self.edges.items():
                from_node = edge_data['from']
                to_node = edge_data['to']
                
                # Evitar bloquear vias que conectam diretamente os 4 cantos
                is_perimeter = (from_node in perimeter_nodes and to_node in perimeter_nodes)
                
                if not is_perimeter:
                    available_edges.append(edge_id)
            
            # Selecionar 6 arestas aleatórias das disponíveis
            if len(available_edges) >= 6:
                self.blocked_edges = set(random.sample(available_edges, 6))
                self.disruption_active = True
                
                # Mostrar quais vias foram bloqueadas
                blocked_info = []
                for edge_id in self.blocked_edges:
                    edge_data = self.edges[edge_id]
                    blocked_info.append(f"{edge_data['from']} -> {edge_data['to']}")
                
                print(f"\n" + "="*80)
                print(f"🚧 DISRUPTOR: Disrupção ATIVADA!")
                print(f"🚧 DISRUPTOR: {len(self.blocked_edges)} vias bloqueadas:")
                for info in blocked_info:
                    print(f"   🚧 {info}")
                print(f"🚧 DISRUPTOR: Preparando notificação para {self.coordinator_jid}")
                print("="*80 + "\n")
                
                # Notificar coordenador de forma segura
                self._schedule_notification()
                return True
            else:
                print(f"⚠️ DISRUPTOR: Não há vias suficientes disponíveis ({len(available_edges)} < 6)")
        return False
    
    def deactivate_disruption(self):
        """Desativa disrupção liberando todas as vias"""
        if self.disruption_active:
            self.blocked_edges = set()
            self.disruption_active = False
            print(f"\n" + "="*80)
            print(f"✅ DISRUPTOR: Disrupção DESATIVADA!")
            print(f"✅ DISRUPTOR: Todas as vias liberadas")
            print(f"✅ DISRUPTOR: Notificando {self.coordinator_jid}")
            print("="*80 + "\n")
            
            # Notificar coordenador de forma segura
            self._schedule_notification()
            return True
        return False
    
    def _schedule_notification(self):
        """Agenda notificação de forma segura (funciona de qualquer thread)"""
        try:
            # Tentar obter o loop do agente
            loop = self.loop
            if loop and loop.is_running():
                # Usar call_soon_threadsafe para agendar a coroutine
                asyncio.run_coroutine_threadsafe(self.notify_coordinator(), loop)
        except Exception as e:
            print(f"⚠️ Erro ao agendar notificação: {e}")
    
    def toggle_disruption(self):
        """Alterna entre ativar/desativar disrupção"""
        if self.disruption_active:
            return self.deactivate_disruption()
        else:
            return self.activate_disruption()
    
    async def notify_coordinator(self):
        """Notifica o coordenador sobre vias bloqueadas"""
        if not self.is_alive():
            return
            
        if self.coordinator_jid:
            try:
                msg = Message(to=self.coordinator_jid)
                msg.set_metadata("performative", "inform")
                msg.body = json.dumps({
                    "type": "road_disruption",
                    "blocked_edges": list(self.blocked_edges),
                    "active": self.disruption_active
                })
                
                # Criar behaviour temporário para enviar mensagem
                behaviour = self.SendNotificationBehaviour(msg)
                self.add_behaviour(behaviour)
                
                print(f"📤 DISRUPTOR: Notificação agendada para coordenador {self.coordinator_jid}")
                print(f"📤 DISRUPTOR: Dados: {len(self.blocked_edges)} bloqueios, ativo={self.disruption_active}")
            except Exception as e:
                print(f"❌ Erro ao enviar notificação: {e}")
    
    class SendNotificationBehaviour(OneShotBehaviour):
        """Behaviour one-shot para enviar notificação"""
        
        def __init__(self, message):
            super().__init__()
            self.message = message
        
        async def run(self):
            try:
                await self.send(self.message)
                print(f"✅ DISRUPTOR: Mensagem ENVIADA com sucesso para {self.message.to}")
            except Exception as e:
                print(f"❌ DISRUPTOR: Erro ao enviar mensagem: {e}")
    
    class ReceiveCommandsBehaviour(CyclicBehaviour):
        """Behaviour para receber comandos externos"""
        
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                try:
                    data = json.loads(msg.body)
                    cmd = data.get('command')
                    
                    if cmd == 'activate':
                        self.agent.activate_disruption()
                    elif cmd == 'deactivate':
                        self.agent.deactivate_disruption()
                    elif cmd == 'toggle':
                        self.agent.toggle_disruption()
                        
                except json.JSONDecodeError:
                    pass
            await asyncio.sleep(0.1)
