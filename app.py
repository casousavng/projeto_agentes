#!/usr/bin/env python3
"""
Flask Web Application - Traffic Simulation Replay
Visualização dos dados coletados dos agentes SPADE via SQLite
"""

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import threading
import time
import os
from utils.data_collector import SimulationDataCollector

app = Flask(__name__)
app.config['SECRET_KEY'] = 'traffic_simulation_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Estado da simulação
simulation_state = {
    'running': False,
    'current_step': 0,
    'max_steps': 0,
    'playback_speed': 1.0,  # 1.0 = tempo real, 2.0 = 2x mais rápido
    'paused': False
}

# Coletor de dados (leitura)
collector = None

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/api/network')
def get_network():
    """API: Retorna a topologia da rede"""
    global collector
    
    if not collector:
        collector = SimulationDataCollector("simulation_data.db")
    
    try:
        topology = collector.get_network_topology()
        
        if not topology['nodes']:
            return jsonify({
                'success': False,
                'error': 'Nenhum dado encontrado. Execute collect_simulation_data.py primeiro!'
            }), 404
        
        return jsonify({
            'success': True,
            'nodes': topology['nodes'],
            'edges': topology['edges']
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/start', methods=['POST'])
def start_simulation():
    """API: Inicia o replay da simulação"""
    global collector, simulation_state
    
    if simulation_state['running']:
        return jsonify({
            'success': False,
            'error': 'Simulação já está rodando'
        })
    
    try:
        if not collector:
            collector = SimulationDataCollector("simulation_data.db")
        
        # Verificar se há dados
        total_snapshots = collector.get_snapshot_count()
        
        if total_snapshots == 0:
            return jsonify({
                'success': False,
                'error': 'Nenhum dado encontrado. Execute collect_simulation_data.py primeiro!'
            }), 404
        
        simulation_state['running'] = True
        simulation_state['current_step'] = 0
        simulation_state['max_steps'] = total_snapshots
        simulation_state['paused'] = False
        
        # Inicia thread de playback
        thread = threading.Thread(target=playback_loop)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': f'Replay iniciado com {total_snapshots} frames',
            'total_frames': total_snapshots
        })
    
    except Exception as e:
        simulation_state['running'] = False
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stop', methods=['POST'])
def stop_simulation():
    """API: Para o replay"""
    global simulation_state
    
    simulation_state['running'] = False
    simulation_state['current_step'] = 0
    
    return jsonify({
        'success': True,
        'message': 'Replay interrompido'
    })

@app.route('/api/pause', methods=['POST'])
def pause_simulation():
    """API: Pausa/retoma o replay"""
    global simulation_state
    
    simulation_state['paused'] = not simulation_state['paused']
    
    return jsonify({
        'success': True,
        'paused': simulation_state['paused']
    })

@app.route('/api/speed/<float:speed>', methods=['POST'])
def set_speed(speed):
    """API: Ajusta a velocidade do replay"""
    global simulation_state
    
    if 0.1 <= speed <= 5.0:
        simulation_state['playback_speed'] = speed
        return jsonify({
            'success': True,
            'speed': speed
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Velocidade deve estar entre 0.1 e 5.0'
        }), 400

@app.route('/api/status')
def get_status():
    """API: Status atual do replay"""
    return jsonify({
        'running': simulation_state['running'],
        'current_step': simulation_state['current_step'],
        'max_steps': simulation_state['max_steps'],
        'paused': simulation_state['paused'],
        'speed': simulation_state['playback_speed'],
        'progress': (simulation_state['current_step'] / simulation_state['max_steps'] * 100) if simulation_state['max_steps'] > 0 else 0
    })

def playback_loop():
    """Loop de replay dos dados gravados"""
    global simulation_state, collector
    
    print("🎬 Iniciando replay...")
    
    try:
        # Recuperar dados step a step
        step = 0
        
        while simulation_state['running'] and step < simulation_state['max_steps']:
            # Pausar se necessário
            while simulation_state['paused'] and simulation_state['running']:
                time.sleep(0.1)
            
            if not simulation_state['running']:
                break
            
            # Buscar snapshot (steps são salvos a cada 10 steps = 1 segundo simulado)
            # Então step 0 = step_db 0, step 1 = step_db 10, etc.
            step_db = step * 10
            
            snapshot = collector.get_snapshot_by_step(step_db)
            
            if not snapshot:
                print(f"⚠️  Snapshot {step_db} não encontrado")
                step += 1
                continue
            
            simulation_state['current_step'] = step
            
            # Emitir dados via WebSocket
            socketio.emit('simulation_update', {
                'step': step,
                'simulation_time': snapshot['simulation_time'],
                'vehicles': snapshot['vehicles'],
                'traffic_lights': snapshot['traffic_lights'],
                'statistics': snapshot['statistics']
            })
            
            # Aguardar de acordo com a velocidade
            # Base: 10 FPS (0.1s entre frames)
            sleep_time = 0.1 / simulation_state['playback_speed']
            time.sleep(sleep_time)
            
            step += 1
        
        print("✅ Replay concluído")
        simulation_state['running'] = False
        
        # Notificar fim
        socketio.emit('simulation_complete', {
            'message': 'Replay concluído!',
            'total_steps': step
        })
    
    except Exception as e:
        print(f"❌ Erro no replay: {e}")
        import traceback
        traceback.print_exc()
        simulation_state['running'] = False
        
        socketio.emit('simulation_error', {
            'error': str(e)
        })

@socketio.on('connect')
def handle_connect():
    """Cliente conectou via WebSocket"""
    print("🔌 Cliente conectado")
    emit('connected', {'message': 'Conectado ao servidor de replay'})

@socketio.on('disconnect')
def handle_disconnect():
    """Cliente desconectou"""
    print("🔌 Cliente desconectado")

if __name__ == '__main__':
    print("="*70)
    print("🚀 SERVIDOR DE REPLAY - SIMULAÇÃO DE TRÁFEGO")
    print("="*70)
    print("\n📊 Este servidor reproduz dados coletados dos agentes SPADE")
    print("   Os dados foram capturados em tempo real durante a simulação\n")
    
    # Verificar se o banco existe
    if not os.path.exists("simulation_data.db"):
        print("⚠️  ATENÇÃO: Banco de dados não encontrado!")
        print("\n📋 Execute primeiro:")
        print("   1. ./scripts/run_sumo_docker.sh")
        print("   2. python collect_simulation_data.py")
        print("   3. python app.py (este servidor)\n")
        print("="*70 + "\n")
    else:
        collector_temp = SimulationDataCollector("simulation_data.db")
        total = collector_temp.get_snapshot_count()
        collector_temp.close()
        
        print(f"✅ Banco de dados encontrado: {total} snapshots disponíveis")
        print(f"   Duração: ~{total/10/60:.2f} minutos de simulação\n")
        print("="*70 + "\n")
    
    print("🌐 Abrindo servidor em http://localhost:5001")
    print("   Use Ctrl+C para parar\n")
    
    socketio.run(app, host='0.0.0.0', port=5001, debug=False, allow_unsafe_werkzeug=True)
