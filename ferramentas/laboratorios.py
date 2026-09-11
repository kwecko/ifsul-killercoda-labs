#!/usr/bin/env python3
"""Cria cenários e sincroniza a infraestrutura comum, sem rede ou publicação."""
import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
COMANDOS = ('identificar-aluno', 'iniciar-registro', 'gerar-comprovante', 'enviar-comprovante')
COMPARTILHADOS = COMANDOS + ('verify-step0.sh', 'laboratorio.sh', 'normalizar-registro.pl')
MARCA_INICIO = '// BEGIN CATALOGO GERADO'
MARCA_FIM = '// END CATALOGO GERADO'


def serializar(valor):
    return json.dumps(valor, ensure_ascii=False, indent=2) + '\n'


def identificador(valor):
    if not isinstance(valor, str) or not re.fullmatch(r'[a-z][a-z0-9-]{0,39}', valor):
        raise ValueError('id deve começar por letra minúscula e ter até 40 letras, dígitos ou hífens')
    return valor


def carregar(root):
    drive = json.loads((root / 'comum/drive.json').read_text())
    if drive['url'] and not re.fullmatch(r'https://script\.google\.com/macros/s/[A-Za-z0-9_-]+/exec', drive['url']):
        raise ValueError('URL do Apps Script inválida em comum/drive.json')
    configs = []
    for arquivo in sorted(root.glob('*/laboratorio.json')):
        c = json.loads(arquivo.read_text())
        if identificador(c['id']) != arquivo.parent.name:
            raise ValueError(f'{arquivo}: id precisa corresponder à pasta')
        for campo in ('titulo', 'descricao', 'imagem'):
            if not isinstance(c[campo], str) or not c[campo].strip():
                raise ValueError(f'{arquivo}: {campo} obrigatório')
        if type(c['recebimento_ativo']) is not bool:
            raise ValueError(f'{arquivo}: recebimento_ativo deve ser true ou false')
        if not re.fullmatch(r'[A-Za-z0-9_-]+', c['pasta_drive']):
            raise ValueError(f'{arquivo}: pasta_drive deve ser um ID do Drive')
        if not c['etapas']:
            raise ValueError(f'{arquivo}: configure pelo menos uma etapa além da identificação')
        vistos = set()
        for etapa in c['etapas']:
            if not isinstance(etapa['title'], str) or not etapa['title'].strip():
                raise ValueError('título de etapa vazio')
            if not re.fullmatch(r'[A-Za-z0-9_-]+\.md', etapa['text']):
                raise ValueError('o texto de uma etapa deve ser um arquivo .md na pasta do cenário')
            if not re.fullmatch(r'assets/verify-step[1-9][0-9]*\.sh', etapa['verify']):
                raise ValueError('verificador deve ser assets/verify-stepN.sh, com N >= 1')
            if etapa['verify'] in vistos:
                raise ValueError('verificador repetido')
            vistos.add(etapa['verify'])
            for chave in ('text', 'verify'):
                if not (arquivo.parent / etapa[chave]).is_file():
                    raise ValueError(f'{arquivo}: arquivo ausente: {etapa[chave]}')
        for nome in ('intro.md', 'step0.md', 'finish.md'):
            if not (arquivo.parent / nome).is_file():
                raise ValueError(f'{arquivo}: arquivo ausente: {nome}')
        configs.append((arquivo.parent, c))
    if not configs:
        raise ValueError('nenhum laboratorio.json encontrado')
    return drive, configs


def sincronizar(root=ROOT, check=False):
    drive, configs = carregar(root)
    saidas = {}
    modos = {}
    for pasta, c in configs:
        for nome in COMPARTILHADOS:
            saidas[pasta / 'assets' / nome] = (root / 'comum/assets' / nome).read_bytes()
            modos[pasta / 'assets' / nome] = 0o755
        etapas = [{'title': 'Identificação do aluno', 'text': 'step0.md', 'verify': 'assets/verify-step0.sh'}] + c['etapas']
        verificadores = ','.join(Path(e['verify']).name for e in etapas)
        saidas[pasta / 'assets/laboratorio.conf'] = f"LABORATORIO={c['id']}\nVERIFICADORES={verificadores}\n".encode()
        saidas[pasta / 'assets/drive-upload-url'] = ((drive['url'] + '\n') if c['recebimento_ativo'] and drive['url'] else '').encode()
        index = pasta / 'index.json'
        config = json.loads(index.read_text()) if index.exists() else {}
        config.update(title=c['titulo'], description=c['descricao'])
        config.setdefault('backend', {})['imageid'] = c['imagem']
        details = config.setdefault('details', {})
        details.setdefault('intro', {'text': 'intro.md'})
        details.setdefault('finish', {'text': 'finish.md'})
        details['steps'] = etapas
        assets = details.setdefault('assets', {})
        gerados = [dict(file=n, target='/usr/local/bin/', chmod='+x') for n in COMANDOS]
        gerados += [dict(file='verify-step*.sh', target='/usr/local/lib/laboratorio/', chmod='+x')]
        gerados += [dict(file=n, target='/usr/local/lib/laboratorio/') for n in ('laboratorio.sh', 'laboratorio.conf', 'drive-upload-url', 'normalizar-registro.pl')]
        nomes = {a['file'] for a in gerados}
        extras = [a for a in assets.get('host01', []) if a['file'] not in nomes]
        assets['host01'] = gerados + extras
        saidas[index] = serializar(config).encode()
    catalogo = {c['id']: {'titulo': c['titulo'], 'pasta_drive': c['pasta_drive'], 'recebimento_ativo': c['recebimento_ativo']} for _, c in configs}
    saidas[root / 'professor/laboratorios.json'] = serializar(catalogo).encode()
    code = root / 'professor/google-drive/Code.gs'
    texto = code.read_text()
    bloco = MARCA_INICIO + '\nconst LABORATORIOS = ' + json.dumps(catalogo, ensure_ascii=False, indent=2) + ';\n' + MARCA_FIM
    if MARCA_INICIO not in texto or MARCA_FIM not in texto:
        raise ValueError('marcadores do catálogo não encontrados no Code.gs')
    texto = texto[:texto.index(MARCA_INICIO)] + bloco + texto[texto.index(MARCA_FIM) + len(MARCA_FIM):]
    saidas[code] = texto.encode()
    divergentes = []
    for caminho, conteudo in saidas.items():
        if not caminho.exists() or caminho.read_bytes() != conteudo or (caminho in modos and caminho.stat().st_mode & 0o777 != modos[caminho]):
            divergentes.append(str(caminho.relative_to(root)))
            if not check:
                caminho.parent.mkdir(parents=True, exist_ok=True)
                caminho.write_bytes(conteudo)
                if caminho in modos:
                    caminho.chmod(modos[caminho])
    if check and divergentes:
        raise ValueError('arquivos desatualizados; execute sincronizar:\n' + '\n'.join(divergentes))
    return len(configs), len(divergentes)


def criar(root, lab_id, titulo, descricao, pasta_drive=None):
    identificador(lab_id)
    destino = root / lab_id
    if destino.exists():
        raise ValueError(f'a pasta {lab_id} já existe; nenhum arquivo foi substituído')
    if not titulo.strip():
        raise ValueError('título obrigatório')
    drive = json.loads((root / 'comum/drive.json').read_text())
    pasta_drive = pasta_drive or drive['pasta_padrao']
    if not re.fullmatch(r'[A-Za-z0-9_-]+', pasta_drive):
        raise ValueError('ID de pasta do Drive inválido')
    # Reúne o modelo antes de criar o diretório de destino.
    arquivos = {}
    for nome in ('intro.md', 'step0.md', 'finish.md', 'step1.md', 'verify-step1.sh'):
        arquivos[nome] = (root / 'modelo' / nome).read_text().replace('__LAB_ID__', lab_id).replace('__TITULO__', titulo).replace('__DESCRICAO__', descricao)
    destino.mkdir()
    (destino / 'assets').mkdir()
    for nome, texto in arquivos.items():
        (destino / ('assets/' + nome if nome.endswith('.sh') else nome)).write_text(texto)
    (destino / 'assets/verify-step1.sh').chmod(0o755)
    config = dict(id=lab_id, titulo=titulo, descricao=descricao, imagem='ubuntu', recebimento_ativo=False, pasta_drive=pasta_drive,
                  etapas=[dict(title='Primeira tarefa', text='step1.md', verify='assets/verify-step1.sh')])
    (destino / 'laboratorio.json').write_text(serializar(config))
    sincronizar(root)
    return destino


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    comandos = parser.add_subparsers(dest='comando', required=True)
    novo = comandos.add_parser('criar', help='cria um cenário em rascunho; não sobrescreve pastas')
    novo.add_argument('id')
    novo.add_argument('--titulo', required=True)
    novo.add_argument('--descricao', default='Atividade prática de Introdução à Informática.')
    novo.add_argument('--pasta-drive', help='ID da pasta; usa a pasta padrão se omitido')
    sync = comandos.add_parser('sincronizar', help='atualiza cópias locais, index.json e catálogos')
    sync.add_argument('--check', action='store_true', help='só verifica, sem escrever arquivos')
    args = parser.parse_args()
    try:
        if args.comando == 'criar':
            destino = criar(ROOT, args.id, args.titulo, args.descricao, args.pasta_drive)
            print(f'Criado: {destino}. Implemente a etapa e o verificador; envio ao Drive desativado.')
        else:
            total, alterados = sincronizar(ROOT, args.check)
            print(f'{total} laboratório(s) sincronizado(s); {alterados} arquivo(s) atualizado(s).')
    except (ValueError, KeyError, OSError) as exc:
        print(f'Erro: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
