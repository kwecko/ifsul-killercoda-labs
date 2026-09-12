#!/usr/bin/env python3
"""Verifica o laboratório de ARP; checkpoints não são prova contra root."""
import json
import re
import subprocess
import sys
from pathlib import Path

BASE = Path('/var/lib/lab-arp')
CAPTURA = Path('/root/captura-arp')
RELATORIO = Path('/root/relatorio-arp')
ESTACOES = {
    'estacao-a': ('veth-a', '10.77.0.1'),
    'estacao-b': ('veth-b', '10.77.0.2'),
    'estacao-c': ('veth-c', '10.77.0.3'),
}

# "ip neigh show dev IFACE" omite o "dev IFACE" de cada linha, por ser redundante com o filtro.
NEIGH_RE = re.compile(r'^(?P<ip>\S+)\s+(?:lladdr\s+(?P<mac>\S+)\s+)?(?P<state>\S+)\s*$')
# tcpdump não preenche zero à esquerda em cada octeto do MAC (ex.: "2:14:..."), por isso o
# tamanho não é fixo; os separadores (">", ",", vírgula) já delimitam onde o MAC termina.
LINE_RE = re.compile(r'^\S+\s+(?P<src>[0-9a-f:]+)\s+>\s+(?P<dst>[0-9a-f:]+),\s+ethertype ARP.*?:\s+(?P<corpo>.+)$')
REQ_RE = re.compile(r'Request who-has (?P<alvo>[\d.]+) tell (?P<origem>[\d.]+)')
REPLY_RE = re.compile(r'Reply (?P<ip>[\d.]+) is-at (?P<mac>[0-9a-f:]+)')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def run(*args):
    p = subprocess.run(args, capture_output=True, text=True)
    need(p.returncode == 0, f'Falha em {args[0]}: {p.stderr.strip()}')
    return p.stdout.strip()


def netns_list():
    out = subprocess.run(['ip', 'netns', 'list'], capture_output=True, text=True).stdout
    return {linha.split()[0] for linha in out.splitlines() if linha.strip()}


def topologia():
    presentes = netns_list()
    for ns in ESTACOES:
        need(ns in presentes, f'Execute preparar-rede: falta o namespace {ns}.')
    for ns, (iface, ip) in ESTACOES.items():
        info = json.loads(run('ip', '-n', ns, '-j', 'addr', 'show', iface))
        need(info, f'Interface {iface} ausente em {ns}. Execute preparar-rede.')
        link = info[0]
        need('UP' in link.get('flags', []), f'Ative {iface} em {ns}; execute preparar-rede novamente.')
        enderecos = {f"{a['local']}/{a['prefixlen']}" for a in link.get('addr_info', []) if a.get('family') == 'inet'}
        need(f'{ip}/24' in enderecos, f'{ns} precisa do endereço {ip}/24 em {iface}.')
    return ESTACOES


def mac_of(ns, iface):
    info = json.loads(run('ip', '-n', ns, '-j', 'link', 'show', iface))
    return info[0]['address']


def neigh_table(ns, iface):
    out = subprocess.run(['ip', '-n', ns, 'neigh', 'show', 'dev', iface], capture_output=True, text=True).stdout
    tabela = {}
    for linha in out.splitlines():
        m = NEIGH_RE.match(linha.strip())
        if m:
            tabela[m.group('ip')] = (m.group('mac'), m.group('state'))
    return tabela


def resolvido(ns, iface, ip, mac_esperado=None, permanente=False):
    tabela = neigh_table(ns, iface)
    need(ip in tabela, f'{ns}: não há entrada ARP para {ip} em {iface}.')
    mac, estado = tabela[ip]
    need(estado not in ('FAILED', 'INCOMPLETE', 'NONE'), f'{ns}: entrada de {ip} em estado {estado}; refaça a resolução.')
    if mac_esperado:
        need(mac == mac_esperado, f'{ns}: {ip} deveria apontar para {mac_esperado}, mas está {mac}.')
    if permanente:
        need(estado == 'PERMANENT', f'{ns}: a entrada de {ip} deveria ser estática (PERMANENT), está {estado}.')
    return mac, estado


def sem_entrada(ns, iface, ip):
    tabela = neigh_table(ns, iface)
    need(ip not in tabela, f'{ns}: ainda não deveria haver entrada ARP para {ip} em {iface} nesta etapa.')


def captura(nome):
    p = CAPTURA / nome
    need(p.is_file() and p.stat().st_size > 0, f'Gere a captura em {p}, conforme a etapa.')
    saida = subprocess.run(['tcpdump', '-tt', '-e', '-n', '-r', str(p)], capture_output=True, text=True)
    need(saida.returncode == 0, f'Captura em {p} corrompida ou incompleta; refaça esta etapa.')
    quadros = []
    for linha in saida.stdout.splitlines():
        m = LINE_RE.match(linha.strip())
        if m:
            quadros.append(m.groupdict())
    return quadros


def report(nome, minimo=1):
    p = RELATORIO / nome
    need(p.is_file() and len(p.read_text().strip()) >= minimo, f'Preencha {p}, conforme o roteiro.')


def check(step):
    est = topologia()
    if step == 1:
        for ns, (iface, _) in est.items():
            for _, ip in est.values():
                sem_entrada(ns, iface, ip)
    elif step == 2:
        mac_a = mac_of('estacao-a', 'veth-a')
        mac_b = mac_of('estacao-b', 'veth-b')
        quadros = captura('step2.pcap')
        pedidos = [REQ_RE.search(q['corpo']) for q in quadros if REQ_RE.search(q['corpo'])]
        respostas = [REPLY_RE.search(q['corpo']) for q in quadros if REPLY_RE.search(q['corpo'])]
        need(any(m.group('alvo') == '10.77.0.2' and m.group('origem') == '10.77.0.1' for m in pedidos),
             'A captura em estacao-c precisa mostrar o pedido ARP de 10.77.0.1 perguntando por 10.77.0.2.')
        need(not respostas,
             'A captura em estacao-c não deveria conter nenhuma resposta ARP: o switch entrega o unicast só para quem pediu.')
        resolvido('estacao-a', 'veth-a', '10.77.0.2', mac_esperado=mac_b)
        resolvido('estacao-b', 'veth-b', '10.77.0.1', mac_esperado=mac_a)
        sem_entrada('estacao-c', 'veth-c', '10.77.0.1')
        sem_entrada('estacao-c', 'veth-c', '10.77.0.2')
    elif step == 3:
        mac_b = mac_of('estacao-b', 'veth-b')
        resolvido('estacao-c', 'veth-c', '10.77.0.2', mac_esperado=mac_b)
    elif step == 4:
        mac_a = mac_of('estacao-a', 'veth-a')
        quadros = captura('step4.pcap')
        need(any(q['dst'] == 'ff:ff:ff:ff:ff:ff' and REPLY_RE.search(q['corpo'])
                 and REPLY_RE.search(q['corpo']).group('ip') == '10.77.0.2'
                 and REPLY_RE.search(q['corpo']).group('mac') == mac_a for q in quadros),
             'A captura precisa mostrar um ARP reply gratuito (destino broadcast) anunciando 10.77.0.2 com o MAC de estacao-a.')
        resolvido('estacao-c', 'veth-c', '10.77.0.2', mac_esperado=mac_a)
    elif step == 5:
        mac_a = mac_of('estacao-a', 'veth-a')
        mac_b = mac_of('estacao-b', 'veth-b')
        resolvido('estacao-c', 'veth-c', '10.77.0.2', mac_esperado=mac_b, permanente=True)
        quadros = captura('step5.pcap')
        need(any(q['dst'] == 'ff:ff:ff:ff:ff:ff' and REPLY_RE.search(q['corpo'])
                 and REPLY_RE.search(q['corpo']).group('mac') == mac_a for q in quadros),
             'Repita o ataque com forjar-arp-gratuito e capture o novo quadro em estacao-c.')
        resolvido('estacao-c', 'veth-c', '10.77.0.2', mac_esperado=mac_b, permanente=True)
    elif step == 6:
        mac_a = mac_of('estacao-a', 'veth-a')
        mac_b = mac_of('estacao-b', 'veth-b')
        resolvido('estacao-a', 'veth-a', '10.77.0.2', mac_esperado=mac_b)
        resolvido('estacao-b', 'veth-b', '10.77.0.1', mac_esperado=mac_a)
        resolvido('estacao-c', 'veth-c', '10.77.0.2', mac_esperado=mac_b, permanente=True)
        report('conclusao.txt', 120)
    else:
        raise ValueError('Etapa desconhecida.')


def identity():
    run('bash', '/usr/local/lib/laboratorio/verify-step0.sh')
    return dict(l.split('=', 1) for l in Path('/root/.laboratorio-aluno').read_text().splitlines() if '=' in l)


def main():
    need(len(sys.argv) == 2 and sys.argv[1].isdigit(), 'Informe a etapa de 1 a 6.')
    step = int(sys.argv[1])
    need(1 <= step <= 6, 'Etapa inválida.')
    who = identity()
    path = BASE / 'progresso.json'
    state = json.loads(path.read_text()) if path.exists() else {'sessao': who['SESSAO'], 'etapas': []}
    need(state['sessao'] == who['SESSAO'], 'Progresso de outra sessão; inicie um ambiente novo.')
    need(all(n in state['etapas'] for n in range(1, step)), 'Volte às etapas anteriores e pressione CHECK em ordem.')
    # A etapa final sempre revalida tudo; as demais confiam no checkpoint já registrado.
    if step not in state['etapas'] or step == 6:
        check(step)
        if step not in state['etapas']:
            state['etapas'].append(step)
        tmp = path.with_suffix('.tmp')
        tmp.write_text(json.dumps(state))
        tmp.chmod(0o600)
        tmp.replace(path)
    print(f'Etapa {step}: concluída. Pode avançar.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as e:
        print(f'Pendente: {e}')
        sys.exit(1)
