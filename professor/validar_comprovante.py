#!/usr/bin/env python3
"""Valida localmente os formatos v1/v2 e checksum; não autentica a origem."""

import argparse
from datetime import datetime
import hashlib
import hmac
import json
from pathlib import Path
import re
import sys

CAMPOS = ('VERSAO', 'LABORATORIO', 'MATRICULA', 'SESSAO', 'DATA', 'RESULTADO', 'CODIGO')


class ComprovanteInvalido(ValueError):
    """O comprovante não atende ao contrato v1/v2."""


def validar(conteudo: bytes, laboratorios=None) -> dict:
    """Confere os bytes originais, sem normalização ou execução de conteúdo."""
    try:
        texto = conteudo.decode('utf-8')
    except UnicodeDecodeError as exc:
        raise ComprovanteInvalido('arquivo não está em UTF-8') from exc
    if texto.startswith('\ufeff'):
        raise ComprovanteInvalido('BOM não é permitido')
    if '\r' in texto or not texto.endswith('\n'):
        raise ComprovanteInvalido('use linhas LF e uma quebra de linha final')
    linhas = texto[:-1].split('\n')
    if linhas[0] not in ('VERSAO=1', 'VERSAO=2'):
        raise ComprovanteInvalido('versão desconhecida')
    campos = CAMPOS if linhas[0] == 'VERSAO=1' else CAMPOS[:3] + ('NOME',) + CAMPOS[3:]
    if len(linhas) != len(campos):
        raise ComprovanteInvalido('número de linhas incorreto para a versão')
    dados = {}
    for campo, linha in zip(campos, linhas):
        chave, separador, valor = linha.partition('=')
        if not separador or chave != campo:
            raise ComprovanteInvalido(f'campo ausente, duplicado ou fora de ordem: esperado {campo}')
        dados[campo] = valor
    if laboratorios is None:
        laboratorios = json.loads(Path(__file__).with_name('laboratorios.json').read_text())
    if not re.fullmatch(r'[a-z][a-z0-9-]{0,39}', dados['LABORATORIO']) or dados['LABORATORIO'] not in laboratorios:
        raise ComprovanteInvalido('laboratório não cadastrado')
    for campo, valor in (('RESULTADO', 'CONCLUIDO'),):
        if dados[campo] != valor:
            raise ComprovanteInvalido(f'{campo} deve ser {valor}')
    if 'NOME' in dados:
        nome = dados['NOME']
        if not nome or len(nome.encode('utf-8')) > 200 or nome != nome.strip(' ') or any(ord(c) < 32 or ord(c) == 127 for c in nome):
            raise ComprovanteInvalido('nome inválido')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._]{0,31}', dados['MATRICULA']):
        raise ComprovanteInvalido('matrícula deve conter de 1 a 32 caracteres (letras ASCII, números, ponto ou sublinhado), começando com letra ou número, sem espaços')
    if not re.fullmatch(r'[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}', dados['SESSAO']):
        raise ComprovanteInvalido('sessão deve ser um UUID completo')
    if not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z', dados['DATA']):
        raise ComprovanteInvalido('DATA deve usar AAAA-MM-DDTHH:MM:SSZ, em UTC')
    try:
        datetime.strptime(dados['DATA'], '%Y-%m-%dT%H:%M:%SZ')
    except ValueError as exc:
        raise ComprovanteInvalido('data ou horário inexistente') from exc
    if not re.fullmatch(r'SHA256:[0-9a-f]{64}', dados['CODIGO']):
        raise ComprovanteInvalido('CODIGO deve ser SHA256: seguido de 64 hexadecimais minúsculos')
    payload = b'\n'.join(conteudo.split(b'\n')[:len(campos)-1]) + b'\n'
    calculado = hashlib.sha256(payload).hexdigest()
    if not hmac.compare_digest(dados['CODIGO'][7:], calculado):
        raise ComprovanteInvalido('SHA-256 divergente: conteúdo alterado ou código incorreto')
    return dados


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('arquivos', nargs='+', type=Path, help='um ou mais arquivos TXT baixados do Moodle')
    parser.add_argument('--laboratorio', help='identificador do laboratório esperado')
    parser.add_argument('--matricula', help='matrícula esperada (comparação textual, preservando maiúsculas, minúsculas e zeros à esquerda)')
    parser.add_argument('--conferir-nome', action='store_true', help='reprovar também se o nome do arquivo divergir dos campos')
    args = parser.parse_args(argv)
    if args.matricula is not None and not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._]{0,31}', args.matricula):
        parser.error('--matricula deve conter de 1 a 32 caracteres (letras ASCII, números, ponto ou sublinhado), começando com letra ou número, sem espaços')
    print('Validação de formato e checksum; não comprova autenticidade ou autoria.')
    erros = 0
    for arquivo in args.arquivos:
        try:
            dados = validar(arquivo.read_bytes())
            if args.laboratorio is not None and dados['LABORATORIO'] != args.laboratorio:
                raise ComprovanteInvalido('laboratório diferente do esperado')
            if args.matricula is not None and dados['MATRICULA'] != args.matricula:
                raise ComprovanteInvalido('matrícula diferente da esperada')
            esperado = f"{dados['LABORATORIO']}_{dados['MATRICULA']}_{dados['SESSAO']}.txt"
            if args.conferir_nome and arquivo.name != esperado:
                raise ComprovanteInvalido(f'nome esperado: {esperado}')
        except (OSError, json.JSONDecodeError, ComprovanteInvalido) as exc:
            print(f'INVÁLIDO {str(arquivo)!r}: {exc}')
            erros += 1
            continue
        print(f"CONSISTENTE {str(arquivo)!r}: laboratório={dados['LABORATORIO']} matrícula={dados['MATRICULA']} nome={dados.get('NOME', '(não informado na v1)')!r} sessão={dados['SESSAO']} data={dados['DATA']}")
        if arquivo.name != esperado:
            print(f'  Aviso: nome diferente do esperado ({esperado}); conteúdo e hash conferem.')
    print(f'{len(args.arquivos) - erros} consistente(s); {erros} inválido(s).')
    return 1 if erros else 0


if __name__ == '__main__':
    sys.exit(main())
