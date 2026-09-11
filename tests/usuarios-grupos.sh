#!/bin/bash
# Execute somente em um contêiner Ubuntu descartável, conforme tests/README.md.
set -euo pipefail
[ -f /.dockerenv ] && [ "${LAB_TEST_CONTAINER:-}" = "1" ] || {
    echo "Este teste modifica contas e diretórios. Use o contêiner descartável documentado."
    exit 1
}

BASE=$(cd "$(dirname "$0")/../usuarios-grupos" && pwd)
install -d /usr/local/lib/laboratorio
install -m 755 "$BASE"/assets/verify-step*.sh /usr/local/lib/laboratorio/
install -m 755 "$BASE"/assets/identificar-aluno "$BASE"/assets/gerar-comprovante /usr/local/bin/
CHECKS=/usr/local/lib/laboratorio
TOTAL=0
passa() {
    if ! "$@" >/tmp/lab-test-output 2>&1; then
        cat /tmp/lab-test-output
        echo "FALHOU (deveria passar): $*"
        exit 1
    fi
    TOTAL=$((TOTAL + 1))
}
falha() {
    if "$@" >/tmp/lab-test-output 2>&1; then
        echo "FALHOU (deveria reprovar): $*"
        exit 1
    fi
    TOTAL=$((TOTAL + 1))
}

for etapa in {0..6}; do falha bash "$CHECKS/verify-step$etapa.sh"; done
falha gerar-comprovante
falha bash -c "printf 'abc\n' | identificar-aluno"
[ ! -e /root/.laboratorio-aluno ]
passa bash -c "printf '20261234\n' | identificar-aluno"
[ "$(stat -c %a /root/.laboratorio-aluno)" = 600 ]
passa bash "$CHECKS/verify-step0.sh"
cp /root/.laboratorio-aluno /tmp/identificacao-original
passa bash -c "printf '999\n' | identificar-aluno"
cmp /tmp/identificacao-original /root/.laboratorio-aluno
falha gerar-comprovante

for grupo in administracao suporte desenvolvimento; do groupadd "$grupo"; done
passa bash "$CHECKS/verify-step1.sh"
# Exercita grupos principal/suplementar e um home fora de /home.
useradd -m -g administracao ana
useradd -m -G suporte carlos
useradd -m -s /bin/bash -g desenvolvimento julia
useradd -m -d /srv/marcos -G desenvolvimento marcos
passa bash "$CHECKS/verify-step2.sh"
usermod -G '' carlos
falha bash "$CHECKS/verify-step2.sh"
usermod -aG suporte carlos
mv /srv/marcos /srv/marcos-ausente
falha bash "$CHECKS/verify-step2.sh"
mv /srv/marcos-ausente /srv/marcos

printf 'ana:SenhaApenasParaTeste123!\n' | chpasswd
usermod -s /bin/bash -c 'Ana - Administração' ana
passa bash "$CHECKS/verify-step3.sh"
usermod -c 'Ana - Administração,,,' ana
passa bash "$CHECKS/verify-step3.sh"
passwd -l ana >/dev/null
falha bash "$CHECKS/verify-step3.sh"
passwd -u ana >/dev/null
usermod -s /bin/sh ana
falha bash "$CHECKS/verify-step3.sh"
usermod -s /bin/bash -c 'Nome incorreto' ana
falha bash "$CHECKS/verify-step3.sh"
usermod -c 'Ana - Administração' ana

mkdir -p /empresa/{administracao,suporte,desenvolvimento}
chmod 755 /empresa
for setor in administracao suporte desenvolvimento; do
    chown root:"$setor" "/empresa/$setor"
    chmod 770 "/empresa/$setor"
done
passa bash "$CHECKS/verify-step4.sh"
passa bash "$CHECKS/verify-step5.sh"
chmod 700 /empresa
falha bash "$CHECKS/verify-step4.sh"
chmod 755 /empresa
chown ana /empresa/administracao
falha bash "$CHECKS/verify-step4.sh"
chown root /empresa/administracao
chgrp suporte /empresa/administracao
falha bash "$CHECKS/verify-step4.sh"
chgrp administracao /empresa/administracao
chmod 777 /empresa/administracao
falha bash "$CHECKS/verify-step5.sh"
chmod 2770 /empresa/administracao
falha bash "$CHECKS/verify-step5.sh"
chmod 00770 /empresa/administracao

runuser -u julia -- sh -c 'cd /empresa/desenvolvimento; mkdir projetos; printf "Projeto em desenvolvimento\n" > projetos/projeto.txt'
passa bash "$CHECKS/verify-step6.sh"
passa gerar-comprovante
grep -q 'Matrícula   : 20261234' /tmp/lab-test-output
grep -q 'Status      : ATIVIDADE CONCLUÍDA' /tmp/lab-test-output
# O registro é dado, não um script a ser executado.
printf '\ntouch /tmp/nao-deve-existir\n' >> /root/.laboratorio-aluno
passa gerar-comprovante
[ ! -e /tmp/nao-deve-existir ]
cp /tmp/identificacao-original /root/.laboratorio-aluno
sed -i 's/INICIO=.*/INICIO="data inválida"/' /root/.laboratorio-aluno
falha bash "$CHECKS/verify-step0.sh"
falha gerar-comprovante
cp /tmp/identificacao-original /root/.laboratorio-aluno

usermod -aG administracao julia
falha bash "$CHECKS/verify-step6.sh"
falha gerar-comprovante
usermod -G '' julia
chmod 700 /empresa
falha bash "$CHECKS/verify-step6.sh"
chmod 755 /empresa
chown root /empresa/desenvolvimento/projetos
falha bash "$CHECKS/verify-step6.sh"
chown julia /empresa/desenvolvimento/projetos
chown root /empresa/desenvolvimento/projetos/projeto.txt
falha bash "$CHECKS/verify-step6.sh"
chown julia /empresa/desenvolvimento/projetos/projeto.txt
printf 'Texto extra\n' >> /empresa/desenvolvimento/projetos/projeto.txt
falha bash "$CHECKS/verify-step6.sh"
printf 'Projeto em desenvolvimento\n' > /empresa/desenvolvimento/projetos/projeto.txt
mv "$CHECKS/verify-step1.sh" /tmp/verify-step1.sh
falha gerar-comprovante
mv /tmp/verify-step1.sh "$CHECKS/verify-step1.sh"
falha runuser -u julia -- gerar-comprovante
falha runuser -u julia -- identificar-aluno
passa gerar-comprovante
printf 'OK: %s verificações positivas e negativas no Ubuntu.\n' "$TOTAL"
