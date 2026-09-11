# Guia do professor — Partições no Linux

## Aplicação sem acompanhamento ao vivo

`particoes-linux` foi reduzido para **uma sessão de até 60 minutos**, com comandos completos, saídas esperadas e instruções para erros comuns. Não exige que o professor esteja presente para explicar os procedimentos normais. A estimativa pressupõe que o aluno já saiba digitar/copiar comandos e navegar pela interface.

São oito etapas práticas, planejadas para 50 minutos, com mais 5 para preparação e 5 para emissão/download. Essa é uma estimativa didática, não garantia de tempo por aluno; instalação, rede e familiaridade com o terminal podem afetá-la. O aluno deve acompanhar o cronômetro e reservar os minutos finais para a entrega. Não há mecanismos de salvar/importar progresso entre sessões.

| Etapa | Minutos | Critérios técnicos |
|---|---:|---|
| Preparação/identificação | 5 | Dois loops de 1 GiB e identificação comum |
| 1. Inventário | 4 | Relatório com dispositivos e ocupação |
| 2. Tabelas/partições | 9 | MBR com p1 1–513 MiB e p2 513–769 MiB; GPT com p1 1–513 MiB e p2 513–897 MiB |
| 3. Formatação | 7 | MBR: ext4 DADOS_MBR e ext2 TEMP_MBR; GPT: ext4 DADOS_GPT e FAT32 TROCA |
| 4. Montagem/arquivos | 7 | Quatro origens/destinos corretos em rw e arquivos identificados |
| 5. Ocupação/diagnóstico | 5 | Carga de 16 MiB, relatório e TROCA em ro |
| 6. Desmontagem | 4 | Nenhuma partição do exercício montada |
| 7. UUID/backup | 5 | Quatro volumes remontados em rw, dados presentes e backup TAR correto |
| 8. Exclusão/recuperação | 9 | MBR p2 excluída; demais volumes intactos/montados, backup e arquivo recuperado; três respostas com pelo menos 120 caracteres no total |
| Entrega | 5 | TXT v2 e histórico legível; download antes de encerrar |

A configuração de `/etc/fstab`, relatórios longos e tarefas sem exemplos completos foram retirados para caber na sessão. A montagem por UUID permanece, usando `mount -U`. Os comandos `read` das perguntas finais são individuais para o aluno não colar respostas acidentalmente como comandos.

## Infraestrutura

`preparar-discos` instala as ferramentas quando necessário e associa duas imagens esparsas a loops livres. Não cria tabelas ou resolve as tarefas. Repetir não trunca imagens nem apaga dados. Os verificadores confirmam o arquivo associado a cada loop e o tamanho de 1 GiB, sem operar no disco do sistema.

- Imagens: `/var/lib/lab-particoes/mbr.img` e `gpt.img`.
- Variáveis: `/root/discos.env` (`MBR` e `GPT`).
- Mapeamento: `/var/lib/lab-particoes/discos.json`.
- Checkpoints: `/var/lib/lab-particoes/progresso.json`.
- Relatórios: `/root/relatorio-discos/{inventario,ocupacao,conclusao}.txt`.
- Volumes: `/mnt/lab/{dados-mbr,temporario,dados-gpt,troca}`.

`atualizar-particoes` relê as tabelas com partprobe e aguarda udev quando disponível. Em ambientes mínimos cria somente os nós de partição já registrados pelo kernel para os loops do exercício.

## Verificação e avaliação

`verify-step1.sh` a `verify-step8.sh` chamam `particoes.py`. Os verificadores leem o estado e registram checkpoints; não formatam, montam nem corrigem tarefas. O aluno precisa usar CHECK em ordem. SKIP não registra uma etapa válida.

Os checkpoints guardam os estados transitórios: ro na etapa 5 e desmontado na 6 continuam válidos depois das transições intencionais. A etapa 8 sempre revalida o estado final, inclusive quando `gerar-comprovante` ou `enviar-comprovante` executam novamente os verificadores. Assim, a emissão não exige recriar a partição excluída e falha se os volumes finais ou arquivos estiverem incorretos.

Os relatórios de inventário e ocupação são gerados por comandos; as três respostas finais são preenchidas pelo aluno e exibidas no histórico. O CHECK verifica presença/tamanho, não o mérito das explicações. A montagem por UUID e a tentativa que produz “busy” aparecem no histórico; o verificador avalia o resultado técnico, não prova a sequência exata de comandos. Avalie posteriormente as respostas e o LOG, além do comprovante.

Como em qualquer VM com root, o aluno pode alterar checkpoints, arquivos e hashes. O mecanismo fornece evidências didáticas, não uma atestação inviolável.

## Entrega e publicação

Reutiliza identificação, TXT v2 (`LABORATORIO=particoes-linux`), histórico legível e envio para a pasta Drive já configurada. Os relatórios entram no LOG pelo `cat` final, sem anexos extras. Há instruções completas de download pelo Editor e entrega no Moodle, incluindo fallback quando o Drive não confirma o recebimento.

O catálogo em `professor/laboratorios.json` e `professor/google-drive/Code.gs` inclui o novo laboratório. **Atualize o Code.gs e publique uma nova versão da implantação existente** para o endpoint aceitar esse ID. Commit/push não atualiza o Apps Script.

Antes de disponibilizar para execução sem acompanhamento, faça uma sessão de teste no Killercoda: preparação, comandos, CHECKs, limite de tempo, Editor/download e recebimento real. Os testes locais Ubuntu/Docker validam o fluxo Linux e o comprovante, mas não a interface web nem o tempo que cada aluno levará. O roteiro completo de teste está fora dos assets em `tests/particoes-linux.sh`.

## Referências

- [Killercoda — documentação para criadores](https://killercoda.com/creators).
- [GNU Parted — manual](https://www.gnu.org/software/parted/manual/parted.html).
- [losetup — util-linux](https://man7.org/linux/man-pages/man8/losetup.8.html).
