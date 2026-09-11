# Registro do terminal

A identificação inicia automaticamente `iniciar-registro` quando executada em terminal interativo. O comando usa `script` do util-linux, somente com `--log-out`, `--flush` e `--append`, e abre um Bash interativo. A gravação fica em `/root/registros/<sessao>.log` e inclui as saídas e o eco dos comandos daquela aba, também nos shells de `su - julia`.

O registro começa após informar a matrícula. A matrícula e sessão já constam no TXT. Se a identificação for executada sem terminal interativo (por exemplo, por automação), ela registra os dados e orienta iniciar a gravação no terminal; não inventa um histórico.

Executar a identificação novamente na sessão gravada não cria gravações aninhadas. Ao sair do shell gravado com `exit`, a gravação termina; `iniciar-registro` permite retomar anexando ao mesmo arquivo. Não há recuperação de comandos executados antes do início, em outras abas, via Editor ou enquanto a gravação estava interrompida. A interface CHECK pode executar verificações separadas, que não passam pelo terminal gravado.

## Senhas e dados visíveis

Não se usam `--log-in` ou `--log-io`. A entrada oculta de `passwd` e de programas que desativam o eco não é gravada como saída. Isso não é um filtro geral de segredos: senhas escritas na linha de comando, arquivos exibidos na tela e qualquer saída sensível aparecem no registro. As instruções orientam usar apenas dados e senhas do exercício.

O registro é uma transcrição bruta do terminal, não uma lista limpa do histórico Bash. Pode conter CR, sequências ANSI, edição de linha e saída de editores. Leia como arquivo de texto, sem executar seu conteúdo. Permissões locais: registros e snapshots são privados para root (modo 600 ou diretório privado).

## Emissão e associação

`gerar-comprovante` continua executando os sete verificadores e agora também exige um registro não vazio com até 1 MiB. Não se truncam arquivos maiores silenciosamente: o aluno é orientado a baixar o registro e falar com o professor.

Na emissão é criada uma cópia em:

`/root/comprovantes/<laboratorio>_<matricula>_<sessao>_<hash-do-comprovante>_historico.log`

O hash no nome é o valor hexadecimal do campo CODIGO do comprovante, sem `SHA256:`. O TXT atual usa v2 e inclui NOME; o formato do registro permanece igual. O histórico não entra no hash interno do TXT; a associação é feita pelo nome do arquivo. O pacote de envio e sua confirmação também usam o SHA-256 dos bytes do próprio histórico para conferir o transporte.

O snapshot inclui o terminal até a cópia, antes de imprimir o comprovante e fazer upload. Comandos ou saídas posteriores, inclusive a confirmação do Drive, não fazem parte dele. `enviar-comprovante` repete o envio do snapshot, sem copiar novamente o registro vivo. Se uma emissão produz o mesmo hash de TXT (por exemplo, no mesmo segundo), o snapshot existente é reutilizado. Nova emissão com outro hash cria um novo snapshot e preserva os anteriores.

A entrega é um par: TXT e LOG. O receptor salva o histórico antes do comprovante e só confirma sucesso ao concluir ambos. Se uma gravação falhar, pode existir um arquivo parcial da entrega no Drive; o reenvio idêntico completa o par. O receptor não substitui um histórico já associado à mesma emissão por outros bytes.

O validador Python do professor confere TXT v1 e v2. Ele não verifica o conteúdo pedagógico do histórico nem sua associação; o professor deve consultar o LOG correspondente pelo nome. Este registro é evidência auxiliar, não prova inviolável: root pode parar a gravação, alterar os arquivos ou fabricar conteúdo e hashes.

Referência: [script — util-linux](https://man7.org/linux/man-pages/man1/script.1.html).
