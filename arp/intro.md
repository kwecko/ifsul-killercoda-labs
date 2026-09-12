# Protocolo ARP em uma LAN comutada — até 60 minutos

Nesta atividade guiada você usará **três estações virtuais** (`estacao-a`, `estacao-b`, `estacao-c`) ligadas por um switch virtual, simulando uma LAN Ethernet real. Você vai observar o pedido e a resposta ARP, comparar o que um switch entrega a um terceiro host, provocar o aprendizado legítimo de uma tabela ARP, forjar um ARP gratuito para envenenar um cache e proteger uma entrada com um registro estático.

O roteiro contém todos os comandos necessários e pode ser realizado sem acompanhamento ao vivo. Execute os blocos na ordem e compare os resultados com as explicações. **A estimativa é de 50 minutos de tarefas, mais 5 para preparação e 5 para entregar.** Se concluir antes, avance: não é preciso esperar o tempo indicado.

| Etapa | Tempo estimado |
|---|---:|
| Preparação e identificação | 5 min |
| 1. Reconhecer a topologia | 5 min |
| 2. Broadcast e resposta unicast | 10 min |
| 3. Aprendizado legítimo por uma terceira estação | 6 min |
| 4. Forjar um ARP gratuito e envenenar o cache | 10 min |
| 5. Proteger com uma entrada ARP estática | 8 min |
| 6. Diagnóstico final e conclusão | 8 min |
| Comprovante e download | 5 min |

**A sessão termina após 60 minutos.** Use o tempo do roteiro como orientação e reserve os minutos finais para baixar a entrega. Não há retomada entre sessões.

As três estações são *network namespaces* do Linux (`10.77.0.1`, `10.77.0.2` e `10.77.0.3`), criados pela preparação. **Use apenas `estacao-a`, `estacao-b` e `estacao-c`**, definidos em `/root/rede.env`. Não experimente comandos na interface de rede real da máquina (`eth0` ou equivalente); ela não faz parte do exercício e é usada pela infraestrutura do laboratório.

Faça tudo na mesma aba de terminal, começando pela identificação. Pressione **CHECK em cada etapa antes de avançar**. Estados intermediários ficam registrados como checkpoints. **SKIP não conclui tarefas.**

Se aparecer uma pendência, leia a mensagem e corrija antes de continuar. Os passos indicam os comandos esperados e como interpretar a saída. Ao final, entregue o TXT e o histórico conforme a página de conclusão.
