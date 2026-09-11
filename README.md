# Laboratórios IFSul no Killercoda

Cada cenário usa a mesma infraestrutura de identificação, gravação do terminal, comprovante e envio ao Google Drive. Os enunciados e verificadores das tarefas pertencem a cada laboratório.

## Criar uma nova atividade

Com Python 3.8 ou superior, na raiz do repositório:

```bash
python3 ferramentas/laboratorios.py criar arquivos-diretorios --titulo "Arquivos e diretórios no Linux"
```

Isso cria a pasta `arquivos-diretorios/`, com identificação, uma etapa de exemplo, página final e todos os scripts necessários. O comando não sobrescreve pastas existentes. Não cria commits, não faz push e não altera sua conta Google.

O rascunho começa com `recebimento_ativo: false` e um verificador que sempre reprova. Escreva o enunciado e implemente os critérios antes de distribuir a atividade. A pasta `modelo/` em si não é um cenário e não tem `index.json`.

## Configurar as etapas

Edite `<laboratorio>/laboratorio.json`. Exemplo:

```json
{
  "id": "arquivos-diretorios",
  "titulo": "Arquivos e diretórios no Linux",
  "descricao": "Atividade sobre arquivos e diretórios.",
  "imagem": "ubuntu",
  "recebimento_ativo": false,
  "pasta_drive": "ID_DA_PASTA_DO_GOOGLE_DRIVE",
  "etapas": [
    {
      "title": "Organização de arquivos",
      "text": "step1.md",
      "verify": "assets/verify-step1.sh"
    }
  ]
}
```

- `id` corresponde à pasta e tem até 40 letras minúsculas, dígitos ou hífens, começando por letra.
- A identificação é incluída automaticamente como etapa zero. Não a repita na lista.
- Acrescente quantas tarefas precisar. Cada uma tem seu Markdown e um `assets/verify-stepN.sh`, com N maior que zero. Números não precisam ser consecutivos; a ordem é a da lista.
- Cada verificador retorna `0` quando os requisitos foram cumpridos e um valor diferente quando há pendências. Não remova nem modifique as tarefas durante a verificação.
- As etapas listadas são exatamente as usadas no CHECK e na emissão/envio. Uma verificação ausente bloqueia a conclusão.
- A pasta padrão e a URL do receptor ficam em `comum/drive.json`. Você pode usar a mesma pasta ou passar `--pasta-drive ID` ao criar uma atividade.
- Quando o laboratório estiver pronto, altere `recebimento_ativo` para `true` e sincronize. Isso habilita a URL no cenário e autoriza o laboratório no receptor gerado. Não comprova que o enunciado ou os testes estão corretos: revise-os antes.

## Sincronizar e publicar

```bash
python3 ferramentas/laboratorios.py sincronizar
python3 ferramentas/laboratorios.py sincronizar --check
```

A sincronização valida referências e atualiza as cópias dos scripts comuns nos cenários, `index.json`, a configuração de execução e os catálogos do professor/Apps Script. Ela preserva os enunciados existentes, os verificadores específicos e configurações adicionais do índice, como assets extras e interface. As seções gerenciadas (título, descrição, imagem, etapas e assets comuns) vêm do `laboratorio.json`.

Revise o diff, execute os testes, faça commit/push na branch configurada no Killercoda e inicie uma nova sessão. Para o Drive reconhecer novos laboratórios, pastas ou mudanças de ativação, copie o `professor/google-drive/Code.gs` atualizado e publique **Nova versão** da implantação existente. Salvar o script ou fazer push no GitHub não atualiza a implantação Google.

O template gera um `index.json` utilizável mesmo em rascunho. `recebimento_ativo: false` desativa uploads, não oculta o cenário no Killercoda. Não publique um rascunho na branch usada pelos alunos até terminar suas tarefas.

## Onde editar

| Local | Responsabilidade |
|---|---|
| `comum/assets/` | Fonte dos scripts compartilhados; edite aqui e sincronize |
| `comum/drive.json` | URL pública do Apps Script e pasta padrão para novos cenários |
| `modelo/` | Textos iniciais e verificador pendente copiados apenas na criação |
| `<laboratorio>/laboratorio.json` | Identidade, apresentação, etapas, pasta e ativação do recebimento |
| `<laboratorio>/step*.md`, `intro.md`, `finish.md` | Conteúdo didático do cenário |
| `<laboratorio>/assets/verify-stepN.sh` (N ≥ 1) | Regras específicas da atividade |
| `<laboratorio>/assets/` (scripts comuns e configuração) | Cópias geradas, necessárias ao upload do Killercoda; não editar diretamente |
| `professor/laboratorios.json` | Catálogo gerado para o validador local |
| `professor/google-drive/Code.gs` | Receptor compartilhado; somente o bloco de catálogo é gerado |

Não há download de scripts compartilhados durante a atividade. Cada cenário é autossuficiente no Killercoda. O código do professor permanece fora dos assets enviados às VMs. Cada VM contém um cenário; a identificação inclui o ID para evitar misturar atividades.

## Comprovantes e confiança

Os comprovantes v2 têm laboratório, matrícula, nome, sessão, data, resultado e SHA-256. O nome do arquivo usa o ID da atividade. O receptor aceita somente laboratórios cadastrados e ativos e escolhe a pasta pelo catálogo, nunca por um destino enviado pelo aluno. A cota diária do Apps Script é global para todos os laboratórios.

O validador Python lê o catálogo ao lado do script e aceita comprovantes v1/v2 de laboratórios cadastrados, inclusive se o recebimento estiver desativado (para permitir conferir entregas anteriores). Use `--laboratorio ID` para exigir a atividade esperada. Distribua `validar_comprovante.py` junto com `laboratorios.json`.

Root pode alterar registros e hashes. A transcrição é evidência auxiliar; nem o comprovante nem o envio autenticam o aluno. Consulte [formato v2](docs/comprovante-v2.md), [registro do terminal](docs/registro-terminal.md) e [configuração do Google Drive](professor/google-drive/README.md).

## Testes

```bash
python3 ferramentas/laboratorios.py sincronizar --check
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
node tests/test_google_drive.cjs
docker run --rm -e LAB_TEST_CONTAINER=1 -v "$PWD:/lab:ro" ubuntu:24.04 bash /lab/tests/usuarios-grupos.sh
PYTHONDONTWRITEBYTECODE=1 python3 tests/test_registro_pty.py
PYTHONDONTWRITEBYTECODE=1 python3 tests/test_novo_laboratorio.py
```

Os testes Docker usam contêineres descartáveis. O teste de novo laboratório cria um segundo cenário em pasta temporária, executa duas tarefas e remove esse cenário ao terminar. Nenhum teste envia dados ao Drive real.
