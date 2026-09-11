#!/bin/bash

ERROS=0

# Usuário deve existir
if ! id ana > /dev/null 2>&1; then
    echo "A conta ana ainda não existe."
    exit 1
fi

# Verifica se existe senha definida
STATUS=$(LC_ALL=C passwd -S ana 2>/dev/null | awk '{print $2}')

if [ "$STATUS" != "P" ]; then
    echo "Defina uma senha ativa para ana (passwd ana)."
    ERROS=$((ERROS + 1))
fi

# Verifica shell
SHELL_USUARIO=$(getent passwd ana | cut -d: -f7)

if [ "$SHELL_USUARIO" != "/bin/bash" ]; then
    echo "O shell de ana deve ser /bin/bash."
    ERROS=$((ERROS + 1))
fi

# Verifica descrição/GECOS
DESCRICAO=$(getent passwd ana | cut -d: -f5 | cut -d, -f1 | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')

# Aceita escrita sem acentos e as formas Unicode composta/decomposta.
# Acentuação e espaços nas extremidades não são o objetivo desta etapa.
case "$DESCRICAO" in
    "Ana - Administração"|"Ana - Administracao"|"Ana - Administração") ;;
    *)
        printf 'Descrição encontrada: <%s>\n' "$DESCRICAO"
        echo 'Use: usermod -c "Ana - Administracao" ana'
        ERROS=$((ERROS + 1))
        ;;
esac

if [ "$ERROS" -eq 0 ]; then
    exit 0
else
    exit 1
fi
