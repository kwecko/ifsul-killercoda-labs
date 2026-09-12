#!/bin/bash
# Somente em container descartável; cria apenas namespaces/bridges próprios do exercício.
set -euo pipefail
[ "${LAB_TEST_CONTAINER:-}" = 1 ] && [ -e /.dockerenv ] || { echo 'Execute no container de testes.'; exit 1; }
BASE=/lab/arp-roteador/assets
CHECKS=/usr/local/lib/laboratorio
mkdir -p "$CHECKS"
install -m 755 "$BASE"/{identificar-aluno,iniciar-registro,gerar-comprovante,enviar-comprovante,preparar-roteador} /usr/local/bin/
install -m 644 "$BASE"/{laboratorio.sh,laboratorio.conf,normalizar-registro.pl,roteador_lab.py} "$CHECKS/"
install -m 755 "$BASE"/verify-step*.sh "$CHECKS/"
: > "$CHECKS/drive-upload-url"

cleanup() {
    for ns in estacao-a estacao-b roteador; do ip netns del "$ns" 2>/dev/null || true; done
    for br in br-a br-b; do ip link del "$br" 2>/dev/null || true; done
}
trap cleanup EXIT

TOTAL=0
passa() { if ! "$@" > /tmp/resultado 2>&1; then cat /tmp/resultado; echo "FALHOU: $*"; exit 1; fi; TOTAL=$((TOTAL+1)); }
falha() { if "$@" > /tmp/resultado 2>&1; then cat /tmp/resultado; echo "PASSOU INDEVIDAMENTE: $*"; exit 1; fi; TOTAL=$((TOTAL+1)); }
verify() { bash "$CHECKS/verify-step$1.sh"; }

passa preparar-roteador
source /root/rede.env
passa preparar-roteador
estacao-a ip addr show veth-a | grep -q '10.77.1.10/24'
estacao-b ip addr show veth-b | grep -q '10.77.2.10/24'
roteador ip addr show rot-a | grep -q '10.77.1.1/24'
roteador ip addr show rot-b | grep -q '10.77.2.1/24'
[ "$(roteador sysctl -n net.ipv4.ip_forward)" = 1 ]

printf '20261CM.INF_I0027\nJosé da Silva\n' | identificar-aluno
SESSAO=$(sed -n 's/^SESSAO=//p' /root/.laboratorio-aluno)
mkdir -p /root/registros
printf 'Registro simulado da atividade de ARP entre redes\n' > "/root/registros/$SESSAO.log"
falha gerar-comprovante
falha verify 2
passa verify 1

# Etapa 2: estacao-a so pede ARP pelo gateway, nunca pelo IP final.
falha verify 2
estacao-a timeout 4 tcpdump -i veth-a -e -n arp -w /root/captura-arp-roteador/step2-a.pcap &
roteador timeout 4 tcpdump -i rot-b -e -n arp -w /root/captura-arp-roteador/step2-b.pcap &
sleep 1
estacao-a ping -c 2 -W 1 10.77.2.10 > /dev/null
wait
falha verify 3
passa verify 2

# Etapa 3: mesma captura, lado do roteador -- ele proprio resolve estacao-b.
passa verify 3

# Etapa 4: MAC muda a cada salto, IP nao muda.
falha verify 4
estacao-a timeout 4 tcpdump -i veth-a -e -n icmp -w /root/captura-arp-roteador/step4-a.pcap &
roteador timeout 4 tcpdump -i rot-b -e -n icmp -w /root/captura-arp-roteador/step4-b.pcap &
sleep 1
estacao-a ping -c 2 -W 1 10.77.2.10 > /dev/null
wait
passa verify 4

# Etapa 5: sem rota, nao ha tentativa de ARP; restaura e conclui.
falha verify 5
estacao-a ip route del default
falha estacao-a ping -c 1 -W 1 10.77.2.10
falha verify 5
estacao-a ip route add default via 10.77.1.1
estacao-a ping -c 1 -W 1 10.77.2.10 > /dev/null
falha verify 5
printf 'curto\n' > /root/relatorio-arp-roteador/conclusao.txt
falha verify 5
printf '1) Porque ela so pergunta pelo gateway; nunca soube o MAC de estacao-b.\n2) Porque o roteador recebe o pacote e refaz sua propria resolucao ao encaminhar para a outra rede.\n3) Porque a resolucao ARP so ocorre depois que o roteamento decide um proximo salto.\n' > /root/relatorio-arp-roteador/conclusao.txt
passa verify 5
# Etapas anteriores continuam validas por checkpoint.
for n in 1 2 3 4; do passa verify "$n"; done

passa gerar-comprovante
TXT="/root/comprovantes/arp-roteador_20261CM.INF_I0027_${SESSAO}.txt"
[ -s "$TXT" ]
grep -qx 'LABORATORIO=arp-roteador' "$TXT"
HASH=$(head -n 7 "$TXT" | sha256sum | cut -d ' ' -f1)
grep -qx "CODIGO=SHA256:$HASH" "$TXT"
[ -f "/root/comprovantes/arp-roteador_20261CM.INF_I0027_${SESSAO}_${HASH}_historico.log" ]

# Progresso de outra sessao nao e reaproveitado.
sed -i "s/$SESSAO/00000000-0000-4000-8000-000000000001/" /var/lib/lab-arp-roteador/progresso.json
falha verify 5
falha gerar-comprovante

printf 'OK: %s verificações do laboratório de ARP entre redes com roteador.\n' "$TOTAL"
