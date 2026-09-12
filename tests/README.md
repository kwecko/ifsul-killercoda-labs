# Testes do laboratório

Execute a partir da raiz do repositório, com Docker disponível:

```bash
docker run --rm -e LAB_TEST_CONTAINER=1 -v "$PWD:/lab:ro" ubuntu:24.04 bash /lab/tests/usuarios-grupos.sh
```

O teste cria contas, grupos e diretórios somente no contêiner descartável. O repositório é montado para leitura. A imagem pode precisar ser baixada na primeira execução.

Os testes percorrem a atividade completa, verificam soluções válidas e introduzem erros de associação, senha, shell, descrição, propriedade, permissões e conteúdo. Também verificam que o comprovante recusa atividades incompletas e não executa o conteúdo do registro de identificação.

Os verificadores ficam em `usuarios-grupos/assets/verify-step*.sh`: o `index.json` os referencia nos botões CHECK e os entrega em `/usr/local/lib/laboratorio/` para o comprovante usar os mesmos critérios.

A validação confere o estado final do ambiente. Ela não comprova quem digitou cada comando nem autentica a matrícula; o aluno tem acesso a root. O comprovante é um registro didático, sem assinatura ou validação externa.

Depois de publicar alterações no GitHub, confira também uma nova sessão no Killercoda: a execução local não testa a sincronização nem a interface da plataforma.

O fluxo também verifica a geração do TXT, nome e campos, SHA-256, alteração dos dados, reemissão, matrícula com zeros à esquerda, falha de publicação sem deixar arquivo parcial e geração de uma nova sessão. São asserções internas do teste em contêiner, não um validador para o professor. O contrato do arquivo está em [comprovante-v2.md](../docs/comprovante-v2.md).

A integração opcional com Drive tem testes do cliente (curl simulado dentro do contêiner) e do receptor: `node tests/test_google_drive.cjs`. Nenhum desses testes envia arquivos ao Google.

Para testar a gravação real em terminal (Docker necessário), execute `python3 tests/test_registro_pty.py`. O teste cria um contêiner descartável, verifica comandos de root/julia, ausência de entrada com eco desativado, prevenção de gravação aninhada e retomada sem apagar o histórico. Não envia dados ao Drive.

A infraestrutura compartilhada é validada com `python3 ferramentas/laboratorios.py sincronizar --check` e `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v`. Os testes PTY e de novo cenário não são executados na descoberta automática. Para testar um segundo laboratório completo em Ubuntu descartável: `PYTHONDONTWRITEBYTECODE=1 python3 tests/test_novo_laboratorio.py`.

## Partições: operações reais em dois discos virtuais

Em uma máquina de desenvolvimento com Docker/Linux:

```bash
docker build -f tests/Dockerfile.particoes -t ifsul-particoes-test .
docker run --rm --privileged -e LAB_TEST_CONTAINER=1 -v "$PWD:/lab:ro" ifsul-particoes-test bash /lab/tests/particoes-linux.sh
```

O container precisa de privilégios para loop e mount. O script se recusa a executar fora do container de testes e só cria/formata imagens próprias em `/var/lib/lab-particoes`; a limpeza desmonta os volumes do exercício e desassocia apenas seus loops. Não envia dados ao Drive. Verifica as oito etapas, recusa de avanço com pendências, rótulo incorreto, ausência de arquivos/backup, somente leitura, volume ocupado, desmontagem, montagem por UUID, exclusão, recuperação e emissão. Também confere regressão no estado final, preparação idempotente e checkpoints de outra sessão.

## ARP: três estações simuladas por network namespaces

Em uma máquina de desenvolvimento com Docker/Linux:

```bash
docker build -f tests/Dockerfile.arp -t ifsul-arp-test .
docker run --rm --privileged -e LAB_TEST_CONTAINER=1 -v "$PWD:/lab:ro" ifsul-arp-test bash /lab/tests/arp.sh
```

O container precisa de privilégios para criar *network namespaces*, interfaces `veth` e um bridge. O script cria apenas os três namespaces do exercício (`estacao-a`, `estacao-b`, `estacao-c`) e o bridge `br-lab`; a limpeza os remove ao final. Não envia dados ao Drive nem toca na interface de rede real do container. Verifica as seis etapas, recusa de avanço com pendências, visibilidade de broadcast/unicast em uma LAN comutada, aprendizado legítimo, envenenamento por ARP gratuito forjado (incluindo a diferença entre um pedido e uma resposta gratuita), resistência de uma entrada estática ao mesmo ataque, diagnóstico final e emissão do comprovante. Também confere checkpoints de outra sessão.

## ARP entre redes: duas sub-redes e um roteador simulados

Em uma máquina de desenvolvimento com Docker/Linux:

```bash
docker build -f tests/Dockerfile.arp-roteador -t ifsul-arp-roteador-test .
docker run --rm --privileged -e LAB_TEST_CONTAINER=1 -v "$PWD:/lab:ro" ifsul-arp-roteador-test bash /lab/tests/arp-roteador.sh
```

O container precisa dos mesmos privilégios do teste de ARP. O script cria dois bridges (`br-a`, `br-b`) e três namespaces (`estacao-a`, `estacao-b`, `roteador`); a limpeza os remove ao final. Verifica as cinco etapas, recusa de avanço com pendências, que a estação de origem só resolve por ARP o gateway (nunca o IP em outra rede), que é o roteador quem refaz a resolução na rede de destino, a troca de endereços de enlace a cada salto com o IP constante, e que a ausência de rota impede qualquer tentativa de ARP. Também confere checkpoints de outra sessão.
