# 3. Aprendizado legítimo por uma terceira estação — 6 minutos

Na etapa anterior, `estacao-c` não aprendeu nada só de observar o tráfego alheio. Ela só aprende quando **ela mesma** participa de uma troca de ARP: faz o pedido e recebe a resposta.

Faça `estacao-c` pingar `estacao-b`:

```bash
estacao-c ping -c 1 -W 1 10.77.0.2
```

Desta vez o pedido ARP ("quem tem 10.77.0.2?") saiu de `estacao-c`, e a resposta de `estacao-b` voltou em unicast diretamente para ela. Confira:

```bash
estacao-c ip neigh show
```

Agora `estacao-c` deve ter uma entrada correta para `10.77.0.2`, com o MAC real de `estacao-b`. Compare com o MAC mostrado em:

```bash
estacao-b ip addr show veth-b
```

Os dois devem ser idênticos. Guarde essa entrada de cabeça: nas próximas etapas você vai ver alguém tentar substituí-la por um MAC falso.

Pressione **CHECK**.
