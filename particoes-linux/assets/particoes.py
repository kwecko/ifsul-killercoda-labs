#!/usr/bin/env python3
"""Verifica o laboratório de 60 minutos; checkpoints não são prova contra root."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tarfile

BASE = Path('/var/lib/lab-particoes')
REPORT = Path('/root/relatorio-discos')
MOUNT = Path('/mnt/lab')
SPEC = {
    'mbr': [(1, 513, 'ext4', 'DADOS_MBR', 'dados-mbr'),
            (513, 769, 'ext2', 'TEMP_MBR', 'temporario')],
    'gpt': [(1, 513, 'ext4', 'DADOS_GPT', 'dados-gpt'),
            (513, 897, 'vfat', 'TROCA', 'troca')],
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def run(*args):
    p = subprocess.run(args, capture_output=True, text=True)
    need(p.returncode == 0, f'Falha em {args[0]}: {p.stderr.strip()}')
    return p.stdout.strip()


def devices():
    need((BASE / 'discos.json').is_file(), 'Execute preparar-discos e source /root/discos.env.')
    ds = json.loads((BASE / 'discos.json').read_text())
    need(set(ds) == set(SPEC), 'Mapeamento dos dois discos inválido.')
    for name, dev in ds.items():
        need(re.fullmatch(r'/dev/loop[0-9]+', dev), 'Use somente os discos virtuais do exercício.')
        image = BASE / f'{name}.img'
        need(image.is_file() and not image.is_symlink() and image.stat().st_size == 1073741824,
             'Imagem do laboratório inválida. Inicie uma sessão nova.')
        need(run('losetup', '-n', '--raw', '-O', 'BACK-FILE', dev) == str(image),
             'Disco associado a outra imagem. Não continue com esse dispositivo.')
        need(run('blockdev', '--getsize64', dev) == '1073741824', 'O disco precisa ter 1 GiB.')
    need(ds['mbr'] != ds['gpt'], 'São necessários dois discos distintos.')
    return ds


def volumes(ds, final=False):
    for name, dev in ds.items():
        specs = SPEC[name][:1] if final and name == 'mbr' else SPEC[name]
        for number, spec in enumerate(specs, 1):
            yield name, f'{dev}p{number}', spec


def layout(ds, final=False):
    for name, dev in ds.items():
        t = json.loads(run('sfdisk', '--json', dev))['partitiontable']
        need(t['label'] == ('dos' if name == 'mbr' else 'gpt'), f'Tabela de {name.upper()} incorreta; confira a etapa 2.')
        specs = SPEC[name][:1] if final and name == 'mbr' else SPEC[name]
        parts = t.get('partitions', [])
        need(len(parts) == len(specs), f'{name.upper()}: esperadas {len(specs)} partições.')
        for number, (p, spec) in enumerate(zip(parts, specs), 1):
            start, end = spec[:2]
            sector = t.get('sectorsize', 512)
            need(p['node'] == f'{dev}p{number}' and p['start'] * sector == start * 1048576
                 and p['size'] * sector == (end - start) * 1048576,
                 f'{name.upper()} p{number}: confira início e fim em MiB na etapa 2.')


def filesystems(ds, final=False):
    layout(ds, final)
    for _, dev, (_, _, fs, label, _) in volumes(ds, final):
        attrs = dict(line.split('=', 1) for line in run('blkid', '-p', '-o', 'export', dev).splitlines() if '=' in line)
        need(attrs.get('TYPE') == fs and attrs.get('LABEL') == label,
             f'{dev}: esperado {fs} com LABEL={label}. Confira a etapa 3; nunca formate um volume montado.')


def mounts():
    return json.loads(run('findmnt', '--json', '--list', '-o', 'TARGET,FSTYPE,OPTIONS,MAJ:MIN')).get('filesystems', [])


def devno(dev):
    st = os.stat(dev).st_rdev
    return f'{os.major(st)}:{os.minor(st)}'


def mounted(ds, final=False, readonly=False):
    current = mounts()
    for _, dev, (_, _, fs, _, folder) in volumes(ds, final):
        target = str(MOUNT / folder)
        matches = [m for m in current if m['target'] == target]
        need(len(matches) == 1, f'Monte {dev} em {target}; consulte a etapa 4 ou 7.')
        m = matches[0]
        need(m['maj:min'] == devno(dev) and m['fstype'] == fs, f'Origem ou tipo incorreto em {target}.')
        mode = 'ro' if readonly and folder == 'troca' else 'rw'
        need(mode in m['options'].split(','), f'Execute mount -o remount,{mode} {target}.')


def unmounted(ds, temporary_only=False):
    wanted = {devno(dev) for _, dev, spec in volumes(ds)
              if Path(dev).exists() and (not temporary_only or spec[4] == 'temporario')}
    for m in mounts():
        target = m['target']
        under = target.startswith(str(MOUNT) + '/')
        if temporary_only:
            under = target == str(MOUNT / 'temporario') or target.startswith(str(MOUNT / 'temporario') + '/')
        need(m['maj:min'] not in wanted and not under, f'Use cd /root e desmonte {target}.')


def identity():
    run('bash', '/usr/local/lib/laboratorio/verify-step0.sh')
    return dict(l.split('=', 1) for l in Path('/root/.laboratorio-aluno').read_text().splitlines() if '=' in l)


def contents(who):
    return f"MATRICULA={who['MATRICULA']}\nNOME={who['NOME']}\n".encode()


def data_files(who, temporary=True):
    for folder in ('dados-mbr', 'dados-gpt', 'troca'):
        need((MOUNT / folder / 'equipe.txt').read_bytes() == contents(who), f'Confira equipe.txt em {folder}; refaça a cópia da etapa 4.')
    if temporary:
        need((MOUNT / 'temporario/rascunho.txt').read_bytes() == contents(who), 'Confira rascunho.txt na partição temporária.')


def report(name, minimum=40):
    p = REPORT / name
    need(p.is_file() and len(p.read_text().strip()) >= minimum, f'Preencha {p}, conforme o roteiro.')


def backup(who):
    p = MOUNT / 'dados-gpt/backup.tar'
    need(p.is_file(), 'Crie backup.tar seguindo a etapa 7.')
    with tarfile.open(p, 'r:') as tf:
        member = tf.getmember('rascunho.txt')
        need(member.isfile() and member.size == len(contents(who)), 'Arquivo inesperado no backup.')
        need(tf.extractfile(member).read() == contents(who), 'O backup precisa conter seu rascunho original.')


def check(step, ds, who):
    if step == 1:
        report('inventario.txt')
    elif step == 2:
        layout(ds)
    elif step == 3:
        filesystems(ds)
    elif step == 4:
        filesystems(ds); mounted(ds); data_files(who)
    elif step == 5:
        filesystems(ds); mounted(ds, readonly=True); data_files(who)
        need((MOUNT / 'dados-gpt/carga.bin').stat().st_size == 16 * 1048576, 'Crie carga.bin de 16 MiB conforme a etapa 5.')
        report('ocupacao.txt')
    elif step == 6:
        filesystems(ds); unmounted(ds)
    elif step == 7:
        filesystems(ds); mounted(ds); data_files(who); backup(who)
    elif step == 8:
        filesystems(ds, final=True); mounted(ds, final=True); unmounted(ds, temporary_only=True)
        data_files(who, temporary=False); backup(who)
        need((MOUNT / 'dados-gpt/recuperados/rascunho.txt').read_bytes() == contents(who), 'Restaure o rascunho com o comando tar da etapa 8.')
        need((MOUNT / 'dados-gpt/carga.bin').stat().st_size == 16 * 1048576, 'Preserve carga.bin de 16 MiB.')
        report('inventario.txt'); report('ocupacao.txt'); report('conclusao.txt', 120)
    else:
        raise ValueError('Etapa desconhecida.')


def main():
    ds = devices()
    if sys.argv[1:] == ['dispositivos']:
        print(json.dumps(ds)); return
    need(len(sys.argv) == 2 and sys.argv[1].isdigit(), 'Informe a etapa de 1 a 8.')
    step = int(sys.argv[1]); need(1 <= step <= 8, 'Etapa inválida.')
    who = identity()
    path = BASE / 'progresso.json'
    state = json.loads(path.read_text()) if path.exists() else {'sessao': who['SESSAO'], 'etapas': []}
    need(state['sessao'] == who['SESSAO'], 'Progresso de outra sessão; inicie um ambiente novo.')
    need(all(n in state['etapas'] for n in range(1, step)), 'Volte às etapas anteriores e pressione CHECK em ordem.')
    # Montagem ro e desmontagem são transitórias; a etapa final sempre revalida tudo que deve permanecer.
    if step not in state['etapas'] or step == 8:
        check(step, ds, who)
        if step not in state['etapas']:
            state['etapas'].append(step)
        tmp = path.with_suffix('.tmp')
        tmp.write_text(json.dumps(state)); tmp.chmod(0o600); tmp.replace(path)
    print(f'Etapa {step}: concluída. Pode avançar.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, tarfile.TarError) as e:
        print(f'Pendente: {e}'); sys.exit(1)
