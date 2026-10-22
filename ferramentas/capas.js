// Gera a capa padrão (1280x1280) de cada anúncio que tem o campo "capa" em dados/imoveis.json.
// Uso: node ferramentas/capas.js [CODIGO ...]   (sem código, gera todas)
// Imóveis com "canva" em "capa" usam a capa feita no Canva (cópia do modelo "Capa VP")
// e salva em fotos/CODIGO/capa.jpg; este script não mexe nelas.
// Campos de "capa": foto (caminho da foto de fundo), local (texto grande),
// esquerda e direita (até 2 linhas cada), foco (posição da foto, ex. "50% 50%").
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const RAIZ = path.resolve(__dirname, '..');
const dados = JSON.parse(fs.readFileSync(path.join(RAIZ, 'dados/imoveis.json'), 'utf8'));
const fonte = f => 'data:font/ttf;base64,' + fs.readFileSync(path.join(__dirname, 'fontes', f)).toString('base64');
const esc = t => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;');

function html(c) {
  // Padrão oficial: segue a capa "Arniqueira" feita pelo Fabricio (out/2026).
  const foto = 'data:image/jpeg;base64,' + fs.readFileSync(path.join(RAIZ, c.foto)).toString('base64');
  const linhas = l => (l || []).map(t => esc(t.toUpperCase().replace(/M²/g, 'm²'))).join('<br>');
  return `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face { font-family: Titulo; src: url(${fonte('Italiana-Regular.ttf')}); }
@font-face { font-family: Texto; src: url(${fonte('OpenSans.ttf')}); }
* { margin: 0; box-sizing: border-box; }
body { width: 1280px; height: 1280px; position: relative; overflow: hidden; background: #1E1D19; }
.foto { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: ${c.foco || '50% 50%'}; }
.veu { position: absolute; inset: 0; background: linear-gradient(to bottom, rgba(30,29,25,0) 0%, rgba(30,29,25,0) 66%, rgba(30,29,25,.75) 82%, rgba(30,29,25,.97) 90%, #1E1D19 100%); }
.base { position: absolute; left: 0; right: 0; bottom: 60px; display: flex; justify-content: center; }
.bloco { display: flex; flex-direction: column; color: #F9F8F4; }
.pino { display: flex; align-items: center; justify-content: center; gap: 22px; height: 46px; }
.pino i { display: block; width: 180px; height: 4px; border-radius: 2px; background: #F9F8F4; }
.pino svg { width: 30px; height: 46px; }
h1 { font-family: Titulo; font-weight: 400; text-align: center; font-size: ${c.tamanho || 112}px; line-height: 1.05; letter-spacing: .02em; text-transform: uppercase; white-space: nowrap; margin-top: 4px; }
.info { display: flex; justify-content: space-between; gap: 40px; margin-top: 8px; padding: 0 4px; font-family: Texto; font-size: 20px; letter-spacing: .01em; line-height: 1.45; }
.info div:last-child { text-align: right; }
</style></head><body>
<img class="foto" src="${foto}">
<div class="veu"></div>
<div class="base"><div class="bloco">
<div class="pino"><i></i><svg viewBox="0 0 30 46"><ellipse cx="15" cy="40" rx="7.5" ry="3" fill="none" stroke="#F9F8F4" stroke-width="2"/><path fill="#F9F8F4" d="M15 2C8 2 2.5 7.5 2.5 14.3 2.5 23.5 15 39 15 39s12.5-15.5 12.5-24.7C27.5 7.5 22 2 15 2z"/><circle cx="15" cy="14.3" r="8.2" fill="#F38049"/></svg><i></i></div>
<h1>${esc(c.local)}</h1>
<div class="info"><div>${linhas(c.esquerda)}</div><div>${linhas(c.direita)}</div></div>
</div></div></body></html>`;
}

(async () => {
  const pedidos = process.argv.slice(2);
  const lista = dados.imoveis.filter(i => i.capa && !i.capa.canva && (!pedidos.length || pedidos.includes(i.codigo)));
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage({ viewport: { width: 1280, height: 1280 } });
  for (const i of lista) {
    await p.setContent(html(i.capa), { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    // Diminui o texto grande se não couber na largura.
    await p.evaluate(() => { const h = document.querySelector('h1'); let t = parseFloat(getComputedStyle(h).fontSize); while (h.getBoundingClientRect().width > 1100 && t > 40) { t -= 2; h.style.fontSize = t + 'px'; } });
    const saida = path.join(RAIZ, 'fotos', i.codigo, 'capa.jpg');
    await p.screenshot({ path: saida, type: 'jpeg', quality: 88 });
    console.log('capa gerada:', path.relative(RAIZ, saida));
  }
  await b.close();
})();
