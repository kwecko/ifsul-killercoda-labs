# Comprovante TXT — formato v1

Formato anterior, mantido para leitura dos comprovantes já emitidos. A emissão atual usa [v2, com nome completo](comprovante-v2.md).

## Emissão no Killercoda

`identificar-aluno` mantém o registro existente em `/root/.laboratorio-aluno`: matrícula numérica, UUID completo gerado por `/proc/sys/kernel/random/uuid` e início da atividade. A matrícula é texto, preservando zeros à esquerda. Não se abrevia o UUID para oito caracteres; usa-se o identificador completo para reduzir colisões. O mesmo registro é reutilizado na sessão.

`gerar-comprovante` executa os sete verificadores existentes, de 0 a 6, e só publica o TXT se todos retornarem sucesso. Os critérios das etapas e o `index.json` permanecem inalterados. A validação confere o estado atual, sem exigir um histórico dos cliques em CHECK.

Destino: `/root/comprovantes/usuarios-grupos_<matricula>_<sessao>.txt`.

O arquivo é escrito primeiro em um temporário no mesmo diretório e renomeado após a gravação completa. Uma nova emissão válida substitui o arquivo da mesma matrícula/sessão e registra a data dessa emissão. Uma tentativa reprovada não cria nem substitui o TXT; se houver uma emissão anterior, ela permanece como registro daquela emissão, não do estado atual. O script não revoga cópias já baixadas.

A emissão também exige o registro do terminal e cria um snapshot separado, descrito em [registro-terminal.md](registro-terminal.md). O formato do TXT v1 permanece inalterado.

O download é feito pelo menu Download do explorador do Editor do Killercoda. Não é necessário iniciar servidor HTTP nem instalar pacotes adicionais. O aluno entrega o TXT original no Moodle.

## Serialização exata

UTF-8 sem BOM, terminadores LF (`0x0a`), incluindo um LF ao final da última linha. Exatamente sete linhas na ordem abaixo, sem espaços extras, aspas, linhas vazias ou campos repetidos:

| Linha | Campo | Valor |
|---|---|---|
| 1 | VERSAO | Literal `1` |
| 2 | LABORATORIO | Literal `usuarios-grupos` |
| 3 | MATRICULA | Um ou mais dígitos ASCII; preservar zeros à esquerda |
| 4 | SESSAO | UUID completo, 36 caracteres no padrão `8-4-4-4-12` hexadecimal |
| 5 | DATA | Data/hora de emissão em UTC, `AAAA-MM-DDTHH:MM:SSZ`, sem frações |
| 6 | RESULTADO | Literal `CONCLUIDO` |
| 7 | CODIGO | `SHA256:` seguido de 64 dígitos hexadecimais minúsculos |

A sessão produzida normalmente pelo Linux é um UUID aleatório v4. Para preservar compatibilidade com o verificador existente, a sintaxe aceita hexadecimais maiúsculos ou minúsculos, sem restringir versão/variante. A grafia do registro é preservada no TXT e no nome do arquivo.

`CODIGO` é o SHA-256 dos **bytes exatos das primeiras seis linhas**, incluindo o LF após `RESULTADO=CONCLUIDO`. A linha `CODIGO`, o nome do arquivo e o caminho não entram no hash. Não normalizar espaços, maiúsculas, encoding ou terminadores antes do cálculo.

O validador local verifica a estrutura, os valores fixos, a validade da data, a sintaxe dos campos e o digest. Campos desconhecidos, duplicados, ausentes ou reordenados e versões desconhecidas devem ser rejeitados. O nome esperado é derivado dos campos LABORATORIO, MATRICULA e SESSAO e pode ser conferido separadamente; renomear o arquivo não altera seu hash. O validador está em `professor/validar_comprovante.py`, fora do cenário e dos assets enviados à VM. Consulte `professor/README.md` para utilização.

## Vetor de referência

Nome: `usuarios-grupos_202612345_550e8400-e29b-41d4-a716-446655440000.txt`.

Os bytes do exemplo abaixo incluem LF depois de cada linha, inclusive a última:

```text
VERSAO=1
LABORATORIO=usuarios-grupos
MATRICULA=202612345
SESSAO=550e8400-e29b-41d4-a716-446655440000
DATA=2026-09-11T18:30:00Z
RESULTADO=CONCLUIDO
CODIGO=SHA256:f8697dc31a6e836d509bc0edaf6051ef45840c10de36e142eb18b83578a0937f
```

## Limite de confiança

Este é um checksum público, sem chave, não uma assinatura digital nem um HMAC. Detecta corrupção ou edição que não seja acompanhada de recálculo do código. **Não detecta adulteração deliberada acompanhada de um novo hash.**

O aluno é root e pode alterar o registro, relógio, scripts, resultados e o próprio TXT, ou recalcular o SHA-256. Portanto, o comprovante não autentica o aluno, não atesta uma hora confiável e não prova conclusão contra um aluno que controle a VM. A restrição de emissão vale para o fluxo normal do script, não como barreira de segurança contra root.

Uma chave privada, senha ou chave de HMAC guardada ou ofuscada na VM não resolveria isso. Para resistência a falsificação seria necessário um componente externo confiável, com chave fora da VM e evidências de conclusão verificadas independentemente; simplesmente assinar o que a VM informa também não prova a conclusão. Essa infraestrutura está fora desta tarefa. O validador offline do professor pode atestar consistência do formato e do checksum, não autenticidade da origem, neste formato v1.

## Referências

- [Linux: geração de UUID pelo kernel](https://docs.kernel.org/admin-guide/sysctl/kernel.html#random).
- [Killercoda: Editor e assets](https://killercoda.com/creators).
- [Theia: menu de download no explorador](https://github.com/eclipse-theia/theia/blob/master/packages/navigator/src/browser/navigator-contribution.ts).
