/* ============================================================
   Portal de Inteligência OrthoDontic — o casco

   Duas regras governam este arquivo:

   1. O CASCO NUNCA CALCULA. Nenhuma soma, média, porcentagem,
      ordenação por valor ou montagem de rótulo.
   2. CONTAR ARRAY NA TELA TAMBÉM É CALCULAR. Todo "quantos itens
      tem aqui" vem pronto num campo ao lado da lista. Onde este
      arquivo escreve um total, ele leu um campo — nunca .length.
      Número nenhum é escrito no HTML: todos mudam a cada coleta.
   ============================================================ */
(function () {
  "use strict";

  var BASE = "dados/portal/";
  var cache = {};
  var manifest = null;
  var franq = null;
  /* §6 · o cabeçalho de cada ferramenta vem pronto de cabecalhos.json. Título
     escrito à mão na tela é título que ninguém conserta pelo dado. */
  var CABS = {};

  /* ---------- utilidades ---------- */

  function el(id) { return document.getElementById(id); }

  function esc(s) {
    if (s === null || s === undefined) return "";
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function tem(v) { return v !== null && v !== undefined && v !== ""; }

  function br(n) {
    if (!tem(n)) return "—";
    if (typeof n !== "number") return esc(n);
    return n.toLocaleString("pt-BR");
  }

  function dec(n) {
    if (!tem(n)) return "—";
    if (typeof n !== "number") return esc(n);
    return n.toLocaleString("pt-BR", { maximumFractionDigits: 1 });
  }

  function plural(n, um, muitos) { return br(n) + " " + (n === 1 ? um : muitos); }

  var MES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];

  /* dia/mês, para a data que aparece ao lado de um texto e não pode roubar
     a linha — a data por extenso fica em data() */
  function dataCurta(s) {
    if (!tem(s)) return "—";
    var m = String(s).slice(0, 10).split("-");
    if (m.length !== 3) return esc(s);
    return m[2] + "/" + m[1];
  }

  function data(s) {
    if (!tem(s)) return "—";
    var m = String(s).slice(0, 10).split("-");
    if (m.length !== 3) return esc(s);
    return Number(m[2]) + "/" + MES[Number(m[1]) - 1] + "/" + m[0];
  }

  function chave(s) {
    return String(s || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  }

  function carregar(nome) {
    if (cache[nome]) return cache[nome];
    cache[nome] = fetch(BASE + nome + ".json").then(function (r) {
      if (!r.ok) throw new Error(nome + " não carregou (" + r.status + ")");
      return r.json();
    });
    return cache[nome];
  }

  var ROTULOS = {};

  function registrarRotulos(lista) {
    (lista || []).forEach(function (x) {
      if (!x || !tem(x.rotulo)) return;
      var id = x.praca_id || (tem(x.estudo) ? String(x.estudo).split("/").pop() : null);
      if (id) ROTULOS[id] = x.rotulo;
    });
  }

  function nomeDaPraca(id) { return ROTULOS[id] || id; }

  /* Os planos deixaram de ser por praça e passaram a ser por LOJA, então
     `manifest.arquivos.planos` traz local_id — que ROTULOS, indexado por
     praca_id, não conhece. O rótulo da loja vem pronto em fila.fila[]:
     esta tabela guarda os dois campos (cidade e unidade) por local_id. */
  var LOJAS = {};

  function registrarLojas(fila) {
    ((fila || {}).fila || []).forEach(function (c) {
      if (tem(c.local_id) && tem(c.rotulo)) LOJAS[c.local_id] = { rotulo: c.rotulo, unidade: c.unidade };
    });
  }

  function loja(id) { return LOJAS[id] || null; }

  /* o card do payload dá título, pergunta, frase e o número de cada tela.
     A chave nem sempre é o nome da tela (o card "alertas" abre "rede_inteira"),
     então a procura aceita as duas. */
  function card(k) {
    return (franq.cards || []).filter(function (c) { return c.tela === k || c.chave === k; })[0] || {};
  }

  /* ---------- peças ---------- */

  var COR = { vermelha: "var(--crit)", amarela: "var(--warn)", verde: "var(--ok)" };

  function vazio(t, d) {
    return '<div class="vazio"><div class="t">' + esc(t) + '</div><div class="d">' + esc(d) + "</div></div>";
  }

  function ressalvas(rot, itens) {
    if (!itens || !itens.length) return "";
    return '<div class="ressalvas"><div class="rot">' + esc(rot) + "</div><ul>" +
      itens.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul></div>";
  }

  /* §6 · a anatomia do cabeçalho, igual à do deck: sobrelinha, régua, título
     grande (quebra em duas linhas, não encolhe), a pergunta, e para quem serve.
     O método NÃO entra aqui — desce para o pé da tela. */
  function cab(k) { return CABS[k] || null; }

  function cabecalhoTela(k) {
    var c = cab(k);
    if (!c) return "";
    return '<div class="tela-cab"><div class="tc-sobre">' +
      '<span class="esq">' + esc(c.sobrelinha) + "</span>" +
      '<span class="dir">ORTHODONTIC INTELLIGENCE</span></div>' +
      "<h1>" + esc(c.titulo) + "</h1>" +
      (tem(c.pergunta) ? '<p class="tc-perg">' + esc(c.pergunta) + "</p>" : "") +
      ((c.para_quem || []).length
        ? '<div class="tc-para"><span class="k">para</span>' +
          c.para_quem.map(function (p) { return "<span>" + esc(p) + "</span>"; }).join("") + "</div>"
        : "") + "</div>";
  }

  /* §6.2 · a instrução de uso, entre o cabeçalho e o conteúdo */
  function comoLer(k) {
    var c = cab(k);
    if (!c || !tem(c.como_ler)) return "";
    return '<div class="como-ler"><span class="rot-sis">como ler</span><p>' + esc(c.como_ler) + "</p></div>";
  }

  /* §6.1 · método e fronteira no rodapé, sempre visíveis — nunca tooltip */
  function rodapeMetodo(k) {
    var c = cab(k);
    if (!c) return "";
    var h = "";
    if (tem(c.metodo)) {
      h += '<div class="mt-linha"><span class="k">como isto é medido</span><p>' + esc(c.metodo) + "</p></div>";
    }
    if (tem(c.o_que_nao_e)) {
      h += '<div class="mt-linha"><span class="k">o que isto não é</span><p>' + esc(c.o_que_nao_e) + "</p></div>";
    }
    return h ? '<div class="metodo-pe">' + h + "</div>" : "";
  }

  /* §7.3 · toda ferramenta fecha com a frase pronta que conclui a leitura */
  function fecho(txt) {
    if (!tem(txt)) return "";
    return '<div class="fecho"><i>→</i><b>' + esc(txt) + "</b></div>";
  }

  /* na página da clínica dez ferramentas convivem: cada bloco leva o cabeçalho
     reduzido da ferramenta de onde ele veio */
  function capCab(k) {
    var c = cab(k);
    if (!c) return "";
    return '<span class="sobre-cap">' + esc(c.sobrelinha) + "</span>" +
      "<h2>" + esc(c.titulo) + "</h2>" +
      (tem(c.pergunta) ? '<span class="cap-perg">' + esc(c.pergunta) + "</span>" : "");
  }

  function telaTopo(sobre, h1, sub) {
    return '<div class="tela-topo">' +
      (sobre ? '<div class="sobre">' + esc(sobre) + "</div>" : "") +
      "<h1>" + esc(h1) + "</h1>" +
      (sub ? '<p class="sub">' + esc(sub) + "</p>" : "") + "</div>";
  }

  function fato(v, k) {
    return '<div class="fato"><div class="v">' + v + '</div><div class="k">' + esc(k) + "</div></div>";
  }

  function pe(txt) { return '<div class="pe">' + esc(txt) + "</div>"; }

  function rodape() {
    return pe("fonte: dados públicos — ficha do Google, avaliação de paciente, busca local e IBGE · " +
      "gerado em " + data(manifest.gerado_em) + " · nenhum número desta tela vem do sistema interno da rede");
  }

  function selo(f) {
    return '<span class="selo" style="--sev:' + (COR[f] || "var(--cyan)") + '">' + esc(f) + "</span>";
  }

  function seloTarefa(t) {
    if (!t) return '<span class="selo" style="--sev:var(--t3)">sem tarefa</span>';
    var venc = t.status === "vencida";
    return '<span class="selo" style="--sev:' + (venc ? "var(--crit)" : "var(--ok)") + '">' +
      (venc ? "fora do prazo" : "no prazo") + "</span>" +
      '<span class="mono" style="font-size:11px;color:var(--t3)">' +
      (t.dias_aberta === 0 ? "aberta hoje" : "aberta há " + plural(t.dias_aberta, "dia", "dias")) +
      " · " + (venc ? "venceu" : "vence") + " em " + data(t.vence_em) + "</span>";
  }

  function delta(d) {
    if (!tem(d) || d === 0) return '<span class="par">· 0</span>';
    if (d > 0) return '<span class="par sobe">▲ ' + br(d) + "</span>";
    return '<span class="par desce">▼ ' + br(Math.abs(d)) + "</span>";
  }

  function movLinha(x, alerta) {
    return '<div class="mov"><span class="nm">' + esc(x.nome) + (x.proprio ? "<em>nossa</em>" : "") + "</span>" +
      '<span class="par">' + br(x.antes) + " → " + br(x.agora) + "</span>" + delta(x.delta) +
      '<span class="par">nota ' + dec(x.nota_antes) + " → " + dec(x.nota_agora) + "</span>" +
      ((x.eventos && x.eventos.length)
        ? '<span class="ev"' + (alerta ? ' style="color:var(--crit)"' : "") + ">" + x.eventos.map(esc).join(" · ") + "</span>"
        : "") + "</div>";
  }

  function avalHTML(i) {
    return '<div class="aval"><div><div class="est">' + "★".repeat(i.nota) + "</div>" +
      '<div class="dt">' + data(i.data) + "</div></div><div>" +
      (i.tem_texto && tem(i.texto)
        ? '<div class="tx">' + esc(i.texto) + "</div>"
        : '<div class="vaz">só estrela, sem texto — pode receber a resposta padrão</div>') +
      "</div></div>";
  }

  /* o payload marca ênfase com **assim** e, nas teses de praça, com <b>assim</b>.
     A ênfase é dele, não do casco — e só <b> passa: o resto continua escapado. */
  function forte(s) {
    return esc(s).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>")
      .replace(/\*([^*\n]+)\*/g, "<i>$1</i>")
      .replace(/&lt;b&gt;/g, "<b>").replace(/&lt;\/b&gt;/g, "</b>");
  }

  /* corta a lista para caber; o rótulo usa o total pronto, nunca uma subtração */
  function comMais(itens, quantos, total, molde) {    var html = itens.slice(0, quantos).map(molde).join("");
    if (tem(total) && total > quantos) {
      html += '<details class="abre"><summary>ver todas as ' + br(total) + "</summary>" +
        itens.slice(quantos).map(molde).join("") + "</details>";
    }
    return html;
  }

  /* ---------- o menu lateral ---------- */

  var SECOES = [
    { id: "inicio", rot: "Inteligência da rede" },
    { id: "clinicas", rot: "Clínicas" },
    { id: "pracas", rot: "Praças" },
    { id: "ensina", rot: "O que a rede ensina" },
    { id: "radar", rot: "Radar de cidades" },
    { id: "marca", rot: "Brand Watch" },
    { id: "arquivo", rot: "Arquivo" }
  ];

  var DONA = {
    "": "inicio", inicio: "inicio", fila: "inicio", agenda: "inicio",
    clinicas: "clinicas", timeline: "clinicas", caixa: "clinicas", mudou: "clinicas",
    constancia: "clinicas", rival: "clinicas", perto: "clinicas", anomalias: "clinicas",
    pracas: "pracas", planos: "arquivo", captacao: "pracas",
    ensina: "ensina", padroes: "ensina", rede_aprende: "ensina", playbook: "ensina",
    radar: "radar", funil: "radar", oportunidade: "radar", pipeline_expansao: "radar",
    radar_antigo: "radar",
    marca: "marca", rede_inteira: "marca", reputacao: "marca", mapa: "marca",
    arquivo: "arquivo", voz_da_cidade: "arquivo", busca: "arquivo", fichas: "arquivo",
    territorio: "arquivo", achados: "arquivo", evidencias: "arquivo", corretor: "arquivo"
  };

  /* o contador de cada seção sai de um campo pronto, nunca de um .length */
  function contaDaSecao(id, fila) {
    var r = franq.rede || {}, cob = franq.cobertura || {};
    if (id === "inicio") return fila ? fila.em_risco : null;
    if (id === "clinicas") return cob.unidades_acompanhadas;
    if (id === "pracas") return cob.pracas_da_rede_estudadas;
    if (id === "radar") return cob.cidades_de_oportunidade_estudadas;
    if (id === "marca") return cob.unidades_total;
    return null;
  }

  function pintarRail(rota, fila) {
    var raiz = rota.split("/")[0];
    var atual = DONA[raiz] || "inicio";
    var html = "";

    SECOES.forEach(function (s) {
      var n = contaDaSecao(s.id, fila);
      html += '<button type="button" class="rail-item" data-ir="' + s.id + '"' +
        (s.id === atual ? ' aria-current="page"' : "") + ">" + esc(s.rot) +
        (tem(n) ? '<span class="cont">' + br(n) + "</span>" : "") + "</button>";
    });

    html += '<div class="rail-rodape"><span class="rot-sis">ciclo de coleta</span>' +
      '<div class="l">corte ' + data(franq.corte) + "<br>próxima coleta: pendente</div></div>";

    el("rail").innerHTML = html;
  }

  /* ---------- INÍCIO · §10.1 INTELIGÊNCIA DA REDE ---------- */

  function telaInicio(r) {
    var fila = r[0], ir = r[1] || {}, ag = r[2] || {};
    var rd = franq.rede || {};

    /* §10.1 · a home deixou de ser painel de ferramentas e virou as cinco
       perguntas da semana. O que era lista de alertas foi para #/fila: aqui
       cabe o cruzamento, e nada se repete de dentro das ferramentas. */
    var html = cabecalhoTela("inteligencia_da_rede") + comoLer("inteligencia_da_rede");

    html += '<div class="tira">' +
      tiraCart(br(ir.itens_total), "coisas para saber esta semana", "cyan") +
      ((ir.resumo || {}).por_gravidade || []).map(function (g) {
        return tiraCart(br(g.quantos), tem(g.rotulo) ? g.rotulo : g.gravidade,
          g.gravidade === "alta" ? "crit" : (g.gravidade === "media" ? "warn" : null));
      }).join("") + "</div>";

    (ir.blocos || []).forEach(function (b) {
      html += '<div class="painel bloco-ir"><div class="painel-cab">' +
        '<h2><span class="b-n mono">' + br(b.quantos) + "</span>" + esc(b.titulo) + "</h2>" +
        '<span class="dir">' + esc(b.pergunta) + "</span></div>";

      if (!(b.itens || []).length) {
        html += vazio("nada nesta faixa nesta rodada", b.vazio_porque);
      } else if (b.chave === "unidades" && (ag.esta_semana || []).length) {
        /* §10.2 · este bloco É a agenda do consultor: a mesma fila na forma da
           conversa — o que vimos, o que conversar, o que levar. */
        html += '<p class="sub-painel">' + esc(ag.manchete) + "</p>" +
          ag.esta_semana.map(linhaAgenda).join("") +
          '<div class="filtros" style="margin-top:12px"><button type="button" class="chip" data-ir="fila">' +
          esc(ag.frase_ver_todas) + "</button></div>";
      } else {
        html += '<div class="insights">' + b.itens.map(cartaoInsight).join("") + "</div>";
      }
      if (tem(b.abre) && ROTAS[b.abre]) {
        html += '<div class="filtros"><button type="button" class="chip" data-ir="' + esc(b.abre) +
          '">abrir a ferramenta inteira</button></div>';
      }
      html += "</div>";
    });

    /* o mapa continua respondendo ONDE — mas agora depois das perguntas, não
       antes delas */
    var ab = franq.abertura || {};
    html += '<div class="heroi heroi-mapa"><div class="heroi-globo"></div><div class="heroi-dentro">' +
      '<div class="sobre">' + esc(ab.sobrelinha) + "</div>" +
      "<h2 class=\"heroi-h2\">" + esc(ab.titulo) + "</h2>" +
      '<p class="sub">' + esc(ab.sublinha) + "</p>" +
      '<div class="mapa-caixa mapa-grande" id="mapa"></div>' + legendaMapa() +
      '<div class="heroi-dica">clique num estado para ver só os sinais dele</div>' +
      '<p class="heroi-escopo">' + esc(ab.escopo) + "</p>" +
      "</div></div>";

    /* §11.5 · só o que muda decisão: alta e crítica. Praça sem segunda medição
       não é praça sem movimento — é praça sem base de comparação, e a tela diz. */
    var mp = franq.movimentos_prioritarios;
    if (mp) {
      html += '<div class="painel" style="margin-top:24px"><div class="painel-cab">' +
        "<h2>O que se moveu no mercado</h2>" +
        '<span class="dir">' + br(mp.total_no_periodo) + " no período · a tela mostra só alta e crítica</span></div>" +
        '<p class="sub-painel">' + esc(mp.o_que_e) + "</p>";
      html += (mp.eventos || []).length
        ? mp.eventos.map(eventoLinha).join("")
        : vazio("Nada de alta severidade nesta janela", mp.porque_algumas_nao_aparecem);
      if ((mp.pracas_sem_delta || []).length) {
        html += '<div class="sem-delta"><span class="rot-sis">' +
          esc(mp.titulo_sem_delta || "ainda não dá para comparar") + "</span>" +
          '<div class="nuvem">' + mp.pracas_sem_delta.map(function (p) {
            return "<span>" + esc(p) + "</span>";
          }).join("") + "</div>" +
          '<p class="pq">' + esc(mp.porque_algumas_nao_aparecem) + "</p></div>";
      }
      html += "</div>";
    }

    html += '<div class="painel"><div class="painel-cab"><h2>A régua da rede</h2>' +
      '<span class="dir">' + esc(rd.fonte) + "</span></div>" +
      '<div class="fatos">' +
      fato('<span class="num">' + br(rd.unidades) + "</span>", "unidades na lista") +
      fato('<span class="num">' + br(rd.abertas) + "</span>", "abertas") +
      fato('<span class="num">' + br(rd.em_implantacao) + "</span>", "em implantação") +
      fato('<span class="num">' + br(rd.cidades) + "</span>", "cidades") +
      fato('<span class="num">' + br(rd.ufs_sem_unidade_total) + "</span>", "estados sem unidade") +
      "</div></div>";

    html += fecho(ir.manchete) + pe(ir.o_que_nao_e) +
      rodapeMetodo("inteligencia_da_rede") + rodape();
    return html;
  }

  /* §10.1 · a fila inteira saiu da home e ganhou tela: 43 unidades com ação
     aberta não caberiam embaixo das cinco perguntas da semana. */
  function telaFila(fila) {
    var html = cabecalhoTela("fila") + comoLer("fila") +
      '<div class="tira">' + (franq.tiras_do_inicio || []).map(function (t) {
        return tiraCart(br(t.numero), t.rotulo, t.tom);
      }).join("") + "</div>" +
      '<div class="painel-cab" style="margin-top:6px"><h2>Os sinais abertos</h2>' +
      '<span class="dir" id="sinais-dir">ordenados por urgência · cada sinal traz o que fazer e a evidência</span></div>' +
      '<div class="sinais" id="sinais">' + (fila.fila || []).map(sinalCart).join("") + "</div>";

    html += '<div class="resolvidas"><details><summary>' +
      '<span class="rs-n mono">' + br(fila.resolvidas_total) + "</span>" +
      '<span class="rs-t">' + esc(fila.frase_resolvidas) + "</span></summary>";
    if ((fila.tarefas_resolvidas || []).length) {
      html += fila.tarefas_resolvidas.map(function (t) {
        return '<div class="mov"><span class="nm">' + esc(t.rotulo) +
          (tem(t.unidade) ? " · " + esc(t.unidade) : "") + "</span>" +
          (tem(t.leitura) ? '<span class="par sobe">' + esc(t.leitura) + "</span>" : "") +
          (tem(t.resolvida_em) ? '<span class="par">' + data(t.resolvida_em) + "</span>" : "") +
          (tem(t.titulo) ? '<span class="ev">' + esc(t.titulo) + "</span>" : "") + "</div>";
      }).join("");
    }
    (fila.porque_descartadas || []).forEach(function (p) {
      html += '<div class="mov"><span class="nm">' + esc(p.motivo) + "</span>" +
        '<span class="par">' + br(p.quantas) + "</span></div>";
    });
    html += '<p class="pq">' + esc(fila.o_que_conta_como_resolvido) + "</p></details></div>";

    html += ressalvas("o que esta fila não enxerga", fila.o_que_isso_nao_ve);
    return html + fecho(fila.manchete) + pe(fila.o_que_e_atencao) +
      rodapeMetodo("fila") + rodape();
  }

  /* o filtro por estado: esconde o que não é do estado clicado, sem recontar
     nada — o total continua sendo o do arquivo */
  var ufFiltro = null;

  function filtrarPorUF(uf, mapa) {
    ufFiltro = (ufFiltro === uf ? null : uf);
    var caixa = el("sinais"), dir = el("sinais-dir");
    if (!caixa) return;
    var visiveis = 0;
    caixa.querySelectorAll(".sinal").forEach(function (n) {
      var bate = !ufFiltro || n.getAttribute("data-uf") === ufFiltro;
      n.style.display = bate ? "" : "none";
      if (bate) visiveis++;
    });
    document.querySelectorAll(".uf").forEach(function (g) {
      g.setAttribute("data-sel", g.getAttribute("data-uf") === ufFiltro ? "true" : "false");
    });
    if (dir) {
      var d = (mapa || []).filter(function (x) { return x.uf === ufFiltro; })[0];
      dir.textContent = ufFiltro
        ? (visiveis ? ufFiltro + " · " + esc(d && d.motivo || "") : ufFiltro + " não tem sinal aberto") +
          " · clique de novo para ver todos"
        : "ordenados por urgência · cada sinal traz o que fazer e a evidência";
    }
  }

  function tiraCart(v, k, cor) {
    return '<div class="tira-cart"><div class="v" style="color:' + cor + '">' + v + "</div>" +
      '<div class="k">' + esc(k) + "</div></div>";
  }

  function sinalCart(c) {
    var g = (c.gatilhos || [])[0] || {};
    var a = c.acao || {};
    /* a UF sai do rótulo pronto ("PR · Londrina"), não é montada:
       é a primeira palavra antes do separador */
    var uf = String(c.rotulo || "").split(" · ")[0];
    return '<button type="button" class="sinal" data-uf="' + esc(uf) + '" style="--sev:' +
      (COR[c.faixa] || "var(--cyan)") + '" data-ir="clinicas/' + esc(c.local_id) + '">' +
      '<div class="sinal-cab">' + selo(c.faixa) +
      '<span class="cidade">' + esc(c.rotulo) + (tem(c.unidade_curta) ? " " + esc(c.unidade_curta) : "") + "</span>" +
      '<span class="ponto"></span>' +
      '<span class="dir">urgência ' + br(c.urgencia) + "</span></div>" +
      "<h3>" + esc(g.titulo || c.unidade) + "</h3>" +
      (tem(g.fato) ? '<div class="fato">' + esc(g.fato) + "</div>" : "") +
      '<div class="medida"><span class="v">' + dec(c.ritmo) + "</span>" +
      '<span class="trilha"><i style="width:' + Math.max(2, Math.min(100, c.urgencia)) + '%"></i></span>' +
      /* "Nª de N" não se compõe aqui: os dois números soltos mentem sobre o
         tamanho da praça, e a frase pronta da posição só existe na clínica */
      '<span class="k">novas por mês</span></div>' +
      (tem(a.o_que)
        ? '<div class="fazer"><div class="rot">o que fazer</div><p>' + esc(a.o_que) + "</p>" +
          '<div class="meta"><span>' + esc(a.prazo) + "</span><span>·</span><span>" + esc(a.dono) +
          "</span><span>·</span><span>" + esc(a.custo) + "</span></div></div>"
        : '<div class="fazer"><div class="rot">o que fazer</div><p style="color:var(--t3)">Nada foi indicado para esta unidade nesta rodada.</p></div>') +
      '<div class="sinal-pe"><span>' +
      (c.tarefa ? (c.tarefa.status === "vencida" ? "venceu" : "vence") + " em " + data(c.tarefa.vence_em) : "sem tarefa aberta") +
      '</span><span class="link">Ver a clínica</span></div>' +
      "</button>";
  }

  /* ---------- o mapa ---------- */

  /* O mapa é pintado por PROBLEMA, não por tamanho: o `tom` vem pronto de
     franqueadora.json → mapa[], e a legenda também. Densidade dizia onde a
     rede é grande; problema diz onde ela precisa de você. */
  /* A tinta da sigla acompanha o tom: o campo de cada estado tem luminância
     própria, e tinta fixa quebra em algum deles. Medido contra o campo real
     (a cor do tom composta com o alfa sobre o painel): o amarelo pede navy
     (5,06:1), os demais pedem branco (4,87 a 12,05). Tom novo entra aqui. */
  var TOM_TINTA = { warn: "#001433" };

  var TOM = {
    crit: "var(--crit)",
    warn: "var(--warn)",
    ok: "var(--ok)",
    sem_escuta: "var(--cyan)",
    sem_unidade: null
  };
  var TOM_ALFA = { crit: .62, warn: .58, ok: .52, sem_escuta: .16 };

  function legendaMapa() {
    /* a chave da legenda leva a mesma cor do estado, pela mesma tabela */
    return '<div class="mapa-legenda">' + (franq.mapa_legenda || []).map(function (l) {
      var cor = TOM[l.tom];
      return '<span><i class="chave chave-' + esc(l.tom) + '"' +
        (cor ? ' style="--c:' + cor + '"' : "") + "></i>" + esc(l.o_que_e) + "</span>";
    }).join("") + "<span>● praça estudada</span></div>";
  }

  function desenharMapa(alvo, mapa) {
    var geo = window.BRASIL_UFS;
    if (!geo || !geo.ufs) {
      alvo.innerHTML = vazio("O desenho do mapa não carregou",
        "O contorno dos estados é um arquivo da própria página, lido antes dela.");
      return;
    }
    if (!mapa || !mapa.length) {
      alvo.innerHTML = vazio("Esta medição não trouxe o mapa", "O arquivo veio sem a lista de estados.");
      return;
    }

    var formas = "", rotulos = "";

    /* A sigla ocupa mais ou menos isto no viewBox. Duas passadas: quem cabe
       dentro reserva o lugar; os pequenos escolhem uma saída livre, senão a
       sigla de um cai sobre o vizinho. */
    var LARG = 18, ALT = 14, ocupado = [];
    function bate(x, y) {
      var a = { x: x - LARG / 2, y: y - ALT / 2, w: LARG, h: ALT };
      return ocupado.some(function (b) {
        return a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h;
      });
    }
    function reservar(x, y) { ocupado.push({ x: x - LARG / 2, y: y - ALT / 2, w: LARG, h: ALT }); }

    var dentro = [], fora = [];
    mapa.forEach(function (x) {
      var g = geo.ufs[x.uf];
      if (!g) return;
      var it = { x: x, g: g };
      if (g.w >= 30 && g.h >= 16) dentro.push(it); else fora.push(it);
    });
    dentro.forEach(function (it) { it.lx = it.g.cx; it.ly = it.g.cy; reservar(it.lx, it.ly); });

    var SAIDAS = [[24, -12], [24, 12], [-24, -12], [-24, 12], [0, -22], [0, 22], [34, 0], [-34, 0]];
    fora.forEach(function (it) {
      var s = SAIDAS.filter(function (d) { return !bate(it.g.cx + d[0], it.g.cy + d[1]); })[0] || SAIDAS[0];
      it.lx = it.g.cx + s[0]; it.ly = it.g.cy + s[1]; it.chamada = true;
      reservar(it.lx, it.ly);
    });

    dentro.concat(fora).forEach(function (it) {
      var g = it.g, x = it.x, cor = TOM[x.tom], sem = !cor;
      formas += '<g class="uf" data-uf="' + esc(x.uf) + '" data-tom="' + esc(x.tom) +
        '" data-sel="false" tabindex="0" role="button" aria-label="' +
        esc(x.uf) + ", " + esc(x.motivo) + '">' +
        '<path class="forma' + (sem ? " sem" : "") + '" d="' + g.d + '"' +
        (sem ? "" : ' style="--c:' + cor + ";--a:" + (TOM_ALFA[x.tom] || .4) + '"') + "></path></g>";

      if (it.chamada) {
        var mx = g.cx + (it.lx - g.cx) * .62, my = g.cy + (it.ly - g.cy) * .62;
        rotulos += '<path class="uf-chamada" d="M' + g.cx + " " + g.cy + "L" + mx.toFixed(1) + " " + my.toFixed(1) + '"></path>';
      }
      var tinta = sem ? "" : TOM_TINTA[x.tom];
      rotulos += '<text class="uf-sig' + (sem ? " fraca" : "") + '"' +
        (tinta ? ' style="--ink:' + tinta + '"' : "") +
        ' x="' + it.lx.toFixed(1) +
        '" y="' + (it.ly + 4).toFixed(1) + '" text-anchor="middle">' + esc(x.uf) + "</text>";
      if (x.pracas_medidas) {
        rotulos += '<circle class="uf-ponto" cx="' + it.lx.toFixed(1) + '" cy="' + (it.ly - 12).toFixed(1) + '" r="3"></circle>';
      }
    });

    alvo.innerHTML = '<svg class="br" viewBox="0 0 ' + geo.w + " " + geo.h + '" role="img" ' +
      'aria-label="Mapa do Brasil pintado por problema: vermelho onde há unidade em faixa vermelha ou alerta grave">' +
      "<g>" + formas + '</g><g pointer-events="none">' + rotulos + "</g></svg>" +
      '<div class="mapa-dica" id="mapa-dica" style="display:none"></div>';

    alvo.querySelectorAll(".uf").forEach(function (g) {
      function entra() { dica(alvo, g, mapa); }
      g.addEventListener("mouseenter", entra);
      g.addEventListener("focus", entra);
      g.addEventListener("mouseleave", semDica);
      g.addEventListener("blur", semDica);
      if (el("sinais")) {
        g.addEventListener("click", function () { filtrarPorUF(g.getAttribute("data-uf"), mapa); });
        g.addEventListener("keydown", function (e) {
          if (e.key === "Enter" || e.key === " ") { e.preventDefault(); filtrarPorUF(g.getAttribute("data-uf"), mapa); }
        });
      }
    });
  }

  function dica(caixa, g, mapa) {
    var uf = g.getAttribute("data-uf");
    var d = mapa.filter(function (x) { return x.uf === uf; })[0];
    var cx = el("mapa-dica");
    if (!d || !cx) return;
    cx.innerHTML = '<div class="tt">' + esc(uf) + "</div>" +
      '<div class="motivo">' + esc(d.motivo) + "</div><dl>" +
      "<dt>unidades</dt><dd>" + br(d.unidades) + "</dd>" +
      "<dt>abertas</dt><dd>" + br(d.abertas) + "</dd>" +
      "<dt>em implantação</dt><dd>" + br(d.em_implantacao) + "</dd>" +
      "<dt>cidades</dt><dd>" + br(d.cidades) + "</dd>" +
      "<dt>praças estudadas</dt><dd>" + br(d.pracas_medidas) + "</dd></dl>";
    cx.style.display = "block";
    var b = g.getBoundingClientRect(), c = caixa.getBoundingClientRect();
    var x = b.left - c.left + b.width / 2 - cx.offsetWidth / 2;
    var y = b.top - c.top - cx.offsetHeight - 10;
    cx.style.left = Math.max(4, Math.min(x, c.width - cx.offsetWidth - 4)) + "px";
    cx.style.top = (y < 4 ? b.bottom - c.top + 10 : y) + "px";
  }

  function semDica() {
    var cx = el("mapa-dica");
    if (cx) cx.style.display = "none";
  }

  /* ---------- CLÍNICAS ---------- */

  /* A tela de Clínicas não é lista: é TRIAGEM. Dez unidades caberiam numa
     grade; 374 não — e uma grade de dez esconde que 364 não foram escutadas.
     Ordem: a manchete do que falta, as que pedem ação, busca e filtro, e o
     mapa de cobertura por UF em sanfona fechada. */
  var indiceClinicas = null;
  var arvoreHTML = "";
  /* a grade nasce com um teto e cresce quando pedida: 374 cards de uma vez
     pesam na máquina de quem abre e ninguém rola 374. O rótulo do botão usa o
     total pronto do payload, nunca uma subtração. */
  var CORTE_GRADE = 60;
  var gradeResto = "";

  function telaClinicas(r) {
    var idx = r[0], fila = r[1];
    var html = cabecalhoTela("clinicas_indice") + comoLer("clinicas_indice");

    html += '<div class="heroi"><div class="heroi-dentro">' +
      '<div class="sobre">o tamanho do que falta</div>' +
      "<h1>" + esc(idx.manchete) + "</h1>" +
      '<div class="fatos" style="margin-top:26px">' +
      fato('<span class="num">' + br(idx.com_estudo) + "</span>", "com estudo") +
      fato('<span class="num" style="color:var(--t3)">' + br(idx.sem_escuta) + "</span>", "ainda não escutadas") +
      fato('<span class="num">' + br(idx.cidades_total) + "</span>", "cidades") +
      fato('<span class="num">' + br(idx.cidades_com_mais_de_uma_loja) + "</span>", "cidades com mais de uma loja") +
      "</div>" +
      /* As duas datas são diferentes DE PROPÓSITO: a lista do site é lida todo
         dia, a varredura das fichas custa cota e vai mais devagar. Foi a
         divergência entre elas que fez o portal dizer 374 numa tela e 373 noutra. */
      '<p class="escopo-clinicas">' + esc((franq.cobertura || {}).aviso) + "</p>" +
      '<div class="duas-datas">' +
      '<span><i class="k">cadastro do site lido em</i> <b class="mono">' + data(idx.cadastro_lido_em) + "</b></span>" +
      '<span><i class="k">fichas do Google medidas em</i> <b class="mono">' + data(idx.fichas_medidas_em) + "</b></span>" +
      (tem(idx.porque_duas_datas) ? '<span class="pq-datas">' + esc(idx.porque_duas_datas) + "</span>" : "") +
      "</div></div></div>";

    /* §V7 · uma lista com uma linha por unidade não sobrevive a 373. A tela vira
       GRADE, e a ordem já vem pronta do payload: ordem de ALERTA, a loja que
       pega fogo primeiro — não a que começa com A. Não reordene. */
    html += '<p class="frase-grade">' + esc(idx.frase_da_grade) + "</p>";

    html += '<div class="visao" id="cl-visao">' +
      '<button type="button" class="chip" data-visao="grade" aria-pressed="true">A grade</button>' +
      '<button type="button" class="chip" data-visao="arvore" aria-pressed="false">Por estado</button>' +
      "</div>";

    /* toda contagem de filtro sai de campo pronto: grupos[].quantas e
       por_faixa[].quantas. Nenhum .length. */
    var chips = '<button type="button" class="chip" data-f="todas" aria-pressed="true">todas' +
      '<span class="n">' + br(idx.cards_total) + "</span></button>";
    (idx.por_faixa || []).forEach(function (f) {
      chips += '<button type="button" class="chip" data-f="faixa:' + esc(f.faixa) + '">' +
        '<i style="background:' + (COR[f.faixa] || "var(--t3)") + '"></i>' + esc(f.faixa) +
        '<span class="n">' + br(f.quantas) + "</span></button>";
    });
    (idx.grupos || []).forEach(function (g) {
      chips += '<button type="button" class="chip" data-f="estado:' + esc(g.chave) +
        '" title="' + esc(g.o_que_e) + '">' + esc(g.titulo) +
        '<span class="n">' + br(g.quantas) + "</span></button>";
    });

    html += '<div class="painel" id="cl-grade-caixa"><div class="painel-cab"><h2>As unidades da rede</h2>' +
      '<span class="dir" id="cl-conta"></span></div>' +
      '<input type="text" class="filtro-campo" id="cl-busca" placeholder="unidade, cidade ou estado…" autocomplete="off">' +
      '<div class="filtros" id="cl-filtros">' + chips + "</div>" +
      '<div class="filtros" style="margin-top:10px"><select class="filtro-uf" id="cl-uf">' +
      '<option value="">todos os estados</option>' +
      (idx.ufs || []).map(function (u) {
        return '<option value="' + esc(u.uf) + '">' + esc(u.uf) + " — " + esc(u.frase) + "</option>";
      }).join("") + "</select></div>" +
      '<div class="grade-cards" id="cl-grade">' +
      (idx.cards || []).slice(0, CORTE_GRADE).map(cardDaGrade).join("") + "</div>" +
      (idx.cards_total > CORTE_GRADE
        ? '<button type="button" class="chip" id="cl-mais" style="margin-top:14px">ver todas as ' +
          br(idx.cards_total) + "</button>"
        : "") +
      '<details class="abre"><summary>como isto está ordenado</summary><p class="pq">' +
      esc(idx.ordem) + "</p></details>" +
      (tem(idx.porque_um_card_a_mais) ? pe(idx.porque_um_card_a_mais) : "") + "</div>";

    /* a árvore continua, como segunda visão: ela responde onde a rede ESTÁ no
       mapa, e a grade responde onde ela DÓI. Ela só é montada quando pedida —
       373 unidades em duas árvores ao mesmo tempo pesam sem servir a ninguém. */
    arvoreHTML = '<div class="painel-cab"><h2>A rede estado por estado</h2>' +
      '<span class="dir">abra um estado para ver as cidades e as unidades</span></div>' +
      '<div class="ufs">' + (idx.ufs || []).map(function (u) {
        var apagado = u.com_estudo === 0;
        return '<details class="uf-linha' + (apagado ? " apagada" : "") + '"><summary>' +
          '<span class="sig">' + esc(u.uf) + "</span>" +
          '<span class="fr">' + esc(u.frase) + "</span>" +
          (u.com_estudo ? '<span class="selo" style="--sev:var(--cyan)">' +
            plural(u.com_estudo, "com estudo", "com estudo") + "</span>" : "") +
          "</summary><div class=\"uf-corpo\">" +
          (u.cidades || []).map(cidadeLinha).join("") + "</div></details>";
      }).join("") + "</div>";

    html += '<div class="painel" id="cl-arvore" hidden></div>';

    gradeResto = (idx.cards || []).slice(CORTE_GRADE).map(cardDaGrade).join("");

    return html + fecho(idx.frase_da_grade) +
      pe(esc(idx.corte ? "medido em " + data(idx.corte) : "")) +
      rodapeMetodo("clinicas_indice") + rodape();
  }

  /* a ficha desta unidade foi lida? sem data de medição não há nota nem
     avaliações — o zero seria uma medição que não aconteceu */
  /* Quatro estados, não dois. O terceiro é o único de fato vazio. */
  function estadoDaUnidade(u) {
    if (u.situacao === "em implantação") return "implantando";
    if (u.com_estudo) return "estudada";
    if (tem(u.nota)) return "ficha";      /* nota do Google, sem escuta */
    return "lista";                        /* só na lista oficial */
  }

  function notaDaFicha(u) {
    if (!tem(u.nota)) return "";
    return '<span class="nota">' + dec(u.nota) + " · " +
      plural(u.avaliacoes, "avaliação", "avaliações") + "</span>";
  }

  var DIZ = {
    ficha: "ainda não escutada",
    lista: "só na lista oficial",
    implantando: "ainda não abriu"
  };

  function cidadeLinha(c) {
    var h = '<div class="cid-linha">' +
      '<div class="cid-cab"><span class="nm">' + esc(c.rotulo) + "</span>" +
      '<span class="fr">' + esc(c.frase) + "</span>" +
      (c.mais_de_uma_loja ? '<span class="selo">mais de uma loja</span>' : "") + "</div>";

    /* cidade com mais de uma loja nunca vira uma linha só: quem abre é a UNIDADE */
    h += (c.unidades || []).map(unidadeLinha).join("");

    /* onde a lista oficial não confirmou a linha, a frase é o conteúdo:
       não se inventa a qual unidade cada estudo corresponde */
    if ((c.estudos_sem_linha_oficial || []).length) {
      h += '<div class="sem-linha"><span class="k">estudos desta cidade sem linha confirmada</span>' +
        '<p class="pq">' + esc(c.porque_sem_linha) + "</p>" +
        c.estudos_sem_linha_oficial.map(function (e) {
          return '<button type="button" class="chip" data-ir="' + esc(e.arquivo) + '">' +
            esc(e.unidade) + "</button>";
        }).join("") + "</div>";
    }
    return h + "</div>";
  }

  function unidadeLinha(u) {
    var e = estadoDaUnidade(u);
    if (e === "estudada" && tem(u.arquivo)) {
      return '<button type="button" class="un-linha" data-ir="' + esc(u.arquivo) + '">' +
        '<span class="nm">' + esc(u.unidade) + "</span>" +
        notaDaFicha(u) + selo(u.faixa) +
        '<span class="ir">abrir →</span></button>';
    }
    /* apagado, não quebrado: mesma tipografia e espaçamento, sem cursor de
       link e sem hover — clique que não vai a lugar nenhum queima a confiança
       no resto da navegação */
    return '<div class="un-linha sem est-' + e + '">' +
      '<span class="nm">' + esc(u.unidade) + "</span>" +
      notaDaFicha(u) +
      (e === "implantando" ? '<span class="selo-impl">em implantação</span>' : "") +
      '<span class="ir">' + esc(DIZ[e]) + "</span></div>";
  }

  /* §V7 · o card da grade. Quatro estados: só o com estudo é clicável; os
     outros aparecem apagados, porque são o tamanho do que falta medir. */
  var GRUPO_DIZ = {
    ficha_medida: "ainda não escutada",
    so_na_lista: "só na lista oficial",
    em_implantacao: "ainda não abriu"
  };

  function cardDaGrade(c) {
    var attrs = ' data-faixa="' + esc(c.faixa || "") + '" data-estado="' + esc(c.estado) +
      '" data-uf="' + esc(c.uf) + '" data-k="' +
      esc(chave([c.rotulo, c.unidade, c.uf, c.cidade].join(" "))) + '"';

    var topo = '<div class="cc-topo">' +
      (tem(c.faixa)
        ? '<span class="cc-faixa" style="--sev:' + (COR[c.faixa] || "var(--cyan)") + '"><i></i>' +
          esc(c.faixa) + "</span>"
        : "") +
      (c.estado === "em_implantacao" ? '<span class="selo-impl">em implantação</span>' : "") +
      (tem(c.ordem) ? '<span class="cc-ord mono">#' + br(c.ordem) + "</span>" : "") +
      "</div>";

    /* o nome próprio da loja é o que distingue: as 373 se chamam OrthoDontic */
    var nome = '<div class="cc-pr mono">' + esc(c.rotulo) + "</div>" +
      '<div class="cc-un">' + esc(c.unidade) + "</div>";
    /* §13.2 · a procedência do número é nota de rodapé do card: as três lojas
       de Cuiabá mostravam a mesma ficha do Google. E quando não há número, o
       motivo escrito ocupa o lugar dele — 49 cards estão nessa situação. */
    var ficha = tem(c.nota)
      ? '<div class="cc-nm mono">' + dec(c.nota) + " · " +
        plural(c.avaliacoes, "avaliação", "avaliações") + "</div>" +
        (tem(c.numero_de) ? '<div class="cc-de mono">' + esc(c.numero_de) + "</div>" : "")
      : (tem(c.sem_numero_porque) ? '<div class="cc-sn">' + esc(c.sem_numero_porque) + "</div>" : "");

    if (c.estado === "com_estudo" && tem(c.arquivo)) {
      return '<button type="button" class="cl-card"' + attrs + ' data-ir="' + esc(c.arquivo) + '">' +
        topo + nome +
        (tem(c.alerta) ? '<div class="cc-al">' + esc(c.alerta) + "</div>" : "") +
        (tem(c.alerta_fato) ? '<div class="cc-ft">' + esc(c.alerta_fato) + "</div>" : "") +
        ficha +
        (c.sem_linha_oficial ? '<div class="cc-sl">' + esc(c.porque_sem_linha) + "</div>" : "") +
        (tem(c.acao) ? '<div class="cc-ac">' + esc(c.acao) + "</div>" : "") +
        "</button>";
    }
    return '<div class="cl-card apagada"' + attrs + ">" + topo + nome +
      (tem(c.endereco) ? '<div class="cc-end">' + esc(c.endereco) + "</div>" : "") +
      ficha +
      (tem(GRUPO_DIZ[c.estado]) ? '<div class="cc-diz">' + esc(GRUPO_DIZ[c.estado]) + "</div>" : "") +
      "</div>";
  }

  function garantirResto() {
    var grade = el("cl-grade");
    if (!grade || !gradeResto) return;
    grade.insertAdjacentHTML("beforeend", gradeResto);
    gradeResto = "";
    var b = el("cl-mais");
    if (b) b.parentNode.removeChild(b);
  }

  /* o filtro esconde o que não casa — nada é recontado. A única contagem da
     tela é a da busca, porque depende do que a pessoa digitou. */
  function filtrarGrade() {
    var grade = el("cl-grade");
    if (!grade) return;
    var campo = el("cl-busca"), sel = el("cl-uf");
    var q = chave(campo ? campo.value : "");
    var uf = sel ? sel.value : "";
    var ativo = document.querySelector('#cl-filtros .chip[aria-pressed="true"]');
    var f = ativo ? ativo.getAttribute("data-f") : "todas";
    /* filtro ou busca precisam ver a rede inteira, não só o topo da ordem */
    if (q || uf || (f && f !== "todas")) garantirResto();
    var casam = 0, mostrados = 0;

    Array.prototype.forEach.call(grade.children, function (n) {
      var ok = true;
      if (f && f !== "todas") {
        var p = f.split(":");
        ok = n.getAttribute("data-" + p[0]) === p[1];
      }
      if (ok && uf) ok = n.getAttribute("data-uf") === uf;
      if (ok && q) ok = n.getAttribute("data-k").indexOf(q) >= 0;
      if (ok) casam++;
      var cabe = ok && (!q || casam <= 30);
      if (cabe) mostrados++;
      n.style.display = cabe ? "" : "none";
    });

    var conta = el("cl-conta");
    if (conta) {
      conta.textContent = q
        ? (casam > mostrados
            ? "mostrando as 30 primeiras de " + br(casam) + " que casam"
            : br(casam) + " que casam")
        : "";
    }
  }

  function ligarGrade() {
    var campo = el("cl-busca");
    if (campo) campo.addEventListener("input", filtrarGrade);
    var sel = el("cl-uf");
    if (sel) sel.addEventListener("change", filtrarGrade);
    var mais = el("cl-mais");
    if (mais) mais.addEventListener("click", function () { garantirResto(); filtrarGrade(); });

    document.querySelectorAll("#cl-filtros .chip").forEach(function (b) {
      b.addEventListener("click", function () {
        var jaLigado = b.getAttribute("aria-pressed") === "true";
        document.querySelectorAll("#cl-filtros .chip").forEach(function (o) {
          o.setAttribute("aria-pressed", "false");
        });
        b.setAttribute("aria-pressed", jaLigado ? "false" : "true");
        if (!document.querySelector('#cl-filtros .chip[aria-pressed="true"]')) {
          document.querySelector('#cl-filtros .chip[data-f="todas"]').setAttribute("aria-pressed", "true");
        }
        filtrarGrade();
      });
    });

    document.querySelectorAll("#cl-visao .chip").forEach(function (b) {
      b.addEventListener("click", function () {
        var v = b.getAttribute("data-visao");
        document.querySelectorAll("#cl-visao .chip").forEach(function (o) {
          o.setAttribute("aria-pressed", o === b ? "true" : "false");
        });
        var g = el("cl-grade-caixa"), a = el("cl-arvore");
        if (a && v === "arvore" && !a.innerHTML) a.innerHTML = arvoreHTML;
        if (g) g.hidden = v !== "grade";
        if (a) a.hidden = v !== "arvore";
      });
    });
  }

  var QUEM = { nossa: "a clínica", paciente: "um paciente", fila: "o acompanhamento", rival: "um concorrente" };

  function telaClinica(d) {
    var cb = d.cabecalho || {};
    var html = '<button type="button" class="voltar" data-ir="clinicas">← todas as clínicas</button>';

    /* A página se APRESENTA antes de se medir: quem chega precisa saber de que
       loja se trata. A nota desce para a tira de números logo abaixo. */
    var ap = d.apresentacao || {};
    html += '<div class="clinica-corpo">';
    html += '<div class="apresenta"><div class="apresenta-txt">' +
      '<div class="sobre">' + esc(ap.cidade || d.rotulo) + "</div>" +
      "<h1>" + esc(ap.unidade || d.unidade) + "</h1>" +
      '<div class="endereco">' +
      (tem(ap.endereco) ? esc(ap.endereco) : "endereço não confirmado na lista oficial") + "</div>" +
      (tem(ap.frase) ? '<p class="apresenta-frase">' + esc(ap.frase) + "</p>" : "") +
      "</div>" +
      '<div class="selos">' + selo(d.faixa) + seloTarefa(d.tarefa) + "</div></div>";

    if ((ap.lojas_irmas || []).length) {
      html += '<div class="irmas"><span class="k">as outras lojas desta cidade</span>' +
        ap.lojas_irmas.map(function (x) {
          return '<button type="button" class="chip" data-ir="clinicas/' + esc(x.local_id) + '">' +
            esc(x.unidade) + "</button>";
        }).join("") + "</div>";
    }

    /* §13 · o ritmo nem sempre é comparável. A amostra sai das avaliações mais
       NOVAS: numa loja grande ela cobre poucas semanas, e o ritmo sem a janela
       ao lado é um número impossível. Amostra truncada chega com posição nula
       de propósito — a loja saiu da classificação, e o motivo vem escrito. */
    html += '<div class="painel"><div class="fatos">' +
      fato('<span class="num">' + dec(cb.nota) + "</span>", "nota") +
      fato('<span class="num">' + br(cb.avaliacoes) + "</span>", "avaliações") +
      fato('<span class="num">' + dec(cb.ritmo) + "</span>",
        tem(cb.amostra_dias)
          ? "por mês nos últimos " + plural(cb.amostra_dias, "dia", "dias")
          : "novas por mês") +
      fato('<span class="num">' + br(cb.meses_seguidos) + "</span>",
        cb.meses_seguidos === 1 ? "mês seguido" : "meses seguidos") +
      (tem(cb.posicao)
        ? fato('<span class="num">' + br(cb.posicao) + "º</span>", "em ritmo na praça")
        : fato('<span class="num" style="color:var(--t3)">fora</span>', "da classificação de ritmo")) +
      "</div>";
    if (tem(cb.frase_da_posicao)) html += '<p class="ritmo-nota">' + esc(cb.frase_da_posicao) + "</p>";
    if (cb.amostra_truncada && tem(cb.porque_fora_do_ranking)) {
      html += '<p class="ritmo-aviso">' + esc(cb.porque_fora_do_ranking) + "</p>";
    }
    if (tem(cb.amostra_lida) && tem(cb.amostra_dias)) {
      html += pe("a amostra: " + plural(cb.amostra_lida, "avaliação lida", "avaliações lidas") +
        " em " + plural(cb.amostra_dias, "dia", "dias") + " — o coletor puxa as mais novas");
    }
    html += "</div>";

    /* 1.5 · onde esta loja aparece na busca — POR LOJA, nunca a média da cidade */
    var pb = d.presenca_na_busca;
    if (pb) {
      html += '<div class="painel' + (pb.invisivel ? " grave" : "") + '"><div class="painel-cab">' +
        capCab("presenca_por_loja") +
        '<span class="dir">leitura desta unidade, não da cidade</span></div>' +
        '<p class="frase-topo' + (pb.invisivel ? " alerta" : "") + '">' + forte(pb.frase_do_topo) + "</p>" +
        '<div class="fatos">' +
        fato('<span class="num"' + (pb.invisivel ? ' style="color:var(--crit)"' : "") + ">" +
          br(pb.aparece_em) + "</span>", "de " + br(pb.de) + " buscas testadas") +
        fato('<span class="num">' + dec(pb.pct) + "%</span>", "das buscas da cidade") +
        fato('<span class="num">' + (tem(pb.melhor_posicao) ? br(pb.melhor_posicao) + "º" : "—") +
          "</span>", "melhor posição") +
        "</div>";

      if (pb.frases_onde_aparece && pb.frases_onde_aparece.length) {
        html += '<div class="nuvem" style="margin-top:16px">' + pb.frases_onde_aparece.map(function (f) {
          return "<span>" + esc(typeof f === "string" ? f : f.frase) +
            (typeof f === "object" && tem(f.posicao) ? " · " + br(f.posicao) + "º" : "") + "</span>";
        }).join("") + "</div>";
      }
      if (tem(d.plano)) {
        html += '<div class="filtros" style="margin-top:16px">' +
          '<button type="button" class="chip forte" data-ir="' + esc(d.plano) + '">O meu plano</button></div>';
      }
      html += carimbo(pb.confianca) + "</div>";
    }

    /* §12 · a MESMA pergunta em duas escalas, e as duas na tela. A leitura da
       cidade responde em cidade pequena e mente em metrópole: as quatro de São
       Paulo apareciam em 0 de 193 e não precisavam da mesma coisa. */
    html += capPerto(d.perto_da_clinica);

    /* §10.4 · o gêmeo: a unidade da rede com o mercado mais parecido. A escolha
       é por MERCADO, nunca por resultado — escolher pela nota tornaria a conta
       circular. O que aparece depois são diferenças observáveis, não causa. */
    html += capGemeo(d.local_id);

    /* 2 · o que fazer agora — uma recomendação nunca se apresenta como medição */
    html += '<div class="painel acao-agora"><div class="painel-cab"><span class="sobre-cap">a ação desta semana</span><h2>O que fazer agora</h2>' +
      '<span class="dir">urgência ' + br(d.urgencia) + "</span></div>";
    if (d.quem_avanca) {
      html += '<div class="medida" style="--sev:var(--crit);margin-bottom:16px">' +
        '<span class="v">' + dec(d.quem_avanca.ritmo) + "</span>" +
        '<span class="trilha"><i style="width:100%"></i><u style="left:' +
        Math.max(0, Math.min(98, (cb.ritmo / (d.quem_avanca.ritmo || 1)) * 100)) + '%"></u></span>' +
        '<span class="k">' + esc(d.quem_avanca.nome) + " · nós " + dec(cb.ritmo) + "</span></div>";
    }
    html += (d.gatilhos || []).map(function (g) {
      return '<div class="gatilho"><div class="t">' + esc(g.titulo) + "<span>peso " + br(g.peso) + "</span></div>" +
        '<div class="f">' + esc(g.fato) + "</div>" +
        (tem(g.fonte) ? '<div class="src">' + esc(g.fonte) + "</div>" : "") + "</div>";
    }).join("");
    var a = d.acao || {};
    html += tem(a.o_que)
      ? '<div class="fazer" style="margin-top:16px"><div class="rot">o que fazer</div><p>' + esc(a.o_que) + "</p>" +
        '<div class="meta"><span>prazo: ' + esc(a.prazo) + "</span><span>quem faz: " + esc(a.dono) +
        "</span><span>" + esc(a.custo) + "</span></div></div>" + carimbo(a.confianca)
      : '<div class="fazer" style="margin-top:16px"><div class="rot">o que fazer</div>' +
        '<p style="color:var(--t3)">Nada foi indicado para esta unidade nesta rodada.</p></div>';
    html += "</div>";

    /* §11.3 · de quem é o conserto. Campanha e balcão se desenham diferente:
       mais mídia sobre um gargalo de recepção só aumenta a fila de irritados. */
    html += capExecucao(d.execucao);

    /* 3 · o que mudou entre as coletas */
    html += '<div class="painel"><div class="painel-cab">' + capCab("o_que_mudou") + "</div>";
    if (!d.o_que_mudou) {
      html += vazio("Ainda só uma medição",
        "A comparação nasce na próxima coleta: são precisas duas leituras do contador público para haver antes e depois.");
    } else {
      var m = d.o_que_mudou, h = m.historico;

      /* Duas janelas, e as duas importam. A curta é o que mudou entre as duas
         últimas medições; a do período é desde a primeira. Sem a segunda, as
         praças com MAIS histórico da rede apareciam como "só 3 dias". */
      html += '<div class="janelas">' +
        '<div class="janela"><div class="rot">entre as duas últimas medições</div>' +
        movLinha(m) +
        '<div class="quando">de ' + data(m.de) + " a " + data(m.ate) + " · " +
        plural(m.dias, "dia medido", "dias medidos") + "</div></div>";

      if (h) {
        html += '<div class="janela"><div class="rot">desde a primeira medição</div>' +
          '<div class="mov"><span class="nm">o período inteiro</span>' +
          delta(h.delta) +
          '<span class="par">' + dec(h.ritmo_do_periodo) + " por mês</span></div>" +
          '<div class="quando">medida desde ' + data(h.desde) + " · " +
          plural(h.dias, "dia", "dias") + " · " + plural(h.medicoes, "medição", "medições") + "</div></div>";
      }
      html += "</div>";

      /* o aviso é do histórico, não da janela curta: se o período é longo,
         dizer "só 3 dias" engana justamente quem tem mais leitura */
      if (tem(m.aviso) && !h) html += '<p class="aviso-curto">' + esc(m.aviso) + "</p>";
      if (h && tem(h.aviso)) html += '<p class="aviso-curto">' + esc(h.aviso) + "</p>";
    }
    html += "</div>";

    /* 4 · a voz do paciente */
    html += '<div class="painel"><div class="painel-cab"><span class="sobre-cap">o que dizem</span><h2>A voz do paciente</h2>' +
      '<span class="dir">quanto das avaliações fala de cada coisa</span></div>';
    if (!d.voz_do_paciente || !d.voz_do_paciente.length) {
      html += vazio("Base fina demais para ler a voz",
        "Esta unidade ainda não tem avaliações com texto suficientes para separar assunto por assunto.");
    } else {
      var maxV = d.voz_do_paciente.reduce(function (x, v) { return Math.max(x, v.pct || 0); }, 0) || 1;
      html += d.voz_do_paciente.map(function (v) {
        return '<div class="barra-tema"><span class="l">' + esc(v.o_que_e) + "</span>" +
          '<span class="trilha"><i style="width:' + (v.pct / maxV * 100) + '%"></i></span>' +
          '<span class="v">' + dec(v.pct) + "%</span></div>";
      }).join("");
    }
    html += "</div>";

    /* 5 · avaliações esperando resposta */
    var sr = d.sem_resposta || {};
    html += '<div class="painel"><div class="painel-cab">' + capCab("caixa_de_respostas") +
      '<span class="dir">' + br(sr.abertas) + " sem resposta · " + br(sr.com_texto) + " com o motivo escrito</span></div>";
    html += (sr.itens && sr.itens.length)
      ? comMais(sr.itens, 8, sr.itens_total, avalHTML)
      : vazio("Nada esperando", "Não há avaliação negativa sem resposta nesta unidade.");
    html += "</div>";

    /* 6 · quem anuncia aparelho na cidade — leitura de CIDADE dentro da
       página da loja: as três de Cuiabá disputam o mesmo leilão */
    var an = d.anuncios_da_cidade;
    if (an) {
      html += '<div class="painel"><div class="painel-cab">' + capCab("anuncios") +
        '<span class="dir">' + br(an.anuncios_ativos) + " anúncios no ar</span></div>" +
        '<div class="de-cidade">leitura da cidade — vale para todas as lojas da rede em ' +
        esc(an.rotulo) + "</div>" +
        '<p class="frase-topo">' + esc(an.manchete) + "</p>";

      html += (an.anunciantes && an.anunciantes.length)
        ? '<div class="anunciantes">' + an.anunciantes.map(function (x) {
            return '<div class="anunciante' + (x.nosso ? " nosso" : "") + '">' +
              '<div class="an-cab"><span class="n">' + esc(x.nome) +
              (x.nosso ? '<em class="mono">a nossa</em>' : "") + "</span>" +
              '<span class="an-num mono">' + plural(x.anuncios, "anúncio", "anúncios") + "</span></div>" +
              '<div class="an-meta mono">' + (x.plataformas || []).map(esc).join(" · ") +
              (tem(x.desde) ? " · no ar desde " + data(x.desde) : "") +
              (tem(x.dias_no_ar_maior) ? " · " + plural(x.dias_no_ar_maior, "dia", "dias") + " no ar" : "") + "</div>" +
              (tem(x.exemplo) ? '<p class="an-ex">' + esc(x.exemplo) + "</p>" : "") +
              (tem(x.de_outra_unidade)
                ? '<div class="an-fora">não é desta praça — ' + esc(x.de_outra_unidade) + "</div>" : "") +
              "</div>";
          }).join("") + "</div>"
        : vazio("Ninguém anuncia aparelho nesta cidade",
            "A varredura da biblioteca de anúncios não encontrou nenhum anúncio de aparelho no ar aqui — " +
            "nem da rede, nem de concorrente.");

      if (tem(an.fora_do_produto) && an.fora_do_produto > 0) {
        html += '<div class="proc">' + plural(an.fora_do_produto, "anúncio ficou", "anúncios ficaram") +
          " fora desta lista: " + esc(an.fora_do_produto_porque) + "</div>";
      }
      html += "</div>";
    }

    /* 6.5 · o anúncio que casou por palavra e é de outra unidade da rede */
    if (d.anuncio_de_outra_unidade && d.anuncio_de_outra_unidade.length) {
      html += '<div class="painel"><div class="painel-cab"><h2>Anúncio que não é desta praça</h2></div>' +
        '<div class="proc">a busca da biblioteca casa por palavra, então unidade de outra cidade com nome parecido ' +
        "entra na varredura — estes saíram da contagem de quem anuncia aqui</div>" +
        d.anuncio_de_outra_unidade.map(function (x) {
          return '<div class="fora-item"><div class="n">' + esc(x.nome) + "</div>" +
            '<div class="p">' + esc(x.por_que_fora || x.motivo) + "</div></div>";
        }).join("") + "</div>";
    }

    /* 6.7 · onde dói, no caminho do paciente */
    html += capJornada(d.jornada);

    /* 6.8 · a disputa comercial — é da CIDADE, e a tela diz isso */
    html += capOferta(d.oferta_da_cidade, "clinica");

    /* 6.9 · o livro de ações: o que aconteceu depois de cada recomendação */
    html += capAcoes(d.acoes);

    /* §11.1 · o território: fato, inferência e hipótese com pesos visuais
       diferentes — e distância em linha reta nunca vira tempo de deslocamento */
    html += capTerritorio(d.meu_territorio);

    /* §11.2 · o que mudou ao redor: leitura de CIDADE dentro da página da loja */
    html += capMovimentos(d.movimentos, d.rotulo);

    /* 7 · o rival de aparelho */
    var rv = d.rival || {};
    html += '<div class="painel"><div class="painel-cab">' + capCab("rival") +
      '<span class="dir">só quem vende aparelho entra na comparação</span></div>';
    if (tem(rv.sem_comparacao_porque)) {
      html += vazio("Sem comparação nesta unidade", rv.sem_comparacao_porque);
    } else if (rv.vantagens_deles && rv.vantagens_deles.length) {
      var maxR = rv.vantagens_deles.reduce(function (x, v) { return Math.max(x, v.eles || 0); }, 0) || 1;
      html += rv.vantagens_deles.map(function (v) {
        return '<div class="barra-tema"><span class="l">' + esc(v.o_que_e) + "</span>" +
          '<span class="trilha"><i style="width:' + (v.eles / maxR * 100) + '%"></i></span>' +
          '<span class="v">' + dec(v.eles) + "%</span></div>" +
          '<div class="mono" style="font-size:11px;color:var(--t3);margin:-2px 0 12px">' +
          esc(v.quem) + " · nós " + dec(v.nos) + "% · " + dec(v.razao) + "× mais</div>";
      }).join("");
      if (rv.comparados && rv.comparados.length) {
        html += '<div class="nuvem" style="margin-top:10px">' +
          rv.comparados.map(function (r) { return "<span>" + esc(r) + "</span>"; }).join("") + "</div>";
      }
    }
    if (rv.fora && rv.fora.length) {
      html += '<details class="abre"><summary>fora da comparação — outro produto (' + br(rv.fora_total) + ")</summary>" +
        rv.fora.map(function (f) {
          return '<div class="fora-item"><div class="n">' + esc(f.nome) + "</div>" +
            '<div class="p">' + esc(f.por_que_fora) + "</div></div>";
        }).join("") + "</details>";
    }
    html += "</div>";

    /* 8 · a linha do tempo */
    html += '<div class="painel"><div class="painel-cab">' + capCab("timeline") + "</div>";
    html += (d.eventos && d.eventos.length)
      ? '<ul class="tempo">' + d.eventos.map(function (e) {
          var sr2 = String(e.texto || "").indexOf("SEM RESPOSTA") >= 0;
          var tx = sr2 ? esc(e.texto).replace("SEM RESPOSTA", "<b>SEM RESPOSTA</b>") : esc(e.texto);
          return '<li data-quem="' + esc(e.quem) + '"><div class="qd"><span>' + esc(QUEM[e.quem] || e.quem) +
            "</span><span>" + data(e.data) + "</span></div><div class=\"tx\">" + tx + "</div></li>";
        }).join("") + "</ul>"
      : vazio("Nada aconteceu nesta janela", "Nenhum evento observável foi registrado no período medido.");
    html += "</div>";

    html += '<div class="painel"><div class="painel-cab"><h2>Ao redor desta clínica</h2></div>' +
      '<div class="filtros">' +
      '<button type="button" class="chip" data-ir="pracas/' + esc(d.praca_id) + '">O mercado de ' + esc(d.rotulo) + "</button>" +
      (tem(d.plano) ? '<button type="button" class="chip" data-ir="' + esc(d.plano) + '">O plano desta loja</button>' : "") +
      '<button type="button" class="chip" data-ir="captacao/' + esc(d.praca_id) + '">Como a cidade procura</button>' +
      "</div></div>";

    return html + "</div>" + rodape();
  }


  var NATUREZA = {
    fato: { rot: "fato medido", cor: "var(--cyan)" },
    inferencia: { rot: "inferência", cor: "var(--warn)" },
    recomendacao: { rot: "recomendação", cor: "var(--bad)" }
  };

  function carimbo(c) {
    if (!c) return "";
    var n = NATUREZA[c.natureza] || { rot: c.natureza, cor: "var(--t3)" };
    var h = '<div class="carimbo carimbo-' + esc(c.natureza) + '" style="--nat:' + n.cor + '">' +
      '<div class="carimbo-cab"><span class="nat">' + esc(n.rot) + "</span>" +
      '<span class="grau">confiança ' + esc(c.confianca) + "</span></div>" +
      (tem(c.procedencia) ? '<div class="proc">' + esc(c.procedencia) + "</div>" : "");

    /* a recomendação mostra o que a sustenta e o que pesa contra — é o que
       separa "faça isto" de "isto foi medido" */
    if ((c.a_favor || []).length) {
      h += '<div class="lados"><span class="k">o que sustenta</span><ul>' +
        c.a_favor.map(function (x) { return "<li>" + forte(x) + "</li>"; }).join("") + "</ul></div>";
    }
    if ((c.contra || []).length) {
      h += '<div class="lados"><span class="k">o que pesa contra</span><ul>' +
        c.contra.map(function (x) { return "<li>" + forte(x) + "</li>"; }).join("") + "</ul></div>";
    }
    if (tem(c.o_que_aumentaria)) {
      h += '<div class="sobe">o que aumentaria a confiança: ' + esc(c.o_que_aumentaria) + "</div>";
    }
    return h + "</div>";
  }

  /* ── §9 · o cartão de insight ──
     Toda ferramenta termina respondendo cinco coisas: o que aconteceu, por que
     importa, quem age, o que fazer e como encaminhar. O payload traz as cinco
     prontas — o casco só as põe na ordem e dá cor ao que é fato e ao que é
     recomendação. Nada aqui é escrito na tela. */
  var INSIGHTS = {};

  var GRAV = { alta: "var(--crit)", media: "var(--warn)", baixa: "var(--t3)" };

  function linhaInsight(k, txt, cls) {
    if (!tem(txt)) return "";
    return '<div class="in-l ' + cls + '"><span class="k">' + esc(k) + "</span><p>" + forte(txt) + "</p></div>";
  }

  function cartaoInsight(i) {
    if (!i) return "";
    if (tem(i.insight_id)) INSIGHTS[i.insight_id] = i;
    var en = i.encaminhamento || {};
    var id = esc(i.insight_id || "");
    var h = '<div class="insight" style="--sev:' + (GRAV[i.gravidade] || "var(--t3)") + '">' +
      '<div class="in-cab"><span class="sev">' + esc(tem(i.gravidade_rotulo) ? i.gravidade_rotulo : i.gravidade) + "</span>" +
      '<span class="onde mono">' + esc(i.onde) + "</span></div>" +
      "<h3>" + esc(i.titulo) + "</h3>" +
      linhaInsight("fato", i.fato, "l-fato") +
      linhaInsight("por que importa", i.por_que_importa, "l-pq") +
      linhaInsight("ação", i.acao, "l-acao") +
      linhaInsight("o que perguntar", i.o_que_perguntar, "l-perg") +
      linhaInsight("não faça", i.nao_faca, "l-nao");

    h += '<div class="in-pe"><span class="k">para</span><b>' + esc(i.quem_age_rotulo) + "</b>" +
      (tem(i.revisar_em_dias)
        ? '<span class="mono">revisar em ' + plural(i.revisar_em_dias, "dia", "dias") + "</span>" : "") +
      (tem(i.medido_em) ? '<span class="mono">medido em ' + data(i.medido_em) + "</span>" : "") + "</div>";

    /* §11 · evidência não é tela: é gaveta dentro do insight */
    if ((i.evidencias || []).length) {
      h += '<details class="in-ev"><summary>ver ' +
        plural(i.evidencias_total, "evidência", "evidências") + "</summary><ul>" +
        i.evidencias.map(function (e) {
          return "<li>" + (tem(e.o_que) ? '<span class="k mono">' + esc(e.o_que) + "</span>" : "") +
            "<span>" + esc(tem(e.texto) ? e.texto : (tem(e.valor) ? e.onde + ": " + e.valor : e.onde)) +
            "</span></li>";
        }).join("") + "</ul></details>";
    }

    h += carimbo(i.carimbo);

    h += '<div class="in-acoes">' +
      (tem(i.link) && ROTAS[String(i.link).split("/")[0]]
        ? '<button type="button" class="chip" data-ir="' + esc(i.link) + '">abrir</button>' : "");

    if ((en.para || []).length) {
      h += '<details class="enc"><summary>encaminhar</summary>' +
        '<div class="enc-corpo"><span class="rot-sis">encaminhar para</span>' +
        '<div class="enc-quem">' + en.para.map(function (p) {
          return '<label><input type="radio" name="enc-' + id + '" value="' + esc(p.chave) + '"' +
            (p.chave === en.recomendado ? " checked" : "") + "><span>" + esc(p.rotulo) + "</span></label>";
        }).join("") + "</div>" +
        '<div class="enc-bt">' +
        '<button type="button" class="chip" data-enc="copiar" data-in="' + id + '">copiar</button>' +
        '<button type="button" class="chip" data-enc="whats" data-in="' + id + '">WhatsApp</button>' +
        '<button type="button" class="chip" data-enc="email" data-in="' + id + '">e-mail</button>' +
        (tem(i.link) ? '<button type="button" class="chip" data-enc="link" data-in="' + id + '">copiar link</button>' : "") +
        '<span class="enc-ok" data-ok="' + id + '"></span></div>' +
        '<p class="pq">' + esc(en.como_usar) + "</p></div></details>";
    }
    return h + "</div></div>";
  }

  /* o texto do encaminhamento vem pronto: abertura do destinatário + corpo.
     A tela não escreve nada — só junta as duas partes que o payload manda. */
  function textoEnc(i, quem) {
    var en = i.encaminhamento || {};
    var p = (en.para || []).filter(function (x) { return x.chave === quem; })[0];
    if (!p) return en.texto_pronto || en.corpo || "";
    return (tem(p.abertura) ? p.abertura + "\n\n" : "") + (en.corpo || "");
  }

  function quemEscolhido(id) {
    var r = document.querySelector('input[name="enc-' + id + '"]:checked');
    return r ? r.value : ((INSIGHTS[id] || {}).encaminhamento || {}).recomendado;
  }

  function avisoEnc(id, txt) {
    var n = document.querySelector('[data-ok="' + id + '"]');
    if (!n) return;
    n.textContent = txt;
    setTimeout(function () { if (n) n.textContent = ""; }, 2600);
  }

  function encaminhar(acao, id) {
    var i = INSIGHTS[id];
    if (!i) return;
    if (acao === "link") {
      var url = location.href.split("#")[0] + "#/" + i.link;
      copiar(url, id, "link copiado");
      return;
    }
    var txt = textoEnc(i, quemEscolhido(id));
    if (acao === "copiar") { copiar(txt, id, "texto copiado"); return; }
    if (acao === "whats") { window.open("https://wa.me/?text=" + encodeURIComponent(txt), "_blank"); return; }
    if (acao === "email") {
      location.href = "mailto:?subject=" + encodeURIComponent(i.titulo) + "&body=" + encodeURIComponent(txt);
    }
  }

  function copiar(txt, id, ok) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(txt).then(function () { avisoEnc(id, ok); },
        function () { avisoEnc(id, "não deu para copiar"); });
      return;
    }
    var t = document.createElement("textarea");
    t.value = txt;
    document.body.appendChild(t);
    t.select();
    try { document.execCommand("copy"); avisoEnc(id, ok); } catch (e) { avisoEnc(id, "não deu para copiar"); }
    t.remove();
  }

  /* §10.2 · a agenda é pauta, não ranking: a ordem é a da conversa */
  function linhaAgenda(a) {
    var h = '<details class="pauta" style="--sev:' + (COR[a.faixa] || "var(--cyan)") + '"><summary>' +
      '<span class="pa-onde"><b>' + esc(a.rotulo) + "</b><span>" + esc(a.unidade) + "</span></span>" +
      '<span class="pa-viu">' + esc(a.o_que_vimos) + "</span>" +
      '<span class="pa-sev mono">' + esc(tem(a.prioridade_rotulo) ? a.prioridade_rotulo : a.prioridade) + "</span></summary>" +
      '<div class="pauta-corpo">' +
      linhaInsight("o que conversar", a.o_que_conversar, "l-perg") +
      ((a.leve || []).length
        ? '<div class="in-l l-fato"><span class="k">levar na visita</span><ul class="leve">' +
          a.leve.map(function (x) {
            return "<li><span class=\"k mono\">" + esc(x.o_que) + "</span><span>" + esc(x.texto) + "</span></li>";
          }).join("") + "</ul></div>"
        : "") +
      (a.acao
        ? linhaInsight("ação", a.acao.o_que + " · " + a.acao.prazo + " · " + a.acao.dono + " · " + a.acao.custo, "l-acao")
        : "") +
      linhaInsight("não faça", a.nao_faca, "l-nao") +
      cartaoInsight(a.insight) + "</div></details>";
    return h;
  }

  /* bloco que é leitura da CIDADE dentro da página da loja: dizer de quem é
     o número evita que um dado de cidade seja lido como desempenho da loja */
  function daCidade(rotulo, quantas) {
    return '<div class="da-cidade">leitura da cidade' +
      (tem(rotulo) ? " — " + esc(rotulo) : "") +
      (quantas ? ", vale para as " + esc(quantas) + " lojas da rede aqui" : "") + "</div>";
  }

  /* ── a jornada: em que momento a unidade dói ── */
  function capJornada(j) {
    if (!j) return "";
    var h = '<div class="painel"><div class="painel-cab">' + capCab("jornada") + "</div>" +
      '<p class="manchete-cap">' + esc(j.manchete) + "</p>";

    h += '<div class="jornada">' + (j.estagios || []).map(function (e) {
      if (!e.medido) {
        return '<div class="etapa vazia"><div class="etapa-cab"><span class="nm">' + esc(e.rotulo) + "</span>" +
          '<span class="oq">' + esc(e.o_que_e) + "</span></div>" +
          '<div class="pq">' + esc(e.porque_vazio || "nenhuma avaliação fala deste momento") + "</div></div>";
      }
      var grau = e.pct_dor >= 60 ? "alta" : (e.pct_dor >= 34 ? "media" : "baixa");
      return '<details class="etapa dor-' + grau + '"><summary>' +
        '<span class="nm">' + esc(e.rotulo) + "</span>" +
        '<span class="oq">' + esc(e.o_que_e) + "</span>" +
        '<span class="barra"><i style="width:' + (e.pct_dor || 0) + '%"></i></span>' +
        '<span class="pct mono">' + br(e.pct_dor) + "%</span>" +
        (e.amostra_curta ? '<span class="curta">amostra curta</span>' : "") +
        "</summary><div class=\"etapa-corpo\">" +
        '<div class="frase">' + esc(e.frase) + "</div>" +
        '<div class="quem">quem resolve: ' + esc(e.quem_resolve) + "</div>" +
        (e.exemplos || []).map(function (x) {
          return '<blockquote class="fala"><span class="est mono">' + "★".repeat(x.nota) + "</span>" +
            '<span class="dt mono">' + dataCurta(x.data) + "</span>" +
            "<p>" + esc(x.texto) + "</p></blockquote>";
        }).join("") + "</div></details>";
    }).join("") + "</div>";

    h += '<p class="pe-cap">' + br(j.sem_estagio) + " de " + br(j.com_texto) +
      " avaliações com texto não dizem em que momento a pessoa estava — " + esc(j.porque_sem_estagio) + ".</p>";
    return h + carimbo(j.confianca) + "</div>";
  }

  /* ── o livro de ações: o ciclo de cada problema ── */
  var VEREDITO = {
    cedo_demais: { rot: "cedo demais", cor: "var(--t3)" },
    melhorou: { rot: "melhorou", cor: "var(--ok)" },
    piorou: { rot: "piorou", cor: "var(--crit)" },
    parado: { rot: "sem mudança", cor: "var(--warn)" }
  };

  function capAcoes(a) {
    if (!a || !(a.arcos || []).length) return "";
    var h = '<div class="painel"><div class="painel-cab">' + capCab("acoes") +
      '<span class="dir">' + plural(a.total, "problema aberto", "problemas abertos") + "</span></div>";

    /* o aviso explica por que ainda não há veredito — a tabela fica de pé */
    if (tem(a.aviso)) h += '<p class="aviso-curto">' + esc(a.aviso) + "</p>";

    h += '<div class="tabela-wrap"><table class="grade"><thead><tr>' +
      "<th>O problema</th><th>O que recomendamos</th>" +
      '<th class="n">Antes</th><th class="n">Depois</th><th class="n">Dias</th><th>Resultado</th>' +
      "</tr></thead><tbody>" +
      a.arcos.map(function (x) {
        var v = VEREDITO[x.veredito] || { rot: x.veredito, cor: "var(--t3)" };
        return "<tr><td>" + esc(x.problema) + "</td>" +
          "<td>" + esc(x.acao_recomendada) + "</td>" +
          '<td class="n mono">' + dec(x.antes) + '</td><td class="n mono">' + dec(x.depois) + "</td>" +
          '<td class="n mono">' + br(x.dias) + "</td>" +
          '<td><span class="selo" style="--sev:' + v.cor + '">' + esc(v.rot) + "</span></td></tr>";
      }).join("") + "</tbody></table></div>";

    h += '<p class="pe-cap">A execução não é medida: o portal lê o mundo de fora e não fala com a unidade. ' +
      "O que ele mede é se o número mudou depois.</p>";
    return h + "</div>";
  }

  /* ── a guerra comercial da cidade ── */
  function capOferta(o, ondeEsta) {
    if (!o) return "";
    var h = '<div class="painel"><div class="painel-cab">' + capCab("oferta") + "</div>";
    if (ondeEsta === "clinica") h += daCidade(o.rotulo, null);

    h += '<p class="manchete-cap">' + esc(o.tese) + "</p>";
    if (tem(o.posicao_vaga)) {
      h += '<div class="vaga"><span class="k">a posição que ninguém ocupou</span>' +
        "<p>" + esc(o.posicao_vaga) + "</p></div>";
    }

    h += '<div class="eixos">' + (o.eixos || []).map(function (e) {
      return '<div class="eixo-l"><span class="nm">' + esc(e.rotulo) + "</span>" +
        '<span class="barra"><i style="width:' + (e.pct || 0) + '%"></i></span>' +
        '<span class="pct mono">' + br(e.anuncios) + "</span>" +
        '<span class="oq">' + esc(e.o_que_significa) + "</span></div>";
    }).join("") + "</div>";

    if (o.fora_do_produto) {
      h += '<p class="pe-cap">' + plural(o.fora_do_produto, "anúncio ficou", "anúncios ficaram") +
        " de fora: " + esc(o.porque_fora) + "</p>";
    }
    if (o.amostra_curta) h += '<p class="aviso-curto">amostra curta — a leitura pode virar na próxima coleta</p>';
    return h + carimbo(o.confianca) + "</div>";
  }

  /* ── a cidade na imprensa, e quem publica ── */
  function capImprensa(im) {
    if (!im) return "";
    var h = '<div class="painel"><div class="painel-cab">' + capCab("o_que_a_cidade_publica") + "</div>";
    if (!im.medido || !(im.materias || []).length) {
      return h + vazio("Nada lido nesta cidade", im.porque_vazio || "A varredura não encontrou matéria nesta janela.") + "</div>";
    }
    h += '<p class="manchete-cap">' + esc(im.manchete) + "</p>" +
      '<ul class="materias">' + im.materias.map(function (m) {
        return '<li><a href="' + esc(m.link) + '" target="_blank" rel="noopener">' + esc(m.titulo) + "</a>" +
          '<span class="fonte mono">' + esc(m.veiculo) + (tem(m.data) ? " · " + dataCurta(m.data) : "") + "</span></li>";
      }).join("") + "</ul>";
    h += '<p class="pe-cap">mostrando ' + br(im.mostrando) + " de " + br(im.total) + " matérias lidas</p>";
    return h + "</div>";
  }

  function capRitmo(rp) {
    if (!rp) return "";
    var h = '<div class="painel"><div class="painel-cab"><span class="sobre-cap">quem publica aqui</span>' +
      "<h2>Ritmo de publicação</h2></div>";
    if (!rp.medido || !(rp.lista || []).length) {
      return h + vazio("Nenhum perfil medido", rp.porque_vazio || "A coleta não encontrou perfil desta cidade.") + "</div>";
    }
    h += '<p class="manchete-cap">' + esc(rp.manchete) + "</p>" +
      '<div class="perfis">' + rp.lista.map(function (p) {
        return '<div class="perfil-l' + (p.parado ? " parado" : "") + '">' +
          '<span class="ponto" style="--sev:' + (p.parado ? "var(--crit)" : "var(--ok)") + '"></span>' +
          '<span class="hd mono">@' + esc(p.handle) + "</span>" +
          '<span class="fr">' + esc(p.frase) + "</span>" +
          '<span class="cur mono">' + br(p.curtidas_medianas) + " curtidas</span></div>";
      }).join("") + "</div>";
    return h + "</div>";
  }

  /* ── §12.1 · a busca feita da porta da clínica ── */

  function escalaCart(rot, n, de, perto) {
    return '<div class="escala' + (perto ? " perto" : "") + '"><div class="rot">' + esc(rot) + "</div>" +
      '<div class="v mono">' + br(n) + "<i>de " + br(de) + "</i></div>" +
      '<div class="k">buscas em que apareceu</div></div>';
  }

  var gemeosDaRede = {};

  function capGemeo(localId) {
    var g = gemeosDaRede || {};
    var L = (g.lojas || []).filter(function (x) { return x.local_id === localId; })[0];
    if (!L || !(L.gemeos || []).length) return "";
    var p = L.gemeos[0];
    var h = '<div class="painel"><div class="painel-cab">' + capCab("gemeos") + "</div>" +
      '<p class="manchete-cap">' + esc(L.frase) + "</p>" +
      '<div class="gemeo"><div class="gm-cab"><span class="nm">' + esc(p.rotulo) +
      (tem(p.unidade) ? " · " + esc(p.unidade) : "") + "</span>" +
      '<span class="dist mono">distância ' + dec(p.distancia) + " · " +
      br(p.eixos_usados) + " de " + br(p.eixos_possiveis) + " eixos</span></div>" +
      '<p class="pq">' + esc(p.porque) + "</p>" +
      ((p.diferencas || []).length
        ? '<div class="in-l l-fato"><span class="k">o que as separa</span><ul class="leve">' +
          p.diferencas.map(function (x) {
            return '<li><span class="k mono">' + esc(x.o_que) + "</span><span>" + esc(x.texto) + "</span></li>";
          }).join("") + "</ul></div>"
        : "") +
      '<div class="filtros"><button type="button" class="chip" data-ir="clinicas/' + esc(p.local_id) +
      '">abrir a mais parecida</button>' +
      '<button type="button" class="chip" data-ir="anomalias">quem está longe dos semelhantes</button></div>' +
      "</div>";

    if ((L.gemeos || []).length > 1) {
      h += '<div class="nuvem" style="margin-top:12px">' + L.gemeos.slice(1).map(function (x) {
        return '<span>' + esc(x.rotulo) + (tem(x.unidade) ? " · " + esc(x.unidade) : "") +
          ' <b class="mono">' + dec(x.distancia) + "</b></span>";
      }).join("") + "</div>";
    }
    return h + carimbo(L.carimbo) + "</div>";
  }

  function capPerto(pc) {
    if (!pc) return "";
    var nc = pc.na_cidade || {};
    /* quando a cidade diz zero e a porta diz o contrário, a informação É essa:
       não é detalhe de rodapé */
    var contradiz = nc.aparece_em === 0 && pc.aparece_em > 0;
    var h = '<div class="painel' + (pc.invisivel_perto ? " grave" : "") + '"><div class="painel-cab">' +
      capCab("perto_da_loja") +
      '<span class="dir">' + plural(pc.de, "busca testada", "buscas testadas") + "</span></div>";

    h += '<div class="escalas">' +
      escalaCart("na cidade inteira", nc.aparece_em, nc.de, false) +
      escalaCart("perto da clínica", pc.aparece_em, pc.de, true) + "</div>";

    h += '<p class="frase-topo' + (pc.invisivel_perto ? " alerta" : "") + '">' + esc(pc.frase) + "</p>";
    if (contradiz) {
      h += '<p class="escala-aviso">A leitura da cidade inteira não vale nesta escala: o paciente procura de onde está, e ninguém disputa o nome do município inteiro.</p>';
    }

    h += '<div class="fatos">' +
      fato('<span class="num"' + (pc.invisivel_perto ? ' style="color:var(--crit)"' : "") + ">" +
        br(pc.aparece_em) + "</span>", "de " + br(pc.de) + " buscas testadas") +
      fato('<span class="num">' + br(pc.em_primeiro) + "</span>", "vezes em primeiro") +
      fato('<span class="num">' + (tem(pc.melhor_posicao) ? br(pc.melhor_posicao) + "º" : "—") +
        "</span>", "melhor posição") +
      "</div>";

    if ((pc.buscas || []).length) {
      h += '<div class="buscas">' + pc.buscas.map(function (b) {
        return '<div class="busca-l' + (tem(b.posicao) ? "" : " fora") + '">' +
          '<span class="fr">' + esc(b.frase) + "</span>" +
          '<span class="int mono">' + esc(b.intencao) + "</span>" +
          '<span class="pos mono">' + (tem(b.posicao) ? br(b.posicao) + "º" : "fora") + "</span>" +
          '<span class="tp">' + esc(b.topo) +
          (tem(b.topo_metros) ? '<i class="mono">' + br(b.topo_metros) + " m da porta</i>" : "") +
          "</span></div>";
      }).join("") + "</div>";
    }

    if ((pc.quem_aparece_na_frente || []).length) {
      h += '<div class="na-frente"><span class="rot-sis">quem apareceu na frente</span>' +
        '<p class="pq">é posição na ordem do mapa, não paciente perdido: para onde o paciente foi ninguém mediu.</p>' +
        pc.quem_aparece_na_frente.map(function (q) {
          return '<div class="mov"><span class="nm">' + esc(q.nome) + "</span>" +
            '<span class="par mono">' + plural(q.vezes_na_frente, "vez à frente", "vezes à frente") +
            "</span></div>";
        }).join("") + "</div>";
    }

    h += pe("medido em " + data(pc.medido_em) +
      " · o raio é a preferência que damos ao Google, não a área de captação — distância no mapa não é tempo de deslocamento");
    return h + carimbo(pc.confianca) + "</div>";
  }

  /* ── §11.1 · o território desta clínica ── */

  function vizinhoCart(rot, x) {
    if (!x) return "";
    return '<div class="vizinho"><div class="rot">' + esc(rot) + "</div>" +
      '<div class="km mono">' + dec(x.km) + " km</div>" +
      '<div class="nm">' + esc(x.nome) + "</div>" +
      '<div class="mt mono">' + dec(x.nota) + " · " + plural(x.avaliacoes, "avaliação", "avaliações") +
      (tem(x.bairro) ? " · " + esc(x.bairro) : "") + "</div></div>";
  }

  function capTerritorio(t) {
    if (!t) return "";
    var h = '<div class="painel"><div class="painel-cab"><span class="sobre-cap">seu território</span>' +
      "<h2>O que existe em volta desta clínica</h2>" +
      (tem(t.bairro) ? '<span class="dir">' + esc(t.bairro) + "</span>" : "") + "</div>";
    if (!t.medido) {
      return h + vazio("Esta unidade não tem posição no mapa",
        "A ficha não trouxe coordenada, então o que existe em volta dela não foi medido.") + "</div>";
    }

    h += '<p class="frase-topo">' + esc(t.frase_fato) + "</p>" +
      '<div class="vizinhos">' +
      vizinhoCart("a clínica mais próxima", t.clinica_mais_proxima) +
      vizinhoCart("a mais próxima que vende aparelho", t.aparelho_mais_proximo) +
      vizinhoCart("a unidade da rede mais próxima", t.unidade_da_rede_mais_proxima) +
      "</div>";

    var raios = t.raios || {}, chaves = Object.keys(raios);
    if (chaves.length) {
      h += '<div class="tabela-wrap" style="margin-top:20px"><table class="grade"><thead><tr><th>Raio</th>' +
        '<th class="n">Clínicas</th><th class="n">De aparelho</th><th class="n">Da rede</th></tr></thead><tbody>' +
        chaves.map(function (k) {
          var r = raios[k] || {};
          return '<tr><td class="nome mono">' + esc(k) + '</td><td class="n">' + br(r.clinicas) + "</td>" +
            '<td class="n">' + br(r.de_aparelho) + '</td><td class="n">' + br(r.da_rede) + "</td></tr>";
        }).join("") + "</tbody></table></div>";
    }

    /* a inferência não pode parecer medição: mesma escala, cor mais fria e
       rótulo em mono dizendo o que ela é */
    var px = t.proximidade_entre_unidades;
    if (px) {
      h += '<div class="inferencia"><div class="cab"><span class="nat mono">' +
        esc(px.natureza === "inferencia" ? "inferência" : px.natureza) + "</span>" +
        '<span class="km mono">' + dec(px.km) + " km</span></div><p>" + esc(px.leitura) + "</p></div>";
    }
    return h + carimbo(t.confianca) + "</div>";
  }

  /* ── §11.2 e §11.5 · o movimento do mercado ── */

  var SEV = { critica: "var(--crit)", alta: "var(--crit)", media: "var(--warn)", baixa: "var(--t3)" };

  function eventoLinha(e) {
    return '<div class="evento" style="--sev:' + (SEV[e.severidade] || "var(--t3)") + '">' +
      '<div class="ev-cab"><span class="sev mono">' + esc(e.severidade) + "</span>" +
      '<span class="pr mono">' + esc(e.rotulo) + "</span>" +
      '<span class="dt mono">' + data(e.data) + "</span></div>" +
      '<div class="tt">' + esc(e.titulo) + "</div>" +
      '<div class="ft">' + esc(e.fato) + "</div>" +
      (tem(e.por_que_importa)
        ? '<div class="pq"><span class="rot-sis">por que importa</span>' + esc(e.por_que_importa) + "</div>" : "") +
      (tem(e.decisao)
        ? '<div class="dec"><span class="rot-sis">a decisão</span>' + esc(e.decisao) + "</div>" : "") +
      "</div>";
  }

  function capMovimentos(mv, rotulo) {
    if (!mv) return "";
    var r = mv.resumo || {};
    var h = '<div class="painel"><div class="painel-cab">' +
      capCab("mudancas_do_mercado") +
      (tem(r.eventos) ? '<span class="dir">' + plural(r.eventos, "evento", "eventos") + "</span>" : "") +
      "</div>" + (mv.e_da_cidade ? daCidade(r.rotulo || rotulo) : "");
    h += (mv.eventos || []).length
      ? mv.eventos.map(eventoLinha).join("")
      : vazio("Nada se moveu nesta janela", r.porque);
    /* a frase de método é o que impede alguém de achar que sumiu clínica
       quando foi a varredura que variou */
    if (tem(r.aviso_de_metodo)) h += '<div class="proc">' + esc(r.aviso_de_metodo) + "</div>";
    else if (tem(r.porque) && (mv.eventos || []).length) h += '<div class="proc">' + esc(r.porque) + "</div>";
    return h + "</div>";
  }

  /* ── §11.3 · de quem é o conserto ── */

  function capExecucao(ex) {
    if (!ex || !(ex.itens || []).length) return "";
    var h = '<div class="painel"><div class="painel-cab">' + capCab("execucao") +
      '<span class="dir">' + br(ex.de_marketing) + " de mídia · " + br(ex.de_operacao) +
      " da unidade</span></div>" +
      '<p class="exec-nota">Sem orçamento e sem promessa de retorno: nenhum dos dois foi medido.</p>';

    h += ex.itens.map(function (it) {
      var e = it.execucao || {};
      var cab, corpo;
      if (e.necessaria === false) {
        cab = '<span class="tag mono">não precisa de execução</span>' +
          (tem(e.tipo) ? '<span class="tp mono">' + esc(e.tipo) + "</span>" : "");
        corpo = (tem(e.porque_nao) ? '<p class="pq">' + esc(e.porque_nao) + "</p>" : "") +
          (tem(e.metrica_de_validacao)
            ? '<div class="met"><span class="rot-sis">como conferir</span>' + esc(e.metrica_de_validacao) + "</div>" : "");
        return '<div class="exec exec-nao"><div class="ex-cab">' + cab + "</div>" +
          '<div class="pb">' + forte(it.problema) + "</div>" + corpo + carimbo(it.confianca) + "</div>";
      }
      if (!it.e_marketing) {
        cab = '<span class="tag mono">é da unidade</span>' +
          (tem(e.quem_resolve) ? '<span class="tp mono">' + esc(e.quem_resolve) + "</span>" : "");
        corpo = (tem(e.porque_nao_e_marketing)
          ? '<div class="met"><span class="rot-sis">por que campanha não resolve</span>' +
            esc(e.porque_nao_e_marketing) + "</div>" : "") +
          (tem(e.metrica_de_validacao)
            ? '<div class="met"><span class="rot-sis">como conferir</span>' + esc(e.metrica_de_validacao) + "</div>" : "") +
          (tem(e.recoletar_em_dias)
            ? '<div class="ex-pe mono">recoletar em ' + plural(e.recoletar_em_dias, "dia", "dias") + "</div>" : "");
        return '<div class="exec exec-unidade"><div class="ex-cab">' + cab + "</div>" +
          '<div class="pb">' + forte(it.problema) + "</div>" + corpo + carimbo(it.confianca) + "</div>";
      }
      cab = '<span class="tag mono">briefing de mídia</span>' +
        (tem(e.especialidade) ? '<span class="tp mono">' + esc(e.especialidade) + "</span>" : "");
      corpo = (tem(e.objetivo)
        ? '<div class="met"><span class="rot-sis">objetivo</span>' + esc(e.objetivo) + "</div>" : "") +
        ((e.evidencias || []).length
          ? '<div class="met"><span class="rot-sis">o que sustenta</span><ul>' +
            e.evidencias.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul></div>" : "") +
        ((e.nao_fazer || []).length
          ? '<div class="met nao-fazer"><span class="rot-sis">o que não fazer</span><ul>' +
            e.nao_fazer.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul></div>" : "") +
        (tem(e.entregavel_sugerido)
          ? '<div class="met"><span class="rot-sis">entregável sugerido</span>' + esc(e.entregavel_sugerido) + "</div>" : "") +
        (tem(e.metrica_de_validacao)
          ? '<div class="met"><span class="rot-sis">como validar</span>' + esc(e.metrica_de_validacao) + "</div>" : "") +
        '<div class="ex-pe mono">' + (tem(e.prazo) ? esc(e.prazo) : "") +
        (tem(e.recoletar_em_dias) ? " · recoletar em " + plural(e.recoletar_em_dias, "dia", "dias") : "") + "</div>";
      return '<div class="exec exec-briefing"><div class="ex-cab">' + cab + "</div>" +
        '<div class="pb">' + forte(e.problema || it.problema) + "</div>" + corpo + carimbo(it.confianca) + "</div>";
    }).join("");

    return h + "</div>";
  }

  /* ── §11.4 · a cidade por dentro: cidade com várias unidades não é um
     mercado homogêneo ── */

  function capBairros(b) {
    if (!b) return "";
    var nome = {};
    (b.territorio || []).forEach(function (t) { nome[t.local_id] = t.unidade; });

    var h = '<div class="painel"><div class="painel-cab">' + capCab("bairros") +
      '<span class="dir">' + plural(b.bairros_medidos, "bairro medido", "bairros medidos") + " · " +
      plural(b.clinicas_medidas, "clínica com endereço legível", "clínicas com endereço legível") +
      "</span></div>";

    if ((b.territorio || []).length) {
      h += '<div class="terr-lista">' + b.territorio.map(function (t) {
        var r1 = (t.raios || {})["1km"] || {};
        return '<button type="button" class="terr" data-ir="clinicas/' + esc(t.local_id) + '">' +
          '<div class="un">' + esc(t.unidade) + "</div>" +
          '<div class="ba mono">' + esc(t.bairro) + "</div>" +
          '<div class="fr">' + esc(t.frase_fato) + "</div>" +
          '<div class="rd mono">a 1 km: ' + br(r1.clinicas) + " clínicas · " + br(r1.de_aparelho) +
          " de aparelho · " + br(r1.da_rede) + " da rede</div>" +
          (t.proximidade_entre_unidades
            ? '<div class="inf mono">inferência · ' + esc(t.proximidade_entre_unidades.leitura) + "</div>" : "") +
          "</button>";
      }).join("") + "</div>";
    }

    if ((b.bairros || []).length) {
      h += '<div class="bairros">' + comMais(b.bairros, 10, b.bairros_medidos, function (x) {
        return '<div class="bairro' + (x.temos_unidade ? " nosso" : "") + '">' +
          '<span class="nm">' + esc(x.bairro) + "</span>" +
          '<span class="qt mono">' + plural(x.clinicas, "clínica", "clínicas") + "</span>" +
          '<span class="av mono">' + br(x.avaliacoes_somadas) + " avaliações somadas</span>" +
          (x.temos_unidade
            ? '<span class="nossa">' + (x.nossas || []).map(function (id) {
                return "<i>" + esc(nome[id] || id) + "</i>";
              }).join("") + "</span>" : "") +
          "</div>";
      }) + "</div>";
    }

    return h + pe("bairro cheio de clínica é onde as clínicas abrem, não necessariamente onde o paciente mora · " +
      "raios medidos: " + (b.raios_declarados_km || []).join(", ") + " km · " +
      plural(b.clinicas_sem_coordenada, "clínica sem coordenada", "clínicas sem coordenada")) + "</div>";
  }

  /* ── §12.4 · o território de uma cidade do Radar ── */

  function terrLinha(t) {
    if (!t) return "";
    return '<div class="terr-frase"><span class="rot-sis">o território</span>' +
      "<p>" + esc(t.frase) + "</p>" +
      '<p class="pq">' + esc(t.e_concentracao_nao_demanda) + "</p>" +
      '<div class="meta mono">' + plural(t.bairros_medidos, "bairro medido", "bairros medidos") + " · " +
      plural(t.clinicas_mapeadas, "clínica mapeada", "clínicas mapeadas") + "</div></div>";
  }

  /* ── §12.5 · a busca perto da clínica, loja por loja ── */

  function telaPerto(d) {
    var c = card("perto");
    var html = cabecalhoTela("perto_da_loja") + comoLer("perto_da_loja") +
      '<div class="painel"><div class="painel-cab"><h2>' + esc(c.pergunta) + "</h2>" +
      '<span class="dir">medido em ' + data(d.medido_em) + "</span></div>" +
      '<p class="frase-topo">' + esc(c.frase) + "</p>" +
      '<p class="sub-painel">' + esc(d.por_que_existe) + "</p>" +
      pe("o que isto não é: " + esc(d.o_que_nao_e)) + "</div>";

    html += '<div class="painel"><div class="painel-cab"><h2>Loja por loja, da pior para a melhor</h2>' +
      '<span class="dir">as duas leituras lado a lado, nunca fundidas</span></div>' +
      '<div class="perto-lista">' + (d.lojas || []).map(function (L) {
        var nc = L.na_cidade || {};
        return '<button type="button" class="perto-l' + (L.invisivel_perto ? " invisivel" : "") +
          '" data-ir="clinicas/' + esc(L.local_id) + '">' +
          '<div class="cb"><span class="pr mono">' + esc(L.rotulo) + "</span>" +
          '<span class="un">' + esc(L.unidade) + "</span></div>" +
          '<div class="nums">' +
          '<span class="par"><i>perto da clínica</i><b class="mono">' + br(L.aparece_em) +
          " de " + br(L.de) + "</b></span>" +
          '<span class="par"><i>em primeiro</i><b class="mono">' + br(L.em_primeiro) + "</b></span>" +
          '<span class="par cid"><i>na cidade inteira</i><b class="mono">' + br(nc.aparece_em) +
          " de " + br(nc.de) + "</b></span></div>" +
          '<div class="fr">' + esc(L.frase) + "</div></button>";
      }).join("") + "</div></div>";

    return html + rodapeMetodo("perto_da_loja") + rodape();
  }

  /* ---------- PRAÇAS ---------- */

  function telaPracas() {
    var cob = franq.cobertura || {};
    return telaTopo("o mercado de cada cidade", card("pracas").titulo, card("pracas").frase) +
      '<div class="cartoes">' + (manifest.pracas || []).map(function (p) {
        return '<button type="button" class="cartao" data-ir="pracas/' + esc(p.praca_id) + '">' +
          '<div class="cid">' + (p.uf || []).join(" · ") + "</div>" +
          '<div class="un">' + esc(p.rotulo) + "</div>" +
          '<div class="met"><div>' + br(p.estudos) + "<i>estudos nesta praça</i></div></div></button>";
      }).join("") + "</div>" +
      pe(br(cob.pracas_da_rede_estudadas) + " praças da rede estudadas") + rodape();
  }

  function telaPraca(d) {
    var html = '<button type="button" class="voltar" data-ir="pracas">← todas as praças</button>' +
      telaTopo(d.eyebrow || "o mercado desta cidade", d.rotulo, null);

    html += '<div class="painel"><div class="painel-cab"><h2>' + esc(d.tese_titulo) + "</h2></div>" +
      '<p class="sub" style="margin:0;font-size:15.5px;line-height:1.6;color:var(--t2)">' + forte(d.tese) + "</p>" +
      pe("base: " + esc(d.base)) + "</div>";

    if (d.o_que_mudou) {
      var m = d.o_que_mudou;
      html += '<div class="painel"><div class="painel-cab"><h2>O que mudou nesta cidade</h2>' +
        '<span class="dir">' + plural(m.dias_medidos, "dia medido", "dias medidos") + "</span></div>";
      if (tem(m.aviso)) html += '<p class="aviso-curto" style="margin-bottom:12px">' + esc(m.aviso) + "</p>";
      (m.contador_caiu || []).forEach(function (x) { html += movLinha(x, true); });
      (m.nossas || []).forEach(function (x) { html += movLinha(x); });
      (m.quem_mais_ganhou || []).forEach(function (x) { html += movLinha(x); });
      html += "</div>";
    }

    if (d.dna && d.dna.length) {
      html += '<div class="painel"><div class="painel-cab"><h2>Como esta cidade fala</h2></div><div class="cartoes">' +
        d.dna.map(function (x) {
          return '<div class="cartao" style="cursor:default"><div class="cid">' + esc(x.l) + "</div>" +
            '<div class="fr">' + forte(x.t) + "</div></div>";
        }).join("") + "</div></div>";
    }

    if (d.citacoes && d.citacoes.length) {
      html += '<div class="painel"><div class="painel-cab"><h2>Na voz de quem foi atendido</h2></div>' +
        d.citacoes.map(function (c) {
          return '<div class="linha"><div style="font-size:16px;line-height:1.55">' + esc(c.t) + "</div>" +
            '<div class="mono" style="font-size:11px;color:var(--t3);margin-top:8px">' + esc(c.c) + "</div></div>";
        }).join("") + "</div>";
    }

    if (d.placar && d.placar.length) {
      html += '<div class="painel"><div class="painel-cab"><h2>As clínicas da cidade</h2>' +
        '<span class="dir">' + forte(d.placar_nota || "") + "</span></div>" +
        '<div class="tabela-wrap"><table class="grade"><thead><tr><th>Clínica</th>' +
        '<th class="n">Nota</th><th class="n">Avaliações</th></tr></thead><tbody>' +
        d.placar.map(function (p) {
          return "<tr" + (p.proprio ? ' class="nossa"' : "") + '><td class="nome">' + esc(p.nome) + "</td>" +
            '<td class="n">' + dec(p.nota) + '</td><td class="n">' + br(p.avaliacoes) + "</td></tr>";
        }).join("") + "</tbody></table></div></div>";
    }

    if (d.temas && d.temas.length) {
      var maxT = d.temas.reduce(function (x, t) { return Math.max(x, t.pct || 0); }, 0) || 1;
      html += '<div class="painel"><div class="painel-cab"><h2>Os temas nas avaliações da cidade</h2></div>' +
        d.temas.map(function (t) {
          return '<div class="barra-tema"><span class="l">' + esc(t.tema) + "</span>" +
            '<span class="trilha"><i style="width:' + (t.pct / maxT * 100) + '%"></i></span>' +
            '<span class="v">' + dec(t.pct) + "%</span></div>";
        }).join("") + "</div>";
    }

    /* O plano é por LOJA desde que Cuiabá se revelou três lojas com três donos
       possíveis. Um botão por item de planos_das_lojas, nomeando a unidade —
       um botão único apontaria para planos/<cidade>, que o build não produz. */
    html += capBairros(d.bairros);
    html += capMovimentos(d.movimentos_do_mercado, d.rotulo);
    html += capOferta(d.oferta, "praca");
    html += capImprensa(d.imprensa);
    html += capRitmo(d.ritmo_de_publicacao);

    var pl = d.planos_das_lojas || [];
    html += '<div class="painel"><div class="painel-cab"><h2>Ao redor desta praça</h2>' +
      (pl.length > 1 ? '<span class="dir">o plano é de cada loja, não da cidade</span>' : "") +
      '</div><div class="filtros">' +
      pl.map(function (x) {
        return '<button type="button" class="chip" data-ir="' + esc(x.arquivo) + '">O plano da ' +
          esc(x.unidade) + "</button>";
      }).join("") +
      '<button type="button" class="chip" data-ir="captacao/' + esc(d.praca_id) + '">Como a cidade procura</button>' +
      "</div></div>";

    return html + rodape();
  }

  /* ---------- O QUE A REDE ENSINA ---------- */

  function telaEnsina(r) {
    var p = r[0], rival = r[1];
    var html = cabecalhoTela("padroes") + comoLer("padroes");

    if (p.hipoteses_testadas && p.hipoteses_testadas.length) {
      html += '<div class="painel"><div class="painel-cab"><h2>As explicações que caíram no teste</h2>' +
        '<span class="dir">' + br(p.hipoteses_testadas_total) + "</span></div>" +
        '<div class="hipoteses">' + p.hipoteses_testadas.map(function (h) {
          return '<div class="hipotese"><div class="h">' + esc(h.h) + "</div>" +
            '<div class="v">' + esc(h.veredito) + '</div><div class="p">' + esc(h.prova) + "</div></div>";
        }).join("") + "</div></div>";
    }

    if (p.conclusao) {
      var c = p.conclusao;
      html += '<div class="painel"><div class="painel-cab"><h2>O que sobrou de pé</h2></div>' +
        '<div class="conclusao"><div class="t">' + esc(c.t) + "</div>" +
        '<div class="b"><div class="r">o que isso quer dizer</div><div class="c">' + esc(c.leitura) + "</div></div>" +
        '<div class="b"><div class="r">o que fazer com isso</div><div class="c">' + esc(c.consequencia) + "</div></div>" +
        '<div class="b"><div class="r">a prova contrária</div><div class="c">' + esc(c.controle) + "</div></div>" +
        /* §13.5 · a conclusão é inferência por eliminação, e a tela precisa
           dizer o que nunca foi testado — senão vira fato por cansaço */
        ((c.o_que_nao_foi_testado || []).length
          ? '<div class="b b-nao"><div class="r">o que não foi testado</div><div class="c"><ul>' +
            c.o_que_nao_foi_testado.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") +
            "</ul><p>" + esc(c.porque_nao_foi_testado) + "</p></div></div>"
          : "") +
        "</div>" + carimbo(c.carimbo) + "</div>";
    }

    if (rival.padrao_da_rede && rival.padrao_da_rede.length) {
      html += '<div class="painel"><div class="painel-cab"><h2>Onde a rede perde, em toda parte</h2>' +
        '<span class="dir">decisão de rede, não de loja</span></div>' +
        pe("só quem vende aparelho entra na comparação · cada clínica precisa de " + br(rival.corte_amostra) +
          " avaliações com texto · só conta acima de " + dec(rival.corte_diferenca) + "× de diferença");
      rival.padrao_da_rede.forEach(function (e) {
        /* um eixo por linha, com barra. As lojas só aparecem quando se abre o
           eixo — uma linha por loja não sobrevive a 373. */
        var largura = e.de ? Math.max(3, Math.min(100, (e.perde_em / e.de) * 100)) : 0;
        html += '<div class="eixo"><div class="ex-t">' + esc(e.o_que_e) + "</div>" +
          '<div class="ex-barra"><i style="width:' + largura + '%"></i></div>' +
          '<div class="ex-meta mono">' + esc(e.frase) +
          (tem(e.pior_razao) ? " · até " + dec(e.pior_razao) + "×" : "") + "</div>" +
          /* §13.3 · o veredito sozinho não se defende: o corte publicado ao
             lado é o que impede um limiar que nunca dispara */
          '<div class="ex-dec mono">decisão de ' + esc(e.de_quem_e_a_decisao) + "</div>" +
          (tem(e.porque_esse_dono) ? '<p class="pq">' + esc(e.porque_esse_dono) + "</p>" : "") +
          ((e.piores || []).length
            ? '<details class="abre"><summary>' + esc(e.frase_ver_todas) + "</summary>" +
              '<p class="pq">as piores primeiro</p>' +
              e.piores.map(function (x) {
                return '<div class="linha-perde"><span>' + esc(x.rotulo) + "</span>" +
                  '<span class="rz">' + dec(x.razao) + "×</span>" +
                  '<span class="quem">' + esc(x.quem) + "</span></div>";
              }).join("") + "</details>"
            : "") +
          "</div>";
      });
      html += "</div>";
    }

    if (p.lojas && p.lojas.length) {
      html += '<div class="painel"><div class="painel-cab"><h2>As lojas, lado a lado</h2></div>' +
        '<div class="tabela-wrap"><table class="grade"><thead><tr>' +
        "<th>Loja</th><th>Cidade</th><th>Situação</th>" +
        '<th class="n">Meses</th><th class="n">Novas/mês</th><th class="n">Idade</th>' +
        '<th class="n">Avaliações</th><th class="n">5★</th><th class="n">Negativas</th>' +
        '<th class="n">Respondidas</th><th class="n">Citam o nome</th></tr></thead><tbody>' +
        p.lojas.map(function (l) {
          return '<tr><td class="nome">' + esc(l.unidade) + "</td><td>" + esc(l.rotulo) + "</td>" +
            '<td><span class="mono" style="font-size:10.5px;letter-spacing:.1em">' + esc(l.selo) + "</span></td>" +
            '<td class="n">' + br(l.meses_seguidos) + '</td><td class="n">' + dec(l.ritmo_vida) + "</td>" +
            '<td class="n">' + br(l.idade_meses) + '</td><td class="n">' + br(l.avaliacoes) + "</td>" +
            '<td class="n">' + dec(l.pct_5_estrelas) + '%</td><td class="n">' + dec(l.pct_negativas) + "%</td>" +
            '<td class="n">' + dec(l.pct_respondidas) + '%</td><td class="n">' + dec(l.pct_nome_citado) + "%</td></tr>";
        }).join("") + "</tbody></table></div></div>";
    }

    return html + ressalvas("o que isso não enxerga", p.o_que_isso_nao_ve) +
      rodapeMetodo("padroes") + rodape();
  }

  /* ---------- RADAR ---------- */

  function telaRadar(r) {
    var d = r[0], fun = r[1], m = fun.metodo || {};
    var cob = franq.cobertura || {};
    var html = cabecalhoTela("radar") + comoLer("radar");

    html += '<div class="painel"><div class="painel-cab"><h2>As cidades estudadas a fundo</h2>' +
      '<span class="dir">' + br(cob.cidades_de_oportunidade_estudadas) + " estudadas</span></div></div>";

    (d.oportunidades || []).forEach(function (o) {
      html += '<div class="painel"><div class="op-cab">' +
        '<div class="rotulo">' + esc(o.rotulo) + "</div>" +
        '<div class="leitura">' + esc(o.leitura) + "</div></div>" +
        '<div class="fatos" style="margin-bottom:18px">' +
        fato('<span class="num">' + br(o.populacao) + "</span>", "habitantes") +
        fato('<span class="num">' + br(o.alvo_9_15) + "</span>", "de 9 a 15 anos") +
        fato('<span class="num">' + br(o.alvo_30_45) + "</span>", "de 30 a 45 anos") +
        fato('<span class="num">' + br(o.clinicas_fortes) + "</span>", "clínicas fortes") +
        fato('<span class="num">' + br(o.hab_por_clinica_forte) + "</span>", "hab. por clínica forte") +
        "</div>";
      if (o.defesa && o.defesa.length) {
        html += '<div class="rot-sis" style="margin-bottom:8px">o que pesa contra</div>' +
          o.defesa.map(function (x) {
            return '<p style="margin:0 0 10px;font-size:14px;line-height:1.6;color:var(--t2)">' + forte(x) + "</p>";
          }).join("");
      }
      html += terrLinha(o.territorio);
      if (tem(o.estudo)) {
        html += '<button type="button" class="chip" data-ir="' + esc(o.estudo) + '">Abrir o estudo completo</button>';
      }
      html += "</div>";
    });

    html += '<div class="painel"><div class="painel-cab"><h2>' + esc(card("funil").titulo) + "</h2>" +
      '<span class="dir">' + br(fun.candidatas_total) + " candidatas</span></div>" +
      '<p style="margin:0;font-size:15px;line-height:1.6;color:var(--t2)">' + esc(fun.o_que_e) + "</p>" +
      '<div style="margin-top:18px"><div class="rot-sis" style="margin-bottom:8px">como a lista é montada</div>' +
      '<p style="margin:0;font-size:14.5px;line-height:1.66;color:var(--t2)">' + esc(m.score) + "</p>" +
      pe("só entram cidades acima de " + br(m.piso_populacao) + " habitantes — " + esc(m.piso_porque) +
        " · fonte: " + esc(m.fonte)) + "</div>";

    if (m.regua_hab_por_unidade && m.regua_hab_por_unidade.length) {
      html += '<div style="margin-top:22px"><div class="rot-sis" style="margin-bottom:10px">a régua da própria rede</div>' +
        '<div class="tabela-wrap"><table class="grade"><thead><tr><th>Tamanho da cidade</th>' +
        '<th class="n">Habitantes por unidade</th><th class="n">Cidades da rede</th></tr></thead><tbody>' +
        m.regua_hab_por_unidade.map(function (f) {
          return '<tr><td class="nome">' + esc(f.faixa) + '</td><td class="n">' + br(f.mediana_hab_por_unidade) +
            '</td><td class="n">' + br(f.cidades_da_rede_na_faixa) + "</td></tr>";
        }).join("") + "</tbody></table></div></div>";
    }
    html += "</div>";

    if (fun.onde_cabem_mais && fun.onde_cabem_mais.length) {
      html += '<div class="painel"><div class="painel-cab"><h2>Onde a rede já está e ainda cabe mais</h2></div>' +
        '<div class="tira">' + fun.onde_cabem_mais.map(function (c) {
          return tiraCart("+" + br(c.folga), c.rotulo + " — " + c.leitura, "var(--ok)");
        }).join("") + "</div></div>";
    }

    if (fun.candidatas && fun.candidatas.length) {
      html += '<div class="painel"><div class="painel-cab"><h2>As candidatas, na ordem do estudo</h2>' +
        '<span class="dir">' + br(fun.candidatas_total) + "</span></div>" +
        '<div class="tabela-wrap"><table class="grade"><thead><tr>' +
        "<th>Cidade</th><th>Tamanho</th>" +
        '<th class="n">População</th><th class="n">9 a 15</th><th class="n">30 a 45</th>' +
        '<th class="n">Renda</th><th class="n">Comporta</th><th>Estudo</th></tr></thead><tbody>' +
        fun.candidatas.map(function (c) {
          return '<tr><td class="nome">' + esc(c.rotulo) + "</td><td>" + esc(c.faixa) + "</td>" +
            '<td class="n">' + br(c.populacao) + '</td><td class="n">' + br(c.alvo_9_15) + "</td>" +
            '<td class="n">' + br(c.alvo_30_45) + '</td><td class="n">' + dec(c.renda_relativa) + "×</td>" +
            '<td class="n">' + br(c.comporta_pela_regua) + "</td>" +
            "<td>" + (c.ja_estudada ? '<span class="mono" style="font-size:10.5px;color:var(--cyan)">já estudada</span>' : "") +
            "</td></tr>";
        }).join("") + "</tbody></table></div></div>";
    }

    (d.ja_tem_unidade || []).forEach(function (o) {
      html += '<div class="painel" style="border-style:dashed"><div class="painel-cab">' +
        "<h2>" + esc(o.rotulo) + '</h2><span class="dir">descartada</span></div>' +
        '<p style="margin:0;font-size:14px;color:var(--t3)">' + esc(o.conferencia && o.conferencia.motivo) + "</p>" +
        terrLinha(o.territorio) + "</div>";
    });

    return html + ressalvas("o que este estudo não enxerga", fun.o_que_isso_nao_ve) +
      ressalvas("ressalvas do radar", d.ressalvas) + rodapeMetodo("radar") + rodape();
  }

  /* ---------- §12.1 · PIPELINE DE EXPANSÃO (o Radar) ---------- */

  /* O funil e o radar eram duas telas para a mesma pergunta comercial. Aqui
     viram uma: dos 5.570 municípios até a conversa, com o motivo de cada
     queda — "6 cidades estudadas" parece pouco até se ver de onde vieram. */
  function telaPipeline(r) {
    var d = r[0], fun = r[1] || {}, m = fun.metodo || {};
    var html = cabecalhoTela("pipeline_expansao") + comoLer("pipeline_expansao");

    html += '<div class="painel"><div class="painel-cab"><h2>O caminho até a conversa comercial</h2>' +
      '<span class="dir">' + br(d.degraus_total) + " degraus · " + br(d.recomendadas_total) +
      " recomendadas no fim</span></div>" +
      '<div class="degraus">' + (d.degraus || []).map(function (g) {
        return '<div class="dg"><div class="dg-l"><span class="n mono">' + br(g.quantos) + "</span>" +
          '<span class="d"><b>' + esc(g.degrau) + "</b>" +
          (tem(g.o_que_e) ? "<span>" + esc(g.o_que_e) + "</span>" : "") + "</span></div>" +
          (tem(g.cairam)
            ? '<div class="dg-cai"><span class="mono">↓ ' + br(g.cairam) + " caíram</span>" +
              (tem(g.porque_caem) ? "<span>" + esc(g.porque_caem) + "</span>" : "") + "</div>"
            : "") +
          ((g.vieram_da_regua != null || g.vieram_por_outro_caminho != null)
            ? '<div class="dg-vias">' +
              (g.vieram_da_regua != null ? '<span><b class="mono">' + br(g.vieram_da_regua) +
                "</b> vieram da régua demográfica</span>" : "") +
              (g.vieram_por_outro_caminho != null ? '<span><b class="mono">' + br(g.vieram_por_outro_caminho) +
                "</b> por outro caminho</span>" : "") + "</div>"
            : "") + "</div>";
      }).join("") + "</div>" + pe(d.o_que_nao_e) + "</div>";

    html += '<div class="painel-cab" style="margin-top:22px"><h2>As cidades para avançar</h2>' +
      '<span class="dir">' + br(d.cidades_total) + ' estudadas · cada uma com o que pesa a favor e o que pesa contra</span></div>';

    (d.cidades || []).forEach(function (c) {
      html += '<div class="painel"><div class="op-cab">' +
        '<div class="rotulo">' + esc(c.rotulo) + "</div>" +
        '<div class="leitura">' + esc(c.leitura) + "</div></div>" +
        '<div class="fatos" style="margin-bottom:18px">' +
        fato('<span class="num">' + br(c.populacao) + "</span>", "habitantes") +
        fato('<span class="num">' + br(c.alvo_9_15) + "</span>", "de 9 a 15 anos") +
        fato('<span class="num">' + br(c.alvo_30_45) + "</span>", "de 30 a 45 anos") +
        fato('<span class="num">' + br(c.clinicas_fortes) + "</span>", "clínicas fortes") +
        fato('<span class="num">' + br(c.lider_avaliacoes) + "</span>", "avaliações do líder local") +
        "</div>";

      if ((c.por_que || []).length) {
        html += '<div class="in-l l-fato"><span class="k">o que pesa a favor</span><ul class="leve">' +
          c.por_que.map(function (x) { return "<li><span>" + forte(x) + "</span></li>"; }).join("") + "</ul></div>";
      }
      /* risco não é opcional: dossê sem risco é fol[h]eto */
      if ((c.riscos || []).length) {
        html += '<div class="in-l l-nao"><span class="k">riscos</span><ul class="leve">' +
          c.riscos.map(function (x) { return "<li><span>" + forte(x) + "</span></li>"; }).join("") + "</ul></div>";
      }
      if (tem(c.proximo_passo)) html += linhaInsight("próximo passo", c.proximo_passo, "l-acao");
      if (c.conferencia && tem(c.conferencia.motivo)) {
        html += pe("praça livre conferida: " + c.conferencia.motivo);
      }
      html += cartaoInsight(c.insight) + "</div>";
    });

    if ((d.onde_cabem_mais || []).length) {
      html += '<div class="painel"><div class="painel-cab"><h2>Onde a rede já está e ainda cabe mais</h2>' +
        '<span class="dir">' + br(d.onde_cabem_mais_total) + " cidades · expansão dentro da praça</span></div>" +
        '<p class="sub-painel">' + esc(d.o_que_e_onde_cabem_mais) + "</p>" +
        '<div class="tabela-wrap"><table class="grade"><thead><tr><th>Cidade</th><th>Tamanho</th>' +
        '<th class="n">Habitantes</th><th class="n">Unidades hoje</th><th class="n">Comporta</th>' +
        '<th class="n">Folga</th><th>Leitura</th></tr></thead><tbody>' +
        d.onde_cabem_mais.map(function (c) {
          return '<tr><td class="nome">' + esc(c.rotulo) + "</td><td>" + esc(c.faixa) + "</td>" +
            '<td class="n">' + br(c.populacao) + '</td><td class="n">' + br(c.unidades_hoje) + "</td>" +
            '<td class="n">' + br(c.comporta_pela_regua) + '</td><td class="n">+' + br(c.folga) + "</td>" +
            "<td>" + esc(c.leitura) + "</td></tr>";
        }).join("") + "</tbody></table></div></div>";
    }

    /* o funil nacional continua existindo, agora como âncora dentro daqui:
       a régua da própria rede é o que sustenta o degrau das 50 candidatas */
    html += '<div class="painel" id="funil"><div class="painel-cab"><h2>A régua que montou a lista</h2>' +
      '<span class="dir">' + br(fun.candidatas_total) + " candidatas pela régua demográfica</span></div>" +
      '<p class="sub-painel">' + esc(m.score) + "</p>" +
      pe("só entram cidades acima de " + br(m.piso_populacao) + " habitantes — " + esc(m.piso_porque) +
        " · fonte: " + esc(m.fonte));
    if ((m.regua_hab_por_unidade || []).length) {
      html += '<div class="tabela-wrap" style="margin-top:18px"><table class="grade"><thead><tr>' +
        '<th>Tamanho da cidade</th><th class="n">Habitantes por unidade</th>' +
        '<th class="n">Cidades da rede</th></tr></thead><tbody>' +
        m.regua_hab_por_unidade.map(function (f) {
          return '<tr><td class="nome">' + esc(f.faixa) + '</td><td class="n">' + br(f.mediana_hab_por_unidade) +
            '</td><td class="n">' + br(f.cidades_da_rede_na_faixa) + "</td></tr>";
        }).join("") + "</tbody></table></div>";
    }
    html += "</div>";

    if (d.nao_conferidas_total) {
      html += '<div class="sem-delta"><span class="rot-sis">não entram em recomendação</span>' +
        '<div class="nuvem">' + (d.nao_conferidas || []).map(function (x) {
          return "<span>" + esc(x.rotulo || x) + "</span>";
        }).join("") + "</div><p class=\"pq\">" + esc(d.porque_nao_conferidas) + "</p></div>";
    }

    return html + ressalvas("o que este estudo não enxerga", fun.o_que_isso_nao_ve) +
      fecho(d.manchete) + rodapeMetodo("pipeline_expansao") + rodape();
  }

  /* §12.2 · a agenda é uma das seis capacidades e tem cabeçalho próprio: em
     tela cheia ela é a pauta da semana do consultor, não a fila de alertas. */
  function telaAgenda(d) {
    var html = cabecalhoTela("agenda") + comoLer("agenda") +
      '<div class="tira">' +
      tiraCart(br(d.esta_semana_total), "visitas nesta pauta", "var(--cyan)") +
      tiraCart(br(d.na_fila_total), "unidades com ação aberta", "var(--warn)") +
      "</div>";

    html += '<div class="painel"><div class="painel-cab"><h2>Esta semana</h2>' +
      '<span class="dir">na ordem em que a conversa acontece — não é ranking</span></div>' +
      (tem(d.manchete) ? '<p class="manchete-cap">' + esc(d.manchete) + "</p>" : "") +
      ((d.esta_semana || []).length
        ? d.esta_semana.map(linhaAgenda).join("")
        : vazio("nenhuma visita nesta pauta", d.vazio_porque)) +
      (tem(d.frase_ver_todas)
        ? '<div class="filtros" style="margin-top:12px"><button type="button" class="chip" data-ir="fila">' +
          esc(d.frase_ver_todas) + "</button></div>"
        : "") + "</div>";

    return html + fecho(d.conclusao) + rodapeMetodo("agenda") + rodape();
  }

  function telaOportunidade(d) {
    var c = d.concorrencia || {};

    /* A cidade do radar abre com os MESMOS quatro campos de uma praça da
       rede — sobrelinha, título, tese e base. Antes ela abria com vinte
       números e nenhuma manchete, e a diferença saltava na tela. */
    var html = '<button type="button" class="voltar" data-ir="radar">← radar de cidades</button>' +
      telaTopo(tem(d.eyebrow) ? d.eyebrow : "estudo de expansão", d.rotulo,
        tem(d.tese_titulo) ? d.tese_titulo : "Cidade sem OrthoDontic hoje. Nada aqui entra em nenhuma conta da rede.");

    if (tem(d.tese) || tem(d.base)) {
      html += '<div class="painel">' +
        (tem(d.tese) ? '<p class="tese">' + esc(d.tese) + "</p>" : "") +
        (tem(d.base) ? pe("base: " + d.base) : "") + "</div>";
    }

    html += '<div class="painel"><div class="fatos">' +
      fato('<span class="num">' + br(d.populacao) + "</span>", "habitantes") +
      fato('<span class="num">' + br(d.alvo_9_15) + "</span>", "de 9 a 15 anos") +
      fato('<span class="num">' + br(d.alvo_30_45) + "</span>", "de 30 a 45 anos") +
      fato('<span class="num">' + br(d.hab_por_clinica_forte) + "</span>", "hab. por clínica forte") +
      "</div></div>";

    html += '<div class="painel"><div class="painel-cab"><h2>A concorrência da cidade</h2>' +
      '<span class="dir">' + br(c.varridas) + " clínicas encontradas · nota do meio " + dec(c.nota_mediana) + "</span></div>" +
      '<div class="fatos" style="margin-bottom:18px">' +
      fato('<span class="num">' + br(c.fortes) + "</span>", "fortes") +
      fato('<span class="num">' + br(c.medias) + "</span>", "médias") +
      fato('<span class="num">' + br(c.fracas) + "</span>", "fracas") +
      fato('<span class="num">' + br(c.de_rede_nacional) + "</span>", "de rede nacional") +
      "</div>";
    if (c.maiores && c.maiores.length) {
      html += '<div class="tabela-wrap"><table class="grade"><thead><tr><th>Clínica</th>' +
        '<th class="n">Nota</th><th class="n">Avaliações</th></tr></thead><tbody>' +
        c.maiores.map(function (m) {
          return '<tr><td class="nome">' + esc(m.nome) + '</td><td class="n">' + dec(m.nota) +
            '</td><td class="n">' + br(m.avaliacoes) + "</td></tr>";
        }).join("") + "</tbody></table></div>";
    }
    html += "</div>";

    if (d.gemea) {
      var g = d.gemea;
      html += '<div class="painel"><div class="painel-cab"><h2>A cidade mais parecida</h2></div>' +
        '<div class="conclusao"><div class="t">' + esc(g.frase) + "</div>" +
        '<div class="b"><div class="r">a gêmea</div><div class="c">' + esc(g.rotulo) + " · " +
        br(g.distancia) + " km de distância</div></div>" +
        ((g.onde_difere && g.onde_difere.length)
          ? '<div class="b"><div class="r">onde é diferente</div><div class="c">' +
            g.onde_difere.map(esc).join(" · ") + "</div></div>" : "") + "</div></div>";
    }

    if (d.faixa_das_parecidas && d.faixa_das_parecidas.length) {
      html += '<div class="painel"><div class="painel-cab"><h2>O que lojas parecidas entregam hoje</h2>' +
        '<span class="dir">referência de mercado, não promessa</span></div>' +
        '<div class="tabela-wrap"><table class="grade"><thead><tr><th>Loja</th><th>Cidade</th><th>Situação</th>' +
        '<th class="n">Novas/mês</th><th class="n">Meses</th><th class="n">Avaliações</th></tr></thead><tbody>' +
        d.faixa_das_parecidas.map(function (f) {
          return '<tr><td class="nome">' + esc(f.unidade) + "</td><td>" + esc(f.praca) + "</td>" +
            '<td><span class="mono" style="font-size:10.5px">' + esc(f.selo) + "</span></td>" +
            '<td class="n">' + dec(f.ritmo) + '</td><td class="n">' + br(f.meses) + "</td>" +
            '<td class="n">' + br(f.total) + "</td></tr>";
        }).join("") + "</tbody></table></div></div>";
    }

    if (d.conferencia) {
      html += '<div class="painel"><div class="painel-cab"><h2>A conferência</h2></div>' +
        '<p style="margin:0;font-size:15px;color:var(--t2)">' +
        (d.conferencia.livre ? "Cidade livre. " : "Cidade não livre. ") + esc(d.conferencia.motivo) + "</p></div>";
    }

    return html + ressalvas("o que este estudo não enxerga", [
      "Nenhum número vem do sistema interno da rede: é ficha do Google, avaliação de paciente e dado público do IBGE.",
      "A varredura cobre as clínicas encontradas na busca. Consultório sem ficha não entra.",
      "O que lojas parecidas entregam hoje é referência de mercado, não promessa de faturamento."
    ]) + rodape();
  }

  /* ---------- A MARCA ---------- */

  function telaMarca(d) {
    var html = cabecalhoTela("rede_inteira") + comoLer("rede_inteira") +
      '<div class="tira">' +
      tiraCart(br(d.na_lista_oficial), "unidades na lista", "var(--t1)") +
      tiraCart(br(d.confirmadas), "fichas encontradas no Google", "var(--cyan)") +
      tiraCart(dec(d.nota_mediana), "nota do meio da rede", "var(--ok)") +
      tiraCart(br(d.abaixo_de_4), "fichas abaixo de 4,0", "var(--crit)") +
      "</div>" + pe(d.o_que_nao_e);

    /* §12.5 · o alerta de ficha deixou de ser diagnóstico: cada um traz o que
       fazer, o custo e o prazo, e quase todos são sem custo de mídia. */
    if (d.alertas && d.alertas.length) {
      html += '<div class="painel-cab" style="margin-top:22px"><h2>Onde a marca está mal na rua</h2>' +
        '<span class="dir">' + br(d.alertas_total) + " alertas · os marcados como franqueadora não dependem do franqueado</span></div>" +
        '<div class="sinais">' + d.alertas.map(function (a) {
          return '<div class="sinal" style="--sev:' + (COR[a.gravidade] || "var(--warn)") + ';cursor:default">' +
            '<div class="sinal-cab">' + selo(a.gravidade) +
            '<span class="cidade">' + esc(a.uf) + " · " + esc(a.cidade) + "</span>" +
            '<span class="dir">' + esc(a.de_quem_e) + "</span></div>" +
            "<h3>" + esc(a.unidade) + "</h3>" +
            '<div class="fato">' + esc(a.por_que) + "</div>" +
            '<div class="medida"><span class="v">' + dec(a.nota) + "</span>" +
            '<span class="trilha"><i style="width:' + Math.max(2, Math.min(100, (a.nota / 5) * 100)) + '%"></i></span>' +
            '<span class="k">' + br(a.avaliacoes) + " avaliações</span></div>" +
            (tem(a.o_que_fazer)
              ? '<div class="in-l l-acao"><span class="k">ação</span><p>' + esc(a.o_que_fazer) + "</p></div>" +
                '<div class="in-pe">' +
                (tem(a.custo) ? '<b>' + esc(a.custo) + "</b>" : "") +
                (tem(a.prazo_dias) ? '<span class="mono">prazo ' + plural(a.prazo_dias, "dia", "dias") + "</span>" : "") +
                "</div>"
              : "") +
            cartaoInsight(a.insight) +
            '<div class="sinal-pe"><span>na lista: ' + esc(a.situacao_na_lista) +
            "</span><span>no Google: " + esc(a.situacao_google) + "</span></div></div>";
        }).join("") + "</div>";
    }

    var redes = franq.reputacao_das_redes || [];
    if (redes.length) {
      html += '<div class="painel" style="margin-top:22px"><div class="painel-cab"><h2>' +
        esc(card("reputacao").titulo) + "</h2>" +
        '<span class="dir">nota nacional — não tem recorte por cidade</span></div>' +
        '<div class="tabela-wrap"><table class="grade"><thead><tr>' +
        "<th>Rede</th><th>O que vende</th><th>Selo</th>" +
        '<th class="n">Nota</th><th class="n">Reclamações</th><th>Por que está aqui</th></tr></thead><tbody>' +
        redes.map(function (r) {
          return "<tr" + (r.nossa ? ' class="nossa"' : "") + '><td class="nome">' + esc(r.marca) + "</td>" +
            "<td>" + esc(String(r.foco).replace(/_/g, " ")) + "</td><td>" + esc(r.selo) + "</td>" +
            '<td class="n">' + dec(r.nota) + '</td><td class="n">' + br(r.reclamacoes) + "</td>" +
            "<td>" + esc(r.nota_de_classificacao) + "</td></tr>";
        }).join("") + "</tbody></table></div>";
      var fora = franq.reputacao_fora_da_tela || {};
      if (fora.redes && fora.redes.length) {
        html += pe(fora.por_que + " — fora: " + fora.redes.map(function (r) { return r.marca; }).join(" · "));
      }
      html += "</div>";
    }

    html += '<div class="painel"><div class="painel-cab"><h2>' + esc(card("mapa").titulo) + "</h2>" +
      '<span class="dir">' + esc((franq.rede || {}).fonte) + "</span></div>" +
      '<div class="mapa-caixa" id="mapa"></div>' + legendaMapa() + "</div>";

    html += '<div class="painel"><div class="painel-cab"><h2>A rede estado por estado</h2></div>' +
      '<div class="tabela-wrap"><table class="grade"><thead><tr><th>UF</th>' +
      '<th class="n">Unidades</th><th class="n">Nota do meio</th></tr></thead><tbody>' +
      (d.por_uf || []).map(function (u) {
        return '<tr><td class="nome">' + esc(u.uf) + '</td><td class="n">' + br(u.unidades) +
          '</td><td class="n">' + dec(u.nota_mediana) + "</td></tr>";
      }).join("") + "</tbody></table></div>" +
      pe(br(d.nao_confirmadas) + " unidades não foram encontradas no Google — " + d.por_que_nao_confirma) + "</div>";

    return html + rodapeMetodo("rede_inteira") + rodape();
  }

  /* ---------- telas de apoio ---------- */

  function telaMudou(d) {
    var html = cabecalhoTela("o_que_mudou") + comoLer("o_que_mudou");
    Object.keys(d.pracas || {}).forEach(function (k) {
      var p = d.pracas[k];
      html += '<div class="painel"><div class="painel-cab"><h2>' + esc(p.rotulo) + "</h2>" +
        '<span class="dir">' + plural(p.dias_medidos, "dia medido", "dias medidos") + "</span></div>";
      if (tem(p.aviso)) html += '<p class="aviso-curto" style="margin-bottom:12px">' + esc(p.aviso) + "</p>";
      if (p.contador_caiu && p.contador_caiu.length) {
        html += '<div class="rot-sis" style="color:var(--crit)">o contador caiu — avaliação apagada</div>' +
          p.contador_caiu.map(function (x) { return movLinha(x, true); }).join("");
      }
      if (p.nossas && p.nossas.length) {
        html += '<div class="rot-sis" style="margin-top:16px">nossas lojas</div>' +
          p.nossas.map(function (x) { return movLinha(x); }).join("");
      } else {
        html += pe("não há loja da rede nesta cidade — ela é estudo de expansão");
      }
      if (p.quem_mais_ganhou && p.quem_mais_ganhou.length) {
        html += '<div class="rot-sis" style="margin-top:16px">quem mais ganhou avaliações</div>' +
          p.quem_mais_ganhou.map(function (x) { return movLinha(x); }).join("");
      }
      html += "</div>";
    });
    return html + rodapeMetodo("o_que_mudou") + rodape();
  }

  /* §12.4 · fila de trabalho, não acervo: quem precisa responder AGORA vem
     primeiro, com o assunto do que reclamam. O 399 continua na tela — embaixo,
     como acervo. Ninguém responde 399. */
  function telaCaixa(d) {
    var html = cabecalhoTela("caixa_de_respostas") + comoLer("caixa_de_respostas") +
      '<div class="tira">' +
      tiraCart(br(d.precisam_agora_total), "unidades precisam responder agora", "var(--crit)") +
      tiraCart(br(d.janela_que_pesa_dias), "dias da janela que pesa", "var(--warn)") +
      tiraCart(br(d.total_abertas), "abertas no acervo", "var(--t1)") +
      tiraCart(br(d.com_texto), "com o motivo escrito", "var(--cyan)") +
      "</div>" + pe(d.ordem);

    var fila = d.precisam_agora || [];
    html += '<div class="painel"><div class="painel-cab"><h2>Precisam responder agora</h2>' +
      '<span class="dir">' + br(d.precisam_agora_total) + ' unidades · críticas sem resposta na janela que pesa</span></div>';
    if (!fila.length) {
      html += vazio("nenhuma unidade em vermelho nesta rodada", d.ordem);
    }
    fila.forEach(function (u) {
      html += '<details class="pauta" style="--sev:' + (GRAV[u.gravidade] || "var(--warn)") + '"><summary>' +
        '<span class="pa-onde"><b>' + esc(u.rotulo) + "</b><span>" + esc(u.unidade) + "</span></span>" +
        '<span class="pa-viu">' + esc(u.frase) +
        ((u.assuntos || []).length
          ? '<span class="assuntos">' + u.assuntos.map(function (a) {
              return "<span>" + esc(a.assunto) + ' <b class="mono">' + br(a.quantas) + "</b></span>";
            }).join("") + "</span>"
          : "") + "</span>" +
        '<span class="pa-sev mono">' + esc(tem(u.gravidade_rotulo) ? u.gravidade_rotulo : u.gravidade) +
        "</span></summary>" +
        '<div class="pauta-corpo">' +
        comMais(u.itens || [], 6, u.itens_total, avalHTML) +
        cartaoInsight(u.insight) +
        '<div class="filtros"><button type="button" class="chip" data-ir="clinicas/' + esc(u.local_id) +
        '">abrir esta clínica</button></div></div></details>';
    });
    html += "</div>";

    /* o acervo: as 40 unidades com fila, sem promessa de que dá para zerar */
    html += '<div class="painel"><div class="painel-cab"><h2>O acervo inteiro</h2>' +
      '<span class="dir">' + br(d.lojas_com_fila) + " unidades com fila · " +
      br(d.total_abertas) + " avaliações abertas</span></div>" +
      '<p class="sub-painel">' + esc(d.a_regra) + "</p>" +
      '<div class="acervo">' + (d.unidades || []).map(function (u) {
        return '<button type="button" class="ac-l" data-ir="clinicas/' + esc(u.local_id) + '">' +
          '<span class="nm">' + esc(u.rotulo) + " · " + esc(u.unidade) + "</span>" +
          '<span class="par mono">' + br(u.abertas) + " abertas</span>" +
          '<span class="par mono">' + br(u.ja_respondidas) + " respondidas</span></button>";
      }).join("") + "</div>" +
      pe(d.prazo_sugerido + " · quem faz: " + d.dono) + "</div>";

    return html + fecho(d.manchete) + rodapeMetodo("caixa_de_respostas") + rodape();
  }

  function telaConstancia(d) {
    return telaTopo("as lojas acompanhadas", card("constancia").titulo,
      "Manter o ritmo é ter meses seguidos ganhando mais avaliações do que a própria loja costuma ganhar.") +
      '<div class="tira">' +
      tiraCart(br(d.sustentam), "mantêm o ritmo", "var(--ok)") +
      tiraCart(br(d.campanha), "só tiveram picos", "var(--warn)") +
      tiraCart(br(d.paradas), "pararam", "var(--crit)") +
      tiraCart(br(d.unidades), "lojas acompanhadas", "var(--t1)") +
      "</div>" +
      '<div class="painel"><div class="tabela-wrap"><table class="grade"><thead><tr>' +
      "<th>Loja</th><th>Cidade</th>" +
      '<th class="n">Avaliações</th><th class="n">Nota</th><th class="n">Novas/mês</th>' +
      '<th class="n">Meses</th><th class="n">Posição</th></tr></thead><tbody>' +
      (d.placar || []).map(function (p) {
        return '<tr><td class="nome">' + esc(p.nome) + "</td><td>" + esc(p.rotulo) + "</td>" +
          '<td class="n">' + br(p.total) + '</td><td class="n">' + dec(p.nota) + "</td>" +
          '<td class="n">' + dec(p.ritmo) + '</td><td class="n">' + br(p.meses) + "</td>" +
          '<td class="n">' + br(p.posicao) + "º de " + br(p.de) + "</td></tr>";
      }).join("") + "</tbody></table></div></div>" +
      ressalvas("o que pesa contra esta leitura", d.pesa_contra) + rodape();
  }

  function telaRival(d) {
    var html = cabecalhoTela("rival") + comoLer("rival");
    (d.pracas || []).forEach(function (p) {
      html += '<div class="painel"><div class="painel-cab"><h2>' + esc(p.unidade) + "</h2>" +
        '<span class="dir">' + esc(p.rotulo) + "</span></div>";
      if (tem(p.sem_comparacao_porque)) {
        html += vazio("Sem comparação nesta unidade", p.sem_comparacao_porque);
      } else {
        var maxR = (p.vantagens_deles || []).reduce(function (a, v) { return Math.max(a, v.eles || 0); }, 0) || 1;
        html += (p.vantagens_deles || []).map(function (v) {
          return '<div class="barra-tema"><span class="l">' + esc(v.o_que_e) + "</span>" +
            '<span class="trilha"><i style="width:' + (v.eles / maxR * 100) + '%"></i></span>' +
            '<span class="v">' + dec(v.eles) + "%</span></div>" +
            '<div class="mono" style="font-size:11px;color:var(--t3);margin:-2px 0 12px">' +
            esc(v.quem) + " · nós " + dec(v.nos) + "%</div>";
        }).join("");
        if (p.rivais_comparados && p.rivais_comparados.length) {
          html += '<div class="nuvem" style="margin-top:8px">' +
            p.rivais_comparados.map(function (r) { return "<span>" + esc(r) + "</span>"; }).join("") + "</div>";
        }
      }
      if (p.rivais_fora && p.rivais_fora.length) {
        html += '<details class="abre"><summary>fora da comparação — outro produto (' +
          br(p.rivais_fora_total) + ")</summary>" +
          p.rivais_fora.map(function (f) {
            return '<div class="fora-item"><div class="n">' + esc(f.nome) + "</div>" +
              '<div class="p">' + esc(f.por_que_fora) + "</div></div>";
          }).join("") + "</details>";
      }
      html += "</div>";
    });
    return html + rodapeMetodo("rival") + rodape();
  }

  function telaTimeline(d) {
    var html = cabecalhoTela("timeline") + comoLer("timeline");
    (d.lojas || []).forEach(function (L) {
      var cb = L.cabecalho || {};
      html += '<div class="painel"><div class="painel-cab"><h2>' + esc(L.unidade) + "</h2>" + selo(L.faixa) +
        '<span class="dir">' + esc(L.rotulo) + "</span></div>" +
        '<div class="fatos" style="margin-bottom:18px">' +
        fato('<span class="num">' + dec(cb.nota) + "</span>", "nota") +
        fato('<span class="num">' + br(cb.avaliacoes) + "</span>", "avaliações") +
        fato('<span class="num">' + dec(cb.ritmo) + "</span>", "novas por mês") +
        (L.sem_resposta ? fato('<span class="num">' + br(L.sem_resposta.abertas) + "</span>", "sem resposta") : "") +
        "</div>" +
        '<ul class="tempo">' + (L.eventos || []).map(function (e) {
          var sr = String(e.texto || "").indexOf("SEM RESPOSTA") >= 0;
          var tx = sr ? esc(e.texto).replace("SEM RESPOSTA", "<b>SEM RESPOSTA</b>") : esc(e.texto);
          return '<li data-quem="' + esc(e.quem) + '"><div class="qd"><span>' + esc(QUEM[e.quem] || e.quem) +
            "</span><span>" + data(e.data) + "</span></div><div class=\"tx\">" + tx + "</div></li>";
        }).join("") + "</ul>" +
        '<div class="filtros" style="margin-top:14px"><button type="button" class="chip" data-ir="clinicas/' +
        esc(L.local_id) + '">Abrir a página desta clínica</button></div></div>';
    });
    return html + rodapeMetodo("timeline") + rodape();
  }

  /* ---------- ARQUIVO ---------- */

  function telaArquivo(saz) {
    var g = (franq.grupos || []).filter(function (x) { return x.chave === "arquivo"; })[0] || {};
    return telaTopo("de onde vem cada número", g.nome, g.explica) +
      '<div class="cartoes">' + (franq.cards || []).filter(function (c) { return c.grupo === "arquivo"; })
        .map(function (c) {
          if (!c.disponivel) {
            /* Um card pode estar marcado como sem dado e MESMO ASSIM ter a
               resposta pronta em arquivo — foi o caso da sazonalidade, que
               deixou de ser pendência e virou pergunta medida e respondida
               com não. Quando existe rota para ele, o card abre. */
            if (ROTAS[c.tela]) {
              /* o motivo antigo diz que falta dado e a tela diz o contrário —
                 quem manda é a manchete do próprio arquivo da resposta */
              var frase = (c.tela === "sazonalidade" && saz && tem(saz.manchete))
                ? saz.manchete : c.indisponivel_porque;
              return '<button type="button" class="cartao medido" data-ir="' + esc(c.tela) + '">' +
                '<div class="cid">pergunta medida</div>' +
                '<div class="un">' + esc(c.titulo) + "</div>" +
                '<div class="fr">' + esc(frase) + "</div></button>";
            }
            return '<div class="cartao apagado"><div class="cid">sem dado ainda</div>' +
              '<div class="un">' + esc(c.titulo) + "</div>" +
              '<div class="fr">' + esc(c.indisponivel_porque) + "</div></div>";
          }
          return '<button type="button" class="cartao" data-ir="' + esc(c.tela) + '">' +
            '<div class="cid">' + esc(c.pergunta) + "</div>" +
            '<div class="un">' + esc(c.titulo) + "</div>" +
            '<div class="fr">' + esc(c.frase) + "</div></button>";
        }).join("") + "</div>" + rodape();
  }

  function telaVoz(d) {
    var html = '<button type="button" class="voltar" data-ir="arquivo">← arquivo</button>' +
      cabecalhoTela("voz_da_cidade") + comoLer("voz_da_cidade") + pe(d.diferenca + " " + d.sem_identidade);
    (d.pracas || []).forEach(function (p) {
      html += '<div class="painel"><div class="painel-cab"><h2>' + esc(nomeDaPraca(p.praca_id)) + "</h2>" +
        '<span class="dir">' + br(p.comentarios_lidos) + " comentários lidos</span></div>";
      if (tem(p.aviso)) html += '<p class="aviso-curto" style="margin-bottom:12px">' + esc(p.aviso) + "</p>";
      (p.sinais || []).forEach(function (s) {
        html += '<div class="linha"><div style="display:flex;gap:12px;align-items:baseline;font-size:14.5px;font-weight:500">' +
          esc(s.o_que_e) + '<span class="mono" style="margin-left:auto;font-size:11px;color:var(--t3)">' +
          br(s.n) + " menções · " + dec(s.pct) + "%</span></div>" +
          (s.exemplos || []).map(function (x) {
            return '<div style="margin-top:10px;padding-left:14px;border-left:1px solid var(--hair)">' +
              '<div style="font-size:13.5px;line-height:1.6;color:var(--t2)">' + esc(x.texto) + "</div>" +
              '<div class="mono" style="font-size:10.5px;color:var(--t3);margin-top:5px">' +
              br(x.curtidas) + " curtidas · canal " + esc(x.tipo_canal) + "</div></div>";
          }).join("") + "</div>";
      });
      html += "</div>";
    });
    return html + fecho(d.manchete) + rodapeMetodo("voz_da_cidade") + rodape();
  }

  function telaBusca() {
    var b = franq.presenca_na_busca || {};
    return '<button type="button" class="voltar" data-ir="arquivo">← arquivo</button>' +
      telaTopo("arquivo", card("busca").titulo, card("busca").pergunta) +
      '<div class="tira">' + Object.keys(b).map(function (k) {
        var f = b[k];
        return '<div class="tira-cart"><div class="v" style="color:var(--cyan)">' + br(f.dentro) +
          '<span style="font-size:20px;color:var(--t3)"> / ' + br(f.dentro + f.fora) + "</span></div>" +
          '<div class="k">' + esc(k) + " — " + br(f.fora) + " frases sem a rede no mapa</div>" +
          '<div class="barra-tema" style="margin-top:12px"><span class="trilha"><i style="width:' +
          (f.dentro / (f.dentro + f.fora) * 100) + '%"></i></span></div></div>';
      }).join("") + "</div>" +
      pe("a conta de dentro e de fora vem pronta do arquivo · a lista de frases de cada cidade está em 'como a cidade procura'") +
      rodape();
  }

  function telaFichas() {
    var f = franq.fichas_da_rede || {};
    var cat = f.por_categoria || {};
    return '<button type="button" class="voltar" data-ir="arquivo">← arquivo</button>' +
      telaTopo("arquivo", card("fichas").titulo, "A categoria da ficha decide em que busca ela entra.") +
      '<div class="tira">' +
      tiraCart(br(f.conferidas), "fichas conferidas", "var(--cyan)") +
      tiraCart(br(f.sem_site), "sem site na ficha", "var(--warn)") +
      "</div>" +
      '<div class="painel"><div class="painel-cab"><h2>Como cada ficha está cadastrada</h2></div>' +
      '<div class="tabela-wrap"><table class="grade"><thead><tr><th>Categoria no Google</th>' +
      '<th class="n">Fichas</th></tr></thead><tbody>' +
      Object.keys(cat).map(function (k) {
        return '<tr><td class="nome">' + esc(k) + '</td><td class="n">' + br(cat[k]) + "</td></tr>";
      }).join("") + "</tbody></table></div>" +
      pe("cobre as " + br(f.conferidas) + " unidades acompanhadas — as demais estão em 'a marca'") + "</div>" + rodape();
  }

  function telaTerritorio(d) {
    var t = d.territorio_vazio || {};
    return '<button type="button" class="voltar" data-ir="arquivo">← arquivo</button>' +
      telaTopo("arquivo", card("territorio").titulo, card("territorio").frase) +
      '<div class="painel">' + Object.keys(t).map(function (k) {
        var lista = t[k] || [];
        return '<div class="linha"><div class="rot-sis" style="margin-bottom:10px">' + esc(k.replace(/_/g, " ")) + "</div>" +
          '<div class="nuvem">' + lista.map(function (p) {
            return "<span>" + esc(nomeDaPraca(p)) + "</span>";
          }).join("") + "</div></div>";
      }).join("") +
      pe("canal vazio não é oportunidade automática: ele pode estar vazio porque não funciona ali") + "</div>" + rodape();
  }

  var DEGRAUS = [
    ["constante", "Vale para toda a rede"],
    ["doutrina", "Já virou regra"],
    ["candidata", "Se repete, falta confirmar"],
    ["hipotese", "Sinal isolado"],
    ["derrubada", "Caiu no teste"]
  ];

  function telaAchados(d) {
    var html = '<button type="button" class="voltar" data-ir="arquivo">← arquivo</button>' +
      telaTopo("arquivo", card("achados").titulo, card("achados").frase) + pe(d.nota_teto);
    DEGRAUS.forEach(function (g) {
      var meus = (d.achados || []).filter(function (a) { return a.estado === g[0]; });
      if (!meus.length) return;
      html += '<div class="painel"><div class="painel-cab"><h2>' + esc(g[1]) + "</h2></div>" +
        meus.map(function (a) {
          return '<div class="linha"><div style="display:flex;gap:12px;align-items:baseline;flex-wrap:wrap">' +
            '<span style="font-size:15.5px;font-weight:500;line-height:1.4">' + esc(a.t) + "</span>" +
            '<span class="mono" style="margin-left:auto;font-size:11px;color:var(--t3)">' + esc(a.n) + "</span></div>" +
            (tem(a.leitura) ? '<div style="margin-top:7px;font-size:13.5px;line-height:1.6;color:var(--t2)">' + esc(a.leitura) + "</div>" : "") +
            (tem(a.ref) ? '<button type="button" class="chip" style="margin-top:10px" data-ev="' + esc(a.ref) + '">Ver evidência</button>' : "") +
            "</div>";
        }).join("") + "</div>";
    });
    return html + rodape();
  }

  /* A sazonalidade não é ferramenta pendente: é pergunta MEDIDA e respondida
     com NÃO. A tela conta o resultado, não fica cinza com "em breve". */
  function telaSazonalidade(d) {
    var html = '<button type="button" class="voltar" data-ir="arquivo">← arquivo</button>' +
      cabecalhoTela("sazonalidade") + comoLer("sazonalidade") +
      '<div class="painel grave"><p class="frase-topo alerta">' + esc(d.manchete) + "</p>" +
      '<div class="fatos">' +
      fato('<span class="num">' + br(d.regioes_medidas) + "</span>", "estados medidos") +
      fato('<span class="num" style="color:var(--crit)">' + br(d.regioes_publicaveis) + "</span>", "com curva publicável") +
      fato('<span class="num" style="font-size:22px">' + esc(d.janela) + "</span>", "janela medida") +
      "</div>" +
      pe("termo: " + d.termo + " · medido em " + data(d.medido_em)) + "</div>";

    html += '<div class="painel"><div class="painel-cab"><h2>Por que não dá para responder por cidade</h2></div>' +
      '<p style="margin:0;font-size:14.5px;line-height:1.7;color:var(--t2)">' + esc(d.por_que_nao_e_por_cidade) + "</p></div>";

    var tv = d.as_duas_travas || {};
    html += '<div class="painel"><div class="painel-cab"><h2>As duas travas que uma curva precisa passar</h2></div>' +
      '<div class="loja-cidade">' +
      '<div><div class="rot mono">volume</div><ul><li>' + esc(tv.volume) + "</li></ul></div>" +
      '<div><div class="rot mono">estabilidade</div><ul><li>' + esc(tv.estabilidade) + "</li></ul></div>" +
      "</div></div>";

    html += '<div class="painel"><div class="painel-cab"><h2>Estado por estado</h2>' +
      '<span class="dir">nenhum passou</span></div>' +
      '<div class="tabela-wrap"><table class="grade"><thead><tr><th>UF</th>' +
      '<th class="n">Semanas com busca</th><th class="n">de</th><th>Pico por ano</th>' +
      '<th class="n">Repete em</th><th>Por que não passou</th></tr></thead><tbody>' +
      (d.veredito || []).map(function (v) {
        var anos = Object.keys(v.anos || {});
        return '<tr><td class="nome">' + esc(v.regiao) + "</td>" +
          '<td class="n">' + br(v.semanas_com_busca) + '</td><td class="n">' + br(v.semanas) + "</td>" +
          "<td>" + (anos.length
            ? anos.map(function (a) { return esc(a.slice(2)) + "/" + esc(v.anos[a]); }).join(" · ")
            : '<span style="color:var(--t3)">sem busca no período</span>') + "</td>" +
          '<td class="n">' + (v.anos_medidos ? br(v.pico_repete_em) + " de " + br(v.anos_medidos) : "—") + "</td>" +
          '<td><span class="selo selo-' + (v.porque === "sem_volume" ? "parada" : "campanha") + '">' +
          esc(String(v.porque).replace(/_/g, " ")) + "</span></td></tr>";
      }).join("") + "</tbody></table></div></div>";

    return html + fecho(d.conclusao) + rodapeMetodo("sazonalidade") + rodape();
  }

  function telaPlanos() {
    return '<button type="button" class="voltar" data-ir="arquivo">← arquivo</button>' +
      telaTopo("arquivo", card("planos").titulo, card("planos").frase) +
      '<div class="cartoes">' + ((manifest.arquivos || {}).planos || []).map(function (id) {
        var L = loja(id);
        return '<button type="button" class="cartao" data-ir="planos/' + esc(id) + '">' +
          '<div class="cid">' + esc(L ? L.rotulo : "plano do franqueado") + "</div>" +
          '<div class="un">' + esc(L ? L.unidade : "plano do franqueado") + "</div></button>";
      }).join("") + "</div>" + rodape();
  }

  function telaPlano(d) {
    var html = '<button type="button" class="voltar" data-ir="' +
      (tem(d.local_id) ? "clinicas/" + esc(d.local_id) : "planos") + '">← ' +
      (tem(d.local_id) ? "a clínica" : "todos os planos") + "</button>" +
      telaTopo("plano do franqueado", tem(d.unidade) ? d.unidade : d.rotulo, null) +
      (tem(d.frase_do_topo) ? '<p class="frase-topo">' + forte(d.frase_do_topo) + "</p>" : "") +
      '<div class="tira">' +
      tiraCart(br(d.placar && d.placar.aparece_em), "aparições de " + br(d.placar && d.placar.de) + " frases medidas", "var(--cyan)") +
      tiraCart(dec(d.placar && d.placar.pct) + "%", "das buscas da cidade", "var(--t1)") +
      tiraCart(br(d.gratis), "tarefas sem custo", "var(--ok)") +
      "</div>";

    /* o que é medida DESTA loja e o que é leitura da cidade — a confusão
       entre os dois foi o que disse "a sua clínica aparece em N buscas"
       justamente para a loja que não aparece em nenhuma */
    if ((d.o_que_e_da_loja || []).length || (d.o_que_e_da_cidade || []).length) {
      html += '<div class="painel"><div class="painel-cab"><h2>O que é desta loja e o que é da cidade</h2></div>' +
        '<div class="loja-cidade">' +
        '<div><div class="rot mono">desta loja</div><ul>' +
        (d.o_que_e_da_loja || []).map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul></div>" +
        '<div><div class="rot mono">da cidade — vale para as outras lojas daqui</div><ul>' +
        (d.o_que_e_da_cidade || []).map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul></div>" +
        "</div></div>";
    }
    (d.tarefas || []).forEach(function (t, i) {
      html += '<div class="tarefa-cx"><div class="n">' + (i + 1) + "</div><div>" +
        "<h3>" + esc(t.titulo) + "</h3>" +
        '<div class="etiquetas"><span class="etiqueta' + (/sem custo/i.test(t.custo) ? " gratis" : "") + '">' +
        esc(t.custo) + '</span><span class="etiqueta">' + esc(t.tempo) + '</span><span class="etiqueta">' +
        esc(t.quem) + "</span></div>";
      (t.o_que_esta_acontecendo || []).forEach(function (x) {
        html += '<p style="margin:0 0 11px;font-size:14.5px;line-height:1.65;color:var(--t2)">' + forte(x) + "</p>";
      });
      if (t.o_que_fazer && t.o_que_fazer.length) {
        html += '<ol class="passos">' + t.o_que_fazer.map(function (x) { return "<li>" + forte(x) + "</li>"; }).join("") + "</ol>";
      }
      if (tem(t.nao_faca)) html += '<div class="nao-faca"><div class="rot">não faça</div><p>' + esc(t.nao_faca) + "</p></div>";
      if (tem(t.como_saber)) html += pe("como saber que funcionou: " + t.como_saber);
      html += "</div></div>";
    });
    return html + ressalvas("ressalvas deste plano", d.ressalvas) + rodape();
  }

  function telaCaptacao(d) {
    var html = '<button type="button" class="voltar" data-ir="pracas/' + esc(d.praca_id) + '">← a praça</button>' +
      telaTopo("como a cidade procura", d.rotulo,
        br(d.portas_medidas) + " frases medidas de " + br(d.portas_total) + " que a cidade digita.") +
      '<div class="tira">' +
      tiraCart(br(d.dentro_total), "frases em que aparecemos", "var(--ok)") +
      tiraCart(br(d.fora_total), "frases em que não aparecemos", "var(--crit)") +
      tiraCart(br(d.sem_dono_total), "frases sem dono claro", "var(--warn)") +
      "</div>";

    [["fora", "As frases em que a rede não aparece", "fora_total"],
     ["sem_dono", "As frases sem dono", "sem_dono_total"],
     ["dentro", "As frases em que a rede aparece", "dentro_total"]].forEach(function (g) {
      var lista = d[g[0]] || [];
      if (!lista.length) return;
      var molde = function (f) {
        var m = f.mapa || {};
        return '<div class="linha" style="display:flex;gap:14px;align-items:baseline;flex-wrap:wrap">' +
          '<span style="flex:1 1 220px;font-size:14px;font-weight:500">' + esc(f.frase) + "</span>" +
          '<span class="mono" style="font-size:11px;color:var(--t3)">' + esc(f.intencao) + "</span>" +
          '<span class="mono" style="font-size:12px">' +
          (tem(m.nossa_posicao) ? br(m.nossa_posicao) + "º" : "não aparece") + "</span></div>";
      };
      html += '<div class="painel"><div class="painel-cab"><h2>' + esc(g[1]) + "</h2>" +
        '<span class="dir">' + br(d[g[2]]) + "</span></div>" +
        comMais(lista, 12, d[g[2]], molde) + "</div>";
    });
    return html + rodape();
  }

  function telaEvidencias(d) {
    var html = '<button type="button" class="voltar" data-ir="arquivo">← arquivo</button>' +
      telaTopo("arquivo", card("evidencias").titulo, card("evidencias").frase) + '<div class="sinais">';
    Object.keys(d).forEach(function (k) {
      var e = d[k];
      html += '<div class="sinal" id="ev-' + esc(k) + '" style="cursor:default">' +
        '<div class="sinal-cab"><span class="cidade">' + esc(e.fonte) + "</span>" +
        '<span class="dir num" style="font-size:17px;color:var(--cyan)">' + esc(e.valor) + "</span></div>" +
        "<h3>" + esc(e.titulo) + "</h3>" +
        '<div class="fato">' + esc(e.legenda) + "</div>" +
        '<dl class="ficha-ev"><dt>amostra</dt><dd>' + esc(e.n) + "</dd>" +
        "<dt>data</dt><dd>" + esc(e.corte) + "</dd>" +
        "<dt>filtro</dt><dd>" + esc(e.filtro) + "</dd>" +
        "<dt>confiança</dt><dd>" + esc(e.conf) + "</dd></dl>" +
        (tem(e.contra) ? '<div class="fazer"><div class="rot">a prova contrária</div><p>' + esc(e.contra) + "</p></div>" : "") +
        "</div>";
    });
    return html + "</div>" + rodape();
  }

  function telaCorretor(d) {
    var html = '<button type="button" class="voltar" data-ir="arquivo">← arquivo</button>' +
      telaTopo("arquivo", "A peça de anúncio conferida", d.peca_exemplo) + '<div class="painel">';
    (d.vereditos || []).forEach(function (v) {
      html += '<div class="linha"><div style="display:flex;gap:12px;align-items:baseline;flex-wrap:wrap">' +
        '<span class="selo" style="--sev:' + (v.v === "risco" ? "var(--crit)" : "var(--ok)") + '">' + esc(v.v) + "</span>" +
        '<span style="font-size:15px">' + esc(nomeDaPraca(v.praca_id)) + "</span></div>" +
        '<div style="margin-top:8px;font-size:14px;color:var(--t2)">' + esc(v.t) + "</div>" +
        pe("sugestão: " + v.sug) + "</div>";
    });
    return html + "</div>" + rodape();
  }

  /* ---------- §10.3 · O QUE A REDE ENSINA ---------- */

  var NIV = {
    confirmado: "var(--ok)", ganhando_forca: "var(--warn)",
    em_teste: "var(--t3)", derrubado: "var(--crit)"
  };

  function telaAprende(d) {
    var html = cabecalhoTela("rede_aprende") + comoLer("rede_aprende") +
      '<div class="tira">' + (d.niveis || []).map(function (n) {
        return tiraCart(br(n.quantos), n.titulo,
          n.chave === "confirmado" ? "ok" : (n.chave === "ganhando_forca" ? "warn" : (n.chave === "derrubado" ? "crit" : null)));
      }).join("") + "</div>";

    /* o nível derrubado é o que dá crédito aos outros três: mesmo peso, mesma
       posição na página, nada escondido no fim */
    (d.niveis || []).forEach(function (n) {
      var itens = (d.descobertas || []).filter(function (x) { return x.nivel === n.chave; });
      html += '<div class="painel nivel" style="--sev:' + (NIV[n.chave] || "var(--t3)") + '">' +
        '<div class="painel-cab"><h2><span class="b-n mono">' + br(n.quantos) + "</span>" + esc(n.titulo) + "</h2>" +
        '<span class="dir">' + esc(n.frase) + "</span></div>" +
        '<p class="sub-painel">' + esc(n.o_que_e) + "</p>";

      if (!itens.length) {
        html += vazio("nenhuma descoberta neste nível", (d.como_o_nivel_e_calculado || {})[n.chave]);
      }
      itens.forEach(function (x) {
        html += '<details class="desc"><summary>' +
          '<span class="pl mono">' + esc(x.placar) + "</span>" +
          '<span class="tt">' + esc(x.titulo) + "</span>" +
          '<span class="pn">' + esc(x.porque_neste_nivel) + "</span></summary>" +
          '<div class="desc-corpo">' +
          (tem(x.como_se_mede) ? linhaInsight("como se mede", x.como_se_mede, "l-fato") : "") +
          (tem(x.leitura) ? linhaInsight("leitura", x.leitura, "l-fato") : "") +
          (tem(x.derrubada_por) ? linhaInsight("derrubada por", x.derrubada_por, "l-nao") : "") +
          (tem(x.o_que_significa) ? linhaInsight("o que significa", x.o_que_significa, "l-pq") : "") +
          (tem(x.decisao_sugerida)
            ? linhaInsight("decisão sugerida", x.decisao_sugerida, "l-acao") +
              (tem(x.dono_da_decisao) ? '<div class="in-pe"><span class="k">de quem é a decisão</span><b>' +
                esc(x.dono_da_decisao) + "</b></div>" : "")
            : "");

        if ((x.evidencias || []).length) {
          html += '<details class="in-ev"><summary>ver ' +
            plural(x.evidencias_total, "evidência", "evidências") + "</summary><ul>" +
            x.evidencias.map(function (e) {
              return '<li><span class="k mono">' + esc(e.onde) + "</span><span>" + esc(e.valor) + "</span></li>";
            }).join("") + "</ul></details>";
        }
        if ((x.excecoes || []).length) {
          html += '<div class="in-l l-nao"><span class="k">exceções</span><p>' +
            x.excecoes.map(function (e) { return esc(tem(e.onde) ? e.onde + ": " + e.valor : e); }).join(" · ") + "</p></div>";
        }
        /* o placar é fato, a decisão é recomendação: dois carimbos, nunca a
           mesma cor */
        html += carimbo(x.carimbo) + carimbo(x.carimbo_da_decisao) + "</div></details>";
      });
      html += "</div>";
    });

    return html + pe(d.nota_do_reteste) + fecho(d.manchete) +
      rodapeMetodo("rede_aprende") + rodape();
  }

  /* ---------- §10.5 · PLAYBOOK COMPETITIVO ---------- */

  function telaPlaybook(d) {
    var html = cabecalhoTela("playbook") + comoLer("playbook");
    var q = d.quem_e_vencedor || {};

    html += '<div class="tira">' +
      tiraCart(br(q.vencedores), "concorrentes que avançam", "ok") +
      tiraCart(br(q.resto), "que não avançam", null) +
      tiraCart(br(d.pracas_com_anuncio), "praças com anúncio medido", "cyan") + "</div>";

    /* §10.5 · quando não há base, o funil É o conteúdo — não é erro */
    if (!d.base_suficiente) {
      html += '<div class="painel"><div class="painel-cab"><h2>Ainda não dá para comparar</h2>' +
        '<span class="dir">' + esc(q.regra) + "</span></div>" +
        '<p class="sub-painel">' + esc(d.porque_sem_comparacao) + "</p>" +
        '<div class="funil">' + (d.funil_ate_a_comparacao || []).map(function (f) {
          return '<div class="fn"><span class="n mono">' + br(f.quantos) + "</span>" +
            '<span class="d">' + esc(f.degrau) + "</span></div>";
        }).join("") + "</div>" +
        pe("o que aumentaria a base: " + d.o_que_aumentaria_a_base) + "</div>";
    }

    [["o_que_os_vencedores_fazem", "O que os que avançam fazem", "l-acao"],
     ["testamos_e_nao_explicou", "Testamos e não explicou nada", "l-nao"]].forEach(function (g) {
      var lista = d[g[0]] || [];
      html += '<div class="painel"><div class="painel-cab"><h2>' + esc(g[1]) + "</h2>" +
        '<span class="dir">' + br(d[g[0] + "_total"]) + "</span></div>";
      if (!lista.length) {
        html += vazio("sem base para esta metade", d.porque_sem_comparacao);
      }
      lista.forEach(function (x) {
        html += '<div class="linha"><div class="in-cab"><span class="onde mono">' + esc(x.eixo) + "</span></div>" +
          (tem(x.frase) ? '<p class="manchete-cap">' + forte(x.frase) + "</p>" : "") +
          (tem(x.o_que_e) ? linhaInsight("o que é", x.o_que_e, "l-fato") : "") +
          (tem(x.o_que_significa) ? linhaInsight("o que significa", x.o_que_significa, "l-pq") : "") +
          carimbo(x.carimbo) + "</div>";
      });
      html += "</div>";
    });

    html += '<div class="painel"><div class="painel-cab"><h2>O que o mercado anuncia</h2>' +
      '<span class="dir">' + br(d.o_que_o_mercado_anuncia_total) + " eixos medidos em " +
      br(d.pracas_com_anuncio) + " praças</span></div>";
    (d.o_que_o_mercado_anuncia || []).forEach(function (x) {
      html += '<div class="eixo"><div class="ex-cab"><span class="nm">' + esc(x.eixo) + "</span>" +
        '<span class="fr mono">' + esc(x.frase) + "</span></div>" +
        '<span class="barra"><i style="width:' + Math.round((x.pracas / (d.pracas_com_anuncio || 1)) * 100) + '%"></i></span>' +
        (tem(x.o_que_significa) ? '<p class="pq">' + esc(x.o_que_significa) + "</p>" : "") + "</div>";
    });
    html += "</div>";

    if ((d.posicoes_vagas || []).length) {
      html += '<div class="painel"><div class="painel-cab"><h2>Posições que ninguém ocupa</h2>' +
        '<span class="dir">espaço de discurso, medido nos anúncios da praça</span></div>' +
        '<div class="nuvem">' + d.posicoes_vagas.map(function (p) {
          return "<span>" + esc(p.posicao) + ' <b class="mono">' + br(p.pracas) + "</b></span>";
        }).join("") + "</div></div>";
    }

    return html + fecho(d.manchete) + rodapeMetodo("playbook") + rodape();
  }

  /* ---------- §10.4 · ANOMALIAS ---------- */

  function linhaAnomalia(a, tom) {
    return '<details class="anom" style="--sev:' + tom + '"><summary>' +
      '<span class="pa-onde"><b>' + esc(a.rotulo) + "</b><span>" + esc(a.unidade) + "</span></span>" +
      '<span class="pa-viu">' + esc(a.leitura) + "</span>" +
      '<span class="pa-sev mono">' + dec(a.razao) + "×</span></summary>" +
      '<div class="pauta-corpo">' +
      linhaInsight("o que perguntar", a.o_que_perguntar, "l-perg") +
      ((a.diferencas_visiveis || []).length
        ? '<div class="in-l l-fato"><span class="k">o que as separa</span><ul class="leve">' +
          a.diferencas_visiveis.map(function (x) {
            return '<li><span class="k mono">' + esc(x.o_que) + "</span><span>" + esc(x.texto) + "</span></li>";
          }).join("") + "</ul></div>"
        : "") +
      ((a.gemeos || []).length
        ? '<div class="in-l l-pq"><span class="k">comparada com</span><p>' +
          a.gemeos.map(function (g) { return esc(g.rotulo + " · " + g.unidade); }).join(" · ") + "</p></div>"
        : "") +
      carimbo(a.carimbo) +
      '<div class="filtros"><button type="button" class="chip" data-ir="clinicas/' + esc(a.local_id) +
      '">abrir esta clínica</button></div></div></details>';
  }

  function telaAnomalias(d) {
    var html = cabecalhoTela("anomalias") + comoLer("anomalias") +
      '<div class="tira">' +
      tiraCart(br(d.anomalias_negativas_total), "deveriam estar melhor", "crit") +
      tiraCart(br(d.fora_da_curva_total), "fora da curva para cima", "ok") + "</div>";

    html += '<div class="painel"><div class="painel-cab"><h2>Deveriam estar melhor</h2>' +
      '<span class="dir">' + esc(d.contra_o_que_compara) + "</span></div>" +
      ((d.anomalias_negativas || []).length
        ? d.anomalias_negativas.map(function (a) { return linhaAnomalia(a, "var(--crit)"); }).join("")
        : vazio("nenhuma unidade muito abaixo dos semelhantes", d.o_que_nao_e)) + "</div>";

    /* a lista mais valiosa é a de cima: boa prática escondida na rede */
    html += '<div class="painel"><div class="painel-cab"><h2>Fora da curva para cima</h2>' +
      '<span class="dir">estão fazendo algo que a rede precisa entender</span></div>' +
      ((d.fora_da_curva || []).length
        ? d.fora_da_curva.map(function (a) { return linhaAnomalia(a, "var(--ok)"); }).join("")
        : vazio("nenhuma unidade muito acima dos semelhantes", d.o_que_nao_e)) + "</div>";

    if ((d.sem_base_de_comparacao || []).length) {
      html += '<div class="sem-delta"><span class="rot-sis">ainda não dá para comparar</span>' +
        '<div class="nuvem">' + d.sem_base_de_comparacao.map(function (x) {
          return "<span>" + esc(x.rotulo + " · " + x.unidade) + "</span>";
        }).join("") + "</div>" +
        '<p class="pq">' + esc((d.cortes || {}).minimo_de_gemeos ? "menos de " +
          d.cortes.minimo_de_gemeos + " unidades semelhantes com medição comparável" : d.o_que_nao_e) + "</p></div>";
    }

    return html + fecho(d.manchete) + rodapeMetodo("anomalias") + rodape();
  }

  /* ---------- roteador ---------- */

  var ROTAS = {
    "": function () { return inicio(); },
    inicio: function () { return inicio(); },
    fila: function () { return carregar("fila").then(telaFila); },
    clinicas: function () {
      return Promise.all([carregar("clinicas_indice"), carregar("fila")]).then(function (r) {
        indiceClinicas = r[0];
        return telaClinicas(r);
      });
    },
    pracas: function () { return Promise.resolve(telaPracas()); },
    ensina: function () { return carregar("rede_aprende").then(telaAprende); },
    rede_aprende: function () { return carregar("rede_aprende").then(telaAprende); },
    agenda: function () { return carregar("agenda").then(telaAgenda); },
    playbook: function () { return carregar("playbook").then(telaPlaybook); },
    anomalias: function () { return carregar("anomalias").then(telaAnomalias); },
    padroes: function () { return Promise.all([carregar("padroes"), carregar("rival")]).then(telaEnsina); },
    radar: function () {
      return Promise.all([carregar("pipeline_expansao"), carregar("funil_nacional")]).then(telaPipeline);
    },
    pipeline_expansao: function () {
      return Promise.all([carregar("pipeline_expansao"), carregar("funil_nacional")]).then(telaPipeline);
    },
    funil: function () {
      return Promise.all([carregar("pipeline_expansao"), carregar("funil_nacional")]).then(telaPipeline);
    },
    radar_antigo: function () { return Promise.all([carregar("radar"), carregar("funil_nacional")]).then(telaRadar); },
    marca: function () { return carregar("rede_inteira").then(telaMarca); },
    rede_inteira: function () { return carregar("rede_inteira").then(telaMarca); },
    reputacao: function () { return carregar("rede_inteira").then(telaMarca); },
    mapa: function () { return carregar("rede_inteira").then(telaMarca); },
    arquivo: function () {
      return carregar("sazonalidade").then(telaArquivo, function () { return telaArquivo(null); });
    },
    mudou: function () { return carregar("o_que_mudou").then(telaMudou); },
    perto: function () { return carregar("perto_da_loja").then(telaPerto); },
    caixa: function () { return carregar("caixa_de_respostas").then(telaCaixa); },
    constancia: function () { return carregar("rede_cruzamento").then(telaConstancia); },
    territorio: function () { return carregar("rede_cruzamento").then(telaTerritorio); },
    rival: function () { return carregar("rival").then(telaRival); },
    timeline: function () { return carregar("timeline").then(telaTimeline); },
    voz_da_cidade: function () { return carregar("voz_da_cidade").then(telaVoz); },
    busca: function () { return Promise.resolve(telaBusca()); },
    fichas: function () { return Promise.resolve(telaFichas()); },
    achados: function () { return carregar("achados").then(telaAchados); },
    sazonalidade: function () { return carregar("sazonalidade").then(telaSazonalidade); },
    planos: function () { return Promise.resolve(telaPlanos()); },
    evidencias: function () { return carregar("evidencias").then(telaEvidencias); },
    corretor: function () { return carregar("corretor").then(telaCorretor); }
  };

  /* a home precisa das três fontes do cruzamento; se uma faltar, a tela abre
     com o que existe em vez de morrer inteira */
  function inicio() {
    return Promise.all([
      carregar("fila"),
      carregar("inteligencia_da_rede").catch(function () { return {}; }),
      carregar("agenda").catch(function () { return {}; })
    ]).then(telaInicio);
  }

  function resolver(rota) {
    if (ROTAS[rota]) return ROTAS[rota]();
    var p = rota.split("/");
    if (p.length === 2) {
      if (p[0] === "clinicas") {
        return Promise.all([carregar("clinicas/" + p[1]),
          carregar("gemeos").catch(function () { return {}; })]).then(function (r) {
          gemeosDaRede = r[1] || {};
          return telaClinica(r[0]);
        });
      }
      if (p[0] === "pracas") return carregar("pracas/" + p[1]).then(telaPraca);
      if (p[0] === "planos") return carregar("planos/" + p[1]).then(telaPlano);
      if (p[0] === "captacao") return carregar("captacao/" + p[1]).then(telaCaptacao);
      if (p[0] === "oportunidade") return carregar("oportunidade/" + p[1]).then(telaOportunidade);
    }
    /* rota que não casa volta ao Painel: a moldura sozinha não diz nada,
       e o Painel é a única tela que responde sem precisar de contexto */
    location.replace("#/");
    return ROTAS[""]();
  }

  function irPara(r) { location.hash = r ? "#/" + r : "#/"; }

  function pintar() {
    var rota = location.hash.replace(/^#\/?/, "");
    var app = el("app");
    app.setAttribute("aria-busy", "true");
    app.innerHTML = '<p class="carregando">carregando…</p>';

    carregar("fila").then(function (f) { pintarRail(rota, f); }).catch(function () { pintarRail(rota, null); });

    resolver(rota).then(function (html) {
      app.innerHTML = '<div class="dentro">' + html + "</div>";
      /* a entrada é escalonada nos primeiros blocos da tela; @starting-style
         só dispara em elemento recém-inserido, que é exatamente o caso */
      var dentro = app.firstChild;
      if (dentro) {
        Array.prototype.slice.call(dentro.children, 0, 6).forEach(function (n) {
          n.classList.add("entra");
        });
      }
      app.setAttribute("aria-busy", "false");
      window.scrollTo(0, 0);
      var alvo = el("mapa");
      if (alvo) desenharMapa(alvo, franq.mapa);
      if (el("cl-grade")) ligarGrade();
    }).catch(function (e) {
      /* falha de dado NÃO vira redirecionamento silencioso: uma publicação
         incompleta ficaria parecendo saudável. Mas ninguém fica sem saída. */
      app.innerHTML = '<div class="dentro">' +
        telaTopo("", "Esta tela não abriu", String(e.message || e)) +
        '<div class="filtros" style="margin-top:22px">' +
        '<button type="button" class="chip" data-ir="">Voltar à Inteligência da rede</button></div></div>';
      app.setAttribute("aria-busy", "false");
    });
  }

  /* ---------- busca global ---------- */

  var indice = [], jaTem = {};

  function aoIndice(rot, tp, ir) {
    if (!tem(rot)) return;
    var k = chave(rot);
    if (jaTem[k]) return;
    jaTem[k] = true;
    indice.push({ rot: rot, tp: tp, ir: ir });
  }

  function montarIndice(fila) {
    SECOES.forEach(function (s) { aoIndice(s.rot, "seção", s.id); });
    /* as capacidades novas não têm item de menu (continuam sete) — mas precisam
       ser alcançáveis pelo nome, que é o que a busca serve */
    [["A fila inteira · unidades com ação aberta", "fila"],
     ["Playbook competitivo", "playbook"],
     ["Quem está longe dos semelhantes", "anomalias"]].forEach(function (x) {
      aoIndice(x[0], "ferramenta", x[1]);
    });
    (fila.fila || []).forEach(function (c) {
      aoIndice(c.unidade + " — " + c.rotulo, "clínica", "clinicas/" + c.local_id);
      /* o plano é da loja: apontar para o de praça abriria o arquivo aposentado,
         com o rótulo somado que a coleta nova desfez */
      aoIndice(c.unidade + " · plano", "plano", "planos/" + c.local_id);
      if (c.quem_avanca) aoIndice(c.quem_avanca.nome, "concorrente", "clinicas/" + c.local_id);
    });
    (manifest.pracas || []).forEach(function (p) {
      aoIndice(p.rotulo, "praça", "pracas/" + p.praca_id);
      aoIndice(p.rotulo + " · como a cidade procura", "busca", "captacao/" + p.praca_id);
    });
    ((manifest.arquivos || {}).oportunidade || []).forEach(function (id) {
      aoIndice(nomeDaPraca(id), "estudo", "oportunidade/" + id);
    });
    (franq.cards || []).forEach(function (c) { if (c.disponivel) aoIndice(c.titulo, "tela", c.tela); });
    carregar("rival").then(function (d) {
      (d.pracas || []).forEach(function (p) {
        (p.rivais_comparados || []).forEach(function (r) { aoIndice(r, "concorrente", "rival"); });
      });
    }).catch(function () { });
  }

  function abrirBusca() {
    if (el("busca-cortina")) return;
    var d = document.createElement("div");
    d.className = "busca-cortina";
    d.id = "busca-cortina";
    d.innerHTML = '<div class="busca-caixa"><header>' +
      '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" style="color:var(--t3)"><circle cx="11" cy="11" r="7"></circle><path d="M20 20l-3.6-3.6"></path></svg>' +
      '<input id="busca-campo" type="text" placeholder="cidade, clínica, concorrente…" autocomplete="off"></header>' +
      '<div class="busca-lista" id="busca-lista"></div>' +
      '<div class="busca-status">enter abre · esc fecha</div></div>';
    document.body.appendChild(d);
    var campo = el("busca-campo");
    campo.focus();
    resultados("");
    campo.addEventListener("input", function () { resultados(campo.value); });
    d.addEventListener("click", function (e) { if (e.target === d) fecharBusca(); });
    campo.addEventListener("keydown", function (e) {
      if (e.key === "Escape") fecharBusca();
      if (e.key === "Enter") {
        var b = document.querySelector("#busca-lista .busca-item");
        if (b) b.click();
      }
    });
  }

  function resultados(q) {
    var lista = el("busca-lista");
    if (!lista) return;
    var k = chave(q);
    var achou = k
      ? indice.filter(function (x) { return chave(x.rot).indexOf(k) >= 0; }).slice(0, 40)
      : indice.filter(function (x) { return x.tp === "seção" || x.tp === "clínica"; }).slice(0, 14);
    if (!achou.length) {
      lista.innerHTML = '<div class="busca-status" style="border:0">nada com “' + esc(q) + "”.</div>";
      return;
    }
    lista.innerHTML = achou.map(function (x) {
      return '<button type="button" class="busca-item" data-ir="' + esc(x.ir) + '">' +
        '<span class="tipo">' + esc(x.tp) + '</span><span class="rot">' + esc(x.rot) + "</span></button>";
    }).join("");
  }

  function fecharBusca() {
    var d = el("busca-cortina");
    if (d) d.remove();
  }

  function aplicarTema(t) {
    document.documentElement.setAttribute("data-theme", t);
    try { localStorage.setItem("od-portal-tema", t); } catch (e) { }
  }

  /* ---------- partida ---------- */

  function partir() {
    var t = "dark";
    try { t = localStorage.getItem("od-portal-tema") || "dark"; } catch (e) { }
    aplicarTema(t);

    document.addEventListener("click", function (e) {
      var ir = e.target.closest("[data-ir]");
      if (ir) { fecharBusca(); irPara(ir.getAttribute("data-ir")); return; }
      var ev = e.target.closest("[data-ev]");
      if (ev) {
        var k = ev.getAttribute("data-ev");
        irPara("evidencias");
        setTimeout(function () {
          var n = el("ev-" + k);
          if (n) window.scrollTo(0, n.getBoundingClientRect().top + window.pageYOffset - 90);
        }, 280);
        return;
      }
      var enc = e.target.closest("[data-enc]");
      if (enc) { encaminhar(enc.getAttribute("data-enc"), enc.getAttribute("data-in")); return; }
      if (e.target.closest("#busca")) { abrirBusca(); return; }
      if (e.target.closest("#tema")) {
        aplicarTema(document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark");
      }
    });

    document.addEventListener("keydown", function (e) {
      if ((e.key === "k" || e.key === "K") && (e.metaKey || e.ctrlKey)) { e.preventDefault(); abrirBusca(); return; }
      if (e.key === "/" && !/input|textarea/i.test(e.target.tagName || "")) { e.preventDefault(); abrirBusca(); }
      if (e.key === "Escape") fecharBusca();
    });

    window.addEventListener("hashchange", pintar);

    Promise.all([carregar("manifest"), carregar("franqueadora"), carregar("radar"), carregar("fila"),
      carregar("cabecalhos").catch(function () { return {}; })])
      .then(function (r) {
        manifest = r[0];
        franq = r[1];
        CABS = (r[4] || {}).ferramentas || {};
        var cob = franq.cobertura || {};
        registrarRotulos(manifest.pracas);
        registrarRotulos((r[2] || {}).oportunidades);
        registrarRotulos((r[2] || {}).ja_tem_unidade);
        registrarLojas(r[3]);

        el("corte").textContent = "corte " + data(franq.corte);
        el("cobertura").innerHTML =
          '<span class="fr"><b>' + br(cob.unidades_acompanhadas) + "</b><i> / " + br(cob.unidades_total) + "</i></span>" +
          '<span class="k">unidades</span>' +
          '<span class="barra"><i style="width:' + (cob.unidades_acompanhadas / cob.unidades_total * 100) + '%"></i></span>';

        montarIndice(r[3]);
        pintar();
      }).catch(function (e) {
        el("app").innerHTML = '<div class="dentro">' + telaTopo("", "O portal não abriu",
          "Os dados não carregaram: " + String(e.message || e) +
          ". Esta página precisa ser aberta por um servidor — abrir o arquivo direto do disco bloqueia a leitura.") + "</div>";
      });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", partir);
  else partir();
})();
