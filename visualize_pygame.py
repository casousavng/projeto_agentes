#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visualização da Simulação SPADE com Pygame
Renderiza a cidade, semáforos, veículos em tempo real
"""

import pygame
import sys
import time
from utils.data_collector import SimulationDataCollector

# Configurações
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
SIDEBAR_WIDTH = 300
FPS = 10  # 10 FPS = 10 snapshots por segundo

# Cores
COLOR_BG = (26, 26, 46)
COLOR_SIDEBAR = (15, 15, 30)
COLOR_ROAD = (70, 70, 70)
COLOR_NODE = (100, 100, 100)
COLOR_VEHICLE_JOURNEY = (251, 191, 36)  # Amarelo - carro principal
COLOR_VEHICLE_NORMAL = (59, 130, 246)   # Azul - tráfego
COLOR_VEHICLE_AMBULANCE = (220, 38, 38)  # Vermelho - emergência
COLOR_LIGHT_GREEN = (16, 185, 129)
COLOR_LIGHT_YELLOW = (251, 191, 36)
COLOR_LIGHT_RED = (239, 68, 68)
COLOR_LIGHT_OFF = (136, 136, 136)
COLOR_TEXT = (255, 255, 255)
COLOR_ACCENT = (102, 126, 234)

class TrafficSimVisualization:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("🚦 SPADE Traffic Simulation - Pygame Visualizer")
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.SysFont('Arial', 28, bold=True)
        self.font_stats = pygame.font.SysFont('Arial', 18, bold=True)
        self.font_label = pygame.font.SysFont('Arial', 14)
        
        # Dados
        self.collector = SimulationDataCollector('simulation_data.db')
        self.current_step = 10  # Começa no primeiro snapshot
        self.step_range = self.collector.get_step_range()
        self.min_step = self.step_range['min'] if self.step_range else 10
        self.max_step = self.step_range['max'] if self.step_range else 1670
        
        # Topologia da rede
        topology = self.collector.get_network_topology()
        self.nodes = topology.get('nodes', [])
        self.edges = topology.get('edges', [])
        
        # Viewport
        self.viewport = self._calculate_viewport()
        
        # Estado
        self.paused = True
        self.speed = 1.0  # Velocidade de reprodução
        
        print(f"✅ Pygame inicializado!")
        print(f"📊 Range de steps: {self.min_step} - {self.max_step} ({self.step_range['count']} snapshots)")
        print(f"🗺️ Rede: {len(self.nodes)} nós, {len(self.edges)} arestas")
    
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
        
        # Área útil (sem sidebar)
        canvas_width = WINDOW_WIDTH - SIDEBAR_WIDTH - 40
        canvas_height = WINDOW_HEIGHT - 40
        
        scale_x = canvas_width / width if width > 0 else 1
        scale_y = canvas_height / height if height > 0 else 1
        scale = min(scale_x, scale_y) * 0.85  # 85% para margem
        
        offset_x = SIDEBAR_WIDTH + 20 + (canvas_width - width * scale) / 2 - min_x * scale
        offset_y = 20 + (canvas_height - height * scale) / 2 - min_y * scale
        
        return {
            'offsetX': offset_x,
            'offsetY': offset_y,
            'scale': scale,
            'minX': min_x,
            'minY': min_y,
            'maxX': max_x,
            'maxY': max_y
        }
    
    def world_to_screen(self, x, y):
        """Converte coordenadas do mundo para tela"""
        screen_x = int(x * self.viewport['scale'] + self.viewport['offsetX'])
        screen_y = int(y * self.viewport['scale'] + self.viewport['offsetY'])
        return (screen_x, screen_y)
    
    def draw_sidebar(self, snapshot_data):
        """Desenha sidebar com controles e estatísticas"""
        # Fundo
        pygame.draw.rect(self.screen, COLOR_SIDEBAR, (0, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT))
        
        y_pos = 20
        
        # Título
        title = self.font_title.render("🚦 Traffic Sim", True, COLOR_TEXT)
        self.screen.blit(title, (20, y_pos))
        y_pos += 60
        
        # Controles
        control_text = "ESPAÇO - Play/Pause"
        text = self.font_label.render(control_text, True, COLOR_TEXT)
        self.screen.blit(text, (20, y_pos))
        y_pos += 25
        
        control_text = "↑↓ - Velocidade"
        text = self.font_label.render(control_text, True, COLOR_TEXT)
        self.screen.blit(text, (20, y_pos))
        y_pos += 25
        
        control_text = "←→ - Avançar/Voltar"
        text = self.font_label.render(control_text, True, COLOR_TEXT)
        self.screen.blit(text, (20, y_pos))
        y_pos += 25
        
        control_text = "R - Reiniciar"
        text = self.font_label.render(control_text, True, COLOR_TEXT)
        self.screen.blit(text, (20, y_pos))
        y_pos += 25
        
        control_text = "Q - Sair"
        text = self.font_label.render(control_text, True, COLOR_TEXT)
        self.screen.blit(text, (20, y_pos))
        y_pos += 50
        
        # Status
        status = "⏸️ PAUSADO" if self.paused else "▶️ RODANDO"
        status_color = (150, 150, 150) if self.paused else COLOR_LIGHT_GREEN
        text = self.font_stats.render(status, True, status_color)
        self.screen.blit(text, (20, y_pos))
        y_pos += 40
        
        # Estatísticas
        pygame.draw.rect(self.screen, (30, 30, 50), (15, y_pos, SIDEBAR_WIDTH - 30, 200), border_radius=10)
        y_pos += 15
        
        stats_title = self.font_stats.render("📊 Estatísticas", True, COLOR_ACCENT)
        self.screen.blit(stats_title, (25, y_pos))
        y_pos += 35
        
        # Step
        step_text = f"Step: {self.current_step}"
        text = self.font_label.render(step_text, True, COLOR_TEXT)
        self.screen.blit(text, (25, y_pos))
        y_pos += 25
        
        # Tempo simulado
        sim_time = self.current_step * 0.1  # 0.1s por step
        minutes = int(sim_time // 60)
        seconds = int(sim_time % 60)
        time_text = f"Tempo: {minutes}:{seconds:02d}"
        text = self.font_label.render(time_text, True, COLOR_TEXT)
        self.screen.blit(text, (25, y_pos))
        y_pos += 25
        
        if snapshot_data:
            stats = snapshot_data.get('stats', {})
            
            # Veículos
            vehicles_text = f"Veículos: {stats.get('total_vehicles', 0)}"
            text = self.font_label.render(vehicles_text, True, COLOR_TEXT)
            self.screen.blit(text, (25, y_pos))
            y_pos += 25
            
            # Velocidade média
            speed_text = f"Velocidade: {stats.get('avg_speed', 0):.1f} km/h"
            text = self.font_label.render(speed_text, True, COLOR_TEXT)
            self.screen.blit(text, (25, y_pos))
            y_pos += 25
            
            # Parados
            waiting_text = f"Parados: {stats.get('total_waiting', 0)}"
            text = self.font_label.render(waiting_text, True, COLOR_TEXT)
            self.screen.blit(text, (25, y_pos))
            y_pos += 25
        
        y_pos += 30
        
        # Legenda
        pygame.draw.rect(self.screen, (30, 30, 50), (15, y_pos, SIDEBAR_WIDTH - 30, 280), border_radius=10)
        y_pos += 15
        
        legend_title = self.font_stats.render("🗺️ Legenda", True, COLOR_ACCENT)
        self.screen.blit(legend_title, (25, y_pos))
        y_pos += 35
        
        # Veículos
        pygame.draw.circle(self.screen, COLOR_VEHICLE_JOURNEY, (35, y_pos + 7), 8)
        text = self.font_label.render("🚗 Viagem A→B", True, COLOR_TEXT)
        self.screen.blit(text, (55, y_pos))
        y_pos += 30
        
        pygame.draw.circle(self.screen, COLOR_VEHICLE_NORMAL, (35, y_pos + 7), 8)
        text = self.font_label.render("🚙 Tráfego", True, COLOR_TEXT)
        self.screen.blit(text, (55, y_pos))
        y_pos += 30
        
        pygame.draw.circle(self.screen, COLOR_VEHICLE_AMBULANCE, (35, y_pos + 7), 8)
        text = self.font_label.render("🚑 Emergência", True, COLOR_TEXT)
        self.screen.blit(text, (55, y_pos))
        y_pos += 40
        
        # Semáforos
        pygame.draw.circle(self.screen, COLOR_LIGHT_GREEN, (35, y_pos + 7), 6)
        text = self.font_label.render("🟢 Verde", True, COLOR_TEXT)
        self.screen.blit(text, (55, y_pos))
        y_pos += 25
        
        pygame.draw.circle(self.screen, COLOR_LIGHT_YELLOW, (35, y_pos + 7), 6)
        text = self.font_label.render("🟡 Amarelo", True, COLOR_TEXT)
        self.screen.blit(text, (55, y_pos))
        y_pos += 25
        
        pygame.draw.circle(self.screen, COLOR_LIGHT_RED, (35, y_pos + 7), 6)
        text = self.font_label.render("🔴 Vermelho", True, COLOR_TEXT)
        self.screen.blit(text, (55, y_pos))
        
        # Progresso
        progress_y = WINDOW_HEIGHT - 60
        pygame.draw.rect(self.screen, (30, 30, 50), (15, progress_y, SIDEBAR_WIDTH - 30, 40), border_radius=10)
        
        progress = (self.current_step - self.min_step) / (self.max_step - self.min_step) if self.max_step > self.min_step else 0
        progress_width = int((SIDEBAR_WIDTH - 50) * progress)
        pygame.draw.rect(self.screen, COLOR_ACCENT, (25, progress_y + 10, progress_width, 20), border_radius=5)
        
        progress_text = f"{int(progress * 100)}%"
        text = self.font_label.render(progress_text, True, COLOR_TEXT)
        text_rect = text.get_rect(center=(SIDEBAR_WIDTH // 2, progress_y + 20))
        self.screen.blit(text, text_rect)
    
    def draw_network(self):
        """Desenha ruas e nós"""
        # Arestas (ruas)
        for edge in self.edges:
            from_pos = self.world_to_screen(edge['from'][0], edge['from'][1])
            to_pos = self.world_to_screen(edge['to'][0], edge['to'][1])
            pygame.draw.line(self.screen, COLOR_ROAD, from_pos, to_pos, 3)
        
        # Nós
        for node in self.nodes:
            pos = self.world_to_screen(node['x'], node['y'])
            pygame.draw.circle(self.screen, COLOR_NODE, pos, 3)
    
    def draw_traffic_lights(self, traffic_lights):
        """Desenha semáforos"""
        for tl in traffic_lights:
            pos = self.world_to_screen(tl['x'], tl['y'])
            
            # Determina cor baseado no estado
            color = COLOR_LIGHT_OFF
            if tl['state']:
                if 'G' in tl['state']:
                    color = COLOR_LIGHT_GREEN
                elif 'y' in tl['state']:
                    color = COLOR_LIGHT_YELLOW
                elif 'r' in tl['state']:
                    color = COLOR_LIGHT_RED
            
            # Desenha círculo do semáforo
            pygame.draw.circle(self.screen, color, pos, 7)
            pygame.draw.circle(self.screen, (255, 255, 255), pos, 7, 2)
    
    def draw_vehicles(self, vehicles):
        """Desenha veículos"""
        for vehicle in vehicles:
            pos = self.world_to_screen(vehicle['x'], vehicle['y'])
            
            # Determina cor baseado no tipo/id
            color = COLOR_VEHICLE_NORMAL
            if vehicle['id'] == 'car_journey':
                color = COLOR_VEHICLE_JOURNEY
            elif vehicle['type'] == 'ambulance':
                color = COLOR_VEHICLE_AMBULANCE
            
            # Desenha veículo
            pygame.draw.circle(self.screen, color, pos, 10)
            pygame.draw.circle(self.screen, (255, 255, 255), pos, 10, 2)
            
            # Label para car_journey
            if vehicle['id'] == 'car_journey':
                label = self.font_label.render("🚗", True, (255, 255, 255))
                label_rect = label.get_rect(center=(pos[0], pos[1] - 20))
                self.screen.blit(label, label_rect)
    
    def handle_events(self):
        """Processa eventos do teclado"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self.current_step = self.min_step
                    self.paused = True
                elif event.key == pygame.K_RIGHT:
                    self.current_step = min(self.current_step + 10, self.max_step)
                elif event.key == pygame.K_LEFT:
                    self.current_step = max(self.current_step - 10, self.min_step)
                elif event.key == pygame.K_UP:
                    self.speed = min(self.speed * 2, 8.0)
                    print(f"⚡ Velocidade: {self.speed}x")
                elif event.key == pygame.K_DOWN:
                    self.speed = max(self.speed / 2, 0.25)
                    print(f"🐢 Velocidade: {self.speed}x")
        
        return True
    
    def update(self):
        """Atualiza estado da simulação"""
        if not self.paused:
            self.current_step += 10 * self.speed
            
            # Loop ao chegar no fim
            if self.current_step > self.max_step:
                self.current_step = self.min_step
    
    def render(self):
        """Renderiza frame"""
        # Limpa tela
        self.screen.fill(COLOR_BG)
        
        # Busca dados do snapshot atual
        snapshot = self.collector.get_snapshot_by_step(int(self.current_step))
        
        # Desenha elementos
        self.draw_network()
        
        if snapshot:
            self.draw_traffic_lights(snapshot.get('traffic_lights', []))
            self.draw_vehicles(snapshot.get('vehicles', []))
        
        # Desenha sidebar por último (overlay)
        self.draw_sidebar(snapshot)
        
        # Atualiza display
        pygame.display.flip()
    
    def run(self):
        """Loop principal"""
        running = True
        
        print("\n" + "="*60)
        print("🎮 CONTROLES:")
        print("  ESPAÇO - Play/Pause")
        print("  ←→ - Avançar/Voltar 10 steps")
        print("  ↑↓ - Aumentar/Diminuir velocidade")
        print("  R - Reiniciar")
        print("  Q - Sair")
        print("="*60 + "\n")
        
        while running:
            running = self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
        
        pygame.quit()
        print("👋 Visualização encerrada!")

def main():
    try:
        viz = TrafficSimVisualization()
        viz.run()
    except KeyboardInterrupt:
        print("\n⏹️ Interrompido pelo usuário")
        pygame.quit()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)

if __name__ == '__main__':
    main()
