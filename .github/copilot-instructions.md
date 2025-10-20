# Projeto de Simulação de Tráfego Multiagente

## Visão Geral
Este projeto implementa uma simulação de tráfego urbano usando agentes inteligentes com SPADE, SUMO e Prosody XMPP.

## Tecnologias
- **Python 3.9+**: Linguagem principal
- **SPADE**: Framework de agentes baseado em XMPP
- **Prosody**: Servidor XMPP rodando em Docker
- **SUMO**: Simulador de tráfego urbano
- **TraCI**: Interface Python para controlar SUMO
- **X11**: Interface gráfica para SUMO no macOS M1

## Tipos de Agentes
1. **Semáforos (TrafficLight)**: Controlam intersecções
2. **Carros (Car)**: Buscam rotas ótimas entre pontos
3. **Ambulâncias (Ambulance)**: Modo urgência com prioridade
4. **Pedestres (Pedestrian)**: Atravessam ruas

## Arquitetura
- Agentes SPADE se comunicam via Prosody XMPP
- SUMO gerencia a simulação física de tráfego
- TraCI conecta agentes Python ao SUMO
- Docker container para Prosody server

## Desenvolvimento
- Usar ambiente virtual Python (venv)
- Prosody rodando em: `docker run -d --name prosody -p 5222:5222 prosody/prosody`
- Registrar agentes: `docker exec -it prosody prosodyctl register <nome> localhost <senha>`
- SUMO com GUI via X11 no macOS M1
