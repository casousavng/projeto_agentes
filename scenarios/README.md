# Cenários SUMO

Este diretório contém cenários de simulação para o SUMO.

## simple_grid

Rede simples em grade 3x3 com:
- 9 intersecções com semáforos
- Ruas horizontais e verticais
- Tipos de veículos: carros normais e veículos de emergência

### Arquivos:
- `network.net.xml`: Definição da rede (nós e edges)
- `routes.rou.xml`: Template de rotas (rotas criadas via TraCI)
- `simulation.sumocfg`: Configuração da simulação

### Criar rede personalizada:

Use o `netedit` do SUMO para criar redes mais complexas:
```bash
netedit
```

Ou use o `netgenerate` para gerar redes automaticamente:
```bash
netgenerate --grid --grid.number=5 --output-file=network.net.xml
```
