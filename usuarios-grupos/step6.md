# Teste de acesso e manipulação de arquivos

Agora você deverá testar as configurações realizadas utilizando uma conta de usuário comum.

Abra uma sessão como a usuária `julia` (por exemplo, com `su - julia`). A troca feita por `root` não exige definir uma senha para `julia`.

Após realizar a troca de usuário:

- confirme qual usuário está utilizando o sistema;
- acesse o diretório `/empresa/desenvolvimento`;
- crie o diretório `projetos`;
- dentro do diretório `projetos`, crie o arquivo `projeto.txt`;
- faça com que o arquivo contenha somente a seguinte linha:

`Projeto em desenvolvimento`

- verifique o proprietário e as permissões do arquivo criado;
- tente acessar o diretório `/empresa/administracao` e observe o comportamento do sistema.

O diretório `projetos` e o arquivo devem pertencer a `julia`. O acesso a `/empresa/administracao` deve resultar em **Permissão negada**; esse é o resultado esperado.

Ao finalizar os testes, retorne à sessão do usuário `root` para realizar a verificação da atividade.

Pressione **CHECK** para verificar esta etapa.
