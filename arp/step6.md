# 6. Diagnóstico final e conclusão — 8 minutos

Limpe as entradas dinâmicas de `estacao-a` e `estacao-b` e force uma nova resolução:

```bash
estacao-a ip neigh flush dev veth-a
estacao-b ip neigh flush dev veth-b
estacao-a ip neigh show
estacao-b ip neigh show
estacao-a ping -c 1 -W 1 10.77.0.2
estacao-a ip neigh show
estacao-b ip neigh show
```

As tabelas devem esvaziar e, depois do ping, se reconstruir corretamente — o ARP resolve de novo sem nenhuma intervenção manual, exatamente como na etapa 2. A entrada estática de `estacao-c`, por ter sido criada com `nud permanent`, não é afetada por `flush` nas outras estações e continua protegendo aquele vizinho.

Para fechar, responda três perguntas curtas sobre o que você observou. Cada `read` grava sua resposta no terminal, que faz parte do histórico enviado ao professor:

```bash
read -rp 'Por que estacao-c viu o pedido ARP mas nao a resposta, na etapa 2? ' R1
read -rp 'Por que um ARP gratuito forjado consegue sobrescrever uma entrada dinamica correta? ' R2
read -rp 'Por que a entrada estatica da etapa 5 resistiu ao mesmo ataque? ' R3
{
  echo "1) $R1"
  echo "2) $R2"
  echo "3) $R3"
} > /root/relatorio-arp/conclusao.txt
cat /root/relatorio-arp/conclusao.txt
```

Escreva com suas próprias palavras; as três respostas somadas precisam ter pelo menos 120 caracteres.

Pressione **CHECK**.
