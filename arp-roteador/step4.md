# 4. O endereço de enlace muda a cada salto; o IP não — 10 minutos

Agora vamos comparar os próprios pacotes do ping (ICMP), capturados nos dois lados ao mesmo tempo:

```bash
estacao-a timeout 4 tcpdump -i veth-a -e -n icmp -w /root/captura-arp-roteador/step4-a.pcap &
roteador timeout 4 tcpdump -i rot-b -e -n icmp -w /root/captura-arp-roteador/step4-b.pcap &
sleep 1
estacao-a ping -c 2 -W 1 10.77.2.10
wait
```

Leia as duas capturas:

```bash
tcpdump -e -n -r /root/captura-arp-roteador/step4-a.pcap
tcpdump -e -n -r /root/captura-arp-roteador/step4-b.pcap
```

Compare o `ICMP echo request` nas duas. O endereço IP é **idêntico** nas duas capturas:

```
10.77.1.10 > 10.77.2.10: ICMP echo request
```

Mas os endereços MAC (mostrados antes do `>` inicial de cada linha, pelo `-e`) são **diferentes** em cada lado:

- Do lado de `estacao-a`: origem é o MAC de `estacao-a`, destino é o MAC do roteador (`rot-a`).
- Do lado do `roteador` (interface `rot-b`): origem é o MAC do roteador (`rot-b`), destino é o MAC de `estacao-b`.

Confirme comparando com os MACs reais:

```bash
estacao-a ip addr show veth-a
roteador ip addr show rot-a
roteador ip addr show rot-b
estacao-b ip addr show veth-b
```

Esse é o ponto central deste laboratório: o **endereço IP de origem e destino não muda** durante todo o trajeto — é ele que identifica a conversa fim a fim. Já o **endereço de enlace (MAC) muda a cada salto**, porque descreve apenas o próximo trecho do caminho, entre dois vizinhos diretos. O roteador é quem faz essa troca: ele recebe o quadro endereçado a si mesmo, decide a rota pelo IP de destino, e reencapsula o mesmo pacote IP dentro de um novo quadro Ethernet, endereçado ao próximo salto.

Pressione **CHECK**.
