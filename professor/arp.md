# Guia do professor — Protocolo ARP

## Aplicação sem acompanhamento ao vivo

`arp` é uma atividade de **até 60 minutos** sobre o protocolo ARP, com três estações virtuais ligadas por um switch (bridge) dentro da própria VM do Killercoda. Não depende de uma segunda máquina real: tudo é simulado com *network namespaces* e interfaces `veth`, da mesma forma que `particoes-linux` simula dois discos com `losetup` em vez de usar discos reais.

São seis etapas práticas, planejadas para 47 minutos, mais 5 de preparação/identificação e 5 de entrega.

| Etapa | Minutos | Critérios técnicos |
|---|---:|---|
| Preparação/identificação | 5 | Três namespaces, três `veth`, um bridge; tabelas ARP vazias |
| 1. Reconhecer a topologia | 5 | Endereços corretos; nenhuma entrada ARP em nenhuma estação |
| 2. Broadcast e resposta unicast | 10 | Captura em `estacao-c` mostra o pedido de A por B, sem nenhuma resposta; A e B resolvidos corretamente; C ainda vazia |
| 3. Aprendizado legítimo por uma terceira estação | 6 | `estacao-c` resolve `estacao-b` corretamente após pingar |
| 4. Forjar um ARP gratuito e envenenar o cache | 10 | Captura mostra um `Reply` gratuito (destino broadcast) com o MAC de A anunciando o IP de B; tabela de C aponta para o MAC de A |
| 5. Proteger com uma entrada ARP estática | 8 | Entrada de C para B é `PERMANENT` com o MAC correto, mesmo após repetir o ataque com uma nova captura |
| 6. Diagnóstico final e conclusão | 8 | A e B resolvidos após `flush`+ping; C continua protegida; relatório com pelo menos 120 caracteres |
| Entrega | 5 | TXT v2 e histórico legível; download antes de encerrar |

A configuração de rotas entre sub-redes, um roteador simulado e o comportamento do ARP fora do domínio de broadcast local ficam fora deste roteiro — são o assunto natural de uma atividade seguinte sobre roteamento.

## Infraestrutura

`preparar-rede` instala `iproute2`, `tcpdump`, `python3` e `iputils-ping` quando necessário e cria três *network namespaces* (`estacao-a`, `estacao-b`, `estacao-c`), cada um com uma interface `veth` ligada a um bridge (`br-lab`) que faz o papel de switch da LAN. Repetir o comando preserva a rede existente. `/root/rede.env` define atalhos (`estacao-a`, `estacao-b`, `estacao-c`) que executam qualquer comando dentro daquele namespace via `ip netns exec`.

- Endereços: `10.77.0.1` (A, `veth-a`), `10.77.0.2` (B, `veth-b`), `10.77.0.3` (C, `veth-c`).
- Capturas: `/root/captura-arp/step2.pcap`, `step4.pcap`, `step5.pcap`.
- Relatório final: `/root/relatorio-arp/conclusao.txt`.
- Checkpoints: `/var/lib/lab-arp/progresso.json`.

`forjar-arp-gratuito` monta manualmente, por socket bruto (`AF_PACKET`), um quadro ARP gratuito (remetente = alvo) do tipo `request` ou `reply`, com o MAC real da interface indicada (ou um MAC explícito). Existe porque o `arping` do sistema (`iputils-arping`) se recusa a anunciar um IP que não esteja configurado na própria interface — o que é justamente o comportamento que a etapa 4 precisa demonstrar. O laboratório não depende de nenhum utilitário externo de spoofing.

O verificador (`arp_lab.py`) lê o estado das tabelas ARP com `ip -n <estação> neigh show dev <interface>` e relê as capturas com `tcpdump -r`, sem depender de qual comando exato o aluno digitou.

## Verificação e avaliação

`verify-step1.sh` a `verify-step6.sh` chamam `arp_lab.py`. Os verificadores leem o estado ao vivo e registram checkpoints; a etapa 6 sempre revalida tudo (tabelas de A, B e C, e o relatório), inclusive quando `gerar-comprovante` executa novamente os verificadores. As etapas 1 a 5 confiam no checkpoint após a primeira aprovação, mesmo que o estado mude depois — o mesmo modelo usado em `particoes-linux` para estados transitórios.

Envenenamento de ARP é temporário por natureza: se a estação vítima trocar qualquer tráfego real com a estação legítima depois do ataque, a entrada se autocorrige. Por isso as etapas 4 e 5 pedem para pressionar CHECK logo após o ataque, e o roteiro explica esse comportamento em vez de escondê-lo — é uma propriedade real do ARP, não uma falha do laboratório.

Como em qualquer VM com root, o aluno pode alterar checkpoints e o próprio kernel. O mecanismo fornece evidências didáticas, não uma atestação inviolável.

## Entrega e publicação

Reutiliza identificação, TXT v2 (`LABORATORIO=arp`), histórico legível e envio para a pasta Drive já configurada. As respostas finais entram no LOG pelo `cat`.

O catálogo em `professor/laboratorios.json` e `professor/google-drive/Code.gs` já inclui `arp`. **Atualize o Code.gs e publique uma nova versão da implantação existente** para o endpoint aceitar esse ID antes de ativar `recebimento_ativo`. Commit/push não atualiza o Apps Script.

Antes de disponibilizar para execução sem acompanhamento, faça uma sessão de teste no Killercoda: preparação, comandos, CHECKs, limite de tempo, Editor/download e recebimento real. Os testes locais em Docker (`tests/arp.sh`) validam o fluxo Linux completo — incluindo o ataque e a mitigação — mas não a interface web nem o tempo que cada aluno levará.

## Referências

- [Killercoda — documentação para criadores](https://killercoda.com/creators).
- [RFC 826 — An Ethernet Address Resolution Protocol](https://www.rfc-editor.org/rfc/rfc826).
- [ip-neighbour(8) — util-linux/iproute2](https://man7.org/linux/man-pages/man8/ip-neighbour.8.html).
- [network_namespaces(7) — Linux manual](https://man7.org/linux/man-pages/man7/network_namespaces.7.html).
