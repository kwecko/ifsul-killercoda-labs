#!/bin/bash

ARQUIVO="/root/.laboratorio-aluno"

if [ -f "$ARQUIVO" ]; then
    echo
    echo "Aluno já identificado:"
    cat "$ARQUIVO"
    echo
    exit 0
fi

echo
echo "========================================"
echo " IDENTIFICAÇÃO DO ALUNO"
echo "========================================"
echo

read -p "Informe sua matrícula: " MATRICULA

if ! [[ "$MATRICULA" =~ ^[0-9]+$ ]]; then
    echo "Matrícula inválida."
    exit 1
fi

SESSAO=$(cat /proc/sys/kernel/random/uuid)
DATA=$(date "+%Y-%m-%d %H:%M:%S")

cat > "$ARQUIVO" <<EOF
MATRICULA=$MATRICULA
SESSAO=$SESSAO
INICIO=$DATA
EOF

chmod 600 "$ARQUIVO"

echo
echo "Identificação registrada."
echo "Matrícula: $MATRICULA"
echo "Sessão: $SESSAO"
echo