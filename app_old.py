#!/usr/bin/env python3
"""
Flask Web Application - Traffic Simulation Visualization
Visualização em tempo real da simulação de tráfego com:
- Rede 8x8 de ruas
- Veículos com rotas dinâmicas
- Semáforos inteligentes
- Veículos de emergência
- Roteamento otimizado A→B
"""

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import traci
import threading
import time
import json
import sys
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'traffic_simulation_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Estado da simulação
simulation_state = {
    'running': False,
    'step': 0,
    'vehicles': {},
    'traffic_lights': {},
    'edges': [],
    'nodes': [],
    'route_info': {},
    'stats': {
        'total_vehicles': 0,
        'avg_speed': 0,
        'stopped_vehicles': 0
    }
}

# Configuração SUMO
SUMO_CONFIG = '/scenarios/grid_8x8/simulation.sumocfg'
TRACI_PORT = 8813

def get_network_topology():
    """Obtém a topologia da rede (nós e edges)"""
    try:
        nodes = []
        edges = []
        
        # Faz um step primeiro para garantir que a conexão está estável
        traci.simulationStep()
        print("✅ Conexão TraCI estável")
        
        # Obtém todos os nós com suas posições
        junction_list = traci.junction.getIDList()
        print(f"📍 Encontrados {len(junction_list)} cruzamentos")
        
        for node_id in junction_list:
            pos = traci.junction.getPosition(node_id)
            nodes.append({
                'id': node_id,
                'x': pos[0],
                'y': pos[1],
                'type': 'traffic_light' if node_id.startswith('n') else 'junction'
            })
        
        # Obtém todas as edges com informações
        edge_list = traci.edge.getIDList()
        print(f"🛣️  Encontradas {len(edge_list)} edges")
        
        for edge_id in edge_list:
            if not edge_id.startswith(':'):  # Ignora edges internas
                try:
                    from_node = traci.edge.getFromJunction(edge_id)
                    to_node = traci.edge.getToJunction(edge_id)
                    
                    # Posições dos nós
                    from_pos = traci.junction.getPosition(from_node)
                    to_pos = traci.junction.getPosition(to_node)
                    
                    # Tipo de via (velocidade máxima)
                    max_speed = traci.edge.getMaxSpeed(edge_id)
                    
                    # Classifica por velocidade
                    if max_speed > 20:
                        road_type = 'highway'
                    elif max_speed > 15:
                        road_type = 'arterial'
                    elif max_speed > 12:
                        road_type = 'collector'
                    else:
                        road_type = 'local'
                    
                    edges.append({
                        'id': edge_id,
                        'from': from_node,
                        'to': to_node,
                        'from_pos': {'x': from_pos[0], 'y': from_pos[1]},
                        'to_pos': {'x': to_pos[0], 'y': to_pos[1]},
                        'max_speed': max_speed * 3.6,  # m/s -> km/h
                        'type': road_type,
                        'lanes': traci.edge.getLaneNumber(edge_id)
                    })
                except Exception as e:
                    print(f"⚠️  Erro na edge {edge_id}: {e}")
                    continue
        
        print(f"✅ Topologia carregada: {len(nodes)} nós, {len(edges)} edges")
        return nodes, edges
        
    except Exception as e:
        print(f"❌ Erro ao obter topologia: {e}")
        import traceback
        traceback.print_exc()
        return [], []

def get_vehicle_route(vehicle_id):
    """Obtém a rota completa de um veículo"""
    try:
        route_edges = traci.vehicle.getRoute(vehicle_id)
        route_index = traci.vehicle.getRouteIndex(vehicle_id)
        
        return {
            'edges': route_edges,
            'current_index': route_index,
            'destination': route_edges[-1] if route_edges else None
        }
    except:
        return None

def update_simulation_state():
    """Atualiza o estado da simulação para enviar ao frontend"""
    try:
        # Veículos
        vehicles = {}
        total_speed = 0
        stopped_count = 0
        
        for veh_id in traci.vehicle.getIDList():
            pos = traci.vehicle.getPosition(veh_id)
            speed = traci.vehicle.getSpeed(veh_id) * 3.6  # m/s -> km/h
            angle = traci.vehicle.getAngle(veh_id)
            edge_id = traci.vehicle.getRoadID(veh_id)
            vehicle_type = traci.vehicle.getTypeID(veh_id)
            color = traci.vehicle.getColor(veh_id)
            
            # Rota do veículo
            route_info = get_vehicle_route(veh_id)
            
            # Determina o tipo (carro, ambulância, etc)
            if vehicle_type == 'emergency':
                vtype = 'ambulance'
            elif veh_id == 'car_journey':
                vtype = 'journey'
            else:
                vtype = 'traffic'
            
            vehicles[veh_id] = {
                'id': veh_id,
                'x': pos[0],
                'y': pos[1],
                'speed': round(speed, 1),
                'angle': angle,
                'edge': edge_id,
                'type': vtype,
                'color': color,
                'route': route_info
            }
            
            total_speed += speed
            if speed < 1:
                stopped_count += 1
        
        simulation_state['vehicles'] = vehicles
        
        # Semáforos
        traffic_lights = {}
        for tl_id in traci.trafficlight.getIDList():
            pos = traci.junction.getPosition(tl_id)
            state = traci.trafficlight.getRedYellowGreenState(tl_id)
            phase = traci.trafficlight.getPhase(tl_id)
            
            # Conta veículos esperando
            controlled_lanes = traci.trafficlight.getControlledLanes(tl_id)
            waiting_vehicles = sum(
                traci.lane.getLastStepHaltingNumber(lane) 
                for lane in set(controlled_lanes)
            )
            
            traffic_lights[tl_id] = {
                'id': tl_id,
                'x': pos[0],
                'y': pos[1],
                'state': state,
                'phase': phase,
                'waiting': waiting_vehicles
            }
        
        simulation_state['traffic_lights'] = traffic_lights
        
        # Estatísticas
        num_vehicles = len(vehicles)
        simulation_state['stats'] = {
            'total_vehicles': num_vehicles,
            'avg_speed': round(total_speed / num_vehicles if num_vehicles > 0 else 0, 1),
            'stopped_vehicles': stopped_count
        }
        
    except Exception as e:
        print(f"❌ Erro ao atualizar estado: {e}")

def simulation_loop():
    """Loop principal da simulação"""
    print("🚀 Iniciando loop de simulação...")
    
    while simulation_state['running']:
        try:
            # Avança um step
            traci.simulationStep()
            simulation_state['step'] += 1
            
            # Atualiza estado
            update_simulation_state()
            
            # Envia atualização para todos os clientes conectados
            socketio.emit('simulation_update', {
                'step': simulation_state['step'],
                'vehicles': simulation_state['vehicles'],
                'traffic_lights': simulation_state['traffic_lights'],
                'stats': simulation_state['stats']
            })
            
            # Controla FPS (10 updates/segundo)
            time.sleep(0.1)
            
        except traci.exceptions.FatalTraCIError:
            print("⚠️ Simulação SUMO encerrada")
            simulation_state['running'] = False
            break
        except Exception as e:
            print(f"❌ Erro no loop: {e}")
            simulation_state['running'] = False
            break
    
    print("🛑 Loop de simulação encerrado")

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_simulation():
    """Inicia a simulação"""
    if simulation_state['running']:
        return jsonify({'status': 'already_running'})
    
    try:
        # Reinicia container SUMO
        print("🔄 Reiniciando SUMO...")
        os.system("docker stop sumo-sim 2>/dev/null")
        os.system("docker rm sumo-sim 2>/dev/null")
        os.system("./scripts/run_sumo_docker.sh > /dev/null 2>&1")
        
        # Aguarda SUMO iniciar
        print("⏳ Aguardando SUMO...")
        time.sleep(3)
        
        # Conecta ao SUMO com retries
        print("🔌 Conectando ao SUMO...")
        max_retries = 10
        connected = False
        for attempt in range(max_retries):
            try:
                traci.connect(TRACI_PORT)
                print(f"✅ Conectado ao SUMO! (tentativa {attempt + 1})")
                connected = True
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⏳ Tentativa {attempt + 1}/{max_retries}...")
                    time.sleep(1)
                else:
                    raise Exception(f"Falha ao conectar após {max_retries} tentativas: {e}")
        
        if not connected:
            raise Exception("Não foi possível conectar ao SUMO")
        
        # Obtém topologia da rede
        print("🗺️ Carregando topologia...")
        nodes, edges = get_network_topology()
        
        if len(nodes) == 0 or len(edges) == 0:
            raise Exception("Falha ao carregar topologia da rede")
        
        simulation_state['nodes'] = nodes
        simulation_state['edges'] = edges
        
        print(f"✅ Topologia OK: {len(nodes)} nós, {len(edges)} edges")
        
        # Inicia simulação
        simulation_state['running'] = True
        simulation_state['step'] = 0
        
        # Inicia thread de simulação
        sim_thread = threading.Thread(target=simulation_loop, daemon=True)
        sim_thread.start()
        
        print("✅ Simulação iniciada!")
        
        return jsonify({
            'status': 'started',
            'nodes': nodes,
            'edges': edges
        })
        
    except Exception as e:
        print(f"❌ Erro ao iniciar: {e}")
        simulation_state['running'] = False
        try:
            traci.close()
        except:
            pass
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def stop_simulation():
    """Para a simulação"""
    simulation_state['running'] = False
    
    try:
        traci.close()
    except:
        pass
    
    return jsonify({'status': 'stopped'})

@app.route('/api/status')
def get_status():
    """Retorna o status atual da simulação"""
    return jsonify({
        'running': simulation_state['running'],
        'step': simulation_state['step'],
        'stats': simulation_state['stats']
    })

@app.route('/api/topology')
def get_topology():
    """Retorna a topologia da rede"""
    return jsonify({
        'nodes': simulation_state['nodes'],
        'edges': simulation_state['edges']
    })

@socketio.on('connect')
def handle_connect():
    """Cliente conectado via WebSocket"""
    print(f"🔌 Cliente conectado")
    emit('connection_response', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Cliente desconectado"""
    print(f"🔌 Cliente desconectado")

if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════╗
║     🚦 TRAFFIC SIMULATION WEB VISUALIZATION 🚗            ║
║                                                            ║
║  Visualização em tempo real da simulação de tráfego       ║
║  Rede 8x8 com semáforos inteligentes                      ║
╚════════════════════════════════════════════════════════════╝

📡 Servidor Flask rodando em: http://localhost:5001
🔌 WebSocket ativo para atualizações em tempo real
⚡ TraCI conectando na porta: 8813

⚠️  ATENÇÃO: Execute o SUMO primeiro:
   ./scripts/run_sumo_docker.sh
    """)
    
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, use_reloader=False)
