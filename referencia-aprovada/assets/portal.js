/* ============================================================
   Portal de Inteligência OrthoDontic — o casco
   O casco NUNCA calcula. Todo valor exibido sai de dados/portal/.
   O que ele faz: buscar, ordenar por campo existente,
   filtrar por campo existente e formatar data.
   ============================================================ */
(function () {
  "use strict";

  var BASE = "./dados/portal/";
  var CHAVE_TEMA = "od-portal-tema";

  var manifesto = null;
  var versao = "0";
  var cache = new Map();
  var app, entradasEl, corteEl;

  /* ================= utilidades ================= */

  function esc(v) {
    if (v === null || v === undefined) return "";
    return String(v)
      .replace(/&amp;/g, "&")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function md(v) {
    return esc(v)
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/\*([^*]+)\*/g, "<em>$1</em>");
  }

  function tem(v) { return v !== null && v !== undefined && v !== ""; }

  /* comparação sem acento: o leitor digita "macapa" e espera achar "Macapá" */
  function chave(v) {
    return String(v == null ? "" : v)
      .normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  }

  function el(tag, attrs, html) {
    var n = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    if (html !== undefined) n.innerHTML = html;
    return n;
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
  function pc(v) {
    if (!tem(v)) return "—";
    return (Number(v) * 100).toLocaleString("pt-BR", { maximumFractionDigits: 1 }) + "%";
  }
  function larg(v) { return (tem(v) ? Math.max(0, Math.min(100, Number(v) * 100)) : 0) + "%"; }

  /* ================= carga ================= */

  function carregar(rel) {
    var chave = versao + "|" + rel;
    if (cache.has(chave)) return cache.get(chave);
    var p = fetch(BASE + rel, { cache: "no-cache" }).then(function (r) {
      if (!r.ok) throw new Error("sem arquivo: " + rel);
      return r.json();
    });
    cache.set(chave, p);
    return p;
  }

  function tentar(rel) {
    return carregar(rel).catch(function () { return null; });
  }

  /* ================= peças ================= */

  function vazio(titulo, desc, qual) {
    return '<div class="vazio"><div class="t">' + esc(titulo) + "</div>" +
      '<div class="d">' + esc(desc) + "</div>" +
      (qual ? '<div class="q">' + esc(qual) + "</div>" : "") + "</div>";
  }

  function proc(partes) {
    var vs = (partes || []).filter(tem).map(esc);
    if (!vs.length) return "";
    return '<div class="proc">' + vs.join(" · ") + "</div>";
  }

  function ressalvas(lista, rot) {
    if (!lista || !lista.length) return "";
    return '<div class="ressalvas"><div class="rot">' + esc(rot || "Leia antes dos números") + "</div><ul>" +
      lista.map(function (r) { return "<li>" + md(r) + "</li>"; }).join("") + "</ul></div>";
  }

  function fato(v, k) {
    return '<div class="fato"><div class="v">' + br(v) + '</div><div class="k">' + esc(k) + "</div></div>";
  }

  function selo(v) {
    if (!tem(v)) return '<span class="selo selo-sem">constância não medida</span>';
    var k = String(v).toLowerCase();
    var c = k.indexOf("opera") === 0 ? "selo-operacao"
      : k.indexOf("campanha") === 0 ? "selo-campanha"
        : k.indexOf("rajada") === 0 ? "selo-rajada" : "selo-parada";
    return '<span class="selo ' + c + '">' + esc(v) + "</span>";
  }

  function legendaSelos() {
    return '<div class="legenda-selos">' +
      "<div>" + selo("OPERAÇÃO") + " 10 meses ou mais seguidos</div>" +
      "<div>" + selo("campanha") + " 3 a 9 meses</div>" +
      "<div>" + selo("rajada") + " um mês concentra 60% ou mais</div>" +
      "<div>" + selo("parada") + " sem movimento nos últimos 60 dias</div>" +
      "</div>";
  }

  function ritmoCel(l) {
    if (!tem(l.ritmo)) return "—";
    var fonte = l.ritmo_fonte || l.fonte || "";
    if (/estimado|~/.test(String(fonte))) {
      return '<span class="estimado" title="medido pelo intervalo da amostra; a próxima coleta confirma pelo contador do Google">~' + br(l.ritmo) + "</span>";
    }
    return br(l.ritmo);
  }

  function ordenador(est) {
    return function (a, b) {
      var av = a[est.campo], bv = b[est.campo];
      if (av === null || av === undefined) return 1;
      if (bv === null || bv === undefined) return -1;
      if (typeof av === "number" && typeof bv === "number") return (av - bv) * est.dir;
      return String(av).localeCompare(String(bv), "pt-BR") * est.dir;
    };
  }

  function cabecalhos(cols, est) {
    return cols.map(function (c) {
      var atual = est.campo === c[0];
      return "<th" + (atual ? ' aria-sort="' + (est.dir === 1 ? "ascending" : "descending") + '"' : "") +
        '><button type="button" data-campo="' + c[0] + '">' + esc(c[1]) +
        (atual ? (est.dir === 1 ? " ▲" : " ▼") : "") + "</button></th>";
    }).join("");
  }

  function ligarOrdenacao(alvo, est, redesenhar) {
    alvo.querySelectorAll("th button").forEach(function (b) {
      b.addEventListener("click", function () {
        var c = b.getAttribute("data-campo");
        if (est.campo === c) est.dir = -est.dir;
        else { est.campo = c; est.dir = -1; }
        redesenhar();
      });
    });
  }

  function quadros(cheios, total, mini) {
    var n = Number(total) || 0, c = Number(cheios) || 0, s = "";
    for (var i = 0; i < n; i++) s += '<div class="quadro' + (i < c ? " cheio" : "") + '"></div>';
    return '<div class="quadros' + (mini ? " mini" : "") + '">' + s + "</div>";
  }

  /* ================= navegação ================= */

  var ENTRADAS = [
    { id: "rede", rot: "Rede", quem: "franqueadora", rota: "#/rede" },
    { id: "radar", rot: "Radar de Oportunidade", quem: "expansão", rota: "#/radar" },
    { id: "praca", rot: "Praça", quem: "consultor", rota: "#/praca" },
    { id: "plano", rot: "Plano", quem: "franqueado", rota: "#/plano" }
  ];

  function familia(rota) {
    var r = String(rota || "").replace(/^#\//, "").split("/")[0];
    if (r === "radar" || r === "oportunidade") return "radar";
    if (r === "praca" || r === "captacao") return "praca";
    if (r === "plano") return "plano";
    return "rede";
  }

  function pintarEntradas() {
    var fam = familia(location.hash || "#/rede");
    entradasEl.innerHTML = ENTRADAS.map(function (e) {
      return '<button type="button" class="entrada" data-rota="' + e.rota + '" aria-current="' + (e.id === fam) + '">' +
        "<b>" + esc(e.rot) + "</b><i>" + esc(e.quem) + "</i></button>";
    }).join("");
    entradasEl.querySelectorAll("[data-rota]").forEach(function (b) {
      b.addEventListener("click", function () { location.hash = b.getAttribute("data-rota"); });
    });
  }

  function pracaDoManifesto(id) {
    if (!manifesto) return null;
    var achou = (manifesto.pracas || []).filter(function (p) { return p.praca_id === id; })[0];
    return achou || null;
  }

  function abasPracas(rotaBase, atual, exigeTela) {
    var lista = (manifesto && manifesto.pracas) || [];
    var vis = lista.filter(function (p) { return !exigeTela || (p.tem || []).indexOf(exigeTela) > -1; });
    if (!vis.length) return "";
    return '<div class="filtros" style="margin-bottom:18px">' + vis.map(function (p) {
      return '<button type="button" class="chip" data-ir="' + rotaBase + "/" + esc(p.praca_id) + '" aria-pressed="' +
        (p.praca_id === atual) + '">' + esc(p.rotulo) + "</button>";
    }).join("") + "</div>";
  }

  function ligarIr() {
    app.querySelectorAll("[data-ir]").forEach(function (b) {
      b.addEventListener("click", function () { location.hash = b.getAttribute("data-ir"); });
    });
  }

  /* ================= gaveta de evidência ================= */

  var evidencias = null;

  function ligarEvidencias() {
    app.querySelectorAll("[data-ev]").forEach(function (b) {
      b.addEventListener("click", function () { abrirEvidencia(b.getAttribute("data-ev")); });
    });
  }

  function abrirEvidencia(chave) {
    tentar("evidencias.json").then(function (todas) {
      evidencias = todas;
      var e = todas && todas[chave];
      var corpo;
      if (!e) {
        corpo = vazio("Este número ainda não tem ficha",
          "A procedência dele não veio nesta coleta.", "evidencias.json → " + chave);
      } else {
        corpo =
          (e.contra ? '<div class="gaveta-secao contra" style="margin-top:0;margin-bottom:22px"><div class="rot">O que pesa contra</div><p>' + md(e.contra) + "</p></div>" : "") +
          '<div class="gaveta-valor">' + esc(e.valor) + "</div>" +
          '<p class="leg">' + md(e.legenda) + "</p>" +
          (e.leitura ? '<div class="gaveta-secao"><div class="rot">A leitura</div><p>' + md(e.leitura) + "</p></div>" : "") +
          '<div class="gaveta-secao"><div class="rot">Ficha técnica</div><dl class="ficha">' +
          linhaFicha("base", e.n) + linhaFicha("corte", e.corte) + linhaFicha("fonte", e.fonte) +
          linhaFicha("filtro", e.filtro) + linhaFicha("confiança", e.conf) +
          linhaFicha("lista de palavras", e.tax) + "</dl></div>";
      }
      var cortina = el("div", { class: "cortina" });
      var gaveta = el("aside", { class: "gaveta", role: "dialog", "aria-label": "De onde veio o número" });
      gaveta.innerHTML =
        '<div class="gaveta-cab"><span class="rot">De onde veio o número</span>' +
        '<button type="button" class="fechar" aria-label="Fechar">✕</button></div>' +
        '<div class="gaveta-corpo">' +
        (e && e.titulo ? '<h2 style="margin-bottom:16px">' + esc(e.titulo) + "</h2>" : "") +
        corpo + "</div>";
      function fechar() { cortina.remove(); gaveta.remove(); document.removeEventListener("keydown", onEsc); }
      function onEsc(ev) { if (ev.key === "Escape") fechar(); }
      cortina.addEventListener("click", fechar);
      gaveta.querySelector(".fechar").addEventListener("click", fechar);
      document.addEventListener("keydown", onEsc);
      document.body.appendChild(cortina);
      document.body.appendChild(gaveta);
      gaveta.querySelector(".fechar").focus();
    });
  }

  function linhaFicha(k, v) {
    if (!tem(v)) return "";
    return "<dt>" + esc(k) + "</dt><dd>" + esc(v) + "</dd>";
  }

  /* ================= TELA: REDE ================= */

  function telaRede() {
    return Promise.all([tentar("rede.json"), tentar("rede_cruzamento.json")]).then(function (r) {
      var rede = r[0], cruz = r[1];
      var h = '<div class="tela-topo"><div class="olho">Rede · a franqueadora</div>' +
        "<h1>A leitura da rede</h1>" +
        '<p class="sub">O que vale para a rede inteira e o que vale para uma cidade só. A cobertura vem primeiro, porque isto é uma amostra.</p></div>';

      if (!rede && !cruz) {
        app.innerHTML = h + vazio("Esta rodada ainda não tem a leitura de rede",
          "Os arquivos da tela não vieram nesta coleta.", "rede.json · rede_cruzamento.json");
        return;
      }

      if (rede && rede.cobertura) {
        var cob = rede.cobertura;
        h += '<div class="cobertura"><div class="grande">' + br(cob.ouvidas) + " / " + br(cob.total) + "</div>" +
          '<div class="txt">praças medidas de ' + br(cob.total) + " unidades. O resto da rede ainda não foi ouvido.</div>" +
          '<div class="barra"><i style="width:' + (cob.total ? (cob.ouvidas / cob.total * 100) : 0) + '%;min-width:4px"></i></div></div>';
      }

      if (cruz) {
        h += '<div class="bloco"><div class="bloco-cab"><h2>O que a rede compra</h2></div>';
        if (cruz.pesa_contra && cruz.pesa_contra.length) h += ressalvas(cruz.pesa_contra, "O que pesa contra");
        h += '<p class="manchete">' + br(cruz.sustentam) + " de " + br(cruz.unidades) +
          " unidades sustentam; " + br(cruz.paradas) + " pararam.</p>";
        h += '<div class="fatos" style="margin-top:18px">' +
          fato(cruz.pracas, "praças") + fato(cruz.unidades, "unidades") + fato(cruz.clinicas, "clínicas medidas") +
          fato(cruz.sustentam, "sustentam") + fato(cruz.campanha, "em campanha") + fato(cruz.paradas, "pararam") + "</div>";
        h += proc(["fonte: rede_cruzamento.json", "gerado em " + dataBR(cruz.gerado_em)]) + "</div>";

        h += '<div class="bloco"><div class="bloco-cab"><h2>O placar das unidades</h2>' +
          '<span class="proc" style="border:0;margin:0;padding:0">' + br((cruz.placar || []).length) + " linhas</span></div>" +
          '<div class="filtros" id="filtros-placar"></div><div class="tabela-wrap" id="tabela-placar"></div>' +
          legendaSelos() + proc(["fonte: rede_cruzamento.json", "gerado em " + dataBR(cruz.gerado_em)]) + "</div>";

        var tv = cruz.territorio_vazio;
        if (tv && Object.keys(tv).length) {
          h += '<div class="bloco"><div class="bloco-cab"><h2>Território vazio</h2>' +
            '<span class="proc" style="border:0;margin:0;padding:0">assunto que ninguém ocupa, por praça</span></div><div class="nuvem">' +
            Object.keys(tv).map(function (k) {
              return "<span>" + esc(k.replace(/_/g, " ")) + " <b>" + br((tv[k] || []).length) + "</b></span>";
            }).join("") + "</div>" + proc(["fonte: rede_cruzamento.json"]) + "</div>";
        }
      }

      if (rede && rede.sinais && rede.sinais.length) {
        var porSev = {};
        rede.sinais.forEach(function (s) { porSev[s.sev] = (porSev[s.sev] || 0) + 1; });
        h += '<div class="bloco"><div class="bloco-cab"><h2>Os sinais abertos</h2></div>';
        Object.keys(porSev).forEach(function (k) {
          h += '<div class="agrupado"><span class="qtd">' + br(porSev[k]) + "</span>" +
            '<span class="sev sev-' + esc(k) + '">' + esc(k) + "</span>" +
            '<span class="txt">' + (porSev[k] === 1 ? "um sinal nesta severidade" : "sinais nesta severidade") + "</span></div>";
        });
        h += '<div class="sinais" style="margin-top:14px">' + rede.sinais.map(function (s) {
          return '<article class="sinal"><div class="sinal-cab">' +
            '<span class="sev sev-' + esc(s.sev) + '">' + esc(s.sev) + "</span>" +
            (s.praca_id ? '<button type="button" class="chip" data-ir="#/praca/' + esc(s.praca_id) + '">' + esc(rotuloDe(s.praca_id)) + "</button>" : "") +
            "</div><h3>" + esc(s.t) + "</h3><p>" + md(s.b) + "</p>" +
            '<div class="acao"><b>O que fazer</b>' + md(s.a) + "</div>" +
            (s.ev ? '<button type="button" class="ver-ev" data-ev="' + esc(s.ev) + '">De onde veio o número</button>' : "") +
            "</article>";
        }).join("") + "</div>";
        h += proc(["fonte: rede.json", "corte " + dataBR(rede.corte)]) + "</div>";
      }

      if (rede && rede.praca_linhas && rede.praca_linhas.length) {
        h += '<div class="bloco"><div class="bloco-cab"><h2>As praças medidas</h2></div>' +
          '<div class="filtros" id="filtros-pracas"></div><div class="tabela-wrap" id="tabela-pracas"></div>' +
          proc(["fonte: rede.json", "corte " + dataBR(rede.corte)]) + "</div>";
      }

      app.innerHTML = h;
      if (cruz) montarPlacar(cruz.placar || []);
      if (rede && rede.praca_linhas && rede.praca_linhas.length) montarPracas(rede.praca_linhas);
      ligarEvidencias();
      ligarIr();
    });
  }

  function rotuloDe(id) {
    var p = pracaDoManifesto(id);
    return p ? p.rotulo : id;
  }

  var estPlacar = { uf: null, selo: null, campo: "ritmo", dir: -1, q: "" };

  function montarPlacar(linhas) {
    var alvo = document.getElementById("tabela-placar");
    var filtros = document.getElementById("filtros-placar");
    if (!alvo || !filtros) return;

    var ufs = [], selos = [];
    linhas.forEach(function (l) {
      if (l.uf && ufs.indexOf(l.uf) < 0) ufs.push(l.uf);
      if (l.selo && selos.indexOf(l.selo) < 0) selos.push(l.selo);
    });
    ufs.sort();

    filtros.innerHTML =
      '<input class="busca-campo" id="q-placar" type="search" placeholder="filtrar unidade…" value="' + esc(estPlacar.q) + '">' +
      '<button type="button" class="chip" data-uf="" aria-pressed="' + (!estPlacar.uf) + '">todas as UF</button>' +
      ufs.map(function (u) {
        return '<button type="button" class="chip" data-uf="' + esc(u) + '" aria-pressed="' + (estPlacar.uf === u) + '">' + esc(u) + "</button>";
      }).join("") +
      selos.map(function (s) {
        return '<button type="button" class="chip" data-selo="' + esc(s) + '" aria-pressed="' + (estPlacar.selo === s) + '">' + esc(s) + "</button>";
      }).join("");

    filtros.querySelectorAll("[data-uf]").forEach(function (b) {
      b.addEventListener("click", function () { estPlacar.uf = b.getAttribute("data-uf") || null; montarPlacar(linhas); });
    });
    filtros.querySelectorAll("[data-selo]").forEach(function (b) {
      b.addEventListener("click", function () {
        var v = b.getAttribute("data-selo");
        estPlacar.selo = estPlacar.selo === v ? null : v;
        montarPlacar(linhas);
      });
    });
    var qi = document.getElementById("q-placar");
    qi.addEventListener("input", function () {
      estPlacar.q = qi.value;
      var pos = qi.selectionStart;
      montarPlacar(linhas);
      var novo = document.getElementById("q-placar");
      if (novo) { novo.focus(); try { novo.setSelectionRange(pos, pos); } catch (e) { } }
    });

    var vis = linhas.slice();
    if (estPlacar.uf) vis = vis.filter(function (l) { return l.uf === estPlacar.uf; });
    if (estPlacar.selo) vis = vis.filter(function (l) { return l.selo === estPlacar.selo; });
    if (estPlacar.q.trim()) {
      var q = estPlacar.q.trim().toLowerCase();
      vis = vis.filter(function (l) { return chave((l.nome || "") + " " + (l.rotulo || "")).indexOf(chave(estPlacar.q)) > -1; });
    }
    vis.sort(ordenador(estPlacar));

    var cols = [["nome", "unidade"], ["rotulo", "praça"], ["total", "avaliações"], ["nota", "nota"],
    ["ritmo", "ritmo por mês"], ["meses", "meses seguidos"], ["posicao", "posição na praça"]];

    if (!vis.length) {
      alvo.innerHTML = vazio("Nenhuma unidade neste filtro", "Tire um filtro para ver as outras.", "");
      return;
    }

    alvo.innerHTML = '<table class="grade"><thead><tr>' + cabecalhos(cols, estPlacar) + "</tr></thead><tbody>" +
      vis.map(function (l) {
        return '<tr class="nossa"><td class="nome">' + esc(l.nome) + "</td><td>" + esc(l.rotulo) + "</td>" +
          '<td class="n">' + br(l.total) + '</td><td class="n">' + br(l.nota) + "</td>" +
          '<td class="n">' + ritmoCel(l) + "</td>" +
          '<td class="n">' + (tem(l.meses) ? br(l.meses) : "—") + (l.selo ? " " + selo(l.selo) : "") + "</td>" +
          '<td class="n">' + (tem(l.posicao) ? br(l.posicao) + " de " + br(l.de) : "—") + "</td></tr>";
      }).join("") + "</tbody></table>";

    ligarOrdenacao(alvo, estPlacar, function () { montarPlacar(linhas); });
  }

  var estPracas = { uf: null, campo: "avaliacoes", dir: -1 };

  function montarPracas(linhas) {
    var alvo = document.getElementById("tabela-pracas");
    var filtros = document.getElementById("filtros-pracas");
    if (!alvo || !filtros) return;

    var ufs = [];
    linhas.forEach(function (l) { (l.uf || []).forEach(function (u) { if (ufs.indexOf(u) < 0) ufs.push(u); }); });
    ufs.sort();

    filtros.innerHTML = '<button type="button" class="chip" data-uf="" aria-pressed="' + (!estPracas.uf) + '">todas as UF</button>' +
      ufs.map(function (u) {
        return '<button type="button" class="chip" data-uf="' + esc(u) + '" aria-pressed="' + (estPracas.uf === u) + '">' + esc(u) + "</button>";
      }).join("");
    filtros.querySelectorAll("[data-uf]").forEach(function (b) {
      b.addEventListener("click", function () { estPracas.uf = b.getAttribute("data-uf") || null; montarPracas(linhas); });
    });

    var vis = linhas.slice();
    if (estPracas.uf) vis = vis.filter(function (l) { return (l.uf || []).indexOf(estPracas.uf) > -1; });
    vis.sort(ordenador(estPracas));

    var cols = [["rotulo", "praça"], ["papel", "papel"], ["nota", "nota"], ["avaliacoes", "avaliações"], ["atendimento_pct", "falam de atendimento"]];

    alvo.innerHTML = '<table class="grade"><thead><tr>' + cabecalhos(cols, estPracas) + "<th></th></tr></thead><tbody>" +
      vis.map(function (l) {
        return '<tr><td class="nome">' + esc(l.rotulo) + "</td>" +
          "<td>" + (tem(l.papel) ? esc(l.papel) : "—") + "</td>" +
          '<td class="n">' + br(l.nota) + '</td><td class="n">' + br(l.avaliacoes) + "</td>" +
          '<td class="n">' + pc(l.atendimento_pct) + (tem(l.atendimento_n) ? " de " + br(l.atendimento_n) : "") + "</td>" +
          '<td><button type="button" class="chip" data-ir="#/praca/' + esc(l.praca_id) + '">ficha</button></td></tr>';
      }).join("") + "</tbody></table>";

    ligarOrdenacao(alvo, estPracas, function () { montarPracas(linhas); });
    ligarIr();
  }

  /* ================= TELA: ACHADOS ================= */

  var ESTADOS = [
    ["hipotese", "SINAL ISOLADO", "vimos em 1 ou 2 praças"],
    ["candidata", "SE REPETE", "vimos em 3 ou mais"],
    ["constante", "VALE PARA A REDE", "vimos em praças bem diferentes"],
    ["doutrina", "VIROU REGRA", "a rede decidiu agir"]
  ];

  function telaAchados() {
    return tentar("achados.json").then(function (d) {
      var h = '<div class="tela-topo"><div class="olho">Rede · a franqueadora</div>' +
        "<h1>O que aprendemos</h1>" +
        '<p class="sub">Um achado só sobe de degrau quando praças diferentes confirmam. Esta tela mostra em que degrau cada um está — e os que caíram.</p></div>';
      if (!d) {
        app.innerHTML = h + vazio("Esta rodada ainda não tem achados", "O arquivo não veio nesta coleta.", "achados.json");
        return;
      }
      if (d.nota_teto) h += ressalvas([d.nota_teto], "Por que nada virou regra ainda");

      var e = d.estados || {};
      h += '<div class="bloco"><div class="escada">' +
        ESTADOS.map(function (s) {
          var n = e[s[0]] || 0;
          return '<div class="degrau' + (n > 0 ? " ativo" : "") + '"><div class="v">' + br(n) + "</div>" +
            '<div class="k">' + esc(s[1]) + '</div><div class="h">' + esc(s[2]) + "</div></div>";
        }).join("") +
        '<div class="degrau caiu"><div class="v">' + br(e.derrubada || 0) + "</div>" +
        '<div class="k">CAIU</div><div class="h">uma praça mostrou o contrário</div></div>' +
        "</div></div>";

      var achados = d.achados || [];
      var caidos = achados.filter(function (a) { return a.estado === "derrubada"; });
      var vivos = achados.filter(function (a) { return a.estado !== "derrubada"; });

      h += '<div class="bloco"><div class="bloco-cab"><h2>Os achados que se repetem</h2>' +
        '<span class="proc" style="border:0;margin:0;padding:0">' + br(vivos.length) + "</span></div>" +
        '<div class="sinais">' + vivos.map(cartaoAchado).join("") + "</div></div>";

      if (caidos.length) {
        h += '<div class="bloco"><div class="bloco-cab"><h2>O que caiu</h2>' +
          '<span class="proc" style="border:0;margin:0;padding:0">mostrar isto é o que prova que a escada é honesta</span></div>' +
          '<div class="sinais">' + caidos.map(cartaoAchado).join("") + "</div></div>";
      }

      var vars = d.variaveis || [];
      if (vars.length) {
        var chaves = Object.keys(vars[0]).filter(function (k) { return k !== "dim"; });
        h += '<div class="bloco"><div class="bloco-cab"><h2>As variáveis</h2>' +
          '<span class="proc" style="border:0;margin:0;padding:0">o que jamais pode ser nacionalizado</span></div>' +
          '<div class="tabela-wrap"><table class="grade"><thead><tr><th>dimensão</th>' +
          chaves.map(function (k) { return "<th>" + esc(rotuloDe(k)) + "</th>"; }).join("") +
          "</tr></thead><tbody>" +
          vars.map(function (v) {
            return '<tr><td class="nome">' + esc(v.dim) + "</td>" +
              chaves.map(function (k) { return '<td style="white-space:normal;min-width:170px">' + esc(v[k]) + "</td>"; }).join("") + "</tr>";
          }).join("") + "</tbody></table></div></div>";
      }

      app.innerHTML = h;
      ligarEvidencias();
      ligarIr();
    });
  }

  function cartaoAchado(a) {
    var caiu = a.estado === "derrubada";
    return '<article class="achado' + (caiu ? " caiu" : "") + '">' +
      '<div class="sinal-cab"><span class="selo ' + (caiu ? "selo-rajada" : "selo-operacao") + '">' +
      esc(caiu ? "CAIU" : "SE REPETE") + "</span>" +
      (a.n && !caiu ? '<span class="proc" style="border:0;margin:0;padding:0">' + esc(a.n) + " praças</span>" : "") +
      (caiu && a.derrubada_por ? '<span class="proc" style="border:0;margin:0;padding:0">por ' + esc(rotuloDe(a.derrubada_por)) + "</span>" : "") +
      "</div><h3>" + esc(a.t) + "</h3>" +
      (a.ev && a.ev.length ? '<div class="achado-ev">' + a.ev.map(function (p) {
        return "<span>" + esc(p[0]) + " · " + esc(p[1]) + "</span>";
      }).join("") + "</div>" : "") +
      (a.ref ? '<button type="button" class="ver-ev" data-ev="' + esc(a.ref) + '">De onde veio o número</button>' : "") +
      "</article>";
  }

  /* ================= TELA: CORRETOR ================= */

  function telaCorretor() {
    return tentar("corretor.json").then(function (d) {
      var h = '<div class="tela-topo"><div class="olho">Rede · o consultor de campo</div>' +
        "<h1>Corretor de campanha</h1>" +
        '<p class="sub">O que uma peça nacional encontra em cada praça ouvida.</p></div>';
      if (!d) {
        app.innerHTML = h + vazio("Esta rodada não tem corretor", "O arquivo não veio nesta coleta.", "corretor.json");
        return;
      }
      if (d.peca_exemplo) {
        h += '<div class="bloco"><div class="bloco-cab"><h2>A peça em análise</h2></div>' +
          '<p class="serif" style="font-size:19px;line-height:1.5;margin:0">' + esc(d.peca_exemplo) + "</p></div>";
      }
      var vs = d.vereditos || [];
      if (vs.length) {
        h += '<div class="sinais">' + vs.map(function (v) {
          var k = String(v.v || "");
          var c = k === "conflito" ? "selo-rajada" : k === "risco" ? "selo-campanha" : k === "adaptar" ? "selo-campanha" : "selo-operacao";
          return '<article class="sinal"><div class="sinal-cab">' +
            '<span class="selo ' + c + '">' + esc(k.replace(/_/g, " ")) + "</span>" +
            '<button type="button" class="chip" data-ir="#/praca/' + esc(v.praca_id) + '">' + esc(rotuloDe(v.praca_id)) + "</button></div>" +
            "<p>" + md(v.t) + "</p>" +
            '<div class="acao"><b>' + (k === "conflito" ? "Bloqueado" : "Sugestão") + "</b>" + esc(v.sug) + "</div></article>";
        }).join("") + "</div>";
      }
      var ds = d.descida || [];
      if (ds.length) {
        h += '<div class="bloco" style="margin-top:18px"><div class="bloco-cab"><h2>A campanha nacional chega à cadeira?</h2></div>';
        h += '<div class="fatos">' + ds.map(function (x) {
          if (tem(x.com_embaixador)) return miniFato(x.com_embaixador, x.posts_analisados, "publicações de unidade com o embaixador");
          if (tem(x.com_jingle)) return miniFato(x.com_jingle, x.posts_analisados, "criativos nacionais com o jingle");
          if (tem(x.mencoes_embaixador)) return miniFato(x.mencoes_embaixador, x.vozes, "menções espontâneas ao embaixador");
          return "";
        }).join("") + "</div>";
        if (d.descida_nota) h += '<p class="serif" style="margin:20px 0 0;font-size:15px;line-height:1.6">' + esc(d.descida_nota) + "</p>";
        h += proc(["fonte: corretor.json", "corte " + dataBR(ds[0].snapshot_date), ds[0].amostra]);
        h += '<div style="margin-top:14px"><button type="button" class="ver-ev" data-ev="telo">De onde veio o número</button></div></div>';
      }
      app.innerHTML = h;
      ligarEvidencias();
      ligarIr();
    });
  }

  function miniFato(a, b, k) {
    return '<div class="fato" style="min-width:160px"><div class="v">' + br(a) +
      '<span style="font-size:15px;color:var(--t3)"> de ' + br(b) + "</span></div>" +
      '<div class="k">' + esc(k) + "</div></div>";
  }

  /* ================= TELA: RADAR ================= */

  function telaRadar() {
    return tentar("radar.json").then(function (d) {
      var h = '<div class="tela-topo"><div class="olho">Radar · a expansão</div>' +
        "<h1>Onde abrir unidade nova</h1>" +
        '<p class="sub">A única tela que aparece como receita, não como custo.</p></div>';
      if (!d) {
        app.innerHTML = h + vazio("Esta rodada não tem radar", "O arquivo não veio nesta coleta.", "radar.json");
        return;
      }

      h += ressalvas(d.ressalvas, "O que esta medição não enxerga");

      var r = d.rede_hoje;
      if (r) {
        h += '<div class="bloco"><div class="bloco-cab"><h2>A rede hoje</h2></div>';
        if (r.ufs_sem_nenhuma_unidade && r.ufs_sem_nenhuma_unidade.length) {
          h += '<p class="manchete">' + esc(r.ufs_sem_nenhuma_unidade.join(", ")) +
            " não têm uma única unidade.</p>";
        }
        h += '<div class="fatos" style="margin-top:18px">' +
          fato(r.unidades, "unidades") + fato(r.abertas, "abertas") +
          fato(r.em_implantacao, "em implantação") + fato(r.cidades, "cidades") + "</div>";
        h += proc(["fonte: " + r.fonte, "corte " + dataBR(r.corte)]) + "</div>";
      }

      var ops = d.oportunidades || [];
      h += '<div class="bloco-cab" style="margin:26px 0 14px"><h2>As oportunidades</h2>' +
        '<span class="proc" style="border:0;margin:0;padding:0">' + br(ops.length) + " cidades, na ordem</span></div>";
      if (!ops.length) {
        h += vazio("Nenhuma cidade no radar desta rodada", "A varredura não produziu candidata.", "radar.json → oportunidades");
      } else {
        h += ops.map(cartaoOportunidade).join("");
      }

      var jt = d.ja_tem_unidade || [];
      var nc = d.nao_conferidas || [];
      h += '<div class="bloco-cab" style="margin:26px 0 14px"><h2>As que saíram do radar</h2>' +
        '<span class="proc" style="border:0;margin:0;padding:0">mostrar isto é o que prova que a checagem funciona</span></div>';
      if (!jt.length && !nc.length) {
        h += vazio("Nenhuma cidade saiu nesta rodada", "Nesta varredura, todas as candidatas passaram na checagem.", "radar.json → ja_tem_unidade · nao_conferidas");
      } else {
        h += jt.map(function (c) {
          return '<div class="saiu"><div class="rotulo">' + esc(c.rotulo) + "</div>" +
            '<div class="motivo">' + esc(c.leitura || (c.conferencia && c.conferencia.motivo)) + "</div>" +
            proc((c.conferencia && c.conferencia.fontes) || []) + "</div>";
        }).join("");
        h += nc.map(function (c) {
          return '<div class="saiu nao-conferida"><div class="rotulo">' + esc(c.rotulo) + "</div>" +
            '<div class="motivo">não deu para conferir contra a lista oficial</div></div>';
        }).join("");
      }

      app.innerHTML = h;
      ligarIr();
    });
  }

  function cartaoOportunidade(o) {
    var h = '<article class="oportunidade"><div class="op-cab">' +
      '<div class="rotulo">' + esc(o.rotulo) + "</div>" +
      (o.leitura ? '<div class="leitura">' + esc(o.leitura) + "</div>" : "") + "</div>";

    h += '<div class="op-numeros">' +
      fato(o.populacao, "habitantes") +
      fato(o.alvo_30_45, "de 30 a 45 anos") +
      fato(o.alvo_9_15, "de 9 a 15 anos") +
      fato(o.clinicas_fortes, "clínicas fortes") +
      fato(o.lider_avaliacoes, "avaliações do líder") +
      fato(o.hab_por_clinica_forte, "hab. por clínica forte") + "</div>";

    h += '<div class="op-corpo">';
    if (o.defesa && o.defesa.length) {
      h += '<div class="defesa">' + o.defesa.map(function (p) { return "<p>" + md(p) + "</p>"; }).join("") + "</div>";
    } else {
      h += vazio("Esta cidade ainda não tem defesa escrita", "A varredura entrou, mas o texto da defesa não veio.", "radar.json → defesa");
    }

    var g = o.gemea;
    if (g) {
      h += '<div class="gemea"><p class="frase">' + md(g.frase) + "</p>";
      if (g.unidades_de_la && g.unidades_de_la.length) {
        h += '<div class="faixa"><div class="rot">O que a unidade faz lá</div>' + g.unidades_de_la.map(function (u) {
          return '<div class="faixa-linha"><span class="un">' + esc(u.nome) +
            "<i>" + br(u.total) + " avaliações · nota " + br(u.nota) +
            (tem(u.posicao) ? " · " + br(u.posicao) + "ª de " + br(u.de) : "") + "</i></span>" +
            '<span class="rt">' + ritmoCel(u) + "/mês</span>" +
            '<span class="rt">' + (tem(u.meses) ? br(u.meses) + " meses" : "—") + "</span>" +
            selo(u.selo) + "</div>";
        }).join("") + "</div>";
      }
      if (g.onde_difere && g.onde_difere.length) {
        h += '<div class="difere"><div class="rot">Onde os eixos não batem</div><ul>' +
          g.onde_difere.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul></div>";
      }
      h += "</div>";
    }

    if (o.estudo) {
      var id = String(o.estudo).split("/")[1];
      h += '<div style="margin-top:16px"><button type="button" class="ver-ev" data-ir="#/oportunidade/' + esc(id) + '">Abrir o estudo da cidade</button></div>';
    }
    h += "</div></article>";
    return h;
  }

  function telaOportunidade(id) {
    return tentar("oportunidade/" + id + ".json").then(function (d) {
      var h = '<div class="tela-topo"><div class="olho">Radar · a expansão</div>';
      if (!d) {
        app.innerHTML = h + "<h1>" + esc(id) + "</h1></div>" +
          vazio("Esta cidade ainda não tem estudo", "A cidade está no radar, mas o estudo completo não veio nesta coleta.",
            "dados/portal/oportunidade/" + id + ".json");
        return;
      }
      h += "<h1>" + esc(d.rotulo) + "</h1>" +
        '<p class="sub">O estudo completo da praça de oportunidade.</p></div>';

      h += '<div class="bloco"><div class="fatos">' +
        fato(d.populacao, "habitantes") + fato(d.alvo_30_45, "de 30 a 45 anos") +
        fato(d.alvo_9_15, "de 9 a 15 anos") + fato(d.renda_per_capita, "massa salarial por pessoa") +
        fato(d.clinicas_varridas, "clínicas varridas") + fato(d.clinicas_fortes, "clínicas fortes") +
        "</div>" + proc(["corte " + dataBR(d.snapshot_date)]) + "</div>";

      var c = d.conferencia;
      if (c) {
        h += '<div class="bloco"><div class="bloco-cab"><h2>A checagem</h2>' +
          (c.livre ? selo("praça livre") : selo("já tem unidade")) + "</div>" +
          '<p class="serif" style="margin:0;font-size:14.5px;line-height:1.6">' + esc(c.motivo) + "</p>" +
          proc(["unidades da rede achadas: " + br(c.unidades_da_rede)]) + "</div>";
      }

      var k = d.concorrencia;
      if (k) {
        h += '<div class="bloco"><div class="bloco-cab"><h2>A concorrência</h2></div><div class="fatos">' +
          fato(k.varridas, "varridas") + fato(k.fortes, "fortes") + fato(k.medias, "médias") + fato(k.fracas, "fracas") +
          fato(k.lider_avaliacoes, "avaliações do líder") + fato(k.de_rede_nacional, "de rede nacional") +
          fato(k.sem_site_pct, "% sem site") + fato(k.enderecos_com_ficha_dobrada, "endereços com ficha dobrada") +
          "</div>";
        if (k.maiores && k.maiores.length) {
          h += '<div class="tabela-wrap" style="margin-top:18px"><table class="grade"><thead><tr>' +
            "<th>clínica</th><th>avaliações</th><th>nota</th><th>endereço</th></tr></thead><tbody>" +
            k.maiores.map(function (m) {
              return '<tr><td class="nome">' + esc(m.nome) + '</td><td class="n">' + br(m.avaliacoes) +
                '</td><td class="n">' + br(m.nota) + '</td><td style="white-space:normal;min-width:220px;color:var(--t3)">' +
                esc(m.endereco || "—") + "</td></tr>";
            }).join("") + "</tbody></table></div>";
        }
        h += proc(["corte " + dataBR(d.snapshot_date)]) + "</div>";
      }

      if (d.gemea) {
        h += '<div class="bloco"><div class="bloco-cab"><h2>A gêmea</h2></div>' +
          '<div class="gemea" style="margin-top:0"><p class="frase">' + md(d.gemea.frase) + "</p>" +
          (d.gemea.onde_difere && d.gemea.onde_difere.length ?
            '<div class="difere"><div class="rot">Onde os eixos não batem</div><ul>' +
            d.gemea.onde_difere.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul></div>" : "") +
          "</div>";
        var fx = d.faixa_das_parecidas || [];
        if (fx.length) {
          h += '<div class="faixa"><div class="rot">O que as praças parecidas entregam — a diferença entre as pontas não é a cidade, é a operação</div>' +
            fx.map(function (u) {
              return '<div class="faixa-linha"><span class="un">' + esc(u.unidade) + "<i>" + esc(u.praca) + "</i></span>" +
                '<span class="rt">' + ritmoCel(u) + "/mês</span>" +
                '<span class="rt">' + (tem(u.meses) ? br(u.meses) + " meses" : "—") + "</span>" +
                selo(u.selo) + "</div>" +
                (u.fonte && /⚠/.test(u.fonte) ? '<div class="proc" style="border:0;padding:4px 0 0;margin:0">' + esc(u.fonte) + "</div>" : "");
            }).join("") + "</div>";
        }
        h += "</div>";
      }

      var im = d.cidade_numeros && d.cidade_numeros.imprensa;
      if (im && im.length) {
        h += '<div class="bloco"><div class="bloco-cab"><h2>A imprensa da cidade</h2></div><div class="nuvem">' +
          im.map(function (v) { return "<span>" + esc(v.veiculo) + " <b>" + br(v.materias) + "</b></span>"; }).join("") +
          "</div></div>";
      }

      h += '<div style="margin-top:18px"><button type="button" class="chip" data-ir="#/radar">← voltar ao radar</button></div>';
      app.innerHTML = h;
      ligarIr();
    });
  }

  /* ================= TELA: PRAÇA ================= */

  function telaPraca(id) {
    if (!id) {
      var lista = (manifesto && manifesto.pracas) || [];
      if (!lista.length) {
        app.innerHTML = vazio("Nenhuma praça no manifesto", "A coleta ainda não indexou praça alguma.", "manifest.json → pracas");
        return Promise.resolve();
      }
      location.replace("#/praca/" + lista[0].praca_id);
      return Promise.resolve();
    }
    return Promise.all([tentar("pracas/" + id + ".json"), tentar("rede_cruzamento.json")]).then(function (r) {
      var d = r[0], cruz = r[1];
      var h = '<div class="tela-topo"><div class="olho">Praça · o consultor</div>';

      if (!d) {
        h += "<h1>" + esc(rotuloDe(id)) + "</h1></div>" + abasPracas("#/praca", id, "praca");
        app.innerHTML = h + vazio("Esta praça ainda não tem ficha",
          "A praça está no manifesto, mas a ficha dela não veio nesta coleta.",
          "dados/portal/pracas/" + id + ".json");
        ligarIr();
        return;
      }

      h += "<h1>" + esc(d.rotulo) + "</h1>";
      if (d.eyebrow) h += '<p class="sub" style="font-family:var(--mono);font-size:12.5px">' + esc(d.eyebrow) + "</p>";
      h += "</div>";
      h += abasPracas("#/praca", id, "praca");

      if (d.tese_titulo || d.tese) {
        h += '<div class="bloco">' +
          (d.tese_titulo ? '<p class="manchete">' + esc(d.tese_titulo) + "</p>" : "") +
          (d.tese ? '<p class="serif" style="font-size:16px;line-height:1.65;color:var(--t2);margin:10px 0 0;max-width:72ch">' + esc(d.tese) + "</p>" : "") +
          proc([d.base, "corte " + dataBR(d.corte)]) + "</div>";
      }

      /* o ritmo abre a ficha — é ele que decide se a clínica opera ou fez campanha */
      var unidades = (cruz && cruz.placar ? cruz.placar : []).filter(function (l) { return l.praca === id; });
      h += '<div class="bloco"><div class="bloco-cab"><h2>O ritmo das unidades</h2>' +
        '<span class="proc" style="border:0;margin:0;padding:0">avaliações novas por mês, e há quantos meses seguidos</span></div>';
      if (!unidades.length) {
        h += vazio("Esta praça ainda não tem leitura de ritmo",
          "O cruzamento da rede não trouxe unidade desta praça nesta coleta.", "rede_cruzamento.json → placar");
      } else {
        h += unidades.map(function (u) {
          return '<div class="faixa-linha"><span class="un">' + esc(u.nome) +
            "<i>" + br(u.total) + " avaliações · nota " + br(u.nota) +
            (tem(u.posicao) ? " · " + br(u.posicao) + "ª de " + br(u.de) + " na praça" : "") + "</i></span>" +
            '<span class="rt">' + ritmoCel(u) + "/mês</span>" +
            '<span class="rt">' + (tem(u.meses) ? br(u.meses) + " meses" : "—") + "</span>" +
            selo(u.selo) + "</div>";
        }).join("") + legendaSelos();
        h += '<div class="proc">Esta coleta mede o ritmo e há quantos meses ele se mantém — não mês a mês.</div>';
      }
      h += "</div>";

      if (d.sazonalidade && d.sazonalidade.length) {
        var maxi = 0;
        d.sazonalidade.forEach(function (s) { maxi = Math.max(maxi, Number(s.indice || s.indice_max || 0)); });
        h += '<div class="bloco"><div class="bloco-cab"><h2>A temporada</h2>' +
          '<span class="proc" style="border:0;margin:0;padding:0">série de ' + br(d.sazonalidade[0].serie_anos) + " anos</span></div>" +
          '<div class="sazo">' + d.sazonalidade.map(function (s) {
            var v = tem(s.indice) ? s.indice : s.indice_max;
            var rot = tem(s.indice) ? br(s.indice) : br(s.indice_min) + "–" + br(s.indice_max);
            var alt = maxi ? Math.max(6, (Number(v) / maxi) * 100) : 6;
            return '<div class="sazo-col"><span class="v">' + rot + "</span>" +
              '<span class="bar' + (s.vale ? " vale" : "") + '" style="height:' + alt + '%"></span>' +
              '<span class="m">' + esc(s.mes) + "</span></div>";
          }).join("") + "</div>" +
          proc(["região " + d.sazonalidade[0].regiao, "corte " + dataBR(d.sazonalidade[0].snapshot_date)]) + "</div>";
      }

      if (d.funil && d.funil.estagios) {
        h += '<div class="bloco"><div class="bloco-cab"><h2>O caminho do paciente</h2></div>';
        if (d.funil.ressalva) h += ressalvas([d.funil.ressalva], "Leia antes dos números");
        var topo = Number(d.funil.estagios[0] && d.funil.estagios[0].v) || 1;
        h += d.funil.estagios.map(function (s) {
          return '<div class="funil-linha"><span class="l">' + esc(s.l) + "</span>" +
            '<span class="trilha"><i style="width:' + (tem(s.pct) ? larg(s.pct) : Math.max(2, (s.v / topo) * 100) + "%") + '"></i>' +
            (tem(s.regua) ? '<u style="left:' + larg(s.regua) + '"></u>' : "") + "</span>" +
            '<span class="v">' + (tem(s.pct) ? pc(s.pct) : br(s.v)) +
            "<i>" + (tem(s.pct) ? "N " + br(s.v) : "topo") + (tem(s.regua) ? " · régua " + pc(s.regua) : "") + "</i></span></div>";
        }).join("");
        h += '<div class="fatos" style="margin-top:16px">' +
          fato(d.funil.base_ativa, "base ativa") + fato(d.funil.contratos_mes, "contratos no mês") +
          fato(d.funil.meta_rede, "meta da rede") + "</div>";
        h += '<div style="margin-top:14px"><button type="button" class="ver-ev" data-ev="agendamento">De onde veio o número</button></div>';
        h += "</div>";
      }

      if (d.placar && d.placar.length) {
        h += '<div class="bloco"><div class="bloco-cab"><h2>O placar da praça</h2>' +
          (d.placar_nota ? '<span class="proc" style="border:0;margin:0;padding:0">' + esc(d.placar_nota) + "</span>" : "") + "</div>" +
          '<div class="tabela-wrap"><table class="grade"><thead><tr><th>clínica</th><th>tipo</th><th>nota</th><th>avaliações</th></tr></thead><tbody>' +
          d.placar.map(function (c) {
            return "<tr" + (c.proprio ? ' class="nossa"' : "") + '><td class="nome">' + esc(c.nome) + "</td>" +
              "<td>" + (c.tipo && c.tipo !== "PREENCHER" ? esc(String(c.tipo).replace(/_/g, " ")) : '<span style="color:var(--t3)">—</span>') + "</td>" +
              '<td class="n">' + br(c.nota) + '</td><td class="n">' + br(c.avaliacoes) + "</td></tr>";
          }).join("") + "</tbody></table></div>" + proc(["corte " + dataBR(d.corte)]) + "</div>";
      }

      if (d.temas && d.temas.length) {
        var t0 = d.temas[0];
        var ord = d.temas.slice().sort(function (a, b) { return (b.pct || 0) - (a.pct || 0); });
        h += '<div class="bloco"><div class="bloco-cab"><h2>Do que o paciente fala</h2>' +
          '<span class="proc" style="border:0;margin:0;padding:0">' + br(t0.n) + " avaliações com texto</span></div>" +
          ord.map(function (t) {
            return '<div class="temas-linha"><span class="l">' + esc(String(t.tema).replace(/_/g, " ")) + "</span>" +
              '<span class="trilha"><i style="width:' + larg(t.pct) + '"></i></span>' +
              '<span class="v">' + pc(t.pct) + "</span></div>";
          }).join("") +
          proc(["fonte: " + t0.fonte, "lista de palavras " + t0.taxonomia_versao, "corte " + dataBR(t0.snapshot_date)]) + "</div>";
      }

      if (d.dna && d.dna.length) {
        h += '<div class="bloco"><div class="bloco-cab"><h2>O jeito de falar da praça</h2></div><div class="dna">' +
          d.dna.map(function (x) {
            return '<div class="dna-item' + (x.proibicao ? " proibicao" : "") + '">' +
              '<div class="l">' + esc(x.l) + '</div><div class="t">' + esc(x.t) + "</div></div>";
          }).join("") + "</div></div>";
      }

      if (d.citacoes && d.citacoes.length) {
        h += '<div class="bloco"><div class="bloco-cab"><h2>Vozes reais</h2></div>' +
          d.citacoes.map(function (c) {
            return '<div class="citacao"><q>' + esc(c.t) + '</q><div class="c">' + esc(c.c) + "</div></div>";
          }).join("") + "</div>";
      }

      if (d.plano && d.plano.length) {
        h += '<div class="bloco"><div class="bloco-cab"><h2>O plano da praça</h2>' +
          '<span class="proc" style="border:0;margin:0;padding:0">a versão do consultor</span></div><ol class="plano-praca" style="padding-left:20px;margin:0">' +
          d.plano.map(function (p) {
            return "<li><b>" + esc(p.t) + "</b>" + (p.d ? " — " + esc(p.d) : "") +
              (p.prazo || p.esforco ? "<br><i>" + esc([p.prazo, p.esforco].filter(tem).join(" · ")) + "</i>" : "") + "</li>";
          }).join("") + "</ol></div>";
      }

      var temPlano = (pracaDoManifesto(id) || {}).tem || [];
      h += '<div class="filtros" style="margin-top:22px">';
      if (temPlano.indexOf("plano") > -1) h += '<button type="button" class="chip" data-ir="#/plano/' + esc(id) + '">Ver o plano do franqueado →</button>';
      if (temPlano.indexOf("captacao") > -1) h += '<button type="button" class="chip" data-ir="#/captacao/' + esc(id) + '">Ver onde captar →</button>';
      h += "</div>";

      app.innerHTML = h;
      ligarEvidencias();
      ligarIr();
    });
  }

  /* ================= TELA: PLANO DO FRANQUEADO ================= */

  function telaPlano(id) {
    if (!id) {
      var lista = ((manifesto && manifesto.pracas) || []).filter(function (p) { return (p.tem || []).indexOf("plano") > -1; });
      if (!lista.length) {
        app.innerHTML = vazio("Nenhuma praça tem plano ainda", "A coleta ainda não produziu plano.", "manifest.json → pracas[].tem");
        return Promise.resolve();
      }
      location.replace("#/plano/" + lista[0].praca_id);
      return Promise.resolve();
    }
    return Promise.all([tentar("planos/" + id + ".json"), tentar("captacao/" + id + ".json")]).then(function (r) {
      var d = r[0], cap = r[1];
      var h = '<div class="tela-topo"><div class="olho">Plano · o franqueado</div>';

      if (!d) {
        h += "<h1>" + esc(rotuloDe(id)) + "</h1></div>" + abasPracas("#/plano", id, "plano");
        app.innerHTML = h + vazio("Esta praça ainda não tem plano de captação",
          "A praça está no manifesto, mas o plano dela não veio nesta coleta.",
          "dados/portal/planos/" + id + ".json");
        ligarIr();
        return;
      }

      h += "<h1>" + esc(d.rotulo) + "</h1></div>";
      h += abasPracas("#/plano", id, "plano");

      var p = d.placar || {};
      h += '<div class="bloco placar-topo">' +
        '<p class="placar-frase">' + (d.frase_do_topo ? md(d.frase_do_topo) :
          "A sua clínica aparece em <strong>" + br(p.aparece_em) + " das " + br(p.de) + " buscas</strong> que testamos na sua cidade.") + "</p>" +
        quadros(p.aparece_em, p.de) +
        proc(["corte " + dataBR(d.snapshot_date)]) + "</div>";

      var tarefas = (d.tarefas || []).slice(0, 5);
      h += tarefas.map(function (t, i) {
        var b = '<div class="tarefa"><div class="tarefa-n">' + String(i + 1).padStart(2, "0") + "</div>" +
          '<div class="tarefa-corpo"><h3>' + esc(t.titulo) + "</h3>" +
          '<div class="etiquetas">' +
          (tem(t.custo) ? '<span class="etiqueta' + (/R\$\s*0/.test(t.custo) ? " gratis" : "") + '">' + esc(t.custo) + "</span>" : "") +
          (tem(t.tempo) ? '<span class="etiqueta">' + esc(t.tempo) + "</span>" : "") +
          (tem(t.quem) ? '<span class="etiqueta">' + esc(t.quem) + "</span>" : "") + "</div>";

        if (i === 0 && cap && cap.por_familia) {
          var fams = Object.keys(cap.por_familia);
          b += '<div class="familias">' + fams.map(function (k) {
            var f = cap.por_familia[k];
            var total = (f.dentro || 0) + (f.fora || 0);
            if (!total) return "";
            return '<div class="familia"><div class="rot">busca com “' + esc(k) + '”</div>' +
              quadros(f.dentro, total, true) +
              '<div class="cnt">' + br(f.dentro) + " de " + br(total) + "</div></div>";
          }).join("") + "</div>";
        }

        if (t.o_que_esta_acontecendo && t.o_que_esta_acontecendo.length) {
          b += '<div class="acontecendo">';
          var buffer = [];
          t.o_que_esta_acontecendo.forEach(function (par) {
            if (String(par).trim().indexOf("·") === 0) {
              buffer.push("<li>" + md(String(par).replace(/^\s*·\s*/, "")) + "</li>");
            } else {
              if (buffer.length) { b += "<ul>" + buffer.join("") + "</ul>"; buffer = []; }
              b += "<p>" + md(par) + "</p>";
            }
          });
          if (buffer.length) b += "<ul>" + buffer.join("") + "</ul>";
          b += "</div>";
        }

        if (t.o_que_fazer && t.o_que_fazer.length) {
          b += '<ol class="passos">' + t.o_que_fazer.map(function (x) { return "<li>" + md(x) + "</li>"; }).join("") + "</ol>";
        }
        if (tem(t.nao_faca)) {
          b += '<div class="nao-faca"><div class="rot">Não faça</div><p>' + md(t.nao_faca) + "</p></div>";
        }
        if (tem(t.como_saber)) {
          b += '<div class="como-saber">' + esc(t.como_saber) + "</div>";
        }
        return b + "</div></div>";
      }).join("");

      if (!tarefas.length) {
        h += vazio("Este plano ainda não tem tarefa", "O plano existe, mas veio sem tarefa nesta coleta.", "planos/" + id + ".json → tarefas");
      }

      h += ressalvas(d.ressalvas, "O que esta medição não enxerga");
      h += '<div class="filtros"><button type="button" class="chip" data-ir="#/praca/' + esc(id) + '">Ver a ficha da praça →</button>' +
        '<button type="button" class="chip" data-ir="#/captacao/' + esc(id) + '">Ver a versão analítica →</button></div>';

      app.innerHTML = h;
      ligarIr();
    });
  }

  /* ================= TELA: CAPTAÇÃO ================= */

  function telaCaptacao(id) {
    if (!id) {
      var lista = ((manifesto && manifesto.pracas) || []).filter(function (p) { return (p.tem || []).indexOf("captacao") > -1; });
      if (!lista.length) {
        app.innerHTML = vazio("Nenhuma praça tem medição de captação", "A coleta ainda não produziu.", "manifest.json");
        return Promise.resolve();
      }
      location.replace("#/captacao/" + lista[0].praca_id);
      return Promise.resolve();
    }
    return tentar("captacao/" + id + ".json").then(function (d) {
      var h = '<div class="tela-topo"><div class="olho">Praça · a versão analítica</div>';
      if (!d) {
        h += "<h1>" + esc(rotuloDe(id)) + "</h1></div>" + abasPracas("#/captacao", id, "captacao");
        app.innerHTML = h + vazio("Esta praça ainda não tem medição de captação",
          "A praça está no manifesto, mas o arquivo não veio nesta coleta.",
          "dados/portal/captacao/" + id + ".json");
        ligarIr();
        return;
      }
      h += "<h1>Onde captar · " + esc(d.rotulo) + "</h1>" +
        '<p class="sub">A mesma medição do plano, sem tradução.</p></div>';
      h += abasPracas("#/captacao", id, "captacao");

      h += '<div class="bloco"><div class="fatos">' +
        fato(d.portas_total, "buscas encontradas") + fato(d.portas_medidas, "buscas medidas") +
        fato((d.dentro || []).length, "aparece") + fato((d.fora || []).length, "não aparece") +
        fato(d.avaliacoes_lidas, "avaliações lidas") + fato(d.anuncios_ativos, "anúncios ativos na praça") +
        "</div>" + proc(["corte " + dataBR(d.snapshot_date), (d.dentro && d.dentro[0] ? d.dentro[0].fonte : "")]) + "</div>";

      if (d.por_familia) {
        h += '<div class="bloco"><div class="bloco-cab"><h2>Por família de busca</h2></div><div class="familias">' +
          Object.keys(d.por_familia).map(function (k) {
            var f = d.por_familia[k];
            var total = (f.dentro || 0) + (f.fora || 0);
            return '<div class="familia"><div class="rot">' + esc(k) + "</div>" +
              quadros(f.dentro, total, true) +
              '<div class="cnt">' + br(f.dentro) + " de " + br(total) + "</div></div>";
          }).join("") + "</div></div>";
      }

      ["dentro", "fora", "sem_dono"].forEach(function (k) {
        var lista = d[k] || [];
        var rot = k === "dentro" ? "Onde a unidade aparece" : k === "fora" ? "Onde a unidade não aparece" : "Buscas sem dono";
        h += '<div class="bloco"><div class="bloco-cab"><h2>' + esc(rot) + "</h2>" +
          '<span class="proc" style="border:0;margin:0;padding:0">' + br(lista.length) + "</span></div>";
        if (!lista.length) {
          h += vazio("Nada nesta lista", "Nesta coleta a lista veio vazia.", "captacao/" + id + ".json → " + k);
        } else {
          h += lista.map(function (x) {
            return '<div class="porta"><div class="porta-cab"><span class="frase">' + esc(x.frase) + "</span>" +
              '<span class="etiqueta">' + esc(x.intencao) + "</span>" +
              '<span class="pos">' + (tem(x.mapa && x.mapa.nossa_posicao) ? "posição " + br(x.mapa.nossa_posicao) + " de " + br(x.mapa.resultados) : "fora das " + br(x.mapa && x.mapa.resultados) + " primeiras") + "</span></div>" +
              '<div class="porta-quem">' + ((x.mapa && x.mapa.quem) || []).map(function (q) {
                var nosso = /orthodontic/i.test(q.nome);
                return '<span class="' + (nosso ? "nosso" : "") + '">' + br(q.posicao) + ". " + esc(q.nome) + " · " + br(q.avaliacoes) + "</span>";
              }).join("") + "</div></div>";
          }).join("");
        }
        h += "</div>";
      });

      if (d.bairros && d.bairros.length) {
        h += '<div class="bloco"><div class="bloco-cab"><h2>Bairros que a cidade digita</h2>' +
          '<span class="proc" style="border:0;margin:0;padding:0">confira antes de usar — a máquina às vezes traz rua ou faculdade</span></div>' +
          '<div class="nuvem">' + d.bairros.map(function (b) { return "<span>" + esc(b) + "</span>"; }).join("") + "</div></div>";
      }
      if (d.convenios && d.convenios.length) {
        h += '<div class="bloco"><div class="bloco-cab"><h2>Convênios que a cidade procura</h2></div><div class="nuvem">' +
          d.convenios.map(function (b) { return "<span>" + esc(b) + "</span>"; }).join("") + "</div></div>";
      }
      if (d.servicos_citados && d.servicos_citados.length) {
        h += '<div class="bloco"><div class="bloco-cab"><h2>O que o paciente diz que foi buscar</h2></div>';
        var maxs = d.servicos_citados[0].mencoes || 1;
        h += d.servicos_citados.map(function (s) {
          return '<div class="temas-linha"><span class="l">' + esc(s.servico) + "</span>" +
            '<span class="trilha"><i style="width:' + Math.max(2, (s.mencoes / maxs) * 100) + '%"></i></span>' +
            '<span class="v">' + br(s.mencoes) + "</span></div>";
        }).join("");
        h += proc([br(d.avaliacoes_lidas) + " avaliações lidas"]) + "</div>";
      }
      if (d.vocabulario_da_praca && d.vocabulario_da_praca.length) {
        h += '<div class="bloco"><div class="bloco-cab"><h2>As palavras da praça</h2></div><div class="nuvem">' +
          d.vocabulario_da_praca.slice(0, 40).map(function (v) {
            return "<span>" + esc(v[0]) + " <b>" + br(v[1]) + "</b></span>";
          }).join("") + "</div></div>";
      }
      if (d.anunciantes_descartados && d.anunciantes_descartados.length) {
        h += '<div class="bloco"><div class="bloco-cab"><h2>Anunciantes descartados</h2>' +
          '<span class="proc" style="border:0;margin:0;padding:0">a busca trouxe, mas não são da praça</span></div><div class="nuvem">' +
          d.anunciantes_descartados.map(function (a) { return "<span>" + esc(a) + "</span>"; }).join("") + "</div></div>";
      }

      h += '<div class="filtros"><button type="button" class="chip" data-ir="#/plano/' + esc(id) + '">Ver a versão do franqueado →</button></div>';
      app.innerHTML = h;
      ligarIr();
    });
  }

  /* ================= busca global =================
     O índice base é barato: manifesto, cruzamento, radar e achados — quatro arquivos.
     Os concorrentes vivem dentro da ficha de cada praça, então entram em segundo plano,
     com fila limitada, depois que a busca abre. Nunca bloqueia o desenho de uma tela. */

  var indice = null;
  var indexadas = 0;
  var aIndexar = 0;
  var aoIndexar = null;

  function juntar(lista, item) {
    var k = chave(item.rot) + "|" + item.tipo;
    if (lista.__vistos && lista.__vistos[k]) return;
    if (!lista.__vistos) lista.__vistos = {};
    lista.__vistos[k] = true;
    lista.push(item);
  }

  function indexarPracas(lista) {
    var ids = (manifesto && manifesto.arquivos && manifesto.arquivos.pracas) || [];
    aIndexar = ids.length;
    indexadas = 0;
    var fila = ids.slice();
    var emVoo = 0;

    function proxima() {
      if (!fila.length) return;
      var id = fila.shift();
      emVoo++;
      tentar("pracas/" + id + ".json").then(function (d) {
        if (d && d.placar) {
          d.placar.forEach(function (c) {
            if (!tem(c.nome)) return;
            juntar(lista, {
              tipo: c.proprio ? "unidade" : "concorrente",
              rot: c.nome + " · " + (d.rotulo || id),
              ir: "#/praca/" + id
            });
          });
        }
        indexadas++;
        emVoo--;
        if (aoIndexar) aoIndexar();
        proxima();
      });
    }
    for (var i = 0; i < 4 && i < fila.length + emVoo; i++) proxima();
  }

  function montarIndice() {
    if (indice) return Promise.resolve(indice);
    return Promise.all([tentar("rede_cruzamento.json"), tentar("radar.json"), tentar("achados.json")]).then(function (r) {
      var out = [];
      ((manifesto && manifesto.pracas) || []).forEach(function (p) {
        juntar(out, { tipo: "praça", rot: p.rotulo, ir: "#/praca/" + p.praca_id });
        if ((p.tem || []).indexOf("plano") > -1) juntar(out, { tipo: "plano", rot: p.rotulo, ir: "#/plano/" + p.praca_id });
        if ((p.tem || []).indexOf("captacao") > -1) juntar(out, { tipo: "captação", rot: p.rotulo, ir: "#/captacao/" + p.praca_id });
      });
      if (r[0] && r[0].placar) r[0].placar.forEach(function (u) {
        juntar(out, { tipo: "unidade", rot: u.nome + " · " + u.rotulo, ir: "#/praca/" + u.praca });
      });
      if (r[1]) {
        (r[1].oportunidades || []).forEach(function (o) {
          var alvo = "#/oportunidade/" + String(o.estudo || "").split("/")[1];
          juntar(out, { tipo: "radar", rot: o.rotulo, ir: alvo });
          (o.maiores || []).forEach(function (m) {
            juntar(out, { tipo: "concorrente", rot: m.nome + " · " + o.rotulo, ir: alvo });
          });
        });
        (r[1].ja_tem_unidade || []).forEach(function (o) {
          juntar(out, { tipo: "saiu do radar", rot: o.rotulo, ir: "#/radar" });
        });
      }
      if (r[2]) (r[2].achados || []).forEach(function (a) {
        juntar(out, { tipo: a.estado === "derrubada" ? "caiu" : "achado", rot: a.t, ir: "#/achados" });
      });
      indice = out;
      indexarPracas(out);
      return out;
    });
  }

  function abrirBusca() {
    montarIndice().then(function (idx) {
      var cortina = el("div", { class: "busca-cortina" });
      cortina.innerHTML = '<div class="busca-caixa"><header>' +
        '<span class="proc" style="border:0;margin:0;padding:0">buscar</span>' +
        '<input type="search" placeholder="praça, unidade, concorrente, cidade, achado…" aria-label="Buscar">' +
        "<kbd>esc</kbd></header>" +
        '<div class="busca-lista"></div><div class="busca-status"></div></div>';
      var caixa = cortina.querySelector(".busca-caixa");
      var input = cortina.querySelector("input");
      var listaEl = cortina.querySelector(".busca-lista");
      var statusEl = cortina.querySelector(".busca-status");
      var sel = 0, vis = [];

      function status() {
        if (!statusEl) return;
        statusEl.textContent = indexadas >= aIndexar
          ? "praças, unidades, concorrentes, cidades do radar e achados"
          : "indexando concorrentes · " + indexadas + " de " + aIndexar + " praças";
      }

      function pinta() {
        var q = input.value.trim();
        vis = (q ? idx.filter(function (i) { return chave(i.rot + " " + i.tipo).indexOf(chave(q)) > -1; }) : idx).slice(0, 40);
        status();
        if (!vis.length) {
          listaEl.innerHTML = '<div style="padding:26px 18px;text-align:center;color:var(--t3);font-size:13.5px;line-height:1.6">' +
            (indexadas < aIndexar
              ? "Nada ainda. Os concorrentes das praças estão sendo indexados — " + indexadas + " de " + aIndexar + "."
              : "Nada com esse nome nas " + aIndexar + " praças coletadas, no radar e nos achados.") +
            "</div>";
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
      function vai(i) { if (i) { location.hash = i.ir; fechar(); } }
      function fechar() { aoIndexar = null; cortina.remove(); document.removeEventListener("keydown", onKey); }
      function onKey(e) {
        if (e.key === "Escape") { fechar(); return; }
        if (e.key === "ArrowDown") { e.preventDefault(); sel = Math.min(sel + 1, vis.length - 1); pinta(); }
        if (e.key === "ArrowUp") { e.preventDefault(); sel = Math.max(sel - 1, 0); pinta(); }
        if (e.key === "Enter") { e.preventDefault(); vai(vis[sel]); }
      }
      cortina.addEventListener("click", function (e) { if (!caixa.contains(e.target)) fechar(); });
      input.addEventListener("input", function () { sel = 0; pinta(); });
      aoIndexar = function () { if (document.body.contains(cortina)) pinta(); };
      document.addEventListener("keydown", onKey);
      document.body.appendChild(cortina);
      input.focus();
      pinta();
    });
  }

  /* ================= tema ================= */

  function aplicarTema(t) {
    document.documentElement.setAttribute("data-theme", t);
    try { localStorage.setItem(CHAVE_TEMA, t); } catch (e) { }
  }

  /* ================= roteador ================= */

  function rotear() {
    var partes = (location.hash || "#/rede").replace(/^#\//, "").split("/");
    var r = partes[0] || "rede";
    var id = partes[1] || "";
    pintarEntradas();
    app.setAttribute("aria-busy", "true");
    var p;
    if (r === "rede") p = telaRede();
    else if (r === "achados") p = telaAchados();
    else if (r === "corretor") p = telaCorretor();
    else if (r === "radar") p = telaRadar();
    else if (r === "oportunidade") p = telaOportunidade(id);
    else if (r === "praca") p = telaPraca(id);
    else if (r === "plano") p = telaPlano(id);
    else if (r === "captacao") p = telaCaptacao(id);
    else p = telaRede();
    Promise.resolve(p).then(function () {
      app.setAttribute("aria-busy", "false");
      window.scrollTo(0, 0);
    });
  }

  /* ================= arranque ================= */

  function iniciar() {
    app = document.getElementById("app");
    entradasEl = document.getElementById("entradas");
    corteEl = document.getElementById("corte");

    try {
      var salvo = localStorage.getItem(CHAVE_TEMA);
      if (salvo) document.documentElement.setAttribute("data-theme", salvo);
    } catch (e) { }

    document.getElementById("tema").addEventListener("click", function () {
      var atual = document.documentElement.getAttribute("data-theme");
      aplicarTema(atual === "light" ? "dark" : "light");
    });
    document.getElementById("busca").addEventListener("click", abrirBusca);
    document.addEventListener("keydown", function (e) {
      if (e.key === "/" && !/^(INPUT|TEXTAREA)$/.test((e.target.tagName || "")) && !document.querySelector(".busca-cortina")) {
        e.preventDefault();
        abrirBusca();
      }
    });

    carregar("manifest.json").then(function (m) {
      manifesto = m;
      versao = m.gerado_em || "0";
      cache.clear();
      cache.set(versao + "|manifest.json", Promise.resolve(m));
      var links = '<button type="button" class="chip" data-ir="#/achados">O que aprendemos</button>' +
        '<button type="button" class="chip" data-ir="#/corretor">Corretor</button>';
      corteEl.textContent = "corte " + dataBR(m.corte);
      document.getElementById("atalhos").innerHTML = links;
      document.getElementById("atalhos").querySelectorAll("[data-ir]").forEach(function (b) {
        b.addEventListener("click", function () { location.hash = b.getAttribute("data-ir"); });
      });
      window.addEventListener("hashchange", rotear);
      rotear();
    }).catch(function () {
      app.innerHTML = vazio("O portal não encontrou o índice da coleta",
        "O casco busca dados/portal/manifest.json e desenha a partir dele. Sem esse arquivo não há o que mostrar. Sirva a pasta por HTTP — abrir o arquivo direto do disco bloqueia a busca.",
        "dados/portal/manifest.json");
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar);
  else iniciar();
})();
