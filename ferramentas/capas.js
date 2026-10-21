// Gera a capa padrão (1280x1280) de cada anúncio que tem o campo "capa" em dados/imoveis.json.
// Uso: node ferramentas/capas.js [CODIGO ...]   (sem código, gera todas)
// Campos de "capa": foto (caminho da foto de fundo), local (texto grande),
// esquerda e direita (até 2 linhas cada), foco (posição da foto, ex. "50% 50%").
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const RAIZ = path.resolve(__dirname, '..');
const dados = JSON.parse(fs.readFileSync(path.join(RAIZ, 'dados/imoveis.json'), 'utf8'));
const fonte = f => 'data:font/ttf;base64,' + fs.readFileSync(path.join(__dirname, 'fontes', f)).toString('base64');
const mono = fs.readFileSync(path.join(RAIZ, 'static/monograma.svg'), 'utf8').replace(/fill="#272742"/g, 'fill="#FFFFFF"');
const esc = t => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;');

function html(c) {
  const foto = 'data:image/jpeg;base64,' + fs.readFileSync(path.join(RAIZ, c.foto)).toString('base64');
  const linhas = l => (l || []).map(t => esc(t.toUpperCase().replace(/M²/g, 'm²'))).join('<br>');
  return `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face { font-family: Julius; src: url(${fonte('JuliusSansOne-Regular.ttf')}); }
@font-face { font-family: Inter; src: url(${fonte('Inter-Regular.otf')}); font-weight: 400; }
@font-face { font-family: Inter; src: url(${fonte('Inter-Medium.otf')}); font-weight: 500; }
* { margin: 0; box-sizing: border-box; }
body { width: 1280px; height: 1280px; position: relative; overflow: hidden; background: #272742; font-family: Inter; }
.foto { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: ${c.foco || '50% 50%'}; }
.veu { position: absolute; inset: 0; background: linear-gradient(to bottom, rgba(39,39,66,.35) 0%, rgba(39,39,66,0) 22%, rgba(39,39,66,0) 48%, rgba(39,39,66,.82) 74%, rgba(26,26,46,.96) 100%); }
.marca { position: absolute; top: 56px; left: 64px; display: flex; align-items: center; gap: 18px; color: #fff; }
.marca svg { width: 52px; height: auto; }
.marca div { border-left: 1px solid rgba(255,255,255,.5); padding-left: 18px; }
.marca b { display: block; font-family: Julius; font-weight: 400; font-size: 26px; letter-spacing: .14em; }
.marca small { display: block; font-size: 13px; letter-spacing: .3em; margin-top: 4px; color: #E4DCD0; }
.base { position: absolute; left: 96px; right: 96px; bottom: 78px; color: #fff; }
.pino { display: flex; align-items: center; justify-content: center; gap: 22px; margin-bottom: 26px; }
.pino i { display: block; width: 170px; height: 2px; background: #B7A996; }
.pino svg { width: 30px; height: 40px; }
h1 { font-family: Julius; font-weight: 400; text-align: center; font-size: ${c.tamanho || 104}px; line-height: 1; letter-spacing: .04em; text-transform: uppercase; white-space: nowrap; }
.info { display: flex; justify-content: space-between; margin-top: 34px; font-size: 21px; font-weight: 500; letter-spacing: .2em; line-height: 1.6; color: #E4DCD0; }
.info div:last-child { text-align: right; }
</style></head><body>
<img class="foto" src="${foto}">
<div class="veu"></div>
<div class="marca">${mono}<div><b>FABRÍCIO BORGES</b><small>NEGÓCIOS IMOBILIÁRIOS</small></div></div>
<div class="base">
<div class="pino"><i></i><svg viewBox="0 0 24 32"><path fill="#B7A996" d="M12 0C5.4 0 0 5.3 0 11.9 0 20.8 12 32 12 32s12-11.2 12-20.1C24 5.3 18.6 0 12 0zm0 16.5a4.6 4.6 0 1 1 0-9.2 4.6 4.6 0 0 1 0 9.2z"/></svg><i></i></div>
<h1>${esc(c.local)}</h1>
<div class="info"><div>${linhas(c.esquerda)}</div><div>${linhas(c.direita)}</div></div>
</div></body></html>`;
}

(async () => {
  const pedidos = process.argv.slice(2);
  const lista = dados.imoveis.filter(i => i.capa && (!pedidos.length || pedidos.includes(i.codigo)));
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage({ viewport: { width: 1280, height: 1280 } });
  for (const i of lista) {
    await p.setContent(html(i.capa), { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    // Diminui o texto grande se não couber na largura.
    await p.evaluate(() => { const h = document.querySelector('h1'); let t = parseFloat(getComputedStyle(h).fontSize); while (h.scrollWidth > h.clientWidth && t > 40) { t -= 2; h.style.fontSize = t + 'px'; } });
    const saida = path.join(RAIZ, 'fotos', i.codigo, 'capa.jpg');
    await p.screenshot({ path: saida, type: 'jpeg', quality: 88 });
    console.log('capa gerada:', path.relative(RAIZ, saida));
  }
  await b.close();
})();
