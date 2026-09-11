# Configuração das permissões de acesso

Os diretórios dos setores já foram criados e associados aos respectivos grupos. Agora é necessário controlar quem poderá acessar essas informações.

Configure as permissões dos seguintes diretórios:

- `/empresa/administracao`
- `/empresa/suporte`
- `/empresa/desenvolvimento`

As seguintes regras devem ser atendidas:

- o proprietário deve possuir permissão de leitura, escrita e execução;
- os membros do grupo proprietário devem possuir permissão de leitura, escrita e execução;
- os demais usuários não devem possuir nenhuma permissão.

Use o modo `770` (`rwxrwx---`), sem bits especiais, nos três diretórios. Em diretórios, leitura permite listar nomes, escrita permite criar/remover entradas e execução permite atravessar o diretório.

Ao final, verifique as permissões configuradas nos três diretórios.

Utilize os comandos que considerar adequados.

Pressione **CHECK** para verificar esta etapa.
