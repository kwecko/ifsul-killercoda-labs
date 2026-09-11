#!/bin/bash

ERROS=0

verificar_diretorio() {
    DIRETORIO="$1"
    GRUPO="$2"

    # Verifica se o diretório existe
    if [ ! -d "$DIRETORIO" ]; then
        ERROS=$((ERROS + 1))
        return
    fi

    # Verifica o proprietário
    DONO=$(stat -c "%U" "$DIRETORIO" 2>/dev/null)

    if [ "$DONO" != "root" ]; then
        ERROS=$((ERROS + 1))
    fi

    # Verifica o grupo proprietário
    GRUPO_ATUAL=$(stat -c "%G" "$DIRETORIO" 2>/dev/null)

    if [ "$GRUPO_ATUAL" != "$GRUPO" ]; then
        ERROS=$((ERROS + 1))
    fi
}

# Diretório principal
if [ ! -d "/empresa" ]; then
    ERROS=$((ERROS + 1))
fi

verificar_diretorio "/empresa/administracao" "administracao"
verificar_diretorio "/empresa/suporte" "suporte"
verificar_diretorio "/empresa/desenvolvimento" "desenvolvimento"

if [ "$ERROS" -eq 0 ]; then
    exit 0
else
    exit 1
fi