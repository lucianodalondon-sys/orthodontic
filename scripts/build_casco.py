#!/usr/bin/env python3
"""
build_casco.py — gera o portal: um arquivo só, dados dentro, marca dentro.

A arquitetura é a do PROJETO.md (seção 3):

  HOME               alertas das clínicas na frente + mapa do Brasil +
                     índice de ferramentas. Cabeçalho com o lockup
                     INTELLIGENCE do primeiro layout.
  PÁGINA DA CLÍNICA  o coração. Uma por unidade (local_id), no espírito
                     da apresentação de Mafra: quem ela é na cidade, o
                     que mudou entre coletas, a voz do paciente, as
                     negativas sem resposta, o rival de aparelho dela,
                     a linha do tempo e a tarefa aberta. É a futura
                     visão do franqueado.
  PÁGINA DA PRAÇA    o mercado da cidade: tese, placar, temas, citações.
  FERRAMENTAS        O que a rede ensina · Radar de cidades · A marca.

A composição da página da clínica acontece AQUI, em Python, juntando os
payloads por local_id — o casco (JS) só desenha. Nenhuma soma nova é
feita: todo número já vem pronto de dados/portal/*.json.

Uso:
    python3 scripts/build_casco.py        # → casco/index.html
"""
import base64, json, pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PORTAL = RAIZ/"dados"/"portal"
CASCO = RAIZ/"casco"


def carrega(nome):
    arq = PORTAL/f"{nome}.json"
    return json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else None


def b64(caminho):
    return base64.b64encode(caminho.read_bytes()).decode()


def compoe_clinicas():
    """A página da clínica, montada por local_id a partir dos payloads."""
    timeline = carrega("timeline") or {"lojas": []}
    caixa = carrega("caixa_de_respostas") or {"unidades": []}
    rival = carrega("rival") or {"pracas": []}
    mudou = carrega("o_que_mudou") or {"pracas": {}}
    fila = carrega("fila") or {"fila": []}

    caixa_por = {u.get("local_id"): u for u in caixa.get("unidades", [])}
    rival_por = {p.get("local_id"): p for p in rival.get("pracas", [])}
    fila_por = {x["local_id"]: x for x in fila.get("fila", [])}
    mudou_por = {}
    for pd in mudou.get("pracas", {}).values():
        for linha in pd.get("nossas", []):
            mudou_por[linha["local_id"]] = dict(linha,
                                                dias=pd.get("dias_medidos"),
                                                aviso=pd.get("aviso"))

    clinicas = []
    for l in timeline.get("lojas", []):
        lid = l["local_id"]
        cx = caixa_por.get(lid) or {}
        rv = rival_por.get(lid) or {}
        fl = fila_por.get(lid) or {}
        clinicas.append({
            "local_id": lid, "praca_id": l.get("praca_id"),
            "rotulo": l.get("rotulo"), "unidade": l.get("unidade"),
            "cabecalho": l.get("cabecalho"),
            "faixa": fl.get("faixa"), "urgencia": fl.get("urgencia"),
            "tarefa": fl.get("tarefa"), "acao": fl.get("acao"),
            "gatilhos": fl.get("gatilhos") or [],
            "quem_avanca": fl.get("quem_avanca"),
            "mudou": mudou_por.get(lid),
            "sem_resposta": {"abertas": cx.get("abertas"),
                             "com_texto": cx.get("com_texto"),
                             "itens": cx.get("itens") or []},
            "voz": rv.get("nosso_perfil"),
            "rival": {"comparados": rv.get("rivais_comparados") or [],
                      "vantagens": rv.get("vantagens_deles") or [],
                      "fora": rv.get("rivais_fora") or [],
                      "sem_comparacao": rv.get("sem_comparacao_porque")},
            "eventos": l.get("eventos") or [],
        })
    clinicas.sort(key=lambda c: (c["rotulo"] or "", c["local_id"]))
    return clinicas


def main():
    fr = carrega("franqueadora")
    manifest = carrega("manifest") or {}
    pracas = {}
    for p in (manifest.get("pracas") or []):
        d = carrega(f"pracas/{p['praca_id']}")
        if d:
            pracas[p["praca_id"]] = d

    dados = {
        "franqueadora": fr,
        "fila": carrega("fila"),
        "clinicas": compoe_clinicas(),
        "pracas": pracas,
        "padroes": carrega("padroes"),
        "rival_rede": (carrega("rival") or {}).get("padrao_da_rede"),
        # o rótulo de balcão de cada eixo da voz — a chave interna nunca
        # aparece na tela
        "eixos": {e["chave"]: e["o_que_e"]
                  for e in (carrega("rival") or {}).get("eixos", [])},
        "rede_inteira": carrega("rede_inteira"),
        "funil": carrega("funil_nacional"),
        "radar": carrega("radar"),
    }

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
    print(f"→ {out.relative_to(RAIZ)}  ({out.stat().st_size/1024:.0f} KB) · "
          f"{len(dados['clinicas'])} clínicas · {len(pracas)} praças")


# ================================================================ template
TEMPLATE = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OrthoDontic Intelligence</title>
<style>
/*__FONTES__*/
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
.miolo{max-width:1200px;margin:0 auto;padding:0 28px}

/* ---------- o cabeçalho INTELLIGENCE ---------- */
.hero{background:linear-gradient(160deg,var(--navy) 0%,var(--navy-2) 100%);
  color:#fff;position:relative;overflow:hidden}
.hero-aneis{position:absolute;right:-160px;top:-260px;width:640px;height:640px;
  pointer-events:none}
.hero-aneis circle{fill:none;stroke:rgba(0,185,255,.20);stroke-width:1}
.hero .miolo{position:relative;padding-top:26px;padding-bottom:26px}
.hero img{height:24px;width:auto;display:block}
.lockup{margin-top:10px;font-weight:300;font-size:clamp(30px,5vw,52px);
  letter-spacing:.26em;line-height:1.05;color:#fff}
.lockup b{font-weight:700;letter-spacing:.26em}
.hero .linha2{margin-top:6px;display:flex;gap:18px;flex-wrap:wrap;align-items:baseline}
.hero .sub{font-size:12px;letter-spacing:.14em;text-transform:uppercase;
  color:rgba(255,255,255,.62)}
.hero .corte{font-size:11.5px;color:rgba(255,255,255,.45);margin-left:auto}
.navbar{background:var(--painel);border-bottom:1px solid var(--linha);
  position:sticky;top:0;z-index:9}
.navbar .miolo{display:flex;gap:2px;overflow-x:auto}
.navbar a{padding:12px 14px;font-size:13px;color:var(--t2);white-space:nowrap;
  border-bottom:2px solid transparent}
.navbar a:hover{color:var(--t1)}
.navbar a.ativo{color:var(--navy);font-weight:500;border-bottom-color:var(--cyan)}
.cobertura{background:var(--lavagem);border-bottom:1px solid var(--linha);
  font-size:11.5px;color:var(--t2)}
.cobertura .miolo{padding:7px 28px}
.conteudo{padding:26px 0 70px}
.rodape{border-top:1px solid var(--linha);color:var(--t3);font-size:11.5px}
.rodape .miolo{padding:16px 28px}

/* ---------- peças ---------- */
.painel{background:var(--painel);border:1px solid var(--linha);border-radius:8px;
  box-shadow:var(--sombra)}
.p-cab{padding:12px 16px;border-bottom:1px solid var(--linha);display:flex;
  align-items:baseline;gap:10px;flex-wrap:wrap}
.p-cab h2{font-size:14px;font-weight:700}
.p-cab .aux{margin-left:auto}
.p-corpo{padding:14px 16px}
.aux{font-size:11.5px;color:var(--t3)}
.olho{font-size:10px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;
  color:var(--t3)}
.num{font-family:Gotham;font-weight:300;font-variant-numeric:tabular-nums}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}
th{font-size:10px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;
  color:var(--t3);text-align:left;padding:8px 10px;
  border-bottom:1px solid var(--linha-2);white-space:nowrap}
td{padding:9px 10px;border-bottom:1px solid var(--linha);vertical-align:top;
  font-size:13px}
tr:last-child td{border-bottom:none}
tr.clica{cursor:pointer}
tr.clica:hover td{background:var(--lavagem)}
td.n,th.n{text-align:right}
.rolagem{overflow-x:auto}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px;
  vertical-align:1px}
.dot.vermelha{background:var(--vermelha)}.dot.amarela{background:var(--amarela)}
.dot.verde{background:var(--verde)}.dot.cinza{background:var(--linha-2)}
.chip{display:inline-block;font-size:10.5px;font-weight:500;letter-spacing:.04em;
  padding:2px 8px;border-radius:99px;border:1px solid var(--linha-2);
  color:var(--t2);white-space:nowrap}
.chip.vencida{border-color:var(--vermelha);color:var(--vermelha)}
.chip.selo{border-color:var(--cyan);color:var(--cyan-ink)}
.aviso{background:#FFF8E8;border:1px solid #EAD9A8;border-radius:6px;
  padding:8px 12px;font-size:12px;color:#6b5410;margin:10px 0}
.naove{margin-top:26px;border-top:1px solid var(--linha);padding-top:12px}
.naove .olho{margin-bottom:6px;display:block}
.naove ul{margin:0;padding-left:18px}
.naove li{font-size:12px;color:var(--t3);margin:4px 0}
.apagado{opacity:.55}
details summary{cursor:pointer;font-size:12px;color:var(--t3)}
details[open] summary{margin-bottom:8px}
.secao{margin:28px 0 12px}
.secao h2{font-size:16px;font-weight:700}
.secao .aux{margin-top:2px}
.estrela{color:var(--amarela);letter-spacing:.06em}

/* ---------- home ---------- */
.grade-home{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,1fr);
  gap:18px;align-items:start}
.alerta-linha{display:block;padding:12px 16px;border-bottom:1px solid var(--linha);
  color:inherit;transition:background 150ms}
.alerta-linha:hover{background:var(--lavagem)}
.alerta-linha:last-child{border-bottom:none}
.alerta-linha .quem{font-size:13.5px;font-weight:500}
.alerta-linha .oq{font-size:12px;color:var(--t2);margin-top:2px}
.alerta-linha .meta{font-size:11px;color:var(--t3);margin-top:2px}
.mapa-svg path{fill:rgba(0,185,255,0);stroke:var(--linha-2);stroke-width:.8;
  transition:stroke 150ms}
.mapa-svg path:hover{stroke:var(--navy);stroke-width:1.4}
.mapa-legenda{display:flex;gap:14px;align-items:center;flex-wrap:wrap;
  padding:10px 16px;border-top:1px solid var(--linha);font-size:11px;
  color:var(--t3)}
.mapa-legenda .sw{display:inline-block;width:12px;height:12px;border-radius:2px;
  border:1px solid var(--linha-2);vertical-align:-2px;margin-right:5px}
.faixa-rede{display:flex;gap:34px;flex-wrap:wrap;align-items:baseline;
  padding:2px 0 18px}
.faixa-rede .num{font-size:40px;line-height:1;color:var(--navy)}
.faixa-rede .rot{font-size:11.5px;color:var(--t3);margin-top:4px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));
  gap:14px}
.card{display:block;background:var(--painel);border:1px solid var(--linha);
  border-radius:8px;padding:16px;color:inherit;box-shadow:var(--sombra);
  transition:border-color 150ms}
.card:hover{border-color:var(--cyan)}
.card .num{font-size:34px;line-height:1;color:var(--navy)}
.card .t{font-size:13px;font-weight:700;margin-top:6px}
.card .d{font-size:11.5px;color:var(--t3);margin-top:3px}

/* ---------- página da clínica ---------- */
.cab-clinica{display:flex;gap:30px;flex-wrap:wrap;align-items:baseline;
  padding:0 0 6px}
.cab-clinica .num{font-size:44px;color:var(--navy)}
.cab-clinica .rot{font-size:11px;color:var(--t3)}
.capitulo{margin:26px 0 12px;display:flex;align-items:baseline;gap:10px}
.capitulo h2{font-size:15px;font-weight:700}
.capitulo:before{content:"";width:18px;height:1px;background:var(--cyan);
  align-self:center}
.tl{list-style:none;margin:0;padding:0 0 0 6px;position:relative}
.tl:before{content:"";position:absolute;left:11px;top:6px;bottom:6px;width:1px;
  background:var(--linha-2)}
.tl li{position:relative;padding:0 0 15px 30px}
.tl .pt{position:absolute;left:7px;top:5px;width:9px;height:9px;border-radius:50%;
  background:#fff;border:2px solid var(--t3)}
.tl li.q-paciente .pt{border-color:var(--amarela)}
.tl li.q-rival .pt{border-color:var(--vermelha)}
.tl li.q-fila .pt{border-color:var(--navy)}
.tl li.q-nossa .pt{border-color:var(--cyan)}
.tl .quando{font-size:11px;color:var(--t3);font-variant-numeric:tabular-nums}
.tl .rotq{font-size:10px;font-weight:700;letter-spacing:.1em;
  text-transform:uppercase;margin-left:8px;color:var(--t3)}
.tl .oq{font-size:13px;margin-top:1px}
.acao-caixa{border-left:3px solid var(--cyan);padding:10px 14px;background:#fff;
  border:1px solid var(--linha);border-left-width:3px;border-radius:0 8px 8px 0}
.barra{height:5px;background:var(--lavagem);border-radius:3px;position:relative;
  min-width:90px;display:inline-block;width:120px;vertical-align:2px}
.barra i{position:absolute;left:0;top:0;bottom:0;background:var(--cyan);
  border-radius:3px}
.hip{border:1px solid var(--linha);border-radius:8px;padding:14px 16px;
  background:#fff}
.hip .veredito{font-size:19px;font-weight:700;color:var(--vermelha);margin:6px 0}
.grade-hip{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));
  gap:12px;margin-bottom:18px}
.conclusao{border-left:3px solid var(--cyan);background:#fff;
  border-radius:0 8px 8px 0;padding:14px 18px;margin:6px 0 18px;
  border-top:1px solid var(--linha);border-right:1px solid var(--linha);
  border-bottom:1px solid var(--linha)}
.cita{border-left:2px solid var(--linha-2);padding:6px 14px;margin:10px 0;
  font-size:13px;color:var(--t2)}
.cita .de{font-size:11px;color:var(--t3);margin-top:3px}
.duas{display:grid;grid-template-columns:1fr 1fr;gap:18px;align-items:start}
@media (max-width:900px){.grade-home,.duas{grid-template-columns:1fr}}
</style>
</head>
<body>

<header class="hero">
  <svg class="hero-aneis" viewBox="0 0 640 640" aria-hidden="true">
    <circle cx="320" cy="320" r="150"/><circle cx="320" cy="320" r="220"/>
    <circle cx="320" cy="320" r="290"/>
  </svg>
  <div class="miolo">
    <img src="__LOGO__" alt="OrthoDontic">
    <div class="lockup">INTELLIGENCE</div>
    <div class="linha2">
      <span class="sub">o mercado visto de fora</span>
      <span class="corte" id="corte"></span>
    </div>
  </div>
</header>
<nav class="navbar"><div class="miolo" id="nav"></div></nav>
<div class="cobertura"><div class="miolo" id="cobertura"></div></div>
<main class="conteudo"><div class="miolo" id="tela"></div></main>
<footer class="rodape"><div class="miolo">Feito só com informação pública —
Google, Instagram, anúncios, imprensa, Reclame Aqui, IBGE. Nenhum dado
interno da rede entra aqui.</div></footer>

<script>
/*__BRASIL__*/
/*__DADOS__*/
(function(){
"use strict";
const D = window.DADOS;
const fmt = n => n==null ? "—" : Number(n).toLocaleString("pt-BR");
const esc = s => String(s==null?"":s).replace(/[&<>"]/g,
  c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const cardPor = ch => (D.franqueadora.cards||[]).find(c=>c.chave===ch)||{};
const dotFaixa = f => `<span class="dot ${esc(f||"cinza")}"></span>`;
const estrelas = n => `<span class="estrela">${"★".repeat(n||0)}${"☆".repeat(Math.max(5-(n||0),0))}</span>`;
const chipTarefa = t => !t ? "" :
  `<span class="chip ${t.status}">${t.status==="vencida"?"vencida":"aberta"}${
   t.vence_em?" · vence "+t.vence_em.slice(5).split("-").reverse().join("/"):""}</span>`;
const naove = l => (l&&l.length)?`<div class="naove"><span class="olho">O que
  isto não vê</span><ul>${l.map(x=>`<li>${esc(x)}</li>`).join("")}</ul></div>`:"";
const painel = (cab,corpo,aux) => `<section class="painel"><div class="p-cab">
  <h2>${cab}</h2>${aux?`<span class="aux">${aux}</span>`:""}</div>${corpo}</section>`;

/* ---------------- navegação ---------------- */
const NAV = [["/", "Início"], ["/clinicas", "As clínicas"],
  ["/pracas", "As praças"], ["/ensina", "O que a rede ensina"],
  ["/radar", "Radar de cidades"], ["/marca", "A marca"],
  ["/arquivo", "Arquivo"]];
function desenhaNav(rota){
  document.getElementById("nav").innerHTML = NAV.map(([r,t]) =>
    `<a href="#${r}" class="${(r==="/"?rota==="/":rota.startsWith(r))?"ativo":""}">${t}</a>`).join("");
}

/* ---------------- mapa ---------------- */
function svgMapa(){
  const porUf = {}; (D.franqueadora.mapa||[]).forEach(m=>porUf[m.uf]=m);
  const ufs = (window.BRASIL_UFS.ufs)||window.BRASIL_UFS;
  const alfa = u => !u?0 : u<5?.16 : u<15?.34 : u<40?.55 : .8;
  let p = "";
  for(const [uf,g] of Object.entries(ufs)){
    const m = porUf[uf]||{unidades:0};
    p += `<path d="${g.d}" style="fill:rgba(0,185,255,${alfa(m.unidades)})">
      <title>${uf} — ${fmt(m.unidades)} unidade(s) · ${fmt(m.abertas)} abertas ·
      ${fmt(m.cidades)} cidade(s)</title></path>`;
  }
  return `<svg class="mapa-svg" viewBox="0 0 560 588" role="img"
    aria-label="Mapa do Brasil por unidades"
    style="width:100%;height:auto;display:block;padding:12px">${p}</svg>`;
}
const legendaMapa = `<div class="mapa-legenda">
  <span><span class="sw" style="background:rgba(0,185,255,0)"></span>sem unidade — o vazio é a informação</span>
  <span><span class="sw" style="background:rgba(0,185,255,.16)"></span>1–4</span>
  <span><span class="sw" style="background:rgba(0,185,255,.34)"></span>5–14</span>
  <span><span class="sw" style="background:rgba(0,185,255,.55)"></span>15–39</span>
  <span><span class="sw" style="background:rgba(0,185,255,.8)"></span>40+</span></div>`;

/* ---------------- telas ---------------- */
const T = {};

T.home = function(){
  const r = D.franqueadora.rede;
  const alertas = ((D.fila||{}).fila||[]).map(x => {
    const g0 = (x.gatilhos||[])[0];
    return `<a class="alerta-linha" href="#/clinica/${esc(x.local_id)}">
      <div class="quem">${dotFaixa(x.faixa)}${esc(x.rotulo)}${
        x.unidade_curta?" · "+esc(x.unidade_curta):""}
        ${chipTarefa(x.tarefa)}</div>
      <div class="oq">${g0?esc(g0.titulo)+" — "+esc(g0.fato):"sem gatilho aberto"}</div>
      ${x.acao?`<div class="meta">→ ${esc(x.acao.o_que)} · ${esc(x.acao.prazo)}
        · ${esc(x.acao.dono)}</div>`:""}</a>`;
  }).join("");
  const ferramentas = [
    ["#/ensina", cardPor("padroes")],
    ["#/radar", cardPor("funil")],
    ["#/marca", cardPor("alertas")],
    ["#/pracas", cardPor("pracas")],
  ].filter(([,c])=>c.chave).map(([href,c]) =>
    `<a class="card" href="${href}"><span class="num">${c.numero==null?"—":fmt(c.numero)}</span>
     <div class="t">${esc(c.titulo)}</div><div class="d">${esc(c.frase)}</div></a>`).join("");
  return `
  <div class="faixa-rede">
    <div><span class="num">${fmt(r.unidades)}</span><div class="rot">unidades na lista oficial</div></div>
    <div><span class="num">${fmt(r.abertas)}</span><div class="rot">abertas</div></div>
    <div><span class="num">${fmt(r.em_implantacao)}</span><div class="rot">em implantação</div></div>
    <div><span class="num">${fmt(r.cidades)}</span><div class="rot">cidades</div></div>
    <div><span class="num">${r.ufs_sem_unidade.length}</span>
      <div class="rot">estados sem unidade (${r.ufs_sem_unidade.join(", ")})</div></div>
  </div>
  <div class="grade-home">
    ${painel("Alertas das clínicas",
      alertas||'<div class="p-corpo aux">nenhuma clínica com alerta</div>',
      "clique para abrir a página da clínica")}
    <div class="painel"><div class="p-cab"><h2>A rede no Brasil</h2>
      <span class="aux">fonte: ${esc(r.fonte)}</span></div>${svgMapa()}${legendaMapa}</div>
  </div>
  <div class="secao"><h2>Ferramentas</h2></div>
  <div class="cards">${ferramentas}</div>`;
};

T.clinicas = function(){
  const linhas = (D.clinicas||[]).map(c => {
    const cb = c.cabecalho||{};
    return `<tr class="clica" data-href="#/clinica/${esc(c.local_id)}">
      <td>${dotFaixa(c.faixa)}${esc(c.rotulo)}<div class="aux">${esc(c.unidade)}</div></td>
      <td class="n">${cb.nota??"—"}</td><td class="n">${fmt(cb.avaliacoes)}</td>
      <td class="n">${cb.ritmo??"—"}/mês</td>
      <td class="n">${cb.posicao?cb.posicao+"º de "+cb.de:"—"}</td>
      <td>${chipTarefa(c.tarefa)||'<span class="aux">sem tarefa</span>'}</td></tr>`;
  }).join("");
  return `<p class="aux" style="max-width:74ch">Uma página por unidade — cidade
    com mais de uma clínica tem uma página para cada, porque nem sempre é o
    mesmo dono. Esta é a visão que o franqueado terá da clínica dele.</p>
  <div class="painel rolagem" style="margin-top:12px"><table>
    <thead><tr><th>clínica</th><th class="n">nota</th><th class="n">avaliações</th>
    <th class="n">ritmo</th><th class="n">posição na cidade</th><th>tarefa</th></tr></thead>
    <tbody>${linhas}</tbody></table></div>`;
};

T.clinica = function(lid){
  const c = (D.clinicas||[]).find(x=>x.local_id===lid);
  if(!c) return `<p>Clínica não encontrada.</p>`;
  const cb = c.cabecalho||{};
  let h = `<p class="aux"><a href="#/clinicas">← todas as clínicas</a> ·
    mercado da cidade: <a href="#/praca/${esc(c.praca_id)}">${esc(c.rotulo)}</a></p>
  <div class="secao" style="margin-top:10px"><h2 style="font-size:22px">
    ${esc(c.rotulo)} · ${esc(c.unidade)}</h2></div>
  <div class="cab-clinica">
    <div><span class="num">${cb.nota??"—"}</span><div class="rot">nota no Google</div></div>
    <div><span class="num">${fmt(cb.avaliacoes)}</span><div class="rot">avaliações</div></div>
    <div><span class="num">${cb.ritmo??"—"}</span><div class="rot">novas/mês (vida)</div></div>
    <div><span class="num">${cb.posicao?cb.posicao+"º":"—"}</span>
      <div class="rot">de ${cb.de??"—"} clínicas medidas na cidade</div></div>
    <div>${chipTarefa(c.tarefa)||'<span class="aux">sem tarefa aberta</span>'}</div>
  </div>`;

  if(c.acao || (c.gatilhos&&c.gatilhos.length)){
    h += `<div class="capitulo"><h2>O que fazer agora</h2></div>`;
    h += (c.gatilhos||[]).map(g=>`<div style="font-size:13px;margin:4px 0">
      · ${esc(g.titulo)} — ${esc(g.fato)}
      <span class="aux">${esc(g.fonte)}</span></div>`).join("");
    if(c.quem_avanca) h += `<div style="font-size:13px;margin:4px 0"><b>quem
      avança:</b> ${esc(c.quem_avanca.nome)} — ${c.quem_avanca.ritmo}/mês há
      ${c.quem_avanca.meses} meses</div>`;
    if(c.acao) h += `<div class="acao-caixa" style="margin-top:10px">
      <b>${esc(c.acao.o_que)}</b><br><span class="aux">${esc(c.acao.prazo)} ·
      ${esc(c.acao.dono)} · ${esc(c.acao.custo)}</span></div>`;
  }

  const m = c.mudou;
  h += `<div class="capitulo"><h2>O que mudou entre as coletas</h2></div>`;
  if(m){
    h += `${m.aviso?`<div class="aviso">${esc(m.aviso)}</div>`:""}
    <div style="font-size:14px">${fmt(m.antes)} → <b>${fmt(m.agora)}</b>
    avaliações (${m.delta>0?"▲ +":m.delta<0?"▼ ":"· "}${m.delta<0?-m.delta:m.delta})
    em ${m.dias} dia(s)${m.nota_antes!==m.nota_agora?` · nota ${m.nota_antes} →
    ${m.nota_agora}`:""}</div>
    ${(m.eventos||[]).map(e=>`<div class="aux" style="margin-top:3px">· ${esc(e)}</div>`).join("")}`;
  } else {
    h += `<p class="aux">ainda só uma medição — a comparação nasce na próxima coleta</p>`;
  }

  if(c.voz){
    const EIXO = D.eixos||{};
    h += `<div class="capitulo"><h2>A voz do paciente desta clínica</h2>
      <span class="aux">% das avaliações com texto que tocam cada assunto</span></div>
    <div class="painel rolagem"><table><tbody>` +
    Object.entries(c.voz).map(([k,v])=>`<tr><td>${esc(EIXO[k]||k)}</td>
      <td><span class="barra"><i style="width:${Math.min(v,100)}%"></i></span></td>
      <td class="n">${v}%</td></tr>`).join("") + `</tbody></table></div>`;
  }

  const sr = c.sem_resposta||{};
  h += `<div class="capitulo"><h2>Avaliações esperando resposta</h2></div>`;
  if(sr.itens&&sr.itens.length){
    h += `<div class="aviso">${fmt(sr.abertas)} negativas sem resposta —
      responder é higiene de reputação.</div>` +
      sr.itens.map(i=>`<div class="painel" style="margin-bottom:8px"><div class="p-corpo">
      ${estrelas(i.nota)} <span class="aux">${esc(i.data||"sem data")}</span>
      <div style="margin-top:4px;max-width:80ch">${esc(i.texto||"(sem texto)")}</div>
      </div></div>`).join("");
  } else {
    h += `<p class="aux">nenhuma negativa sem resposta nesta clínica</p>`;
  }

  const rv = c.rival||{};
  h += `<div class="capitulo"><h2>O rival de aparelho desta clínica</h2>
    <span class="aux">só quem vende aparelho entra — clínica geral e implante
    são outro produto</span></div>`;
  if(rv.sem_comparacao){
    h += `<p class="aux">${esc(rv.sem_comparacao)}</p>`;
  } else if(rv.vantagens&&rv.vantagens.length){
    h += `<div class="painel rolagem"><table><thead><tr><th>onde perdemos</th>
      <th>para quem</th><th class="n">eles · nós</th><th class="n">razão</th></tr></thead>
      <tbody>`+rv.vantagens.map(v=>`<tr><td>${esc(v.o_que_e)}</td><td>${esc(v.quem)}</td>
      <td class="n">${v.eles}% · ${v.nos}%</td><td class="n">${v.razao}x</td></tr>`).join("")+
      `</tbody></table></div>`;
  } else if(rv.comparados&&rv.comparados.length){
    h += `<p class="aux">nenhuma vantagem acima do corte contra
      ${rv.comparados.map(esc).join(", ")} — a praça está equilibrada</p>`;
  }
  if(rv.fora&&rv.fora.length){
    h += `<div style="margin-top:8px"><details><summary>fora da comparação —
      outro produto (${rv.fora.length})</summary><ul>`+
      rv.fora.map(f=>`<li style="font-size:12.5px">${esc(f.nome)} —
      <span class="aux">${esc(f.por_que_fora)}</span></li>`).join("")+
      `</ul></details></div>`;
  }

  h += `<div class="capitulo"><h2>A linha do tempo</h2>
    <span class="aux">nossa · paciente · fila · rival</span></div>
  <ul class="tl">`+(c.eventos||[]).map(e=>`<li class="q-${esc(e.quem)}">
    <span class="pt"></span><span class="quando">${esc(e.data)}</span>
    <span class="rotq">${esc(e.quem)}</span>
    <div class="oq">${esc(e.texto)}</div></li>`).join("")+`</ul>`;
  return h;
};

T.pracas = function(){
  const linhas = Object.values(D.pracas||{}).map(p =>
    `<tr class="clica" data-href="#/praca/${esc(p.praca_id)}">
     <td>${esc(p.rotulo)}</td><td>${esc(p.tese_titulo||"")}</td>
     <td class="aux">${esc(p.base||"")}</td></tr>`).join("");
  return `<p class="aux" style="max-width:74ch">O mercado de cada cidade
    estudada a fundo — a tese, o placar da cidade, os temas da voz do
    paciente. Análise de mercado é por cidade; leitura de clínica é por
    clínica.</p>
  <div class="painel rolagem" style="margin-top:12px"><table>
    <thead><tr><th>praça</th><th>a tese</th><th>base</th></tr></thead>
    <tbody>${linhas}</tbody></table></div>`;
};

T.praca = function(pid){
  const p = (D.pracas||{})[pid];
  if(!p) return "<p>Praça não encontrada.</p>";
  const minhas = (D.clinicas||[]).filter(c=>c.praca_id===pid);
  let h = `<p class="aux"><a href="#/pracas">← todas as praças</a></p>
  <div class="secao" style="margin-top:10px"><h2 style="font-size:22px">${esc(p.rotulo)}</h2>
    <div class="aux">${esc(p.eyebrow||"")}</div></div>
  <div class="conclusao"><b>${esc(p.tese_titulo||"")}</b>
    <p style="margin:6px 0 0;max-width:78ch">${esc(p.tese||"")}</p>
    <div class="aux" style="margin-top:6px">${esc(p.base||"")}</div></div>`;
  if(minhas.length){
    h += `<div class="capitulo"><h2>Nossas clínicas nesta cidade</h2></div>`+
      minhas.map(c=>`<p style="margin:4px 0"><a href="#/clinica/${esc(c.local_id)}">
      ${dotFaixa(c.faixa)}${esc(c.unidade)}</a></p>`).join("");
  }
  const mud = p.o_que_mudou;
  if(mud){
    h += `<div class="capitulo"><h2>O que mudou na cidade</h2>
      <span class="aux">${mud.dias_medidos} dia(s) medidos</span></div>
      ${mud.aviso?`<div class="aviso">${esc(mud.aviso)}</div>`:""}`+
      [["nossas","nossas"],["quem_mais_ganhou","rivais de aparelho que mais ganharam"],
       ["contador_caiu","contador caiu — avaliação apagada"]].map(([k,t])=>{
        const ls=(mud[k]||[]).filter(x=>k!=="quem_mais_ganhou"||!x.proprio);
        return ls.length?`<div class="olho" style="margin:10px 0 4px">${t}</div>`+
          ls.map(x=>`<div style="font-size:13px;margin:2px 0">${esc(x.nome)} —
          ${fmt(x.antes)} → ${fmt(x.agora)} (${x.delta>0?"+":""}${x.delta})</div>`).join(""):"";
      }).join("");
  }
  if(p.placar&&p.placar.length){
    h += `<div class="capitulo"><h2>O placar da cidade</h2>
      <span class="aux">${esc(p.placar_nota||"")}</span></div>
    <div class="painel rolagem"><table><thead><tr><th>#</th><th>clínica</th>
      <th class="n">avaliações</th><th class="n">nota</th></tr></thead><tbody>`+
      p.placar.map((x,i)=>`<tr${x.proprio||x.nossa?' style="background:var(--lavagem);font-weight:500"':""}>
      <td class="n">${x.posicao??i+1}</td><td>${esc(x.nome)}</td>
      <td class="n">${fmt(x.avaliacoes??x.total)}</td><td class="n">${x.nota??"—"}</td>
      </tr>`).join("")+`</tbody></table></div>`;
  }
  if(p.citacoes&&p.citacoes.length){
    h += `<div class="capitulo"><h2>Na voz de quem vive a cidade</h2></div>`+
      p.citacoes.map(c=>`<div class="cita">"${esc(c.texto||c.t||c)}"`+
        ((c.de||c.fonte)?`<div class="de">— ${esc(c.de||c.fonte)}</div>`:"")+`</div>`).join("");
  }
  return h;
};

T.ensina = function(){
  const pz = D.padroes||{};
  const hips = (pz.hipoteses_testadas||[]).map(x=>`<div class="hip">
    <div class="aux">${esc(x.h)}</div><div class="veredito">${esc(x.veredito)}</div>
    <div style="font-size:12.5px">${esc(x.prova)}</div></div>`).join("");
  const c = pz.conclusao||{};
  const rede = (D.rival_rede||[]).map(e=>`<tr><td>${esc(e.o_que_e)}</td>
    <td><span class="barra"><i style="width:${Math.round(100*e.perde_em/e.de)}%"></i></span>
    <span class="aux"> perde em ${e.perde_em} de ${e.de} clínicas</span></td>
    <td class="n">até ${e.pior_razao}x</td></tr>`).join("");
  const lojas = (pz.lojas||[]).map(l=>`<tr><td>${esc(l.rotulo)}
    <div class="aux">${esc(l.unidade)}</div></td>
    <td class="n">${l.ritmo_vida??"—"}/mês</td>
    <td class="n">${l.meses_seguidos??"—"} meses</td>
    <td><span class="chip">${esc(l.selo||"")}</span></td></tr>`).join("");
  return `<p class="aux" style="max-width:74ch">O que as clínicas ensinam quando
    lidas juntas — o bom e o ruim. Padrão que se repete em muitas cidades é
    decisão de rede, não de clínica.</p>
  <div class="secao"><h2>As explicações que caíram no teste</h2>
    <div class="aux">o valor está no que NÃO separa quem cresce de quem parou</div></div>
  <div class="grade-hip">${hips}</div>
  <div class="conclusao"><b>${esc(c.t||"")}</b>
    <p style="margin:6px 0 0;max-width:78ch">${esc(c.leitura||"")}</p>
    <p style="margin:6px 0 0;max-width:78ch"><b>consequência:</b> ${esc(c.consequencia||"")}</p>
    <p class="aux" style="margin:6px 0 0">${esc(c.controle||"")}</p></div>
  <div class="secao"><h2>Onde a rede perde para o rival de aparelho</h2>
    <div class="aux">na voz do paciente deles — perder em muitas cidades vira
    treinamento e protocolo</div></div>
  <div class="painel rolagem"><table><tbody>${rede}</tbody></table></div>
  <div class="secao"><h2>Clínica a clínica</h2></div>
  <div class="painel rolagem"><table><thead><tr><th>clínica</th>
    <th class="n">ritmo</th><th class="n">constância</th><th>selo</th></tr></thead>
    <tbody>${lojas}</tbody></table></div>
  ${naove(pz.o_que_isso_nao_ve)}`;
};

T.radar = function(){
  const f = D.funil||{}, r = D.radar||{};
  const met = f.metodo||{};
  const cands = (f.candidatas||[]).map((c,i)=>`<tr><td class="n">${i+1}</td>
    <td>${esc(c.rotulo)}${c.ja_estudada?' <span class="chip selo">estudo pronto</span>':""}</td>
    <td class="n">${fmt(c.populacao)}</td><td class="n">${fmt(c.alvo_9_15)}</td>
    <td class="n">${fmt(c.alvo_30_45)}</td><td class="n">${c.renda_relativa}x</td>
    <td class="n">${fmt(c.score)}</td></tr>`).join("");
  const cabem = (f.onde_cabem_mais||[]).map(s=>`<tr><td>${esc(s.rotulo)}</td>
    <td class="n">${s.unidades_hoje}</td><td class="n">${s.comporta_pela_regua}</td>
    <td class="n" style="color:var(--cyan-ink);font-weight:500">+${s.folga}</td></tr>`).join("");
  const ops = (r.oportunidades||[]).map(o=>`<div class="painel" style="margin-bottom:12px">
    <div class="p-cab"><h2>${esc(o.rotulo)}</h2>
    <span class="aux">${fmt(o.populacao)} habitantes</span></div>
    <div class="p-corpo"><p style="margin:0;max-width:80ch">${esc(o.leitura||"")}</p>
    <div class="aux" style="margin-top:6px">${fmt(o.alvo_9_15)} no alvo 9–15 ·
    ${fmt(o.alvo_30_45)} no alvo 30–45 · ${fmt(o.clinicas_fortes)} clínica(s)
    forte(s) · 1 forte para ${fmt(o.hab_por_clinica_forte)} hab</div></div></div>`).join("");
  return `<div class="aviso">Estudo de expansão — nada aqui entra nas contas da
    rede. Score é régua de prioridade, não promessa de faturamento.</div>
  <div class="secao"><h2>As cidades já estudadas a fundo</h2>
    <div class="aux">o embrião do Dossiê da Cidade — o material do candidato a
    franqueado</div></div>
  ${ops}
  <div class="secao"><h2>O funil nacional</h2>
    <div class="aux">score = ${esc(met.score||"")}</div></div>
  <div class="duas">
    ${painel("A régua da própria rede", `<div class="rolagem"><table>
      <thead><tr><th>faixa de cidade</th><th class="n">hab por unidade</th>
      <th class="n">base</th></tr></thead><tbody>`+
      (met.regua_hab_por_unidade||[]).map(x=>`<tr><td>${esc(x.faixa)}</td>
      <td class="n">1 : ${fmt(x.mediana_hab_por_unidade)}</td>
      <td class="n">${x.cidades_da_rede_na_faixa} cidades</td></tr>`).join("")+
      `</tbody></table></div>`)}
    ${painel("Onde cabem mais — dentro de casa", `<div class="rolagem"><table>
      <thead><tr><th>cidade</th><th class="n">hoje</th><th class="n">comporta</th>
      <th class="n">folga</th></tr></thead><tbody>${cabem}</tbody></table></div>`)}
  </div>
  <div class="secao"><h2>As ${(f.candidatas||[]).length} melhores cidades sem
    unidade</h2></div>
  <div class="painel rolagem"><table><thead><tr><th class="n">#</th><th>cidade</th>
    <th class="n">população</th><th class="n">alvo 9–15</th><th class="n">alvo 30–45</th>
    <th class="n">renda</th><th class="n">score</th></tr></thead>
    <tbody>${cands}</tbody></table></div>
  ${naove(f.o_que_isso_nao_ve)}`;
};

T.marca = function(){
  const ri = D.rede_inteira||{};
  const reps = D.franqueadora.reputacao_das_redes||[];
  const alertas = (ri.alertas||[]).map(a=>`<tr>
    <td>${dotFaixa(a.gravidade)}${esc(a.unidade||a.nome_no_google)}
    <div class="aux">${esc(a.cidade)}/${esc(a.uf)}</div></td>
    <td>${esc(a.por_que)}</td>
    <td><span class="chip">${esc(a.de_quem_e||"—")}</span></td></tr>`).join("");
  const linhas = reps.map(r=>`<tr${r.nossa?' style="background:var(--lavagem);font-weight:500"':""}>
    <td>${esc(r.marca)}${r.nossa?' <span class="chip selo">nós</span>':""}</td>
    <td><span class="chip">${esc(r.foco||"")}</span></td>
    <td class="n">${fmt(r.reclamacoes)}</td><td class="n">${r.nota??"—"}</td>
    <td>${esc(r.selo||"")}</td></tr>`).join("");
  const fb = D.franqueadora.fichas_da_rede||{};
  return `<div class="secao" style="margin-top:0"><h2>Alertas nas 374 fichas</h2>
    <div class="aux">${fmt(ri.confirmadas)} de ${fmt(ri.na_lista_oficial)} fichas
    conferidas · nota mediana ${ri.nota_mediana}</div></div>
  <div class="painel rolagem"><table><thead><tr><th>unidade</th><th>por quê</th>
    <th>de quem é</th></tr></thead><tbody>${alertas}</tbody></table></div>
  <div class="secao"><h2>Rede contra rede, no Reclame Aqui</h2>
    <div class="aux">só ortodontia e odontologia popular entram na comparação</div></div>
  <div class="painel rolagem"><table><thead><tr><th>marca</th><th>foco</th>
    <th class="n">reclamações</th><th class="n">nota</th><th>selo</th></tr></thead>
    <tbody>${linhas}</tbody></table></div>
  <p class="aux" style="margin-top:10px">Cadastro: ${fmt(fb.conferidas)} fichas
    das nossas conferidas · ${fmt(fb.sem_site)} sem site.</p>
  ${naove([ri.o_que_nao_e])}`;
};

T.arquivo = function(){
  const cards = (D.franqueadora.cards||[]).filter(c=>c.grupo==="arquivo");
  return `<p class="aux" style="max-width:70ch">De onde vem cada número.
    Ferramenta apagada aparece com o motivo — esconder o que falta é proibido.</p>
  <div class="painel rolagem" style="margin-top:12px"><table>
    <thead><tr><th>ferramenta</th><th class="n">número</th><th>o que diz</th></tr></thead>
    <tbody>`+cards.map(c=>`<tr class="${c.disponivel?"":"apagado"}">
    <td><b>${esc(c.titulo)}</b><div class="aux">${esc(c.pergunta)}</div></td>
    <td class="n">${c.numero==null?"—":fmt(c.numero)}</td>
    <td style="max-width:46ch">${esc(c.frase)}${c.indisponivel_porque?
    `<div class="aux">apagada: ${esc(c.indisponivel_porque)}</div>`:""}</td></tr>`).join("")+
    `</tbody></table></div>`;
};

/* ---------------- roteador ---------------- */
function rota(){
  const h = location.hash.replace(/^#/,"") || "/";
  const el = document.getElementById("tela");
  let html;
  if(h==="/") html = T.home();
  else if(h==="/clinicas") html = T.clinicas();
  else if(h.startsWith("/clinica/")) html = T.clinica(decodeURIComponent(h.slice(9)));
  else if(h==="/pracas") html = T.pracas();
  else if(h.startsWith("/praca/")) html = T.praca(decodeURIComponent(h.slice(7)));
  else if(h==="/ensina") html = T.ensina();
  else if(h==="/radar") html = T.radar();
  else if(h==="/marca") html = T.marca();
  else if(h==="/arquivo") html = T.arquivo();
  else html = T.home();
  desenhaNav(h);
  el.innerHTML = html;
  el.querySelectorAll("tr[data-href]").forEach(tr =>
    tr.addEventListener("click", () => location.hash = tr.dataset.href));
  window.scrollTo(0,0);
}
window.addEventListener("hashchange", rota);

document.getElementById("corte").textContent =
  "corte " + (D.franqueadora.corte||"");
document.getElementById("cobertura").textContent =
  (D.franqueadora.cobertura||{}).aviso||"";
rota();
})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
