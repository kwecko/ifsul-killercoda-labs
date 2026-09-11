# 6. Desmontar — 4 minutos

Simule um volume ocupado:

```bash
cd /mnt/lab/dados-mbr
umount /mnt/lab/dados-mbr
```

**A falha “target is busy” é esperada:** seu shell está dentro do volume. Resolva saindo dele e desmonte os quatro:

```bash
cd /root
sync
umount /mnt/lab/dados-mbr
umount /mnt/lab/temporario
umount /mnt/lab/dados-gpt
umount /mnt/lab/troca
lsblk -o NAME,FSTYPE,MOUNTPOINTS "$MBR" "$GPT"
ls -la /mnt/lab/dados-mbr
df -hT /mnt/lab/dados-mbr
```

Os pontos de montagem ficam vazios em `lsblk`. Os arquivos deixam de aparecer no diretório, mas **continuam na partição**. O `df` desse diretório agora mostra o sistema de arquivos principal, onde o diretório vazio está localizado.

Se ainda aparecer “busy”, confirme `pwd` mostrando `/root` e feche outros processos/abas que estejam usando o volume. Não use `umount -f` ou `-l`. Se disser “not mounted”, ele já está desmontado: confira com `lsblk`.

**Pressione CHECK antes de montar novamente.**
