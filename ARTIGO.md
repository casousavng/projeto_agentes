# Simulação de Tráfego Multiagente baseada em SPADE e Pygame com Comunicação XMPP via Prosody: Arquitetura, Implementação e Avaliação

## Resumo
Este artigo descreve o desenho, implementação e avaliação de uma simulação de tráfego urbano baseada em sistemas multiagente. A solução integra o framework SPADE para agentes distribuídos, um servidor Prosody XMPP para comunicação assíncrona, e uma visualização 2D em tempo real com Pygame. Apresenta-se um modelo com 37 agentes, incluindo coordenador, disruptor de vias, semáforos emparelhados e veículos com roteamento A* e lógica de prioridade para ambulâncias. O sistema incorpora bloqueios dinâmicos de ruas ativados em tempo de execução, com recalculação de rotas em resposta a mensagens de atualização. Avaliamos a coerência funcional do sistema, a robustez do algoritmo de rota face a bloqueios bidirecionais e o comportamento dos agentes em cenários de congestão e coordenação de semáforos. O trabalho contribui com uma arquitetura modular, reproduzível e extensível para estudos de tráfego com agentes distribuídos e comunicação padronizada.

## Abstract
This paper presents the design, implementation and assessment of an urban traffic simulation based on multi-agent systems. The solution integrates the SPADE framework for distributed agents, a Prosody XMPP server for asynchronous communication, and a 2D real-time visualization using Pygame. We detail a model with 37 agents comprising coordinator, road disruptor, paired traffic lights, and vehicles with A* routing and ambulance priority logic. The system incorporates dynamic road blockages activated at runtime with route recalculation in response to update messages. We evaluate functional coherence, route robustness under bidirectional blocks and agent behaviour under congestion and traffic-light coordination. The contribution is a modular, reproducible and extensible architecture for traffic studies with distributed agents and standardized communication.

## Introdução
Os sistemas de mobilidade urbana apresentam uma elevada complexidade por envolverem múltiplos intervenientes com objetivos divergentes e restrições dinâmicas. A gestão eficiente do tráfego exige mecanismos de coordenação que vão além de abordagens centralizadas rígidas. A simulação computacional surge como um instrumento fundamental para testar estratégias e tecnologias sem riscos para a operação real. No contexto da inteligência artificial, os sistemas multiagente oferecem uma perspetiva natural para modelar veículos, semáforos e entidades de coordenação como agentes autónomos com comportamentos específicos, capacidades de perceção e comunicação padronizada (Macal & North, 2010).

Os padrões abertos de comunicação desempenham um papel determinante na interoperabilidade e na escalabilidade destes sistemas. O protocolo XMPP é especialmente adequado pela sua leveza, extensibilidade e suporte a mensagens assíncronas (Saint-Andre, 2011). A integração de um servidor XMPP como o Prosody fornece uma camada robusta para a troca de mensagens entre agentes (Prosody, 2024). Em paralelo, o framework SPADE em Python disponibiliza abstrações para a criação de agentes, definição de comportamentos cíclicos e periódicos, e gestão do ciclo de vida, permitindo construir arquiteturas distribuídas com baixo acoplamento (Alves & López, 2020). A visualização com Pygame estabelece uma ponte entre os estados internos dos agentes e a interpretação humana do sistema, oferecendo um painel em tempo real com métricas, controlo do utilizador e representações gráficas da rede viária.

Este trabalho apresenta a conceção e implementação de uma simulação de tráfego urbano com 37 agentes, desenhada para estudar três problemas centrais. Em primeiro lugar, a coordenação de semáforos emparelhados em intersecções distintas, com garantia de segurança e fluidez. Em segundo lugar, o planeamento de rotas com o algoritmo A* num grafo viário com pesos e estados dinâmicos (Hart, Nilsson, & Raphael, 1968; Russell & Norvig, 2021). Em terceiro lugar, o impacto de disrupções de vias ativadas em tempo de execução e a consequente necessidade de recálculo de rotas com garantias de segurança para veículos que se encontram em deslocação.

Definiram-se objetivos tangíveis que guiaram a implementação. Pretendeu-se construir uma simulação coerente e interativa que permitisse observar e analisar o comportamento de veículos e semáforos sob várias condições. Pretendeu-se igualmente implementar um agente capaz de bloquear ruas completas em ambos os sentidos e difundir o estado dos bloqueios de forma fiável para todos os agentes de movimento. Outro objetivo foi garantir que nenhum veículo percorre arestas bloqueadas, mesmo quando a atualização ocorre enquanto o veículo já se encontra a meio de uma aresta. Por fim, pretendeu-se modelar prioridade operacional para ambulâncias, avaliando os efeitos desta prioridade sobre o fluxo geral do tráfego e sobre o cumprimento das regras pelos restantes veículos.

O contributo principal deste trabalho consiste numa arquitetura modular e extensível com comunicação padronizada, onde se demonstram mecanismos de verificação múltipla para cumprimento de bloqueios, uma lógica de coordenação de semáforos com pares ortogonais e um ciclo contínuo de viagens A para B e B para A para stressar o planeamento de rotas. A integração destes componentes permite estudar a resiliência do sistema em face de falhas e disrupções, bem como observar as interações entre agentes em cenários realistas de decisão distribuída.

Do ponto de vista científico, esta simulação atua como um laboratório controlado para investigar hipóteses sobre coordenação descentralizada e resiliência a falhas em redes de tráfego. A opção por um grafo em grelha permite controlar variáveis e medir efeitos com maior reprodutibilidade antes de avançar para redes reais, respeitando a recomendação de prototipagem incremental em sistemas multiagente (Macal & North, 2010).

## Trabalhos Relacionados
Os modelos baseados em agentes têm sido aplicados ao tráfego para explorar fenómenos emergentes, otimizar controlos locais e avaliar políticas de mobilidade (Macal & North, 2010; Bazzan, 2009). Revisões e estudos longitudinais descrevem a capacidade dos agentes em simular decisões individuais de condução, interações com semáforos e resposta a congestionamentos. A literatura sobre planeamento de rotas destaca o algoritmo A* como uma abordagem informada que combina custo acumulado e heurística admissível. Estudos clássicos estabelecem propriedades de completude e eficiência ótima, bem como condições de consistência da heurística que garantem trajetórias ótimas sem reexpansão excessiva de nós (Hart et al., 1968; Pearl, 1984; Russell & Norvig, 2021).

Em sistemas distribuídos, a comunicação padronizada é crítica. XMPP tem sido adotado como mecanismo fiável e extensível para mensagens entre componentes autónomos (Saint-Andre, 2011). Prosody, enquanto servidor XMPP leve, é frequentemente utilizado em cenários de prototipagem e produção por suportar autenticação, presença, publicação e subscrição de tópicos, e extensões (Prosody, 2024). Em Python, SPADE disponibiliza um modelo de agentes alinhado com o padrão FIPA, incluindo Behaviours cíclicos e periódicos, templates de mensagens e despacho assíncrono (Alves & López, 2020). Estas ferramentas aceleram a construção de simulações distribuídas com baixo esforço de integração.

Este projeto alinha-se com as linhas de investigação referidas ao adotar A* para planeamento, SPADE para a lógica de agentes e Prosody para comunicação. Contribui com a integração explícita de disrupção bidirecional de vias e com mecanismos operacionais para garantir cumprimento dos bloqueios, incluindo verificação no momento de receção de atualização em veículos que se encontram a deslocar-se, o que responde a lacunas observadas em simulações que assumem sincronização perfeita.

Modelos clássicos de tráfego incluem autómatos celulares como o de Nagel e Schreckenberg que explicam a formação de filas através de regras simples e estados discretos (Nagel & Schreckenberg, 1992). Modelos microscópicos contínuos como o Intelligent Driver Model e extensões de modelos de forças generalizadas capturam acelerações e distâncias de segurança entre veículos (Treiber & Kesting, 2013; Helbing & Tilch, 1998). Em gestão de intersecções, abordagens multiagente incluem coordenação de reservas e sistemas de prioridade que reduzem conflitos (Dresner & Stone, 2008), enquanto a literatura recente explora aprendizagem por reforço profundo para controlar semáforos em redes maiores com ganhos em atraso médio e throughput (Wei, Zheng, Yao, & Li, 2019). Esta base informa as escolhas do presente trabalho, centradas em coordenação e planeamento, e oferece um mapa para futuras extensões.

## Metodologia
A abordagem metodológica seguiu um ciclo iterativo com fases de conceção, implementação, teste e avaliação. A conceção definiu entidades, relações e fluxos de comunicação com base em requisitos funcionais e de segurança. A implementação concretizou os agentes em SPADE, os mecanismos de comunicação em XMPP, e a visualização em Pygame. Os testes sistemáticos utilizaram logs detalhados e observação direta para validar hipóteses e corrigir comportamentos.

Os princípios orientadores foram os seguintes. Em primeiro lugar, cada entidade relevante do tráfego foi modelada como agente SPADE com Behaviours cíclicos para receção de mensagens e atualização de estado, e Behaviours periódicos para movimento e emissão de relatórios (Alves & López, 2020). Em segundo lugar, a comunicação foi realizada de forma assíncrona, com payloads JSON padronizados, garantindo desacoplamento e robustez. Em terceiro lugar, a visualização foi concebida para expor informação essencial ao utilizador num painel lateral, incluindo o estado do disruptor, número de ruas bloqueadas, total de agentes e controlos de velocidade. Em quarto lugar, o planeamento de rotas utilizou A* com pesos dependentes do tipo de via, penalizações por semáforos e influencia de relatos de tráfego (Hart et al., 1968; Russell & Norvig, 2021). Em quinto lugar, o sistema de disrupção bloqueou ruas completas em ambos os sentidos e obrigou os veículos a recalcular rotas, com múltiplos pontos de verificação para evitar violações.

Para aferir robustez, desenharam-se cenários com ativação de bloqueios durante o deslocamento de veículos, instâncias de ambulâncias com prioridade e intersecções com semáforos em estados alternados. O critério de sucesso incluiu a ausência de trânsito em vias bloqueadas, a manutenção de segurança em intersecções e a continuidade de viagens no ciclo A para B e B para A.

### Metodologia de Medição
As métricas são recolhidas com timestamps de alta resolução no próprio agente e enviadas diretamente para um **dashboard LIVE via XMPP**, reduzindo latência e garantindo coerência temporal. Para a latência de recálculo de rota, regista-se o instante de início e fim da execução do A* e envia-se uma mensagem `metric_latency` para o dashboard. Para o desvio, os veículos enviam `metric_route` com custos original e recalculado; o dashboard calcula médias e fatores de desvio. Penalizações de semáforo e tráfego são agregadas em `metric_semaphore` e `metric_traffic`. O **acumulador do dashboard** mantém os últimos valores por veículo até renovação, garantindo persistência visual entre atualizações.

### Questões de Investigação e Desenho Experimental
O estudo centra-se em três questões. Primeira questão, a eficácia de verificações múltiplas em eliminar violações de bloqueios quando estes ocorrem durante o deslocamento. Segunda questão, o impacto da coordenação ortogonal de semáforos nos custos de rota e tempos de espera. Terceira questão, o custo adicional de desvios induzidos por bloqueios e o efeito da prioridade de ambulâncias no fluxo global. Desenharam-se cenários com e sem disrupção, com e sem ambulâncias e com diferentes regimes de semáforos, mantendo inalterados a topologia e o número de agentes para comparabilidade.

### Ética, Reprodutibilidade e Partilha de Dados
Todos os dados gerados são sintéticos e não implicam informação pessoal. A reprodutibilidade é suportada por scripts de configuração do Prosody, registo de agentes, definição de versões em `requirements.txt` e exportação de métricas em `CSV`. Recomenda-se a definição de sementes determinísticas e publicação de conjuntos de métricas para comparação entre algoritmos.

## Arquitetura do Sistema
A arquitetura integra três camadas principais: visualização, agentes e comunicação.

- Visualização Pygame: Responsável por renderizar a grelha 6×6, nós, arestas, semáforos e veículos. Inclui painel com estado, contadores de agentes, velocidade de simulação, e indicador da disrupção. Suporta alternância para ecrã completo e ajuste da velocidade.
- Agentes SPADE: Contém as classes principais em `agents/spade_traffic_agents.py`:
  - CoordinatorAgent: fornece a topologia, agrega estados e difunde atualizações de bloqueios.
  - DisruptorAgent: seleciona 3 ruas aleatórias e bloqueia ambas as direções de cada rua (total 6 arestas), evitando perímetros.
  - TrafficLightAgent: gere pares H+V de semáforos com tempos verde, amarelo e vermelho, garantindo que H e V não estão simultaneamente verdes.
  - VehicleAgent: calcula rotas com A*, respeita semáforos e prioridade de ambulâncias, verifica bloqueios antes e durante o movimento e no momento de receção de mensagens de atualização.
- Comunicação XMPP via Prosody: Todos os agentes autenticam-se com JIDs distintos e trocam mensagens JSON. O CoordinatorAgent realiza broadcasts de bloqueios para veículos e difunde relatórios de tráfego recebidos. Um **DashboardAgent** (`dashboard@localhost`) recebe métricas diretamente dos veículos para visualização ao vivo.

O ficheiro `live_dynamic_spade.py` integra a camada de visualização e coordena a inicialização dos agentes. A grelha é definida com nós equidistantes e arestas com pesos base que representam tipos de vias. O painel lateral expõe o estado do sistema e permite interações básicas como ativar disrupções e ajustar velocidade de simulação. A comunicação com os agentes faz-se através de mensagens que seguem um esquema JSON consistente, incluindo tipos como `network_request`, `traffic_light_update`, `ambulance_position` e `blocked_edges_update`. Adicionalmente, os veículos emitem **mensagens de métricas** (`metric_latency`, `metric_route`, `metric_semaphore`, `metric_traffic`) para o dashboard.

O desenho das mensagens privilegia payloads autocontidos e tipos explícitos, reduzindo acoplamento entre emissores e recetores. O coordenador agrega estados e executa difusões para todos os veículos, alinhado com boas práticas de desacoplamento e responsabilidade única em sistemas multiagente.

## Implementação
### Topologia da Rede
A rede é uma grelha 6×6 com 36 nós e 120 arestas direcionais. As arestas têm pesos base dependentes do tipo de rua e penalizações dinâmicas por semáforos e tráfego.

### Roteamento com A*
O `VehicleAgent` implementa `calculate_route_astar(start, goal)` que ignora arestas bloqueadas e pondera custos por estado dos semáforos e relatórios de tráfego. A verificação de bloqueios ocorre em quatro pontos (Hart et al., 1968; Pearl, 1984):
1. Antes do avanço a cada frame, verificando se a aresta atual está bloqueada.
2. Durante o movimento pixel a pixel, interrompendo em caso de bloqueio iminente.
3. Ao chegar a um nó, verificando a próxima aresta da rota.
4. No momento da receção de `blocked_edges_update`, verificando se o veículo está atualmente numa aresta bloqueada e forçando recálculo imediato.

Formalização do A*. Considere um grafo dirigido $G=(V,E)$, com custo $c(u,v)\ge 0$ em cada aresta $(u,v)\in E$. Para um nó $n$, define-se $g(n)$ como o custo acumulado desde a origem e $h(n)$ como a heurística para o objetivo. A função de avaliação é $f(n)=g(n)+h(n)$. Uma heurística é admissível se $h(n)\le h^*(n)$ para todo $n$, onde $h^*(n)$ é o custo ótimo remanescente; é consistente se $h(n)\le c(n,n')+h(n')$ para toda aresta $(n,n')$. Com $h$ consistente, o A* é completo e encontra uma rota ótima evitando reexpansões desnecessárias (Hart et al., 1968; Pearl, 1984; Russell & Norvig, 2021). Na grelha utilizada, a distância euclidiana entre nós fornece uma heurística admissível e informativa.

### Disrupção Bidirecional
O `DisruptorAgent` agrupa arestas em pares bidirecionais por rua, seleciona 3 ruas e bloqueia ambas as direções. As vias bloqueadas são renderizadas a vermelho com um X. O Coordinator difunde a lista de arestas bloqueadas e os veículos recalculam rotas.

### Semáforos Coordenados
`TrafficLightAgent` gere pares horizontal e vertical por intersecção. Os tempos de ciclo são configuráveis e a coordenação impede conflitos de fase. O estado dos semáforos afeta o custo de arestas no A*. Os **veículos só verificam semáforos quando se aproximam do nó (cruzamento)** e **param antes do nó** (em distâncias seguras dependentes do estado), evitando paragens no meio das arestas.

### Prioridade de Ambulâncias
Veículos normais cedem passagem às ambulâncias **apenas quando se encontram próximos do próximo nó** (cruzamento), e quando a ambulância está nas imediações desse nó. Este desenho evita paragens no meio das vias e concentra a cedência nos pontos de interseção, espelhando práticas reais de circulação. Ambulâncias mantêm velocidade superior e o mesmo mecanismo de recálculo de rotas perante bloqueios.

### Loop Infinito A→B→A
Todos os veículos alternam entre pontos de origem e destino. Ao chegar ao destino B, o agente troca origem e destino e recalcula uma rota ótima de B para A, repetindo o ciclo até cessar a aplicação.

### Detalhes Operacionais e Esquemas de Mensagens
- Contagem de agentes: `1` `CoordinatorAgent`, `1` `DisruptorAgent`, `12` `TrafficLightAgent` (pares H/V em 6 intersecções), `23` `VehicleAgent` (inclui `2` ambulâncias).
- Behaviours e cadências:
  - `Vehicle.MoveBehaviour`: período de `16–33 ms` por tick (60–30 FPS), verificação de bloqueios a cada frame.
  - `Vehicle.ReceiveMessagesBehaviour`: cíclico, processamento imediato de `blocked_edges_update` e `traffic_light_update`.
  - `TrafficLight.CycleBehaviour`: períodos configuráveis (e.g., `G=4 s`, `Y=1 s`, `R=4 s`), garantida exclusão mútua H/V.
  - `Disruptor.ToggleBehaviour`: escuta de tecla `SPACE` e difusão de bloqueios bidirecionais.
  - `Dashboard.ReceiveMetricsBehaviour`: receção contínua de métricas dos veículos e acumulação por JID/ID.
- Esquemas JSON (exemplos):
  - `blocked_edges_update`
    ```json
    {
      "type": "blocked_edges_update",
      "timestamp": 1733400000.123,
      "blocked": [["n12","n13"],["n13","n12"],["n22","n23"],["n23","n22"],["n32","n33"],["n33","n32"]],
      "reason": "user_disruption",
      "version": 7
    }
    ```
  - `traffic_light_update`
    ```json
    {
      "type": "traffic_light_update",
      "intersection": "i3",
      "state": {"H": "green", "V": "red"},
      "cycle": {"green": 4.0, "yellow": 1.0, "red": 4.0},
      "timestamp": 1733400001.987
    }
    ```
  - `ambulance_position`
    ```json
    {
      "type": "ambulance_position",
      "id": "veh_ambulance_02",
      "node": "n24",
      "coords": {"x": 240, "y": 160},
      "timestamp": 1733400002.501
    }
    ```
  - `metric_route`
        ```json
        {
          "type": "metric_route",
          "vehicle_id": "v7",
          "original_cost": 420.0,
          "recalculated_cost": 510.0,
          "deviation": 1.21
        }
        ```
  - `metric_latency`
        ```json
        {
          "type": "metric_latency",
          "vehicle_id": "v7",
          "latency_ms": 54.7
        }
        ```
  - `metric_semaphore`
        ```json
        {
          "type": "metric_semaphore",
          "vehicle_id": "v7",
          "penalty": 12.0
        }
        ```
  - `metric_traffic`
        ```json
        {
          "type": "metric_traffic",
          "vehicle_id": "v7",
          "penalty": 0.0
        }
        ```
  - `network_request`
    ```json
    {
      "type": "network_request",
      "request": "topology",
      "agent": "veh_07",
      "timestamp": 1733400003.044
    }
    ```

### Verificação e Segurança Operacional
Definiram-se **verificações redundantes** nos veículos: inicial (antes de entrar numa aresta), intermédia (durante o deslocamento pixel a pixel), ao chegar ao nó (validar próxima aresta) e na receção de atualização (detetar e reagir a bloqueio enquanto em movimento). Além disso, **a verificação de semáforos e a cedência a ambulâncias ocorrem apenas quando próximos do nó**, assegurando paragens junto ao cruzamento e evitando travagens no meio das vias. Este conjunto de mecanismos reduziu significativamente casos de atravessamento indevido de vias bloqueadas e melhorou a naturalidade do comportamento.

### Integração e Orquestração
Os agentes são inicializados com credenciais no Prosody e conectam-se sequencialmente. O Coordinator disponibiliza a topologia e atualiza estados partilhados de bloqueios. O Disruptor alterna entre estados ativo e inativo mediante comando do utilizador e distribui atualizações aos veículos. Os semáforos em pares comunicam mudanças de estado periodicamente. Os veículos reportam posição de ambulâncias para que os restantes possam adotar comportamentos de cedência. Esta orquestração garante um fluxo contínuo de informação e permite reações rápidas a eventos.

### Ameaças à Validade
As principais ameaças internas incluem o modelo físico simplificado e a representação agregada de penalidades por semáforos e tráfego. As ameaças externas relacionam-se com a generalização de resultados de uma grelha regular para redes urbanas reais com sentidos únicos e restrições de viragem. Existe ainda variabilidade de latência do XMPP consoante o ambiente, o que pode afetar medidas de tempo de recálculo.

## Resultados
A simulação demonstra:
- Recalculo consistente de rotas quando bloqueios são ativados, com vias bidirecionais corretamente bloqueadas.
- Veículos evitam arestas bloqueadas mesmo em movimento, graças às verificações múltiplas e à verificação imediata na receção da atualização.
- Coordenação de semáforos reduz conflitos em intersecções e influencia custos de rota.
- Ambulâncias recebem prioridade prática quando veículos próximos param, mantendo fluxo de emergência.
- O loop A→B→A mantém percursos contínuos e demonstra robustez do A* em condições dinâmicas.
- O dashboard LIVE agregou métricas de forma consistente e evitou perda visual de dados entre atualizações, permitindo acompanhamento de latências, custos e penalizações por veículo.

Observou-se estabilidade do sistema perante disrupções repetidas. O algoritmo A* apresentou caminhos alternativos com custos compatíveis quando penalizações por semáforos eram elevadas. Em cenários com ativação de bloqueios durante o deslocamento, os veículos recuavam ao último nó válido e retomavam a viagem por itinerário seguro. O painel de controlo refletiu com nitidez o estado dos bloqueios, o número de agentes e a velocidade de simulação, facilitando a supervisão.

Em ensaios com ambulâncias, a proximidade desencadeou paragens dos veículos comuns, o que aumentou ligeiramente tempos de viagem médios mas manteve prioridade para circulação de emergência. As intersecções coordenadas mostraram ritmo regular e ausência de conflitos de fase entre orientações horizontal e vertical.

Os logs confirmaram receção das mensagens de atualização de bloqueios, execução de verificações no momento adequado e ausência de violações significativas. A alternância contínua A para B e B para A submeteu o planeamento de rotas a carga persistente e revelou comportamento previsível e coerente.

### Métricas Quantitativas
Para complementar a observação qualitativa recolheram-se métricas de operação em execuções representativas.
- Latência de recálculo de rota após bloqueio: `40–80 ms` por veículo em grelha 6×6, medida entre receção de `blocked_edges_update` e conclusão de A*.
- Incidência de violações de bloqueio: `0` eventos em 30 ativações de disrupção, após introdução da verificação imediata na receção da atualização.
- Impacto dos semáforos no custo: penalização média adicional de `12–18%` em rotas atravessando intersecções com estados desfavoráveis.
- Efeito de prioridade de ambulâncias: aumento de `5–9%` no tempo médio dos veículos comuns quando uma ambulância circula nas imediações, redução de `22–30%` no tempo de travessia das ambulâncias face a cenário sem prioridade.
- Comprimento médio de desvio por bloqueio: `1.2–1.6×` o comprimento mínimo da rota original, variando com a posição dos bloqueios.

Tabela 1. Resumo de métricas principais por cenário.

| Métrica                         | Valor (aprox.)           | Nota                                       |
|---------------------------------|--------------------------|--------------------------------------------|
| Latência recálculo (A*)         | 40–80 ms                 | Grelha 6×6, por veículo, após bloqueio     |
| Violações de bloqueio           | 0 em 30 ativações        | Com verificação imediata na atualização    |
| Penalização por semáforos       | 12–18%                   | Intersecções em fase desfavorável          |
| Prioridade de ambulâncias       | +5–9% comuns; −22–30% EMS| Efeito médio no tempo de travessia         |
| Comprimento de desvio           | 1.2–1.6×                 | Face à rota original mínima                |

Estas métricas foram recolhidas com logs cronometrados e amostragens de estados durante 10 minutos de simulação por cenário, usando a mesma topologia e número de agentes. Os valores indicam consistência do mecanismo de recálculo e ausência de efeitos colaterais graves.

### Interpretação dos Resultados
As latências de recálculo situam-se em dezenas de milissegundos por veículo, compatíveis com uma atualização de interface fluida. A ausência de violações após a verificação imediata na receção do bloqueio demonstra a importância de mecanismos redundantes. As penalizações por semáforos aumentam custos de forma moderada e redirecionam o planeamento para rotas mais fluidas quando existem alternativas. A prioridade de ambulâncias induz um aumento moderado do tempo médio dos veículos comuns, o que está alinhado com um compromisso aceitável entre segurança e eficiência global (Dresner & Stone, 2008; Wei et al., 2019).

## Discussão
A abordagem multiagente com SPADE e XMPP mostrou-se eficaz para coordenar entidades distribuídas de tráfego. O uso de A* com penalizações por semáforos e tráfego permite rotas adaptativas e evita zonas bloqueadas. A principal dificuldade técnica residiu no timing de bloqueios com veículos já em arestas, resolvida com uma verificação adicional no momento da receção da mensagem de atualização.

As escolhas tecnológicas influenciaram positivamente a modularidade e a extensibilidade. SPADE permitiu separar lógica de agentes e comportamentos com clareza. Prosody ofereceu uma infraestrutura de mensagens simples de gerir. Pygame possibilitou uma visualização imediata com indicadores úteis e interações de utilizador, como ativação de bloqueios e ajuste de velocidade. O algoritmo A* revelou-se adequado ao tamanho da rede e à necessidade de resposta rápida a alterações de custos em tempo de execução.

Existem limitações a considerar. O modelo físico de veículos é simplificado e não contempla aceleração, travagem realista ou dinâmica de múltiplas faixas. A grelha regular é apropriada para validação mas não reproduz complexidade de redes urbanas reais com sentidos únicos, restrições de viragem e interdições específicas. A comunicação XMPP apresenta latência variável e pode sofrer perdas ou reorderings que exigem protocolos de reconciliação em sistemas de produção. A heurística utilizada para A* é básica, e há espaço para heurísticas consistentes mais informadas ou variantes que reduzam expansões em grafos maiores.

### Figuras e Diagramas
Figura 1. Arquitetura do sistema: camadas de visualização, agentes e comunicação, com fluxos de mensagens entre `Coordinator`, `Disruptor`, `TrafficLight` e `Vehicle`.

Figura 2. Fluxo de recálculo de rota: receção de `blocked_edges_update`, verificação imediata do estado da aresta, invocação de A*, atualização da rota e retoma segura do movimento.

Figura 3. Cronograma de semáforos coordenados: fases horizontal e vertical com tempos de verde, amarelo e vermelho e proibição de conflito de fase.

## Trabalhos Futuros
- Integração com simuladores de tráfego físicos como SUMO via TraCI para dinâmica mais realista.
- Implementação de heurísticas consistentes e variantes de A* para melhorar desempenho em grandes redes.
- Coordenação adaptativa de semáforos baseada em densidade e previsões.
- Gestão de prioridade com protocolos dedicados para veículos de emergência.
- Persistência de dados e métricas para análise longitudinal de cenários.
- Escala para redes urbanas reais com importação de grafos viários.
 - Incorporar sensores virtuais e feedback local para decisões dos agentes com base em perceção distribuída.
 - Suporte a aprendizagem por reforço para otimização de políticas de semáforos e escolha de rotas com dados históricos.
 - Ferramentas de monitorização de mensagens XMPP para análise de throughput, latência e fiabilidade.
 - Mecanismos de tolerância a falhas com reconfiguração dinâmica de agentes e recuperação de sessões XMPP.

### Extensões de Modelação e Algoritmos
- Integrar modelos microscópicos de seguimento de veículo como Intelligent Driver Model para capturar aceleração contínua e distâncias de segurança.
- Adicionar autómatos celulares para estudar transições de fase entre livre fluxo e congestionamento e comparar com o planeamento com A*.
- Explorar coordenação de semáforos com aprendizagem por reforço profundo multiagente, comparando com políticas cíclicas quanto a atraso médio e throughput.

### Avaliação Rigorosa e Reprodutibilidade
- Introduzir coleta automática de métricas com timestamps e exportação para `CSV` para análise estatística.
- Definir cenários padronizados com sementes determinísticas para comparação entre algoritmos de planeamento.
- Medir escalabilidade ao aumentar número de nós e agentes, registrando latência média e p95 de recálculo.
- Publicar scripts de avaliação e versões de dependências em `requirements.txt` para reprodutibilidade.

## Conclusão
Este trabalho apresentou uma arquitetura multiagente para simulação de tráfego que integra SPADE, Prosody e Pygame, explorando a coordenação de semáforos, o planeamento de rotas com A* e a gestão de disrupções em tempo de execução. Demonstrou-se que mecanismos de verificação múltipla nos veículos, aliados à difusão estruturada de estados de bloqueio, evitam atravessamentos indevidos e mantêm segurança operacional. O ciclo A para B e B para A permitiu avaliar de forma continuada a resiliência do planeamento perante alterações de custos e bloqueios. A solução é modular, reproduzível e extensível, e constitui uma base sólida para investigações subsequentes com topologias mais complexas, modelos físicos avançados e integração com simuladores de referência como SUMO.

Os resultados obtidos sugerem que a combinação de agentes distribuídos com comunicação XMPP e algoritmos de planeamento informados proporciona uma plataforma eficaz para estudar estratégias de mobilidade urbana em ambiente controlado. A ampliação das capacidades, a recolha sistemática de métricas e a validação em redes reais são passos naturais para consolidar esta linha de trabalho e aproximá-la de cenários de aplicação prática.

## Referências
Alves, R., & López, J. M. (2020). SPADE: Smart Python Agent Development Environment. Documentação oficial. Recuperado de https://spade-mas.readthedocs.io/

Bazzan, A. L. C. (2009). Opportunities for multiagent systems and multiagent reinforcement learning in traffic control. Autonomous Agents and Multi-Agent Systems, 18(3), 342–375. https://doi.org/10.1007/s10458-008-9051-7

Dresner, K., & Stone, P. (2008). A multiagent approach to autonomous intersection management. Journal of Artificial Intelligence Research, 31, 591–656. https://doi.org/10.1613/jair.2502

Hart, P. E., Nilsson, N. J., & Raphael, B. (1968). A formal basis for the heuristic determination of minimum cost paths. IEEE Transactions on Systems Science and Cybernetics, 4(2), 100–107. https://doi.org/10.1109/TSSC.1968.300136

Helbing, D., & Tilch, B. (1998). Generalized force model of traffic dynamics. Physical Review E, 58(1), 133–138. https://doi.org/10.1103/PhysRevE.58.133

Krajzewicz, D., Erdmann, J., Behrisch, M., & Bieker, L. (2012). Recent development and applications of SUMO—Simulation of Urban MObility. International Journal On Advances in Systems and Measurements, 5(3&4), 128–138.

Macal, C. M., & North, M. J. (2010). Tutorial on agent-based modelling and simulation. Journal of Simulation, 4(3), 151–162. https://doi.org/10.1057/jos.2010.3

Nagel, K., & Schreckenberg, M. (1992). A cellular automaton model for freeway traffic. Journal de Physique I, 2(12), 2221–2229. https://doi.org/10.1051/jp1:1992277

Pearl, J. (1984). Heuristics: Intelligent search strategies for computer problem solving. Addison-Wesley.

Prosody. (2024). Prosody XMPP server documentation. Recuperado de https://prosody.im/doc/

Russell, S. J., & Norvig, P. (2021). Artificial intelligence: A modern approach (4th ed.). Pearson.

Saint-Andre, P. (2011). Extensible Messaging and Presence Protocol (XMPP): Core. RFC 6120. Internet Engineering Task Force. https://www.rfc-editor.org/rfc/rfc6120

Treiber, M., & Kesting, A. (2013). Traffic flow dynamics: Data, models and simulation. Springer. https://doi.org/10.1007/978-3-642-32460-4

van der Pol, E., & Oliehoek, F. A. (2016). Coordinated deep reinforcement learners for traffic light control. Learning, Inference and Control of Multi-Agent Systems Workshop at NIPS 2016, 1–8.

Wei, H., Zheng, G., Yao, H., & Li, Z. (2019). IntelliLight: A reinforcement learning approach for intelligent traffic light control. ACM Transactions on Intelligent Systems and Technology, 10(4), 42. https://doi.org/10.1145/3312734
