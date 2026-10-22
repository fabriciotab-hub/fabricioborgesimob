#!/usr/bin/env python3
"""Gera o site estático em ./docs a partir de dados/imoveis.json.

Uso: python3 build.py
Sem dependências além do Python 3.
"""
import html
import json
import shutil
from datetime import date
from pathlib import Path
import re
from urllib.parse import quote

RAIZ = Path(__file__).parent
SAIDA = RAIZ / "docs"
DOMINIO = "https://fabricioborgesimob.com.br"
WHATS = "5561995620101"
WHATS_TXT = "(61) 99562-0101"
CRECI = "CRECI/DF 27547"
MARCA = "Fabrício Borges"
INSTAGRAM = "fabricioborgescorretor"
# Endereço do canal no YouTube, ex.: "https://www.youtube.com/@fabricioborgescorretor". Vazio esconde o link.
YOUTUBE = "https://www.youtube.com/@FabricioBorgesCorretorIm-sb5mb"
# Endereço do perfil no TikTok, ex.: "https://www.tiktok.com/@fabricioborgescorretor". Vazio esconde o link.
TIKTOK = "https://www.tiktok.com/@fabricioborgescorretor"
LINKEDIN = "https://www.linkedin.com/in/fabricio-teixeira-43273960"
MARCA_SUB = "Negócios Imobiliários"

TIPOS = ["Casa", "Apartamento", "Lote", "Área residencial", "Área comercial", "Comércio", "Chácara", "Fazenda"]

REGIOES = {
    "vicente-pires": {
        "busca": "Casas e lotes à venda em Vicente Pires, DF",
        "nome": "Vicente Pires",
        "curto": "Casas e lotes amplos, com ruas em regularização: mostro a situação de cada um.",
        "texto": "Vicente Pires tem casas em lotes grandes, ruas cada vez mais urbanizadas e preço por metro quadrado abaixo de Águas Claras. Parte da região ainda está em regularização com a Terracap, por isso cada anúncio aqui mostra a situação do documento antes da visita.",
    },
    "joquei": {
        "busca": "Casas em condomínio à venda no Jóquei, Vicente Pires, DF",
        "nome": "Jóquei",
        "curto": "Casas em condomínio com terrenos grandes, perto de Vicente Pires.",
        "texto": "O Jóquei reúne condomínios horizontais com terrenos grandes e clima de chácara, a poucos minutos de Vicente Pires e da EPTG. É uma boa escolha para quem quer espaço e segurança de condomínio.",
    },
    "arniqueira": {
        "busca": "Casas e lotes à venda em Arniqueira, DF",
        "nome": "Arniqueira",
        "curto": "Lotes e casas em uma região em crescimento, ao lado de Águas Claras.",
        "texto": "Arniqueira é a região administrativa mais nova do DF e cresce ao lado de Águas Claras. Tem lotes e casas novas com bom custo, e boa parte dos imóveis está em processo de regularização.",
    },
    "aguas-claras": {
        "busca": "Apartamentos à venda em Águas Claras, DF",
        "nome": "Águas Claras",
        "curto": "Apartamentos com lazer completo e metrô perto de casa.",
        "texto": "Águas Claras concentra apartamentos com lazer completo, comércio a pé e estações de metrô. Os imóveis são escriturados e aceitam financiamento bancário normalmente.",
    },
    "outras-regioes": {
        "busca": "Imóveis à venda em Brasília e outras regiões do DF",
        "nome": "Outras regiões do DF",
        "curto": "Tem um imóvel em outra região de Brasília? Também atendo, é só me chamar.",
        "texto": "Meu foco é Vicente Pires, Jóquei, Arniqueira e Águas Claras, mas também atendo quem quer vender ou comprar em outras regiões de Brasília. O cuidado é o mesmo: avaliação, documentação conferida e acompanhamento até a escritura.",
        "acoes": True,
        "h1": "Imóveis em outras regiões do DF",
        "rodape": "Outras regiões do DF",
        "card": "Outras regiões",
        "cta": "Fale comigo",
    },
    "aguas-lindas": {
        "busca": "Casas e lotes à venda em Águas Lindas de Goiás",
        "nome": "Águas Lindas de Goiás",
        "uf": "GO",
        "curto": "Casas e lotes com bom custo no Entorno do DF, pela BR-070.",
        "texto": "Águas Lindas de Goiás fica no Entorno do DF, pela BR-070, e tem casas e lotes com preço mais acessível que em Brasília. Como no DF, confiro a documentação de cada imóvel antes da visita.",
    },
    "valparaiso": {
        "busca": "Casas e apartamentos à venda em Valparaíso de Goiás",
        "nome": "Valparaíso de Goiás",
        "uf": "GO",
        "curto": "Casas e apartamentos no Entorno Sul, pela BR-040.",
        "texto": "Valparaíso de Goiás fica no Entorno Sul do DF, pela BR-040, com casas, apartamentos e comércio completo. Confiro a documentação de cada imóvel antes da visita.",
    },
    "jardim-inga": {
        "busca": "Casas e lotes à venda no Jardim Ingá, Luziânia, GO",
        "nome": "Jardim Ingá",
        "uf": "GO",
        "curto": "Casas e lotes no distrito de Luziânia, pela BR-040.",
        "texto": "O Jardim Ingá é um distrito de Luziânia, na BR-040, entre Valparaíso e Luziânia, com casas e lotes de bom custo. Confiro a documentação de cada imóvel antes da visita.",
    },
    "luziania": {
        "busca": "Casas, lotes e chácaras à venda em Luziânia, GO",
        "nome": "Luziânia",
        "uf": "GO",
        "curto": "Casas, lotes e chácaras em uma das maiores cidades do Entorno.",
        "texto": "Luziânia é uma das maiores cidades do Entorno do DF, pela BR-040, com casas, lotes e chácaras. Confiro a documentação de cada imóvel antes da visita.",
    },
    "padre-bernardo": {
        "busca": "Chácaras e fazendas à venda em Padre Bernardo, GO",
        "nome": "Padre Bernardo",
        "uf": "GO",
        "curto": "Chácaras, fazendas e lotes ao norte do DF, pela BR-080.",
        "texto": "Padre Bernardo fica ao norte do DF, pela BR-080, e tem chácaras, fazendas e lotes com bastante espaço. Confiro a documentação de cada imóvel antes da visita.",
    },
    "algarve": {
        "busca": "Imóveis no Algarve, Portugal, para brasileiros investirem",
        "nome": "Algarve",
        "uf": "PT",
        "em": "no Algarve",
        "curto": "Lançamentos e oportunidades de alto padrão no sul de Portugal, para investir ou morar.",
        "texto": "Por meio de uma parceria luso-brasileira com um corretor estabelecido no Algarve, apresento a brasileiros imóveis e oportunidades de investimento no sul de Portugal, com praias, golfe e um mercado em valorização. Você fala comigo, em português do Brasil, e a intermediação em Portugal é feita pelo parceiro, licenciado no país.",
        "h1": "Imóveis à venda no Algarve, Portugal",
        "card": "Algarve · Portugal",
        "rodape": "Algarve, Portugal",
    },
}

UFS = {"DF": "Distrito Federal", "GO": "Goiás", "PT": "Portugal"}
PAISES = {"PT": "Portugal"}


def uf(reg):
    return reg.get("uf", "DF")


def local(reg):
    """Cidade e estado para textos e mapas: 'Vicente Pires, Brasília, DF' ou 'Luziânia, GO'."""
    if uf(reg) in PAISES:
        return f"{reg['nome']}, {PAISES[uf(reg)]}"
    return f"{reg['nome']}, Brasília, DF" if uf(reg) == "DF" else f"{reg['nome']}, {uf(reg)}"


def em_regiao(reg):
    return reg.get("em", "em " + reg["nome"])


def por_uf():
    return [(u, nome, [(s, v) for s, v in REGIOES.items() if uf(v) == u]) for u, nome in UFS.items()]

DOCS = {
    "escriturado": {
        "rotulo": "Escriturado",
        "cor": "#1F7A4D",
        "resumo": "Matrícula em cartório. Aceita financiamento bancário normalmente.",
        "texto": "Este imóvel tem escritura e matrícula registradas em cartório. A compra pode ser financiada pelos bancos e a transferência é feita direto no cartório.",
    },
    "regularizacao": {
        "rotulo": "Em regularização",
        "cor": "#C98A0C",
        "resumo": "Área em processo com a Terracap. A escritura sai ao fim do processo.",
        "texto": "Este imóvel está em uma área em regularização com a Terracap. Hoje a venda é feita por cessão de direitos, e a escritura sai quando o processo da área terminar. Eu explico o passo a passo e o que muda no pagamento.",
    },
    "cessao": {
        "rotulo": "Cessão de direitos",
        "cor": "#6B7A72",
        "resumo": "Venda por contrato de cessão. Pagamento normalmente à vista.",
        "texto": "A venda deste imóvel é feita por contrato de cessão de direitos, sem escritura no momento. Normalmente o pagamento é à vista ou combinado com o vendedor. Antes da proposta eu levanto toda a documentação disponível com você.",
    },
    "lancamento": {
        "rotulo": "Lançamento",
        "cor": "#272742",
        "resumo": "Imóvel na planta, com incorporação registrada em cartório.",
        "texto": "Este é um lançamento na planta, com memorial de incorporação registrado em cartório. A compra é feita direto com a construtora, com entrada e parcelas durante a obra, e o restante pode ser financiado na entrega das chaves. Eu explico a tabela e as condições de pagamento.",
        "secao": False,
    },
    "portugal": {
        "rotulo": "Portugal · Algarve",
        "titulo": "Compra em Portugal, com parceiro licenciado",
        "cor": "#272742",
        "resumo": "Imóvel em Portugal, intermediado por corretor parceiro licenciado no país.",
        "texto": "Este imóvel fica em Portugal. A intermediação da venda em Portugal é feita pelo meu parceiro, corretor licenciado no país, e eu acompanho você daqui, em português do Brasil, do primeiro contato até a escritura. As condições, a documentação e os impostos de compra (IMT e Imposto do Selo) são confirmados com o parceiro antes da proposta.",
        "secao": False,
    },
}

E = html.escape


def brl(v):
    if v is None:
        return "Preço sob consulta"
    return "R$ " + f"{v:,.0f}".replace(",", ".")


def preco(i, v=None):
    """Valor do imóvel na moeda dele (campo "moeda": "EUR" para Portugal)."""
    v = i["preco"] if v is None else v
    if i.get("moeda") == "EUR" and v is not None:
        return "€ " + f"{v:,.0f}".replace(",", ".")
    return brl(v)


def wa(msg=None):
    return f"https://wa.me/{WHATS}" + (f"?text={quote(msg)}" if msg else "")


MONO_D = (RAIZ / "static/monograma.path").read_text().strip()


def monograma(altura, cor="currentColor", classe=""):
    largura = round(altura * 441 / 469, 1)
    return (f'<svg class="{classe}" aria-hidden="true" width="{largura}" height="{altura}" viewBox="0 0 441 469">'
            f'<path fill="{cor}" fill-rule="evenodd" d="{MONO_D}"/></svg>')


ICONE_YT = '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2.5" y="5" width="19" height="14" rx="4"/><path d="M10 9.2v5.6l4.8-2.8z" fill="currentColor" stroke="none"/></svg>'


def youtube_id(url):
    m = re.search(r"(?:youtu\.be/|v=|/shorts/|/embed/|/live/)([A-Za-z0-9_-]{11})", url or "")
    return m.group(1) if m else None


ICONE_TT = '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M16.6 5.8A4.3 4.3 0 0 1 15.5 3h-3.1v12.4a2.6 2.6 0 1 1-2.6-2.6c.3 0 .5 0 .8.1V9.7a5.7 5.7 0 1 0 4.9 5.7V9a7.4 7.4 0 0 0 4.3 1.4V7.3a4.3 4.3 0 0 1-3.2-1.5z"/></svg>'
ICONE_IN = '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M4.5 3.5a2 2 0 1 1 0 4 2 2 0 0 1 0-4zM3 9h3v12H3zM9 9h2.9v1.7h.1a3.2 3.2 0 0 1 2.9-1.6c3 0 3.6 2 3.6 4.6V21h-3v-6.5c0-1.5 0-3.5-2.1-3.5S10.9 12.7 10.9 14.4V21H9z"/></svg>'
ICONE_INSTA = '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>'
ICONE_WHATS = '<svg aria-hidden="true" width="{s}" height="{s}" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.7-1.4.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6a2.7 2.7 0 0 0 1.8-1.2 2.2 2.2 0 0 0 .1-1.2c0-.1-.2-.2-.5-.3z"/></svg>'
ICONE_FOTO = '<svg aria-hidden="true" width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="10" r="2"/><path d="M21 16l-5-5-8 8"/></svg>'
ICONE_PESSOA = '<svg aria-hidden="true" width="72" height="72" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3"><circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6"/></svg>'


def m2(v):
    return f"{v:g}".replace(".", ",")


def specs_curtas(i):
    partes = []
    if i.get("area"):
        partes.append(f"{m2(i['area'])} m²")
    elif i.get("lote"):
        partes.append(f"lote {i['lote']} m²")
    if i.get("quartos_texto"):
        partes.append(i["quartos_texto"])
    elif i.get("quartos"):
        partes.append(f"{i['quartos']} quarto{'s' if i['quartos'] > 1 else ''}")
    if i.get("vagas"):
        partes.append(f"{i['vagas']} vaga{'s' if i['vagas'] > 1 else ''}")
    if i.get("area") and i.get("lote"):
        partes.append(f"lote {i['lote']} m²")
    return " · ".join(partes)


def foco(i):
    return f' style="object-position:{E(i["capa_foco"])}"' if i.get("capa_foco") else ""


def foto_capa(i, r):
    if i.get("fotos"):
        return f'<img src="{r}{E(i["fotos"][0])}" alt="{E(i["titulo"])}" loading="lazy"{foco(i)}>'
    return ICONE_FOTO


def card(i, r):
    d = DOCS[i["documento"]]
    reg = REGIOES[i["regiao"]]["nome"]
    attrs = (
        f'data-tipo="{E(i["tipo"])}" data-regiao="{i["regiao"]}" data-preco="{i["preco"] or 0}" '
        f'data-quartos="{i.get("quartos") or 0}" data-doc="{i["documento"]}" '
        f'data-area="{i.get("area") or i.get("lote") or 0}" data-ordem="{i["_ordem"]}"'
    )
    return f"""<a class="card" href="{r}imoveis/{i['codigo']}.html" {attrs}>
<div class="card-foto">{foto_capa(i, r)}<span class="selo selo-{i['documento']}">{d['rotulo']}</span>{'<span class="selo selo-video">' + ICONE_YT + ' Vídeo</span>' if youtube_id(i.get("video")) else ''}</div>
<div class="card-corpo">
<span class="preco">{preco(i)}</span>
<span class="card-titulo">{E(i['titulo'])}</span>
<span class="card-local">{E(reg)} · {E(i['tipo'])}</span>
<span class="card-specs">{specs_curtas(i)}</span>
<span class="codigo">Código {i['codigo']}</span>
</div>
</a>"""


def ld_script(*objs):
    return "\n".join(f'<script type="application/ld+json">{json.dumps(o, ensure_ascii=False)}</script>' for o in objs)


def trilha_ld(passos):
    """Caminho de navegação para o Google mostrar no resultado da busca."""
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": n + 1, "name": nome, "item": f"{DOMINIO}/{c}"} for n, (nome, c) in enumerate(passos)
        ],
    }


def layout(r, titulo, descricao, corpo, ativo="", caminho="", tem_exemplo=False, extra_head="", imagem="static/img/fabricio-retrato.jpg", indexar=True):
    canonical = f"{DOMINIO}/{caminho}"
    robots = "" if indexar else '<meta name="robots" content="noindex">\n'
    menu = [
        ("imoveis.html", "Comprar", "comprar"),
        ("index.html#regioes", "Regiões", "regioes"),
        ("investidores.html", "Investidores", "investidores"),
        ("anuncie.html", "Anuncie seu imóvel", "anuncie"),
        ("sobre.html", "Sobre", "sobre"),
    ]
    links = "\n".join(
        f'<a href="{r}{h}"{" aria-current=\"page\"" if k == ativo else ""}>{t}</a>' for h, t, k in menu
    )
    aviso = (
        '<div class="aviso-previa">Prévia do site: os imóveis mostrados são exemplos fictícios.</div>'
        if tem_exemplo else ""
    )
    yt_rodape = f'<li><a href="{E(YOUTUBE)}" rel="noopener">{ICONE_YT} Canal no YouTube</a></li>' if YOUTUBE else ""
    if TIKTOK:
        yt_rodape += f'<li><a href="{E(TIKTOK)}" rel="noopener">{ICONE_TT} TikTok</a></li>'
    if LINKEDIN:
        yt_rodape += f'<li><a href="{E(LINKEDIN)}" rel="noopener">{ICONE_IN} LinkedIn</a></li>'
    regioes_rodape = "".join(
        f'<li><a href="{r}regioes/{s}.html">{E(v.get("rodape", "Imóveis em " + v["nome"]))}</a></li>' for s, v in REGIOES.items()
    )
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(titulo)}</title>
<meta name="description" content="{E(descricao)}">
{robots}<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{MARCA} · {MARCA_SUB}">
<meta property="og:title" content="{E(titulo)}">
<meta property="og:description" content="{E(descricao)}">
<meta property="og:url" content="{canonical}">
<meta property="og:locale" content="pt_BR">
<meta property="og:image" content="{DOMINIO}/{E(imagem)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#272742">
<link rel="icon" href="{r}static/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Julius+Sans+One&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{r}static/style.css">
{extra_head}
</head>
<body>
{aviso}
<header class="topo">
<div class="wrap">
<a class="marca" href="{r}index.html" aria-label="{MARCA}, página inicial">
<span class="marca-icone">{monograma(44)}</span>
<span class="marca-texto"><span class="marca-nome">{MARCA}</span><span class="marca-sub">{MARCA_SUB}</span></span>
</a>
<nav class="menu" aria-label="Principal">
{links}
<a class="btn btn-azul btn-pilula" href="{wa('Olá Fabrício, vim pelo site e gostaria de falar sobre imóveis.')}">{ICONE_WHATS.format(s=18)} WhatsApp</a>
</nav>
</div>
</header>
<main>
{corpo}
</main>
<footer class="rodape">
<div class="wrap">
<div class="rodape-marca">{monograma(56, classe="rodape-mono")}<div><strong>{MARCA}</strong><br>{MARCA_SUB}<br>Corretor de imóveis · {CRECI}<br>Brasília, DF</div></div>
<div><strong>Contato</strong><ul><li><a href="{wa()}">WhatsApp {WHATS_TXT}</a></li><li><a href="https://instagram.com/{INSTAGRAM}" rel="noopener">{ICONE_INSTA} @{INSTAGRAM}</a></li>{yt_rodape}</ul></div>
<div><ul>{regioes_rodape}</ul></div>
<div><ul><li><a href="{r}investidores.html">Lançamentos para investidores</a></li><li><a href="{r}anuncie.html">Anuncie seu imóvel</a></li><li><a href="{r}privacidade.html">Política de privacidade</a></li></ul></div>
</div>
</footer>
<a class="whats-flutuante" href="{wa('Olá Fabrício, vim pelo site e gostaria de falar sobre imóveis.')}" aria-label="Falar no WhatsApp">{ICONE_WHATS.format(s=30)}</a>
<script src="{r}static/app.js" defer></script>
</body>
</html>
"""


def form_busca(r, regiao_sel=""):
    opts_reg = "".join(
        f'<optgroup label="{nome}">' + "".join(
            f'<option value="{s}"{" selected" if s == regiao_sel else ""}>{E(v["nome"])}</option>' for s, v in regs
        ) + "</optgroup>"
        for _, nome, regs in por_uf()
    )
    return f"""<form class="busca" action="{r}imoveis.html" method="get" aria-label="Buscar imóveis">
<label class="campo">Tipo<select name="tipo"><option value="">Todos</option>{"".join(f"<option>{t}</option>" for t in TIPOS)}</select></label>
<label class="campo">Região<select name="regiao"><option value="">Todas as regiões</option>{opts_reg}</select></label>
<label class="campo">Preço até<select name="ate"><option value="">Qualquer valor</option><option value="500000">R$ 500 mil</option><option value="800000">R$ 800 mil</option><option value="1200000">R$ 1,2 milhão</option><option value="2000000">R$ 2 milhões</option></select></label>
<label class="campo">Quartos<select name="quartos"><option value="">Qualquer</option><option value="1">1+</option><option value="2">2+</option><option value="3">3+</option><option value="4">4+</option></select></label>
<label class="check"><input type="checkbox" name="esc" value="1"> Só escriturados</label>
<button class="btn btn-areia" type="submit">Buscar imóveis</button>
</form>"""


def secao_docs():
    itens = "".join(
        f'<div><strong><span class="ponto" style="background:{d["cor"]}"></span>{d["rotulo"]}</strong><small>{d["resumo"]}</small></div>'
        for d in DOCS.values() if d.get("secao", True)
    )
    return f"""<section class="faixa-azul">
<div class="wrap">
<div style="flex:1 1 420px">
<h2 style="font-size:clamp(26px,3.4vw,32px)">Saiba a situação do documento antes de visitar</h2>
<p>Em Vicente Pires, no Jóquei e em Arniqueira, parte dos imóveis ainda está em regularização. Cada anúncio mostra se o imóvel é escriturado, está em regularização com a Terracap ou é vendido por cessão de direitos.</p>
</div>
<div class="lista-docs">{itens}</div>
</div>
</section>"""


def secao_sobre(r, completa=False):
    extra = ""
    foto = f'<div class="foto-corretor"><img src="{r}static/img/fabricio.jpg" alt="{MARCA}, corretor de imóveis" width="200" height="200"></div>'
    if completa:
        foto = f'<div class="foto-retrato"><img src="{r}static/img/fabricio-retrato.jpg" alt="{MARCA}, corretor de imóveis" width="360" height="540"></div>'
    if completa:
        extra = """<p>Trabalho só com venda. Isso me deixa focado em uma coisa: ajudar quem quer comprar a encontrar o imóvel certo, com a documentação entendida, e ajudar quem quer vender a chegar no preço justo com segurança.</p>
<p>Antes de cada visita eu explico a situação do documento, os custos de transferência e as opções de pagamento, para você decidir com calma.</p>
<p>Para quem vai financiar, conto com a parceria da <a href="https://cvtcorrespondente.com.br/" rel="noopener" style="color:var(--areia);font-weight:600">CVT Correspondente Bancário</a>, que analisa o crédito em vários bancos e cuida do processo até a assinatura.</p>"""
    return f"""<section class="sobre" id="sobre">
<div class="wrap">
{foto}
<div class="sobre-texto">
<h2 style="font-size:clamp(26px,3.4vw,32px)">{MARCA}, corretor de imóveis</h2>
<p>{CRECI}. Especialista em venda de imóveis em Vicente Pires, Jóquei, Arniqueira e Águas Claras.</p>
{extra}
<div><a class="btn btn-azul" href="{wa('Olá Fabrício, vim pelo site e gostaria de falar sobre imóveis.')}">{ICONE_WHATS.format(s=18)} Falar comigo no WhatsApp</a></div>
</div>
</div>
</section>"""


PARCEIRO = {
    "nome": "CVT Correspondente Bancário",
    "frase": "Crédito imobiliário com estratégia, segurança e alto padrão.",
    "servico": "Análise de crédito em vários bancos ao mesmo tempo, uso do FGTS e acompanhamento do pedido até a assinatura do contrato.",
    "whats": "https://wa.me/5561984390099?text=" + quote("Olá, vim pelo site do corretor Fabrício Borges e quero simular um financiamento."),
    "whats_txt": "(61) 98439-0099",
    "site": "https://cvtcorrespondente.com.br/",
    "instagram": "https://www.instagram.com/cvtoficial/",
}


def selo_parceiro():
    return '<span class="cvt-marca" aria-hidden="true"><b>CVT</b><small>Correspondente<br>Bancário</small></span>'


def secao_financiamento():
    p = PARCEIRO
    return f"""<section class="secao financiamento" id="financiamento">
<div class="wrap">
<div class="fin-caixa">
<div class="fin-texto">
<span class="sobretitulo">Parceria</span>
<h2>Financiamento facilitado</h2>
<p>Para quem vai financiar, trabalho em parceria com a <strong>{p['nome']}</strong>. {p['frase']} {p['servico']}</p>
<div class="fin-botoes">
<a class="btn btn-areia" href="{p['whats']}" rel="noopener">{ICONE_WHATS.format(s=18)} Simular com a CVT</a>
<a class="btn btn-contorno-claro" href="{p['site']}" rel="noopener">Conhecer a CVT</a>
</div>
<p class="fin-contato">WhatsApp {p['whats_txt']} · <a href="{p['instagram']}" rel="noopener">@cvtoficial</a></p>
</div>
{selo_parceiro()}
</div>
</div>
</section>"""


def secao_simulador_anuncie(r):
    return f"""<section class="secao">
<div class="wrap duas">
<div class="caixa" id="simulador">
<h2>Quanto posso financiar?</h2>
<p class="sub" style="margin:0">Uma conta rápida para saber a faixa de preço certa antes de procurar.</p>
<div class="linha-campos">
<label class="campo">Renda familiar mensal<input id="sim-renda" inputmode="numeric" value="15.000"></label>
<label class="campo">Entrada disponível<input id="sim-entrada" inputmode="numeric" value="150.000"></label>
</div>
<button class="btn btn-azul" type="button" id="sim-botao">Simular</button>
<div class="resultado" id="sim-resultado" hidden aria-live="polite"></div>
<p class="nota">Estimativa com parcela de até 30% da renda, 35 anos e juros de 11% ao ano. Imóveis em regularização ou cessão de direitos não costumam aceitar financiamento bancário.</p>
</div>
<div class="caixa caixa-areia" id="anuncie">
<div style="display:flex;flex-direction:column;gap:12px">
<h2>Quer vender seu imóvel?</h2>
<p style="color:var(--texto-2);line-height:1.6">Faço a avaliação, as fotos e a divulgação no site e nos portais. Você acompanha cada visita.</p>
</div>
<a class="btn btn-escuro" href="{r}anuncie.html">Anunciar meu imóvel</a>
</div>
</div>
</section>"""


def pagina_inicial(imoveis, tem_exemplo):
    r = ""
    destaques = [i for i in imoveis if i.get("destaque")][:3] or imoveis[:3]
    cards = "\n".join(card(i, r) for i in destaques)
    reg_cards = "\n".join(
        f'<a class="regiao-card" href="regioes/{s}.html"><strong>{E(v.get("card", v["nome"]))}</strong><span>{E(v["curto"])}</span><em>{v.get("cta", "Ver imóveis")}</em></a>'
        for s, v in REGIOES.items() if uf(v) in ("DF", "PT")
    )
    corpo = f"""<section class="hero">
{monograma(520, classe="hero-mono")}
<div class="wrap">
<div style="display:flex;flex-direction:column;gap:16px">
<span class="sobretitulo">Venda de imóveis no DF, Entorno e Portugal</span>
<h1>Casas, lotes e apartamentos em Vicente Pires, Jóquei, Arniqueira e Águas Claras</h1>
<p class="lead">Um corretor que conhece cada rua da região, com a situação do documento de cada imóvel explicada antes da visita. E, para quem quer investir ou morar fora, <a href="investidores.html" style="color:inherit;font-weight:600">lançamentos e oportunidades no Algarve, Portugal</a>.</p>
</div>
{form_busca(r)}
</div>
</section>
<section class="secao" id="regioes">
<div class="wrap">
<div class="secao-cabeca"><h2>Onde eu atuo</h2></div>
<div class="regioes">{reg_cards}</div>
</div>
</section>
<section class="secao" style="padding-top:0">
<div class="wrap">
<div class="secao-cabeca"><h2>Imóveis em destaque</h2><a href="imoveis.html" style="font-weight:700">Ver todos os imóveis</a></div>
<div class="grade">{cards}</div>
</div>
</section>
{secao_docs()}
{secao_simulador_anuncie(r)}
{secao_financiamento()}
{secao_sobre(r)}"""
    ld = {
        "@context": "https://schema.org",
        "@type": "RealEstateAgent",
        "name": f"{MARCA} · {MARCA_SUB}",
        "url": DOMINIO,
        "telephone": "+55 61 99562-0101",
        "sameAs": [f"https://instagram.com/{INSTAGRAM}"] + [u for u in (YOUTUBE, TIKTOK, LINKEDIN) if u],
        "areaServed": [local(v) for k, v in REGIOES.items() if k != "outras-regioes"] + ["Distrito Federal"],
        "address": {"@type": "PostalAddress", "addressLocality": "Brasília", "addressRegion": "DF", "addressCountry": "BR"},
        "image": f"{DOMINIO}/static/img/fabricio-retrato.jpg",
        "logo": f"{DOMINIO}/static/monograma.svg",
        "description": "Corretor de imóveis em Brasília, com venda de casas, lotes e apartamentos em Vicente Pires, Jóquei, Arniqueira, Águas Claras, Entorno do DF e Algarve, Portugal.",
        "knowsLanguage": "pt-BR",
        "identifier": CRECI,
        "employee": {"@type": "Person", "name": "Fabrício Borges", "jobTitle": "Corretor de imóveis", "identifier": CRECI},
    }
    site = {"@context": "https://schema.org", "@type": "WebSite", "name": f"{MARCA} · {MARCA_SUB}", "url": f"{DOMINIO}/", "inLanguage": "pt-BR"}
    head = ld_script(ld, site)
    return layout(
        r,
        f"Imóveis à venda em Vicente Pires, Arniqueira e Águas Claras · {MARCA}, corretor no DF",
        f"Corretor de imóveis em Brasília ({CRECI}): casas, lotes e apartamentos à venda em Vicente Pires, Jóquei, Arniqueira e Águas Claras, no Entorno do DF e no Algarve, Portugal. Documentação explicada antes da visita.",
        corpo, "", "", tem_exemplo, head,
    )


def lista_com_filtros(r, imoveis, regiao_fixa=None):
    cards = "\n".join(card(i, r) for i in imoveis)
    if regiao_fixa:
        filtro_reg = f'<input type="hidden" name="regiao" value="{regiao_fixa}">'
    else:
        checks = "".join(
            f'<span class="filtro-uf">{nome}</span>' + "".join(
                f'<label class="check" style="font-weight:500"><input type="checkbox" name="regiao" value="{s}"> {E(v["nome"])}</label>'
                for s, v in regs
            )
            for _, nome, regs in por_uf()
        )
        filtro_reg = f'<fieldset><legend>Região</legend>{checks}</fieldset>'
    return f"""<div class="busca-layout" data-busca>
<form class="filtros" aria-label="Filtros" onsubmit="return false">
{filtro_reg}
<fieldset><legend>Tipo</legend>
<div class="pilulas">
<button type="button" class="pilula" data-tipo="" aria-pressed="true">Todos</button>
{"".join(f'<button type="button" class="pilula" data-tipo="{t}" aria-pressed="false">{t}</button>' for t in TIPOS)}
</div></fieldset>
<label class="campo">Preço até<select name="ate"><option value="">Qualquer valor</option><option value="500000">R$ 500 mil</option><option value="800000">R$ 800 mil</option><option value="1200000">R$ 1,2 milhão</option><option value="2000000">R$ 2 milhões</option></select></label>
<label class="campo">Quartos<select name="quartos"><option value="">Qualquer</option><option value="1">1+</option><option value="2">2+</option><option value="3">3+</option><option value="4">4+</option></select></label>
<label class="check" style="background:var(--fundo-2);border-radius:10px;padding:8px 12px"><input type="checkbox" name="esc" value="1"> Só escriturados</label>
</form>
<div class="resultados">
<div class="barra-resultados">
<p><strong data-total>{len(imoveis)}</strong> imóveis encontrados</p>
<label class="campo" style="flex-direction:row;align-items:center;gap:8px;font-weight:500">Ordenar por
<select name="ordem" style="width:auto"><option value="recentes">Mais recentes</option><option value="menor">Menor preço</option><option value="maior">Maior preço</option><option value="area">Maior área</option></select></label>
</div>
<div class="grade" data-lista>{cards}</div>
<div class="vazio" data-vazio hidden>Nenhum imóvel com esses filtros agora. Ajuste a busca ou peça um alerta abaixo.</div>
<div class="alerta">
<div><strong style="font-size:18px">Não achou o que procura?</strong><br><span style="color:var(--texto-2)">Me conte o que você quer e eu aviso no WhatsApp quando aparecer.</span></div>
<a class="btn btn-areia" href="{wa('Olá Fabrício, estou procurando um imóvel e queria receber opções. Procuro: ')}">Criar alerta no WhatsApp</a>
</div>
</div>
</div>"""


def pagina_busca(imoveis, tem_exemplo):
    r = ""
    corpo = f"""<div class="busca-pagina"><div class="wrap">
<div style="display:flex;flex-direction:column;gap:8px;margin-bottom:24px">
<h1 style="font-size:clamp(28px,4vw,36px)">Imóveis à venda</h1>
<p style="color:var(--texto-2)">Vicente Pires, Jóquei, Arniqueira e Águas Claras</p>
</div>
{lista_com_filtros(r, imoveis)}
</div></div>"""
    return layout(r, f"Imóveis à venda no DF, Entorno e Algarve · {MARCA}", "Casas, lotes, apartamentos e pontos comerciais à venda em Vicente Pires, Jóquei, Arniqueira, Águas Claras, outras regiões de Brasília, Entorno do DF e Algarve, com filtro por preço, quartos e situação do documento.", corpo, "comprar", "imoveis.html", tem_exemplo)


def pagina_regiao(slug, imoveis, tem_exemplo):
    r = "../"
    reg = REGIOES[slug]
    doms = [i for i in imoveis if i["regiao"] == slug]
    acoes = ""
    if reg.get("acoes"):
        acoes = (f'<div style="display:flex;flex-wrap:wrap;gap:12px;margin-top:8px">'
                 f'<a class="btn btn-azul" href="../anuncie.html">Quero vender meu imóvel</a>'
                 f'<a class="btn btn-contorno" href="{wa("Olá Fabrício, procuro um imóvel em outra região de Brasília: ")}">Quero comprar em outra região</a></div>')
    corpo = f"""<div class="busca-pagina"><div class="wrap">
<nav class="trilha" aria-label="Caminho" style="padding-top:0"><a href="../index.html">Início</a><span aria-hidden="true">/</span><span>{E(reg['nome'])}</span></nav>
<div style="display:flex;flex-direction:column;gap:12px;margin-bottom:28px;max-width:820px">
<h1 style="font-size:clamp(28px,4vw,38px)">{E(reg.get("h1", "Imóveis à venda em " + reg["nome"]))}</h1>
<p style="color:var(--texto-2);font-size:18px;line-height:1.6">{E(reg['texto'])}</p>
{acoes}
</div>
{lista_com_filtros(r, doms, slug) if doms else '<div class="vazio">Nenhum imóvel anunciado aqui agora. <a href="' + wa('Olá Fabrício, procuro imóvel em ' + reg['nome'] + '.') + '">Me chame no WhatsApp</a> e eu aviso quando aparecer.</div>'}
</div></div>"""
    head = ld_script(trilha_ld([("Início", ""), (reg["nome"], f"regioes/{slug}.html")]))
    desc = f"{reg['busca']}. {reg['curto']} Corretor {MARCA}, {CRECI}."
    return layout(r, f"{reg['busca']} · {MARCA}", desc, corpo, "regioes", f"regioes/{slug}.html", tem_exemplo, head)


def pagina_imovel(i, tem_exemplo):
    r = "../"
    d = DOCS[i["documento"]]
    reg = REGIOES[i["regiao"]]
    msg = f"Olá Fabrício, tenho interesse no imóvel {i['codigo']} ({i['titulo']})."
    fotos = i.get("fotos") or []
    rotulos = ["Foto principal", "Sala", "Cozinha", "Quarto", "Área externa"]
    cel = []
    for n in range(5):
        if n < len(fotos):
            cel.append(f'<div><img src="{r}{E(fotos[n])}" alt="{E(i["titulo"])}, foto {n + 1}" loading="{"eager" if n == 0 else "lazy"}"{foco(i) if n == 0 else ""}></div>')
        else:
            cel.append(f"<div>{rotulos[n]}</div>")
    if len(fotos) > 1:
        cel.append(f'<button type="button" class="ver-fotos" data-abrir-fotos>Ver as {len(fotos)} fotos</button>')
    todas = "".join(f'<img src="{r}{E(f)}" alt="{E(i["titulo"])}, foto {n + 1}" loading="lazy">' for n, f in enumerate(fotos))
    janela_fotos = (f'<dialog class="fotos-todas" data-fotos aria-label="Fotos do imóvel {i["codigo"]}">'
                    f'<button type="button" class="fechar-fotos" data-fechar-fotos>Fechar</button>{todas}</dialog>') if len(fotos) > 1 else ""
    specs = []
    if i.get("area"):
        specs.append(("Área" if i["tipo"] == "Comércio" else "Área construída", f"{m2(i['area'])} m²"))
    if i.get("lote"):
        specs.append(("Lote", f"{i['lote']} m²"))
    if i.get("quartos_texto"):
        specs.append(("Quartos", i["quartos_texto"]))
    elif i.get("quartos"):
        q = f"{i['quartos']}"
        if i.get("suites") and i["suites"] == i["quartos"]:
            q = f"{i['suites']} suíte{'s' if i['suites'] > 1 else ''}"
        elif i.get("suites"):
            q += f" ({i['suites']} suíte{'s' if i['suites'] > 1 else ''})"
        specs.append(("Quartos", q))
    if i.get("vagas"):
        specs.append(("Vagas", str(i["vagas"])))
    specs += [tuple(x) for x in i.get("specs", [])]
    specs_html = "".join(f"<div><span>{a}</span><strong>{b}</strong></div>" for a, b in specs)
    tags = "".join(f"<span>{E(t)}</span>" for t in i.get("itens", []))
    custos = []
    if i.get("condominio"):
        custos.append(("Condomínio", f"{preco(i, i['condominio'])}/mês"))
    if i.get("iptu_ano"):
        custos.append(("IPTU", f"{preco(i, i['iptu_ano'])}/ano"))
    custos_html = "".join(f"<div><span>{a}</span><b>{b}</b></div>" for a, b in custos)
    vid = youtube_id(i.get("video"))
    if vid:
        mais = f'<a href="{E(YOUTUBE)}" rel="noopener" style="font-weight:600">{ICONE_YT} Ver mais vídeos no meu canal</a>' if YOUTUBE else ""
        secao_video = (f'<section style="display:flex;flex-direction:column;gap:12px"><h2>Vídeo do imóvel</h2>'
                       f'<div class="video{" vertical" if "/shorts/" in (i.get("video") or "") else ""}"><iframe src="https://www.youtube-nocookie.com/embed/{vid}" title="Vídeo do imóvel {i['codigo']}" loading="lazy" allow="accelerometer; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>'
                       f'<p style="font-size:15px;color:var(--texto-2)"><a href="https://www.youtube.com/watch?v={vid}" rel="noopener">Assistir no YouTube</a></p>{mais}</section>')
    elif YOUTUBE:
        secao_video = f'<p><a href="{E(YOUTUBE)}" rel="noopener" style="font-weight:600">{ICONE_YT} Veja os vídeos dos imóveis no meu canal do YouTube</a></p>'
    else:
        secao_video = ""
    aviso_fin = ""
    if i["documento"] == "escriturado" or "financ" in (i.get("descricao") or "").lower() and "não aceita financ" not in (i.get("descricao") or "").lower():
        aviso_fin = (f'<p class="aviso-fin">Financiamento facilitado com a <strong>{PARCEIRO["nome"]}</strong>, parceira. '
                     f'<a href="{PARCEIRO["whats"]}" rel="noopener">Simular no WhatsApp</a></p>')
    mapa_q = quote(i.get("mapa") or local(reg))
    corpo = f"""<div class="wrap">
<nav class="trilha" aria-label="Caminho"><a href="../imoveis.html">Imóveis à venda</a><span aria-hidden="true">/</span><a href="../regioes/{i['regiao']}.html">{E(reg['nome'])}</a><span aria-hidden="true">/</span><span>Código {i['codigo']}</span></nav>
<div class="galeria">{''.join(cel)}</div>
{janela_fotos}
<div class="imovel-layout">
<div class="imovel-principal">
<div style="display:flex;flex-direction:column;gap:10px">
<span class="selo selo-{i['documento']}" style="align-self:flex-start;font-size:14px;padding:6px 12px">{d['rotulo']}</span>
<h1>{E(i['titulo'])}{'' if i['regiao'] == 'outras-regioes' else ' ' + E(em_regiao(reg))}</h1>
<p style="color:var(--texto-2)">{E(i['endereco'])}, {E(local(reg).split(", ", 1)[1] if uf(reg) in ("DF", *PAISES) else uf(reg))}</p>
</div>
<div class="specs">{specs_html}</div>
<section style="display:flex;flex-direction:column;gap:12px">
<h2>Sobre o imóvel</h2>
<p style="line-height:1.7;color:#33334A">{E(i['descricao'])}</p>
<div class="tags">{tags}</div>
</section>
{secao_video}
<section class="doc-box doc-{i['documento']}">
<h2 style="font-size:22px">{d.get('titulo', 'Situação do documento: ' + d['rotulo'].lower())}</h2>
<p style="line-height:1.6;color:#33334A">{d['texto']}</p>
{aviso_fin}
</section>
<section style="display:flex;flex-direction:column;gap:12px">
<h2>Localização</h2>
<div class="mapa"><iframe title="Mapa de {E(reg['nome'])}" loading="lazy" src="https://www.google.com/maps?q={mapa_q}&z={i.get("mapa_zoom", 13)}&output=embed"></iframe></div>
<p style="font-size:15px;color:var(--texto-2)">O endereço exato é passado ao agendar a visita.</p>
</section>
</div>
<aside class="lateral" aria-label="Contato">
<span class="preco">{preco(i)}</span>
<div class="custos">{custos_html or ('<div><span>Sem condomínio</span></div>' if i.get("condominio") == 0 else '')}</div>
<a class="btn btn-azul" style="min-height:52px;font-size:17px" href="{wa(msg)}">{ICONE_WHATS.format(s=20)} Conversar no WhatsApp</a>
<button class="btn btn-contorno" type="button" data-abrir-visita style="min-height:52px">Agendar visita</button>
<form class="form-visita" data-visita data-codigo="{i['codigo']}" hidden>
<label class="campo">Seu nome<input name="nome" required autocomplete="name"></label>
<label class="campo">Melhor dia e horário<select name="quando"><option>Sábado de manhã</option><option>Sábado à tarde</option><option>Dia de semana de manhã</option><option>Dia de semana à tarde</option><option>Dia de semana à noite</option></select></label>
<button class="btn btn-areia" type="submit">Enviar pedido pelo WhatsApp</button>
</form>
<p class="codigo">Código {i['codigo']} · {CRECI}{" · intermediação em Portugal por corretor parceiro licenciado" if uf(reg) == "PT" else ""}</p>
</aside>
</div>
</div>"""
    url = f"{DOMINIO}/imoveis/{i['codigo']}.html"
    # Bairro do anúncio: a região, ou o campo "bairro" para imóveis em "outras-regioes".
    bairro = i.get("bairro") or ("Brasília" if i["regiao"] == "outras-regioes" else reg["nome"])
    onde = f"em {bairro}" if i.get("bairro") or i["regiao"] == "outras-regioes" else em_regiao(reg)
    lugar = f"{bairro}, {PAISES[uf(reg)]}" if uf(reg) in PAISES else f"{bairro}, {uf(reg)}"
    ld = {
        "@context": "https://schema.org",
        "@type": "RealEstateListing",
        "name": i["titulo"],
        "url": url,
        "description": i.get("descricao", ""),
        "image": [f"{DOMINIO}/{f}" for f in fotos[:6]],
        "offers": {
            "@type": "Offer",
            **({"price": i["preco"]} if i["preco"] else {}),
            "priceCurrency": i.get("moeda", "BRL"),
            "availability": "https://schema.org/InStock",
            "url": url,
            "seller": {"@type": "RealEstateAgent", "name": f"{MARCA} · {MARCA_SUB}", "url": DOMINIO, "telephone": "+55 61 99562-0101"},
            "itemOffered": {
                "@type": "SingleFamilyResidence" if i["tipo"] == "Casa" else ("Apartment" if i["tipo"] == "Apartamento" else "Place"),
                "name": i["titulo"],
                **({"floorSize": {"@type": "QuantitativeValue", "value": i["area"], "unitCode": "MTK"}} if i.get("area") else {}),
                **({"numberOfRooms": i["quartos"]} if i.get("quartos") else {}),
                "address": {"@type": "PostalAddress", "addressLocality": bairro, "addressRegion": reg["nome"] if uf(reg) in PAISES else uf(reg), "addressCountry": uf(reg) if uf(reg) in PAISES else "BR"},
            },
        },
    }
    head = ld_script(ld, trilha_ld([("Imóveis à venda", "imoveis.html"), (reg["nome"], f"regioes/{i['regiao']}.html"), (f"Código {i['codigo']}", f"imoveis/{i['codigo']}.html")]))
    tipo = {"Comércio": "Ponto comercial", "Lote": "Terreno" if uf(reg) in PAISES else "Lote"}.get(i["tipo"], i["tipo"])
    desc = f"{tipo} à venda {onde}, {lugar.split(', ', 1)[1]}: {specs_curtas(i) or i['titulo']}. {preco(i)}. {d['rotulo']}. Código {i['codigo']}, com fotos e vídeo. Fale com o corretor {MARCA}."
    if not youtube_id(i.get("video")):
        desc = desc.replace(", com fotos e vídeo", ", com fotos")
    titulo = i.get("titulo_seo") or f"{i['titulo']}{'' if i['regiao'] == 'outras-regioes' else ' ' + em_regiao(reg)} · {preco(i)}"
    return layout(r, titulo, desc, corpo, "comprar", f"imoveis/{i['codigo']}.html", tem_exemplo, head, fotos[0] if fotos else "static/img/fabricio-retrato.jpg")


def pagina_anuncie(tem_exemplo):
    r = ""
    opts_reg = "".join(
        f'<optgroup label="{nome}">' + "".join(f"<option>{E(v['nome'])}</option>" for _, v in regs) + "</optgroup>"
        for _, nome, regs in por_uf()
    )
    corpo = f"""<section class="pagina-texto"><div class="wrap">
<span class="sobretitulo">Para proprietários</span>
<h1>Venda seu imóvel com quem conhece a região</h1>
<p>Faço a avaliação com base nas vendas reais da região, produzo as fotos, divulgo no site e nos principais portais e acompanho cada visita. Antes de anunciar, verifico com você a documentação, para o comprador chegar já sabendo a situação do imóvel.</p>
<h2>Como funciona</h2>
<ol>
<li>Você me conta sobre o imóvel aqui ou no WhatsApp.</li>
<li>Faço uma visita para avaliar e conversar sobre o preço.</li>
<li>Produzo as fotos e publico o anúncio.</li>
<li>Filtro os interessados e acompanho as visitas e a negociação até a escritura.</li>
</ol>
<h2>Conte sobre o seu imóvel</h2>
<form class="caixa" data-anuncie>
<div class="linha-campos">
<label class="campo">Seu nome<input name="nome" required autocomplete="name"></label>
<label class="campo">Tipo<select name="tipo">{"".join(f"<option>{t}</option>" for t in TIPOS)}</select></label>
<label class="campo">Região<select name="regiao">{opts_reg}</select></label>
</div>
<label class="campo">Situação do documento<select name="doc"><option>Escriturado</option><option>Em regularização</option><option>Cessão de direitos</option><option>Não sei</option></select></label>
<label class="campo">Conte um pouco sobre o imóvel<textarea name="obs" placeholder="Tamanho, quartos, valor que você espera..."></textarea></label>
<button class="btn btn-azul" type="submit">{ICONE_WHATS.format(s=18)} Enviar pelo WhatsApp</button>
</form>
</div></section>"""
    return layout(r, f"Quer vender seu imóvel em Brasília? Anuncie com corretor · {MARCA}", "Venda sua casa, lote ou apartamento em Vicente Pires, Jóquei, Arniqueira, Águas Claras ou outra região do DF com avaliação gratuita, fotos profissionais, divulgação e documentação conferida.", corpo, "anuncie", "anuncie.html", tem_exemplo)


def pagina_sobre(tem_exemplo):
    r = ""
    corpo = secao_sobre(r, completa=True) + secao_docs()
    return layout(r, f"{MARCA}, corretor de imóveis em Brasília · {CRECI}", f"{MARCA}, corretor de imóveis {CRECI}, especialista em venda de casas, lotes e apartamentos em Vicente Pires, Jóquei, Arniqueira e Águas Claras, no Entorno do DF e no Algarve, Portugal.", corpo, "sobre", "sobre.html", tem_exemplo)


def para_investidor(i):
    return i.get("investidor", i["documento"] in ("lancamento", "portugal"))


def pagina_investidores(imoveis, tem_exemplo):
    r = ""
    sel = [i for i in imoveis if para_investidor(i)]
    br = [i for i in sel if uf(REGIOES[i["regiao"]]) not in PAISES]
    pt = [i for i in sel if uf(REGIOES[i["regiao"]]) in PAISES]

    def grupo(titulo, texto, lista, msg):
        cards = "\n".join(card(i, r) for i in lista) if lista else f'<div class="vazio">Novas oportunidades chegam em breve. <a href="{wa(msg)}">Me chame no WhatsApp</a> e eu aviso primeiro.</div>'
        return f"""<section class="secao" style="padding-top:0">
<div class="secao-cabeca"><h2>{titulo}</h2></div>
<p style="color:var(--texto-2);line-height:1.6;max-width:820px;margin-bottom:20px">{texto}</p>
<div class="grade">{cards}</div>
</section>"""

    corpo = f"""<div class="busca-pagina"><div class="wrap">
<nav class="trilha" aria-label="Caminho" style="padding-top:0"><a href="index.html">Início</a><span aria-hidden="true">/</span><span>Investidores</span></nav>
<div style="display:flex;flex-direction:column;gap:12px;margin-bottom:28px;max-width:820px">
<span class="sobretitulo" style="color:var(--texto-2)">Para investidores</span>
<h1 style="font-size:clamp(28px,4vw,38px)">Lançamentos e oportunidades para investir</h1>
<p style="color:var(--texto-2);font-size:18px;line-height:1.6">Lançamentos na planta são a porta de entrada de quem investe: entrada menor, parcelas durante a obra e valorização até a entrega das chaves. Aqui reúno os empreendimentos do DF e as oportunidades em Portugal, no Algarve, por meio da minha parceria luso-brasileira. Eu analiso cada um com você, do potencial de valorização à documentação.</p>
<div style="display:flex;flex-wrap:wrap;gap:12px;margin-top:8px"><a class="btn btn-azul" href="{wa("Olá Fabrício, sou investidor e quero conhecer os lançamentos e oportunidades.")}">{ICONE_WHATS.format(s=18)} Falar sobre investimento</a></div>
</div>
{grupo("Lançamentos no DF", "Empreendimentos na planta, comprados direto com a construtora, com tabela e condições de pagamento explicadas por mim.", br, "Olá Fabrício, quero saber dos lançamentos no DF.")}
{grupo("Portugal · Algarve", "Imóveis e oportunidades no sul de Portugal, com preços em euro. Você fala comigo, em português do Brasil, e a intermediação em Portugal é feita pelo meu parceiro, corretor licenciado no país.", pt, "Olá Fabrício, quero saber das oportunidades em Portugal.")}
</div></div>"""
    head = ld_script(trilha_ld([("Início", ""), ("Investidores", "investidores.html")]))
    return layout(r, f"Investir em imóveis: lançamentos no DF e no Algarve, Portugal · {MARCA}", f"Lançamentos na planta em Brasília e imóveis para investir no Algarve, Portugal, com atendimento em português do Brasil. Corretor {MARCA}, {CRECI}, com parceiro licenciado em Portugal.", corpo, "investidores", "investidores.html", tem_exemplo, head)


def pagina_privacidade(tem_exemplo):
    corpo = f"""<section class="pagina-texto"><div class="wrap">
<h1>Política de privacidade</h1>
<p>Atualizada em {date.today().strftime('%d/%m/%Y')}.</p>
<p>Este site é mantido por {MARCA}, corretor de imóveis {CRECI}, com atuação em Brasília, DF.</p>
<h2>Quais dados recebo</h2>
<p>O site não tem cadastro nem guarda formulários. Quando você usa o botão de WhatsApp, agenda uma visita ou anuncia um imóvel, a mensagem é aberta no seu próprio WhatsApp e só chega a mim se você enviar. Nela vão os dados que você escrever, como nome e informações do imóvel.</p>
<h2>Para que uso</h2>
<p>Uso esses dados apenas para responder você, agendar visitas e tratar da compra ou venda do imóvel. Não vendo nem repasso seus dados a terceiros, exceto quando necessário para a negociação, como ao vendedor, ao banco ou ao cartório, com o seu conhecimento.</p>
<h2>Seus direitos</h2>
<p>Pela Lei Geral de Proteção de Dados (Lei 13.709/2018), você pode pedir a qualquer momento acesso, correção ou exclusão dos seus dados. Basta me chamar no WhatsApp {WHATS_TXT}.</p>
<h2>Serviços de terceiros</h2>
<p>As páginas de imóveis mostram um mapa do Google Maps e podem mostrar vídeos do YouTube, e o site usa fontes do Google Fonts. Esses serviços podem registrar dados técnicos de acesso conforme as políticas do Google.</p>
</div></section>"""
    return layout("", f"Política de privacidade · {MARCA}", "Como o site de Fabrício Borges trata os dados de quem entra em contato.", corpo, "", "privacidade.html", tem_exemplo)


def pagina_404(tem_exemplo):
    corpo = """<section class="pagina-texto"><div class="wrap">
<h1>Página não encontrada</h1>
<p>Esse imóvel pode já ter sido vendido ou o endereço mudou.</p>
<p><a class="btn btn-azul" href="/imoveis.html">Ver os imóveis à venda</a></p>
</div></section>"""
    return layout("/", f"Página não encontrada · {MARCA}", "Página não encontrada.", corpo, "", "404.html", tem_exemplo, indexar=False)


def main():
    dados = json.loads((RAIZ / "dados/imoveis.json").read_text(encoding="utf-8"))
    imoveis = dados["imoveis"]
    for n, i in enumerate(imoveis):
        i["_ordem"] = n
        # Capa gerada por ferramentas/capas.js entra como primeira foto.
        capa = f"fotos/{i['codigo']}/capa.jpg"
        if i.get("capa") and (RAIZ / capa).exists() and capa not in i.get("fotos", []):
            i["fotos"] = [capa] + i.get("fotos", [])
            i["capa_foco"] = "50% 100%"
    tem_exemplo = any(i.get("exemplo") for i in imoveis)

    if SAIDA.exists():
        shutil.rmtree(SAIDA)
    (SAIDA / "imoveis").mkdir(parents=True)
    (SAIDA / "regioes").mkdir()
    shutil.copytree(RAIZ / "static", SAIDA / "static")
    if (RAIZ / "fotos").exists():
        shutil.copytree(RAIZ / "fotos", SAIDA / "fotos")

    paginas = {
        "index.html": pagina_inicial(imoveis, tem_exemplo),
        "imoveis.html": pagina_busca(imoveis, tem_exemplo),
        "anuncie.html": pagina_anuncie(tem_exemplo),
        "sobre.html": pagina_sobre(tem_exemplo),
        "investidores.html": pagina_investidores(imoveis, tem_exemplo),
        "privacidade.html": pagina_privacidade(tem_exemplo),
        "404.html": pagina_404(tem_exemplo),
    }
    for slug in REGIOES:
        paginas[f"regioes/{slug}.html"] = pagina_regiao(slug, imoveis, tem_exemplo)
    for i in imoveis:
        paginas[f"imoveis/{i['codigo']}.html"] = pagina_imovel(i, tem_exemplo)
    for caminho, conteudo in paginas.items():
        (SAIDA / caminho).write_text(conteudo, encoding="utf-8")

    hoje = date.today().isoformat()
    urls = "".join(
        f"<url><loc>{DOMINIO}/{'' if c == 'index.html' else c}</loc><lastmod>{hoje}</lastmod></url>"
        for c in paginas if c != "404.html"
    )
    (SAIDA / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n',
        encoding="utf-8",
    )
    (SAIDA / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {DOMINIO}/sitemap.xml\n", encoding="utf-8")
    (SAIDA / "CNAME").write_text("fabricioborgesimob.com.br\n", encoding="utf-8")
    # Verificação do Google Search Console (não remover)
    (SAIDA / "google1be5a2dd9e10a72d.html").write_text("google-site-verification: google1be5a2dd9e10a72d.html", encoding="utf-8")
    (SAIDA / ".nojekyll").write_text("", encoding="utf-8")
    print(f"{len(paginas)} páginas geradas em {SAIDA}")


if __name__ == "__main__":
    main()
