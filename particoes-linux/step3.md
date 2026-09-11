# 3. Formatar os volumes — 7 minutos

Cada comando abaixo cria um sistema de arquivos **na partição**, não no disco inteiro. As chaves em `"${MBR}p1"` separam a variável do sufixo `p1`.

```bash
mkfs.ext4 -L DADOS_MBR "${MBR}p1"
mkfs.ext2 -L TEMP_MBR "${MBR}p2"
mkfs.ext4 -L DADOS_GPT "${GPT}p1"
mkfs.vfat -F 32 -n TROCA "${GPT}p2"
```

Confira:

```bash
lsblk -f "$MBR" "$GPT"
blkid "${MBR}p1" "${MBR}p2" "${GPT}p1" "${GPT}p2"
```

| Volume | TYPE esperado | LABEL esperado |
|---|---|---|
| MBR p1 | ext4 | DADOS_MBR |
| MBR p2 | ext2 | TEMP_MBR |
| GPT p1 | ext4 | DADOS_GPT |
| GPT p2 | vfat | TROCA |

FAT32 aparece como `vfat` no Linux. ext4 possui journaling; ext2 não. FAT32 é comum em troca de arquivos entre sistemas. `LABEL` é um nome para o volume; `UUID` é seu identificador. Nenhum deles é a tabela MBR/GPT.

Se uma partição não existir, rode `atualizar-particoes` e confira a etapa anterior. Se aparecer aviso de sistema de arquivos já existente, não confirme uma nova formatação sem conferir: você pode estar repetindo um comando. **Não formate depois de montar ou gravar arquivos.**

Pressione **CHECK**.
