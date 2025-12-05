#!/usr/bin/env zsh
#
# Script para iniciar a simulação de tráfego SPADE e o dashboard de métricas
# Uso: ./start_simulation.sh
#

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Diretório do projeto
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

echo "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "${CYAN}🚦 Simulação de Tráfego Multiagente SPADE${NC}"
echo "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 1. Verificar se venv existe
if [ ! -d "venv" ]; then
    echo "${RED}❌ Ambiente virtual 'venv' não encontrado!${NC}"
    echo "${YELLOW}💡 Crie o ambiente virtual primeiro:${NC}"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# 2. Verificar se Prosody está rodando
if ! docker ps | grep -q prosody; then
    echo "${YELLOW}⚠️  Prosody XMPP não está rodando!${NC}"
    echo "${CYAN}🚀 A iniciar Prosody...${NC}"
    ./scripts/setup_prosody.sh
    
    if [ $? -ne 0 ]; then
        echo "${RED}❌ Falha ao iniciar Prosody!${NC}"
        exit 1
    fi
    
    echo "${GREEN}✅ Prosody iniciado com sucesso!${NC}"
    echo "${YELLOW}⏳ A aguardar 3 segundos para o Prosody estabilizar...${NC}"
    sleep 3
else
    echo "${GREEN}✅ Prosody já está rodando${NC}"
fi

# 3. Verificar se os agentes estão registrados
AGENT_COUNT=$(docker exec prosody prosodyctl list localhost 2>/dev/null | wc -l)
if [ "$AGENT_COUNT" -lt 30 ]; then
    echo "${YELLOW}⚠️  Agentes não registrados ou incompletos!${NC}"
    echo "${CYAN}📝 A registrar agentes...${NC}"
    ./scripts/register_10_paired_lights.sh
    
    if [ $? -ne 0 ]; then
        echo "${RED}❌ Falha ao registrar agentes!${NC}"
        exit 1
    fi
    
    echo "${GREEN}✅ Agentes registrados com sucesso!${NC}"
else
    echo "${GREEN}✅ Agentes já estão registrados (${AGENT_COUNT} agentes)${NC}"
fi

echo ""
echo "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "${GREEN}🎮 A iniciar simulação e dashboard...${NC}"
echo "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "${YELLOW}📊 Dashboard de métricas será aberto num novo terminal${NC}"
echo "${YELLOW}🎮 Simulação principal neste terminal${NC}"
echo ""
echo "${CYAN}Controlos da simulação:${NC}"
echo "  ${GREEN}ESPAÇO${NC}   - Ativar/Desativar bloqueios de vias"
echo "  ${GREEN}F11${NC}      - Alternar tela cheia"
echo "  ${GREEN}+/-${NC}      - Ajustar velocidade (2x-5x)"
echo "  ${GREEN}ESC${NC}      - Sair"
echo ""
echo "${CYAN}Para encerrar:${NC}"
echo "  ${GREEN}Ctrl+C${NC}   - Neste terminal (fecha simulação)"
echo "  ${GREEN}Ctrl+C${NC}   - No terminal do dashboard (fecha dashboard)"
echo ""
echo "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 4. Determinar o terminal emulator disponível
if command -v osascript &> /dev/null; then
    # macOS - usar Terminal.app ou iTerm
    echo "${CYAN}🍎 Detectado macOS - a abrir dashboard em novo terminal...${NC}"
    osascript <<EOF
tell application "Terminal"
    activate
    do script "cd '$PROJECT_DIR' && source venv/bin/activate && echo '📊 Dashboard de Métricas' && echo '' && python dashboard_metrics.py --refresh 1.5"
end tell
EOF
    sleep 2
elif command -v gnome-terminal &> /dev/null; then
    # Linux com GNOME
    echo "${CYAN}🐧 Detectado GNOME - a abrir dashboard em novo terminal...${NC}"
    gnome-terminal -- bash -c "cd '$PROJECT_DIR' && source venv/bin/activate && echo '📊 Dashboard de Métricas' && echo '' && python dashboard_metrics.py --refresh 1.5; exec bash"
    sleep 2
elif command -v xterm &> /dev/null; then
    # Fallback para xterm
    echo "${CYAN}🐧 A abrir dashboard em xterm...${NC}"
    xterm -e "cd '$PROJECT_DIR' && source venv/bin/activate && echo '📊 Dashboard de Métricas' && echo '' && python dashboard_metrics.py --refresh 1.5" &
    sleep 2
else
    # Sem terminal disponível - instrução manual
    echo "${YELLOW}⚠️  Terminal automático não disponível${NC}"
    echo "${YELLOW}💡 Abra um novo terminal manualmente e execute:${NC}"
    echo "${CYAN}   cd '$PROJECT_DIR'${NC}"
    echo "${CYAN}   source venv/bin/activate${NC}"
    echo "${CYAN}   python dashboard_metrics.py --refresh 1.5${NC}"
    echo ""
    echo "${YELLOW}⏳ A aguardar 5 segundos antes de iniciar a simulação...${NC}"
    sleep 5
fi

# 5. Iniciar a simulação principal
echo "${GREEN}🚀 A iniciar simulação principal...${NC}"
echo ""

# Ativar venv e executar
source venv/bin/activate
python live_dynamic_spade.py

# 6. Cleanup após encerramento
echo ""
echo "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "${YELLOW}👋 Simulação encerrada!${NC}"
echo "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "${CYAN}📊 Para ver métricas geradas:${NC}"
echo "   ls metrics/"
echo "   cat metrics/summary.csv"
echo ""
echo "${CYAN}🧹 Para limpar métricas:${NC}"
echo "   rm -f metrics/*.csv"
echo ""
echo "${GREEN}✅ Obrigado por usar a simulação SPADE!${NC}"
