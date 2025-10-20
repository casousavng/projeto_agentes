// Traffic Simulation Visualization - JavaScript Client
// Renderização em tempo real da simulação

const canvas = document.getElementById('simulationCanvas');
const ctx = canvas.getContext('2d');

// Estado da visualização
let simulationData = {
    nodes: [],
    edges: [],
    vehicles: [],  // Array em vez de objeto
    traffic_lights: [],  // Array em vez de objeto
    stats: {},
    step: 0
};

let viewport = {
    offsetX: 0,
    offsetY: 0,
    scale: 1.0,
    isDragging: false,
    lastX: 0,
    lastY: 0
};

// WebSocket
const socket = io();

// Cores
const COLORS = {
    highway: '#ef4444',
    arterial: '#f59e0b',
    collector: '#10b981',
    local: '#6b7280',
    junction: '#374151',
    traffic_light: '#1f2937',
    vehicle_journey: '#fbbf24',
    vehicle_traffic: '#3b82f6',
    vehicle_ambulance: '#dc2626',
    tl_green: '#10b981',
    tl_yellow: '#fbbf24',
    tl_red: '#ef4444',
    route: '#8b5cf6'
};

// FPS Counter
let lastFrameTime = Date.now();
let fps = 0;

// ============ WebSocket Events ============

socket.on('connect', () => {
    console.log('✅ Conectado ao servidor');
});

socket.on('disconnect', () => {
    console.log('❌ Desconectado do servidor');
});

socket.on('simulation_update', (data) => {
    // Backend envia arrays, então usamos diretamente
    simulationData.vehicles = data.vehicles || [];
    simulationData.traffic_lights = data.traffic_lights || [];
    simulationData.stats = data.stats || {};
    simulationData.step = data.step || 0;
    
    console.log('📦 Update recebido - Step:', data.step, 'Veículos:', simulationData.vehicles.length, 'Semáforos:', simulationData.traffic_lights.length);
    
    updateStats();
    render();
});

// ============ API Functions ============

async function startSimulation() {
    document.getElementById('loading').style.display = 'block';
    
    try {
        const response = await fetch('/api/start', { method: 'POST' });
        const data = await response.json();
        
        if (data.status === 'started') {
            simulationData.nodes = data.nodes;
            simulationData.edges = data.edges;
            
            // Ajusta viewport para centralizar a rede
            centerViewport();
            
            document.getElementById('status-badge').className = 'status-badge status-running';
            document.getElementById('status-badge').textContent = '▶️ RODANDO';
            document.getElementById('info-panel').style.display = 'flex';
            
            console.log('✅ Simulação iniciada!');
        }
    } catch (error) {
        console.error('❌ Erro ao iniciar:', error);
        alert('Erro ao iniciar simulação. Verifique se o SUMO está rodando!');
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
}

async function stopSimulation() {
    try {
        await fetch('/api/stop', { method: 'POST' });
        
        document.getElementById('status-badge').className = 'status-badge status-stopped';
        document.getElementById('status-badge').textContent = '⏸️ PARADO';
        document.getElementById('info-panel').style.display = 'none';
        
        console.log('🛑 Simulação parada');
    } catch (error) {
        console.error('❌ Erro ao parar:', error);
    }
}

function updateStats() {
    document.getElementById('stat-step').textContent = simulationData.step;
    document.getElementById('stat-vehicles').textContent = simulationData.stats.total_vehicles || 0;
    document.getElementById('stat-speed').textContent = (simulationData.stats.avg_speed || 0) + ' km/h';
    document.getElementById('stat-stopped').textContent = simulationData.stats.stopped_vehicles || 0;
    
    // Tempo simulado (cada step = 0.1s)
    const seconds = Math.floor(simulationData.step * 0.1);
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    document.getElementById('info-time').textContent = `${minutes}:${secs.toString().padStart(2, '0')}`;
    
    // FPS
    const now = Date.now();
    const delta = now - lastFrameTime;
    fps = Math.round(1000 / delta);
    document.getElementById('info-fps').textContent = fps;
    lastFrameTime = now;
}

// ============ Viewport Controls ============

function centerViewport() {
    if (simulationData.nodes.length === 0) return;
    
    // Calcula bounding box
    let minX = Infinity, minY = Infinity;
    let maxX = -Infinity, maxY = -Infinity;
    
    simulationData.nodes.forEach(node => {
        minX = Math.min(minX, node.x);
        minY = Math.min(minY, node.y);
        maxX = Math.max(maxX, node.x);
        maxY = Math.max(maxY, node.y);
    });
    
    const networkWidth = maxX - minX;
    const networkHeight = maxY - minY;
    
    // Calcula escala para caber na tela
    const scaleX = (canvas.width * 0.9) / networkWidth;
    const scaleY = (canvas.height * 0.9) / networkHeight;
    viewport.scale = Math.min(scaleX, scaleY);
    
    // Centraliza
    viewport.offsetX = (canvas.width - networkWidth * viewport.scale) / 2 - minX * viewport.scale;
    viewport.offsetY = (canvas.height - networkHeight * viewport.scale) / 2 - minY * viewport.scale;
}

function worldToScreen(x, y) {
    return {
        x: x * viewport.scale + viewport.offsetX,
        y: y * viewport.scale + viewport.offsetY
    };
}

// ============ Canvas Interactions ============

canvas.addEventListener('mousedown', (e) => {
    viewport.isDragging = true;
    viewport.lastX = e.clientX;
    viewport.lastY = e.clientY;
    canvas.style.cursor = 'grabbing';
});

canvas.addEventListener('mousemove', (e) => {
    if (viewport.isDragging) {
        const dx = e.clientX - viewport.lastX;
        const dy = e.clientY - viewport.lastY;
        
        viewport.offsetX += dx;
        viewport.offsetY += dy;
        
        viewport.lastX = e.clientX;
        viewport.lastY = e.clientY;
        
        render();
    }
});

canvas.addEventListener('mouseup', () => {
    viewport.isDragging = false;
    canvas.style.cursor = 'move';
});

canvas.addEventListener('wheel', (e) => {
    e.preventDefault();
    
    const zoomFactor = e.deltaY > 0 ? 0.9 : 1.1;
    const newScale = viewport.scale * zoomFactor;
    
    // Limita o zoom
    if (newScale > 0.1 && newScale < 5) {
        viewport.scale = newScale;
        render();
    }
});

// ============ Rendering ============

function drawEdge(edge) {
    const from = worldToScreen(edge.from_pos.x, edge.from_pos.y);
    const to = worldToScreen(edge.to_pos.x, edge.to_pos.y);
    
    // Cor baseada no tipo
    ctx.strokeStyle = COLORS[edge.type] || COLORS.local;
    ctx.lineWidth = edge.lanes * 2 * viewport.scale;
    
    ctx.beginPath();
    ctx.moveTo(from.x, from.y);
    ctx.lineTo(to.x, to.y);
    ctx.stroke();
}

function drawNode(node) {
    const pos = worldToScreen(node.x, node.y);
    const radius = (node.type === 'traffic_light' ? 8 : 5) * viewport.scale;
    
    ctx.fillStyle = COLORS[node.type] || COLORS.junction;
    ctx.beginPath();
    ctx.arc(pos.x, pos.y, radius, 0, Math.PI * 2);
    ctx.fill();
}

function drawTrafficLight(tl) {
    const pos = worldToScreen(tl.x, tl.y);
    const size = 12 * viewport.scale;
    
    // Determina cor dominante do estado
    let color = COLORS.tl_red;
    if (tl.state.includes('G') || tl.state.includes('g')) {
        color = COLORS.tl_green;
    } else if (tl.state.includes('y')) {
        color = COLORS.tl_yellow;
    }
    
    // Desenha semáforo
    ctx.fillStyle = color;
    ctx.shadowColor = color;
    ctx.shadowBlur = 10 * viewport.scale;
    ctx.beginPath();
    ctx.arc(pos.x, pos.y, size, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0;
    
    // Mostra veículos esperando se zoom suficiente
    if (viewport.scale > 0.5 && tl.waiting > 0) {
        ctx.fillStyle = '#fff';
        ctx.font = `${10 * viewport.scale}px Arial`;
        ctx.textAlign = 'center';
        ctx.fillText(tl.waiting, pos.x, pos.y - size - 5);
    }
}

function drawVehicle(vehicle) {
    const pos = worldToScreen(vehicle.x, vehicle.y);
    
    // Cor baseada no tipo
    let color;
    if (vehicle.type === 'journey') {
        color = COLORS.vehicle_journey;
    } else if (vehicle.type === 'ambulance') {
        color = COLORS.vehicle_ambulance;
    } else {
        color = COLORS.vehicle_traffic;
    }
    
    // Tamanho do veículo
    const size = (vehicle.type === 'journey' ? 10 : 7) * viewport.scale;
    
    // Desenha veículo (retângulo rotacionado)
    ctx.save();
    ctx.translate(pos.x, pos.y);
    ctx.rotate((vehicle.angle - 90) * Math.PI / 180); // Ajuste de orientação
    
    // Corpo do veículo
    ctx.fillStyle = color;
    ctx.fillRect(-size/2, -size, size, size * 2);
    
    // Destaque para veículo da jornada
    if (vehicle.type === 'journey') {
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 2;
        ctx.strokeRect(-size/2, -size, size, size * 2);
    }
    
    ctx.restore();
    
    // Mostra velocidade se zoom suficiente
    if (viewport.scale > 0.8) {
        ctx.fillStyle = '#fff';
        ctx.font = `${8 * viewport.scale}px Arial`;
        ctx.textAlign = 'center';
        ctx.fillText(`${vehicle.speed}`, pos.x, pos.y - size - 5);
    }
    
    // Desenha rota para veículo da jornada
    if (vehicle.type === 'journey' && vehicle.route && viewport.scale > 0.5) {
        drawRoute(vehicle.route);
    }
}

function drawRoute(route) {
    if (!route.edges || route.edges.length === 0) return;
    
    ctx.strokeStyle = COLORS.route;
    ctx.lineWidth = 3 * viewport.scale;
    ctx.setLineDash([5 * viewport.scale, 5 * viewport.scale]);
    ctx.globalAlpha = 0.5;
    
    ctx.beginPath();
    
    for (let i = 0; i < route.edges.length; i++) {
        const edgeId = route.edges[i];
        const edge = simulationData.edges.find(e => e.id === edgeId);
        
        if (edge) {
            const from = worldToScreen(edge.from_pos.x, edge.from_pos.y);
            const to = worldToScreen(edge.to_pos.x, edge.to_pos.y);
            
            if (i === 0) {
                ctx.moveTo(from.x, from.y);
            }
            ctx.lineTo(to.x, to.y);
        }
    }
    
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.globalAlpha = 1.0;
}

function render() {
    // Limpa canvas
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // 1. Desenha edges (ruas)
    simulationData.edges.forEach(edge => drawEdge(edge));
    
    // 2. Desenha nodes (junções)
    simulationData.nodes.forEach(node => drawNode(node));
    
    // 3. Desenha semáforos (agora é array)
    simulationData.traffic_lights.forEach(tl => drawTrafficLight(tl));
    
    // 4. Desenha veículos (agora é array)
    simulationData.vehicles.forEach(vehicle => drawVehicle(vehicle));
    
    // Grid de referência (opcional, se zoom alto)
    if (viewport.scale > 1.5) {
        drawGrid();
    }
}

function drawGrid() {
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctx.lineWidth = 1;
    
    for (let i = 0; i < canvas.width; i += 50 * viewport.scale) {
        ctx.beginPath();
        ctx.moveTo(i, 0);
        ctx.lineTo(i, canvas.height);
        ctx.stroke();
    }
    
    for (let i = 0; i < canvas.height; i += 50 * viewport.scale) {
        ctx.beginPath();
        ctx.moveTo(0, i);
        ctx.lineTo(canvas.width, i);
        ctx.stroke();
    }
}

// ============ Initialization ============

// Renderiza canvas vazio inicial
render();

console.log('🚀 Cliente de visualização carregado!');
