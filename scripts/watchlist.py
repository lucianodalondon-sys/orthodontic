#!/usr/bin/env python3
"""
watchlist.py — os rivais que valem ser medidos toda semana.

O PROBLEMA DAS DUAS VELOCIDADES. A varredura da categoria devolve o
mercado inteiro da cidade e custa caro — e, pior, **não devolve o mesmo
universo duas vezes**: em Cuiabá só 53% das clínicas apareceram nas duas
rodadas. Comparar conjuntos instáveis produz "concorrente abriu" e
"concorrente sumiu" que são variação da própria coleta.

Então a varredura completa passa a ter uma função só: **descobrir**. Ela
roda por mês, encontra entrante, atualiza o mapa e reconstrói esta lista.

E o acompanhamento semanal passa a ser feito sobre uma lista ESTÁVEL,
chaveada por `place_id`, que não depende de o Google devolver a mesma
resposta. Medindo os mesmos 10–20 por semana, o sistema consegue dizer com
confiança: este rival tinha 583 avaliações, agora tem 604, e a nota mudou.

QUEM ENTRA, E POR QUÊ

  1. quem DISPUTA APARELHO — carimbado em `produto.disputa_aparelho`.
     Odontologia não é ortodontia: clínica geral e rede de implante
     dividem a rua, não o paciente.
  2. nossas próprias unidades — sempre, todas.
  3. entre os que disputam, os de maior volume de avaliação, até o teto.

Quem tem volume mas não disputa aparelho fica de fora e **aparece
declarado** na saída: esconder o descarte é o que faz alguém achar que a
lista é o mercado inteiro.

Uso:
    python3 scripts/watchlist.py
    python3 scripts/watchlist.py --salvar
    python3 scripts/watchlist.py --por-praca 20
"""
import argparse, json, pathlib, sys
import datetime as dt
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from cruzamento import jsonl, identidades, conta

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SAIDA = RAIZ/"dados"/"serie"/"watchlist.jsonl"
PORTAL = RAIZ/"dados"/"portal"/"watchlist.json"

TETO_PADRAO = 15        # por praça, além das nossas unidades
MIN_AVALIACOES = 20     # abaixo disso o delta semanal é ruído


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--por-praca", type=int, default=TETO_PADRAO)
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()

    ident = identidades(com_unidade=False)
    cat = jsonl("categoria")
    if not cat:
        print("  ✗ FALHA: categoria.jsonl vazio")
        sys.exit(1)

    # a última medição DE CADA praça — nunca a última data do arquivo
    corte = {}
    for r in cat:
        p = r.get("praca_id")
        corte[p] = max(corte.get(p, ""), r.get("snapshot_date") or "")
    ult = {}
    for r in cat:
        if r["snapshot_date"] != corte.get(r.get("praca_id")):
            continue
        pid = r.get("place_id")
        if pid:
            ult[(r["praca_id"], pid)] = r

    hoje = dt.date.today().isoformat()
    linhas, resumo = [], []
    for p, pr in sorted(ident.items()):
        nossos = {l.get("place_id"): l for l in pr.get("locais", [])
                  if l.get("papel") == "proprio" and l.get("place_id")}
        disputam = {l.get("place_id") for l in pr.get("locais", [])
                    if (l.get("produto") or {}).get("disputa_aparelho") == "sim"
                    and l.get("place_id")}
        da_praca = [r for (pp, pid), r in ult.items() if pp == p]
        if not da_praca:
            continue

        candidatos = [r for r in da_praca
                      if r["place_id"] in disputam
                      and (r.get("avaliacoes") or 0) >= MIN_AVALIACOES
                      and r["place_id"] not in nossos]
        candidatos.sort(key=lambda r: -(r.get("avaliacoes") or 0))
        escolhidos = candidatos[:a.por_praca]

        # o que ficou de fora, e por quê — declarado, nunca escondido
        fora_volume = [r for r in da_praca
                       if r["place_id"] not in disputam
                       and r["place_id"] not in nossos
                       and (r.get("avaliacoes") or 0)
                       >= (escolhidos[-1].get("avaliacoes") if escolhidos else 0)]
        cortados = candidatos[a.por_praca:]

        for pid, l in nossos.items():
            linhas.append({
                "snapshot_date": hoje, "praca_id": p, "place_id": pid,
                "nome": l.get("unidade") or l.get("nome"),
                "papel": "proprio", "disputa_aparelho": True,
                "avaliacoes_na_entrada": (ult.get((p, pid)) or {}).get("avaliacoes"),
                "porque": "unidade da rede — acompanhada sempre",
            })
        for r in escolhidos:
            linhas.append({
                "snapshot_date": hoje, "praca_id": p, "place_id": r["place_id"],
                "nome": r.get("nome"), "papel": "rival",
                "disputa_aparelho": True,
                "avaliacoes_na_entrada": r.get("avaliacoes"),
                "nota_na_entrada": r.get("nota"),
                "porque": "disputa aparelho e está entre os maiores da praça",
            })
        resumo.append({
            "praca_id": p, "rotulo": pr.get("rotulo") or p,
            "nossas": len(nossos), "rivais": len(escolhidos),
            "medidas_na_praca": len(da_praca),
            "disputam_aparelho": len(disputam),
            "cortados_por_teto": [
                {"nome": r.get("nome"), "avaliacoes": r.get("avaliacoes")}
                for r in cortados[:5]],
            "fora_por_nao_disputar": [
                {"nome": r.get("nome"), "avaliacoes": r.get("avaliacoes")}
                for r in sorted(fora_volume,
                                key=lambda r: -(r.get("avaliacoes") or 0))[:5]],
            "porque_fora": ("odontologia não é ortodontia: clínica geral, "
                            "implante e universidade dividem a rua, não o "
                            "paciente de aparelho"),
        })

    n_riv = sum(x["rivais"] for x in resumo)
    n_nos = sum(x["nossas"] for x in resumo)
    print(f"  {conta(len(linhas), 'ficha na watchlist', 'fichas na watchlist')}"
          f" — {n_nos} nossas e {n_riv} rivais, em "
          f"{conta(len(resumo), 'praça')}\n")
    print(f"  {'praça':<24}{'nossas':>7}{'rivais':>7}{'medidas':>9}   "
          f"maior descarte por não disputar aparelho")
    for x in sorted(resumo, key=lambda x: -x["rivais"]):
        f = (x["fora_por_nao_disputar"] or [{}])[0]
        print(f"  {x['rotulo'][:23]:<24}{x['nossas']:>7}{x['rivais']:>7}"
              f"{x['medidas_na_praca']:>9}   "
              + (f"{str(f.get('nome'))[:30]} ({f.get('avaliacoes')})"
                 if f.get("nome") else "—"))

    if not a.salvar:
        print("\n  (--salvar para gravar)")
        return
    with SAIDA.open("a", encoding="utf-8") as fh:
        for r in linhas:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    PORTAL.write_text(json.dumps({
        "o_que_e": "Os concorrentes que disputam APARELHO e são medidos toda "
                   "semana por place_id, mais as unidades da rede.",
        "por_que_existe": "a varredura completa da categoria não devolve o "
                          "mesmo universo duas vezes — em Cuiabá só 53% das "
                          "clínicas apareceram nas duas rodadas — e comparar "
                          "conjunto instável inventa entrada e saída de "
                          "concorrente",
        "o_que_nao_e": "não é o mercado inteiro da cidade: é a lista estável "
                       "que dá para acompanhar de semana em semana, e o que "
                       "ficou de fora está declarado ao lado",
        # O TETO DA LISTA NÃO É O TETO POR PRAÇA — É QUEM FOI CARIMBADO.
        #
        # Só entra clínica que tem `produto.disputa_aparelho` na identidade,
        # e a identidade guarda ~15 concorrentes por praça enquanto a
        # varredura mediu ~140. Ou seja: a watchlist escolhe entre 355
        # clínicas classificadas, não entre as 3.206 medidas. Uma clínica
        # grande que dispute aparelho e nunca tenha entrado na identidade
        # fica fora sem aparecer em lugar nenhum — e é por isso que este
        # campo existe.
        "o_teto_de_verdade": {
            "candidatas_classificadas": 355,
            "clinicas_medidas": 3206,
            "porque": ("`produto_do_concorrente.py` carimba os concorrentes "
                       "que estão na identidade da praça, e a identidade "
                       "não tem as 140 clínicas da varredura"),
            "o_que_aumentaria": ("classificar por produto as clínicas de "
                                 "`categoria.jsonl` que ainda não estão na "
                                 "identidade, começando pelas de maior "
                                 "volume"),
        },
        "as_duas_velocidades": {
            "descobrir": "varredura completa da categoria, mensal — acha "
                         "entrante e reconstrói esta lista",
            "acompanhar": "esta watchlist, semanal, por place_id",
        },
        "medido_em": hoje, "teto_por_praca": a.por_praca,
        "minimo_de_avaliacoes": MIN_AVALIACOES,
        "fichas_total": len(linhas), "nossas": n_nos, "rivais": n_riv,
        "pracas": resumo,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n  → dados/serie/watchlist.jsonl +{len(linhas)}")
    print(f"  → {PORTAL.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
