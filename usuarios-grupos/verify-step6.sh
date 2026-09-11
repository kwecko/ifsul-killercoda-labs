#!/bin/bash

ARQUIVO="/empresa/desenvolvimento/projetos/projeto.txt"

# Verifica se o diretório projetos existe
if [ ! -d "/empresa/desenvolvimento/projetos" ]; then
    exit 1
fi

# Verifica se projeto.txt existe e é um arquivo regular
if [ ! -f "$ARQUIVO" ]; then
    exit 1
fi

# Verifica se o arquivo foi criado pela usuária julia
DONO=$(stat -c "%U" "$ARQUIVO" 2>/dev/null)

if [ "$DONO" != "julia" ]; then
    exit 1
fi

# Verifica o conteúdo solicitado
if ! grep -Fxq "Projeto em desenvolvimento" "$ARQUIVO"; then
    exit 1
fi

exit 0