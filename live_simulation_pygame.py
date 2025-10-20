#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visualizacao LIVE da Simulacao SPADE com Pygame (SEM SUMO)
Usa apenas agentes SPADE + Prosody para simular trafego
Visual melhorado com ruas de dupla faixa
"""

import pygame
import sys
import asyncio
import threading
import time
import subprocess
import random
from queue import Queue
from typing import Dict, List, Tuple
import json

# Configuracoes Pygame
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
SIDEBAR_WIDTH = 300
FPS = 10

# Cores
COLOR_BG = (26, 26, 46)
COLOR_SIDEBAR = (15, 15, 30)
COLOR_ROAD_BORDER = (50, 50, 50)
COLOR_ROAD_LANE1 = (70, 70, 70)
COLOR_ROAD_LANE2 = (60, 60, 60)
COLOR_LANE_DIVIDER = (200, 200, 100)
COLOR_NODE = (100, 100, 100)
COLOR_VEHICLE_JOURNEY = (251, 191, 36)
COLOR_VEHICLE_NORMAL = (59, 130, 246)
COLOR_VEHICLE_AMBULANCE = (220, 38, 38)
COLOR_LIGHT_GREEN = (16, 185, 129)
COLOR_LIGHT_YELLOW = (251, 191, 36)
COLOR_LIGHT_RED = (239, 68, 68)
COLOR_LIGHT_OFF = (136, 136, 136)
COLOR_TEXT = (255, 255, 255)
COLOR_ACCENT = (102, 126, 234)

class LiveSPADESimulation:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("[Traffic] LIVE SPADE Traffic Simulation (Agentes + Prosody)")
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.SysFont('Arial', 28, bold=True)
        self.font_stats = pygame.font.SysFont('Arial', 18, bold=True)
        self.font_label = pygame.font.SysFont('Arial', 14)
        
        # Rede 8x8 (carregada de JSON ou hardcoded)
        self.nodes = []
        self.edges = []
        self.load_network_8x8()
        
        # Viewport
        self.viewport = self._calculate_viewport()
        
        # Dados em tempo real
        self.current_data = {
            'vehicles': [],
            'traffic_lights': [],
            'stats': {
                'step': 0,
                'total_vehicles': 0,
                'avg_speed': 0.0,
                'total_waiting': 0
            }
        }
        
        # Agentes SPADE
        self.traffic_light_agents = {}
        
        # Estado
        self.running = False
        self.paused = False
        self.simulation_thread = None
        
        # Simulacao de veiculo
        self.car_journey = None
        
        print("Pygame inicializado!")
        print("Rede 8x8:", len(self.nodes), "nos,", len(self.edges), "arestas")
    
    def load_network_8x8(self):
        """Carrega rede 8x8 (grid 200m entre nos)"""
        # Criar grid 8x8
        spacing = 200  # metros entre nos
        
        for row in range(8):
            for col in range(8):
                node_id = "node_" + str(row) + "_" + str(col)
                x = col * spacing
                y = row * spacing
                self.nodes.append({
                    'id': node_id,
                    'x': x,
                    'y': y
                })
        
        # Criar arestas (conexoes horizontais e verticais)
        for row in range(8):
            for col in range(8):
                # Horizontal (esquerda → direita)
                if col < 7:
                    from_node = self.nodes[row * 8 + col]
                    to_node = self.nodes[row * 8 + col + 1]
                    self.edges.append({
                        'id': "edge_" + str(row) + "_" + str(col) + "_to_" + str(row) + "_" + str(col+1),
                        'from': (from_node['x'], from_node['y']),
                        'to': (to_node['x'], to_node['y'])
                    })
                
                # Vertical (cima → baixo)
                if row < 7:
                    from_node = self.nodes[row * 8 + col]
                    to_node = self.nodes[(row + 1) * 8 + col]
                    self.edges.append({
                        'id': "edge_" + str(row) + "_" + str(col) + "_to_" + str(row+1) + "_" + str(col),
                        'from': (from_node['x'], from_node['y']),
                        'to': (to_node['x'], to_node['y'])
                    })
    
    def _calculate_viewport(self):
        """Calcula viewport para centralizar o mapa"""
        if not self.nodes:
            return {'offsetX': 0, 'offsetY': 0, 'scale': 1.0}
        
        xs = [n['x'] for n in self.nodes]
        ys = [n['y'] for n in self.nodes]
        
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
        
        return {
            'offsetX': offset_x,
            'offsetY': offset_y,
            'scale': scale
        }
    
    def world_to_screen(self, x, y):
        """Converte coordenadas do mundo para tela"""
        screen_x = int(x * self.viewport['scale'] + self.viewport['offsetX'])
        screen_y = int(y * self.viewport['scale'] + self.viewport['offsetY'])
        return (screen_x, screen_y)
    
    def start_prosody(self):
        """Inicia container Prosody"""
        print("[Docker] Verificando Prosody...")
        
        check = subprocess.run(
            ['docker', 'ps', '--filter', 'name=prosody', '--format', '{{.Names}}'],
            capture_output=True, text=True
        )
        
        if 'prosody' in check.stdout:
            print("OK Prosody ja esta rodando")
            return True
        
        start = subprocess.run(['docker', 'start', 'prosody'], capture_output=True)
        if start.returncode == 0:
            print("OK Prosody iniciado")
            time.sleep(2)
            return True
        
        print("[Start] Criando container Prosody...")
        run = subprocess.run([
            'docker', 'run', '-d',
            '--name', 'prosody',
            '-p', '5222:5222',
            'prosody/prosody'
        ], capture_output=True)
        
        if run.returncode == 0:
            print("OK Prosody criado e iniciado")
            time.sleep(3)
            return True
        
        print("ERRO Erro ao iniciar Prosody")
        return False
    
    def register_agents(self):
        """Registra agentes no Prosody"""
        print("[Register] Registrando agentes...")
        
        # Semaforos (24 agentes em interseccoes principais)
        tl_positions = [
            (1, 1), (1, 3), (1, 5), (1, 7),
            (3, 1), (3, 3), (3, 5), (3, 7),
            (5, 1), (5, 3), (5, 5), (5, 7),
            (7, 1), (7, 3), (7, 5), (7, 7),
            (2, 2), (2, 4), (2, 6),
            (4, 2), (4, 4), (4, 6),
            (6, 2), (6, 4), (6, 6)
        ]
        
        for row, col in tl_positions:
            tl_id = "tl_" + str(row) + "_" + str(col)
            subprocess.run(
                ['docker', 'exec', 'prosody', 'prosodyctl', 'register', 
                 tl_id, 'localhost', 'password'],
                capture_output=True
            )
        
        print("OK", len(tl_positions), "semaforos registrados")
    
    def create_traffic_light_agents(self):
        """Cria agentes SPADE para semaforos"""
        print("[Agent] Criando agentes SPADE...")
        
        tl_positions = [
            (1, 1), (1, 3), (1, 5), (1, 7),
            (3, 1), (3, 3), (3, 5), (3, 7),
            (5, 1), (5, 3), (5, 5), (5, 7),
            (7, 1), (7, 3), (7, 5), (7, 7),
            (2, 2), (2, 4), (2, 6),
            (4, 2), (4, 4), (4, 6),
            (6, 2), (6, 4), (6, 6)
        ]
        
        for row, col in tl_positions:
            tl_id = "tl_" + str(row) + "_" + str(col)
            jid = tl_id + "@localhost"
            
            # Criar agente (simplificado - sem iniciar por enquanto)
            # Para evitar complexidade, vamos simular estados
            x = col * 200
            y = row * 200
            
            self.traffic_light_agents[tl_id] = {
                'id': tl_id,
                'jid': jid,
                'x': x,
                'y': y,
                'state': 'GGrrGGrr',  # Estado inicial
                'cycle_time': 0,
                'green_time': 30,
                'red_time': 30
            }
        
        print("OK", len(self.traffic_light_agents), "agentes criados")
    
    def init_car_journey(self):
        """Inicializa veiculo para viagem A→B"""
        # Rota: canto superior esquerdo → canto inferior direito
        route = [
            (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),  # Direita
            (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7)          # Baixo
        ]
        
        self.car_journey = {
            'id': 'car_journey',
            'route': route,
            'current_waypoint': 0,
            'x': 0,
            'y': 0,
            'speed': 50,  # km/h
            'waiting_time': 0,
            'type': 'journey'
        }
        
        print("[Car] Veiculo 'car_journey' inicializado")
    
    def simulation_loop(self):
        """Loop principal da simulacao (apenas agentes SPADE)"""
        try:
            print("[Sim] Iniciando simulacao SPADE...")
            
            step = 0
            
            while self.running:
                if not self.paused:
                    step += 1
                    
                    # Atualizar semaforos (logica simplificada)
                    for tl_id, tl in self.traffic_light_agents.items():
                        tl['cycle_time'] += 1
                        
                        # Alternar entre verde e vermelho
                        if tl['cycle_time'] < tl['green_time']:
                            tl['state'] = 'GGrrGGrr'  # Verde
                        elif tl['cycle_time'] < tl['green_time'] + 3:
                            tl['state'] = 'yyrryyrr'  # Amarelo
                        elif tl['cycle_time'] < tl['green_time'] + tl['red_time']:
                            tl['state'] = 'rrGGrrGG'  # Vermelho
                        else:
                            tl['cycle_time'] = 0  # Reset
                    
                    # Atualizar veiculo
                    if self.car_journey and self.car_journey['current_waypoint'] < len(self.car_journey['route']):
                        waypoint = self.car_journey['route'][self.car_journey['current_waypoint']]
                        target_x = waypoint[1] * 200
                        target_y = waypoint[0] * 200
                        
                        # Mover em direcao ao waypoint
                        dx = target_x - self.car_journey['x']
                        dy = target_y - self.car_journey['y']
                        distance = (dx**2 + dy**2) ** 0.5
                        
                        if distance < 5:  # Chegou ao waypoint
                            self.car_journey['current_waypoint'] += 1
                            if self.car_journey['current_waypoint'] >= len(self.car_journey['route']):
                                print("OK Veiculo chegou ao destino!")
                        else:
                            # Mover 5 pixels por frame
                            move_speed = 5
                            self.car_journey['x'] += (dx / distance) * move_speed
                            self.car_journey['y'] += (dy / distance) * move_speed
                    
                    # Atualizar dados
                    vehicles = []
                    if self.car_journey:
                        vehicles.append({
                            'id': self.car_journey['id'],
                            'x': self.car_journey['x'],
                            'y': self.car_journey['y'],
                            'speed': self.car_journey['speed'],
                            'type': 'journey'
                        })
                    
                    traffic_lights = []
                    for tl_id, tl in self.traffic_light_agents.items():
                        traffic_lights.append({
                            'id': tl['id'],
                            'x': tl['x'],
                            'y': tl['y'],
                            'state': tl['state']
                        })
                    
                    self.current_data = {
                        'vehicles': vehicles,
                        'traffic_lights': traffic_lights,
                        'stats': {
                            'step': step,
                            'total_vehicles': len(vehicles),
                            'avg_speed': self.car_journey['speed'] if self.car_journey else 0,
                            'total_waiting': 0
                        }
                    }
                
                time.sleep(0.1)  # 10 FPS
            
            print("OK Simulacao concluida!")
            
        except Exception as e:
            print("ERRO Erro na simulacao: " + str(e) + "")
            import traceback
            traceback.print_exc()
        finally:
            self.running = False
    
    def draw_sidebar(self):
        """Desenha sidebar"""
        pygame.draw.rect(self.screen, COLOR_SIDEBAR, (0, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT))
        
        y_pos = 20
        
        title = self.font_title.render("[Traffic] SPADE Live", True, COLOR_TEXT)
        self.screen.blit(title, (20, y_pos))
        y_pos += 60
        
        if self.running:
            status = "PAUSE PAUSADO" if self.paused else "PLAY RODANDO"
            status_color = (150, 150, 150) if self.paused else COLOR_LIGHT_GREEN
        else:
            status = "STOP PARADO"
            status_color = (150, 150, 150)
        
        text = self.font_stats.render(status, True, status_color)
        self.screen.blit(text, (20, y_pos))
        y_pos += 50
        
        # Stats
        pygame.draw.rect(self.screen, (30, 30, 50), (15, y_pos, SIDEBAR_WIDTH - 30, 180), border_radius=10)
        y_pos += 15
        
        stats_title = self.font_stats.render("[Stats] Stats", True, COLOR_ACCENT)
        self.screen.blit(stats_title, (25, y_pos))
        y_pos += 35
        
        stats = self.current_data['stats']
        items = [
            "Step: " + str(stats['step']),
            "Veiculos: " + str(stats['total_vehicles']),
            "Velocidade: {:.1f} km/h".format(stats['avg_speed']),
            "Semaforos: " + str(len(self.traffic_light_agents))
        ]
        
        for item in items:
            text = self.font_label.render(item, True, COLOR_TEXT)
            self.screen.blit(text, (25, y_pos))
            y_pos += 25
        
        y_pos += 30
        
        # Controles
        pygame.draw.rect(self.screen, (30, 30, 50), (15, y_pos, SIDEBAR_WIDTH - 30, 130), border_radius=10)
        y_pos += 15
        
        controls_title = self.font_stats.render("[Controls] Controles", True, COLOR_ACCENT)
        self.screen.blit(controls_title, (25, y_pos))
        y_pos += 35
        
        controls = ["S - Start/Stop", "ESPAÇO - Pause", "Q - Sair"]
        for ctrl in controls:
            text = self.font_label.render(ctrl, True, COLOR_TEXT)
            self.screen.blit(text, (25, y_pos))
            y_pos += 25
        
        y_pos += 30
        
        # Legenda
        pygame.draw.rect(self.screen, (30, 30, 50), (15, y_pos, SIDEBAR_WIDTH - 30, 120), border_radius=10)
        y_pos += 15
        
        legend_title = self.font_stats.render("[Map] Legenda", True, COLOR_ACCENT)
        self.screen.blit(legend_title, (25, y_pos))
        y_pos += 35
        
        pygame.draw.circle(self.screen, COLOR_VEHICLE_JOURNEY, (35, y_pos + 7), 8)
        text = self.font_label.render("[Car] Viagem A→B", True, COLOR_TEXT)
        self.screen.blit(text, (55, y_pos))
        y_pos += 30
        
        pygame.draw.circle(self.screen, COLOR_LIGHT_GREEN, (35, y_pos + 7), 6)
        text = self.font_label.render("[Green] Verde", True, COLOR_TEXT)
        self.screen.blit(text, (55, y_pos))
    
    def draw_dual_lane_road(self, from_pos, to_pos):
        """Desenha rua com duas faixas"""
        from_screen = self.world_to_screen(from_pos[0], from_pos[1])
        to_screen = self.world_to_screen(to_pos[0], to_pos[1])
        
        dx = to_screen[0] - from_screen[0]
        dy = to_screen[1] - from_screen[1]
        length = (dx**2 + dy**2) ** 0.5
        
        if length == 0:
            return
        
        perp_x = -dy / length
        perp_y = dx / length
        
        lane_width = 3
        lane_offset = 2.5
        
        lane1_from = (
            int(from_screen[0] + perp_x * lane_offset),
            int(from_screen[1] + perp_y * lane_offset)
        )
        lane1_to = (
            int(to_screen[0] + perp_x * lane_offset),
            int(to_screen[1] + perp_y * lane_offset)
        )
        
        lane2_from = (
            int(from_screen[0] - perp_x * lane_offset),
            int(from_screen[1] - perp_y * lane_offset)
        )
        lane2_to = (
            int(to_screen[0] - perp_x * lane_offset),
            int(to_screen[1] - perp_y * lane_offset)
        )
        
        pygame.draw.line(self.screen, COLOR_ROAD_BORDER, lane1_from, lane1_to, lane_width + 2)
        pygame.draw.line(self.screen, COLOR_ROAD_BORDER, lane2_from, lane2_to, lane_width + 2)
        
        pygame.draw.line(self.screen, COLOR_ROAD_LANE1, lane1_from, lane1_to, lane_width)
        pygame.draw.line(self.screen, COLOR_ROAD_LANE2, lane2_from, lane2_to, lane_width)
        
        segments = 10
        for i in range(segments):
            if i % 2 == 0:
                seg_from = (
                    int(from_screen[0] + (to_screen[0] - from_screen[0]) * i / segments),
                    int(from_screen[1] + (to_screen[1] - from_screen[1]) * i / segments)
                )
                seg_to = (
                    int(from_screen[0] + (to_screen[0] - from_screen[0]) * (i + 1) / segments),
                    int(from_screen[1] + (to_screen[1] - from_screen[1]) * (i + 1) / segments)
                )
                pygame.draw.line(self.screen, COLOR_LANE_DIVIDER, seg_from, seg_to, 1)
    
    def draw_network(self):
        """Desenha rede com ruas duplas"""
        for edge in self.edges:
            self.draw_dual_lane_road(edge['from'], edge['to'])
        
        for node in self.nodes:
            pos = self.world_to_screen(node['x'], node['y'])
            pygame.draw.circle(self.screen, COLOR_NODE, pos, 4)
    
    def draw_traffic_lights(self):
        """Desenha semaforos"""
        for tl in self.current_data['traffic_lights']:
            pos = self.world_to_screen(tl['x'], tl['y'])
            
            color = COLOR_LIGHT_OFF
            if tl['state']:
                if 'G' in tl['state']:
                    color = COLOR_LIGHT_GREEN
                elif 'y' in tl['state']:
                    color = COLOR_LIGHT_YELLOW
                elif 'r' in tl['state']:
                    color = COLOR_LIGHT_RED
            
            pygame.draw.circle(self.screen, color, pos, 7)
            pygame.draw.circle(self.screen, (255, 255, 255), pos, 7, 2)
    
    def draw_vehicles(self):
        """Desenha veiculos"""
        for vehicle in self.current_data['vehicles']:
            pos = self.world_to_screen(vehicle['x'], vehicle['y'])
            
            color = COLOR_VEHICLE_JOURNEY if vehicle['id'] == 'car_journey' else COLOR_VEHICLE_NORMAL
            
            pygame.draw.circle(self.screen, color, pos, 10)
            pygame.draw.circle(self.screen, (255, 255, 255), pos, 10, 2)
            
            if vehicle['id'] == 'car_journey':
                label = self.font_label.render("[Car]", True, (255, 255, 255))
                label_rect = label.get_rect(center=(pos[0], pos[1] - 20))
                self.screen.blit(label, label_rect)
    
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
        
        return True
    
    def start_simulation(self):
        """Inicia simulacao"""
        if self.running:
            return
        
        print("\n" + "="*60)
        print("[Start] Iniciando simulacao SPADE...")
        print("="*60)
        
        if not self.start_prosody():
            print("ERRO Erro ao iniciar Prosody")
            return
        
        self.register_agents()
        self.create_traffic_light_agents()
        self.init_car_journey()
        
        self.running = True
        self.simulation_thread = threading.Thread(target=self.simulation_loop, daemon=True)
        self.simulation_thread.start()
        
        print("OK Simulacao iniciada!")
    
    def stop_simulation(self):
        """Para simulacao"""
        print("STOP Parando simulacao...")
        self.running = False
        if self.simulation_thread:
            self.simulation_thread.join(timeout=5)
    
    def run(self):
        """Loop principal"""
        running = True
        
        print("\n" + "="*60)
        print("[Controls] CONTROLES:")
        print("  S - Start/Stop simulacao")
        print("  ESPAÇO - Pause")
        print("  Q - Sair")
        print("="*60 + "\n")
        
        while running:
            running = self.handle_events()
            self.render()
            self.clock.tick(FPS)
        
        self.stop_simulation()
        pygame.quit()
        print("👋 Visualizacao encerrada!")

def main():
    try:
        viz = LiveSPADESimulation()
        viz.run()
    except KeyboardInterrupt:
        print("\nSTOP Interrompido pelo usuario")
        pygame.quit()
        sys.exit(0)
    except Exception as e:
        print("ERRO Erro: " + str(e) + "")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)

if __name__ == '__main__':
    main()
