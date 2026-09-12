# Preparação e identificação — 5 minutos

Execute e aguarde a instalação das ferramentas e a criação das duas sub-redes e do roteador:

`preparar-roteador`{{exec}}

Continue somente quando aparecer **Duas sub-redes prontas**. Repetir esse comando preserva a topologia já criada. Se houver falha de rede durante a instalação, tente novamente. Se persistir, registre a mensagem e informe o problema pelo canal da atividade; não altere a interface de rede real da máquina (`eth0` ou equivalente) para contornar a falha.

`identificar-aluno`{{exec}}

Informe matrícula (de 1 a 32 caracteres: letras A-Z/a-z, números, ponto e sublinhado; comece com letra ou número, sem espaços) e nome completo. Exemplo: `20261CM.INF_I0027`. Digite a matrícula exatamente como consta no registro acadêmico; maiúsculas, minúsculas e zeros à esquerda são preservados. A gravação do terminal começa automaticamente. Os comandos e as saídas visíveis compõem o histórico da entrega.

Carregue os atalhos que executam comandos dentro de cada namespace:

```bash
source /root/rede.env
estacao-a ip addr show veth-a
estacao-b ip addr show veth-b
roteador ip addr show rot-a
roteador ip addr show rot-b
```

O resultado deve mostrar `10.77.1.10/24` em `estacao-a`, `10.77.2.10/24` em `estacao-b`, e `10.77.1.1/24`/`10.77.2.1/24` nas duas interfaces do `roteador`. `estacao-a` e `estacao-b` estão em **redes diferentes** (10.77.1.0/24 e 10.77.2.0/24); o `roteador` tem uma perna em cada uma e encaminha pacotes entre elas.

Se um atalho não funcionar durante a atividade, execute novamente `source /root/rede.env` nessa aba. Se sair da gravação com `exit`, execute `iniciar-registro`, depois carregue os atalhos novamente. Não trabalhe em outra aba: esses comandos não seriam registrados.

Pressione **CHECK** e avance.
