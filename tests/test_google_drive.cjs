const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../professor/google-drive/Code.gs'), 'utf8');
const payload = 'VERSAO=1\nLABORATORIO=usuarios-grupos\nMATRICULA=202612345\nSESSAO=550e8400-e29b-41d4-a716-446655440000\nDATA=2026-09-11T18:30:00Z\nRESULTADO=CONCLUIDO\n';
const receipt = p => p + 'CODIGO=SHA256:' + crypto.createHash('sha256').update(p).digest('hex') + '\n';
function setup(code = source) {
  const files = [], props = {}, state = {locked: false, busy: false, fail: false, reads: 0};
  const context = vm.createContext({
    ContentService: {MimeType: {TEXT: 'text/plain'}, createTextOutput: text => ({text, setMimeType() {return this;}})},
    Utilities: {
      DigestAlgorithm: {SHA_256: 'sha256'}, Charset: {UTF_8: 'utf8'},
      computeDigest: (algorithm, text) => Array.from(crypto.createHash('sha256').update(text).digest()).map(b => b > 127 ? b - 256 : b),
      formatDate: () => '2026-09-11', newBlob: (text, mime, name) => ({text, mime, name})
    },
    PropertiesService: {getScriptProperties: () => ({getProperty: key => props[key], setProperty: (key, value) => {props[key] = value;}})},
    LockService: {getScriptLock: () => ({tryLock: () => state.locked = !state.busy, hasLock: () => state.locked, releaseLock: () => {state.locked = false;}})},
    DriveApp: {getFolderById: id => {
      assert.equal(id, '1a8qOKwk72bMuULU0c1Jjxr3LCXL-Xcgm'); state.reads++;
      return {
        getFilesByName: name => {
          const matches = files.filter(f => f.name === name); let i = 0;
          return {hasNext: () => i < matches.length, next: () => {
            const f = matches[i++]; return {getSize: () => Buffer.byteLength(f.text), getBlob: () => ({getDataAsString: () => f.text})};
          }};
        },
        createFile: blob => {if (state.fail) throw Error('erro privado'); files.push(blob);}
      };
    }}
  });
  new vm.Script(code).runInContext(context);
  const post = (text, type = 'text/plain; charset=utf-8') => context.doPost({contentLength: Buffer.byteLength(text), postData: {contents: text, type, length: Buffer.byteLength(text)}}).text;
  return {post, files, props, state, context};
}
let count = 0;
function test(name, fn) {fn(); count++; console.log('OK: ' + name);}
test('grava TXT original e confirma nome e hash', () => {
  const s = setup(), txt = receipt(payload); const reply = s.post(txt);
  assert.equal(reply, 'OK\nARQUIVO=usuarios-grupos_202612345_550e8400-e29b-41d4-a716-446655440000.txt\n' + txt.trimEnd().split('\n').at(-1));
  assert.equal(s.files[0].text, txt); assert.equal(s.files[0].mime, 'text/plain'); assert.equal(s.state.locked, false);
});
test('reenvio idêntico não duplica nem consome nova cota', () => {
  const s = setup(), txt = receipt(payload); s.post(txt); const props = JSON.stringify(s.props);
  assert.equal(s.post(txt).split('\n')[0], 'OK'); assert.equal(s.files.length, 1); assert.equal(JSON.stringify(s.props), props);
});
test('rejeita edição, campos inválidos, tamanho e MIME', () => {
  const s = setup();
  const invalid = [receipt(payload).replace('202612345', '999999999'), receipt(payload).replaceAll('\n', '\r\n'),
    receipt(payload.replace('2026-09-11', '2026-02-30')), receipt(payload.replace('usuarios-grupos', 'outro')),
    receipt(payload.replace('202612345', '1'.repeat(33))), 'x'.repeat(4097), receipt(payload) + '\n'];
  for (const txt of invalid) assert.match(s.post(txt), /^ERRO=/);
  assert.equal(s.post(receipt(payload), 'application/json'), 'ERRO=FORMATO_INVALIDO');
  assert.equal(s.files.length, 0); assert.equal(s.state.reads, 0);
});
test('recalcular hash não prova autoria', () => {assert.match(setup().post(receipt(payload.replace('202612345', '999999999'))), /^OK\n/);});
test('preserva versões e limita a cinco', () => {
  const s = setup();
  for (let i = 0; i < 5; i++) assert.match(s.post(receipt(payload.replace('18:30:00', '18:30:0' + i))), /^OK\n/);
  assert.equal(s.post(receipt(payload.replace('18:30:00', '18:30:05'))), 'ERRO=LIMITE_VERSOES');
  assert.equal(s.files.length, 5);
});
test('cota diária e virada do dia', () => {
  const s = setup(); s.props.LIMITE_UPLOADS = JSON.stringify({dia: '2026-09-11', total: 200});
  assert.equal(s.post(receipt(payload)), 'ERRO=LIMITE_DIARIO');
  s.props.LIMITE_UPLOADS = JSON.stringify({dia: '2026-09-10', total: 200});
  assert.match(s.post(receipt(payload)), /^OK\n/);
});
test('Drive indisponível não confirma e libera lock', () => {
  const s = setup(); s.state.fail = true;
  assert.equal(s.post(receipt(payload)), 'ERRO=FALHA_INTERNA'); assert.equal(s.files.length, 0); assert.equal(s.state.locked, false);
});
test('concorrência ocupada não grava', () => {
  const s = setup(); s.state.busy = true;
  assert.equal(s.post(receipt(payload)), 'ERRO=OCUPADO'); assert.equal(s.state.reads, 0);
});
test('recebimento encerrado não acessa Drive', () => {
  const s = setup(source.replace('RECEBIMENTO_ATIVO = true', 'RECEBIMENTO_ATIVO = false'));
  assert.equal(s.post(receipt(payload)), 'ERRO=RECEBIMENTO_ENCERRADO'); assert.equal(s.state.reads, 0);
});
test('GET não expõe pasta nem entregas', () => {
  const s = setup(); assert.equal(s.context.doGet().text, 'Receptor de comprovantes. Envie o TXT via POST.'); assert.equal(s.state.reads, 0);
});
console.log(`${count} testes do receptor passaram (serviços Google simulados).`);
