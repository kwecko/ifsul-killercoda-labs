#!/bin/bash

ARQUIVO="/root/.laboratorio-aluno"

if [ ! -f "$ARQUIVO" ]; then
    echo "Aluno não identificado."
    exit 1
fi

source "$ARQUIVO"

DATA_FINAL=$(date "+%Y-%m-%d %H:%M:%S")

echo
echo "================================================"
echo "       COMPROVANTE DE CONCLUSÃO DO LABORATÓRIO"
echo "================================================"
echo
echo "Laboratório : Gerenciamento de Usuários e Grupos"
echo "Matrícula   : $MATRICULA"
echo "Sessão      : $SESSAO"
echo "Início      : $INICIO"
echo "Conclusão   : $DATA_FINAL"
echo
echo "Status      : ATIVIDADE CONCLUÍDA"
echo
echo "================================================"