// Instalar no Google Apps Script da conta do professor; não enviar à VM.
// BEGIN CATALOGO GERADO
const LABORATORIOS = {
  "arp": {
    "titulo": "Protocolo ARP: resolução de endereços em uma LAN comutada",
    "pasta_drive": "1a8qOKwk72bMuULU0c1Jjxr3LCXL-Xcgm",
    "recebimento_ativo": false
  },
  "particoes-linux": {
    "titulo": "Partições, sistemas de arquivos e montagem no Linux",
    "pasta_drive": "1a8qOKwk72bMuULU0c1Jjxr3LCXL-Xcgm",
    "recebimento_ativo": true
  },
  "usuarios-grupos": {
    "titulo": "Gerenciamento de Usuários e Grupos no Linux",
    "pasta_drive": "1a8qOKwk72bMuULU0c1Jjxr3LCXL-Xcgm",
    "recebimento_ativo": true
  }
};
// END CATALOGO GERADO
const RECEBIMENTO_ATIVO = true;
const LIMITE_DIARIO = 200;
const LIMITE_VERSOES = 5;
const MAX_BYTES = 4096;
const MAX_REGISTRO_BYTES = 1048576;
const MAX_PACOTE_BYTES = 1500000;

function resposta_(texto) {
  return ContentService.createTextOutput(texto).setMimeType(ContentService.MimeType.TEXT);
}

function sha256_(texto) {
  return Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, texto, Utilities.Charset.UTF_8)
    .map(b => ('0' + ((b + 256) % 256).toString(16)).slice(-2)).join('');
}

function validarTxt_(texto) {
  if (typeof texto !== 'string' || texto.length > MAX_BYTES || texto.includes('\r') || !texto.endsWith('\n')) {
    throw new Error('FORMATO_INVALIDO');
  }
  const linhas = texto.slice(0, -1).split('\n');
  const campos = ['VERSAO', 'LABORATORIO', 'MATRICULA', 'SESSAO', 'DATA', 'RESULTADO', 'CODIGO'];
  if (linhas[0] === 'VERSAO=2') campos.splice(3, 0, 'NOME');
  if (linhas.length !== campos.length) throw new Error('FORMATO_INVALIDO');
  const dados = {};
  campos.forEach((campo, i) => {
    if (!linhas[i].startsWith(campo + '=')) throw new Error('FORMATO_INVALIDO');
    dados[campo] = linhas[i].slice(campo.length + 1);
  });
  if (dados.VERSAO === '2' && (!dados.NOME || Utilities.newBlob(dados.NOME).getBytes().length > 200 || /^ | $|[\x00-\x1f\x7f]/.test(dados.NOME))) throw new Error('FORMATO_INVALIDO');
  if (!['1', '2'].includes(dados.VERSAO) || (!Object.prototype.hasOwnProperty.call(LABORATORIOS, dados.LABORATORIO) || !LABORATORIOS[dados.LABORATORIO].recebimento_ativo) || dados.RESULTADO !== 'CONCLUIDO' ||
      !/^[A-Za-z0-9][A-Za-z0-9._]{0,31}$/.test(dados.MATRICULA) ||
      !/^[0-9a-fA-F]{8}(-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}$/.test(dados.SESSAO) ||
      !/^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$/.test(dados.DATA) ||
      !/^SHA256:[0-9a-f]{64}$/.test(dados.CODIGO)) throw new Error('FORMATO_INVALIDO');
  const data = new Date(dados.DATA);
  if (dados.DATA.startsWith('0000-') || isNaN(data.getTime()) || data.toISOString() !== dados.DATA.replace('Z', '.000Z')) {
    throw new Error('FORMATO_INVALIDO');
  }
  if (dados.CODIGO !== 'SHA256:' + sha256_(linhas.slice(0, -1).join('\n') + '\n')) throw new Error('HASH_INVALIDO');
  dados.nome = dados.LABORATORIO + '_' + dados.MATRICULA + '_' + dados.SESSAO + '.txt';
  return dados;
}

function doGet() {
  return resposta_('Receptor de comprovantes. Envie o TXT via POST.');
}

function hashBytes_(bytes) {
  return Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, bytes)
    .map(b => ('0' + ((b + 256) % 256).toString(16)).slice(-2)).join('');
}

function decodificar_(valor, limite) {
  if (typeof valor !== 'string' || valor.length > Math.ceil(limite / 3) * 4 ||
      !/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(valor)) throw new Error('FORMATO_INVALIDO');
  const bytes = Utilities.base64Decode(valor);
  if (!bytes.length || bytes.length > limite || Utilities.base64Encode(bytes) !== valor) throw new Error('FORMATO_INVALIDO');
  return bytes;
}

function pacote_(e) {
  if (!e || !e.postData || e.contentLength > MAX_PACOTE_BYTES || e.postData.length > MAX_PACOTE_BYTES ||
      typeof e.postData.contents !== 'string' || e.postData.contents.length > MAX_PACOTE_BYTES) throw new Error('FORMATO_INVALIDO');
  const tipo = e.postData.type || '';
  let texto, registro;
  if (/^application\/json(?:;|$)/i.test(tipo)) {
    let pacote;
    try { pacote = JSON.parse(e.postData.contents); } catch (_) { throw new Error('FORMATO_INVALIDO'); }
    if (!pacote || pacote.versao !== 2 || Object.keys(pacote).sort().join(',') !== 'comprovante,registro,versao') throw new Error('FORMATO_INVALIDO');
    texto = Utilities.newBlob(decodificar_(pacote.comprovante, MAX_BYTES)).getDataAsString('UTF-8');
    registro = decodificar_(pacote.registro, MAX_REGISTRO_BYTES);
  } else if (/^text\/plain(?:;|$)/i.test(tipo)) {
    // Compatibilidade com os clientes anteriores, que enviam apenas o TXT.
    texto = e.postData.contents;
  } else { throw new Error('FORMATO_INVALIDO'); }
  const dados = validarTxt_(texto);
  const arquivos = [];
  let confirmacao = 'OK\nARQUIVO=' + dados.nome + '\nCODIGO=' + dados.CODIGO;
  if (registro) {
    const nome = dados.nome.slice(0, -4) + '_' + dados.CODIGO.slice(7) + '_historico.log';
    const hash = hashBytes_(registro);
    arquivos.push({nome: nome, blob: Utilities.newBlob(registro, 'text/plain', nome), tamanho: registro.length, hash: hash, historico: true});
    confirmacao += '\nREGISTRO=' + nome + '\nREGISTRO_SHA256=' + hash;
  }
  arquivos.push({nome: dados.nome, blob: Utilities.newBlob(texto, 'text/plain', dados.nome), tamanho: Utilities.newBlob(texto).getBytes().length, hash: sha256_(texto), historico: false});
  return {arquivos: arquivos, confirmacao: confirmacao, pasta: LABORATORIOS[dados.LABORATORIO].pasta_drive};
}

function doPost(e) {
  let lock;
  try {
    if (!RECEBIMENTO_ATIVO) return resposta_('ERRO=RECEBIMENTO_ENCERRADO');
    const pacote = pacote_(e);
    lock = LockService.getScriptLock();
    if (!lock.tryLock(5000)) return resposta_('ERRO=OCUPADO');
    const pasta = DriveApp.getFolderById(pacote.pasta);
    const pendentes = [];
    for (const item of pacote.arquivos) {
      const existentes = pasta.getFilesByName(item.nome);
      let versoes = 0, igual = false;
      while (existentes.hasNext()) {
        const arquivo = existentes.next();
        versoes++;
        if (arquivo.getSize() === item.tamanho && hashBytes_(arquivo.getBlob().getBytes()) === item.hash) igual = true;
      }
      if (igual) continue;
      // Não troca o histórico já associado a uma emissão.
      if (item.historico && versoes > 0) return resposta_('ERRO=HISTORICO_DIVERGENTE');
      if (versoes >= LIMITE_VERSOES) return resposta_('ERRO=LIMITE_VERSOES');
      pendentes.push(item);
    }
    if (!pendentes.length) return resposta_(pacote.confirmacao);
    const props = PropertiesService.getScriptProperties();
    const hoje = Utilities.formatDate(new Date(), 'UTC', 'yyyy-MM-dd');
    const estado = JSON.parse(props.getProperty('LIMITE_UPLOADS') || '{}');
    const total = estado.dia === hoje ? Number(estado.total) : 0;
    if (!Number.isFinite(total) || total < 0 || total >= LIMITE_DIARIO) return resposta_('ERRO=LIMITE_DIARIO');
    // Cota por tentativa de entrega; falhas de Drive também consomem uma tentativa.
    props.setProperty('LIMITE_UPLOADS', JSON.stringify({dia: hoje, total: total + 1}));
    // Histórico primeiro. Se a segunda gravação falhar, o reenvio completa o par.
    for (const item of pendentes) pasta.createFile(item.blob);
    return resposta_(pacote.confirmacao);
  } catch (erro) {
    const mensagem = ['FORMATO_INVALIDO', 'HASH_INVALIDO'].includes(erro.message) ? erro.message : 'FALHA_INTERNA';
    return resposta_('ERRO=' + mensagem);
  } finally {
    if (lock && lock.hasLock()) lock.releaseLock();
  }
}
