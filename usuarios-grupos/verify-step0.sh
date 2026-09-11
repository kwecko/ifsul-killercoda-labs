#!/bin/bash

ARQUIVO="/root/.laboratorio-aluno"

if [ ! -f "$ARQUIVO" ]; then
    exit 1
fi

MATRICULA=$(grep '^MATRICULA=' "$ARQUIVO" | cut -d= -f2)
SESSAO=$(grep '^SESSAO=' "$ARQUIVO" | cut -d= -f2)

if ! [[ "$MATRICULA" =~ ^[0-9]+$ ]]; then
    exit 1
fi

if [ -z "$SESSAO" ]; then
    exit 1
fi

exit 0