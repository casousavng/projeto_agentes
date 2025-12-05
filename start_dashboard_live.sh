#!/bin/bash

# Script para iniciar dashboard XMPP live
echo "🚀 Iniciando Dashboard XMPP Live..."
echo "📊 Dashboard receberá métricas diretamente via mensagens XMPP"
echo "🔄 Atualização: 1.0s"
echo ""

python3 dashboard_live.py --refresh 1.0
