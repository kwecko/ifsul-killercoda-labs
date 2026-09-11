# Testes do laboratório

Execute a partir da raiz do repositório, com Docker disponível:

```bash
docker run --rm -e LAB_TEST_CONTAINER=1 -v "$PWD:/lab:ro" ubuntu:24.04 bash /lab/tests/usuarios-grupos.sh
```

O teste cria contas, grupos e diretórios somente no contêiner descartável. O repositório é montado para leitura. A imagem pode precisar ser baixada na primeira execução.

Os testes percorrem a atividade completa, verificam soluções válidas e introduzem erros de associação, senha, shell, descrição, propriedade, permissões e conteúdo. Também verificam que o comprovante recusa atividades incompletas e não executa o conteúdo do registro de identificação.

Os verificadores ficam em `usuarios-grupos/assets/verify-step*.sh`: o `index.json` os referencia nos botões CHECK e os entrega em `/usr/local/lib/laboratorio/` para o comprovante usar os mesmos critérios.

A validação confere o estado final do ambiente. Ela não comprova quem digitou cada comando nem autentica a matrícula; o aluno tem acesso a root. O comprovante é um registro didático, sem assinatura ou validação externa.

Depois de publicar alterações no GitHub, confira também uma nova sessão no Killercoda: a execução local não testa a sincronização nem a interface da plataforma.

O fluxo também verifica a geração do TXT, nome e campos, SHA-256, alteração dos dados, reemissão, matrícula com zeros à esquerda, falha de publicação sem deixar arquivo parcial e geração de uma nova sessão. São asserções internas do teste em contêiner, não um validador para o professor. O contrato do arquivo está em [comprovante-v1.md](../docs/comprovante-v1.md).

A integração opcional com Drive tem testes do cliente (curl simulado dentro do contêiner) e do receptor: `node tests/test_google_drive.cjs`. Nenhum desses testes envia arquivos ao Google.

Para testar a gravação real em terminal (Docker necessário), execute `python3 tests/test_registro_pty.py`. O teste cria um contêiner descartável, verifica comandos de root/julia, ausência de entrada com eco desativado, prevenção de gravação aninhada e retomada sem apagar o histórico. Não envia dados ao Drive.
