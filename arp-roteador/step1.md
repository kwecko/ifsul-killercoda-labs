# 1. Reconhecer a topologia — 5 minutos

Você tem duas sub-redes, ligadas por um roteador:

| Namespace | Endereço IP | Rede | Interface |
|---|---|---|---|
| `estacao-a` | 10.77.1.10 | 10.77.1.0/24 | `veth-a` |
| `estacao-b` | 10.77.2.10 | 10.77.2.0/24 | `veth-b` |
| `roteador` | 10.77.1.1 e 10.77.2.1 | as duas | `rot-a` e `rot-b` |

`estacao-a` e `estacao-b` **não estão na mesma rede**: seus endereços IP têm prefixos diferentes (`10.77.1.0/24` e `10.77.2.0/24`), então não há como um enviar um quadro Ethernet diretamente para o outro — cada um só enxerga o `roteador`, que tem uma interface em cada rede.

Confira as rotas de cada estação:

```bash
estacao-a ip route
estacao-b ip route
roteador ip route
```

`estacao-a` e `estacao-b` devem ter uma rota padrão (`default`) apontando para o `roteador`. O `roteador` conhece as duas redes diretamente conectadas, sem rota padrão.

Confirme que o roteador está encaminhando pacotes entre as duas interfaces:

```bash
roteador sysctl net.ipv4.ip_forward
```

O valor deve ser `1`.

Por fim, confira que nenhuma tabela ARP tem entradas ainda — ninguém conversou com ninguém nesta sessão:

```bash
estacao-a ip neigh show
estacao-b ip neigh show
roteador ip neigh show
```

As três devem estar vazias.

Se algum comando falhar, execute `source /root/rede.env` novamente e repita.

Pressione **CHECK**.
