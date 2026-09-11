# 5. Ocupação e somente leitura — 5 minutos

Observe o uso antes e depois de criar um arquivo de 16 MiB:

```bash
df -hT /mnt/lab/dados-gpt
dd if=/dev/zero of=/mnt/lab/dados-gpt/carga.bin bs=1M count=16 status=progress
sync
{ df -hT /mnt/lab/dados-gpt; du -h /mnt/lab/dados-gpt/carga.bin; lsblk -o NAME,SIZE,FSTYPE "$GPT"; } > /root/relatorio-discos/ocupacao.txt
cat /root/relatorio-discos/ocupacao.txt
```

`df` mostra uso do sistema de arquivos; `du`, uso por arquivo; `lsblk`, dispositivos e seus tamanhos. Gravar um arquivo ocupa espaço, mas não aumenta a partição. Volumes recém-formatados já usam algum espaço com metadados.

Agora torne TROCA somente leitura:

```bash
mount -o remount,ro /mnt/lab/troca
findmnt -no SOURCE,FSTYPE,OPTIONS /mnt/lab/troca
cat /mnt/lab/troca/equipe.txt
touch /mnt/lab/troca/teste.txt
```

**A falha do último comando é esperada**: deve indicar sistema de arquivos somente leitura. Ler continua funcionando. Isso não se resolve com `chmod`, porque `ro` é uma opção da montagem.

**Pressione CHECK agora, com TROCA ainda em `ro`.** Depois do sucesso, execute:

`mount -o remount,rw /mnt/lab/troca`{{exec}}

Se voltou para `rw` antes do CHECK, execute novamente `mount -o remount,ro /mnt/lab/troca`, confira o CHECK e então volte para `rw`.
