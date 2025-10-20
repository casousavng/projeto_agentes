#!/usr/bin/env python3
# -*- coding: utf-8 -*-

html_content = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simulação SPADE Traffic</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            overflow: hidden;
        }
        .container {
            display: grid;
            grid-template-columns: 300px 1fr;
            height: 100vh;
        }
        .sidebar { background: rgba(0, 0, 0, 0.3); padding: 20px; }
        h1 { font-size: 24px; margin-bottom: 20px; text-align: center; }
        .btn {
            width: 100%;
            padding: 12px;
            margin: 8px 0;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
        }
        .btn-start { background: #10b981; color: white; }
        .btn-stop { background: #ef4444; color: white; }
        .stats { background: rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 15px; margin: 15px 0; }
        .stat-item { display: flex; justify-content: space-between; margin: 10px 0; }
        .stat-value { font-weight: bold; font-size: 18px; color: #10b981; }
        .canvas-area { position: relative; background: #1a1a2e; display: flex; align-items: center; justify-content: center; }
        #simulationCanvas { border: 2px solid rgba(255, 255, 255, 0.2); border-radius: 10px; }
        .status-badge { position: absolute; top: 20px; right: 20px; padding: 10px 20px; border-radius: 20px; font-weight: bold; }
        .status-running { background: #10b981; }
        .status-stopped { background: #6b7280; }
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h1>🚦 Traffic Sim</h1>
            <div>
                <button class="btn btn-start" onclick="startSimulation()">▶️ Iniciar</button>
                <button class="btn btn-stop" onclick="stopSimulation()">⏹️ Parar</button>
            </div>
            <div class="stats">
                <h3>📊 Stats</h3>
                <div class="stat-item"><span>Step:</span><span class="stat-value" id="stat-step">0</span></div>
                <div class="stat-item"><span>Veículos:</span><span class="stat-value" id="stat-vehicles">0</span></div>
                <div class="stat-item"><span>Velocidade:</span><span class="stat-value" id="stat-speed">0 km/h</span></div>
            </div>
        </div>
        <div class="canvas-area">
            <div id="status-badge" class="status-badge status-stopped">⏸️ PARADO</div>
            <canvas id="simulationCanvas" width="1200" height="900"></canvas>
        </div>
    </div>
    <script>
const canvas = document.getElementById('simulationCanvas');
const ctx = canvas.getContext('2d');
const socket = io();
let simData = { nodes: [], edges: [], vehicles: [], trafficLights: [], stats: {}, step: 0 };
let viewport = { offsetX: 0, offsetY: 0, scale: 3.0, minX: 0, minY: 0, maxX: 0, maxY: 0 };

socket.on('simulation_update', (data) => {
    simData.vehicles = data.vehicles || [];
    simData.trafficLights = data.traffic_lights || [];
    simData.stats = data.stats || {};
    simData.step = data.step || 0;
    updateStats();
    render();
});

async function startSimulation() {
    const response = await fetch('/api/start', { method: 'POST' });
    const data = await response.json();
    if (data.status === 'started') {
        simData.nodes = data.nodes || [];
        simData.edges = data.edges || [];
        calculateBounds();
        centerView();
        document.getElementById('status-badge').className = 'status-badge status-running';
        document.getElementById('status-badge').textContent = '▶️ RODANDO';
        render();
    }
}

async function stopSimulation() {
    await fetch('/api/stop', { method: 'POST' });
    document.getElementById('status-badge').className = 'status-badge status-stopped';
    document.getElementById('status-badge').textContent = '⏸️ PARADO';
}

function updateStats() {
    document.getElementById('stat-step').textContent = simData.step;
    document.getElementById('stat-vehicles').textContent = simData.stats.total_vehicles || 0;
    document.getElementById('stat-speed').textContent = (simData.stats.avg_speed || 0).toFixed(1) + ' km/h';
}

function calculateBounds() {
    if (simData.nodes.length === 0) return;
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    simData.nodes.forEach(node => {
        minX = Math.min(minX, node.x);
        minY = Math.min(minY, node.y);
        maxX = Math.max(maxX, node.x);
        maxY = Math.max(maxY, node.y);
    });
    viewport.minX = minX; viewport.minY = minY; viewport.maxX = maxX; viewport.maxY = maxY;
}

function centerView() {
    const width = viewport.maxX - viewport.minX;
    const height = viewport.maxY - viewport.minY;
    const scaleX = canvas.width / width;
    const scaleY = canvas.height / height;
    viewport.scale = Math.min(scaleX, scaleY) * 0.9;
    viewport.offsetX = (canvas.width - width * viewport.scale) / 2 - viewport.minX * viewport.scale;
    viewport.offsetY = (canvas.height - height * viewport.scale) / 2 - viewport.minY * viewport.scale;
}

function worldToScreen(x, y) {
    return { x: x * viewport.scale + viewport.offsetX, y: y * viewport.scale + viewport.offsetY };
}

function render() {
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    simData.edges.forEach(edge => {
        ctx.strokeStyle = '#444';
        ctx.lineWidth = 3;
        ctx.beginPath();
        const from = worldToScreen(edge.from[0], edge.from[1]);
        ctx.moveTo(from.x, from.y);
        const to = worldToScreen(edge.to[0], edge.to[1]);
        ctx.lineTo(to.x, to.y);
        ctx.stroke();
    });
    
    simData.nodes.forEach(node => {
        const pos = worldToScreen(node.x, node.y);
        ctx.fillStyle = '#666';
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, 3, 0, Math.PI * 2);
        ctx.fill();
    });
    
    simData.trafficLights.forEach(tl => {
        const pos = worldToScreen(tl.x, tl.y);
        let color = '#888';
        if (tl.state && tl.state.includes('G')) color = '#10b981';
        else if (tl.state && tl.state.includes('y')) color = '#fbbf24';
        else if (tl.state && tl.state.includes('r')) color = '#ef4444';
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, 5, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = 'white';
        ctx.lineWidth = 1;
        ctx.stroke();
    });
    
    simData.vehicles.forEach(vehicle => {
        const pos = worldToScreen(vehicle.x, vehicle.y);
        let color = '#3b82f6';
        if (vehicle.id === 'car_journey') color = '#fbbf24';
        if (vehicle.type === 'ambulance') color = '#ef4444';
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, 6, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = 'white';
        ctx.lineWidth = 2;
        ctx.stroke();
    });
}

render();
    </script>
</body>
</html>"""

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print('✅ Ficheiro index.html criado com sucesso!')
print(f'📏 Tamanho: {len(html_content)} bytes')
