# 4. Montar e gravar arquivos — 7 minutos

Criar um diretório não monta um volume. Faça as duas operações:

```bash
mkdir -p /mnt/lab/{dados-mbr,temporario,dados-gpt,troca}
mount "${MBR}p1" /mnt/lab/dados-mbr
mount "${MBR}p2" /mnt/lab/temporario
mount "${GPT}p1" /mnt/lab/dados-gpt
mount "${GPT}p2" /mnt/lab/troca
lsblk -o NAME,FSTYPE,LABEL,MOUNTPOINTS "$MBR" "$GPT"
df -hT /mnt/lab/dados-mbr /mnt/lab/temporario /mnt/lab/dados-gpt /mnt/lab/troca
```

Cada partição deve mostrar o destino correspondente. Se o comando disser que já está montada, confira com `findmnt /mnt/lab/dados-mbr` (adapte o destino) e não faça uma montagem sobre outra.

Crie um arquivo com a identificação já informada e faça cópias:

```bash
sed -n '/^MATRICULA=/p; /^NOME=/p' /root/.laboratorio-aluno > /mnt/lab/dados-mbr/equipe.txt
cp /mnt/lab/dados-mbr/equipe.txt /mnt/lab/dados-gpt/
cp /mnt/lab/dados-mbr/equipe.txt /mnt/lab/troca/
cp /mnt/lab/dados-mbr/equipe.txt /mnt/lab/temporario/rascunho.txt
cat /mnt/lab/dados-gpt/equipe.txt
```

O resultado deve mostrar sua matrícula e seu nome, em duas linhas. O rascunho está em uma partição que será excluída mais adiante.

Pressione **CHECK** com os quatro volumes montados.
