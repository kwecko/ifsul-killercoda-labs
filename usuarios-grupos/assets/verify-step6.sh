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

# Verifica a propriedade atual; ela não comprova quem executou os comandos.
DONO=$(stat -c "%U" "$ARQUIVO" 2>/dev/null)

if [ "$DONO" != "julia" ]; then
    exit 1
fi

# Verifica o conteúdo solicitado
if [ "$(cat "$ARQUIVO")" != "Projeto em desenvolvimento" ]; then
    exit 1
fi

# O diretório também deve pertencer à usuária que realizou a tarefa.
if [ "$(stat -c "%U" /empresa/desenvolvimento/projetos 2>/dev/null)" != "julia" ]; then
    exit 1
fi

# Confirma acesso real com os privilégios de julia, e não com os de root.
if ! id julia >/dev/null 2>&1; then
    exit 1
fi
if ! runuser -u julia -- sh -c 'cd /empresa/desenvolvimento && test -w . && test -r projetos/projeto.txt' >/dev/null 2>&1; then
    exit 1
fi
if [ ! -d /empresa/administracao ]; then
    exit 1
fi
# Distingue uma falha da ferramenta de um bloqueio de acesso esperado.
runuser -u julia -- sh -c 'if cd /empresa/administracao 2>/dev/null; then exit 0; else exit 42; fi' >/dev/null 2>&1
if [ "$?" -ne 42 ]; then
    exit 1
fi

exit 0
