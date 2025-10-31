#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de visualização da simulação via TraCI
Mostra informações sobre o veículo car_journey em sua jornada COMPLETA
Coleta métricas: tempo total, distância percorrida, velocidade média
"""
import traci
import time
import math

print("🔌 Conectando ao SUMO...")
try:
    traci.init(8813)
    print("✅ Conectado!")
except Exception as e:
    print(f"❌ Erro ao conectar: {e}")
    exit(1)

print(f"\n🗺️  Rede carregada:")
print(f"   Edges: {len(traci.edge.getIDList())}")
print(f"   Nodes: {len(traci.junction.getIDList())}")

print(f"\n🚗 Monitorando veículo 'car_journey'...")
print(f"   Origem: n0_0 (canto inferior esquerdo)")
print(f"   Destino: n7_7 (canto superior direito)\n")

step = 0
journey_started = False
journey_complete = False

# Métricas
start_time = 0
start_pos = None
total_distance = 0.0
last_pos = None
speeds = []
stops_count = 0
last_speed = 0

try:
    while not journey_complete:
        traci.simulationStep()
        step += 1
        
        vehicles = traci.vehicle.getIDList()
        
        # Procurar nosso veículo principal
        if 'car_journey' in vehicles:
            if not journey_started:
                journey_started = True
                start_time = step
                start_pos = traci.vehicle.getPosition('car_journey')
                last_pos = start_pos
                print(f"🚀 Step {step}: Veículo car_journey iniciou a viagem!")
                print(f"   Posição inicial: ({start_pos[0]:.1f}, {start_pos[1]:.1f})\n")
            
            # Informações do veículo
            road = traci.vehicle.getRoadID('car_journey')
            pos = traci.vehicle.getPosition('car_journey')
            speed = traci.vehicle.getSpeed('car_journey')
            route = traci.vehicle.getRoute('car_journey')
            route_index = traci.vehicle.getRouteIndex('car_journey')
            
            # Calcular distância percorrida
            if last_pos:
                dx = pos[0] - last_pos[0]
                dy = pos[1] - last_pos[1]
                distance_step = math.sqrt(dx*dx + dy*dy)
                total_distance += distance_step
            last_pos = pos
            
            # Registrar velocidade
            speeds.append(speed)
            
            # Contar paradas (velocidade < 1 km/h)
            if speed < 0.28 and last_speed >= 0.28:  # 0.28 m/s = 1 km/h
                stops_count += 1
            last_speed = speed
            
            # Mostrar progresso a cada 100 steps
            if step % 100 == 0:
                avg_speed = sum(speeds) / len(speeds) if speeds else 0
                print(f"📍 Step {step}:")
                print(f"   Rua atual: {road}")
                print(f"   Posição: ({pos[0]:.1f}, {pos[1]:.1f})")
                print(f"   Velocidade: {speed*3.6:.1f} km/h")
                print(f"   Velocidade média: {avg_speed*3.6:.1f} km/h")
                print(f"   Distância percorrida: {total_distance:.1f} m")
                print(f"   Progresso: {route_index+1}/{len(route)} segmentos")
                print(f"   Paradas: {stops_count}")
                print()
            
            # Verificar se chegou ao destino (última edge da rota)
            if route_index >= len(route) - 1:
                # Verificar se está perto do final da edge
                edge_id = route[-1]
                try:
                    edge_length = traci.lane.getLength(f"{edge_id}_0")
                    lane_pos = traci.vehicle.getLanePosition('car_journey')
                    if lane_pos > edge_length * 0.9:  # 90% da edge
                        journey_complete = True
                        print(f"\n🎯 Step {step}: car_journey chegou ao destino!")
                except:
                    pass
        
        elif journey_started and 'car_journey' not in vehicles:
            journey_complete = True
            print(f"\n✅ Step {step}: Veículo completou a viagem e saiu da simulação!")
        
        # Mostrar estatísticas gerais
        if step % 200 == 0:
            print(f"🚦 Estatísticas gerais (step {step}):")
            print(f"   Veículos ativos: {len(vehicles)}")
            print(f"   Tempo decorrido: {step * 0.1:.1f}s")
            print()

except KeyboardInterrupt:
    print("\n⚠️  Interrompido pelo usuário")

finally:
    # Calcular métricas finais
    travel_time = (step - start_time) * 0.1 if journey_started else 0
    avg_speed = sum(speeds) / len(speeds) if speeds else 0
    
    # Calcular distância linear (linha reta)
    if start_pos and last_pos:
        dx = last_pos[0] - start_pos[0]
        dy = last_pos[1] - start_pos[1]
        linear_distance = math.sqrt(dx*dx + dy*dy)
    else:
        linear_distance = 0
    
    print(f"\n{'='*60}")
    print(f"📊 MÉTRICAS FINAIS DA VIAGEM")
    print(f"{'='*60}\n")
    
    print(f"⏱️  Tempo de viagem: {travel_time:.1f} segundos ({travel_time/60:.2f} minutos)")
    print(f"📏 Distância percorrida: {total_distance:.1f} metros ({total_distance/1000:.2f} km)")
    print(f"📐 Distância linear (A→B): {linear_distance:.1f} metros")
    print(f"🔀 Fator de desvio: {total_distance/linear_distance:.2f}x" if linear_distance > 0 else "")
    print(f"🚗 Velocidade média: {avg_speed*3.6:.1f} km/h")
    print(f"🏁 Velocidade máxima: {max(speeds)*3.6:.1f} km/h" if speeds else "N/A")
    print(f"🐌 Velocidade mínima: {min(speeds)*3.6:.1f} km/h" if speeds else "N/A")
    print(f"🛑 Número de paradas: {stops_count}")
    print(f"📊 Steps executados: {step}")
    
    if journey_started:
        status = "✅ COMPLETADA" if journey_complete else "⚠️  EM PROGRESSO"
        print(f"\n🎯 Status: {status}")
    else:
        print(f"\n❌ Veículo car_journey não foi encontrado")
    
    print(f"\n{'='*60}\n")
    
    traci.close()
    print("👋 Desconectado do SUMO")
