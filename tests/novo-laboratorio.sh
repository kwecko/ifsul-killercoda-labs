#!/bin/bash
# Usado somente pelo teste Python em um contêiner descartável.
set -euo pipefail
[ -f /.dockerenv ] && [ "${LAB_TEST_CONTAINER:-}" = 1 ] || exit 1
install -d /usr/local/lib/laboratorio
install -m 644 /cenario/assets/normalizar-registro.pl /usr/local/lib/laboratorio/
install -m 755 /cenario/assets/verify-step*.sh /usr/local/lib/laboratorio/
install -m 644 /cenario/assets/laboratorio.sh /cenario/assets/laboratorio.conf /usr/local/lib/laboratorio/
install -m 755 /cenario/assets/identificar-aluno /cenario/assets/gerar-comprovante /cenario/assets/enviar-comprovante /cenario/assets/iniciar-registro /usr/local/bin/
: > /usr/local/lib/laboratorio/drive-upload-url
printf '001234\nAluno de Teste\n' | identificar-aluno >/dev/null
SESSAO=$(sed -n 's/^SESSAO=//p' /root/.laboratorio-aluno)
mkdir /root/registros
printf 'transcrição simulada do teste\n' > "/root/registros/$SESSAO.log"
# Não aprova um cenário vazio nem apenas a primeira tarefa.
if gerar-comprovante >/dev/null; then exit 1; fi
mkdir /exemplo-atividade
if gerar-comprovante >/dev/null; then exit 1; fi
printf 'Concluído\n' > /exemplo-atividade/resultado.txt
gerar-comprovante >/dev/null
TXT="/root/comprovantes/arquivos-diretorios_001234_${SESSAO}.txt"
grep -qx 'LABORATORIO=arquivos-diretorios' "$TXT"
grep -qx 'NOME=Aluno de Teste' "$TXT"
HASH=$(head -n 7 "$TXT" | sha256sum | cut -d ' ' -f1)
grep -qx "CODIGO=SHA256:$HASH" "$TXT"
[ -f "/root/comprovantes/arquivos-diretorios_001234_${SESSAO}_${HASH}_historico.log" ]
# Perder um verificador declarado bloqueia nova emissão.
mv /usr/local/lib/laboratorio/verify-step2.sh /tmp/verify-step2.sh
if gerar-comprovante >/dev/null; then exit 1; fi
mv /tmp/verify-step2.sh /usr/local/lib/laboratorio/verify-step2.sh
# Não reutiliza registro de outro laboratório na mesma VM.
sed -i 's/LABORATORIO=arquivos-diretorios/LABORATORIO=outro/' /root/.laboratorio-aluno
if gerar-comprovante >/dev/null; then exit 1; fi
if identificar-aluno </dev/null >/dev/null; then exit 1; fi
printf 'OK: segundo laboratório com duas tarefas, identificação própria, hash e histórico; reprovação de etapas pendentes e registro alheio.\n'
