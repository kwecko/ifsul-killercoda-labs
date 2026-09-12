# ARP entre redes: o papel do roteador — até 60 minutos

Esta atividade continua o laboratório de ARP, agora com **duas sub-redes** (`10.77.1.0/24` e `10.77.2.0/24`) ligadas por um **roteador** virtual. Você vai descobrir, na prática, por que uma estação nunca resolve por ARP o IP de um destino em outra rede — ela resolve apenas o **gateway** — e como é o roteador quem refaz a resolução ARP do outro lado, usando seus próprios endereços de enlace a cada segmento.

O roteiro contém todos os comandos necessários e pode ser realizado sem acompanhamento ao vivo. Execute os blocos na ordem e compare os resultados com as explicações. **A estimativa é de 45 minutos de tarefas, mais 5 para preparação e 5 para entregar.** Se concluir antes, avance: não é preciso esperar o tempo indicado.

| Etapa | Tempo estimado |
|---|---:|
| Preparação e identificação | 5 min |
| 1. Reconhecer a topologia | 5 min |
| 2. A estação só resolve o gateway por ARP | 10 min |
| 3. O roteador refaz a resolução na outra rede | 10 min |
| 4. O endereço de enlace muda a cada salto; o IP não | 10 min |
| 5. Sem rota não há tentativa de ARP | 10 min |
| Comprovante e download | 5 min |

**A sessão termina após 60 minutos.** Use o tempo do roteiro como orientação e reserve os minutos finais para baixar a entrega. Não há retomada entre sessões.

As três máquinas virtuais são *network namespaces* do Linux: `estacao-a` (10.77.1.10), `estacao-b` (10.77.2.10) e `roteador` (10.77.1.1 de um lado, 10.77.2.1 do outro), criadas pela preparação. **Use apenas `estacao-a`, `estacao-b` e `roteador`**, definidos em `/root/rede.env`. Não experimente comandos na interface de rede real da máquina (`eth0` ou equivalente); ela não faz parte do exercício e é usada pela infraestrutura do laboratório.

Faça tudo na mesma aba de terminal, começando pela identificação. Pressione **CHECK em cada etapa antes de avançar**. Estados intermediários ficam registrados como checkpoints. **SKIP não conclui tarefas.**

Se aparecer uma pendência, leia a mensagem e corrija antes de continuar. Os passos indicam os comandos esperados e como interpretar a saída. Ao final, entregue o TXT e o histórico conforme a página de conclusão.
