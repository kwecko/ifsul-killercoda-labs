import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('validar_comprovante', ROOT / 'professor/validar_comprovante.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

PAYLOAD = (
    b'VERSAO=1\nLABORATORIO=usuarios-grupos\nMATRICULA=202612345\n'
    b'SESSAO=550e8400-e29b-41d4-a716-446655440000\n'
    b'DATA=2026-09-11T18:30:00Z\nRESULTADO=CONCLUIDO\n'
)
VETOR = PAYLOAD + b'CODIGO=SHA256:f8697dc31a6e836d509bc0edaf6051ef45840c10de36e142eb18b83578a0937f\n'


def com_hash(payload):
    return payload + b'CODIGO=SHA256:' + hashlib.sha256(payload).hexdigest().encode('ascii') + b'\n'


class ValidacaoTests(unittest.TestCase):
    def test_vetor_documentado(self):
        self.assertEqual(mod.validar(VETOR)['MATRICULA'], '202612345')
        self.assertIn(VETOR.decode(), (ROOT / 'docs/comprovante-v1.md').read_text())

    def test_edicao_sem_recalculo(self):
        with self.assertRaisesRegex(mod.ComprovanteInvalido, 'SHA-256 divergente'):
            mod.validar(VETOR.replace(b'202612345', b'999999999'))

    def test_edicao_com_recalculo_expoe_limite_de_confianca(self):
        self.assertEqual(mod.validar(com_hash(PAYLOAD.replace(b'202612345', b'999999999')))['MATRICULA'], '999999999')

    def test_zeros_iniciais(self):
        self.assertEqual(mod.validar(com_hash(PAYLOAD.replace(b'202612345', b'00202612345')))['MATRICULA'], '00202612345')

    def test_uuid_maiusculo(self):
        mod.validar(com_hash(PAYLOAD.replace(b'550e8400-e29b-41d4-a716-446655440000', b'550E8400-E29B-41D4-A716-446655440000')))

    def test_serializacao_invalida(self):
        for dados in (VETOR.replace(b'\n', b'\r\n'), b'\xef\xbb\xbf' + VETOR,
                      VETOR[:-1], VETOR + b'\n', VETOR + b'EXTRA=1\n',
                      VETOR.replace(b'MATRICULA', b'\xff'), VETOR.replace(b'VERSAO=1', b'VERSAO=1 '), b''):
            with self.subTest(dados=dados[:40]), self.assertRaises(mod.ComprovanteInvalido):
                mod.validar(dados)

    def test_campos_invalidos_mesmo_com_hash_correto(self):
        casos = [(b'VERSAO=1', b'VERSAO=2'), (b'LABORATORIO=usuarios-grupos', b'LABORATORIO=outro'),
                 (b'RESULTADO=CONCLUIDO', b'RESULTADO=PENDENTE'), (b'202612345', b'abc'),
                 (b'202612345', '１２３'.encode()), (b'550e8400-e29b-41d4-a716-446655440000', b'UG-A72F91C3'),
                 (b'2026-09-11T18:30:00Z', b'2026-02-30T18:30:00Z'),
                 (b'2026-09-11T18:30:00Z', b'2026-09-11T25:30:00Z'),
                 (b'2026-09-11T18:30:00Z', b'2026-09-11T18:30:00-03:00'),
                 (b'MATRICULA=', b'VERSAO='), (b'MATRICULA=', b'OUTRO=')]
        for antes, depois in casos:
            with self.subTest(depois=depois), self.assertRaises(mod.ComprovanteInvalido):
                mod.validar(com_hash(PAYLOAD.replace(antes, depois)))
        linhas = PAYLOAD.splitlines(keepends=True)
        linhas[0], linhas[1] = linhas[1], linhas[0]
        with self.assertRaises(mod.ComprovanteInvalido):
            mod.validar(com_hash(b''.join(linhas)))

    def test_codigo_invalido(self):
        for dados in (VETOR.replace(b'SHA256:', b'MD5:'), VETOR[:-2] + b'\n',
                      PAYLOAD + VETOR[len(PAYLOAD):].upper()):
            with self.subTest(dados=dados), self.assertRaises(mod.ComprovanteInvalido):
                mod.validar(dados)

    def executar(self, args):
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            retorno = mod.main(args)
        return retorno, saida.getvalue()

    def test_cli_nome_matricula_e_lote(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / 'renomeado.txt'
            arquivo.write_bytes(VETOR)
            codigo, texto = self.executar([str(arquivo)])
            self.assertEqual(codigo, 0)
            self.assertIn('Aviso: nome diferente', texto)
            self.assertEqual(self.executar(['--conferir-nome', str(arquivo)])[0], 1)
            self.assertEqual(self.executar(['--matricula', '202612345', str(arquivo)])[0], 0)
            self.assertEqual(self.executar(['--matricula', '0202612345', str(arquivo)])[0], 1)
            esperado = arquivo.with_name('usuarios-grupos_202612345_550e8400-e29b-41d4-a716-446655440000.txt')
            arquivo.rename(esperado)
            self.assertEqual(self.executar(['--conferir-nome', str(esperado)])[0], 0)
            arquivo.write_text('invalido')
            codigo, texto = self.executar([str(arquivo), str(esperado), str(Path(pasta) / 'ausente.txt')])
            self.assertEqual(codigo, 1)
            self.assertIn('1 consistente(s); 2 inválido(s)', texto)
            self.assertEqual(esperado.read_bytes(), VETOR)

    def test_cli_erro_de_argumentos(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as erro:
            mod.main(['--matricula', 'abc', 'arquivo.txt'])
        self.assertEqual(erro.exception.code, 2)

    def test_nao_incluido_no_cenario(self):
        cenario = ROOT / 'usuarios-grupos'
        config = json.loads((cenario / 'index.json').read_text())
        for asset in config['details']['assets']['host01']:
            for arquivo in (cenario / 'assets').glob(asset['file']):
                self.assertNotIn('professor', arquivo.parts)
                self.assertNotEqual(arquivo.name, 'validar_comprovante.py')
        self.assertNotIn('professor', json.dumps(config))
        self.assertFalse((ROOT / 'professor/index.json').exists())


if __name__ == '__main__':
    unittest.main()
