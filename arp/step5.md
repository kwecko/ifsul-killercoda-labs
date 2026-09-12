# 5. Proteger com uma entrada ARP estática — 8 minutos

Uma defesa clássica contra o envenenamento de ARP é fixar manualmente a associação IP-MAC de um host crítico, em vez de deixá-la ser aprendida (e reescrita) por qualquer quadro que chegue. Essa entrada é chamada de **estática** ou **permanente**: o kernel para de atualizá-la a partir do tráfego recebido.

Descubra o MAC real de `estacao-b` e fixe-o em `estacao-c`:

```bash
estacao-b ip addr show veth-b
estacao-c ip neigh replace 10.77.0.2 lladdr <MAC_DE_ESTACAO_B> dev veth-c nud permanent
estacao-c ip neigh show
```

Substitua `<MAC_DE_ESTACAO_B>` pelo MAC mostrado no primeiro comando. A tabela agora deve mostrar `10.77.0.2` com o estado `PERMANENT`.

Repita exatamente o ataque da etapa anterior:

```bash
estacao-c timeout 5 tcpdump -c 1 -i veth-c -e -n arp -w /root/captura-arp/step5.pcap &
sleep 1
estacao-a forjar-arp-gratuito veth-a 10.77.0.2 reply
wait
tcpdump -e -n -r /root/captura-arp/step5.pcap
```

A captura confirma que o quadro forjado chegou até `estacao-c` normalmente — o switch não filtra nada disso, e nenhum firewall entrou em ação. Agora olhe a tabela ARP de novo:

```bash
estacao-c ip neigh show
```

Diferente da etapa anterior, a entrada de `10.77.0.2` **continua correta e `PERMANENT`**. O ataque chegou, mas o kernel o ignorou para essa entrada porque ela é estática. Esse é o motivo pelo qual entradas estáticas são recomendadas para vizinhos críticos (gateway, servidores sensíveis) em redes onde o ARP spoofing é uma preocupação real — ao custo de precisar atualizar manualmente se o MAC daquele host mudar de verdade.

Pressione **CHECK**.
