# 2. Broadcast e resposta unicast — 10 minutos

`estacao-a` ainda não sabe o MAC de `estacao-b`. Ao pingar, o kernel de `estacao-a` primeiro precisa perguntar "quem tem 10.77.0.2?" por ARP. Essa pergunta é enviada em **broadcast** (endereço `ff:ff:ff:ff:ff:ff`), então **todo mundo ligado ao switch a recebe**, inclusive `estacao-c`, que nem está envolvida na conversa.

Capture o tráfego ARP em `estacao-c` — a estação de fora — enquanto `estacao-a` pinga `estacao-b`:

```bash
estacao-c timeout 4 tcpdump -i veth-c -e -n arp -w /root/captura-arp/step2.pcap &
sleep 1
estacao-a ping -c 2 -W 1 10.77.0.2
wait
```

O `&` coloca a captura em segundo plano; `wait` espera ela terminar sozinha depois de 4 segundos (por causa do `timeout 4`). Agora leia o que `estacao-c` capturou:

```bash
tcpdump -e -n -r /root/captura-arp/step2.pcap
```

Você deve ver uma linha assim (os MACs do seu ambiente serão diferentes):

```
... aa:bb:cc:dd:ee:01 > ff:ff:ff:ff:ff:ff, ethertype ARP (0x0806), length 42: Request who-has 10.77.0.2 tell 10.77.0.1, length 28
```

Repare no destino do quadro: `ff:ff:ff:ff:ff:ff`. É por isso que `estacao-c` viu o **pedido**, mesmo sem participar da conversa.

Agora procure a **resposta** ("Reply ... is-at ...") nessa mesma captura. Ela não deve aparecer. A resposta de `estacao-b` para `estacao-a` é enviada em **unicast**, direto para o MAC de quem perguntou; o switch virtual já aprendeu em qual porta está cada MAC e entrega o quadro só para `estacao-a`, sem inundar `estacao-c`.

Confira as tabelas ARP das três estações:

```bash
estacao-a ip neigh show
estacao-b ip neigh show
estacao-c ip neigh show
```

`estacao-a` e `estacao-b` devem ter aprendido uma à outra (elas trocaram pedido e resposta diretamente). `estacao-c` continua sem nenhuma entrada: só ouviu, de passagem, um pedido que não era endereçado a ela, e isso sozinho não basta para o Linux registrar uma entrada ARP.

Pressione **CHECK**.
