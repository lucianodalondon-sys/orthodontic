#!/usr/bin/env python3
"""
build_casco.py — gera o casco: um arquivo só, dados dentro, marca dentro.

Por que existe: três rodadas de prompt para o Claude Design voltaram
apresentação — grade de resumo, sem navegação, sem densidade. Um portal de
inteligência é uma FERRAMENTA: barra lateral fixa, mapa de verdade, tabela
densa, linha do tempo. Este script monta essa ferramenta aqui dentro,
lendo `dados/portal/*.json` e embutindo tudo (payloads, Gotham, geometria
do Brasil, logo) num único `casco/index.html` que abre em qualquer lugar.

As regras de sempre valem: o casco NÃO calcula — todo número vem pronto
do build; rótulo chega com a UF na frente; palavra interna não aparece;
estado vazio é conteúdo.

Uso:
    python3 scripts/build_casco.py        # → casco/index.html
"""
import base64, json, pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PORTAL = RAIZ/"dados"/"portal"
CASCO = RAIZ/"casco"

PAYLOADS = ["franqueadora", "fila", "timeline", "o_que_mudou", "rival",
            "padroes", "caixa_de_respostas", "rede_inteira",
            "funil_nacional", "radar"]


def b64(caminho):
    return base64.b64encode(caminho.read_bytes()).decode()


def main():
    dados = {}
    for p in PAYLOADS:
        arq = PORTAL/f"{p}.json"
        dados[p] = json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else None

    fontes = {peso: b64(CASCO/"assets"/"fonts"/nome) for peso, nome in
              [("300", "gotham-300.otf"), ("400", "gotham-400.ttf"),
               ("500", "gotham-500.ttf"), ("700", "gotham-700.otf")]}
    logo = b64(CASCO/"assets"/"logo-horizontal-white.png")
    brasil = (CASCO/"assets"/"brasil-ufs.js").read_text(encoding="utf-8")

    html = TEMPLATE
    html = html.replace("/*__FONTES__*/", "".join(
        f"@font-face{{font-family:Gotham;font-weight:{peso};font-display:swap;"
        f"src:url(data:font/otf;base64,{dado}) format('opentype');}}"
        for peso, dado in fontes.items()))
    html = html.replace("__LOGO__", f"data:image/png;base64,{logo}")
    html = html.replace("/*__BRASIL__*/", brasil)
    html = html.replace("/*__DADOS__*/",
                        "window.DADOS = " +
                        json.dumps(dados, ensure_ascii=False) + ";")

    CASCO.mkdir(exist_ok=True)
    out = CASCO/"index.html"
    out.write_text(html, encoding="utf-8")
    print(f"→ {out.relative_to(RAIZ)}  ({out.stat().st_size/1024:.0f} KB)")


# ============================================================ o template
TEMPLATE = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OrthoDontic · Inteligência de mercado</title>
<style>
/*__FONTES__*/

/* ---------- o chão ---------- */
:root{
  --navy:#001E78; --navy-2:#001257; --cyan:#00B9FF; --cyan-ink:#0B6E9E;
  --fundo:#F6F8FB; --painel:#FFFFFF; --lavagem:#EEF3FA;
  --t1:#0E1F55; --t2:#3D4A73; --t3:#6B7694;
  --linha:#DCE4F0; --linha-2:#C6D2E6;
  --vermelha:#C2384A; --amarela:#96690A; --verde:#1E7A5A;
  --sombra:0 1px 3px rgba(0,30,120,.06);
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--fundo);color:var(--t1);
  font:400 14px/1.55 Gotham,system-ui,sans-serif;-webkit-font-smoothing:antialiased}
a{color:var(--cyan-ink);text-decoration:none}
h1,h2,h3{margin:0;font-weight:500;letter-spacing:-.01em}
:focus-visible{outline:2px solid var(--cyan);outline-offset:2px;border-radius:3px}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}

/* ---------- a moldura: sidebar + topo ---------- */
.app{display:grid;grid-template-columns:236px 1fr;min-height:100vh}
.lateral{background:linear-gradient(168deg,var(--navy) 0%,var(--navy-2) 100%);
  color:#fff;position:sticky;top:0;height:100vh;overflow-y:auto;
  display:flex;flex-direction:column}
.lateral::-webkit-scrollbar{width:0}
.l-marca{padding:22px 20px 18px;position:relative;overflow:hidden;flex:none}
.l-marca img{height:22px;width:auto;display:block;position:relative}
.l-marca .sub{font-size:11px;letter-spacing:.12em;text-transform:uppercase;
  color:rgba(255,255,255,.55);margin-top:8px;position:relative}
.l-aneis{position:absolute;right:-70px;top:-70px;width:190px;height:190px;
  pointer-events:none}
.l-aneis circle{fill:none;stroke:rgba(0,185,255,.25);stroke-width:1}
.l-nav{padding:6px 0 18px;flex:1}
.l-grupo{font-size:10px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;
  color:rgba(255,255,255,.42);padding:18px 20px 6px}
.l-item{display:flex;align-items:center;gap:8px;padding:7px 20px 7px 17px;
  color:rgba(255,255,255,.82);font-size:13px;border-left:3px solid transparent;
  cursor:pointer;transition:background 150ms}
.l-item:hover{background:rgba(255,255,255,.06);color:#fff}
.l-item.ativo{border-left-color:var(--cyan);background:rgba(0,185,255,.10);color:#fff}
.l-item .badge{margin-left:auto;font-size:11px;font-weight:500;
  color:var(--cyan);font-variant-numeric:tabular-nums}
.l-item .badge.alerta{color:#FF8FA0}
.l-rodape{padding:14px 20px 20px;font-size:10.5px;line-height:1.5;
  color:rgba(255,255,255,.38);border-top:1px solid rgba(255,255,255,.10);flex:none}

.palco{min-width:0}
.topo{background:var(--painel);border-bottom:1px solid var(--linha);
  padding:14px 28px;display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;
  position:sticky;top:0;z-index:5}
.topo h1{font-size:19px;font-weight:500}
.topo .corte{margin-left:auto;font-size:11.5px;color:var(--t3)}
.cobertura{background:var(--lavagem);border-bottom:1px solid var(--linha);
  padding:7px 28px;font-size:11.5px;color:var(--t2)}
.conteudo{padding:24px 28px 60px;max-width:1240px}

/* ---------- peças ---------- */
.painel{background:var(--painel);border:1px solid var(--linha);border-radius:8px;
  box-shadow:var(--sombra)}
.p-cab{padding:12px 16px;border-bottom:1px solid var(--linha);display:flex;
  align-items:baseline;gap:10px}
.p-cab h2{font-size:14px;font-weight:700}
.p-cab .aux{margin-left:auto}
.p-corpo{padding:14px 16px}
.aux{font-size:11.5px;color:var(--t3)}
.olho{font-size:10px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;
  color:var(--t3)}
.num{font-family:Gotham;font-weight:300;font-variant-numeric:tabular-nums}

table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}
th{font-size:10px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;
  color:var(--t3);text-align:left;padding:8px 10px;border-bottom:1px solid var(--linha-2);
  white-space:nowrap}
td{padding:9px 10px;border-bottom:1px solid var(--linha);vertical-align:top;font-size:13px}
tr:last-child td{border-bottom:none}
tr.clica{cursor:pointer}
tr.clica:hover td{background:var(--lavagem)}
td.n,th.n{text-align:right}
.rolagem{overflow-x:auto}

.dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px;
  vertical-align:1px}
.dot.vermelha{background:var(--vermelha)} .dot.amarela{background:var(--amarela)}
.dot.verde{background:var(--verde)} .dot.cinza{background:var(--linha-2)}
.chip{display:inline-block;font-size:10.5px;font-weight:500;letter-spacing:.04em;
  padding:2px 8px;border-radius:99px;border:1px solid var(--linha-2);color:var(--t2);
  white-space:nowrap}
.chip.vencida{border-color:var(--vermelha);color:var(--vermelha)}
.chip.aberta{border-color:var(--linha-2)}
.chip.selo{border-color:var(--cyan);color:var(--cyan-ink)}
.aviso{background:#FFF8E8;border:1px solid #EAD9A8;border-radius:6px;
  padding:8px 12px;font-size:12px;color:#6b5410;margin:10px 0}
.naove{margin-top:26px;border-top:1px solid var(--linha);padding-top:12px}
.naove .olho{margin-bottom:6px;display:block}
.naove li{font-size:12px;color:var(--t3);margin:4px 0 4px 0}
.naove ul{margin:0;padding-left:18px}
.apagado{opacity:.55}
details summary{cursor:pointer;font-size:12px;color:var(--t3)}
details[open] summary{margin-bottom:8px}

/* ---------- HOJE ---------- */
.faixa-rede{display:flex;gap:36px;flex-wrap:wrap;align-items:baseline;
  padding:4px 0 20px}
.faixa-rede .b .num{font-size:44px;line-height:1;color:var(--navy)}
.faixa-rede .b .rot{font-size:11.5px;color:var(--t3);margin-top:4px}
.grade-hoje{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(280px,1fr);
  gap:18px;align-items:start}
.mapa-svg path{fill:rgba(0,185,255,0);stroke:var(--linha-2);stroke-width:.8;
  cursor:pointer;transition:stroke 150ms}
.mapa-svg path:hover{stroke:var(--navy);stroke-width:1.4}
.mapa-svg path.sel{stroke:var(--navy);stroke-width:1.6}
.mapa-legenda{display:flex;gap:14px;align-items:center;flex-wrap:wrap;
  padding:10px 16px;border-top:1px solid var(--linha);font-size:11px;color:var(--t3)}
.mapa-legenda .sw{display:inline-block;width:12px;height:12px;border-radius:2px;
  border:1px solid var(--linha-2);vertical-align:-2px;margin-right:5px}
.uf-painel{padding:12px 16px;border-top:1px solid var(--linha);font-size:13px}
.uf-painel .num{font-size:30px;color:var(--navy)}
.acao-item{display:block;padding:12px 16px;border-bottom:1px solid var(--linha);
  color:inherit;transition:background 150ms}
.acao-item:hover{background:var(--lavagem)}
.acao-item:last-child{border-bottom:none}
.acao-item .num{font-size:30px;line-height:1.1;color:var(--navy)}
.acao-item.quente .num{color:var(--vermelha)}
.acao-item .t{font-size:12.5px;font-weight:700;margin-top:2px}
.acao-item .d{font-size:11.5px;color:var(--t3);margin-top:2px}

/* ---------- fila ---------- */
.urg{display:inline-block;width:64px;height:4px;border-radius:2px;
  background:var(--lavagem);position:relative;vertical-align:2px}
.urg i{position:absolute;left:0;top:0;bottom:0;border-radius:2px;background:var(--navy)}
.det{background:var(--lavagem);border-radius:6px;padding:10px 12px;margin:4px 0 8px;
  font-size:12.5px}
.det .g{margin:4px 0}
.det .fonte{color:var(--t3);font-size:11px}
.acao-caixa{border-left:3px solid var(--cyan);padding:6px 10px;margin-top:8px;
  font-size:12.5px;background:#fff;border-radius:0 6px 6px 0}

/* ---------- timeline ---------- */
.grade-lojas{display:grid;grid-template-columns:300px minmax(0,1fr);gap:18px;
  align-items:start}
.loja-item{padding:10px 14px;border-bottom:1px solid var(--linha);cursor:pointer;
  transition:background 150ms}
.loja-item:hover{background:var(--lavagem)}
.loja-item.sel{background:var(--lavagem);border-left:3px solid var(--cyan);
  padding-left:11px}
.loja-item .n1{font-size:13px;font-weight:500}
.loja-item .n2{font-size:11.5px;color:var(--t3);margin-top:1px}
.tl{list-style:none;margin:0;padding:0 0 0 6px;position:relative}
.tl:before{content:"";position:absolute;left:11px;top:6px;bottom:6px;
  width:1px;background:var(--linha-2)}
.tl li{position:relative;padding:0 0 16px 30px}
.tl .pt{position:absolute;left:7px;top:5px;width:9px;height:9px;border-radius:50%;
  background:#fff;border:2px solid var(--t3)}
.tl li.q-paciente .pt{border-color:var(--amarela)}
.tl li.q-rival .pt{border-color:var(--vermelha)}
.tl li.q-fila .pt{border-color:var(--navy)}
.tl li.q-nossa .pt{border-color:var(--cyan)}
.tl .quando{font-size:11px;color:var(--t3);font-variant-numeric:tabular-nums}
.tl .oq{font-size:13px;margin-top:1px}
.tl .rotq{font-size:10px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;
  margin-left:8px;color:var(--t3)}
.cab-loja{display:flex;gap:28px;flex-wrap:wrap;align-items:baseline;
  padding:2px 0 14px}
.cab-loja .num{font-size:30px;color:var(--navy)}
.cab-loja .rot{font-size:11px;color:var(--t3)}

/* ---------- rival / padrões ---------- */
.barra{height:5px;background:var(--lavagem);border-radius:3px;position:relative;
  min-width:90px}
.barra i{position:absolute;left:0;top:0;bottom:0;background:var(--cyan);
  border-radius:3px}
.hip{border:1px solid var(--linha);border-radius:8px;padding:14px 16px;background:#fff}
.hip .veredito{font-size:20px;font-weight:700;color:var(--vermelha);
  letter-spacing:.02em;margin:6px 0}
.grade-hip{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));
  gap:12px;margin-bottom:18px}
.conclusao{border-left:3px solid var(--cyan);background:#fff;border-radius:0 8px 8px 0;
  padding:14px 18px;margin:6px 0 18px;border-top:1px solid var(--linha);
  border-right:1px solid var(--linha);border-bottom:1px solid var(--linha)}
.estrela{color:var(--amarela);letter-spacing:.06em}
.secao{margin:26px 0 10px}
.secao h2{font-size:15px;font-weight:700}
.secao .aux{margin-top:2px}

@media (max-width:960px){
  .app{grid-template-columns:1fr}
  .lateral{position:relative;height:auto}
  .grade-hoje,.grade-lojas{grid-template-columns:1fr}
}
</style>
</head>
<body>
<div class="app">
<aside class="lateral">
  <div class="l-marca">
    <svg class="l-aneis" viewBox="0 0 200 200" aria-hidden="true">
      <circle cx="100" cy="100" r="52"/><circle cx="100" cy="100" r="76"/>
      <circle cx="100" cy="100" r="98"/>
    </svg>
    <img src="__LOGO__" alt="OrthoDontic">
    <div class="sub">Inteligência de mercado</div>
  </div>
  <nav class="l-nav" id="nav"></nav>
  <div class="l-rodape" id="rodape"></div>
</aside>
<div class="palco">
  <header class="topo"><h1 id="titulo"></h1><span class="corte" id="corte"></span></header>
  <div class="cobertura" id="cobertura"></div>
  <main class="conteudo" id="tela"></main>
</div>
</div>

<script>
/*__BRASIL__*/
/*__DADOS__*/

(function(){
"use strict";
const D = window.DADOS;
const fmt = n => n==null ? "—" : Number(n).toLocaleString("pt-BR");
const esc = s => String(s==null?"":s).replace(/[&<>"]/g,
  c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const cardPor = ch => (D.franqueadora.cards||[]).find(c => c.chave===ch) || {};

/* ---------------- navegação ---------------- */
const NAV = [
 {grupo:"", itens:[["hoje","Hoje"]]},
 {grupo:"A rede", itens:[["mapa","A rede no Brasil"],["alertas","Alertas nas fichas"],
   ["reputacao","Reclame Aqui"]]},
 {grupo:"As 10 lojas", itens:[["fila","Onde agir primeiro"],["lojas","A vida de cada loja"],
   ["mudou","O que mudou"],["caixa","Avaliações sem resposta"],
   ["rival","Concorrentes de ortodontia"],["padroes","O que faz crescer"]]},
 {grupo:"Expansão", itens:[["funil","As melhores cidades"],["radar","Cidades estudadas"]]},
 {grupo:"", itens:[["arquivo","Arquivo"]]},
];
const TIT = {}; NAV.forEach(g => g.itens.forEach(([id,t]) => TIT[id]=t));

function badge(id){
  const f = D.fila, c = D.caixa_de_respostas;
  if(id==="fila" && f) return {n:f.em_risco, alerta:f.em_risco>0};
  if(id==="caixa" && c) return {n:c.total_abertas, alerta:false};
  if(id==="alertas") return {n:(cardPor("alertas").numero), alerta:cardPor("alertas").numero>0};
  return null;
}
function desenhaNav(atual){
  document.getElementById("nav").innerHTML = NAV.map(g =>
    (g.grupo?`<div class="l-grupo">${esc(g.grupo)}</div>`:"") +
    g.itens.map(([id,t]) => {
      const b = badge(id);
      return `<a class="l-item${id===atual?" ativo":""}" href="#/${id}">${esc(t)}`+
        (b&&b.n!=null?`<span class="badge${b.alerta?" alerta":""}">${fmt(b.n)}</span>`:"")+`</a>`;
    }).join("")).join("");
}

/* ---------------- peças ---------------- */
const painel = (cab, corpo, aux) =>
  `<section class="painel"><div class="p-cab"><h2>${cab}</h2>`+
  (aux?`<span class="aux">${aux}</span>`:"")+`</div>${corpo}</section>`;
const naove = lista => (lista&&lista.length) ?
  `<div class="naove"><span class="olho">O que isto não vê</span><ul>`+
  lista.map(x=>`<li>${esc(x)}</li>`).join("")+`</ul></div>` : "";
const estrelas = n => `<span class="estrela">${"★".repeat(n||0)}${"☆".repeat(Math.max(5-(n||0),0))}</span>`;
const dotFaixa = f => `<span class="dot ${esc(f||"cinza")}"></span>`;
const chipTarefa = t => !t ? "" :
  `<span class="chip ${t.status}">${t.status==="vencida"?"vencida há "+(t.dias_aberta-(t.prazo_dias||0))+"d":"aberta"}${t.vence_em?" · vence "+t.vence_em.slice(5).split("-").reverse().join("/"):""}</span>`;

/* ---------------- mapa ---------------- */
function svgMapa(sel){
  const porUf = {}; (D.franqueadora.mapa||[]).forEach(m => porUf[m.uf]=m);
  const ufs = (window.BRASIL_UFS.ufs)||window.BRASIL_UFS;
  const alfa = u => !u ? 0 : u<5 ? .16 : u<15 ? .34 : u<40 ? .55 : .8;
  let p = "";
  for(const [uf,g] of Object.entries(ufs)){
    const m = porUf[uf]||{unidades:0};
    p += `<path d="${g.d}" data-uf="${uf}" class="${sel===uf?"sel":""}"
      style="fill:rgba(0,185,255,${alfa(m.unidades)})">
      <title>${uf} — ${fmt(m.unidades)} unidade(s)</title></path>`;
  }
  return `<svg class="mapa-svg" viewBox="0 0 560 588" role="img"
    aria-label="Mapa do Brasil por unidades" style="width:100%;height:auto;display:block;padding:14px">${p}</svg>`;
}
const legendaMapa = `<div class="mapa-legenda">
  <span><span class="sw" style="background:rgba(0,185,255,0)"></span>sem unidade — o vazio é a informação</span>
  <span><span class="sw" style="background:rgba(0,185,255,.16)"></span>1–4</span>
  <span><span class="sw" style="background:rgba(0,185,255,.34)"></span>5–14</span>
  <span><span class="sw" style="background:rgba(0,185,255,.55)"></span>15–39</span>
  <span><span class="sw" style="background:rgba(0,185,255,.8)"></span>40+</span></div>`;
function painelUf(uf){
  const m = (D.franqueadora.mapa||[]).find(x=>x.uf===uf);
  if(!m) return "";
  return `<div class="uf-painel"><span class="olho">${esc(uf)}</span>
    <div style="display:flex;gap:26px;flex-wrap:wrap;align-items:baseline">
    <div><span class="num">${fmt(m.unidades)}</span> <span class="aux">unidades</span></div>
    <div><span class="num">${fmt(m.abertas)}</span> <span class="aux">abertas</span></div>
    <div><span class="num">${fmt(m.em_implantacao)}</span> <span class="aux">em implantação</span></div>
    <div><span class="num">${fmt(m.cidades)}</span> <span class="aux">cidades</span></div>
    <div><span class="num">${fmt(m.pracas_medidas)}</span> <span class="aux">praças medidas</span></div>
    </div></div>`;
}
function ligaMapa(container, telaBase){
  container.querySelectorAll(".mapa-svg path").forEach(p =>
    p.addEventListener("click", () => { location.hash = `#/${telaBase}?uf=${p.dataset.uf}`; }));
}

/* ---------------- telas ---------------- */
const TELAS = {};

TELAS.hoje = function(){
  const r = D.franqueadora.rede, ag = D.franqueadora.agora||{};
  const rail = [
    {ch:"fila", quente:(D.fila&&D.fila.em_risco>0)},
    {ch:"mudou", quente:cardPor("mudou").numero>0},
    {ch:"caixa", quente:false},
    {ch:"alertas", quente:cardPor("alertas").numero>0},
    {ch:"rival", quente:false},
  ].map(({ch,quente}) => {
    const c = cardPor(ch); if(!c.chave) return "";
    const tela = {mudou:"mudou",caixa:"caixa",fila:"fila",alertas:"alertas",rival:"rival"}[ch];
    return `<a class="acao-item${quente?" quente":""}" href="#/${tela}">
      <span class="num">${c.numero==null?"—":fmt(c.numero)}</span>
      <div class="t">${esc(c.titulo)}</div><div class="d">${esc(c.frase)}</div></a>`;
  }).join("");
  const lojas = ((D.timeline||{}).lojas||[]).map(l => {
    const c = l.cabecalho||{};
    return `<tr class="clica" data-lid="${esc(l.local_id)}">
      <td>${dotFaixa(l.faixa)}${esc(l.rotulo)}<div class="aux">${esc(l.unidade)}</div></td>
      <td class="n">${c.nota==null?"—":c.nota}</td>
      <td class="n">${fmt(c.avaliacoes)}</td>
      <td class="n">${c.ritmo==null?"—":c.ritmo}/mês</td>
      <td class="n">${c.posicao?c.posicao+"º de "+c.de:"—"}</td>
      <td>${chipTarefa(l.tarefa)||'<span class="aux">sem tarefa</span>'}</td></tr>`;
  }).join("");
  return `
  <div class="faixa-rede">
    <div class="b"><span class="num">${fmt(r.unidades)}</span><div class="rot">unidades na lista oficial</div></div>
    <div class="b"><span class="num">${fmt(r.abertas)}</span><div class="rot">abertas</div></div>
    <div class="b"><span class="num">${fmt(r.em_implantacao)}</span><div class="rot">em implantação</div></div>
    <div class="b"><span class="num">${fmt(r.cidades)}</span><div class="rot">cidades</div></div>
    <div class="b"><span class="num">${r.ufs_sem_unidade.length}</span><div class="rot">estados sem unidade (${r.ufs_sem_unidade.join(", ")})</div></div>
  </div>
  <div class="grade-hoje">
    <div class="painel" id="bloco-mapa">
      <div class="p-cab"><h2>A rede no Brasil</h2>
        <span class="aux">clique num estado · fonte: ${esc(r.fonte)}</span></div>
      ${svgMapa()}${legendaMapa}
    </div>
    <div class="painel"><div class="p-cab"><h2>O que pede atenção</h2></div>${rail}</div>
  </div>
  <div class="secao"><h2>As 10 lojas acompanhadas</h2>
    <div class="aux">${esc(ag.o_que_e_atencao||"")}</div></div>
  <div class="painel rolagem"><table>
    <thead><tr><th>loja</th><th class="n">nota</th><th class="n">avaliações</th>
    <th class="n">ritmo</th><th class="n">posição na praça</th><th>tarefa</th></tr></thead>
    <tbody>${lojas}</tbody></table></div>`;
};
TELAS.hoje.depois = function(el){
  ligaMapa(el, "mapa");
  el.querySelectorAll("tr[data-lid]").forEach(tr =>
    tr.addEventListener("click", () => location.hash = "#/lojas?lid="+tr.dataset.lid));
};

TELAS.mapa = function(q){
  const ri = D.rede_inteira||{};
  const uf = q.uf || "";
  const tabela = (ri.por_uf||[]).map(x =>
    `<tr class="clica" data-uf="${x.uf}"><td>${x.uf}</td>
     <td class="n">${fmt(x.unidades)}</td><td class="n">${x.nota_mediana??"—"}</td></tr>`).join("");
  return `<div class="grade-hoje">
    <div class="painel" id="bloco-mapa">${svgMapa(uf)}${legendaMapa}${uf?painelUf(uf):""}</div>
    <div class="painel"><div class="p-cab"><h2>Estado a estado</h2>
      <span class="aux">nota mediana das fichas conferidas</span></div>
      <div class="rolagem"><table><thead><tr><th>UF</th><th class="n">unidades</th>
      <th class="n">nota mediana</th></tr></thead><tbody>${tabela}</tbody></table></div></div>
  </div>`;
};
TELAS.mapa.depois = function(el){
  ligaMapa(el, "mapa");
  el.querySelectorAll("tr[data-uf]").forEach(tr =>
    tr.addEventListener("click", () => location.hash = "#/mapa?uf="+tr.dataset.uf));
};

TELAS.alertas = function(){
  const ri = D.rede_inteira||{};
  const linhas = (ri.alertas||[]).map(a =>
    `<tr><td>${dotFaixa(a.gravidade)}${esc(a.unidade||a.nome_no_google)}
       <div class="aux">${esc(a.cidade)}/${esc(a.uf)}</div></td>
     <td>${esc(a.por_que)}</td>
     <td><span class="chip">${esc(a.de_quem_e||"—")}</span></td>
     <td class="n">${a.nota??"—"}</td><td class="n">${fmt(a.avaliacoes)}</td></tr>`).join("");
  return `<p class="aux" style="max-width:70ch">${esc(ri.o_que_e||"")}</p>
  <div class="painel rolagem" style="margin-top:12px"><table>
    <thead><tr><th>unidade</th><th>por quê</th><th>de quem é</th>
    <th class="n">nota</th><th class="n">avaliações</th></tr></thead>
    <tbody>${linhas}</tbody></table></div>
  <p class="aux" style="margin-top:10px">${fmt(ri.confirmadas)} de ${fmt(ri.na_lista_oficial)}
    fichas conferidas · ${fmt(ri.nao_confirmadas)} não confirmadas, nomeadas no arquivo.</p>
  ${naove([ri.o_que_nao_e])}`;
};

TELAS.reputacao = function(){
  const reps = D.franqueadora.reputacao_das_redes||[];
  const fora = (D.franqueadora.reputacao_fora_da_tela||{});
  const linhas = reps.map(r =>
    `<tr${r.nossa?' style="background:var(--lavagem);font-weight:500"':""}>
     <td>${esc(r.marca)}${r.nossa?' <span class="chip selo">nós</span>':""}</td>
     <td><span class="chip">${esc(r.foco||"")}</span></td>
     <td class="n">${fmt(r.reclamacoes)}</td><td class="n">${r.nota??"—"}</td>
     <td>${esc(r.selo||"")}</td></tr>`).join("");
  return painel("Rede contra rede, no Reclame Aqui",
    `<div class="rolagem"><table><thead><tr><th>marca</th><th>foco</th>
     <th class="n">reclamações</th><th class="n">nota</th><th>selo</th></tr></thead>
     <tbody>${linhas}</tbody></table></div>`)+
    naove([(fora.por_que||"")+" "+((fora.redes||[]).map(r=>r.marca||r).join(", "))]);
};

TELAS.fila = function(){
  const f = D.fila||{};
  const linhas = (f.fila||[]).map(x => {
    const gat = (x.gatilhos||[]).map(g =>
      `<div class="g">· ${esc(g.titulo)} — ${esc(g.fato)}
       <span class="fonte">${esc(g.fonte)}</span></div>`).join("");
    const acao = x.acao ? `<div class="acao-caixa"><b>${esc(x.acao.o_que)}</b><br>
      <span class="aux">${esc(x.acao.prazo)} · ${esc(x.acao.dono)} · ${esc(x.acao.custo)}</span></div>` : "";
    const rival = x.quem_avanca ? `<div class="g" style="margin-top:6px">
      <b>quem avança:</b> ${esc(x.quem_avanca.nome)} — ${x.quem_avanca.ritmo}/mês há
      ${x.quem_avanca.meses} meses</div>` : "";
    return `<tr class="clica" data-abre="${x.pos}">
      <td style="white-space:nowrap">${x.pos}. ${dotFaixa(x.faixa)}${esc(x.rotulo)}${x.unidade_curta?" · "+esc(x.unidade_curta):""}</td>
      <td><span class="urg"><i style="width:${x.urgencia}%"></i></span>
        <span class="aux"> ${x.urgencia}</span></td>
      <td class="n">${x.nota??"—"}</td><td class="n">${x.ritmo??"—"}/mês</td>
      <td>${chipTarefa(x.tarefa)||'<span class="aux">—</span>'}</td></tr>
    <tr class="detalhe" id="det-${x.pos}" hidden><td colspan="5">
      <div class="det">${gat}${rival}${acao}</div></td></tr>`;
  }).join("");
  const res = (f.tarefas_resolvidas||[]);
  const resolvidas = res.length ?
    painel("Tarefas resolvidas — o dado externo fechou o loop",
      res.map(r=>`<div class="p-corpo" style="border-bottom:1px solid var(--linha)">
        ${esc(r.rotulo)} — ${esc(r.titulo)} <span class="aux">(aberta em ${r.aberta_em};
        ${esc(r.leitura)})</span></div>`).join("")) :
    `<p class="aux" style="margin-top:14px">Nenhuma tarefa resolvida ainda — o histórico
     começou em ${esc(f.gerado_em||"")}; a partir da próxima medição, gatilho que sumir
     aparece aqui como vitória.</p>`;
  return `<p style="max-width:70ch">${esc(f.manchete||"")}</p>
    <p class="aux" style="max-width:70ch">${esc(f.o_que_e_atencao||"")}</p>
    <div class="painel rolagem" style="margin-top:12px"><table>
    <thead><tr><th>loja</th><th>urgência</th><th class="n">nota</th>
    <th class="n">ritmo</th><th>tarefa</th></tr></thead><tbody>${linhas}</tbody></table></div>
    <p class="aux" style="margin-top:8px">clique numa linha para ver os gatilhos e a ação</p>
    <div style="margin-top:18px">${resolvidas}</div>
    ${naove(f.o_que_isso_nao_ve)}`;
};
TELAS.fila.depois = function(el){
  el.querySelectorAll("tr[data-abre]").forEach(tr =>
    tr.addEventListener("click", () => {
      const d = el.querySelector("#det-"+tr.dataset.abre);
      if(d) d.hidden = !d.hidden;
    }));
};

TELAS.lojas = function(q){
  const ls = (D.timeline||{}).lojas||[];
  const sel = q.lid ? ls.find(l=>l.local_id===q.lid) : ls[0];
  const lista = ls.map(l =>
    `<div class="loja-item${sel&&l.local_id===sel.local_id?" sel":""}" data-lid="${esc(l.local_id)}">
     <div class="n1">${dotFaixa(l.faixa)}${esc(l.rotulo)}</div>
     <div class="n2">${esc(l.unidade)} ${l.tarefa?"· tarefa "+l.tarefa.status:""}</div></div>`).join("");
  let det = `<div class="p-corpo aux">selecione uma loja</div>`;
  if(sel){
    const c = sel.cabecalho||{};
    const evs = (sel.eventos||[]).map(e =>
      `<li class="q-${esc(e.quem)}"><span class="pt"></span>
       <span class="quando">${esc(e.data)}</span><span class="rotq">${esc(e.quem)}</span>
       <div class="oq">${esc(e.texto)}</div></li>`).join("");
    det = `<div class="p-corpo">
      <div class="cab-loja">
        <div><span class="num">${c.nota??"—"}</span><div class="rot">nota</div></div>
        <div><span class="num">${fmt(c.avaliacoes)}</span><div class="rot">avaliações</div></div>
        <div><span class="num">${c.ritmo??"—"}</span><div class="rot">/mês</div></div>
        <div><span class="num">${c.posicao?c.posicao+"º":"—"}</span><div class="rot">de ${c.de??"—"} na praça</div></div>
        <div>${chipTarefa(sel.tarefa)||'<span class="aux">sem tarefa</span>'}</div>
      </div>
      ${sel.sem_resposta&&sel.sem_resposta.abertas?`<div class="aviso">${fmt(sel.sem_resposta.abertas)}
        avaliação(ões) negativas sem resposta nesta loja — a lista está em
        <a href="#/caixa">Avaliações sem resposta</a>.</div>`:""}
      <ul class="tl">${evs||'<li><span class="pt"></span><div class="oq aux">sem eventos na janela</div></li>'}</ul>
      ${sel.eventos_alem_da_janela?`<div class="aux">+${sel.eventos_alem_da_janela} eventos além do corte</div>`:""}
    </div>`;
  }
  return `<p class="aux" style="max-width:74ch">${esc((D.timeline||{}).como_ler||"")}</p>
  <div class="grade-lojas" style="margin-top:12px">
    <div class="painel">${lista}</div>
    <div class="painel"><div class="p-cab"><h2>${sel?esc(sel.rotulo)+" · "+esc(sel.unidade):""}</h2></div>${det}</div>
  </div>`;
};
TELAS.lojas.depois = function(el){
  el.querySelectorAll(".loja-item").forEach(li =>
    li.addEventListener("click", () => location.hash = "#/lojas?lid="+li.dataset.lid));
};

TELAS.mudou = function(){
  const m = D.o_que_mudou||{};
  const blocos = Object.values(m.pracas||{}).map(p => {
    const linha = x => `<tr><td>${x.proprio?'<span class="chip selo">nossa</span> ':""}
      ${esc(x.nome)}</td>
      <td class="n">${fmt(x.antes)} → ${fmt(x.agora)}</td>
      <td class="n" style="color:${x.delta>0?"var(--verde)":x.delta<0?"var(--vermelha)":"var(--t3)"}">
      ${x.delta>0?"▲ +":x.delta<0?"▼ ":"· "}${x.delta<0?-x.delta:x.delta}</td>
      <td class="aux">${(x.eventos||[]).map(esc).join(" · ")}</td></tr>`;
    const nossas = (p.nossas||[]).map(linha).join("");
    const ganhou = (p.quem_mais_ganhou||[]).filter(x=>!x.proprio).map(linha).join("");
    const caiu = (p.contador_caiu||[]).map(linha).join("");
    return `<div class="secao"><h2>${esc(p.rotulo)}</h2>
      <div class="aux">${p.dias_medidos} dia(s) medidos</div></div>
      ${p.aviso?`<div class="aviso">${esc(p.aviso)}</div>`:""}
      <div class="painel rolagem"><table><tbody>
      ${nossas || '<tr><td class="aux">nenhuma loja nossa com par de medições aqui</td></tr>'}
      ${caiu?`<tr><th colspan="4">contador caiu — avaliação apagada, evento raro</th></tr>${caiu}`:""}
      ${ganhou?`<tr><th colspan="4">rivais de aparelho que mais ganharam</th></tr>${ganhou}`:""}
      </tbody></table></div>`;
  }).join("");
  return `<p class="aux" style="max-width:74ch">${esc(m.como_ler||"")}</p>${blocos}`;
};

TELAS.caixa = function(){
  const c = D.caixa_de_respostas||{};
  const blocos = (c.unidades||[]).map(u => {
    const itens = (u.itens||[]).map(i =>
      `<div class="p-corpo" style="border-bottom:1px solid var(--linha)">
       ${estrelas(i.nota)} <span class="aux">${esc(i.data||"sem data")}</span>
       <div style="margin-top:4px;max-width:80ch">${esc(i.texto||"(sem texto)")}</div></div>`).join("");
    return painel(`${esc(u.rotulo)} · ${esc(u.unidade)}`,
      itens||'<div class="p-corpo aux">sem avaliações abertas com texto</div>',
      `${fmt(u.abertas)} abertas · ${fmt(u.com_texto)} com texto`)+"<br>";
  }).join("");
  return `<p style="max-width:70ch">${esc(c.manchete||"")}</p>
    <div class="aviso">${esc(c.a_regra||"")}</div>${blocos}`;
};

TELAS.rival = function(){
  const r = D.rival||{};
  const rede = (r.padrao_da_rede||[]).map(e =>
    `<tr><td>${esc(e.o_que_e)}</td>
     <td><span class="barra"><i style="width:${Math.round(100*e.perde_em/e.de)}%"></i></span>
     <span class="aux"> perde em ${e.perde_em} de ${e.de} lojas</span></td>
     <td class="n">até ${e.pior_razao}x</td>
     <td>${e.de_quem_e_a_decisao?`<span class="chip">${esc(e.de_quem_e_a_decisao)}</span>`:""}</td></tr>`).join("");
  const lojas = (r.pracas||[]).map(p => {
    if(p.sem_comparacao_porque){
      return `<div class="painel apagado" style="margin-bottom:12px"><div class="p-cab">
        <h2>${esc(p.rotulo)} · ${esc(p.unidade)}</h2></div>
        <div class="p-corpo aux">${esc(p.sem_comparacao_porque)}</div></div>`;
    }
    const v = (p.vantagens_deles||[]).map(x =>
      `<tr><td>${esc(x.o_que_e)}</td><td>${esc(x.quem)}</td>
       <td class="n">${x.eles}% deles · ${x.nos}% nosso</td><td class="n">${x.razao}x</td></tr>`).join("");
    const fora = (p.rivais_fora||[]).map(x =>
      `<li>${esc(x.nome)} — <span class="aux">${esc(x.por_que_fora)}</span></li>`).join("");
    return `<div class="painel" style="margin-bottom:12px"><div class="p-cab">
      <h2>${esc(p.rotulo)} · ${esc(p.unidade)}</h2>
      <span class="aux">${fmt(p.nossas_avaliacoes_lidas)} avaliações nossas ·
      contra ${(p.rivais_comparados||[]).map(esc).join(", ")}</span></div>
      ${v?`<div class="rolagem"><table><thead><tr><th>onde perdemos</th><th>para quem</th>
      <th class="n">proporção</th><th class="n">razão</th></tr></thead><tbody>${v}</tbody></table></div>`
      :'<div class="p-corpo aux">nenhuma vantagem acima do corte — a praça está equilibrada</div>'}
      ${fora?`<div class="p-corpo"><details><summary>fora da comparação — outro produto
      (${(p.rivais_fora||[]).length})</summary><ul>${fora}</ul></details></div>`:""}
    </div>`;
  }).join("");
  return `<p class="aux" style="max-width:74ch">${esc(r.o_que_e||"")} ${esc(r.o_que_nao_e||"")}</p>
  <div class="secao"><h2>O padrão da rede</h2>
    <div class="aux">perder num eixo em muitas praças é decisão de franqueadora, não de loja</div></div>
  <div class="painel rolagem"><table><tbody>${rede}</tbody></table></div>
  <div class="secao"><h2>Loja por loja</h2></div>${lojas}`;
};

TELAS.padroes = function(){
  const p = D.padroes||{};
  const hips = (p.hipoteses_testadas||[]).map(h =>
    `<div class="hip"><div class="aux">${esc(h.h)}</div>
     <div class="veredito">${esc(h.veredito)}</div>
     <div style="font-size:12.5px">${esc(h.prova)}</div></div>`).join("");
  const c = p.conclusao||{};
  const lojas = (p.lojas||[]).map(l =>
    `<tr><td>${esc(l.rotulo)}<div class="aux">${esc(l.unidade)}</div></td>
     <td class="n">${l.ritmo_vida??"—"}/mês</td><td class="n">${l.meses_seguidos??"—"} meses</td>
     <td><span class="chip">${esc(l.selo||"")}</span></td></tr>`).join("");
  return `<div class="grade-hip">${hips}</div>
    <div class="conclusao"><b>${esc(c.t||"")}</b>
    <p style="margin:6px 0 0;max-width:76ch">${esc(c.leitura||"")}</p>
    <p style="margin:6px 0 0;max-width:76ch"><b>consequência:</b> ${esc(c.consequencia||"")}</p>
    <p class="aux" style="margin:6px 0 0">${esc(c.controle||"")}</p></div>
    <div class="painel rolagem"><table><thead><tr><th>loja</th><th class="n">ritmo</th>
    <th class="n">constância</th><th>selo</th></tr></thead><tbody>${lojas}</tbody></table></div>
    ${naove(p.o_que_isso_nao_ve)}`;
};

TELAS.funil = function(){
  const f = D.funil_nacional||{};
  const met = f.metodo||{};
  const regua = (met.regua_hab_por_unidade||[]).map(r =>
    `<tr><td>${esc(r.faixa)}</td><td class="n">1 : ${fmt(r.mediana_hab_por_unidade)}</td>
     <td class="n">${r.cidades_da_rede_na_faixa} cidades</td></tr>`).join("");
  const cands = (f.candidatas||[]).map((c,i) =>
    `<tr><td class="n">${i+1}</td><td>${esc(c.rotulo)}
     ${c.ja_estudada?'<span class="chip selo">já estudada</span>':""}</td>
     <td class="n">${fmt(c.populacao)}</td><td class="n">${fmt(c.alvo_9_15)}</td>
     <td class="n">${fmt(c.alvo_30_45)}</td><td class="n">${c.renda_relativa}x</td>
     <td class="n">${fmt(c.score)}</td>
     <td class="n">${c.comporta_pela_regua??"—"}</td></tr>`).join("");
  const cabem = (f.onde_cabem_mais||[]).map(s =>
    `<tr><td>${esc(s.rotulo)}</td><td class="n">${s.unidades_hoje}</td>
     <td class="n">${s.comporta_pela_regua}</td>
     <td class="n" style="color:var(--cyan-ink);font-weight:500">+${s.folga}</td>
     <td class="aux">${esc(s.leitura)}</td></tr>`).join("");
  return `<p class="aux" style="max-width:74ch">${esc(f.o_que_e||"")}</p>
  <div class="grade-hoje" style="margin-top:12px">
    ${painel("O método, aberto", `<div class="p-corpo" style="font-size:12.5px">
      <b>score</b> = ${esc(met.score||"")}<br><span class="aux">piso de população:
      ${fmt(met.piso_populacao)} hab — ${esc(met.piso_porque||"")}</span></div>
      <div class="rolagem"><table><thead><tr><th>faixa de cidade</th>
      <th class="n">hab por unidade</th><th class="n">base</th></tr></thead>
      <tbody>${regua}</tbody></table></div>`, "a régua é a própria rede")}
    ${painel("Onde cabem mais unidades — dentro de casa",
      `<div class="rolagem"><table><thead><tr><th>cidade</th><th class="n">hoje</th>
       <th class="n">comporta</th><th class="n">folga</th><th></th></tr></thead>
       <tbody>${cabem||'<tr><td class="aux">nenhuma cidade com folga ≥ 2</td></tr>'}</tbody></table></div>`)}
  </div>
  <div class="secao"><h2>As ${(f.candidatas||[]).length} melhores cidades sem unidade</h2>
    <div class="aux">entre os 5.570 municípios do IBGE · sem unidade na lista oficial</div></div>
  <div class="painel rolagem"><table><thead><tr><th class="n">#</th><th>cidade</th>
    <th class="n">população</th><th class="n">alvo 9–15</th><th class="n">alvo 30–45</th>
    <th class="n">renda</th><th class="n">score</th><th class="n">comporta</th></tr></thead>
    <tbody>${cands}</tbody></table></div>
  ${naove(f.o_que_isso_nao_ve)}`;
};

TELAS.radar = function(){
  const r = D.radar||{};
  const ops = (r.oportunidades||[]).map(o =>
    `<div class="painel" style="margin-bottom:12px"><div class="p-cab">
     <h2>${esc(o.rotulo)}</h2><span class="aux">${fmt(o.populacao)} habitantes</span></div>
     <div class="p-corpo">
       <div style="display:flex;gap:26px;flex-wrap:wrap;align-items:baseline;margin-bottom:8px">
       <div><span class="num" style="font-size:26px;color:var(--navy)">${fmt(o.alvo_9_15)}</span>
         <div class="aux">alvo 9–15</div></div>
       <div><span class="num" style="font-size:26px;color:var(--navy)">${fmt(o.alvo_30_45)}</span>
         <div class="aux">alvo 30–45</div></div>
       <div><span class="num" style="font-size:26px;color:var(--navy)">${fmt(o.clinicas_fortes)}</span>
         <div class="aux">clínicas fortes</div></div>
       <div><span class="num" style="font-size:26px;color:var(--navy)">${fmt(o.hab_por_clinica_forte)}</span>
         <div class="aux">hab por clínica forte</div></div></div>
       <p style="max-width:80ch;margin:0">${esc(o.leitura||"")}</p></div></div>`).join("");
  return `<div class="aviso">Estudo de expansão: estas cidades NÃO têm unidade e não entram
    em nenhuma conta da rede.</div>${ops}
    ${naove(r.ressalvas)}`;
};

TELAS.arquivo = function(){
  const cards = (D.franqueadora.cards||[]).filter(c=>c.grupo==="arquivo");
  const linhas = cards.map(c =>
    `<tr class="${c.disponivel?"":"apagado"}"><td><b>${esc(c.titulo)}</b>
     <div class="aux">${esc(c.pergunta)}</div></td>
     <td class="n">${c.numero==null?"—":fmt(c.numero)}</td>
     <td style="max-width:46ch">${esc(c.frase)}
     ${c.indisponivel_porque?`<div class="aux">apagada: ${esc(c.indisponivel_porque)}</div>`:""}</td></tr>`).join("");
  return `<p class="aux" style="max-width:70ch">De onde vem cada número. As telas do arquivo
    abrem no build completo; ferramenta apagada aparece com o motivo — esconder o que falta
    é proibido.</p>
    <div class="painel rolagem" style="margin-top:12px"><table>
    <thead><tr><th>ferramenta</th><th class="n">número</th><th>o que diz</th></tr></thead>
    <tbody>${linhas}</tbody></table></div>`;
};

/* ---------------- roteador ---------------- */
function rota(){
  const h = location.hash.replace(/^#\/?/,"") || "hoje";
  const [id, qs] = h.split("?");
  const q = {}; (qs||"").split("&").forEach(kv => {
    const [k,v] = kv.split("="); if(k) q[k] = decodeURIComponent(v||"");
  });
  const tela = TELAS[id] ? id : "hoje";
  desenhaNav(tela);
  document.getElementById("titulo").textContent = TIT[tela]||"";
  const el = document.getElementById("tela");
  el.innerHTML = TELAS[tela](q);
  if(TELAS[tela].depois) TELAS[tela].depois(el);
  window.scrollTo(0,0);
}
window.addEventListener("hashchange", rota);

const fr = D.franqueadora;
document.getElementById("corte").textContent = "corte " + (fr.corte||"");
document.getElementById("cobertura").textContent = (fr.cobertura||{}).aviso||"";
document.getElementById("rodape").textContent =
  "Feito só com informação pública — Google, Instagram, anúncios, imprensa, " +
  "Reclame Aqui, IBGE. Nenhum dado interno da rede entra aqui.";
rota();
})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
