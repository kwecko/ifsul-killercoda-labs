#!/bin/bash

ERROS=0

for grupo in administracao suporte desenvolvimento
do
    if getent group "$grupo" > /dev/null 2>&1; then
        :
    else
        ERROS=$((ERROS + 1))
    fi
done

if [ "$ERROS" -eq 0 ]; then
    exit 0
else
    exit 1
fi