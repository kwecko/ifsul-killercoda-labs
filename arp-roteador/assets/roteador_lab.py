#!/usr/bin/env python3
"""Verifica o laboratório de ARP entre redes; checkpoints não são prova contra root."""
import json
import re
import subprocess
import sys
from pathlib import Path

BASE = Path('/var/lib/lab-arp-roteador')
CAPTURA = Path('/root/captura-arp-roteador')
RELATORIO = Path('/root/relatorio-arp-roteador')

# (namespace, interface, IP, gateway, rede)
ESTACOES = {
    'estacao-a': ('veth-a', '10.77.1.10', '10.77.1.1'),
    'estacao-b': ('veth-b', '10.77.2.10', '10.77.2.1'),
}
# (interface do roteador, IP naquela rede)
ROTEADOR = {'rot-a': '10.77.1.1', 'rot-b': '10.77.2.1'}

# "ip neigh show dev IFACE" omite o "dev IFACE" de cada linha, por ser redundante com o filtro.
NEIGH_RE = re.compile(r'^(?P<ip>\S+)\s+(?:lladdr\s+(?P<mac>\S+)\s+)?(?P<state>\S+)\s*$')
# tcpdump não preenche zero à esquerda em cada octeto do MAC, por isso o tamanho não é fixo.
LINE_RE = re.compile(r'^\S+\s+(?P<src>[0-9a-f:]+)\s+>\s+(?P<dst>[0-9a-f:]+),\s+ethertype (?P<eth>\S+).*?:\s+(?P<corpo>.+)$')
REQ_RE = re.compile(r'Request who-has (?P<alvo>[\d.]+) tell (?P<origem>[\d.]+)')
ICMP_RE = re.compile(r'^(?P<src_ip>[\d.]+) > (?P<dst_ip>[\d.]+): ICMP echo request')


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


def endereco_ok(ns, iface, ip):
    info = json.loads(run('ip', '-n', ns, '-j', 'addr', 'show', iface))
    need(info, f'Interface {iface} ausente em {ns}. Execute preparar-roteador.')
    link = info[0]
    need('UP' in link.get('flags', []), f'Ative {iface} em {ns}; execute preparar-roteador novamente.')
    enderecos = {f"{a['local']}/{a['prefixlen']}" for a in link.get('addr_info', []) if a.get('family') == 'inet'}
    need(f'{ip}/24' in enderecos, f'{ns} precisa do endereço {ip}/24 em {iface}.')


def topologia():
    presentes = netns_list()
    for ns in list(ESTACOES) + ['roteador']:
        need(ns in presentes, f'Execute preparar-roteador: falta o namespace {ns}.')
    for ns, (iface, ip, _) in ESTACOES.items():
        endereco_ok(ns, iface, ip)
    for iface, ip in ROTEADOR.items():
        endereco_ok('roteador', iface, ip)
    forward = run('ip', 'netns', 'exec', 'roteador', 'sysctl', '-n', 'net.ipv4.ip_forward')
    need(forward == '1', 'Habilite o encaminhamento no roteador: execute preparar-roteador novamente.')
    for ns, (iface, _, gw) in ESTACOES.items():
        rota = subprocess.run(['ip', '-n', ns, 'route', 'show', 'default'], capture_output=True, text=True).stdout
        need(f'via {gw}' in rota and f'dev {iface}' in rota, f'{ns} precisa de uma rota padrão via {gw} em {iface}.')


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


def resolvido(ns, iface, ip, mac_esperado=None):
    tabela = neigh_table(ns, iface)
    need(ip in tabela, f'{ns}: não há entrada ARP para {ip} em {iface}.')
    mac, estado = tabela[ip]
    need(estado not in ('FAILED', 'INCOMPLETE', 'NONE'), f'{ns}: entrada de {ip} em estado {estado}; refaça a resolução.')
    if mac_esperado:
        need(mac == mac_esperado, f'{ns}: {ip} deveria apontar para {mac_esperado}, mas está {mac}.')
    return mac, estado


def sem_entrada(ns, iface, ip):
    tabela = neigh_table(ns, iface)
    need(ip not in tabela, f'{ns}: não deveria haver entrada ARP para {ip} em {iface} nesta etapa.')


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
    topologia()
    if step == 1:
        for ns, (iface, _, gw) in ESTACOES.items():
            sem_entrada(ns, iface, gw)
        for iface in ROTEADOR:
            sem_entrada('roteador', iface, '10.77.1.10')
            sem_entrada('roteador', iface, '10.77.2.10')
    elif step == 2:
        mac_roteador_a = mac_of('roteador', 'rot-a')
        quadros = [q for q in captura('step2-a.pcap') if q['eth'] == 'ARP']
        pedidos = [REQ_RE.search(q['corpo']) for q in quadros if REQ_RE.search(q['corpo'])]
        need(any(m.group('alvo') == '10.77.1.1' and m.group('origem') == '10.77.1.10' for m in pedidos),
             'A captura do lado de estacao-a precisa mostrar um pedido ARP perguntando pelo gateway 10.77.1.1.')
        need(not any(m.group('alvo') == '10.77.2.10' for m in pedidos),
             'estacao-a nunca deveria perguntar por ARP diretamente pelo IP de estacao-b (10.77.2.10): ele está em outra rede.')
        resolvido('estacao-a', 'veth-a', '10.77.1.1', mac_esperado=mac_roteador_a)
        sem_entrada('estacao-a', 'veth-a', '10.77.2.10')
    elif step == 3:
        # Mesma captura simultânea da etapa 2, vista do lado de estacao-b (interface rot-b do roteador).
        quadros = [q for q in captura('step2-b.pcap') if q['eth'] == 'ARP']
        pedidos = [REQ_RE.search(q['corpo']) for q in quadros if REQ_RE.search(q['corpo'])]
        need(any(m.group('alvo') == '10.77.2.10' and m.group('origem') == '10.77.2.1' for m in pedidos),
             'A captura na interface rot-b do roteador (feita na etapa 2) precisa mostrar o PRÓPRIO roteador (10.77.2.1) perguntando pelo IP de estacao-b.')
        resolvido('estacao-b', 'veth-b', '10.77.2.1', mac_esperado=mac_of('roteador', 'rot-b'))
        sem_entrada('estacao-b', 'veth-b', '10.77.1.10')
    elif step == 4:
        mac_a = mac_of('estacao-a', 'veth-a')
        mac_rot_a = mac_of('roteador', 'rot-a')
        mac_rot_b = mac_of('roteador', 'rot-b')
        mac_b = mac_of('estacao-b', 'veth-b')
        lado_a = [q for q in captura('step4-a.pcap') if q['eth'] == 'IPv4' and ICMP_RE.search(q['corpo'])]
        lado_b = [q for q in captura('step4-b.pcap') if q['eth'] == 'IPv4' and ICMP_RE.search(q['corpo'])]
        need(any(ICMP_RE.search(q['corpo']).group('src_ip') == '10.77.1.10'
                 and ICMP_RE.search(q['corpo']).group('dst_ip') == '10.77.2.10'
                 and q['src'] == mac_a and q['dst'] == mac_rot_a for q in lado_a),
             'Na captura de estacao-a, o quadro do ping precisa ter MAC de origem de estacao-a e MAC de destino do roteador (rot-a).')
        need(any(ICMP_RE.search(q['corpo']).group('src_ip') == '10.77.1.10'
                 and ICMP_RE.search(q['corpo']).group('dst_ip') == '10.77.2.10'
                 and q['src'] == mac_rot_b and q['dst'] == mac_b for q in lado_b),
             'Na captura do roteador (rot-b), o quadro do mesmo ping precisa ter MAC de origem do roteador e MAC de destino de estacao-b.')
    elif step == 5:
        rota = subprocess.run(['ip', '-n', 'estacao-a', 'route', 'show', 'default'], capture_output=True, text=True).stdout
        need('via 10.77.1.1' in rota and 'dev veth-a' in rota, 'Restaure a rota padrão de estacao-a via 10.77.1.1.')
        resolvido('estacao-a', 'veth-a', '10.77.1.1', mac_esperado=mac_of('roteador', 'rot-a'))
        report('conclusao.txt', 120)
    else:
        raise ValueError('Etapa desconhecida.')


def identity():
    run('bash', '/usr/local/lib/laboratorio/verify-step0.sh')
    return dict(l.split('=', 1) for l in Path('/root/.laboratorio-aluno').read_text().splitlines() if '=' in l)


def main():
    need(len(sys.argv) == 2 and sys.argv[1].isdigit(), 'Informe a etapa de 1 a 5.')
    step = int(sys.argv[1])
    need(1 <= step <= 5, 'Etapa inválida.')
    who = identity()
    path = BASE / 'progresso.json'
    state = json.loads(path.read_text()) if path.exists() else {'sessao': who['SESSAO'], 'etapas': []}
    need(state['sessao'] == who['SESSAO'], 'Progresso de outra sessão; inicie um ambiente novo.')
    need(all(n in state['etapas'] for n in range(1, step)), 'Volte às etapas anteriores e pressione CHECK em ordem.')
    # A etapa final sempre revalida tudo; as demais confiam no checkpoint já registrado.
    if step not in state['etapas'] or step == 5:
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
