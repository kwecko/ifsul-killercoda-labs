// Instalar no Google Apps Script da conta do professor; não enviar à VM.
const PASTA_ID = '1a8qOKwk72bMuULU0c1Jjxr3LCXL-Xcgm';
const RECEBIMENTO_ATIVO = true;
const LIMITE_DIARIO = 200;
const LIMITE_VERSOES = 5;
const MAX_BYTES = 4096;

function resposta_(texto) {
  return ContentService.createTextOutput(texto).setMimeType(ContentService.MimeType.TEXT);
}

function sha256_(texto) {
  return Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, texto, Utilities.Charset.UTF_8)
    .map(b => ('0' + ((b + 256) % 256).toString(16)).slice(-2)).join('');
}

function validarTxt_(texto) {
  if (typeof texto !== 'string' || texto.length > MAX_BYTES || /[^\x00-\x7f]/.test(texto) || texto.includes('\r') || !texto.endsWith('\n')) {
    throw new Error('FORMATO_INVALIDO');
  }
  const linhas = texto.slice(0, -1).split('\n');
  const campos = ['VERSAO', 'LABORATORIO', 'MATRICULA', 'SESSAO', 'DATA', 'RESULTADO', 'CODIGO'];
  if (linhas.length !== 7) throw new Error('FORMATO_INVALIDO');
  const dados = {};
  campos.forEach((campo, i) => {
    if (!linhas[i].startsWith(campo + '=')) throw new Error('FORMATO_INVALIDO');
    dados[campo] = linhas[i].slice(campo.length + 1);
  });
  if (dados.VERSAO !== '1' || dados.LABORATORIO !== 'usuarios-grupos' || dados.RESULTADO !== 'CONCLUIDO' ||
      !/^[0-9]{1,32}$/.test(dados.MATRICULA) ||
      !/^[0-9a-fA-F]{8}(-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}$/.test(dados.SESSAO) ||
      !/^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$/.test(dados.DATA) ||
      !/^SHA256:[0-9a-f]{64}$/.test(dados.CODIGO)) throw new Error('FORMATO_INVALIDO');
  const data = new Date(dados.DATA);
  if (dados.DATA.startsWith('0000-') || isNaN(data.getTime()) || data.toISOString() !== dados.DATA.replace('Z', '.000Z')) {
    throw new Error('FORMATO_INVALIDO');
  }
  if (dados.CODIGO !== 'SHA256:' + sha256_(linhas.slice(0, 6).join('\n') + '\n')) throw new Error('HASH_INVALIDO');
  dados.nome = 'usuarios-grupos_' + dados.MATRICULA + '_' + dados.SESSAO + '.txt';
  return dados;
}

function doGet() {
  return resposta_('Receptor de comprovantes. Envie o TXT via POST.');
}

function doPost(e) {
  let lock;
  try {
    if (!RECEBIMENTO_ATIVO) return resposta_('ERRO=RECEBIMENTO_ENCERRADO');
    if (!e || !e.postData || e.contentLength > MAX_BYTES || e.postData.length > MAX_BYTES ||
        !/^text\/plain(?:;|$)/i.test(e.postData.type || '')) return resposta_('ERRO=FORMATO_INVALIDO');
    const texto = e.postData.contents;
    const dados = validarTxt_(texto);
    lock = LockService.getScriptLock();
    if (!lock.tryLock(5000)) return resposta_('ERRO=OCUPADO');
    const pasta = DriveApp.getFolderById(PASTA_ID);
    const existentes = pasta.getFilesByName(dados.nome);
    let versoes = 0;
    while (existentes.hasNext()) {
      const arquivo = existentes.next();
      versoes++;
      // Repetir o mesmo envio não cria uma nova cópia.
      if (arquivo.getSize() <= MAX_BYTES && arquivo.getBlob().getDataAsString('UTF-8') === texto) {
        return resposta_('OK\nARQUIVO=' + dados.nome + '\nCODIGO=' + dados.CODIGO);
      }
    }
    if (versoes >= LIMITE_VERSOES) return resposta_('ERRO=LIMITE_VERSOES');
    const props = PropertiesService.getScriptProperties();
    const hoje = Utilities.formatDate(new Date(), 'UTC', 'yyyy-MM-dd');
    const estado = JSON.parse(props.getProperty('LIMITE_UPLOADS') || '{}');
    const total = estado.dia === hoje ? Number(estado.total) : 0;
    if (!Number.isFinite(total) || total < 0 || total >= LIMITE_DIARIO) return resposta_('ERRO=LIMITE_DIARIO');
    // Reserva a cota antes da gravação: falhas de Drive também consomem uma tentativa.
    props.setProperty('LIMITE_UPLOADS', JSON.stringify({dia: hoje, total: total + 1}));
    pasta.createFile(Utilities.newBlob(texto, 'text/plain', dados.nome));
    // Não expõe links, IDs, conteúdo alheio nem altera compartilhamento da pasta.
    return resposta_('OK\nARQUIVO=' + dados.nome + '\nCODIGO=' + dados.CODIGO);
  } catch (erro) {
    const mensagem = ['FORMATO_INVALIDO', 'HASH_INVALIDO'].includes(erro.message) ? erro.message : 'FALHA_INTERNA';
    return resposta_('ERRO=' + mensagem);
  } finally {
    if (lock && lock.hasLock()) lock.releaseLock();
  }
}
