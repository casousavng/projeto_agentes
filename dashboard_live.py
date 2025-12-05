#!/usr/bin/env python3
"""
Dashboard de Métricas em Tempo Real - Recebe dados via XMPP diretamente dos agentes
Sem dependência de CSVs.

Uso:
    python dashboard_live.py [--refresh SECONDS]
"""

import asyncio
import json
import argparse
from datetime import datetime
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

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
    exit(1)


class DashboardAgent(Agent):
    """Agente que recebe métricas em tempo real via XMPP."""
    
    def __init__(self, jid, password, refresh_interval=1.0):
        super().__init__(jid, password)
        self.refresh_interval = refresh_interval
        self.console = Console()
        
        # Estrutura de dados acumulados por veículo
        self._accumulated_data = {}
        
        # Definir TODOS os veículos esperados
        self.all_vehicles = ['v0'] + [f'v{i}' for i in range(1, 11)] + [f'AMB{i}' for i in range(4)]
        
        # Inicializar estrutura
        for vid in self.all_vehicles:
            self._accumulated_data[vid] = {
                'latency': [],
                'route': [],
                'sem': [],
                'traffic': []
            }
    
    class ReceiveMetricsBehaviour(CyclicBehaviour):
        """Recebe métricas dos veículos via XMPP."""
        
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                try:
                    data = json.loads(msg.body)
                    msg_type = data.get('type')
                    vid = data.get('vehicle_id')
                    
                    # print(f"📨 Recebida mensagem: {msg_type} de {vid}")  # DEBUG
                    
                    if vid not in self.agent.all_vehicles:
                        # print(f"⚠️ Veículo {vid} não reconhecido")  # DEBUG
                        return
                    
                    if msg_type == 'metric_latency':
                        lat = data.get('latency_ms')
                        if lat and lat not in self.agent._accumulated_data[vid]['latency']:
                            self.agent._accumulated_data[vid]['latency'].append(lat)
                            # print(f"✅ {vid}: Latência adicionada ({lat:.2f}ms)")  # DEBUG
                    
                    elif msg_type == 'metric_route':
                        orig = data.get('original_cost')
                        rec = data.get('recalculated_cost')
                        route_data = (orig, rec)
                        if orig and route_data not in self.agent._accumulated_data[vid]['route']:
                            self.agent._accumulated_data[vid]['route'].append(route_data)
                            # print(f"✅ {vid}: Rota adicionada (orig={orig:.1f}, rec={rec:.1f})")  # DEBUG
                    
                    elif msg_type == 'metric_semaphore':
                        pen = data.get('penalty')
                        if pen is not None and pen not in self.agent._accumulated_data[vid]['sem']:
                            self.agent._accumulated_data[vid]['sem'].append(pen)
                            # print(f"✅ {vid}: Semáforo adicionado (pen={pen:.1f})")  # DEBUG
                    
                    elif msg_type == 'metric_traffic':
                        pen = data.get('penalty')
                        if pen is not None and pen not in self.agent._accumulated_data[vid]['traffic']:
                            self.agent._accumulated_data[vid]['traffic'].append(pen)
                            # print(f"✅ {vid}: Tráfego adicionado (pen={pen:.1f})")  # DEBUG
                
                except Exception as e:
                    print(f"❌ Erro ao processar mensagem: {e}")
    
    def build_dashboard(self):
        """Constrói o dashboard usando Rich."""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        # Header
        header_text = Text("📊 Dashboard de Métricas LIVE - Simulação de Tráfego SPADE", style="bold cyan")
        layout["header"].update(Panel(Align.center(header_text), border_style="cyan"))
        
        # Criar tabela principal
        table = Table(title="🚗 Métricas por Veículo (Tempo Real)", border_style="cyan", show_header=True, expand=True)
        table.add_column("Veículo", style="bold yellow", width=12)
        table.add_column("Tipo", style="cyan", width=11)
        table.add_column("Recálc.", justify="right", style="green", width=8)
        table.add_column("Lat. Méd", justify="right", style="magenta", width=10)
        table.add_column("Custo Orig", justify="right", style="blue", width=11)
        table.add_column("Custo Rec", justify="right", style="blue", width=11)
        table.add_column("Desvio", justify="right", style="red", width=9)
        table.add_column("Pen. Sem", justify="right", style="yellow", width=10)
        table.add_column("Pen. Tráf", justify="right", style="yellow", width=10)
        
        # Tipo por veículo
        tipo_map = {
            'v0': ('A→B', '🟣'),
            **{f'v{i}': ('Normal', '🔵') for i in range(1, 11)},
            **{f'AMB{i}': ('Ambulância', '🔴') for i in range(4)}
        }
        
        # Adicionar linhas
        for vid in self.all_vehicles:
            tipo, emoji = tipo_map.get(vid, ('?', '⚪'))
            data = self._accumulated_data.get(vid, {})
            
            # Calcular estatísticas
            latencies = [float(x) for x in data.get('latency', []) if x is not None]
            routes = data.get('route', [])
            sems = [float(x) for x in data.get('sem', []) if x is not None]
            traffics = [float(x) for x in data.get('traffic', []) if x is not None]
            
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
        
        # Combinar tabela e legenda
        from rich.console import Group
        layout["body"].update(Group(
            Panel(table, border_style="cyan", title="📊 Todas as Métricas"),
            legend_panel
        ))
        
        # Footer
        now = datetime.now().strftime("%H:%M:%S")
        footer_text = f"🔄 Última atualização: {now} | Dados via XMPP | Pressione ESPAÇO na simulação | Ctrl+C para sair"
        layout["footer"].update(Panel(footer_text, border_style="dim"))
        
        return layout
    
    async def setup(self):
        """Configuração inicial do agente."""
        print("🚀 Dashboard Agent iniciando...")
        self.add_behaviour(self.ReceiveMetricsBehaviour())
        print("✅ Dashboard Agent pronto para receber métricas via XMPP")


async def main(refresh_interval):
    """Função principal."""
    # Criar agente dashboard
    dashboard = DashboardAgent("dashboard@localhost", "dashboard", refresh_interval)
    
    await dashboard.start()
    print("✅ Dashboard conectado ao servidor XMPP")
    print(f"📡 Aguardando métricas dos veículos...\n")
    
    try:
        with Live(dashboard.build_dashboard(), refresh_per_second=1/refresh_interval, console=dashboard.console) as live:
            while dashboard.is_alive():
                await asyncio.sleep(refresh_interval)
                live.update(dashboard.build_dashboard())
    except KeyboardInterrupt:
        print("\n[yellow]Dashboard encerrado pelo utilizador.[/yellow]")
    finally:
        await dashboard.stop()
        print("✅ Dashboard desconectado")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Dashboard de métricas LIVE via XMPP"
    )
    parser.add_argument(
        '--refresh',
        type=float,
        default=1.0,
        help='Intervalo de atualização em segundos (padrão: 1.0)'
    )
    
    args = parser.parse_args()
    
    if not RICH_AVAILABLE:
        print("❌ Biblioteca 'rich' é necessária. Instale com: pip install rich")
        exit(1)
    
    # Executar
    import spade
    spade.run(main(args.refresh))
