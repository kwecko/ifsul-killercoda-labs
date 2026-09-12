#!/bin/bash

source /usr/local/lib/laboratorio/laboratorio.sh || exit 1

ARQUIVO="/root/.laboratorio-aluno"
[ -f "$ARQUIVO" ] || exit 1
REGISTRO_LAB=$(sed -n 's/^LABORATORIO=//p' "$ARQUIVO")
if [ "$REGISTRO_LAB" != "$LAB_ID" ]; then
    echo "Identificação ausente para este laboratório. Execute identificar-aluno."
    exit 1
fi

# Leia os dados como texto, sem executar o conteúdo do arquivo.
MATRICULA=$(sed -n 's/^MATRICULA=//p' "$ARQUIVO")
NOME=$(sed -n 's/^NOME=//p' "$ARQUIVO")
SESSAO=$(sed -n 's/^SESSAO=//p' "$ARQUIVO")
INICIO=$(sed -n 's/^INICIO="\(.*\)"$/\1/p' "$ARQUIVO")

if [ -z "$NOME" ] || [ "$(printf '%s' "$NOME" | wc -c)" -gt 200 ] ||
   [[ "$NOME" = ' '* || "$NOME" = *' ' ]] ||
   printf '%s' "$NOME" | LC_ALL=C grep -q '[[:cntrl:]]' ||
   ! printf '%s' "$NOME" | iconv -f UTF-8 -t UTF-8 >/dev/null 2>&1; then
    echo "Nome ausente ou inválido. Execute identificar-aluno."
    exit 1
fi

[[ "$MATRICULA" =~ ^[A-Za-z0-9][A-Za-z0-9._]{0,31}$ ]] || exit 1
[[ "$SESSAO" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]] || exit 1
[[ "$INICIO" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}\ [0-9]{2}:[0-9]{2}:[0-9]{2}$ ]] || exit 1
date -d "$INICIO" >/dev/null 2>&1 || exit 1

exit 0
