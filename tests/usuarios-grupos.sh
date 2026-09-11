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
install -m 755 "$BASE"/assets/enviar-comprovante "$BASE"/assets/iniciar-registro /usr/local/bin/
# Nunca carregar uma URL real nos testes.
: > /usr/local/lib/laboratorio/drive-upload-url
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
[ ! -d /root/comprovantes ]
falha bash -c "printf 'abc\n' | identificar-aluno"
[ ! -e /root/.laboratorio-aluno ]
passa bash -c "printf '20261234\n' | identificar-aluno"
[ "$(stat -c %a /root/.laboratorio-aluno)" = 600 ]
passa bash "$CHECKS/verify-step0.sh"
# O teste de regras é não interativo; o teste PTY separado verifica a gravação real.
mkdir -p /root/registros
SESSAO_TESTE=$(sed -n 's/^SESSAO=//p' /root/.laboratorio-aluno)
printf 'registro simulado para teste das regras\n' > "/root/registros/$SESSAO_TESTE.log"
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
usermod -c 'Ana - Administracao' ana
passa bash "$CHECKS/verify-step3.sh"
usermod -c '  Ana - Administração  ,,,' ana
passa bash "$CHECKS/verify-step3.sh"
usermod -c 'Ana - Suporte' ana
falha bash "$CHECKS/verify-step3.sh"
usermod -c 'Ana - Administrador' ana
falha bash "$CHECKS/verify-step3.sh"
usermod -c 'Ana - Administração' ana
passa bash "$CHECKS/verify-step3.sh"
usermod -c 'Ana - Administração' ana

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
SESSAO=$(sed -n 's/^SESSAO=//p' /root/.laboratorio-aluno)
TXT="/root/comprovantes/usuarios-grupos_20261234_${SESSAO}.txt"
[ -f "$TXT" ]
[ "$(stat -c %a "$TXT")" = 644 ]
[ "$(wc -l < "$TXT")" -eq 7 ]
grep -qx 'VERSAO=1' "$TXT"
grep -qx 'LABORATORIO=usuarios-grupos' "$TXT"
grep -qx 'MATRICULA=20261234' "$TXT"
grep -qx "SESSAO=$SESSAO" "$TXT"
grep -Eq '^DATA=[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$' "$TXT"
grep -qx 'RESULTADO=CONCLUIDO' "$TXT"
grep -Eq '^CODIGO=SHA256:[0-9a-f]{64}$' "$TXT"
DIGEST=$(head -n 6 "$TXT" | sha256sum | cut -d ' ' -f1)
[ "$(tail -n 1 "$TXT")" = "CODIGO=SHA256:$DIGEST" ]
# Edição dos dados muda o digest; o checksum não é uma assinatura.
sed 's/MATRICULA=20261234/MATRICULA=99999999/' "$TXT" > /tmp/comprovante-editado.txt
ALTERADO=$(head -n 6 /tmp/comprovante-editado.txt | sha256sum | cut -d ' ' -f1)
[ "$ALTERADO" != "$DIGEST" ]
cp "$TXT" /tmp/comprovante-anterior.txt
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
cp "$TXT" /tmp/comprovante-anterior.txt
falha gerar-comprovante
cmp "$TXT" /tmp/comprovante-anterior.txt
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
# Reemissão válida conserva o nome e substitui o conteúdo anterior.
printf 'conteudo anterior\n' > "$TXT"
passa gerar-comprovante
grep -qx 'RESULTADO=CONCLUIDO' "$TXT"
[ "$(find /root/comprovantes -name '*.txt' | wc -l)" -eq 1 ]
[ -z "$(find /root/comprovantes -name '.comprovante.*' -print)" ]
# Erro na publicação não pode ser anunciado como sucesso.
cp "$TXT" /tmp/comprovante-anterior.txt
rm "$TXT"
mkdir "$TXT"
falha gerar-comprovante
[ -d "$TXT" ]
[ -z "$(find /root/comprovantes -name '.comprovante.*' -print)" ]
rmdir "$TXT"
# Matrículas são texto e conservam os zeros iniciais no nome e nos dados.
sed -i 's/^MATRICULA=.*/MATRICULA=0020261234/' /root/.laboratorio-aluno
passa gerar-comprovante
NOVO_TXT="/root/comprovantes/usuarios-grupos_0020261234_${SESSAO}.txt"
grep -qx 'MATRICULA=0020261234' "$NOVO_TXT"
# Nova identificação independente gera outro UUID completo.
rm /root/.laboratorio-aluno
passa bash -c "printf '20261234\n' | identificar-aluno"
NOVA_SESSAO=$(sed -n 's/^SESSAO=//p' /root/.laboratorio-aluno)
[ "$NOVA_SESSAO" != "$SESSAO" ]
passa bash "$CHECKS/verify-step0.sh"
printf 'registro simulado da nova sessão\n' > "/root/registros/$NOVA_SESSAO.log"
# Exercita o cliente de upload com rede simulada, sem dados enviados ao Google.
passa gerar-comprovante
TXT="/root/comprovantes/usuarios-grupos_20261234_${NOVA_SESSAO}.txt"
falha enviar-comprovante
mkdir -p /tmp/lab-mock-bin
cat > /tmp/lab-mock-bin/curl <<'MOCK'
#!/bin/bash
set -eu
printf 'chamado\n' >> /tmp/lab-curl-calls
case "${LAB_CURL_MODE:-sucesso}" in
    rede) exit 7 ;;
    html) printf '<html>Login Google</html>'; exit 0 ;;
    limite) printf 'ERRO=LIMITE_DIARIO'; exit 0 ;;
    errado) printf 'OK\nARQUIVO=outro.txt\nCODIGO=SHA256:errado'; exit 0 ;;
esac
TXT=''
for ARG in "$@"; do
    case "$ARG" in @*) TXT=${ARG#@} ;; esac
done
[ -f "$TXT" ]
sed -n 's/.*"comprovante":"\([^"]*\)".*/\1/p' "$TXT" | base64 -d > /tmp/mock-comprovante.txt
sed -n 's/.*"registro":"\([^"]*\)".*/\1/p' "$TXT" | base64 -d > /tmp/mock-registro.log
M=$(sed -n 's/^MATRICULA=//p' /tmp/mock-comprovante.txt)
S=$(sed -n 's/^SESSAO=//p' /tmp/mock-comprovante.txt)
C=$(sed -n 's/^CODIGO=//p' /tmp/mock-comprovante.txt)
H=$(sha256sum /tmp/mock-registro.log | cut -d ' ' -f1)
printf 'OK\nARQUIVO=usuarios-grupos_%s_%s.txt\nCODIGO=%s\nREGISTRO=usuarios-grupos_%s_%s_%s_historico.log\nREGISTRO_SHA256=%s' "$M" "$S" "$C" "$M" "$S" "${C#SHA256:}" "$H"
MOCK
chmod +x /tmp/lab-mock-bin/curl
export PATH="/tmp/lab-mock-bin:$PATH"
printf 'https://exemplo.invalid/exec\n' > "$CHECKS/drive-upload-url"
falha enviar-comprovante
[ ! -e /tmp/lab-curl-calls ]
printf 'https://script.google.com/macros/s/TESTE_SEM_REDE/exec\n' > "$CHECKS/drive-upload-url"
passa enviar-comprovante
grep -q 'Recebimento confirmado' /tmp/lab-test-output
passa gerar-comprovante
grep -q 'Recebimento confirmado' /tmp/lab-test-output
cp "$TXT" /tmp/lab-before-upload.txt
for LAB_CURL_MODE in rede html limite errado; do
    export LAB_CURL_MODE
    falha enviar-comprovante
    cmp "$TXT" /tmp/lab-before-upload.txt
done
export LAB_CURL_MODE=rede
passa gerar-comprovante
grep -q 'envio ao Drive não foi confirmado' /tmp/lab-test-output
[ -f "$TXT" ]
export LAB_CURL_MODE=sucesso
CHAMADAS=$(wc -l < /tmp/lab-curl-calls)
chmod 777 /empresa/administracao
falha enviar-comprovante
[ "$(wc -l < /tmp/lab-curl-calls)" -eq "$CHAMADAS" ]
chmod 770 /empresa/administracao
passa enviar-comprovante
# O histórico enviado é um snapshot: comandos posteriores não mudam um reenvio.
printf 'comando posterior\n' >> "/root/registros/$NOVA_SESSAO.log"
passa enviar-comprovante
if grep -q 'comando posterior' /tmp/mock-registro.log; then exit 1; fi
LOG="/root/registros/$NOVA_SESSAO.log"
mv "$LOG" "$LOG.ausente"
falha gerar-comprovante
mv "$LOG.ausente" "$LOG"
truncate -s 1048577 "$LOG"
falha gerar-comprovante
printf 'OK: %s verificações positivas e negativas no Ubuntu.\n' "$TOTAL"
