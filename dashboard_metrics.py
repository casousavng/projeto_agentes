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
        self._accumulated_data = {}
        
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
        
        # Definir TODOS os veículos esperados (estrutura fixa)
        v0_vehicles = ['v0']
        normal_vehicles = ['v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'v7', 'v8', 'v9', 'v10']
        ambulance_vehicles = ['AMB0', 'AMB1', 'AMB2', 'AMB3']
        
        all_vehicles_expected = v0_vehicles + normal_vehicles + ambulance_vehicles
        
        # Inicializar estrutura de dados acumulados para TODOS os veículos
        for vid in all_vehicles_expected:
            if vid not in self._accumulated_data:
                self._accumulated_data[vid] = {
                    'latency': [],
                    'route': [],
                    'sem': [],
                    'traffic': []
                }
        
        # Atualizar dados acumulados com novos dados dos CSVs
        # Latência
        for row in self.data.get('recalc_latency', []):
            vid = row.get('vehicle_id', '')
            if vid in all_vehicles_expected:
                lat = row.get('latency_ms')
                if lat and lat not in self._accumulated_data[vid]['latency']:
                    self._accumulated_data[vid]['latency'].append(lat)
        
        # Rotas
        for row in self.data.get('route_costs', []):
            vid = row.get('vehicle_id', '')
            if vid in all_vehicles_expected:
                route_data = (row.get('original_cost'), row.get('new_cost'))
                if route_data[0] and route_data not in self._accumulated_data[vid]['route']:
                    self._accumulated_data[vid]['route'].append(route_data)
        
        # Semáforo
        for row in self.data.get('semaphore_penalty', []):
            vid = row.get('vehicle_id', '')
            if vid in all_vehicles_expected:
                pen = row.get('penalty_cost')
                if pen and pen not in self._accumulated_data[vid]['sem']:
                    self._accumulated_data[vid]['sem'].append(pen)
        
        # Tráfego
        for row in self.data.get('traffic_penalty', []):
            vid = row.get('vehicle_id', '')
            if vid in all_vehicles_expected:
                pen = row.get('penalty_cost')
                if pen and pen not in self._accumulated_data[vid]['traffic']:
                    self._accumulated_data[vid]['traffic'].append(pen)
        
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
        
        # Adicionar linhas para TODOS os veículos (estrutura fixa)
        tipo_map = {
            'v0': ('A→B', '🟣'),
            **{f'v{i}': ('Normal', '🔵') for i in range(1, 11)},
            **{f'AMB{i}': ('Ambulância', '🔴') for i in range(4)}
        }
        
        for vid in all_vehicles_expected:
            tipo, emoji = tipo_map.get(vid, ('?', '⚪'))
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
            
            # Verificar se tem dados
            has_data = (recalc_count > 0 or len(routes) > 0 or len(sems) > 0 or len(traffics) > 0)
            
            if has_data:
                table.add_row(
                    f"{emoji} {vid}",
                    tipo,
                    str(recalc_count) if recalc_count > 0 else "-",
                    f"{lat_avg:.2f}ms" if lat_avg > 0 else "-",
                    f"{orig_avg:.1f}" if orig_avg > 0 else "-",
                    f"{new_avg:.1f}" if new_avg > 0 else "-",
                    f"{desvio:.2f}×" if desvio > 0 else "-",
                    f"{sem_avg:.1f}" if len(sems) > 0 else "-",
                    f"{traf_avg:.1f}" if len(traffics) > 0 else "-"
                )
            else:
                # Linha vazia aguardando dados
                table.add_row(
                    f"⚪ {vid}",
                    tipo,
                    "-", "-", "-", "-", "-", "-", "-",
                    style="dim"
                )
        
        layout["body"].update(Panel(table, border_style="cyan", title="📊 Todas as Métricas"))
        
        # Legenda das colunas
        legend = Table.grid(padding=(0, 2))
        legend.add_column(style="bold cyan", justify="right")
        legend.add_column(style="white")
        
        legend.add_row("Recálc.:", "Número de recálculos de rota executados")
        legend.add_row("Lat. Méd:", "Latência média do recálculo A* em milissegundos")
        legend.add_row("Custo Orig:", "Custo médio da rota original (antes de bloqueios)")
        legend.add_row("Custo Rec:", "Custo médio da rota recalculada (após bloqueios)")
        legend.add_row("Desvio:", "Fator de desvio (Custo Rec ÷ Custo Orig)")
        legend.add_row("Pen. Sem:", "Penalização média por semáforos vermelhos")
        legend.add_row("Pen. Tráf:", "Penalização média por tráfego reportado")
        
        legend_panel = Panel(
            legend,
            title="📖 Legenda das Colunas",
            border_style="dim",
            padding=(0, 1)
        )
        
        # Combinar tabela e legenda no body
        from rich.console import Group
        layout["body"].update(Group(
            Panel(table, border_style="cyan", title="📊 Todas as Métricas"),
            legend_panel
        ))
        
        # Footer
        now = datetime.now().strftime("%H:%M:%S")
        footer_text = f"🔄 Última atualização: {now} | Pasta: {self.metrics_dir} | Pressione ESPAÇO na simulação | Ctrl+C para sair"
        layout["footer"].update(Panel(footer_text, border_style="dim"))
        
        return layout
    
    def run_rich(self):
        """Executa o dashboard usando Rich (modo avançado)."""
        try:
            with Live(self.build_rich_dashboard(), refresh_per_second=1/self.refresh_interval, console=self.console) as live:
                while True:
                    time.sleep(self.refresh_interval)
                    self.load_all_metrics()
                    live.update(self.build_rich_dashboard())
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Dashboard encerrado pelo utilizador.[/yellow]")
    
    def run(self):
        """Executa o dashboard (seleciona modo automaticamente)."""
        if not self.check_metrics_folder():
            print(f"❌ Pasta '{self.metrics_dir}' não encontrada!")
            print(f"Certifique-se de que a simulação está a correr e a gerar métricas.")
            sys.exit(1)
        
        if RICH_AVAILABLE:
            print("✅ Iniciando dashboard em modo avançado (Rich)...")
            print(f"📂 Monitorizando: {self.metrics_dir.absolute()}")
            print(f"🔄 Atualização a cada {self.refresh_interval}s")
            print("⏳ Aguardando dados dos CSVs...\n")
            self.run_rich()
        else:
            print("❌ Modo básico não implementado. Instale 'rich': pip install rich")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Dashboard de métricas em tempo real para simulação de tráfego SPADE"
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
        help='Diretório com os ficheiros CSV de métricas (padrão: metrics)'
    )
    
    args = parser.parse_args()
    
    dashboard = MetricsDashboard(
        metrics_dir=args.metrics_dir,
        refresh_interval=args.refresh
    )
    dashboard.run()


if __name__ == "__main__":
    main()
