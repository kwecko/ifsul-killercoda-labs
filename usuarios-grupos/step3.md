# Configuração das contas de usuário

Agora configure a conta da usuária `ana`.

Realize as seguintes tarefas:

- Defina uma senha para a usuária `ana`;
- Configure `/bin/bash` como shell padrão da conta;
- Defina a descrição da conta como:

`Ana - Administração`

Ao digitar a senha, o terminal não exibe os caracteres. Isso é esperado. Use uma senha apenas para este laboratório.

A descrição corresponde ao nome/comentário da conta (campo GECOS). Como contém espaços, coloque o texto inteiro entre aspas ao usá-lo em um comando. Por exemplo:

`usermod -c "Ana - Administração" ana`{{exec}}

A versão sem acentos, `Ana - Administracao`, também é aceita nesta atividade.

Para conferir a descrição registrada:

`getent passwd ana | cut -d: -f5`{{exec}}

O botão **CHECK** verifica os três requisitos: senha ativa, shell `/bin/bash` e descrição. Se houver falha, confira também a senha e o shell.

Após realizar as configurações, verifique os dados da conta utilizando os comandos que considerar adequados.

Pressione **CHECK** para verificar esta etapa.
