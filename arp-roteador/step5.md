# 5. Sem rota não há tentativa de ARP — 10 minutos

Remova a rota padrão de `estacao-a` e tente pingar `estacao-b` de novo:

```bash
estacao-a ip route del default
estacao-a ip route
estacao-a ping -c 2 -W 1 10.77.2.10
```

O ping falha imediatamente com `Network is unreachable` — e nem chega a ser enviado nenhum quadro. Confirme capturando ao mesmo tempo:

```bash
estacao-a timeout 3 tcpdump -i veth-a -e -n -w /root/captura-arp-roteador/sem-rota.pcap &
sleep 1
estacao-a ping -c 2 -W 1 10.77.2.10
wait
tcpdump -e -n -r /root/captura-arp-roteador/sem-rota.pcap
```

A captura fica vazia. Sem uma rota para `10.77.2.0/24`, o kernel de `estacao-a` nem sabe **para quem perguntar** — a resolução ARP só acontece depois que a tabela de rotas já indicou um próximo salto (o gateway, neste caso). ARP não substitui roteamento: ele resolve o "quem é o próximo salto na camada de enlace" depois que o roteamento já decidiu "qual é o próximo salto na camada de rede".

Restaure a rota:

```bash
estacao-a ip route add default via 10.77.1.1
estacao-a ping -c 1 -W 1 10.77.2.10
estacao-a ip neigh show
```

A comunicação deve voltar a funcionar normalmente.

Para fechar, responda três perguntas curtas sobre o que você observou. Cada `read` grava sua resposta no terminal, que faz parte do histórico enviado ao professor:

```bash
read -rp 'Por que estacao-a nunca tem, na sua tabela ARP, uma entrada para o IP de estacao-b? ' R1
read -rp 'Por que quem pede ARP por estacao-b eh o roteador, e nao estacao-a? ' R2
read -rp 'Por que remover a rota impediu qualquer tentativa de ARP, em vez de gerar um pedido que falha? ' R3
{
  echo "1) $R1"
  echo "2) $R2"
  echo "3) $R3"
} > /root/relatorio-arp-roteador/conclusao.txt
cat /root/relatorio-arp-roteador/conclusao.txt
```

Escreva com suas próprias palavras; as três respostas somadas precisam ter pelo menos 120 caracteres.

Pressione **CHECK**.
