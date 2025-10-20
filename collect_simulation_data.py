#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coletor de Dados da Simulação
Executa a simulação com agentes SPADE e coleta dados via TraCI
Armazena em SQLite para replay na aplicação web
"""
import traci
import time
import sys
from utils.data_collector import SimulationDataCollector

print("="*70)
print("🎬 COLETOR DE DADOS DA SIMULAÇÃO")
print("="*70)
print("\n📊 Este script irá:")
print("   1. Conectar ao SUMO")
print("   2. Coletar dados dos agentes SPADE em tempo real")
print("   3. Armazenar no banco SQLite")
print("   4. Permitir replay na aplicação web\n")

# Inicializar coletor
collector = SimulationDataCollector("simulation_data.db")

print("🧹 Limpando dados antigos...")
collector.clear_all_data()

print("\n🔌 Conectando ao SUMO...")
try:
    traci.init(8813)
    print("✅ Conectado!")
except Exception as e:
    print(f"❌ Erro ao conectar: {e}")
    print("\n💡 Certifique-se de que o SUMO está rodando:")
    print("   ./scripts/run_sumo_docker.sh")
    sys.exit(1)

# 1. Coletar topologia da rede
print("\n🗺️  Coletando topologia da rede...")
try:
    # Coletar nós (junctions)
    nodes = []
    junction_ids = traci.junction.getIDList()
    for j_id in junction_ids:
        if j_id.startswith(':'):  # Ignorar junctions internas
            continue
        pos = traci.junction.getPosition(j_id)
        nodes.append({
            'id': j_id,
            'x': pos[0],
            'y': pos[1]
        })
    
    # Coletar edges
    edges = []
    edge_ids = traci.edge.getIDList()
    for e_id in edge_ids:
        if e_id.startswith(':'):  # Ignorar edges internas
            continue
        
        # Pegar os nós de origem e destino
        from_junction = None
        to_junction = None
        
        # Usar a lane 0 para obter coordenadas
        lane_id = f"{e_id}_0"
        try:
            shape = traci.lane.getShape(lane_id)
            if shape and len(shape) >= 2:
                from_pos = shape[0]
                to_pos = shape[-1]
                
                edges.append({
                    'id': e_id,
                    'from': from_pos,  # Coordenadas ao invés de junction ID
                    'to': to_pos,
                    'shape': shape,
                    'lanes': traci.edge.getLaneNumber(e_id)
                })
        except Exception as e:
            print(f"   ⚠️  Erro ao processar edge {e_id}: {e}")
    
    print(f"   ✅ {len(nodes)} nós")
    print(f"   ✅ {len(edges)} arestas")
    
    collector.save_network_topology(nodes, edges)
    
except Exception as e:
    print(f"   ❌ Erro ao coletar topologia: {e}")
    traci.close()
    sys.exit(1)

# 2. Executar simulação e coletar dados
print("\n🎬 Iniciando coleta de dados da simulação...")
print("   Pressione Ctrl+C para parar\n")

step = 0
journey_started = False
journey_complete = False
max_steps = 5000  # Limite de segurança

try:
    while step < max_steps and not journey_complete:
        traci.simulationStep()
        step += 1
        
        # A cada 10 steps (1 segundo na simulação), coletar dados
        if step % 10 == 0:
            simulation_time = step * 0.1  # 0.1s por step
            
            # Criar snapshot
            snapshot_id = collector.create_snapshot(step, simulation_time)
            
            # Coletar veículos
            vehicles = []
            vehicle_ids = traci.vehicle.getIDList()
            
            total_waiting = 0
            speeds = []
            waiting_times = []
            
            for v_id in vehicle_ids:
                try:
                    pos = traci.vehicle.getPosition(v_id)
                    angle = traci.vehicle.getAngle(v_id)
                    speed = traci.vehicle.getSpeed(v_id)
                    edge = traci.vehicle.getRoadID(v_id)
                    lane = traci.vehicle.getLaneIndex(v_id)
                    route = traci.vehicle.getRoute(v_id)
                    v_type = traci.vehicle.getTypeID(v_id)
                    waiting_time = traci.vehicle.getWaitingTime(v_id)
                    
                    # Determinar cor baseado no tipo
                    if 'ambulance' in v_id.lower():
                        color = '#ff0000'
                        v_type = 'ambulance'
                    elif 'car' in v_id.lower():
                        color = '#4a90e2'
                        v_type = 'car'
                    else:
                        color = '#888888'
                        v_type = 'other'
                    
                    # Destacar car_journey
                    if v_id == 'car_journey':
                        color = '#9b59b6'  # Roxo para o veículo principal
                    
                    vehicles.append({
                        'id': v_id,
                        'type': v_type,
                        'x': pos[0],
                        'y': pos[1],
                        'angle': angle,
                        'speed': speed,
                        'edge': edge,
                        'lane': lane,
                        'route': route,
                        'color': color
                    })
                    
                    speeds.append(speed)
                    waiting_times.append(waiting_time)
                    if waiting_time > 1.0:
                        total_waiting += 1
                    
                except Exception as e:
                    print(f"   ⚠️  Erro ao processar veículo {v_id}: {e}")
            
            collector.save_vehicles(snapshot_id, vehicles)
            
            # Coletar semáforos
            traffic_lights = []
            tl_ids = traci.trafficlight.getIDList()
            
            for tl_id in tl_ids:
                try:
                    # Pegar posição da primeira lane controlada
                    controlled_lanes = traci.trafficlight.getControlledLanes(tl_id)
                    if controlled_lanes:
                        lane_id = controlled_lanes[0]
                        shape = traci.lane.getShape(lane_id)
                        pos = shape[-1] if shape else (0, 0)  # Final da lane
                        
                        state = traci.trafficlight.getRedYellowGreenState(tl_id)
                        phase_duration = traci.trafficlight.getPhaseDuration(tl_id)
                        
                        traffic_lights.append({
                            'id': tl_id,
                            'x': pos[0],
                            'y': pos[1],
                            'state': state,
                            'phase_duration': phase_duration
                        })
                except Exception as e:
                    print(f"   ⚠️  Erro ao processar semáforo {tl_id}: {e}")
            
            collector.save_traffic_lights(snapshot_id, traffic_lights)
            
            # Calcular estatísticas
            stats = {
                'total_vehicles': len(vehicles),
                'total_waiting': total_waiting,
                'avg_speed': sum(speeds) / len(speeds) if speeds else 0.0,
                'avg_waiting_time': sum(waiting_times) / len(waiting_times) if waiting_times else 0.0
            }
            
            collector.save_statistics(snapshot_id, stats)
            
            # Mostrar progresso
            if step % 100 == 0:
                print(f"📊 Step {step} ({simulation_time:.1f}s):")
                print(f"   Veículos: {len(vehicles)} | Esperando: {total_waiting}")
                print(f"   Vel. média: {stats['avg_speed']*3.6:.1f} km/h")
                print(f"   Semáforos: {len(traffic_lights)}")
        
        # Verificar se car_journey completou
        if 'car_journey' in traci.vehicle.getIDList():
            journey_started = True
        elif journey_started:
            journey_complete = True
            print(f"\n✅ car_journey completou a viagem no step {step}!")

except KeyboardInterrupt:
    print("\n⚠️  Coleta interrompida pelo usuário")

finally:
    collector.close()
    traci.close()
    
    print(f"\n{'='*70}")
    print(f"✅ COLETA CONCLUÍDA")
    print(f"{'='*70}\n")
    
    # Reabrir para mostrar estatísticas
    collector = SimulationDataCollector("simulation_data.db")
    
    total_snapshots = collector.get_snapshot_count()
    duration = (step * 0.1) / 60  # minutos
    
    print(f"📊 Dados coletados:")
    print(f"   Total de snapshots: {total_snapshots}")
    print(f"   Steps executados: {step}")
    print(f"   Duração simulada: {duration:.2f} minutos")
    print(f"   Taxa de amostragem: 10 FPS (1 snapshot/segundo)")
    
    print(f"\n💾 Banco de dados: simulation_data.db")
    print(f"   ✅ Pronto para replay na aplicação web!")
    
    print(f"\n🚀 Próximos passos:")
    print(f"   1. Inicie a aplicação web: python app.py")
    print(f"   2. Clique em 'Iniciar Simulação'")
    print(f"   3. Veja os dados dos agentes SPADE em ação!")
    
    print(f"\n{'='*70}\n")
    
    collector.close()
