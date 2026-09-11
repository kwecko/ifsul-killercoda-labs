#!/bin/bash
# Somente em container descartável; os únicos discos alterados são imagens próprias.
set -euo pipefail
[ "${LAB_TEST_CONTAINER:-}" = 1 ] && [ -e /.dockerenv ] || { echo 'Execute no container de testes.'; exit 1; }
BASE=/lab/particoes-linux/assets
CHECKS=/usr/local/lib/laboratorio
mkdir -p "$CHECKS"
install -m 755 "$BASE"/{identificar-aluno,iniciar-registro,gerar-comprovante,enviar-comprovante,preparar-discos,atualizar-particoes} /usr/local/bin/
install -m 644 "$BASE"/{laboratorio.sh,laboratorio.conf,normalizar-registro.pl,particoes.py} "$CHECKS/"
install -m 755 "$BASE"/verify-step*.sh "$CHECKS/"
: > "$CHECKS/drive-upload-url"
cleanup() {
    cd /root
    for folder in dados-mbr temporario dados-gpt troca; do umount "/mnt/lab/$folder" 2>/dev/null || true; done
    for name in mbr gpt; do
        while read -r dev; do [ -z "$dev" ] || losetup -d "$dev"; done < <(losetup -j "/var/lib/lab-particoes/$name.img" -n -O NAME)
    done
}
trap cleanup EXIT
TOTAL=0
passa() { if ! "$@" > /tmp/resultado 2>&1; then cat /tmp/resultado; echo "FALHOU: $*"; exit 1; fi; TOTAL=$((TOTAL+1)); }
falha() { if "$@" > /tmp/resultado 2>&1; then cat /tmp/resultado; echo "PASSOU INDEVIDAMENTE: $*"; exit 1; fi; TOTAL=$((TOTAL+1)); }
verify() { bash "$CHECKS/verify-step$1.sh"; }
passa preparar-discos
source /root/discos.env
ANTES=$MBR
passa preparar-discos
source /root/discos.env
[ "$ANTES" = "$MBR" ]
printf '20261CM.INF_I0027\nJosé da Silva\n' | identificar-aluno
SESSAO=$(sed -n 's/^SESSAO=//p' /root/.laboratorio-aluno)
mkdir -p /root/registros
printf 'Registro simulado da atividade de 60 minutos\n' > "/root/registros/$SESSAO.log"
falha gerar-comprovante
falha verify 2
falha verify 1
{ lsblk -b -o NAME,SIZE,TYPE "$MBR" "$GPT"; df -hT; findmnt /; } > /root/relatorio-discos/inventario.txt
passa verify 1
parted -s "$MBR" mklabel msdos
parted -s "$GPT" mklabel gpt
falha verify 2
parted -s "$MBR" mkpart primary ext4 1MiB 513MiB
parted -s "$MBR" mkpart primary ext2 513MiB 769MiB
parted -s "$GPT" mkpart dados ext4 1MiB 513MiB
parted -s "$GPT" mkpart troca fat32 513MiB 897MiB
atualizar-particoes
passa verify 2
falha verify 3
mkfs.ext4 -q -L DADOS_MBR "${MBR}p1"
mkfs.ext2 -q -L TEMP_MBR "${MBR}p2"
mkfs.ext4 -q -L DADOS_GPT "${GPT}p1"
mkfs.vfat -F 32 -n ERRADO "${GPT}p2"
falha verify 3
fatlabel "${GPT}p2" TROCA
passa verify 3
falha verify 4
mkdir -p /mnt/lab/{dados-mbr,temporario,dados-gpt,troca}
mount "${MBR}p1" /mnt/lab/dados-mbr
mount "${MBR}p2" /mnt/lab/temporario
mount "${GPT}p1" /mnt/lab/dados-gpt
mount "${GPT}p2" /mnt/lab/troca
falha verify 4
sed -n '/^MATRICULA=/p; /^NOME=/p' /root/.laboratorio-aluno > /mnt/lab/dados-mbr/equipe.txt
cp /mnt/lab/dados-mbr/equipe.txt /mnt/lab/dados-gpt/
cp /mnt/lab/dados-mbr/equipe.txt /mnt/lab/troca/
cp /mnt/lab/dados-mbr/equipe.txt /mnt/lab/temporario/rascunho.txt
passa verify 4
falha verify 5
dd if=/dev/zero of=/mnt/lab/dados-gpt/carga.bin bs=1M count=16 status=none
{ df -hT /mnt/lab/dados-gpt; du -h /mnt/lab/dados-gpt/carga.bin; lsblk -o NAME,SIZE,FSTYPE "$GPT"; } > /root/relatorio-discos/ocupacao.txt
falha verify 5
mount -o remount,ro /mnt/lab/troca
falha touch /mnt/lab/troca/teste.txt
passa verify 5
mount -o remount,rw /mnt/lab/troca
passa verify 5
cd /mnt/lab/dados-mbr
falha umount /mnt/lab/dados-mbr
cd /root
falha verify 6
for folder in dados-mbr temporario dados-gpt troca; do umount "/mnt/lab/$folder"; done
passa verify 6
falha verify 7
mount -U "$(blkid -s UUID -o value "${MBR}p1")" /mnt/lab/dados-mbr
mount -U "$(blkid -s UUID -o value "${MBR}p2")" /mnt/lab/temporario
mount -U "$(blkid -s UUID -o value "${GPT}p1")" /mnt/lab/dados-gpt
mount -U "$(blkid -s UUID -o value "${GPT}p2")" /mnt/lab/troca
falha verify 7
tar -cf /mnt/lab/dados-gpt/backup.tar -C /mnt/lab/temporario rascunho.txt
passa verify 7
falha verify 8
umount /mnt/lab/temporario
parted -s "$MBR" rm 2
atualizar-particoes
falha verify 8
mkdir -p /mnt/lab/dados-gpt/recuperados
tar -xf /mnt/lab/dados-gpt/backup.tar -C /mnt/lab/dados-gpt/recuperados
cmp /mnt/lab/dados-mbr/equipe.txt /mnt/lab/dados-gpt/recuperados/rascunho.txt
falha verify 8
printf 'lsblk descreve os dispositivos e df informa ocupação dos volumes montados. O modo ro impede escrita, mesmo como root. Desmontar preserva os dados; excluir remove a entrada da tabela de partições.\n' > /root/relatorio-discos/conclusao.txt
passa verify 8
# Etapas transitórias não precisam ser recriadas depois da exclusão.
for n in $(seq 1 7); do passa verify "$n"; done
passa gerar-comprovante
TXT="/root/comprovantes/particoes-linux_20261CM.INF_I0027_${SESSAO}.txt"
[ -s "$TXT" ]
grep -q '^LABORATORIO=particoes-linux$' "$TXT"
# Mesmo após concluir, não emite se o estado final foi quebrado.
umount /mnt/lab/troca
falha gerar-comprovante
mount "${GPT}p2" /mnt/lab/troca
printf 'adulterado\n' > /mnt/lab/dados-gpt/recuperados/rascunho.txt
falha gerar-comprovante
cp /mnt/lab/dados-mbr/equipe.txt /mnt/lab/dados-gpt/recuperados/rascunho.txt
passa gerar-comprovante
passa preparar-discos
passa verify 8
sed -i "s/$SESSAO/00000000-0000-4000-8000-000000000001/" /var/lib/lab-particoes/progresso.json
falha verify 8
printf 'OK: %s verificações do laboratório guiado de 60 minutos.\n' "$TOTAL"
