# 3. O roteador refaz a resolução na outra rede — 10 minutos

O ping da etapa anterior chegou até `estacao-b` — alguém precisou resolver `10.77.2.10` por ARP na rede `10.77.2.0/24`. Veja quem foi, na captura que você já fez do lado do `roteador` (`step2-b.pcap`, feita ao mesmo tempo que a da etapa 2):

```bash
tcpdump -e -n -r /root/captura-arp-roteador/step2-b.pcap
```

Você deve ver:

```
... Request who-has 10.77.2.10 tell 10.77.2.1, length 28
```

Repare no campo "tell": o pedido diz `tell 10.77.2.1` — o **próprio roteador**, não `estacao-a` (10.77.1.10). Faz sentido: o roteador recebeu o pacote de `estacao-a` (endereçado a ele mesmo, na camada de enlace), decidiu para onde encaminhar consultando sua própria tabela de rotas, e então fez sua **própria** resolução ARP na rede de destino — como se ele fosse a origem, porque naquele segmento, para efeitos de ARP, ele é.

Confira a tabela ARP de `estacao-b`:

```bash
estacao-b ip neigh show
```

Deve haver uma entrada para `10.77.2.1` (o roteador) — e **nenhuma** para `10.77.1.10` (`estacao-a`). Assim como `estacao-a` nunca aprendeu o MAC de `estacao-b`, `estacao-b` nunca aprende o MAC de `estacao-a`: cada estação só conhece, por ARP, os vizinhos do seu próprio segmento.

Pressione **CHECK**.
