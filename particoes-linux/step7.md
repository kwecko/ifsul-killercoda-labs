# 7. Montar por UUID e fazer backup — 5 minutos

Um UUID identifica o sistema de arquivos, independentemente do número do dispositivo. Veja os valores e monte por UUID:

```bash
blkid "${MBR}p1" "${MBR}p2" "${GPT}p1" "${GPT}p2"
mount -U "$(blkid -s UUID -o value "${MBR}p1")" /mnt/lab/dados-mbr
mount -U "$(blkid -s UUID -o value "${MBR}p2")" /mnt/lab/temporario
mount -U "$(blkid -s UUID -o value "${GPT}p1")" /mnt/lab/dados-gpt
mount -U "$(blkid -s UUID -o value "${GPT}p2")" /mnt/lab/troca
cat /mnt/lab/temporario/rascunho.txt
```

Os dados reaparecem sem formatação. `$(...)` usa a saída de `blkid` como argumento de `mount`. Não vamos editar `/etc/fstab` nem reiniciar a máquina.

Antes de excluir a partição temporária, copie seu rascunho para um backup no volume permanente GPT:

```bash
tar -cvf /mnt/lab/dados-gpt/backup.tar -C /mnt/lab/temporario rascunho.txt
tar -tvf /mnt/lab/dados-gpt/backup.tar
tar -xOf /mnt/lab/dados-gpt/backup.tar rascunho.txt
```

Confira seu nome e matrícula na saída do último comando. O backup precisa estar **fora da partição que será excluída**. Ele está no mesmo ambiente virtual e não protege contra a expiração da sessão.

Se o arquivo não for encontrado, confira as quatro montagens com `lsblk -f`. Não formate novamente para tentar recuperar arquivos.

**Pressione CHECK antes de excluir qualquer partição.**
