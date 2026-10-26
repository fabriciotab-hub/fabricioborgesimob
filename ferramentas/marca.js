// Aplica a marca d'água padrão dos anúncios (monograma FB, "FABRÍCIO BORGES" e @fabricioborgescorretor,
// em branco no canto inferior direito) nas fotos de um imóvel.
// Uso: node ferramentas/marca.js ORIGEM_DIR fotos/CODIGO   (grava 01.jpg, 02.jpg ... na ordem dos nomes da origem)
// A capa (capa.jpg) não leva marca d'água; não coloque a capa na pasta de origem.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const RAIZ = path.resolve(__dirname, '..');
const MONO = fs.readFileSync(path.join(RAIZ, 'static/monograma.path'), 'utf8').trim();
const fonte = 'data:font/ttf;base64,' + fs.readFileSync(path.join(__dirname, 'fontes', 'OpenSans.ttf')).toString('base64');

function html(foto, w, h) {
  // Tamanho proporcional ao menor lado da foto (referência: 1080 px -> monograma de 120 px).
  const u = Math.min(w, h) / 1080;
  return `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face { font-family: Texto; src: url(${fonte}); }
* { margin: 0; }
body { width: ${w}px; height: ${h}px; position: relative; overflow: hidden; }
img { position: absolute; inset: 0; width: 100%; height: 100%; }
.marca { position: absolute; right: ${56 * u}px; bottom: ${44 * u}px; color: #fff; font-family: Texto;
  filter: drop-shadow(0 0 ${6 * u}px rgba(0,0,0,.6)); display: flex; flex-direction: column; align-items: flex-end; }
.topo { display: flex; align-items: center; gap: ${14 * u}px; }
svg { height: ${120 * u}px; width: ${120 * u * 441 / 469}px; }
.nome { font-size: ${22 * u}px; letter-spacing: .12em; line-height: 1.25; }
.arroba { font-size: ${20 * u}px; margin-top: ${10 * u}px; }
</style></head><body>
<img src="${foto}">
<div class="marca"><div class="topo"><svg viewBox="0 0 441 469"><path fill="#fff" fill-rule="evenodd" d="${MONO}"/></svg>
<div class="nome">FABRÍCIO<br>BORGES</div></div><div class="arroba">@fabricioborgescorretor</div></div>
</body></html>`;
}

(async () => {
  const [origem, destino] = process.argv.slice(2);
  const arquivos = fs.readdirSync(origem).filter(f => /\.jpe?g$/i.test(f)).sort();
  fs.mkdirSync(path.resolve(RAIZ, destino), { recursive: true });
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage();
  for (const [n, f] of arquivos.entries()) {
    const foto = 'data:image/jpeg;base64,' + fs.readFileSync(path.join(origem, f)).toString('base64');
    await p.setContent(`<img src="${foto}">`, { waitUntil: 'load' });
    const [w, h] = await p.evaluate(() => { const i = document.querySelector('img'); return [i.naturalWidth, i.naturalHeight]; });
    await p.setViewportSize({ width: w, height: h });
    await p.setContent(html(foto, w, h), { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    const saida = path.resolve(RAIZ, destino, String(n + 1).padStart(2, '0') + '.jpg');
    await p.screenshot({ path: saida, type: 'jpeg', quality: 88 });
    console.log(f, '->', path.relative(RAIZ, saida));
  }
  await b.close();
})();
