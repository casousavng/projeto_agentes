"""
Data Collector - Armazena dados da simulação em SQLite
Coleta dados dos agentes SPADE via TraCI e persiste em BD
"""
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any
import os


class SimulationDataCollector:
    """Coleta e armazena dados da simulação em SQLite"""
    
    def __init__(self, db_path: str = "simulation_data.db"):
        self.db_path = db_path
        self.conn = None
        # Não inicializa aqui - será feito quando necessário
        # Isso permite que cada thread crie sua própria conexão
    
    def _get_connection(self):
        """Obtém conexão SQLite (thread-safe)"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return self.conn
    
    def initialize_database(self):
        """Cria as tabelas necessárias"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Tabela de snapshots da simulação (um registro por step)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS simulation_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                step INTEGER NOT NULL,
                simulation_time REAL NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        # Tabela de veículos (estado em cada step)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id INTEGER NOT NULL,
                vehicle_id TEXT NOT NULL,
                vehicle_type TEXT NOT NULL,
                position_x REAL NOT NULL,
                position_y REAL NOT NULL,
                angle REAL NOT NULL,
                speed REAL NOT NULL,
                edge_id TEXT,
                lane_index INTEGER,
                route_edges TEXT,
                color TEXT,
                FOREIGN KEY (snapshot_id) REFERENCES simulation_snapshots(id)
            )
        """)
        
        # Tabela de semáforos (estado em cada step)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS traffic_lights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id INTEGER NOT NULL,
                tl_id TEXT NOT NULL,
                position_x REAL NOT NULL,
                position_y REAL NOT NULL,
                state TEXT NOT NULL,
                phase_duration REAL,
                FOREIGN KEY (snapshot_id) REFERENCES simulation_snapshots(id)
            )
        """)
        
        # Tabela de topologia da rede (carregada uma vez)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS network_topology (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                nodes TEXT NOT NULL,
                edges TEXT NOT NULL
            )
        """)
        
        # Tabela de estatísticas (agregadas por step)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id INTEGER NOT NULL,
                total_vehicles INTEGER NOT NULL,
                total_waiting INTEGER NOT NULL,
                avg_speed REAL NOT NULL,
                avg_waiting_time REAL NOT NULL,
                FOREIGN KEY (snapshot_id) REFERENCES simulation_snapshots(id)
            )
        """)
        
        # Índices para performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshot_step ON simulation_snapshots(step)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_vehicle_snapshot ON vehicles(snapshot_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tl_snapshot ON traffic_lights(snapshot_id)")
        
        conn.commit()
        print(f"✅ Database initialized: {self.db_path}")
    
    def save_network_topology(self, nodes: List[Dict], edges: List[Dict]):
        """Salva a topologia da rede (executado uma vez)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Limpa topologia anterior
        cursor.execute("DELETE FROM network_topology")
        
        cursor.execute("""
            INSERT INTO network_topology (created_at, nodes, edges)
            VALUES (?, ?, ?)
        """, (
            datetime.now().isoformat(),
            json.dumps(nodes),
            json.dumps(edges)
        ))
        
        conn.commit()
        print(f"✅ Topologia salva: {len(nodes)} nós, {len(edges)} arestas")
    
    def create_snapshot(self, step: int, simulation_time: float) -> int:
        """Cria um novo snapshot da simulação e retorna seu ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO simulation_snapshots (timestamp, step, simulation_time, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            simulation_time,
            step,
            simulation_time,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        return cursor.lastrowid
    
    def save_vehicles(self, snapshot_id: int, vehicles: List[Dict]):
        """Salva o estado dos veículos neste snapshot"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        for vehicle in vehicles:
            cursor.execute("""
                INSERT INTO vehicles (
                    snapshot_id, vehicle_id, vehicle_type,
                    position_x, position_y, angle, speed,
                    edge_id, lane_index, route_edges, color
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                snapshot_id,
                vehicle['id'],
                vehicle['type'],
                vehicle['x'],
                vehicle['y'],
                vehicle['angle'],
                vehicle['speed'],
                vehicle.get('edge'),
                vehicle.get('lane'),
                json.dumps(vehicle.get('route', [])),
                vehicle.get('color')
            ))
        
        conn.commit()
    
    def save_traffic_lights(self, snapshot_id: int, traffic_lights: List[Dict]):
        """Salva o estado dos semáforos neste snapshot"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        for tl in traffic_lights:
            cursor.execute("""
                INSERT INTO traffic_lights (
                    snapshot_id, tl_id, position_x, position_y,
                    state, phase_duration
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                snapshot_id,
                tl['id'],
                tl['x'],
                tl['y'],
                tl['state'],
                tl.get('phase_duration')
            ))
        
        conn.commit()
    
    def save_statistics(self, snapshot_id: int, stats: Dict):
        """Salva estatísticas agregadas do snapshot"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO statistics (
                snapshot_id, total_vehicles, total_waiting,
                avg_speed, avg_waiting_time
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            snapshot_id,
            stats['total_vehicles'],
            stats['total_waiting'],
            stats['avg_speed'],
            stats['avg_waiting_time']
        ))
        
        conn.commit()
    
    def get_network_topology(self) -> Dict:
        """Recupera a topologia da rede"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT nodes, edges FROM network_topology ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        
        if row:
            return {
                'nodes': json.loads(row[0]),
                'edges': json.loads(row[1])
            }
        return {'nodes': [], 'edges': []}
    
    def get_snapshot_count(self) -> int:
        """Retorna o número total de snapshots"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM simulation_snapshots")
        return cursor.fetchone()[0]
    
    def get_step_range(self):
        """Retorna (min_step, max_step, count) dos snapshots disponíveis"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MIN(step), MAX(step), COUNT(*) FROM simulation_snapshots")
        row = cursor.fetchone()
        if row and row[0] is not None:
            return {'min': row[0], 'max': row[1], 'count': row[2]}
        return {'min': 0, 'max': 0, 'count': 0}
    
    def get_snapshot_by_step(self, step: int) -> Dict:
        """Recupera um snapshot específico com todos os dados"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Busca o snapshot
        cursor.execute("""
            SELECT id, timestamp, step, simulation_time
            FROM simulation_snapshots
            WHERE step = ?
        """, (step,))
        
        snapshot_row = cursor.fetchone()
        if not snapshot_row:
            return None
        
        snapshot_id = snapshot_row[0]
        
        # Busca veículos
        cursor.execute("""
            SELECT vehicle_id, vehicle_type, position_x, position_y,
                   angle, speed, edge_id, lane_index, route_edges, color
            FROM vehicles
            WHERE snapshot_id = ?
        """, (snapshot_id,))
        
        vehicles = []
        for row in cursor.fetchall():
            vehicles.append({
                'id': row[0],
                'type': row[1],
                'x': row[2],
                'y': row[3],
                'angle': row[4],
                'speed': row[5],
                'edge': row[6],
                'lane': row[7],
                'route': json.loads(row[8]) if row[8] else [],
                'color': row[9]
            })
        
        # Busca semáforos
        cursor.execute("""
            SELECT tl_id, position_x, position_y, state, phase_duration
            FROM traffic_lights
            WHERE snapshot_id = ?
        """, (snapshot_id,))
        
        traffic_lights = []
        for row in cursor.fetchall():
            traffic_lights.append({
                'id': row[0],
                'x': row[1],
                'y': row[2],
                'state': row[3],
                'phase_duration': row[4]
            })
        
        # Busca estatísticas
        cursor.execute("""
            SELECT total_vehicles, total_waiting, avg_speed, avg_waiting_time
            FROM statistics
            WHERE snapshot_id = ?
        """, (snapshot_id,))
        
        stats_row = cursor.fetchone()
        stats = {
            'total_vehicles': stats_row[0] if stats_row else 0,
            'total_waiting': stats_row[1] if stats_row else 0,
            'avg_speed': stats_row[2] if stats_row else 0,
            'avg_waiting_time': stats_row[3] if stats_row else 0
        }
        
        return {
            'timestamp': snapshot_row[1],
            'step': snapshot_row[2],
            'simulation_time': snapshot_row[3],
            'vehicles': vehicles,
            'traffic_lights': traffic_lights,
            'statistics': stats
        }
    
    def clear_all_data(self):
        """Limpa todos os dados da simulação (mantém estrutura)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM statistics")
        cursor.execute("DELETE FROM traffic_lights")
        cursor.execute("DELETE FROM vehicles")
        cursor.execute("DELETE FROM simulation_snapshots")
        cursor.execute("DELETE FROM network_topology")
        conn.commit()
        print("✅ Todos os dados foram limpos")
    
    def close(self):
        """Fecha a conexão com o banco"""
        if self.conn:
            self.conn.close()
            print("✅ Conexão fechada")
