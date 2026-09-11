# Receber comprovantes no Google Drive

Destino já configurado no `Code.gs`: [pasta de entregas](https://drive.google.com/drive/folders/1a8qOKwk72bMuULU0c1Jjxr3LCXL-Xcgm).

## Ativar na conta do professor

1. Entre em [Google Apps Script](https://script.google.com/) com uma conta que possa criar arquivos nessa pasta.
2. Crie um projeto chamado **Recebimento de comprovantes IFSul**.
3. Substitua o conteúdo de `Code.gs` pelo arquivo [Code.gs](Code.gs) desta pasta e salve.
4. Selecione **Implantar → Nova implantação → Aplicativo da Web**.
5. Em **Executar como**, escolha **Eu**. Em acesso, escolha **Qualquer pessoa**, pois o terminal do aluno não tem login Google. Autorize o acesso ao Drive na sua conta e conclua a implantação.
6. Copie a URL de implantação terminada em `/exec` e coloque somente essa URL no arquivo `usuarios-grupos/assets/drive-upload-url` do repositório. Não use a URL da pasta nem uma URL `/dev`.
7. Publique a alteração na branch usada pelo Killercoda e inicie uma nova sessão do cenário.

A URL de implantação fornecida pelo professor está configurada em `usuarios-grupos/assets/drive-upload-url`. Para desativar o envio no laboratório, deixe esse arquivo vazio. O link da pasta, sozinho, não habilita uploads.

Se sua conta institucional não permitir acesso anônimo ao aplicativo, o administrador poderá restringir essa implantação. Nesse caso, mantenha o download do TXT; não há tentativa de contornar a política da instituição.

A pasta não precisa ser pública e não deve conceder edição aos alunos. O aplicativo recebe autorização da sua conta para usar DriveApp (o consentimento do Google pode abranger o Drive, não apenas essa pasta); seu código só acessa o ID fixo configurado. Não altere o compartilhamento da pasta para habilitar este fluxo.

## Funcionamento

Após validar todas as etapas, `gerar-comprovante` grava o TXT local e tenta enviá-lo, se a URL estiver configurada. O aluno só deve considerar o envio confirmado quando aparecer **Recebimento confirmado no Google Drive**.

`enviar-comprovante` permite repetir o envio do mesmo arquivo sem gerar outra data ou hash. O comando também confere as etapas antes de enviar. Erros de conexão, limites ou autorização não removem o arquivo local. O download e a entrega no Moodle continuam disponíveis.

O receptor aceita apenas o TXT v1 de `usuarios-grupos`, com até 4 KiB e matrícula de 1 a 32 dígitos. Confere os campos, a data e o SHA-256. O nome é derivado dos dados, nunca de um caminho informado pelo cliente. O arquivo salvo tem exatamente o conteúdo recebido.

O mesmo nome e conteúdo não geram cópias adicionais. Uma nova emissão com conteúdo diferente preserva a versão anterior: o Drive pode mostrar até cinco arquivos com o mesmo nome. A data de criação no Drive indica quando cada versão foi recebida; a DATA no TXT é informada pela VM. O receptor não sobrescreve, remove ou compartilha arquivos existentes e não oferece listagem nem download pelo endpoint.

Há limite global de 200 novas tentativas de gravação por dia UTC e cinco versões por nome. Uma falha do Drive após reservar a cota também consome uma tentativa. Um bloqueio de concorrência evita duplicação por envios simultâneos. Ajuste `LIMITE_DIARIO`, `LIMITE_VERSOES` e `RECEBIMENTO_ATIVO` no Apps Script conforme necessário; depois atualize a implantação com uma nova versão.

Esses limites reduzem acúmulo de arquivos, mas não impedem abuso ou esgotamento das cotas de execução do Google. A URL é pública na VM, não é uma senha. Alunos com root podem inventar matrícula/sessão e recalcular hashes. Receber no Drive não autentica o aluno nem prova a conclusão. Não se armazena chave Google na VM. Para encerrar os envios, arquive a implantação ou publique `RECEBIMENTO_ATIVO = false`.

## Protocolo e testes

POST HTTPS com `Content-Type: text/plain; charset=utf-8` e bytes do TXT no corpo. O ContentService redireciona a resposta; o cliente usa `curl --location` sem forçar POST após o redirecionamento. Sucesso tem três linhas:

```text
OK
ARQUIVO=usuarios-grupos_<matricula>_<sessao>.txt
CODIGO=SHA256:<hash>
```

Falhas devolvem `ERRO=<motivo>`; HTTP 200 sozinho não confirma recebimento. O cliente exige nome e código correspondentes. Não imprime mensagens arbitrárias ou páginas de login devolvidas pelo servidor.

Testes locais, a partir da raiz do repositório:

```bash
node tests/test_google_drive.cjs
python3 -m unittest discover -s tests -p 'test_validar_comprovante.py' -v
docker run --rm -e LAB_TEST_CONTAINER=1 -v "$PWD:/lab:ro" ubuntu:24.04 bash /lab/tests/usuarios-grupos.sh
```

Os testes do Apps Script usam substitutos em memória de DriveApp, PropertiesService e LockService. O cliente usa um substituto de curl nos testes, sem enviar dados à internet. Depois de implantar, é necessário validar um envio real e conferir o arquivo na pasta. A gravação do histórico de comandos não faz parte desta integração; somente o comprovante TXT é enviado.

O receptor e o validador Python ficam em `professor/`, fora do cenário e dos assets da VM. Somente o cliente de envio e a URL pública vão para o Killercoda.

Referências: [aplicativos da Web](https://developers.google.com/apps-script/guides/web), [ContentService e redirecionamento](https://developers.google.com/apps-script/guides/content), [bloqueio de concorrência](https://developers.google.com/apps-script/reference/lock/lock-service).
