// Aplica a marca d'água padrão dos anúncios nas fotos de um imóvel: só o monograma FB, em branco,
// pequeno e centralizado, no estilo clean dos primeiros anúncios (preferência do Fabricio, out/2026).
// Uso: node ferramentas/marca.js ORIGEM_DIR fotos/CODIGO   (grava 01.jpg, 02.jpg ... na ordem dos nomes da origem)
// A capa (capa.jpg) não leva marca d'água; não coloque a capa na pasta de origem.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const RAIZ = path.resolve(__dirname, '..');
const MONO = fs.readFileSync(path.join(RAIZ, 'static/monograma.path'), 'utf8').trim();

function html(foto, w, h) {
  // Monograma com ~6% do menor lado da foto (60 px numa foto de 960 px).
  const alt = Math.min(w, h) * 0.065;
  return `<!doctype html><html><head><meta charset="utf-8"><style>
* { margin: 0; }
body { width: ${w}px; height: ${h}px; position: relative; overflow: hidden; }
img { position: absolute; inset: 0; width: 100%; height: 100%; }
svg { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); height: ${alt}px; width: ${alt * 441 / 469}px;
  opacity: .85; filter: drop-shadow(0 0 ${alt * .04}px rgba(0,0,0,.35)); }
</style></head><body>
<img src="${foto}">
<svg viewBox="0 0 441 469"><path fill="#fff" fill-rule="evenodd" d="${MONO}"/></svg>
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
    const saida = path.resolve(RAIZ, destino, String(n + 1).padStart(2, '0') + '.jpg');
    await p.screenshot({ path: saida, type: 'jpeg', quality: 88 });
    console.log(f, '->', path.relative(RAIZ, saida));
  }
  await b.close();
})();
