#!/bin/bash

ERROS=0

verificar_permissao() {
    DIRETORIO="$1"

    if [ ! -d "$DIRETORIO" ]; then
        ERROS=$((ERROS + 1))
        return
    fi

    PERMISSAO=$(stat -c "%a" "$DIRETORIO" 2>/dev/null)

    if [ "$PERMISSAO" != "770" ]; then
        ERROS=$((ERROS + 1))
    fi
}

verificar_permissao "/empresa/administracao"
verificar_permissao "/empresa/suporte"
verificar_permissao "/empresa/desenvolvimento"

if [ "$ERROS" -eq 0 ]; then
    exit 0
else
    exit 1
fi