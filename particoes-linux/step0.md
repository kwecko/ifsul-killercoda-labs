# Preparação e identificação — 5 minutos

Execute e aguarde a instalação das ferramentas e a preparação dos dois discos vazios:

`preparar-discos`{{exec}}

Continue somente quando aparecer **Dois discos de 1 GiB prontos**. Repetir esse comando preserva os discos existentes. Se houver falha de rede durante a instalação, tente novamente. Se persistir, registre a mensagem e informe o problema pelo canal da atividade; não altere discos do sistema para contornar a falha.

`identificar-aluno`{{exec}}

Informe matrícula (somente números) e nome completo. A gravação do terminal começa automaticamente. Os comandos e as saídas visíveis compõem o histórico da entrega.

Carregue as variáveis com os nomes dos dois discos:

```bash
source /root/discos.env
printf 'Disco MBR: %s\nDisco GPT: %s\n' "$MBR" "$GPT"
```

O resultado deve mostrar **dois dispositivos diferentes** como `/dev/loop0` e `/dev/loop1`; os números podem variar. Use as variáveis nos comandos seguintes.

Se uma variável aparecer vazia durante a atividade, execute novamente `source /root/discos.env` nessa aba. Se sair da gravação com `exit`, execute `iniciar-registro`, depois carregue as variáveis novamente. Não trabalhe em outra aba: esses comandos não seriam registrados.

Pressione **CHECK** e avance.
