#!/bin/bash

ERROS=0

verificar_usuario() {
    USUARIO="$1"
    GRUPO="$2"

    # Verifica se o usuário existe
    if ! id "$USUARIO" > /dev/null 2>&1; then
        ERROS=$((ERROS + 1))
        return
    fi

    # Verifica se o diretório pessoal existe
    if [ ! -d "/home/$USUARIO" ]; then
        ERROS=$((ERROS + 1))
    fi

    # Verifica se o usuário pertence ao grupo esperado
    if ! id -nG "$USUARIO" | tr ' ' '\n' | grep -qx "$GRUPO"; then
        ERROS=$((ERROS + 1))
    fi
}

verificar_usuario "ana" "administracao"
verificar_usuario "carlos" "suporte"
verificar_usuario "julia" "desenvolvimento"
verificar_usuario "marcos" "desenvolvimento"

if [ "$ERROS" -eq 0 ]; then
    exit 0
else
    exit 1
fi