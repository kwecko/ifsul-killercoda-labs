# Receber comprovantes no Google Drive

Destino do laboratório `usuarios-grupos`, cadastrado no bloco gerado de `Code.gs`: [pasta de entregas](https://drive.google.com/drive/folders/1a8qOKwk72bMuULU0c1Jjxr3LCXL-Xcgm).

## Ativar na conta do professor

1. Entre em [Google Apps Script](https://script.google.com/) com uma conta que possa criar arquivos nessa pasta.
2. Crie um projeto chamado **Recebimento de comprovantes IFSul**.
3. Substitua o conteúdo de `Code.gs` pelo arquivo [Code.gs](Code.gs) desta pasta e salve.
4. Selecione **Implantar → Nova implantação → Aplicativo da Web**.
5. Em **Executar como**, escolha **Eu**. Em acesso, escolha **Qualquer pessoa**, pois o terminal do aluno não tem login Google. Autorize o acesso ao Drive na sua conta e conclua a implantação.
6. Copie a URL de implantação terminada em `/exec` para o campo `url` de `comum/drive.json` e execute `python3 ferramentas/laboratorios.py sincronizar`. Não use a URL da pasta nem uma URL `/dev`.
7. Publique a alteração na branch usada pelo Killercoda e inicie uma nova sessão do cenário.

A URL de implantação fornecida pelo professor está em `comum/drive.json` e é copiada para os assets dos cenários ativos. Para desativar o envio de um laboratório, configure `recebimento_ativo: false` no seu `laboratorio.json`, sincronize e atualize a implantação Google. O link da pasta, sozinho, não habilita uploads.

Se sua conta institucional não permitir acesso anônimo ao aplicativo, o administrador poderá restringir essa implantação. Nesse caso, mantenha o download do TXT; não há tentativa de contornar a política da instituição.

A pasta não precisa ser pública e não deve conceder edição aos alunos. O aplicativo recebe autorização da sua conta para usar DriveApp (o consentimento do Google pode abranger o Drive, não apenas essa pasta); seu código só acessa os IDs de pasta cadastrados para cada laboratório. Não altere o compartilhamento da pasta para habilitar este fluxo.

## Funcionamento

Após validar todas as etapas e a existência do registro, `gerar-comprovante` grava o TXT e uma cópia legível do histórico local, e tenta enviar os dois, se a URL estiver configurada. O aluno só deve considerar o envio confirmado quando aparecer **Recebimento confirmado no Google Drive**.

`enviar-comprovante` permite repetir o envio do mesmo par de arquivos sem gerar outra data ou hash. O comando também confere as etapas antes de enviar. Erros de conexão, limites ou autorização não removem os arquivos locais. O download e a entrega no Moodle continuam disponíveis.

O receptor aceita apenas TXT v1 ou v2 de laboratórios cadastrados e com recebimento ativo, com até 4 KiB e matrícula de 1 a 32 caracteres (letras ASCII, números, ponto e sublinhado), começando com letra ou número, preservando caixa e zeros iniciais. Confere os campos, a data e o SHA-256. O nome é derivado dos dados, nunca de um caminho informado pelo cliente. Os arquivos salvos têm exatamente os bytes recebidos. O histórico tem limite de 1 MiB e é enviado como base64 no pacote JSON, preservando os bytes do texto legível produzido na VM.

O mesmo nome e conteúdo não geram cópias adicionais. Uma nova emissão com conteúdo diferente preserva a versão anterior: o Drive pode mostrar até cinco arquivos com o mesmo nome. A data de criação no Drive indica quando cada versão foi recebida; a DATA no TXT é informada pela VM. O receptor não sobrescreve, remove ou compartilha arquivos existentes e não oferece listagem nem download pelo endpoint.

O histórico é salvo primeiro, e o receptor só confirma após gravar o par. Se houver falha parcial, o reenvio completa o que falta sem duplicar. Para uma mesma emissão, um histórico diferente é recusado.

Há limite global de 200 novas tentativas de entrega por dia UTC e cinco versões por nome. Uma falha do Drive após reservar a cota também consome uma tentativa. Um bloqueio de concorrência evita duplicação por envios simultâneos. Ajuste `LIMITE_DIARIO`, `LIMITE_VERSOES` e `RECEBIMENTO_ATIVO` no Apps Script conforme necessário; depois atualize a implantação com uma nova versão.

Esses limites reduzem acúmulo de arquivos, mas não impedem abuso ou esgotamento das cotas de execução do Google. A URL é pública na VM, não é uma senha. Alunos com root podem inventar matrícula/sessão e recalcular hashes. Receber no Drive não autentica o aluno nem prova a conclusão. Não se armazena chave Google na VM. Para encerrar os envios, arquive a implantação ou publique `RECEBIMENTO_ATIVO = false`.

## Protocolo e testes

O cliente atual envia POST HTTPS com `Content-Type: application/json`, contendo exatamente:

```json
{"versao":2,"comprovante":"<base64 dos bytes do TXT>","registro":"<base64 dos bytes do histórico>"}
```

O pacote tem limite de 1.500.000 bytes. O ContentService redireciona a resposta; o cliente usa `curl --location` sem forçar POST após o redirecionamento. Sucesso tem cinco linhas:

```text
OK
ARQUIVO=<laboratorio>_<matricula>_<sessao>.txt
CODIGO=SHA256:<hash do comprovante>
REGISTRO=<laboratorio>_<matricula>_<sessao>_<hash do comprovante>_historico.log
REGISTRO_SHA256=<hash dos bytes do histórico>
```

Falhas devolvem `ERRO=<motivo>`; HTTP 200 sozinho não confirma recebimento. O cliente exige nomes e códigos correspondentes aos dois arquivos. Não imprime páginas de login ou mensagens arbitrárias devolvidas pelo servidor.

O receptor conserva compatibilidade com POST `text/plain` da versão anterior (somente TXT, resposta de três linhas). O novo cliente exige o par; não aceita a confirmação antiga como entrega completa. O TXT atual usa versão **2**, com NOME. O receptor também aceita TXT v1 sem nome. A versão 2 do pacote de transporte é independente da versão do TXT.

## Cadastrar outros laboratórios

Use o comando de criação e o `laboratorio.json` de cada cenário, conforme o [guia do repositório](../../README.md). `python3 ferramentas/laboratorios.py sincronizar` gera o catálogo `professor/laboratorios.json` e o bloco `LABORATORIOS` do Code.gs. Não edite esse bloco manualmente: ele será substituído na próxima sincronização. O restante do receptor é compartilhado e permanece editável.

Cada entrada define título, pasta de destino e se o recebimento está ativo. A pasta é escolhida pelo ID de laboratório presente no TXT e conferido no catálogo. Um cliente não escolhe uma pasta arbitrária. Laboratórios desconhecidos ou inativos são recusados. O limite diário é compartilhado por todos os laboratórios nesta implantação.

## Atualizar a implantação existente

1. No projeto do Apps Script já criado, substitua `Code.gs` pela versão atual deste repositório e salve.
2. Abra **Implantar → Gerenciar implantações**, selecione a implantação em uso e clique em **Editar** (lápis).
3. Em versão, selecione **Nova versão** e clique em **Implantar**.
4. Atualizando a implantação existente, a URL `/exec` permanece a mesma. Não basta salvar o código: a implantação precisa usar a nova versão.
5. Publique os arquivos do cenário no GitHub e use uma nova sessão do Killercoda. Sessões antigas não têm a gravação desde o início.

Sem essa atualização, o endpoint anterior recusará o pacote com histórico; os arquivos continuarão disponíveis para download. Nenhuma atualização da implantação Google é feita automaticamente por um commit ou push deste repositório.

Testes locais, a partir da raiz do repositório:

```bash
node tests/test_google_drive.cjs
python3 tests/test_registro_pty.py
python3 -m unittest discover -s tests -p 'test_validar_comprovante.py' -v
docker run --rm -e LAB_TEST_CONTAINER=1 -v "$PWD:/lab:ro" ubuntu:24.04 bash /lab/tests/usuarios-grupos.sh
```

Os testes do Apps Script usam substitutos em memória de DriveApp, PropertiesService e LockService. O cliente usa um substituto de curl nos testes, sem enviar dados à internet. Depois de implantar, é necessário validar um envio real e conferir o arquivo na pasta. O teste PTY verifica a gravação real em Ubuntu, inclusive troca de usuário, entrada sem eco e retomada. Consulte [registro do terminal](../../docs/registro-terminal.md) para o escopo da gravação.

O receptor e o validador Python ficam em `professor/`, fora do cenário e dos assets da VM. Somente o cliente de envio e a URL pública vão para o Killercoda.

Referências: [aplicativos da Web](https://developers.google.com/apps-script/guides/web), [ContentService e redirecionamento](https://developers.google.com/apps-script/guides/content), [bloqueio de concorrência](https://developers.google.com/apps-script/reference/lock/lock-service).
