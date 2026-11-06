# Site Fabricio Borges · Negócios Imobiliários

Site estático de fabricioborgesimob.com.br.

- `dados/imoveis.json`: lista de imóveis (cada um vira uma página).
- `fotos/CODIGO/1.jpg ...`: fotos de cada imóvel (caminhos listados em `fotos` no JSON).
- `static/`: estilo, script e ícone.
- `python3 build.py`: gera o site pronto em `docs/` (publicado pelo GitHub Pages).

Imóveis com `"exemplo": true` são fictícios e mostram um aviso de prévia no topo.

Capa dos anúncios: feita no Canva a partir de uma cópia do modelo "Capa VP" (fonte Metanoia),
exportada em JPG e salva em `fotos/CODIGO/capa.jpg`. No JSON, `"capa": {"canva": "<id do design>", ...}`.
O `build.py` põe a capa como primeira foto. `ferramentas/capas.js` só gera capa automática para quem não tem `canva`.

Novidades (nov/2026):
- `"vendido": true` no imóvel: mostra o selo "Vendido", troca o preço por "Vendido", leva o anúncio para o fim da lista e o WhatsApp passa a pedir "um imóvel parecido".
- `dados/depoimentos.json`: depoimentos reais, com autorização do cliente. Lista vazia esconde a seção na home e no Sobre.
- Guias (`GUIAS` no `build.py`) viram páginas em `guias/` e entram no sitemap.
- Medição: todo clique que abre o WhatsApp vira o evento `contato_whatsapp` (origem e código do imóvel). Preencha `GA4_ID` e `GOOGLE_ADS_CONVERSAO` no `build.py` para ver no Analytics e contar conversão no Google Ads.
