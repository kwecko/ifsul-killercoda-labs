# 1. Reconhecer a topologia — 5 minutos

Você tem três estações virtuais na mesma LAN, ligadas por um switch virtual (`br-lab`):

| Estação | Endereço IP | Interface |
|---|---|---|
| `estacao-a` | 10.77.0.1 | `veth-a` |
| `estacao-b` | 10.77.0.2 | `veth-b` |
| `estacao-c` | 10.77.0.3 | `veth-c` |

Confirme os endereços e os endereços MAC (físicos) de cada interface:

```bash
estacao-a ip addr show veth-a
estacao-b ip addr show veth-b
estacao-c ip addr show veth-c
```

Anote mentalmente que cada interface tem um MAC diferente, gerado aleatoriamente pelo kernel; os valores do seu ambiente não são os mesmos de um colega.

Agora confira a tabela ARP (tabela de vizinhos) de cada estação:

```bash
estacao-a ip neigh show
estacao-b ip neigh show
estacao-c ip neigh show
```

As três tabelas devem estar **vazias**. Nenhuma estação jamais conversou com outra nesta sessão, então nenhuma delas ainda sabe qual MAC corresponde a qual IP na LAN. É exatamente esse aprendizado que o ARP resolve.

Se algum comando `estacao-*` falhar, execute `source /root/rede.env` novamente e repita.

Pressione **CHECK**.
