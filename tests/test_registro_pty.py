"""Teste de terminal real no Ubuntu via Docker; não envia arquivos à internet."""
import os
from pathlib import Path
import pty
import select
import subprocess
import time
import uuid

root = Path(__file__).resolve().parents[1]
name = 'lab-registro-test-' + uuid.uuid4().hex[:12]
master, slave = pty.openpty()
setup = '''install -d /usr/local/lib/laboratorio
install -m 755 /lab/usuarios-grupos/assets/verify-step0.sh /usr/local/lib/laboratorio/
install -m 755 /lab/usuarios-grupos/assets/identificar-aluno /lab/usuarios-grupos/assets/iniciar-registro /usr/local/bin/
identificar-aluno
identificar-aluno
'''
process = subprocess.Popen(['docker', 'run', '--rm', '-it', '--name', name, '-e', 'TERM=dumb',
                            '-v', str(root) + ':/lab:ro', '-w', '/root', 'ubuntu:24.04', 'bash', '-c', setup],
                           stdin=slave, stdout=slave, stderr=slave, close_fds=True)
os.close(slave)
buffer = b''

def wait_for(token):
    global buffer
    end = time.monotonic() + 25
    while token not in buffer:
        if time.monotonic() > end:
            raise AssertionError('Terminal não respondeu: ' + repr(token) + '\n' + repr(buffer[-1500:]))
        if select.select([master], [], [], 0.2)[0]:
            buffer += os.read(master, 65536)
    _, buffer = buffer.split(token, 1)


def send(command):
    os.write(master, command.encode() + b'\n')


def log():
    return subprocess.check_output(['docker', 'exec', name, 'bash', '-c', 'cat /root/registros/*.log'])


try:
    wait_for(b'Informe sua matr')
    send('000000000')
    wait_for(b'# ')
    send("printf 'REGISTRO_ROOT_OK\\n'")
    wait_for(b'\r\nREGISTRO_ROOT_OK\r\n')
    send('identificar-aluno')
    wait_for('A gravação já está ativa'.encode())
    wait_for(b'# ')
    send('useradd -m -s /bin/bash julia; su - julia')
    wait_for(b'$ ')
    send("printf 'REGISTRO_JULIA_OK\\n'")
    wait_for(b'\r\nREGISTRO_JULIA_OK\r\n')
    send('exit')
    wait_for(b'# ')
    send("read -r -s -p 'TESTE_SENHA: ' SEGREDO; unset SEGREDO; printf '\\nSENHA_LIDA\\n'")
    wait_for(b'\r\nTESTE_SENHA: ')
    send('SEGREDO_NAO_DEVE_SER_GRAVADO_9x')
    wait_for(b'\r\nSENHA_LIDA\r\n')
    wait_for(b'# ')
    before = log()
    assert b'REGISTRO_ROOT_OK\r\n' in before
    assert b'REGISTRO_JULIA_OK\r\n' in before
    assert b'SEGREDO_NAO_DEVE_SER_GRAVADO_9x' not in before
    assert before.count(b'Script started on') == 1
    send('exit')
    wait_for('Gravação encerrada'.encode())
    wait_for(b'# ')
    send("printf 'REGISTRO_RETOMADO_OK\\n'")
    wait_for(b'\r\nREGISTRO_RETOMADO_OK\r\n')
    wait_for(b'# ')
    after = log()
    assert b'REGISTRO_ROOT_OK\r\n' in after
    assert b'REGISTRO_RETOMADO_OK\r\n' in after
    assert after.count(b'Script started on') == 2
    send('exit')
    process.wait(timeout=15)
    assert process.returncode == 0
    print('OK: identificação inicia gravação; root e julia registrados; senha oculta ausente; sem gravação aninhada; retomada preserva histórico.')
finally:
    subprocess.run(['docker', 'rm', '-f', name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if process.poll() is None:
        process.terminate()
        process.wait(timeout=10)
    os.close(master)
