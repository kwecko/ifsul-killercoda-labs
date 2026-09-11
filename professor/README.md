# Validação local dos comprovantes

Requer Python 3.8 ou superior, sem dependências adicionais. Execute no computador do professor, a partir da raiz deste repositório:

```bash
python3 professor/validar_comprovante.py /caminho/comprovante.txt
python3 professor/validar_comprovante.py /caminho/entregas/*.txt
python3 professor/validar_comprovante.py --matricula 202612345 /caminho/comprovante.txt
python3 professor/validar_comprovante.py --laboratorio usuarios-grupos --conferir-nome /caminho/comprovante.txt
```

Coloque caminhos com espaços entre aspas. Informe arquivos, não pastas ou ZIPs; extraia primeiro os arquivos baixados do Moodle. Em Windows, informe os arquivos individualmente se o terminal não expandir `*.txt`.

O programa lê `laboratorios.json` ao lado do script, gerado pelo comando de sincronização. Distribua os dois arquivos juntos. Ele aceita apenas laboratórios cadastrados; `--laboratorio ID` também exige a atividade esperada. Laboratórios com recebimento desativado continuam reconhecidos localmente para permitir avaliar entregas anteriores.

O programa verifica a serialização exata, os campos e sua ordem, versão, laboratório, matrícula, UUID, data válida em UTC, resultado e SHA-256. Ele apenas lê os arquivos, não os altera e não executa seu conteúdo. `--matricula` compara com o número informado pelo professor, preservando zeros à esquerda; se houver vários arquivos, compara todos com essa mesma matrícula.

Por padrão, renomear o arquivo gera apenas um aviso, pois o Moodle ou o navegador podem alterar o nome durante o download. Use `--conferir-nome` para exigir o nome definido no contrato.

Saídas: **CONSISTENTE** significa formato e checksum corretos; **INVÁLIDO** indica erro e sua causa. O código de saída é `0` se todos forem consistentes, `1` se qualquer arquivo for inválido ou ilegível e `2` para erro no uso da linha de comando.

**Limite:** quem controla a VM como root pode modificar os dados e recalcular o hash. O resultado CONSISTENTE não comprova autenticidade, autoria ou conclusão real. Não há chave secreta e não se consulta nenhum serviço externo.

Esta pasta está fora de `usuarios-grupos/`, não possui `index.json` e não é referenciada nos assets do cenário. Portanto, o script não é instalado na VM pelo fluxo configurado do Killercoda. Ele pode ser versionado no GitHub; se o repositório for público, seu código continuará público. A proteção não depende de escondê-lo.

Contratos: [formato v2 com nome](../docs/comprovante-v2.md) e [formato v1 anterior](../docs/comprovante-v1.md). O validador aceita ambos e exibe o nome quando presente.

Testes locais:

```bash
python3 -m unittest discover -s tests -p 'test_validar_comprovante.py' -v
```
