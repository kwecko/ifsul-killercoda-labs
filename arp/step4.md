# 4. Forjar um ARP gratuito e envenenar o cache — 10 minutos

Um **ARP gratuito** é um quadro em que o remetente anuncia o próprio endereço sem que ninguém tenha perguntado: o campo "quem tem" e o campo "diga para" apontam para o **mesmo IP**. Hosts de verdade usam isso de forma legítima — por exemplo, ao trocar de placa de rede ou assumir um IP após uma falha (failover), para que todo mundo na LAN atualize o cache rapidamente.

O problema: nada impede que **qualquer estação** anuncie um IP que não é dela. É exatamente isso que faz um ataque de **ARP spoofing** funcionar. O comando `arping` do sistema se recusa a fazer isso (ele exige que o IP anunciado esteja configurado na própria interface), então vamos montar o quadro manualmente com o utilitário `forjar-arp-gratuito`, incluído neste laboratório.

Capture o ataque do ponto de vista de `estacao-c` e, de `estacao-a`, forje um ARP gratuito alegando ser `10.77.0.2` (o IP de `estacao-b`):

```bash
estacao-c timeout 5 tcpdump -c 1 -i veth-c -e -n arp -w /root/captura-arp/step4.pcap &
sleep 1
estacao-a forjar-arp-gratuito veth-a 10.77.0.2 reply
wait
tcpdump -e -n -r /root/captura-arp/step4.pcap
```

A linha capturada deve mostrar destino `ff:ff:ff:ff:ff:ff` (broadcast — o quadro grita para toda a LAN) e `Reply 10.77.0.2 is-at <MAC>`. Compare esse MAC com o MAC real de `estacao-a`:

```bash
estacao-a ip addr show veth-a
```

Eles devem coincidir: `estacao-a` está anunciando o IP de `estacao-b`, usando o próprio MAC.

Agora veja o estrago:

```bash
estacao-c ip neigh show
```

A entrada de `10.77.0.2` em `estacao-c`, que na etapa anterior apontava corretamente para o MAC de `estacao-b`, agora foi **sobrescrita** com o MAC de `estacao-a`. Qualquer pacote que `estacao-c` mandar para `10.77.0.2` a partir de agora vai, na verdade, para `estacao-a`. Esse é o mecanismo por trás de ataques de interceptação (man-in-the-middle) em redes locais: o ARP não tem autenticação, e qualquer estação pode anunciar qualquer IP.

O envenenamento é temporário: se `estacao-b` trocar qualquer tráfego real com `estacao-c` depois disso, `estacao-c` reaprende o MAC verdadeiro e a entrada se corrige sozinha. É por isso que um ataque de ARP spoofing de verdade repete o quadro forjado continuamente, em vez de enviá-lo uma única vez.

Pressione **CHECK** logo em seguida, sem executar outros comandos entre o ataque e o CHECK.
