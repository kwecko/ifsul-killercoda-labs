#!/bin/bash

ARQUIVO="/root/.laboratorio-aluno"
[ -f "$ARQUIVO" ] || exit 1

# Leia os dados como texto, sem executar o conteúdo do arquivo.
MATRICULA=$(sed -n 's/^MATRICULA=//p' "$ARQUIVO")
SESSAO=$(sed -n 's/^SESSAO=//p' "$ARQUIVO")
INICIO=$(sed -n 's/^INICIO="\(.*\)"$/\1/p' "$ARQUIVO")

[[ "$MATRICULA" =~ ^[0-9]+$ ]] || exit 1
[[ "$SESSAO" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]] || exit 1
[[ "$INICIO" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}\ [0-9]{2}:[0-9]{2}:[0-9]{2}$ ]] || exit 1
date -d "$INICIO" >/dev/null 2>&1 || exit 1

exit 0
