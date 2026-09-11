# 2. Criar tabelas e partições — 9 minutos

**MBR e GPT são tabelas de partições**, não sistemas de arquivos. O Parted chama a tabela MBR de `msdos`. Usaremos duas partições primárias em MBR e duas partições em GPT.

Execute estes comandos **uma única vez** para criar as tabelas:

```bash
parted -s "$MBR" mklabel msdos
parted -s "$GPT" mklabel gpt
```

Crie as quatro partições, com limites em MiB:

```bash
parted -s "$MBR" mkpart primary ext4 1MiB 513MiB
parted -s "$MBR" mkpart primary ext2 513MiB 769MiB
parted -s "$GPT" mkpart dados ext4 1MiB 513MiB
parted -s "$GPT" mkpart troca fat32 513MiB 897MiB
atualizar-particoes
```

| Disco | Partição | Tamanho | Uso |
|---|---|---:|---|
| MBR | p1 | 512 MiB | dados ext4 |
| MBR | p2 | 256 MiB | temporário ext2 |
| GPT | p1 | 512 MiB | dados ext4 |
| GPT | p2 | 384 MiB | troca FAT32 |

Confira:

```bash
fdisk -l "$MBR" "$GPT"
parted "$MBR" unit MiB print free
parted "$GPT" unit MiB print free
lsblk -o NAME,SIZE,TYPE,FSTYPE "$MBR" "$GPT"
```

Você deve ver duas partições por disco, tabelas `dos`/`msdos` e `gpt`, e espaço sem partição no final de ambos. `FSTYPE` ainda estará vazio: `mkpart ... ext4` **não formata**.

**Se ocorrer sobreposição de partições**, provavelmente um comando já foi executado. Inspecione com `parted ... print`; não repita `mklabel` nem os comandos que já deram certo. Se um limite estiver errado nesta etapa, antes da formatação, remova somente aquela partição com `parted -s "$MBR" rm 2` (exemplo para MBR p2) e recrie-a com os limites da tabela. Não aplique esse exemplo ao outro disco ou número sem conferir.

Pressione **CHECK**. Nas próximas etapas, não execute `mklabel` novamente.
