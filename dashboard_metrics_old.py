#!/usr/bin/env python3
"""
Dashboard de Métricas em Tempo Real para Simulação de Tráfego
Monitoriza os ficheiros CSV da pasta metrics/ e apresenta estatísticas atualizadas.

Uso:
    python dashboard_metrics.py [--refresh SECONDS]
"""

import os
import sys
import time
import csv
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import argparse

try:
    from rich.console import Console
    from rich.table import Table
    from rich.live import Live
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.text import Text
    from rich.align import Align
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️  Biblioteca 'rich' não encontrada. Instale com: pip install rich")
    print("A usar modo básico de terminal...\n")


class MetricsDashboard:
    """Dashboard para monitorizar métricas da simulação em tempo real."""
    
    def __init__(self, metrics_dir="metrics", refresh_interval=2.0):
        self.metrics_dir = Path(metrics_dir)
        self.refresh_interval = refresh_interval
        self.console = Console() if RICH_AVAILABLE else None
        
        # Ficheiros de métricas esperados
        self.files = {
            'recalc_latency': self.metrics_dir / 'recalc_latency.csv',
            'route_costs': self.metrics_dir / 'route_costs.csv',
            'semaphore_penalty': self.metrics_dir / 'semaphore_penalty.csv',
            'traffic_penalty': self.metrics_dir / 'traffic_penalty.csv',
            'summary': self.metrics_dir / 'summary.csv'
        }
        
        self.data = {
            'recalc_latency': [],
            'route_costs': [],
            'semaphore_penalty': [],
            'traffic_penalty': []
        }
        
        self.summary_stats = {}
        self.last_modified = {}
        
    def check_metrics_folder(self):
        """Verifica se a pasta metrics/ existe."""
        if not self.metrics_dir.exists():
            return False
        return True
    
    def load_csv_file(self, filepath):
        """Carrega dados de um ficheiro CSV."""
        if not filepath.exists():
            return []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            return []
    
    def load_all_metrics(self):
        """Carrega todos os ficheiros de métricas."""
        for key, filepath in self.files.items():
            if key == 'summary':
                continue
            
            # Verifica se o ficheiro foi modificado
            if filepath.exists():
                mod_time = filepath.stat().st_mtime
                if key not in self.last_modified or mod_time > self.last_modified[key]:
                    self.data[key] = self.load_csv_file(filepath)
                    self.last_modified[key] = mod_time
        
        # Carrega summary separadamente
        if self.files['summary'].exists():
            rows = self.load_csv_file(self.files['summary'])
            self.summary_stats = {row.get('metric', ''): row for row in rows}
    
    def calculate_stats(self, values):
        """Calcula estatísticas básicas de uma lista de valores."""
        if not values:
            return {'count': 0, 'avg': 0, 'min': 0, 'max': 0}
        
        float_values = [float(v) for v in values if v]
        if not float_values:
            return {'count': 0, 'avg': 0, 'min': 0, 'max': 0}
        
        return {
            'count': len(float_values),
            'avg': sum(float_values) / len(float_values),
            'min': min(float_values),
            'max': max(float_values)
        }
    
    def build_rich_dashboard(self):
        """Constrói o dashboard usando Rich com tabela unificada."""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        # Header
        header_text = Text("📊 Dashboard de Métricas - Simulação de Tráfego SPADE", style="bold cyan")
        layout["header"].update(Panel(Align.center(header_text), border_style="cyan"))
        
        # Coletar todos os vehicle_ids únicos de todos os CSVs
        all_vehicles = set()
        for csv_name in ['recalc_latency', 'route_costs', 'semaphore_penalty', 'traffic_penalty']:
            for row in self.data.get(csv_name, []):
                vid = row.get('vehicle_id', '')
                if vid:
                    all_vehicles.add(vid)
        
        # Separar por categorias e ordenar
        v0_vehicles = sorted([v for v in all_vehicles if v == 'v0'])
        normal_vehicles = sorted([v for v in all_vehicles if v.startswith('v') and v != 'v0'])
        ambulance_vehicles = sorted([v for v in all_vehicles if v.startswith('AMB')])
        
        # Criar tabela principal
        table = Table(title="🚗 Métricas por Veículo (Acumuladas)", border_style="cyan", show_header=True, expand=True)
        table.add_column("Veículo", style="bold yellow", width=12)
        table.add_column("Tipo", style="cyan", width=11)
        table.add_column("Recálc.", justify="right", style="green", width=8)
        table.add_column("Lat. Méd", justify="right", style="magenta", width=10)
        table.add_column("Custo Orig", justify="right", style="blue", width=11)
        table.add_column("Custo Rec", justify="right", style="blue", width=11)
        table.add_column("Desvio", justify="right", style="red", width=9)
        table.add_column("Pen. Sem", justify="right", style="yellow", width=10)
        table.add_column("Pen. Tráf", justify="right", style="yellow", width=10)
        
        # Acumular dados por veículo
        if not hasattr(self, '_accumulated_data'):
            self._accumulated_data = {}
        
        # Atualizar dados acumulados para cada veículo
        for vid in all_vehicles:
            if vid not in self._accumulated_data:
                self._accumulated_data[vid] = {
                    'latency': [],
                    'route': [],
                    'sem': [],
                    'traffic': []
                }
            
            # Latência - verificar duplicatas por valor
            for row in self.data.get('recalc_latency', []):
                if row.get('vehicle_id') == vid:
                    lat = row.get('latency_ms')
                    if lat and lat not in self._accumulated_data[vid]['latency']:
                        self._accumulated_data[vid]['latency'].append(lat)
            
            # Rotas - verificar duplicatas por par de valores
            for row in self.data.get('route_costs', []):
                if row.get('vehicle_id') == vid:
                    route_data = (row.get('original_cost'), row.get('new_cost'))
                    if route_data[0] and route_data not in self._accumulated_data[vid]['route']:
                        self._accumulated_data[vid]['route'].append(route_data)
            
            # Semáforo
            for row in self.data.get('semaphore_penalty', []):
                if row.get('vehicle_id') == vid:
                    pen = row.get('penalty_cost')
                    if pen and pen not in self._accumulated_data[vid]['sem']:
                        self._accumulated_data[vid]['sem'].append(pen)
            
            # Tráfego
            for row in self.data.get('traffic_penalty', []):
                if row.get('vehicle_id') == vid:
                    pen = row.get('penalty_cost')
                    if pen and pen not in self._accumulated_data[vid]['traffic']:
                        self._accumulated_data[vid]['traffic'].append(pen)
        
        # Adicionar linhas para cada veículo organizado por categoria
        for vehicles, tipo, emoji in [(v0_vehicles, "Journey", "🟣"), (normal_vehicles, "Normal", "🔵"), (ambulance_vehicles, "Ambulância", "🔴")]:
            for vid in vehicles:
                data = self._accumulated_data.get(vid, {})
                
                # Calcular estatísticas
                latencies = [float(x) for x in data.get('latency', []) if x]
                routes = data.get('route', [])
                sems = [float(x) for x in data.get('sem', []) if x]
                traffics = [float(x) for x in data.get('traffic', []) if x]
                
                lat_avg = sum(latencies) / len(latencies) if latencies else 0
                recalc_count = len(latencies)
                
                orig_costs = [float(r[0]) for r in routes if r[0]]
                new_costs = [float(r[1]) for r in routes if r[1]]
                orig_avg = sum(orig_costs) / len(orig_costs) if orig_costs else 0
                new_avg = sum(new_costs) / len(new_costs) if new_costs else 0
                desvio = new_avg / orig_avg if orig_avg > 0 else 0
                
                sem_avg = sum(sems) / len(sems) if sems else 0
                traf_avg = sum(traffics) / len(traffics) if traffics else 0
                
                table.add_row(
                    f"{emoji} {vid}",
                    tipo,
                    str(recalc_count) if recalc_count > 0 else "-",
                    f"{lat_avg:.2f}ms" if lat_avg > 0 else "-",
                    f"{orig_avg:.1f}" if orig_avg > 0 else "-",
                    f"{new_avg:.1f}" if new_avg > 0 else "-",
                    f"{desvio:.2f}×" if desvio > 0 else "-",
                    f"{sem_avg:.1f}" if sem_avg > 0 else "-",
                    f"{traf_avg:.1f}" if traf_avg > 0 else "-"
                )
        
        if not all_vehicles:
            table.add_row("⏳", "Aguardando dados...", "-", "-", "-", "-", "-", "-", "-")
        
        layout["body"].update(Panel(table, border_style="cyan", title="📊 Todas as Métricas"))
        
        # Footer
        now = datetime.now().strftime("%H:%M:%S")
        footer_text = f"🔄 Última atualização: {now} | Pasta: {self.metrics_dir} | Ctrl+C para sair"
        layout["footer"].update(Panel(footer_text, border_style="dim"))
        
        return layout
    
    def build_basic_dashboard(self):
        """Constrói o dashboard em modo texto básico."""
        lines = []
        lines.append("=" * 100)
        lines.append("📊 DASHBOARD DE MÉTRICAS - Simulação de Tráfego SPADE".center(100))
            if row.get('vehicle_id') == 'v0':
                # Verificar se já existe (comparar valores)
                exists = any(r.get('latency_ms') == row.get('latency_ms') for r in self._v0_latency_accumulated)
                if not exists:
                    self._v0_latency_accumulated.append(row.copy())
        
        for row in self.data.get('route_costs', []):
            if row.get('vehicle_id') == 'v0':
                exists = any(r.get('original_cost') == row.get('original_cost') and 
                           r.get('new_cost') == row.get('new_cost') for r in self._v0_route_accumulated)
                if not exists:
                    self._v0_route_accumulated.append(row.copy())
        
        for row in self.data.get('semaphore_penalty', []):
            if row.get('vehicle_id') == 'v0':
                exists = any(r.get('penalty_cost') == row.get('penalty_cost') for r in self._v0_sem_accumulated)
                if not exists:
                    self._v0_sem_accumulated.append(row.copy())
        
        for row in self.data.get('traffic_penalty', []):
            if row.get('vehicle_id') == 'v0':
                exists = any(r.get('penalty_cost') == row.get('penalty_cost') for r in self._v0_traffic_accumulated)
                if not exists:
                    self._v0_traffic_accumulated.append(row.copy())
        
        if self._v0_latency_accumulated or self._v0_route_accumulated:
            table_v0 = Table(title="🟣 Journey Vehicle (v0 - Loop A↔B)", border_style="magenta", show_header=True)
            table_v0.add_column("Métrica", style="cyan")
            table_v0.add_column("Valor", justify="right", style="yellow")
            
            if self._v0_latency_accumulated:
                latencies = [float(row.get('latency_ms', '0')) for row in self._v0_latency_accumulated]
                stats = self.calculate_stats(latencies)
                table_v0.add_row("Latência Média", f"{stats['avg']:.2f} ms")
                table_v0.add_row("Latência Máx", f"{stats['max']:.2f} ms")
                table_v0.add_row("Recálculos", f"{stats['count']}")
            
            if self._v0_route_accumulated:
                costs_orig = [float(row.get('original_cost', '0')) for row in self._v0_route_accumulated]
                costs_new = [float(row.get('new_cost', '0')) for row in self._v0_route_accumulated]
                stats_orig = self.calculate_stats(costs_orig)
                stats_new = self.calculate_stats(costs_new)
                
                table_v0.add_row("─" * 15, "─" * 10)
                table_v0.add_row("Custo Original", f"{stats_orig['avg']:.1f}")
                table_v0.add_row("Custo Recalc.", f"{stats_new['avg']:.1f}")
                if stats_orig['avg'] > 0:
                    ratio = stats_new['avg'] / stats_orig['avg']
                    table_v0.add_row("Desvio Factor", f"{ratio:.2f}×")
                table_v0.add_row("Ciclos A↔B", f"{stats_orig['count']}")
            
            if self._v0_sem_accumulated:
                penalties = [float(row.get('penalty_cost', '0')) for row in self._v0_sem_accumulated]
                stats = self.calculate_stats(penalties)
                table_v0.add_row("─" * 15, "─" * 10)
                table_v0.add_row("Penaliz. Sem.", f"{stats['avg']:.1f}")
            
            if self._v0_traffic_accumulated:
                penalties = [float(row.get('penalty_cost', '0')) for row in self._v0_traffic_accumulated]
                stats = self.calculate_stats(penalties)
                table_v0.add_row("Penaliz. Tráf.", f"{stats['avg']:.1f}")
            
            left_tables.append(table_v0)
        else:
            left_tables.append(Panel("⏳ Aguardando dados do Journey Vehicle (v0)...\nPressione ESPAÇO na simulação para gerar bloqueios.", border_style="dim"))
        
        if left_tables:
            from rich.console import Group
            layout["left"].update(Panel(Group(*left_tables), border_style="magenta"))
        else:
            layout["left"].update(Panel("⏳ Aguardando dados...", border_style="dim"))
        
        # Coluna do meio: Veículo Normal (primeiro disponível)
        middle_tables = []
        
        # Detectar primeiro veículo normal com dados (re-escanear todos os CSVs)
        if not hasattr(self, '_normal_vehicle_id'):
            self._normal_vehicle_id = None
        
        # Buscar em TODOS os CSVs se ainda não encontramos
        if not self._normal_vehicle_id:
            all_vehicle_ids = set()
            # Coletar IDs de todos os CSVs
            for csv_name in ['recalc_latency', 'route_costs', 'semaphore_penalty', 'traffic_penalty']:
                for row in self.data.get(csv_name, []):
                    vid = row.get('vehicle_id', '')
                    if vid.startswith('v') and vid != 'v0' and not vid.startswith('AMB'):
                        all_vehicle_ids.add(vid)
            
            # Pegar o primeiro (ordem alfabética)
            if all_vehicle_ids:
                self._normal_vehicle_id = sorted(all_vehicle_ids)[0]
        
        # Acumular dados do veículo normal detectado
        if not hasattr(self, '_normal_latency_accumulated'):
            self._normal_latency_accumulated = []
            self._normal_route_accumulated = []
            self._normal_sem_accumulated = []
            self._normal_traffic_accumulated = []
        
        if self._normal_vehicle_id:
            for row in self.data.get('recalc_latency', []):
                if row.get('vehicle_id') == self._normal_vehicle_id:
                    exists = any(r.get('latency_ms') == row.get('latency_ms') for r in self._normal_latency_accumulated)
                    if not exists:
                        self._normal_latency_accumulated.append(row.copy())
            
            for row in self.data.get('route_costs', []):
                if row.get('vehicle_id') == self._normal_vehicle_id:
                    exists = any(r.get('original_cost') == row.get('original_cost') and 
                               r.get('new_cost') == row.get('new_cost') for r in self._normal_route_accumulated)
                    if not exists:
                        self._normal_route_accumulated.append(row.copy())
            
            for row in self.data.get('semaphore_penalty', []):
                if row.get('vehicle_id') == self._normal_vehicle_id:
                    exists = any(r.get('penalty_cost') == row.get('penalty_cost') for r in self._normal_sem_accumulated)
                    if not exists:
                        self._normal_sem_accumulated.append(row.copy())
            
            for row in self.data.get('traffic_penalty', []):
                if row.get('vehicle_id') == self._normal_vehicle_id:
                    exists = any(r.get('penalty_cost') == row.get('penalty_cost') for r in self._normal_traffic_accumulated)
                    if not exists:
                        self._normal_traffic_accumulated.append(row.copy())
        
        if self._normal_latency_accumulated or self._normal_route_accumulated:
            table_normal = Table(title=f"🔵 Veículo Normal ({self._normal_vehicle_id} - Representante)", border_style="blue", show_header=True)
            table_normal.add_column("Métrica", style="cyan")
            table_normal.add_column("Valor", justify="right", style="yellow")
            
            if self._normal_latency_accumulated:
                latencies = [float(row.get('latency_ms', '0')) for row in self._normal_latency_accumulated]
                stats = self.calculate_stats(latencies)
                table_normal.add_row("Latência Média", f"{stats['avg']:.2f} ms")
                table_normal.add_row("Latência Máx", f"{stats['max']:.2f} ms")
                table_normal.add_row("Recálculos", f"{stats['count']}")
            
            if self._normal_route_accumulated:
                costs_orig = [float(row.get('original_cost', '0')) for row in self._normal_route_accumulated]
                costs_new = [float(row.get('new_cost', '0')) for row in self._normal_route_accumulated]
                stats_orig = self.calculate_stats(costs_orig)
                stats_new = self.calculate_stats(costs_new)
                
                table_normal.add_row("─" * 15, "─" * 10)
                table_normal.add_row("Custo Original", f"{stats_orig['avg']:.1f}")
                table_normal.add_row("Custo Recalc.", f"{stats_new['avg']:.1f}")
                if stats_orig['avg'] > 0:
                    ratio = stats_new['avg'] / stats_orig['avg']
                    table_normal.add_row("Desvio Factor", f"{ratio:.2f}×")
                table_normal.add_row("Rotas Calc.", f"{stats_orig['count']}")
            
            if self._normal_sem_accumulated:
                penalties = [float(row.get('penalty_cost', '0')) for row in self._normal_sem_accumulated]
                stats = self.calculate_stats(penalties)
                table_normal.add_row("─" * 15, "─" * 10)
                table_normal.add_row("Penaliz. Sem.", f"{stats['avg']:.1f}")
            
            if self._normal_traffic_accumulated:
                penalties = [float(row.get('penalty_cost', '0')) for row in self._normal_traffic_accumulated]
                stats = self.calculate_stats(penalties)
                table_normal.add_row("Penaliz. Tráf.", f"{stats['avg']:.1f}")
            
            middle_tables.append(table_normal)
        else:
            msg = "⏳ Aguardando dados de Veículo Normal..."
            if self._normal_vehicle_id:
                msg = f"⏳ Aguardando dados de {self._normal_vehicle_id}..."
            msg += "\nPressione ESPAÇO na simulação para gerar bloqueios."
            middle_tables.append(Panel(msg, border_style="dim"))
        
        if middle_tables:
            from rich.console import Group
            layout["middle"].update(Panel(Group(*middle_tables), border_style="blue"))
        else:
            layout["middle"].update(Panel("⏳ Aguardando dados...", border_style="dim"))
        
        # Coluna direita: Ambulâncias (primeira disponível)
        right_tables = []
        
        # Detectar primeira ambulância com dados (re-escanear todos os CSVs)
        if not hasattr(self, '_amb_vehicle_id'):
            self._amb_vehicle_id = None
        
        # Buscar em TODOS os CSVs se ainda não encontramos
        if not self._amb_vehicle_id:
            all_amb_ids = set()
            # Coletar IDs de todos os CSVs
            for csv_name in ['recalc_latency', 'route_costs', 'semaphore_penalty', 'traffic_penalty']:
                for row in self.data.get(csv_name, []):
                    vid = row.get('vehicle_id', '')
                    if vid.startswith('AMB'):
                        all_amb_ids.add(vid)
            
            # Pegar o primeiro (ordem alfabética)
            if all_amb_ids:
                self._amb_vehicle_id = sorted(all_amb_ids)[0]
        
        # Acumular dados da ambulância detectada
        if not hasattr(self, '_amb_latency_accumulated'):
            self._amb_latency_accumulated = []
            self._amb_route_accumulated = []
            self._amb_sem_accumulated = []
            self._amb_traffic_accumulated = []
        
        if self._amb_vehicle_id:
            for row in self.data.get('recalc_latency', []):
                if row.get('vehicle_id') == self._amb_vehicle_id:
                    exists = any(r.get('latency_ms') == row.get('latency_ms') for r in self._amb_latency_accumulated)
                    if not exists:
                        self._amb_latency_accumulated.append(row.copy())
            
            for row in self.data.get('route_costs', []):
                if row.get('vehicle_id') == self._amb_vehicle_id:
                    exists = any(r.get('original_cost') == row.get('original_cost') and 
                               r.get('new_cost') == row.get('new_cost') for r in self._amb_route_accumulated)
                    if not exists:
                        self._amb_route_accumulated.append(row.copy())
            
            for row in self.data.get('semaphore_penalty', []):
                if row.get('vehicle_id') == self._amb_vehicle_id:
                    exists = any(r.get('penalty_cost') == row.get('penalty_cost') for r in self._amb_sem_accumulated)
                    if not exists:
                        self._amb_sem_accumulated.append(row.copy())
            
            for row in self.data.get('traffic_penalty', []):
                if row.get('vehicle_id') == self._amb_vehicle_id:
                    exists = any(r.get('penalty_cost') == row.get('penalty_cost') for r in self._amb_traffic_accumulated)
                    if not exists:
                        self._amb_traffic_accumulated.append(row.copy())
        
        if self._amb_latency_accumulated or self._amb_route_accumulated:
            table_amb = Table(title=f"🚑 Ambulância ({self._amb_vehicle_id} - Representante)", border_style="red", show_header=True)
            table_amb.add_column("Métrica", style="cyan")
            table_amb.add_column("Valor", justify="right", style="yellow")
            
            if self._amb_latency_accumulated:
                latencies = [float(row.get('latency_ms', '0')) for row in self._amb_latency_accumulated]
                stats = self.calculate_stats(latencies)
                table_amb.add_row("Latência Média", f"{stats['avg']:.2f} ms")
                table_amb.add_row("Latência Máx", f"{stats['max']:.2f} ms")
                table_amb.add_row("Recálculos", f"{stats['count']}")
            
            if self._amb_route_accumulated:
                costs_orig = [float(row.get('original_cost', '0')) for row in self._amb_route_accumulated]
                costs_new = [float(row.get('new_cost', '0')) for row in self._amb_route_accumulated]
                stats_orig = self.calculate_stats(costs_orig)
                stats_new = self.calculate_stats(costs_new)
                
                table_amb.add_row("─" * 15, "─" * 10)
                table_amb.add_row("Custo Original", f"{stats_orig['avg']:.1f}")
                table_amb.add_row("Custo Recalc.", f"{stats_new['avg']:.1f}")
                if stats_orig['avg'] > 0:
                    ratio = stats_new['avg'] / stats_orig['avg']
                    table_amb.add_row("Desvio Factor", f"{ratio:.2f}×")
                table_amb.add_row("Rotas Emerg.", f"{stats_orig['count']}")
            
            if self._amb_sem_accumulated:
                penalties = [float(row.get('penalty_cost', '0')) for row in self._amb_sem_accumulated]
                stats = self.calculate_stats(penalties)
                table_amb.add_row("─" * 15, "─" * 10)
                table_amb.add_row("Penaliz. Sem.", f"{stats['avg']:.1f}")
            
            if self._amb_traffic_accumulated:
                penalties = [float(row.get('penalty_cost', '0')) for row in self._amb_traffic_accumulated]
                stats = self.calculate_stats(penalties)
                table_amb.add_row("Penaliz. Tráf.", f"{stats['avg']:.1f}")
            
            right_tables.append(table_amb)
        else:
            msg = "⏳ Aguardando dados de Ambulância..."
            if self._amb_vehicle_id:
                msg = f"⏳ Aguardando dados de {self._amb_vehicle_id}..."
            msg += "\nPressione ESPAÇO na simulação para gerar bloqueios."
            right_tables.append(Panel(msg, border_style="dim"))
        
        if right_tables:
            from rich.console import Group
            layout["right"].update(Panel(Group(*right_tables), border_style="red"))
        else:
            layout["right"].update(Panel("⏳ Aguardando dados...", border_style="dim"))
        
        # Footer
        now = datetime.now().strftime("%H:%M:%S")
        footer_text = f"🔄 Última atualização: {now} | Pasta: {self.metrics_dir} | Ctrl+C para sair"
        layout["footer"].update(Panel(footer_text, border_style="dim"))
        
        return layout
    
    def build_basic_dashboard(self):
        """Constrói o dashboard em modo texto básico."""
        lines = []
        lines.append("=" * 100)
        lines.append("📊 DASHBOARD DE MÉTRICAS - Simulação de Tráfego SPADE".center(100))
        lines.append("=" * 100)
        lines.append("")
        
        # Journey Vehicle (v0)
        v0_latency = [row for row in self.data.get('recalc_latency', []) if row.get('vehicle_id') == 'v0']
        v0_route = [row for row in self.data.get('route_costs', []) if row.get('vehicle_id') == 'v0']
        
        if v0_latency or v0_route:
            lines.append("🟣 JOURNEY VEHICLE (v0 - Loop A↔B)")
            if v0_latency:
                latencies = [float(row.get('latency_ms', '0')) for row in v0_latency]
                stats = self.calculate_stats(latencies)
                lines.append(f"   Latência: Média={stats['avg']:.2f}ms | Máx={stats['max']:.2f}ms | Recálculos={stats['count']}")
            if v0_route:
                costs_orig = [float(row.get('original_cost', '0')) for row in v0_route]
                costs_new = [float(row.get('new_cost', '0')) for row in v0_route]
                stats_orig = self.calculate_stats(costs_orig)
                stats_new = self.calculate_stats(costs_new)
                ratio = stats_new['avg'] / stats_orig['avg'] if stats_orig['avg'] > 0 else 0
                lines.append(f"   Custos: Original={stats_orig['avg']:.1f} | Recalc={stats_new['avg']:.1f} | Desvio={ratio:.2f}× | Ciclos={stats_orig['count']}")
            lines.append("")
        
        # Veículos Normais (v1-v10)
        normal_latency = [row for row in self.data.get('recalc_latency', []) 
                         if row.get('vehicle_id', '').startswith('v') and row.get('vehicle_id') not in ['v0']]
        normal_route = [row for row in self.data.get('route_costs', []) 
                       if row.get('vehicle_id', '').startswith('v') and row.get('vehicle_id') not in ['v0']]
        
        if normal_latency or normal_route:
            lines.append("🔵 VEÍCULOS NORMAIS (v1-v10)")
            if normal_latency:
                latencies = [float(row.get('latency_ms', '0')) for row in normal_latency]
                stats = self.calculate_stats(latencies)
                lines.append(f"   Latência: Média={stats['avg']:.2f}ms | Máx={stats['max']:.2f}ms | Recálculos={stats['count']}")
            if normal_route:
                costs_orig = [float(row.get('original_cost', '0')) for row in normal_route]
                costs_new = [float(row.get('new_cost', '0')) for row in normal_route]
                stats_orig = self.calculate_stats(costs_orig)
                stats_new = self.calculate_stats(costs_new)
                ratio = stats_new['avg'] / stats_orig['avg'] if stats_orig['avg'] > 0 else 0
                lines.append(f"   Custos: Original={stats_orig['avg']:.1f} | Recalc={stats_new['avg']:.1f} | Desvio={ratio:.2f}× | Rotas={stats_orig['count']}")
            lines.append("")
        
        # Ambulâncias (AMB0-AMB3)
        amb_latency = [row for row in self.data.get('recalc_latency', []) 
                      if row.get('vehicle_id', '').startswith('AMB')]
        amb_route = [row for row in self.data.get('route_costs', []) 
                    if row.get('vehicle_id', '').startswith('AMB')]
        
        if amb_latency or amb_route:
            lines.append("🚑 AMBULÂNCIAS (AMB0-AMB3)")
            if amb_latency:
                latencies = [float(row.get('latency_ms', '0')) for row in amb_latency]
                stats = self.calculate_stats(latencies)
                lines.append(f"   Latência: Média={stats['avg']:.2f}ms | Máx={stats['max']:.2f}ms | Recálculos={stats['count']}")
            if amb_route:
                costs_orig = [float(row.get('original_cost', '0')) for row in amb_route]
                costs_new = [float(row.get('new_cost', '0')) for row in amb_route]
                stats_orig = self.calculate_stats(costs_orig)
                stats_new = self.calculate_stats(costs_new)
                ratio = stats_new['avg'] / stats_orig['avg'] if stats_orig['avg'] > 0 else 0
                lines.append(f"   Custos: Original={stats_orig['avg']:.1f} | Recalc={stats_new['avg']:.1f} | Desvio={ratio:.2f}× | Rotas={stats_orig['count']}")
            lines.append("")
        
        if not any([v0_latency, v0_route, normal_latency, normal_route, amb_latency, amb_route]):
            lines.append("⏳ Aguardando dados das métricas...")
            lines.append(f"   Pasta monitorizada: {self.metrics_dir}")
            lines.append("   Pressione ESPAÇO na simulação para ativar bloqueios e gerar métricas")
            lines.append("")
        
        # Footer
        now = datetime.now().strftime("%H:%M:%S")
        lines.append("-" * 100)
        lines.append(f"🔄 Última atualização: {now} | Ctrl+C para sair")
        lines.append("=" * 100)
        
        return "\n".join(lines)
    
    def run_rich(self):
        """Executa o dashboard com Rich (modo avançado)."""
        try:
            with Live(self.build_rich_dashboard(), refresh_per_second=1, screen=True) as live:
                while True:
                    time.sleep(self.refresh_interval)
                    self.load_all_metrics()
                    live.update(self.build_rich_dashboard())
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Dashboard encerrado pelo utilizador.[/yellow]")
    
    def run_basic(self):
        """Executa o dashboard em modo texto básico."""
        try:
            while True:
                # Limpa o ecrã (cross-platform)
                os.system('clear' if os.name == 'posix' else 'cls')
                
                self.load_all_metrics()
                print(self.build_basic_dashboard())
                
                time.sleep(self.refresh_interval)
        except KeyboardInterrupt:
            print("\n⚠️  Dashboard encerrado pelo utilizador.")
    
    def run(self):
        """Executa o dashboard no modo apropriado."""
        if not self.check_metrics_folder():
            print(f"❌ Pasta '{self.metrics_dir}' não encontrada.")
            print(f"   Certifique-se de que a simulação está a gerar métricas.")
            print(f"   Execute: python live_dynamic_spade.py")
            return
        
        print(f"🚀 A iniciar dashboard de métricas...")
        print(f"📂 Pasta: {self.metrics_dir.absolute()}")
        print(f"🔄 Intervalo de atualização: {self.refresh_interval}s")
        print()
        
        if RICH_AVAILABLE:
            self.run_rich()
        else:
            self.run_basic()


def main():
    parser = argparse.ArgumentParser(
        description='Dashboard de métricas em tempo real para simulação de tráfego SPADE'
    )
    parser.add_argument(
        '--refresh',
        type=float,
        default=2.0,
        help='Intervalo de atualização em segundos (padrão: 2.0)'
    )
    parser.add_argument(
        '--metrics-dir',
        type=str,
        default='metrics',
        help='Pasta com os ficheiros CSV de métricas (padrão: metrics)'
    )
    
    args = parser.parse_args()
    
    dashboard = MetricsDashboard(
        metrics_dir=args.metrics_dir,
        refresh_interval=args.refresh
    )
    dashboard.run()


if __name__ == '__main__':
    main()
