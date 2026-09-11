# Discos e partições no Linux — até 60 minutos

Nesta atividade guiada você usará **dois discos virtuais de 1 GiB**. Um terá tabela **MBR** (também chamada `msdos`), o outro **GPT**. Você criará partições ext4, ext2 e FAT32, montará e desmontará volumes, usará `lsblk` e `df` e fará backup antes de excluir uma partição.

O roteiro contém todos os comandos necessários e pode ser realizado sem acompanhamento ao vivo. Execute os blocos na ordem e compare os resultados com as explicações. **A estimativa é de 50 minutos de tarefas, mais 5 para preparação e 5 para entregar.** Se concluir antes, avance: não é preciso esperar o tempo indicado.

| Etapa | Tempo estimado |
|---|---:|
| Preparação e identificação | 5 min |
| 1. Reconhecer os discos | 4 min |
| 2. Tabelas e quatro partições | 9 min |
| 3. Formatação | 7 min |
| 4. Montagem e arquivos | 7 min |
| 5. Ocupação e somente leitura | 5 min |
| 6. Desmontagem | 4 min |
| 7. Montagem por UUID e backup | 5 min |
| 8. Exclusão e recuperação | 9 min |
| Comprovante e download | 5 min |

**A sessão termina após 60 minutos.** Use o tempo do roteiro como orientação e reserve os minutos finais para baixar a entrega. Não há retomada entre sessões.

Os discos são arquivos associados a dispositivos `/dev/loopN`; o Linux permite trabalhar neles como dispositivos de bloco. **Use apenas `$MBR` e `$GPT`**, definidos na preparação. Não substitua por `/dev/sda`, `/dev/vda` ou outro disco do sistema. Os números de loop podem ser diferentes dos números de um colega.

Faça tudo na mesma aba de terminal, começando pela identificação. Pressione **CHECK em cada etapa antes de avançar**. Estados intermediários ficam registrados, permitindo desmontar ou excluir o que foi criado anteriormente. **SKIP não conclui tarefas.**

Se aparecer uma pendência, leia a mensagem e corrija antes de continuar. Os passos indicam os erros esperados e como resolvê-los. Ao final, entregue o TXT e o histórico conforme a página de conclusão.
