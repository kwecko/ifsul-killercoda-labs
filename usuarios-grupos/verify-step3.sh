#!/bin/bash

ERROS=0

# Usuário deve existir
if ! id ana > /dev/null 2>&1; then
    exit 1
fi

# Verifica se existe senha definida
STATUS=$(passwd -S ana 2>/dev/null | awk '{print $2}')

if [ "$STATUS" != "P" ]; then
    ERROS=$((ERROS + 1))
fi

# Verifica shell
SHELL_USUARIO=$(getent passwd ana | cut -d: -f7)

if [ "$SHELL_USUARIO" != "/bin/bash" ]; then
    ERROS=$((ERROS + 1))
fi

# Verifica descrição/GECOS
DESCRICAO=$(getent passwd ana | cut -d: -f5)

if [ "$DESCRICAO" != "Ana - Administração" ]; then
    ERROS=$((ERROS + 1))
fi

if [ "$ERROS" -eq 0 ]; then
    exit 0
else
    exit 1
fi