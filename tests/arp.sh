#!/bin/bash
# Somente em container descartável; cria apenas namespaces/bridge próprios do exercício.
set -euo pipefail
[ "${LAB_TEST_CONTAINER:-}" = 1 ] && [ -e /.dockerenv ] || { echo 'Execute no container de testes.'; exit 1; }
BASE=/lab/arp/assets
CHECKS=/usr/local/lib/laboratorio
mkdir -p "$CHECKS"
install -m 755 "$BASE"/{identificar-aluno,iniciar-registro,gerar-comprovante,enviar-comprovante,preparar-rede,forjar-arp-gratuito} /usr/local/bin/
install -m 644 "$BASE"/{laboratorio.sh,laboratorio.conf,normalizar-registro.pl,arp_lab.py} "$CHECKS/"
install -m 755 "$BASE"/verify-step*.sh "$CHECKS/"
: > "$CHECKS/drive-upload-url"

cleanup() {
    for ns in estacao-a estacao-b estacao-c; do ip netns del "$ns" 2>/dev/null || true; done
    ip link del br-lab 2>/dev/null || true
}
trap cleanup EXIT

TOTAL=0
passa() { if ! "$@" > /tmp/resultado 2>&1; then cat /tmp/resultado; echo "FALHOU: $*"; exit 1; fi; TOTAL=$((TOTAL+1)); }
falha() { if "$@" > /tmp/resultado 2>&1; then cat /tmp/resultado; echo "PASSOU INDEVIDAMENTE: $*"; exit 1; fi; TOTAL=$((TOTAL+1)); }
verify() { bash "$CHECKS/verify-step$1.sh"; }

passa preparar-rede
source /root/rede.env
passa preparar-rede
estacao-a ip addr show veth-a | grep -q '10.77.0.1/24'
estacao-b ip addr show veth-b | grep -q '10.77.0.2/24'
estacao-c ip addr show veth-c | grep -q '10.77.0.3/24'

printf '20261CM.INF_I0027\nJosé da Silva\n' | identificar-aluno
SESSAO=$(sed -n 's/^SESSAO=//p' /root/.laboratorio-aluno)
mkdir -p /root/registros
printf 'Registro simulado da atividade de ARP\n' > "/root/registros/$SESSAO.log"
falha gerar-comprovante
falha verify 2
passa verify 1

# Etapa 2: broadcast visivel em estacao-c, resposta unicast nao.
falha verify 2
estacao-c timeout 4 tcpdump -i veth-c -e -n arp -w /root/captura-arp/step2.pcap &
sleep 1
estacao-a ping -c 2 -W 1 10.77.0.2 > /dev/null
wait
falha verify 3
passa verify 2

# Etapa 3: estacao-c aprende de verdade ao pingar.
falha verify 3
estacao-c ping -c 1 -W 1 10.77.0.2 > /dev/null
passa verify 3

# Etapa 4: ARP gratuito forjado envenena o cache de estacao-c.
falha verify 4
# Um pedido (request) gratuito nao deve satisfazer o verificador, que exige uma resposta (reply).
estacao-c timeout 5 tcpdump -c 1 -i veth-c -e -n arp -w /root/captura-arp/step4.pcap &
sleep 1
estacao-a forjar-arp-gratuito veth-a 10.77.0.2 request
wait
falha verify 4
estacao-c timeout 5 tcpdump -c 1 -i veth-c -e -n arp -w /root/captura-arp/step4.pcap &
sleep 1
estacao-a forjar-arp-gratuito veth-a 10.77.0.2 reply
wait
passa verify 4
MACA=$(estacao-a ip -j link show veth-a | python3 -c 'import json,sys; print(json.load(sys.stdin)[0]["address"])')
estacao-c ip neigh show | grep -q "10.77.0.2 dev veth-c lladdr $MACA"

# Etapa 5: entrada estatica resiste ao mesmo ataque.
falha verify 5
MACB=$(estacao-b ip -j link show veth-b | python3 -c 'import json,sys; print(json.load(sys.stdin)[0]["address"])')
# Sem protecao, uma entrada dinamica correta ainda e vulneravel ao mesmo ataque.
estacao-c ping -c 1 -W 1 10.77.0.2 > /dev/null
estacao-c timeout 5 tcpdump -c 1 -i veth-c -e -n arp -w /root/captura-arp/step5.pcap &
sleep 1
estacao-a forjar-arp-gratuito veth-a 10.77.0.2 reply
wait
falha verify 5
estacao-c ip neigh replace 10.77.0.2 lladdr "$MACB" dev veth-c nud permanent
estacao-c timeout 5 tcpdump -c 1 -i veth-c -e -n arp -w /root/captura-arp/step5.pcap &
sleep 1
estacao-a forjar-arp-gratuito veth-a 10.77.0.2 reply
wait
passa verify 5
estacao-c ip neigh show | grep -q "10.77.0.2 dev veth-c lladdr $MACB PERMANENT"

# Etapa 6: diagnostico final e conclusao.
falha verify 6
estacao-a ip neigh flush dev veth-a
estacao-b ip neigh flush dev veth-b
estacao-a ping -c 1 -W 1 10.77.0.2 > /dev/null
falha verify 6
printf 'resposta muito curta\n' > /root/relatorio-arp/conclusao.txt
falha verify 6
printf '1) O pedido eh broadcast e alcanca todos; a resposta eh unicast e o switch aprende a porta certa, entregando so para quem perguntou.\n2) Nada autentica quem envia um ARP gratuito; qualquer estacao pode anunciar um IP alheio.\n3) Entradas PERMANENT ignoram atualizacoes vindas da rede.\n' > /root/relatorio-arp/conclusao.txt
passa verify 6
# Etapas anteriores continuam validas por checkpoint.
for n in 1 2 3 4 5; do passa verify "$n"; done

passa gerar-comprovante
TXT="/root/comprovantes/arp_20261CM.INF_I0027_${SESSAO}.txt"
[ -s "$TXT" ]
grep -qx 'LABORATORIO=arp' "$TXT"
HASH=$(head -n 7 "$TXT" | sha256sum | cut -d ' ' -f1)
grep -qx "CODIGO=SHA256:$HASH" "$TXT"
[ -f "/root/comprovantes/arp_20261CM.INF_I0027_${SESSAO}_${HASH}_historico.log" ]

# Progresso de outra sessao nao e reaproveitado.
sed -i "s/$SESSAO/00000000-0000-4000-8000-000000000001/" /var/lib/lab-arp/progresso.json
falha verify 6
falha gerar-comprovante

printf 'OK: %s verificações do laboratório de ARP com três estações.\n' "$TOTAL"
