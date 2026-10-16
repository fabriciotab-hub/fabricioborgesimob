# Site Fabricio Borges · Negócios Imobiliários

Site estático de fabricioborgesimob.com.br.

- `dados/imoveis.json`: lista de imóveis (cada um vira uma página).
- `fotos/CODIGO/1.jpg ...`: fotos de cada imóvel (caminhos listados em `fotos` no JSON).
- `static/`: estilo, script e ícone.
- `python3 build.py`: gera o site pronto em `docs/` (publicado pelo GitHub Pages).

Imóveis com `"exemplo": true` são fictícios e mostram um aviso de prévia no topo.
