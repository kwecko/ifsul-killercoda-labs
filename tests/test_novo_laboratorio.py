"""Cria e executa um segundo cenário somente em diretório e contêiner temporários."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


def main():
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location('laboratorios', root / 'ferramentas/laboratorios.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    with tempfile.TemporaryDirectory(prefix='teste-modelo-lab-') as tmp:
        projeto = Path(tmp)
        for nome in ('comum', 'modelo', 'professor', 'usuarios-grupos'):
            shutil.copytree(root / nome, projeto / nome)
        novo = mod.criar(projeto, 'arquivos-diretorios', 'Arquivos e diretórios', 'Cenário de teste temporário')
        (novo / 'assets/verify-step1.sh').write_text('#!/bin/bash\ntest -d /exemplo-atividade\n')
        (novo / 'assets/verify-step2.sh').write_text("#!/bin/bash\ngrep -qx 'Concluído' /exemplo-atividade/resultado.txt 2>/dev/null\n")
        (novo / 'step2.md').write_text('Segunda tarefa')
        config = json.loads((novo / 'laboratorio.json').read_text())
        config['etapas'].append(dict(title='Segunda tarefa', text='step2.md', verify='assets/verify-step2.sh'))
        (novo / 'laboratorio.json').write_text(json.dumps(config))
        mod.sincronizar(projeto)
        subprocess.run(['docker', 'run', '--rm', '-e', 'LAB_TEST_CONTAINER=1', '-v', f'{root}:/lab:ro',
                        '-v', f'{novo}:/cenario:ro', 'ubuntu:24.04', 'bash', '/lab/tests/novo-laboratorio.sh'], check=True)


if __name__ == '__main__':
    main()
