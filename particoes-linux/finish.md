# Entrega — últimos 5 minutos

Na sessão de `root`, execute:

`gerar-comprovante`{{exec}}

O comando confere os oito checkpoints e verifica novamente o estado final. Montagens e partições de etapas intermediárias ficam registradas pelos CHECKs; não precisam ser recriadas. Se indicar um requisito pendente, corrija-o e execute o comando novamente. Os arquivos só são gerados quando todas as verificações passam e existe registro do terminal.

O terminal informa os caminhos do TXT e do histórico `_historico.log`, salvos na pasta `/root/comprovantes`. O histórico é uma cópia da gravação até a emissão; comandos posteriores não entram nessa cópia. O nome reúne laboratório, matrícula e sessão, por exemplo:

`particoes-linux_202612345_550e8400-e29b-41d4-a716-446655440000.txt`

Para localizar seu arquivo:

`ls -lh /root/comprovantes/`{{exec}}

## Entrega no Google Drive

Quando o envio automático estiver configurado pelo professor, `gerar-comprovante` também enviará o TXT e o histórico para a pasta de entrega. Aguarde a mensagem **Recebimento confirmado no Google Drive**. A confirmação deve citar os dois arquivos. Apenas gerar os arquivos não confirma o envio.

Se houver falha de conexão, mantenha a sessão aberta e tente novamente sem gerar outro comprovante:

`enviar-comprovante`{{exec}}

**Não espere o tempo da sessão acabar tentando reenviar.** Se o serviço estiver indisponível ou ainda não configurado, baixe o TXT e o histórico e entregue conforme a orientação do professor. O envio ao Drive não realiza a submissão no Moodle; se a atividade do Moodle exigir anexo, envie o TXT por lá também.

## Baixar o arquivo

1. Clique na aba **Editor**, no topo do ambiente Killercoda.
2. No explorador de arquivos, abra a pasta `comprovantes` dentro de `/root`. Se ela não estiver visível, use **File → Open Folder…** e informe `/root/comprovantes`.
3. Clique com o botão direito no arquivo `.txt` indicado pelo comando e escolha **Download**. Repita para o arquivo `_historico.log` indicado na mesma emissão.
4. Confira se os dois arquivos foram salvos no seu computador, normalmente na pasta **Downloads**.
5. No Moodle, abra a atividade correspondente, anexe o comprovante `.txt` e o histórico `.log` e confirme a entrega conforme as instruções do professor.

Envie os arquivos originais baixados, sem editar seu conteúdo. Não substitua o TXT por uma captura de tela ou pelo texto copiado do terminal.

Se gerar novamente, as etapas serão verificadas outra vez e o arquivo da mesma sessão será substituído, com uma nova data de emissão. O histórico anterior é preservado. Baixe o TXT e o histórico associados à emissão mais recente, conforme os caminhos mostrados no terminal.

**Baixe o arquivo antes de encerrar o laboratório. O ambiente é temporário e seus arquivos não ficam disponíveis após o encerramento.**

As respostas da última etapa estarão no histórico porque foram exibidas com `cat`. O download do TXT e do LOG é indispensável se o envio automático falhar. Não há salvamento/retomada entre sessões neste roteiro.
