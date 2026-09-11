#!/bin/bash
# Biblioteca comum. Configuração é lida como dados, nunca executada.
LAB_CONFIG=/usr/local/lib/laboratorio/laboratorio.conf
if [ ! -r "$LAB_CONFIG" ]; then
    echo "Configuração do laboratório ausente. Reinicie em uma nova sessão."
    return 1
fi
LAB_ID=$(sed -n 's/^LABORATORIO=//p' "$LAB_CONFIG")
LAB_LISTA=$(sed -n 's/^VERIFICADORES=//p' "$LAB_CONFIG")
if ! [[ "$LAB_ID" =~ ^[a-z][a-z0-9-]{0,39}$ ]] ||
   ! [[ "$LAB_LISTA" =~ ^verify-step0\.sh(,verify-step[1-9][0-9]*\.sh)+$ ]]; then
    echo "Configuração do laboratório inválida."
    return 1
fi
IFS=',' read -r -a LAB_VERIFICADORES <<< "$LAB_LISTA"
