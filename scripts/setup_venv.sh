#!/bin/bash
# Script para criar ambiente virtual e instalar dependências

echo "🐍 Configurando ambiente Python..."

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale Python 3.9 ou superior."
    exit 1
fi

# Verificar versão do Python
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "📌 Python version: $PYTHON_VERSION"

# Criar ambiente virtual
if [ -d "venv" ]; then
    echo "⚠️  Ambiente virtual já existe. Deseja recriar? (s/N)"
    read -r response
    if [[ "$response" =~ ^[Ss]$ ]]; then
        rm -rf venv
        python3 -m venv venv
    fi
else
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo "🔌 Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar pip
echo "⬆️  Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
echo "📥 Instalando dependências..."
pip install -r requirements.txt

echo ""
echo "✅ Ambiente Python configurado com sucesso!"
echo ""
echo "Para ativar o ambiente virtual:"
echo "   source venv/bin/activate"
echo ""
echo "Para desativar:"
echo "   deactivate"
