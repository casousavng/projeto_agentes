#!/bin/bash
# Run simulation with Docker SUMO

# Ativar ambiente virtual
source venv/bin/activate

# Executar simulação em modo Docker
python main_docker.py --docker
