#!/usr/bin/env python3
"""
comparador_de_lojas.py — os GÊMEOS da rede: quem é comparável com quem, e
o que separa os dois.

A pergunta
----------
"Sua loja está amarela" não ensina nada ao franqueado. O que ensina é:

    existe uma unidade da rede com cidade parecida, concorrência parecida
    e tamanho parecido — e ela cresce mais que a sua. Estas são as
    diferenças que dá para ver de fora.

Isso é comparação entre PARES, e é a única forma honesta de comparar numa
rede em que uma loja de São Paulo e uma de Mafra não jogam o mesmo jogo.

Como o gêmeo é escolhido
------------------------
Por semelhança de MERCADO, não de resultado — senão a conta vira circular
("as que crescem parecem com as que crescem"). Quatro eixos:

    tamanho da cidade      população do município (IBGE)
    público adulto         proporção de 30 a 45 anos
    densidade da categoria  clínicas medidas naquela praça
    idade da própria loja   meses desde a PRIMEIRA avaliação da ficha

Cada eixo entra normalizado, e a distância é a soma das diferenças
relativas. A loja mais próxima é o gêmeo; a tela mostra os três mais
próximos, com a distância declarada.

O que este arquivo NÃO faz
--------------------------
Não diz por que um cresce mais que o outro. Ele lista DIFERENÇAS
OBSERVÁVEIS — presença na busca, ritmo, respostas, citação de
profissional — e para aí. Correlação entre duas lojas não é causa, e com
45 unidades medidas nenhuma diferença isolada tem força estatística.
Quem transforma isso em explicação é a visita do consultor, não o script.

Uso:
    python3 scripts/comparador_de_lojas.py
    python3 scripts/comparador_de_lojas.py --loja ortho_joi_america
    python3 scripts/comparador_de_lojas.py --salvar
"""
import argparse, datetime as dt, json, pathlib, sys
from collections import defaultdict

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ/"scripts"))
from cruzamento import coleta, identidades, reviews_unicos, conta, confianca

PORTAL = RAIZ/"dados"/"portal"

QUANTOS_GEMEOS = 3

# Diferença abaixo disto é ruído de medição, não achado. Sem esta trava a
# tela publicaria "ele ganha 3,1 e você 3,0" como se fosse uma lição.
MIN_RITMO = 1.5          # razão entre ritmos
MIN_PONTOS = 2           # diferença em pontos de busca
MIN_PCT = 10             # diferença em pontos percentuais


def carrega(nome):
    p = PORTAL/f"{nome}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def faixa_adulta(ib):
    """Proporção de 30 a 45 anos. É o público que o achado 22/22 diz que
    ninguém está atendendo — e é uma das faces do mercado."""
    fx = ((ib or {}).get("idades") or {}).get("por_faixa") or {}
    def n(k):
        try:
            return float(str(fx.get(k, 0)).replace(".", "")) if fx.get(k) else 0
        except ValueError:
            return 0
    tot = sum(n(k) for k in fx) or 0
    adulto = sum(n(k) for k in fx if k in ("30a34", "35a39", "40a44",
                                           "30a39", "40a49"))
    return (adulto/tot) if tot else None


def populacao(ib):
    try:
        return float(((ib or {}).get("populacao_estimada") or {}).get("valor"))
    except (TypeError, ValueError):
        return None


def monta():
    ident, linhas = coleta()
    nossas = [x for x in linhas if x["papel"] == "proprio"
              and x["ritmo"] is not None]

    ib_por_praca = {}
    for p, d in ident.items():
        ib = (d.get("ibge") or [{}])[0]
        ib_por_praca[p] = {"populacao": populacao(ib),
                           "adulto": faixa_adulta(ib)}

    presenca = {x["local_id"]: x for x in carrega("presenca_por_loja")
                .get("lojas", [])}
    perto = {x["local_id"]: x for x in carrega("perto_da_loja").get("lojas", [])}
    caixa = {x["local_id"]: x for x in carrega("caixa_de_respostas")
             .get("unidades", [])}
    # a dor dominante da loja: o estágio medido com maior proporção de
    # dor, entre os que têm amostra. A jornada guarda por estágio, não
    # pronto — e "atendimento" não é um problema: recepção, cadeira e
    # telefone são três, de três donos diferentes.
    jornada = {}
    for x in carrega("jornada").get("lojas", []):
        doi = [e for e in x.get("estagios", [])
               if e.get("medido") and not e.get("amostra_curta")
               and e.get("pct_dor") is not None]
        doi.sort(key=lambda e: -e["pct_dor"])
        jornada[x.get("local_id")] = {
            "momento_que_mais_doi": doi[0]["rotulo"] if doi else None,
            "pct_dor": doi[0]["pct_dor"] if doi else None,
            "quem_resolve": doi[0]["quem_resolve"] if doi else None,
        }

    # IDADE DA LOJA É DESDE A PRIMEIRA AVALIAÇÃO, NÃO "MESES COM
    # MOVIMENTO". A primeira versão usou `meses`, que é quantos meses a
    # loja teve movimento acima do próprio típico — ou seja, RESULTADO. Um
    # eixo de resultado dentro da escolha do gêmeo torna a conta circular,
    # que é exatamente o que este arquivo diz não fazer.
    primeira = {}
    for r in reviews_unicos():
        if not r.get("data"):
            continue
        lid, d10 = r.get("local_id"), str(r["data"])[:10]
        if lid not in primeira or d10 < primeira[lid]:
            primeira[lid] = d10

    # quanto das avaliações de cada loja cita um profissional pelo nome —
    # é o eixo em que a rede perde para o rival em 5 de 5 comparações
    import re
    RX_NOME = re.compile(r"\bdr[a]?\.?\s+[a-z]|doutor|doutora", re.I)
    com_nome, com_texto = defaultdict(int), defaultdict(int)
    for r in reviews_unicos():
        t = (r.get("texto") or "").strip()
        if not t:
            continue
        lid = r.get("local_id")
        com_texto[lid] += 1
        if RX_NOME.search(t):
            com_nome[lid] += 1

    perfil = {}
    for u in nossas:
        lid = u["local_id"]
        pr = ib_por_praca.get(u["praca"]) or {}
        pz = presenca.get(lid) or {}
        pt = perto.get(lid) or {}
        cx = caixa.get(lid) or {}
        n_txt = com_texto.get(lid, 0)
        perfil[lid] = {
            "local_id": lid, "praca_id": u["praca"], "rotulo": u["rotulo"],
            "unidade": u["nome"],
            # --- o mercado (é isto que escolhe o gêmeo)
            "populacao": pr.get("populacao"),
            "adulto_30_45": pr.get("adulto"),
            "clinicas_na_praca": u.get("medidas_na_praca"),
            "meses_de_loja": (
                (dt.date.today() - dt.date.fromisoformat(primeira[lid])).days//30
                if primeira.get(lid) else None),
            # --- o que dá para observar (é isto que a tela compara)
            "ritmo": u["ritmo"],
            "nota": u.get("nota"),
            "avaliacoes": u.get("total"),
            "ritmo_comparavel": u.get("ritmo_comparavel"),
            "busca_cidade": pz.get("aparece_em"),
            "busca_cidade_de": pz.get("de"),
            "busca_perto": pt.get("aparece_em"),
            "busca_perto_de": pt.get("de"),
            "avaliacoes_abertas": cx.get("abertas"),
            "ja_respondidas": cx.get("ja_respondidas"),
            "pct_respondidas": (
                round(100*cx["ja_respondidas"]
                      / (cx["ja_respondidas"] + cx["abertas"]), 1)
                if cx.get("ja_respondidas") is not None
                and (cx.get("ja_respondidas") or 0) + (cx.get("abertas") or 0)
                else None),
            "pct_com_nome": (round(100*com_nome.get(lid, 0)/n_txt, 1)
                             if n_txt >= 30 else None),
            "avaliacoes_com_texto": n_txt,
            "dor_dominante": (jornada.get(lid) or {}).get("momento_que_mais_doi"),
        }

    # ---------------------------------------------------------- a distância
    def eixo(a, b, campo):
        va, vb = a.get(campo), b.get(campo)
        if va is None or vb is None or not max(va, vb):
            return None
        return abs(va - vb)/max(va, vb)

    EIXOS = ("populacao", "adulto_30_45", "clinicas_na_praca", "meses_de_loja")
    saida = []
    for lid, a in perfil.items():
        cand = []
        for outro, b in perfil.items():
            if outro == lid:
                continue
            ds = [eixo(a, b, c) for c in EIXOS]
            usados = [d for d in ds if d is not None]
            if len(usados) < 3:            # sem eixo suficiente não compara
                continue
            cand.append((sum(usados)/len(usados), len(usados), b))
        cand.sort(key=lambda x: x[0])
        gemeos = []
        for dist, n_eixos, b in cand[:QUANTOS_GEMEOS]:
            gemeos.append({
                "local_id": b["local_id"], "rotulo": b["rotulo"],
                "unidade": b["unidade"],
                "distancia": round(dist, 3),
                "eixos_usados": n_eixos, "eixos_possiveis": len(EIXOS),
                "mesma_cidade": b["praca_id"] == a["praca_id"],
                "porque": _porque(a, b),
                "diferencas": _diferencas(a, b),
                "quem_cresce_mais": (
                    b["local_id"] if (b["ritmo"] or 0) > (a["ritmo"] or 0)
                    else a["local_id"]),
            })
        if not gemeos:
            continue
        g0 = gemeos[0]
        saida.append({
            **{k: a[k] for k in ("local_id", "praca_id", "rotulo", "unidade")},
            "perfil": a,
            "gemeos": gemeos,
            "frase": (f"o mercado mais parecido com o desta unidade é "
                      f"{g0['rotulo']}"
                      + (f" · {g0['unidade'].replace('OrthoDontic', '').strip(' ·')}"
                         if g0["unidade"] else "")),
            "carimbo": confianca(
                natureza="inferencia",
                amostra=len(perfil), unidade_amostra=("loja", "lojas"),
                a_favor=["a semelhança é medida sobre mercado (população, "
                         "público adulto, densidade da categoria e idade "
                         "da loja), não sobre resultado"],
                contra=["cidade parecida no papel não é mercado igual na "
                        "rua: ponto comercial, aluguel e equipe não são "
                        "medidos por nenhuma fonte pública"],
                o_que_aumentaria="medir mais unidades da rede — hoje só "
                                 "45 das 373 têm leitura completa"),
        })

    saida.sort(key=lambda x: x["rotulo"])
    return {
        "o_que_e": "A unidade da rede mais comparável com cada clínica — e "
                   "as diferenças que dá para ver de fora entre as duas.",
        "por_que_importa": ("comparar uma loja de São Paulo com uma de "
                            "Mafra não ensina nada. Comparar com quem "
                            "joga o mesmo jogo, sim"),
        "o_que_nao_e": ("não é causa. A tela lista diferenças observáveis; "
                        "dizer que uma delas explica o resultado é "
                        "trabalho da visita, não do dado"),
        "como_escolhe_o_gemeo": {
            "eixos": ["população do município (IBGE)",
                      "proporção de adultos de 30 a 45 anos",
                      "clínicas medidas na praça",
                      "meses desde a primeira avaliação da loja"],
            "porque_nao_usa_resultado": ("escolher o gêmeo por nota ou "
                                         "ritmo tornaria a conta circular: "
                                         "as que crescem pareceriam com as "
                                         "que crescem"),
            "minimo_de_eixos": 3,
        },
        "cortes": {"ritmo": MIN_RITMO, "pontos_de_busca": MIN_PONTOS,
                   "pontos_percentuais": MIN_PCT,
                   "porque": "diferença menor que isto é ruído de medição, "
                             "não lição"},
        "lojas_total": len(saida),
        "lojas": saida,
    }


def _porque(a, b):
    """A frase que justifica o par, com os números dos dois lados."""
    ps = []
    if a.get("populacao") and b.get("populacao"):
        ps.append(f"cidades de {a['populacao']/1000:.0f} mil e "
                  f"{b['populacao']/1000:.0f} mil habitantes")
    if a.get("clinicas_na_praca") and b.get("clinicas_na_praca"):
        ps.append(f"{a['clinicas_na_praca']} e {b['clinicas_na_praca']} "
                  f"clínicas medidas na praça")
    if a.get("meses_de_loja") is not None and b.get("meses_de_loja") is not None:
        ps.append(f"lojas com {a['meses_de_loja']} e {b['meses_de_loja']} "
                  f"meses desde a primeira avaliação")
    return " · ".join(ps)


def _diferencas(a, b):
    """O que separa as duas, só onde a diferença passa do ruído."""
    out = []

    def par(rotulo, va, vb, fmt="{:.1f}", sufixo=""):
        out.append({"o_que": rotulo,
                    "aqui": va, "la": vb,
                    "texto": (f"{fmt.format(va)}{sufixo} aqui contra "
                              f"{fmt.format(vb)}{sufixo} lá")})

    ra, rb = a.get("ritmo"), b.get("ritmo")
    if (ra and rb and a.get("ritmo_comparavel") and b.get("ritmo_comparavel")
            and max(ra, rb)/max(min(ra, rb), 0.1) >= MIN_RITMO):
        par("avaliações por mês", ra, rb, "{:.1f}")

    for campo, de, rotulo in (("busca_cidade", "busca_cidade_de",
                               "buscas da cidade em que aparece"),
                              ("busca_perto", "busca_perto_de",
                               "buscas perto da loja em que aparece")):
        va, vb = a.get(campo), b.get(campo)
        if va is not None and vb is not None and abs(va - vb) >= MIN_PONTOS:
            out.append({"o_que": rotulo, "aqui": va, "la": vb,
                        "texto": (f"{va} de {a.get(de)} aqui contra "
                                  f"{vb} de {b.get(de)} lá")})

    for campo, rotulo in (("pct_respondidas", "avaliações já respondidas"),
                          ("pct_com_nome",
                           "avaliações que citam um profissional pelo nome")):
        va, vb = a.get(campo), b.get(campo)
        if va is not None and vb is not None and abs(va - vb) >= MIN_PCT:
            par(rotulo, va, vb, "{:.0f}", "%")

    if (a.get("dor_dominante") and b.get("dor_dominante")
            and a["dor_dominante"] != b["dor_dominante"]):
        out.append({"o_que": "onde o paciente dói",
                    "aqui": a["dor_dominante"], "la": b["dor_dominante"],
                    "texto": f"{a['dor_dominante']} aqui, "
                             f"{b['dor_dominante']} lá"})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--loja")
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()
    d = monta()

    print(f"\n{'='*78}\n  OS GÊMEOS DA REDE — quem é comparável com quem"
          f"\n{'='*78}\n")
    for x in d["lojas"]:
        if a.loja and x["local_id"] != a.loja:
            continue
        g = x["gemeos"][0]
        print(f"  {x['rotulo']} · {x['unidade']}")
        print(f"     ≈ {g['rotulo']} · {g['unidade']}   "
              f"(distância {g['distancia']}, {g['eixos_usados']} de "
              f"{g['eixos_possiveis']} eixos)")
        print(f"       {g['porque']}")
        for df in g["diferencas"]:
            print(f"       · {df['o_que']}: {df['texto']}")
        if not g["diferencas"]:
            print("       · nenhuma diferença acima do corte — as duas "
                  "estão no mesmo lugar")
        print()

    if a.salvar:
        (PORTAL/"gemeos.json").write_text(
            json.dumps(d, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8")
        print(f"  → dados/portal/gemeos.json ({d['lojas_total']} lojas)")


if __name__ == "__main__":
    main()
