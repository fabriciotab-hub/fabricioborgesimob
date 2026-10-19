(function () {
  var WHATS = '5561995620101';
  function abrirWhats(msg) {
    var a = document.createElement('a');
    a.href = 'https://wa.me/' + WHATS + '?text=' + encodeURIComponent(msg);
    a.target = '_blank';
    a.rel = 'noopener';
    document.body.appendChild(a);
    a.click();
    a.remove();
  }
  function num(txt) { return Number(String(txt).replace(/\D/g, '')) || 0; }
  function brl(v) { return 'R$ ' + Math.round(v).toLocaleString('pt-BR'); }

  // Busca com filtros
  var busca = document.querySelector('[data-busca]');
  if (busca) {
    var form = busca.querySelector('.filtros');
    var lista = busca.querySelector('[data-lista]');
    var cards = Array.prototype.slice.call(lista.querySelectorAll('.card'));
    var total = busca.querySelector('[data-total]');
    var vazio = busca.querySelector('[data-vazio]');
    var ordem = busca.querySelector('select[name="ordem"]');
    var tipo = '';
    var pilulas = busca.querySelectorAll('.pilula');

    function marcarTipo(t) {
      tipo = t;
      pilulas.forEach(function (p) { p.setAttribute('aria-pressed', p.dataset.tipo === t ? 'true' : 'false'); });
    }

    // Aplica os filtros vindos da busca da página inicial
    var q = new URLSearchParams(location.search);
    if (q.get('tipo')) marcarTipo(q.get('tipo'));
    if (q.get('ate')) form.elements.ate.value = q.get('ate');
    if (q.get('quartos')) form.elements.quartos.value = q.get('quartos');
    if (q.get('esc')) form.elements.esc.checked = true;
    var regs = q.getAll('regiao');
    form.querySelectorAll('input[type="checkbox"][name="regiao"]').forEach(function (c) { c.checked = regs.indexOf(c.value) >= 0; });

    function aplicar() {
      var marcadas = [];
      form.querySelectorAll('input[name="regiao"]').forEach(function (c) {
        if (c.type === 'hidden' || c.checked) marcadas.push(c.value);
      });
      var ate = num(form.elements.ate.value);
      var quartos = num(form.elements.quartos.value);
      var esc = form.elements.esc.checked;
      var n = 0;
      cards.forEach(function (c) {
        var d = c.dataset;
        var ok = (!tipo || d.tipo === tipo) &&
          (!marcadas.length || marcadas.indexOf(d.regiao) >= 0) &&
          (!ate || Number(d.preco) <= ate) &&
          (!quartos || Number(d.quartos) >= quartos) &&
          (!esc || d.doc === 'escriturado');
        c.hidden = !ok;
        if (ok) n++;
      });
      var o = ordem.value;
      cards.slice().sort(function (a, b) {
        if (o === 'menor') return a.dataset.preco - b.dataset.preco;
        if (o === 'maior') return b.dataset.preco - a.dataset.preco;
        if (o === 'area') return b.dataset.area - a.dataset.area;
        return a.dataset.ordem - b.dataset.ordem;
      }).forEach(function (c) { lista.appendChild(c); });
      total.textContent = n;
      vazio.hidden = n > 0;
    }

    pilulas.forEach(function (p) {
      p.addEventListener('click', function () { marcarTipo(p.dataset.tipo); aplicar(); });
    });
    form.addEventListener('change', aplicar);
    ordem.addEventListener('change', aplicar);
    aplicar();
  }

  // Simulador de financiamento (tabela Price, estimativa)
  var simBotao = document.getElementById('sim-botao');
  if (simBotao) {
    var renda = document.getElementById('sim-renda');
    var entrada = document.getElementById('sim-entrada');
    var saida = document.getElementById('sim-resultado');
    [renda, entrada].forEach(function (el) {
      el.addEventListener('input', function () {
        var v = num(el.value);
        el.value = v ? v.toLocaleString('pt-BR') : '';
      });
    });
    simBotao.addEventListener('click', function () {
      var parcela = num(renda.value) * 0.3;
      var i = Math.pow(1.11, 1 / 12) - 1;
      var meses = 420;
      var financiavel = parcela * (1 - Math.pow(1 + i, -meses)) / i;
      var ent = num(entrada.value);
      // Bancos financiam até cerca de 80% do valor do imóvel
      var preco = Math.min(financiavel + ent, ent / 0.2 || financiavel + ent);
      if (!parcela) { saida.hidden = false; saida.innerHTML = 'Informe a renda para simular.'; return; }
      saida.hidden = false;
      saida.innerHTML = '<span>Você pode buscar imóveis de até</span><strong>' + brl(preco) + '</strong>' +
        '<span class="nota">Parcela inicial de até ' + brl(parcela) + ' por mês. A aprovação final depende do banco.</span>' +
        '<div style="margin-top:12px"><a class="btn btn-areia" href="imoveis.html?ate=' + Math.round(preco) + '">Ver imóveis nessa faixa</a></div>';
    });
  }

  // Pedido de visita pelo WhatsApp
  var abrirVisita = document.querySelector('[data-abrir-visita]');
  var formVisita = document.querySelector('[data-visita]');
  if (abrirVisita && formVisita) {
    abrirVisita.addEventListener('click', function () {
      formVisita.hidden = false;
      abrirVisita.hidden = true;
      formVisita.elements.nome.focus();
    });
    formVisita.addEventListener('submit', function (e) {
      e.preventDefault();
      abrirWhats('Olá Fabrício, sou ' + formVisita.elements.nome.value + ' e quero agendar uma visita ao imóvel ' +
        formVisita.dataset.codigo + '. Melhor horário: ' + formVisita.elements.quando.value + '.');
    });
  }

  // Anuncie seu imóvel pelo WhatsApp
  var formAnuncie = document.querySelector('[data-anuncie]');
  if (formAnuncie) {
    formAnuncie.addEventListener('submit', function (e) {
      e.preventDefault();
      var f = formAnuncie.elements;
      abrirWhats('Olá Fabrício, sou ' + f.nome.value + ' e quero vender meu imóvel.\n' +
        'Tipo: ' + f.tipo.value + '\nRegião: ' + f.regiao.value + '\nDocumento: ' + f.doc.value +
        (f.obs.value ? '\nSobre o imóvel: ' + f.obs.value : ''));
    });
  }

  // Galeria: todas as fotos
  var janela = document.querySelector('[data-fotos]');
  if (janela && janela.showModal) {
    document.querySelectorAll('[data-abrir-fotos], .galeria img').forEach(function (b) {
      b.addEventListener('click', function () { janela.showModal(); });
    });
    janela.querySelector('[data-fechar-fotos]').addEventListener('click', function () { janela.close(); });
    janela.addEventListener('click', function (e) { if (e.target === janela) janela.close(); });
  }
})();
