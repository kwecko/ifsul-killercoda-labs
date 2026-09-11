# Comprovante para entrega no Moodle

Na sessão de `root`, execute:

`gerar-comprovante`{{exec}}

O comando verifica novamente todas as etapas. Se indicar um requisito pendente, corrija-o e execute o comando novamente. O arquivo só é gerado quando todas as verificações passam.

O terminal informa o caminho completo do TXT, salvo na pasta `/root/comprovantes`. O nome reúne laboratório, matrícula e sessão, por exemplo:

`usuarios-grupos_202612345_550e8400-e29b-41d4-a716-446655440000.txt`

Para localizar seu arquivo:

`ls -lh /root/comprovantes/*.txt`{{exec}}

## Entrega no Google Drive

Quando o envio automático estiver configurado pelo professor, `gerar-comprovante` também enviará o TXT para a pasta de entrega. Aguarde a mensagem **Recebimento confirmado no Google Drive**. Apenas gerar o arquivo não confirma o envio.

Se houver falha de conexão, mantenha a sessão aberta e tente novamente sem gerar outro comprovante:

`enviar-comprovante`{{exec}}

Se o serviço estiver indisponível ou ainda não configurado, baixe o TXT e entregue conforme a orientação do professor. O envio ao Drive não realiza a submissão no Moodle; se a atividade do Moodle exigir anexo, envie o TXT por lá também.

## Baixar o arquivo

1. Clique na aba **Editor**, no topo do ambiente Killercoda.
2. No explorador de arquivos, abra a pasta `comprovantes` dentro de `/root`. Se ela não estiver visível, use **File → Open Folder…** e informe `/root/comprovantes`.
3. Clique com o botão direito no arquivo `.txt` indicado pelo comando e escolha **Download**.
4. Confira se o arquivo foi salvo no seu computador, normalmente na pasta **Downloads**.
5. No Moodle, abra a atividade correspondente, anexe esse arquivo `.txt` e confirme a entrega conforme as instruções do professor.

Envie o arquivo original baixado, sem editar seu conteúdo. Não substitua o TXT por uma captura de tela ou pelo texto copiado do terminal.

Se gerar novamente, as etapas serão verificadas outra vez e o arquivo da mesma sessão será substituído, com uma nova data de emissão. Baixe a versão mais recente.

**Baixe o arquivo antes de encerrar o laboratório. O ambiente é temporário e seus arquivos não ficam disponíveis após o encerramento.**
