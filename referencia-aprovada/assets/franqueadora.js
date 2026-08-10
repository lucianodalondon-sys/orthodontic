/* ============================================================
   Sala de comando da franqueadora — OrthoDontic
   A tela não calcula. Todo número exibido sai de
   dados/portal/franqueadora.json e dados/portal/manifest.json.
   O que ela faz: buscar, ordenar por campo existente,
   filtrar por campo existente e formatar data.
   ============================================================ */
(function () {
  "use strict";

  var BASE = "./dados/portal/";
  var CHAVE_TEMA = "od-franqueadora-tema";

  var dados = null;
  var manifesto = null;
  var ufSel = null;
  var ferrSel = "mapa";

  /* ---------------- utilidades ---------------- */

  function esc(v) {
    if (v === null || v === undefined) return "";
    return String(v)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  function tem(v) { return v !== null && v !== undefined && v !== ""; }

  function chaveTexto(v) {
    return String(v == null ? "" : v).normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  }

  var MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];
  function dataBR(iso) {
    if (!iso) return "";
    var m = String(iso).match(/^(\d{4})-(\d{2})-(\d{2})/);
    if (!m) return String(iso);
    return Number(m[3]) + "/" + MESES[Number(m[2]) - 1] + "/" + m[1];
  }

  function br(n) {
    if (!tem(n)) return "—";
    return Number(n).toLocaleString("pt-BR");
  }

  function el(id) { return document.getElementById(id); }

  /* ---------------- ícones (Lucide, traço médio) ---------------- */

  var ICONES = {
    mapa: '<path d="M14.5 3.5 9.5 6 3 3.5v14L9.5 20l5-2.5L21 20V6z"/><path d="M9.5 6v14"/><path d="M14.5 3.5v14"/>',
    pracas: '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/>',
    radar: '<circle cx="12" cy="12" r="9"/><path d="m15.5 8.5-2 5-5 2 2-5z"/>',
    territorio: '<path d="m12 2 9 5-9 5-9-5z"/><path d="m3 12 9 5 9-5"/><path d="m3 17 9 5 9-5"/>',
    constancia: '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    busca: '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.6-3.6"/>',
    fichas: '<rect x="8" y="2" width="8" height="4" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/>',
    reputacao: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    sazonalidade: '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    consultor: '<rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>',
    planos: '<path d="M10 6h11M10 12h11M10 18h11"/><path d="m3 5 1.5 1.5L7 4"/><path d="m3 11 1.5 1.5L7 10"/><path d="m3 17 1.5 1.5L7 16"/>',
    achados: '<path d="M22 7 13.5 15.5 8.5 10.5 2 17"/><path d="M16 7h6v6"/>',
    evidencias: '<path d="M12 7v14"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/>'
  };

  function icone(chave, px) {
    var d = ICONES[chave] || ICONES.territorio;
    var t = px || 17;
    return '<svg width="' + t + '" height="' + t + '" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
      'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + d + "</svg>";
  }

  /* ---------------- estrutura da barra ---------------- */

  var GRUPOS = [
    ["Panorama", ["mapa", "pracas"]],
    ["Crescer", ["radar", "territorio"]],
    ["A rede hoje", ["constancia", "busca", "fichas", "reputacao", "sazonalidade"]],
    ["Operação", ["consultor", "planos", "achados", "evidencias"]]
  ];

  /* telas que já existem no portal — o resto declara que ainda não foi construído */
  var ROTAS = {
    radar: "index.html#/radar",
    achados: "index.html#/achados",
    pracas: "index.html#/praca",
    planos: "index.html#/plano",
    constancia: "index.html#/rede",
    territorio: "index.html#/rede",
    busca: "index.html#/captacao"
  };

  /* o nome por extenso de cada estado — o diretor digita "Goiás", não "GO" */
  var NOMES_UF = {
    AC: "Acre", AL: "Alagoas", AP: "Amapá", AM: "Amazonas", BA: "Bahia", CE: "Ceará",
    DF: "Distrito Federal", ES: "Espírito Santo", GO: "Goiás", MA: "Maranhão",
    MT: "Mato Grosso", MS: "Mato Grosso do Sul", MG: "Minas Gerais", PA: "Pará",
    PB: "Paraíba", PR: "Paraná", PE: "Pernambuco", PI: "Piauí", RJ: "Rio de Janeiro",
    RN: "Rio Grande do Norte", RS: "Rio Grande do Sul", RO: "Rondônia", RR: "Roraima",
    SC: "Santa Catarina", SP: "São Paulo", SE: "Sergipe", TO: "Tocantins"
  };

  function nomeUF(uf) { return NOMES_UF[uf] || uf; }

  /* ---------------- cor por densidade ---------------- */

  /* Cinco paradas na família sky → navy da marca. Não é interpolação linear:
     o meio do caminho entre os dois cai numa zona onde nem texto branco nem
     texto navy chegam a 4,5:1. Cada parada abaixo passa com a tinta que usa. */
  var RAMPA = ["#DFEAF8", "#C3D3EC", "#9DB4DF", "#4E6FB5", "#001E78"];

  function tinta(i) { return RAMPA[Math.max(1, Math.min(5, i)) - 1]; }

  function faixa(u, maxU) {
    if (!u) return 0;
    return Math.max(1, Math.min(5, Math.ceil((u / maxU) * 5)));
  }

  /* ---------------- números da barra, de campos reais ---------------- */

  function numeroDe(chave) {
    var arq = (manifesto && manifesto.arquivos) || {};
    if (chave === "mapa") return (dados.rede || {}).unidades;
    if (chave === "pracas") return ((manifesto || {}).pracas || []).length;
    if (chave === "planos") return (arq.planos || []).length;
    if (chave === "radar") return (arq.oportunidade || []).length;
    if (chave === "reputacao") return (dados.reputacao_das_redes || []).length;
    if (chave === "fichas") return (dados.fichas_da_rede || {}).conferidas;
    if (chave === "busca") return Object.keys(dados.presenca_na_busca || {}).length;
    return null;
  }

  function ferramentaPor(chave) {
    return (dados.ferramentas || []).filter(function (f) { return f.chave === chave; })[0] || null;
  }

  /* ---------------- cabeçalho ---------------- */

  function pintarCabecalho() {
    var r = dados.rede || {};
    el("rede-numeros").innerHTML =
      item(r.unidades, "unidades") +
      item(r.abertas, "abertas") +
      item(r.em_implantacao, "em implantação") +
      item(r.cidades, "cidades");

    el("proveniencia").textContent =
      "medido em " + dataBR(r.medido_em) + " · fonte: " + (r.fonte || "não informada");

    function item(v, k, suave) {
      return '<div class="item' + (suave ? " suave" : "") + '"><div class="v">' + br(v) + "</div>" +
        '<div class="k">' + esc(k) + "</div></div>";
    }
  }

  /* ---------------- barra esquerda ---------------- */

  function pintarBarra() {
    var lista = el("barra-lista");
    var usadas = {};
    var h = "";

    GRUPOS.forEach(function (g) {
      var itens = g[1].map(ferramentaPor).filter(Boolean);
      if (!itens.length) return;
      h += '<div class="barra-grupo">' + esc(g[0]) + "</div>";
      itens.forEach(function (f) { usadas[f.chave] = true; h += linha(f); });
    });

    var sobra = (dados.ferramentas || []).filter(function (f) { return !usadas[f.chave]; });
    if (sobra.length) {
      h += '<div class="barra-grupo">Outras</div>';
      sobra.forEach(function (f) { h += linha(f); });
    }

    lista.innerHTML = h;
    lista.querySelectorAll("[data-ferr]").forEach(function (b) {
      b.addEventListener("click", function () { selecionarFerramenta(b.getAttribute("data-ferr")); });
    });

    function linha(f) {
      var n = f.disponivel === false ? "sem dado" : numeroDe(f.chave);
      return '<button type="button" class="ferramenta' + (f.disponivel === false ? " apagada" : "") +
        '" data-ferr="' + esc(f.chave) + '" aria-current="' + (ferrSel === f.chave) + '"' +
        (f.disponivel === false && f.indisponivel_porque ? ' title="' + esc(f.indisponivel_porque) + '"' : "") + ">" +
        '<span class="faixa"></span>' + icone(f.chave) +
        '<span class="nome">' + esc(f.nome) + "</span>" +
        (tem(n) ? '<span class="num">' + (typeof n === "number" ? br(n) : esc(n)) + "</span>" : "") +
        "</button>";
    }
  }

  function pintarRodapeBarra() {
    var c = dados.cobertura || {};
    var medidas = tem(c.pracas_medidas) ? c.pracas_medidas : c.ouvidas;
    var total = c.total;
    el("cobertura-n").textContent = br(medidas) + " praças medidas de " + br(total) + " unidades";
    el("cobertura-d").textContent = c.aviso || "";
    el("cobertura-barra").style.width = (tem(medidas) && total ? Math.max(0.6, (medidas / total) * 100) : 0) + "%";
  }

  function selecionarFerramenta(chave) {
    ferrSel = chave;
    document.querySelectorAll("[data-ferr]").forEach(function (b) {
      b.setAttribute("aria-current", String(b.getAttribute("data-ferr") === chave));
    });
    document.querySelectorAll("[data-cartao]").forEach(function (c) {
      c.setAttribute("data-sel", String(c.getAttribute("data-cartao") === chave));
    });
    var alvo = chave === "mapa" ? el("painel-mapa") : document.querySelector('[data-cartao="' + chave + '"]');
    if (alvo) window.scrollTo({ top: alvo.getBoundingClientRect().top + window.pageYOffset - 18, behavior: "smooth" });
  }

  /* ---------------- o mapa ---------------- */

  function pintarMapa() {
    var mapa = (dados.mapa || []).slice();
    var caixa = el("mapa-caixa");
    var geo = window.BRASIL_UFS;

    if (!mapa.length) {
      caixa.innerHTML = vazioEstado("Esta coleta não trouxe o mapa da rede",
        "O arquivo veio sem a lista de estados.", "franqueadora.json → mapa");
      return;
    }
    if (!geo || !geo.ufs) {
      caixa.innerHTML = vazioEstado("O contorno dos estados não carregou",
        "A malha é um arquivo local da própria página, lido antes dela.", "assets/brasil-ufs.js");
      return;
    }

    var maxU = mapa.reduce(function (m, x) { return Math.max(m, x.unidades || 0); }, 0) || 1;
    var formas = "", rotulos = "", semGeo = [];

    mapa.forEach(function (x) {
      var g = geo.ufs[x.uf];
      if (!g) { semGeo.push(x.uf); return; }
      var u = x.unidades || 0, i = faixa(u, maxU), vazio = i === 0;

      formas += '<g class="uf-tile" data-uf="' + esc(x.uf) + '" data-sel="' + (ufSel === x.uf) +
        '" tabindex="0" role="button" aria-label="' + esc(nomeUF(x.uf)) + ", " + br(u) + ' unidades">' +
        '<path class="fundo' + (vazio ? " vazia" : "") + '" d="' + g.d + '"' +
        (vazio ? "" : ' style="--c:' + tinta(i) + '"') + "></path></g>";

      /* o rótulo cai no centro de área; onde o estado é pequeno demais para
         a sigla caber, ele sai para fora com uma linha de chamada */
      var cabe = g.w >= 24 && g.h >= 13;
      var lx = cabe ? g.cx : g.cx + 20, ly = cabe ? g.cy : g.cy - 11;
      var corTexto = vazio ? "var(--marca-tinta)" : (i < 4 ? "#001E78" : "#FFFFFF");
      var comNumero = !vazio && g.w >= 34 && g.h >= 30;
      /* "SEM UNIDADE" só entra onde cabe dentro do próprio estado; num estado
         pequeno o texto invadiria o vizinho, e aí ele fica só com o contorno
         tracejado, a legenda e o aviso acima do mapa */
      var cabeAviso = vazio && g.w >= 60 && g.h >= 40;

      if (!cabe) {
        rotulos += '<path d="M' + g.cx + " " + g.cy + "L" + (g.cx + 14) + " " + (g.cy - 8) +
          '" style="stroke:var(--marca-tinta);stroke-width:.9;fill:none"></path>';
      }

      rotulos += '<text x="' + lx + '" y="' + (ly + (cabeAviso ? -4 : (comNumero ? -2 : (vazio ? 0 : 4)))) +
        '" text-anchor="middle" style="fill:' + corTexto +
        ';font-size:11px;font-weight:900;letter-spacing:.02em">' + esc(x.uf) + "</text>";

      if (comNumero) {
        rotulos += '<text x="' + lx + '" y="' + (ly + 10) + '" text-anchor="middle" style="fill:' + corTexto +
          ';font-size:9.5px;font-weight:500;opacity:.92;font-variant-numeric:tabular-nums">' + br(u) + "</text>";
      }
      if (cabeAviso) {
        rotulos += '<text x="' + lx + '" y="' + (ly + 6) + '" text-anchor="middle" ' +
          'style="fill:var(--marca-tinta);font-size:8px;font-weight:700;letter-spacing:.08em">SEM</text>' +
          '<text x="' + lx + '" y="' + (ly + 15) + '" text-anchor="middle" ' +
          'style="fill:var(--marca-tinta);font-size:8px;font-weight:700;letter-spacing:.08em">UNIDADE</text>';
      }
      if (x.pracas_medidas) {
        rotulos += '<circle cx="' + lx + '" cy="' + (ly - 15) + '" r="3.2" ' +
          'style="fill:var(--marca);stroke:var(--cartao);stroke-width:1.2"></circle>';
      }
    });

    caixa.innerHTML = '<svg viewBox="0 0 ' + geo.w + " " + geo.h + '" role="img" ' +
      'aria-label="Mapa do Brasil por estado, colorido pela quantidade de unidades">' +
      '<g class="uf-formas">' + formas + '</g>' +
      '<g class="uf-rotulos" pointer-events="none">' + rotulos + "</g></svg>" +
      '<div class="mapa-dica" id="mapa-dica" style="display:none"></div>' +
      (semGeo.length ? '<div class="mapa-nota">sem contorno nesta malha: ' + semGeo.map(esc).join(", ") + "</div>" : "");

    caixa.querySelectorAll(".uf-tile").forEach(function (g) {
      g.addEventListener("mouseenter", function () { mostrarDica(g, mapa); });
      g.addEventListener("mouseleave", esconderDica);
      g.addEventListener("focus", function () { mostrarDica(g, mapa); });
      g.addEventListener("blur", esconderDica);
      g.addEventListener("click", function () { alternarUF(g.getAttribute("data-uf")); });
      g.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); alternarUF(g.getAttribute("data-uf")); }
      });
    });

    pintarLegenda(maxU);
    pintarVaziosAviso();
    pintarRanking(mapa, maxU);
    pintarPracasTira();
  }

  function mostrarDica(g, mapa) {
    var uf = g.getAttribute("data-uf");
    var x = mapa.filter(function (m) { return m.uf === uf; })[0];
    if (!x) return;
    var dica = el("mapa-dica");
    var vazio = !x.unidades;
    dica.innerHTML = '<div class="uf">' + esc(nomeUF(x.uf)) + "</div>" +
      '<div style="font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;color:rgba(255,255,255,.55);margin-top:2px">' + esc(x.uf) + "</div><dl>" +
      par("unidades", x.unidades) + par("abertas", x.abertas) +
      par("em implantação", x.em_implantacao) + par("cidades", x.cidades) +
      par("praças medidas", x.pracas_medidas) + "</dl>" +
      (vazio ? '<div class="sem">SEM UNIDADE</div>' : "");
    dica.style.display = "block";
    var r = g.getBoundingClientRect();
    var c = el("mapa-caixa").getBoundingClientRect();
    var left = r.left - c.left + r.width + 12;
    if (left + 200 > c.width) left = r.left - c.left - 200;
    dica.style.left = Math.max(0, left) + "px";
    dica.style.top = Math.max(0, r.top - c.top) + "px";

    function par(k, v) { return "<dt>" + esc(k) + "</dt><dd>" + br(v) + "</dd>"; }
  }

  function esconderDica() {
    var d = el("mapa-dica");
    if (d) d.style.display = "none";
  }

  function pintarLegenda(maxU) {
    var caixas = "";
    for (var i = 1; i <= 5; i++) caixas += '<i style="background:' + tinta(i) + '"></i>';
    el("mapa-legenda").innerHTML =
      '<div class="escala"><span>menos</span><span class="caixas">' + caixas + "</span>" +
      "<span>mais · até " + br(maxU) + "</span></div>" +
      '<div class="vazio-chave"><i></i><span>estado sem nenhuma unidade</span></div>' +
      '<div class="vazio-chave"><i style="border:0;background:var(--marca);width:10px;height:10px;border-radius:50%"></i>' +
      "<span>tem praça medida</span></div>";
  }

  function pintarVaziosAviso() {
    var ufs = (dados.rede || {}).ufs_sem_unidade || [];
    var alvo = el("vazios-aviso");
    if (!ufs.length) { alvo.innerHTML = ""; return; }
    alvo.innerHTML = '<div class="n">' + br(ufs.length) + "</div>" +
      '<div class="txt"><b>estados sem nenhuma unidade.</b> É o vão mais largo do mapa — e o ponto de partida do Radar de Oportunidade.' +
      '<span class="ufs">' + ufs.map(esc).join(" · ") + "</span></div>";
  }

  function pintarRanking(mapa, maxU) {
    var vis = mapa.filter(function (x) { return (x.unidades || 0) > 0; })
      .sort(function (a, b) { return (b.unidades || 0) - (a.unidades || 0); });
    var alvo = el("ranking");
    alvo.innerHTML = vis.map(function (x) {
      return '<button type="button" class="ranking-linha" data-uf="' + esc(x.uf) + '" data-sel="' + (ufSel === x.uf) +
        '" title="' + esc(nomeUF(x.uf)) + '">' +
        '<span class="sig">' + esc(x.uf) + "</span>" +
        '<span class="trilho"><i style="width:' + Math.max(2, (x.unidades / maxU) * 100) + '%"></i></span>' +
        '<span class="n">' + br(x.unidades) + "</span></button>";
    }).join("");
    alvo.querySelectorAll("[data-uf]").forEach(function (b) {
      b.addEventListener("click", function () { alternarUF(b.getAttribute("data-uf")); });
    });
  }

  function alternarUF(uf) {
    ufSel = ufSel === uf ? null : uf;
    document.querySelectorAll(".uf-tile").forEach(function (g) {
      g.setAttribute("data-sel", String(g.getAttribute("data-uf") === ufSel));
    });
    document.querySelectorAll(".ranking-linha").forEach(function (b) {
      b.setAttribute("data-sel", String(b.getAttribute("data-uf") === ufSel));
    });
    pintarPracasTira();
  }

  function pintarPracasTira() {
    var todas = (manifesto || {}).pracas || [];
    var vis = ufSel ? todas.filter(function (p) { return (p.uf || []).indexOf(ufSel) > -1; }) : todas;
    var alvo = el("pracas-tira");
    var rot = ufSel ? "praças medidas em " + nomeUF(ufSel) : "praças medidas";
    if (!vis.length) {
      alvo.innerHTML = '<span class="rot">' + esc(rot) + "</span>" +
        '<span style="font-size:12.5px;color:var(--t3)">nenhuma praça medida neste estado ainda</span>' +
        (ufSel ? ' <button type="button" class="pastilha" data-limpar="1">ver todas</button>' : "");
    } else {
      alvo.innerHTML = '<span class="rot">' + esc(rot) + "</span>" +
        vis.map(function (p) {
          return '<a class="pastilha" href="index.html#/praca/' + esc(p.praca_id) + '">' + esc(p.rotulo) + "</a>";
        }).join("") +
        (ufSel ? ' <button type="button" class="pastilha" data-limpar="1">ver todas</button>' : "");
    }
    var limpar = alvo.querySelector("[data-limpar]");
    if (limpar) limpar.addEventListener("click", function () { alternarUF(ufSel); });
  }

  /* ---------------- o que mudou ---------------- */

  function pintarMudou() {
    var cards = [];
    var r = dados.rede || {};
    var pb = dados.presenca_na_busca || {};
    var fi = dados.fichas_da_rede || {};
    var rep = (dados.reputacao_das_redes || []).slice();

    if ((r.ufs_sem_unidade || []).length) {
      cards.push({
        v: r.ufs_sem_unidade.length, grave: true, ferr: "mapa",
        t: "<b>estados sem nenhuma unidade</b> — " + r.ufs_sem_unidade.join(" · "),
        ir: "ver no mapa"
      });
    }

    if (pb.dentista && tem(pb.dentista.fora)) {
      cards.push({
        v: pb.dentista.fora, grave: true, ferr: "busca",
        t: "<b>ausências</b> contra " + br(pb.dentista.dentro) + " aparições na busca por “dentista”",
        ir: "abrir presença na busca"
      });
    }

    var cats = Object.keys(fi.por_categoria || {}).map(function (k) { return [k, fi.por_categoria[k]]; })
      .sort(function (a, b) { return b[1] - a[1]; });
    if (cats.length && tem(fi.conferidas)) {
      cards.push({
        v: cats[0][1], ferr: "fichas",
        t: "<b>de " + br(fi.conferidas) + " fichas</b> cadastradas como “" + esc(cats[0][0]) + "”",
        ir: "abrir auditoria de ficha"
      });
    }

    rep.sort(function (a, b) { return (b.reclamacoes || 0) - (a.reclamacoes || 0); });
    var nossa = rep.filter(function (x) { return x.nossa; })[0];
    if (nossa && rep[0]) {
      cards.push({
        v: nossa.reclamacoes, ferr: "reputacao",
        t: nossa === rep[0]
          ? "<b>reclamações</b> — o maior volume entre as " + br(rep.length) + " redes medidas"
          : "<b>reclamações</b> contra " + br(rep[0].reclamacoes) + " da maior rede, " + esc(rep[0].marca),
        ir: "abrir rede contra rede"
      });
    }

    var alvo = el("mudou");
    if (!cards.length) {
      alvo.innerHTML = vazioEstado("Esta coleta não trouxe nada que exija olhar",
        "Os campos que alimentam esta faixa não vieram.", "franqueadora.json");
      return;
    }
    alvo.innerHTML = cards.map(function (c) {
      return '<button type="button" class="mudou-cartao' + (c.grave ? " grave" : "") + '" data-ferr="' + esc(c.ferr) + '">' +
        '<span class="v">' + br(c.v) + "</span>" +
        '<span class="t">' + c.t + "</span>" +
        '<span class="ir">' + esc(c.ir) + " →</span></button>";
    }).join("");
    alvo.querySelectorAll("[data-ferr]").forEach(function (b) {
      b.addEventListener("click", function () { selecionarFerramenta(b.getAttribute("data-ferr")); });
    });
  }

  /* ---------------- cartões das ferramentas ---------------- */

  function pintarFerramentas() {
    var ordem = [];
    GRUPOS.forEach(function (g) { g[1].forEach(function (c) { ordem.push(c); }); });
    var lista = (dados.ferramentas || []).slice().sort(function (a, b) {
      var ia = ordem.indexOf(a.chave), ib = ordem.indexOf(b.chave);
      return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib);
    });

    var alvo = el("grade-ferramentas");
    if (!lista.length) {
      alvo.innerHTML = vazioEstado("Esta coleta não trouxe ferramenta alguma",
        "A lista veio vazia.", "franqueadora.json → ferramentas");
      return;
    }

    alvo.innerHTML = lista.map(function (f) {
      var larga = f.chave === "reputacao" || f.chave === "busca";
      var indisp = f.disponivel === false;
      var h = '<article class="f-cartao' + (larga ? " larga" : "") + (indisp ? " indisponivel" : "") +
        '" data-cartao="' + esc(f.chave) + '" data-sel="' + (ferrSel === f.chave) + '">' +
        '<div class="cab"><span class="icone">' + icone(f.chave, 18) + "</span>" +
        "<h3>" + esc(f.nome) + "</h3></div>" +
        '<p class="pergunta">' + esc(f.o_que_responde) + "</p>";

      if (indisp) {
        h += '<div class="motivo">' + esc(f.indisponivel_porque || "sem dado nesta coleta") + "</div>";
        return h + "</article>";
      }

      if (tem(f.resumo)) h += '<div class="resumo">' + esc(f.resumo) + "</div>";
      if (f.chave === "reputacao") h += blocoReputacao();
      if (f.chave === "busca") h += blocoBusca();
      if (f.chave === "fichas") h += blocoFichas();

      if (f.chave === "mapa") {
        h += '<button type="button" class="abrir" data-ferr="mapa">Ver o mapa desta tela</button>';
      } else if (ROTAS[f.chave]) {
        h += '<a class="abrir" href="' + ROTAS[f.chave] + '">Abrir a ferramenta →</a>';
      } else {
        h += '<div class="nao-tem">O número já existe. A tela desta ferramenta ainda não foi construída.</div>';
      }
      return h + "</article>";
    }).join("");

    alvo.querySelectorAll("[data-ferr]").forEach(function (b) {
      b.addEventListener("click", function () { selecionarFerramenta(b.getAttribute("data-ferr")); });
    });
  }

  function classeSelo(s) {
    var k = String(s || "").toUpperCase();
    if (k === "RA1000" || k === "GREAT") return "selo-bom";
    if (k === "REGULAR") return "selo-medio";
    return "selo-ruim";
  }

  function blocoReputacao() {
    var rep = (dados.reputacao_das_redes || []).slice()
      .sort(function (a, b) { return (b.reclamacoes || 0) - (a.reclamacoes || 0); });
    if (!rep.length) return "";
    var max = rep[0].reclamacoes || 1;
    return '<div style="margin-top:4px">' + rep.map(function (x) {
      return '<div class="rep-linha' + (x.nossa ? " nossa" : "") + '">' +
        '<span class="marca-nome">' + esc(x.marca) + "</span>" +
        '<span class="trilho"><i style="width:' + Math.max(1.5, (x.reclamacoes / max) * 100) + '%"></i></span>' +
        '<span class="fim"><span class="n">' + br(x.reclamacoes) + "</span>" +
        '<span class="selo ' + classeSelo(x.selo) + '">' + esc(String(x.selo || "").replace(/_/g, " ")) + "</span>" +
        '<span class="n" style="min-width:26px">' + br(x.nota) + "</span></span></div>";
    }).join("") +
      '<div class="proveniencia-linha">reclamações registradas no Reclame Aqui · nota da própria fonte · medido em ' +
      dataBR(rep[0].medido_em) + "</div></div>";
  }

  function blocoBusca() {
    var pb = dados.presenca_na_busca || {};
    var chaves = Object.keys(pb);
    if (!chaves.length) return "";
    return '<div style="margin-top:4px">' + chaves.map(function (k) {
      var x = pb[k] || {};
      var dentro = x.dentro || 0, fora = x.fora || 0, total = dentro + fora;
      return '<div class="busca-linha"><div class="topo"><span class="termo">' + esc(k) + "</span>" +
        '<span class="cnt">' + br(dentro) + " aparições · " + br(fora) + " ausências</span></div>" +
        '<div class="trilho"><i style="width:' + (total ? (dentro / total) * 100 : 0) + '%"></i></div></div>';
    }).join("") +
      '<div class="proveniencia-linha">a barra cheia é onde a rede aparece; o vazio é onde a cidade procura e não encontra</div></div>';
  }

  function blocoFichas() {
    var fi = dados.fichas_da_rede || {};
    var cats = Object.keys(fi.por_categoria || {});
    if (!cats.length) return "";
    return '<div style="margin-top:2px">' + cats.map(function (k) {
      return '<div class="rep-linha"><span class="marca-nome">' + esc(k) + "</span>" +
        '<span class="trilho"><i style="width:' + (fi.conferidas ? (fi.por_categoria[k] / fi.conferidas) * 100 : 0) + '%"></i></span>' +
        '<span class="fim"><span class="n">' + br(fi.por_categoria[k]) + "</span></span></div>";
    }).join("") + "</div>";
  }

  /* ---------------- estado vazio ---------------- */

  function vazioEstado(t, d, q) {
    return '<div class="vazio-estado"><div class="t">' + esc(t) + "</div>" +
      '<div class="d">' + esc(d) + "</div>" +
      (q ? '<div class="q">' + esc(q) + "</div>" : "") + "</div>";
  }

  /* ---------------- busca global ---------------- */

  function indice() {
    var out = [];
    (dados.ferramentas || []).forEach(function (f) {
      out.push({ tipo: "ferramenta", rot: f.nome, acao: function () { selecionarFerramenta(f.chave); } });
    });
    ((manifesto || {}).pracas || []).forEach(function (p) {
      out.push({ tipo: "praça", rot: p.rotulo, href: "index.html#/praca/" + p.praca_id });
      (p.cidades || []).forEach(function (c) {
        if (c !== p.rotulo) out.push({ tipo: "cidade", rot: c, href: "index.html#/praca/" + p.praca_id });
      });
    });
    (dados.mapa || []).forEach(function (x) {
      out.push({
        tipo: "estado", rot: nomeUF(x.uf) + " · " + br(x.unidades) + " unidades",
        busca: x.uf + " " + nomeUF(x.uf),
        acao: function () { ufSel = null; alternarUF(x.uf); selecionarFerramenta("mapa"); }
      });
    });
    (dados.reputacao_das_redes || []).forEach(function (x) {
      out.push({ tipo: "rede", rot: x.marca, acao: function () { selecionarFerramenta("reputacao"); } });
    });
    return out;
  }

  function abrirBusca() {
    if (document.querySelector(".busca-cortina")) return;
    var idx = indice();
    var cortina = document.createElement("div");
    cortina.className = "busca-cortina";
    cortina.innerHTML = '<div class="busca-caixa"><header>' +
      '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" style="color:var(--t3)"><circle cx="11" cy="11" r="7"></circle><path d="m20 20-3.6-3.6"></path></svg>' +
      '<input type="search" placeholder="praça, cidade, estado, ferramenta…" aria-label="Buscar">' +
      "<kbd>esc</kbd></header><div class=\"busca-lista\"></div></div>";
    var caixa = cortina.querySelector(".busca-caixa");
    var input = cortina.querySelector("input");
    var listaEl = cortina.querySelector(".busca-lista");
    var sel = 0, vis = [];

    function pinta() {
      var q = input.value.trim();
      vis = (q ? idx.filter(function (i) {
        return chaveTexto((i.busca || "") + " " + i.rot + " " + i.tipo).indexOf(chaveTexto(q)) > -1;
      }) : idx).slice(0, 40);
      if (!vis.length) {
        listaEl.innerHTML = '<div class="busca-nada">Nada com esse nome nas ' +
          br(((manifesto || {}).pracas || []).length) + " praças medidas, nos " +
          br((dados.mapa || []).length) + " estados nem nas " + br((dados.ferramentas || []).length) + " ferramentas.</div>";
        return;
      }
      if (sel >= vis.length) sel = 0;
      listaEl.innerHTML = vis.map(function (i, n) {
        return '<button type="button" class="busca-item' + (n === sel ? " sel" : "") + '" data-n="' + n + '">' +
          '<span class="tipo">' + esc(i.tipo) + '</span><span class="rot">' + esc(i.rot) + "</span></button>";
      }).join("");
      listaEl.querySelectorAll(".busca-item").forEach(function (b) {
        b.addEventListener("click", function () { vai(vis[Number(b.getAttribute("data-n"))]); });
      });
    }
    function vai(i) {
      if (!i) return;
      fechar();
      if (i.href) location.href = i.href;
      else if (i.acao) i.acao();
    }
    function fechar() { cortina.remove(); document.removeEventListener("keydown", onKey); }
    function onKey(e) {
      if (e.key === "Escape") { fechar(); return; }
      if (e.key === "ArrowDown") { e.preventDefault(); sel = Math.min(sel + 1, vis.length - 1); pinta(); }
      if (e.key === "ArrowUp") { e.preventDefault(); sel = Math.max(sel - 1, 0); pinta(); }
      if (e.key === "Enter") { e.preventDefault(); vai(vis[sel]); }
    }
    cortina.addEventListener("click", function (e) { if (!caixa.contains(e.target)) fechar(); });
    input.addEventListener("input", function () { sel = 0; pinta(); });
    document.addEventListener("keydown", onKey);
    document.body.appendChild(cortina);
    input.focus();
    pinta();
  }

  /* ---------------- arranque ---------------- */

  function aplicarTema(t) {
    document.documentElement.setAttribute("data-theme", t);
    try { localStorage.setItem(CHAVE_TEMA, t); } catch (e) { }
  }

  function iniciar() {
    try {
      var salvo = localStorage.getItem(CHAVE_TEMA);
      if (salvo) document.documentElement.setAttribute("data-theme", salvo);
    } catch (e) { }

    el("tema").addEventListener("click", function () {
      aplicarTema(document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark");
    });
    el("busca").addEventListener("click", abrirBusca);
    document.addEventListener("keydown", function (e) {
      if (e.key === "/" && !/^(INPUT|TEXTAREA)$/.test(e.target.tagName || "")) {
        e.preventDefault();
        abrirBusca();
      }
    });
    window.addEventListener("resize", function () { esconderDica(); });

    Promise.all([
      fetch(BASE + "manifest.json", { cache: "no-cache" }).then(function (r) { return r.json(); }),
      fetch(BASE + "franqueadora.json", { cache: "no-cache" }).then(function (r) {
        if (!r.ok) throw new Error("sem franqueadora.json");
        return r.json();
      })
    ]).then(function (r) {
      manifesto = r[0];
      dados = r[1];
      el("corte").textContent = "corte " + dataBR(dados.corte);
      pintarCabecalho();
      pintarBarra();
      pintarRodapeBarra();
      pintarMapa();
      pintarMudou();
      pintarFerramentas();
      document.body.setAttribute("aria-busy", "false");
    }).catch(function () {
      el("trabalho").innerHTML = vazioEstado(
        "A sala de comando não encontrou os arquivos da coleta",
        "Esta tela lê dados/portal/manifest.json e dados/portal/franqueadora.json e desenha a partir deles. Sirva a pasta por HTTP — abrir o arquivo direto do disco bloqueia a leitura.",
        "dados/portal/franqueadora.json");
      document.body.setAttribute("aria-busy", "false");
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar);
  else iniciar();
})();
