# 1. Reconhecer os discos — 4 minutos

Execute:

```bash
lsblk -b -o NAME,SIZE,TYPE "$MBR" "$GPT"
df -hT
findmnt /
```

Confira os resultados:

- `lsblk` lista dispositivos de bloco. Cada disco do exercício deve ter **1073741824 bytes**, equivalentes a 1 GiB.
- Ainda não deve haver partições `p1`/`p2` abaixo deles.
- `df` mostra espaço de sistemas de arquivos montados. Os dois discos vazios ainda não aparecem como volumes montados.
- `findmnt /` mostra a origem do sistema principal; ela não será modificada.

Registre o inventário:

```bash
{ lsblk -b -o NAME,SIZE,TYPE "$MBR" "$GPT"; df -hT; findmnt /; } > /root/relatorio-discos/inventario.txt
cat /root/relatorio-discos/inventario.txt
```

Se `lsblk` reclamar de dispositivo inexistente, execute `source /root/discos.env` e tente novamente.

Pressione **CHECK**.
