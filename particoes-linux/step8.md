# 8. Excluir e recuperar — 9 minutos

Você excluirá **somente a partição 2 do disco MBR**, usada como temporária. O disco GPT e a partição MBR p1 devem permanecer intactos.

```bash
cd /root
sync
umount /mnt/lab/temporario
parted -s "$MBR" rm 2
atualizar-particoes
parted "$MBR" unit MiB print free
lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINTS "$MBR" "$GPT"
```

Confira: MBR agora tem **uma** partição; GPT continua com **duas**. O espaço não particionado no MBR aumentou. Excluir uma entrada da tabela não é o mesmo que apagar seguramente todos os bytes antigos.

Se `rm 2` informar que a partição não existe, confira a tabela: ela pode já ter sido excluída. Não remova outra partição. Se informar que está em uso, confirme a desmontagem antes de prosseguir.

Restaure o rascunho a partir do backup, no volume permanente:

```bash
mkdir -p /mnt/lab/dados-gpt/recuperados
tar -xvf /mnt/lab/dados-gpt/backup.tar -C /mnt/lab/dados-gpt/recuperados
cat /mnt/lab/dados-gpt/recuperados/rascunho.txt
cmp /mnt/lab/dados-mbr/equipe.txt /mnt/lab/dados-gpt/recuperados/rascunho.txt
```

`cmp` sem saída indica arquivos iguais. Não recrie a partição temporária: a recuperação ocorreu em outro volume.

Responda às três perguntas no terminal, com uma frase explicativa para cada uma. **Execute uma linha de `read` por vez, digite sua resposta e pressione Enter antes da próxima**:

`read -r -p 'Qual a diferença entre lsblk e df? ' R1`{{exec}}

`read -r -p 'Por que touch falhou no volume em ro? ' R2`{{exec}}

`read -r -p 'Qual a diferença entre desmontar e excluir uma partição? ' R3`{{exec}}

Grave e exiba as respostas:

```bash
printf 'lsblk e df: %s\nSomente leitura: %s\nDesmontar e excluir: %s\n' "$R1" "$R2" "$R3" > /root/relatorio-discos/conclusao.txt
cat /root/relatorio-discos/*.txt
```

Escreva pelo menos **120 caracteres no total**, com suas palavras. Se precisar corrigir, repita os `read` e o `printf`. O professor avaliará posteriormente o conteúdo das respostas e o histórico.

Pressione **CHECK**. O estado final deve ter três volumes montados em leitura e escrita, MBR p2 excluída, backup e rascunho recuperado. **Mantenha os volumes montados e avance imediatamente para gerar e baixar a entrega.**
