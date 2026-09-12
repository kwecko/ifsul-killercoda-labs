# Preparação e identificação — 5 minutos

Execute e aguarde a instalação das ferramentas e a criação das três estações virtuais:

`preparar-rede`{{exec}}

Continue somente quando aparecer **Três estações prontas**. Repetir esse comando preserva a rede já criada. Se houver falha de rede durante a instalação, tente novamente. Se persistir, registre a mensagem e informe o problema pelo canal da atividade; não altere a interface de rede real da máquina (`eth0` ou equivalente) para contornar a falha.

`identificar-aluno`{{exec}}

Informe matrícula (de 1 a 32 caracteres: letras A-Z/a-z, números, ponto e sublinhado; comece com letra ou número, sem espaços) e nome completo. Exemplo: `20261CM.INF_I0027`. Digite a matrícula exatamente como consta no registro acadêmico; maiúsculas, minúsculas e zeros à esquerda são preservados. A gravação do terminal começa automaticamente. Os comandos e as saídas visíveis compõem o histórico da entrega.

Carregue os atalhos que executam comandos dentro de cada estação:

```bash
source /root/rede.env
estacao-a ip addr show veth-a
estacao-b ip addr show veth-b
estacao-c ip addr show veth-c
```

O resultado deve mostrar `10.77.0.1/24`, `10.77.0.2/24` e `10.77.0.3/24`, cada um em sua interface. As três estações são *network namespaces* do Linux, ligadas por um switch virtual (`br-lab`): comandos como `ping`, `ip`, `tcpdump` e `forjar-arp-gratuito` executados com `estacao-a`, `estacao-b` ou `estacao-c` rodam isolados dentro daquela estação, exatamente como se fossem três computadores separados na mesma rede.

Se um atalho não funcionar durante a atividade, execute novamente `source /root/rede.env` nessa aba. Se sair da gravação com `exit`, execute `iniciar-registro`, depois carregue os atalhos novamente. Não trabalhe em outra aba: esses comandos não seriam registrados.

Pressione **CHECK** e avance.
