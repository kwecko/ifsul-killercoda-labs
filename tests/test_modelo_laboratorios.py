import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('laboratorios', ROOT / 'ferramentas/laboratorios.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ModeloTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        # Copia todos os cenários: o catálogo acompanha os laboratórios reais.
        cenarios = [p.parent.name for p in ROOT.glob('*/laboratorio.json')]
        for nome in ('comum', 'modelo', 'professor', *cenarios):
            shutil.copytree(ROOT / nome, self.root / nome)

    def tearDown(self):
        self.tmp.cleanup()

    def test_sincronizado_e_preserva_etapas_originais(self):
        original = [(self.root / f'usuarios-grupos/assets/verify-step{i}.sh').read_bytes() for i in range(1, 7)]
        mod.sincronizar(self.root, check=True)
        mod.sincronizar(self.root)
        self.assertEqual(original, [(self.root / f'usuarios-grupos/assets/verify-step{i}.sh').read_bytes() for i in range(1, 7)])

    def test_criar_modelo_reprova_e_nao_envia(self):
        destino = mod.criar(self.root, 'arquivos-diretorios', 'Arquivos e diretórios', 'Exercício')
        index = json.loads((destino / 'index.json').read_text())
        self.assertEqual(index['title'], 'Arquivos e diretórios')
        self.assertEqual(len(index['details']['steps']), 2)
        self.assertEqual((destino / 'assets/drive-upload-url').read_text(), '')
        self.assertIn('LABORATORIO=arquivos-diretorios', (destino / 'assets/laboratorio.conf').read_text())
        self.assertNotIn('usuarios-grupos', (destino / 'assets/gerar-comprovante').read_text())
        self.assertEqual(subprocess.run(['bash', str(destino / 'assets/verify-step1.sh')], capture_output=True).returncode, 1)
        mod.sincronizar(self.root, check=True)
        with self.assertRaises(ValueError):
            mod.criar(self.root, 'arquivos-diretorios', 'Outro', 'Outro')

    def test_quantidade_de_etapas_e_ativacao(self):
        destino = mod.criar(self.root, 'arquivos-diretorios', 'Arquivos', 'Exercício')
        (destino / 'step2.md').write_text('Segunda tarefa')
        (destino / 'assets/verify-step2.sh').write_text('#!/bin/bash\nexit 1\n')
        config = json.loads((destino / 'laboratorio.json').read_text())
        config['etapas'].append(dict(title='Segunda', text='step2.md', verify='assets/verify-step2.sh'))
        config['recebimento_ativo'] = True
        config['pasta_drive'] = 'pasta-teste'
        (destino / 'laboratorio.json').write_text(json.dumps(config))
        mod.sincronizar(self.root)
        self.assertIn('verify-step0.sh,verify-step1.sh,verify-step2.sh', (destino / 'assets/laboratorio.conf').read_text())
        self.assertTrue((destino / 'assets/drive-upload-url').read_text().startswith('https://script.google.com/'))
        catalogo = json.loads((self.root / 'professor/laboratorios.json').read_text())
        self.assertEqual(catalogo['arquivos-diretorios']['pasta_drive'], 'pasta-teste')

    def test_detecta_copia_desatualizada_sem_modificar(self):
        arquivo = self.root / 'usuarios-grupos/assets/gerar-comprovante'
        arquivo.write_text('ALTERADO')
        with self.assertRaises(ValueError):
            mod.sincronizar(self.root, check=True)
        self.assertEqual(arquivo.read_text(), 'ALTERADO')
        mod.sincronizar(self.root)
        mod.sincronizar(self.root, check=True)

    def test_caminhos_invalidos_e_referencias_ausentes(self):
        for identificador in ('../fora', 'nome/com/barra', 'Aula', 'a' * 41):
            with self.subTest(id=identificador), self.assertRaises(ValueError):
                mod.criar(self.root, identificador, 'Título', 'Descrição')
        destino = self.root / 'usuarios-grupos'
        config = json.loads((destino / 'laboratorio.json').read_text())
        config['etapas'][0]['verify'] = '../comum/assets/verify-step0.sh'
        (destino / 'laboratorio.json').write_text(json.dumps(config))
        with self.assertRaises(ValueError):
            mod.sincronizar(self.root)

    def test_modelo_nao_e_cenario_publicavel_por_si_so(self):
        self.assertFalse((self.root / 'modelo/index.json').exists())
        self.assertFalse((self.root / 'comum/index.json').exists())


if __name__ == '__main__':
    unittest.main()
