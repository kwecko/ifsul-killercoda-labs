# Guia do professor — ARP entre redes (com roteador)

## Aplicação sem acompanhamento ao vivo

`arp-roteador` é a continuação natural de `arp`: a mesma técnica (network namespaces + bridges dentro da VM), aplicada a duas sub-redes ligadas por um roteador virtual com encaminhamento IP habilitado. O foco não é mais o mecanismo do ARP em si, mas **onde** ele acontece quando existe um salto de roteamento no meio do caminho — um dos pontos que mais gera confusão em turmas iniciantes ("por que o computador não pergunta o MAC do destino final?").

São cinco etapas práticas, planejadas para 45 minutos, mais 5 de preparação/identificação e 5 de entrega.

| Etapa | Minutos | Critérios técnicos |
|---|---:|---|
| Preparação/identificação | 5 | Duas sub-redes, roteador com IP forwarding, rotas padrão corretas, tabelas ARP vazias |
| 1. Reconhecer a topologia | 5 | Endereços e rotas corretos; `ip_forward=1`; nenhuma entrada ARP |
| 2. A estação só resolve o gateway por ARP | 10 | Captura do lado de A mostra pedido pelo gateway, nunca pelo IP de B; tabela de A só tem o gateway |
| 3. O roteador refaz a resolução na outra rede | 10 | Mesma captura, lado do roteador: pedido com `tell` = IP do roteador, não de A; tabela de B só tem o roteador |
| 4. O endereço de enlace muda a cada salto; o IP não | 10 | ICMP capturado nos dois lados: mesmo par de IPs, MACs diferentes e coerentes com cada segmento |
| 5. Sem rota não há tentativa de ARP | 10 | Rota padrão restaurada e resolvida; relatório com pelo menos 120 caracteres |
| Entrega | 5 | TXT v2 e histórico legível; download antes de encerrar |

## Infraestrutura

`preparar-roteador` cria dois bridges (`br-a`, `br-b`, um por sub-rede) e três *network namespaces*: `estacao-a` (10.77.1.10/24), `estacao-b` (10.77.2.10/24) e `roteador` (10.77.1.1 na interface `rot-a`, ligada a `br-a`; 10.77.2.1 na interface `rot-b`, ligada a `br-b`). O roteador tem `net.ipv4.ip_forward=1`; as estações têm rota padrão para o roteador. `/root/rede.env` define os atalhos `estacao-a`, `estacao-b` e `roteador`.

**Decisão de design importante**: as etapas 2 e 3 capturam **simultaneamente** dos dois lados durante o *primeiro* ping entre as estações (quando as tabelas ainda estão vazias), e a etapa 3 reaproveita a captura do lado do roteador feita na etapa 2 — sem gerar um novo pedido ARP. Isso evita um problema real encontrado no desenvolvimento: depois do primeiro ping bem-sucedido, tanto A quanto o roteador já têm cache, então um segundo ping não gera *nenhum* tráfego ARP novo (a comunicação simplesmente flui usando as entradas já resolvidas). Forçar uma nova resolução exigiria apagar a entrada do roteador para B (`ip neigh del`), mas isso também dispara reconfirmações (NUD) de vizinhos não relacionados na mesma janela de tempo, poluindo a captura. Capturar tudo de uma vez, no primeiro contato, é determinístico e evita as duas armadilhas.

## Verificação e avaliação

`verify-step1.sh` a `verify-step5.sh` chamam `roteador_lab.py`, no mesmo modelo de `arp_lab.py`: leitura de estado ao vivo (`ip -n <namespace> neigh/route/addr show`) e capturas relidas com `tcpdump -r`. A etapa 5 sempre revalida tudo; as etapas 1 a 4 confiam no checkpoint após a primeira aprovação.

Como em `arp` e `particoes-linux`, o aluno tem acesso root e pode alterar checkpoints ou o próprio kernel — o mecanismo é evidência didática, não uma atestação inviolável.

## Entrega e publicação

Reutiliza identificação, TXT v2 (`LABORATORIO=arp-roteador`), histórico legível e envio para a pasta Drive já configurada. O catálogo em `professor/laboratorios.json` e `professor/google-drive/Code.gs` já inclui `arp-roteador`. **Atualize o Code.gs e publique uma nova versão da implantação existente** para o endpoint aceitar esse ID antes de ativar `recebimento_ativo`.

Antes de disponibilizar para execução sem acompanhamento, faça uma sessão de teste no Killercoda. Os testes locais em Docker (`tests/arp-roteador.sh`) validam o fluxo Linux completo, mas não a interface web nem o tempo que cada aluno levará.

## Referências

- [RFC 826 — An Ethernet Address Resolution Protocol](https://www.rfc-editor.org/rfc/rfc826).
- [RFC 1122 — Requirements for Internet Hosts, §2.3.2.1 (ARP e roteamento)](https://www.rfc-editor.org/rfc/rfc1122).
- [ip-route(8) — util-linux/iproute2](https://man7.org/linux/man-pages/man8/ip-route.8.html).
