# 2. A estação só resolve o gateway por ARP — 10 minutos

`estacao-a` quer falar com `10.77.2.10` (`estacao-b`), que está em outra rede. O ARP só funciona dentro do mesmo domínio de broadcast — `estacao-a` **não pode** perguntar "quem tem 10.77.2.10?" diretamente, porque esse quadro nunca chegaria lá. Em vez disso, o kernel consulta a tabela de rotas, decide que o destino é alcançado pela rota padrão, e resolve por ARP o **gateway** (`10.77.1.1`), não o destino final.

Vamos capturar dos dois lados ao mesmo tempo, no primeiro contato entre as estações (as tabelas ainda estão vazias, da etapa 1):

```bash
estacao-a timeout 4 tcpdump -i veth-a -e -n arp -w /root/captura-arp-roteador/step2-a.pcap &
roteador timeout 4 tcpdump -i rot-b -e -n arp -w /root/captura-arp-roteador/step2-b.pcap &
sleep 1
estacao-a ping -c 2 -W 1 10.77.2.10
wait
```

Guarde a segunda captura (`step2-b.pcap`) para a próxima etapa. Por agora, examine só o lado de `estacao-a`:

```bash
tcpdump -e -n -r /root/captura-arp-roteador/step2-a.pcap
```

Você deve ver um pedido ARP perguntando pelo **gateway**:

```
... Request who-has 10.77.1.1 tell 10.77.1.10, length 28
```

Repare que **em nenhum momento** aparece um pedido perguntando por `10.77.2.10`. `estacao-a` nunca soube — e não precisa saber — o endereço de enlace de `estacao-b`.

Confira a tabela ARP de `estacao-a`:

```bash
estacao-a ip neigh show
```

Deve haver uma entrada para `10.77.1.1` (o gateway), e **nenhuma** para `10.77.2.10`. Isso vale mesmo que o ping para `estacao-b` tenha funcionado perfeitamente: comunicar-se com um host em outra rede não exige, e não gera, uma entrada ARP para o IP desse host.

Pressione **CHECK**.
