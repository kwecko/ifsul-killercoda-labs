"""Reconstrução das edições comuns de linha, sem modificar o bruto."""
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'comum/assets/normalizar-registro.pl'

class NormalizarRegistroTest(unittest.TestCase):
    def converter(self, raw):
        with tempfile.NamedTemporaryFile() as source:
            source.write(raw)
            source.flush()
            result = subprocess.run(['perl', str(SCRIPT), source.name], capture_output=True)
            self.assertEqual(Path(source.name).read_bytes(), raw)
            return result

    def test_edicoes(self):
        cases = [
            ('\x1b]0;título\x07\x1b[?2004h\x1b[32mroot$ \x1b[0mecho ação\r\n', 'root$ echo ação\n'),
            ('abc\b \bd\r\n', 'abd\n'),
            ('10%\r100%\r\n', '100%\n'),
            ('abcd\x1b[2D\x1b[1@X\r\n', 'abXcd\n'),
            ('abcde\x1b[3D\x1b[1P\r\n', 'abde\n'),
            ('errado\rOK\x1b[K\r\n', 'OK\n'),
            ('antes\r\n\x1b[2J\x1b[Hdepois\r\n', 'antes\n\ndepois\n'),
            ('a\tá\x07\r\n', 'a       á\n'),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                result = self.converter(raw.encode())
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.decode(), expected)

    def test_invalid_utf8(self):
        self.assertNotEqual(self.converter(b'\xff').returncode, 0)

    def test_size_limit(self):
        self.assertNotEqual(self.converter(b'a' * 1048577).returncode, 0)
