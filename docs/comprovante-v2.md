# Comprovante TXT — formato v2

A emissão atual acrescenta `NOME` depois de `MATRICULA`. O nome completo é solicitado na identificação, conservando acentos e espaços internos. Espaços ASCII nas extremidades são removidos na entrada. Exige-se nome não vazio, UTF-8 válido, até 200 bytes, sem caracteres de controle ASCII (0–31 e 127). Não se executa o conteúdo do campo como código.

O nome não entra no nome do arquivo; este continua identificando laboratório, matrícula e UUID. Quem já possui um registro antigo sem NOME pode executar `identificar-aluno` novamente para acrescentá-lo, mantendo matrícula, sessão e histórico.

## Bytes e hash

Exatamente oito linhas UTF-8, sem BOM, terminadas em LF inclusive na última linha. Ordem: VERSAO, LABORATORIO, MATRICULA, NOME, SESSAO, DATA, RESULTADO, CODIGO. A versão deve ser `2`. O campo LABORATORIO recebe o ID do cenário cadastrado (`[a-z][a-z0-9-]{0,39}`), não apenas `usuarios-grupos`. O nome do arquivo é `<laboratorio>_<matricula>_<sessao>.txt`. As demais regras são as do [formato v1](comprovante-v1.md).

O SHA-256 cobre os bytes exatos das primeiras **sete** linhas, incluindo o LF após RESULTADO. Isso inclui o nome. Não normalizar Unicode, espaços ou acentos antes do cálculo. Exemplo:

```text
VERSAO=2
LABORATORIO=usuarios-grupos
MATRICULA=202612345
NOME=José da Silva
SESSAO=550e8400-e29b-41d4-a716-446655440000
DATA=2026-09-11T18:30:00Z
RESULTADO=CONCLUIDO
CODIGO=SHA256:29e3f5afe1a15c14bbc3df3ebd773af4c4fdc1be4f01eae592a0bd56dcd3adb2
```

O validador local e o receptor atualizado aceitam v1 (sem nome) e v2 (com nome), cada uma com sua quantidade e ordem exatas de campos. Não adicionar NOME a um TXT v1 nem editar um TXT emitido: gerar novamente pelo script.

O transporte JSON com histórico permanece na versão 2 e pode conter comprovantes v1 ou v2. Essas versões são independentes. Atualize o Code.gs e publique uma nova versão da implantação antes de usar a emissão com nome. A URL do Apps Script pode permanecer a mesma.

O nome é autodeclarado, assim como a matrícula. O hash não autentica a identidade; as limitações de root e a associação do histórico permanecem as descritas no [registro do terminal](registro-terminal.md).
