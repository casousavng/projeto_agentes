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
    
