#!/usr/bin/env python3
"""
onde_cada_loja_aparece.py — a presença na busca POR LOJA, não por cidade.

A regra do projeto diz que a unidade é a menor conta e que loja não se
funde com loja. A captação, porém, era medida e escrita por CIDADE: "a
sua clínica aparece em 12 das 157 buscas". Em Cuiabá, onde há três lojas
que podem nem ser do mesmo dono, essa frase é verdadeira para uma e
mentira para as outras duas.

Dá para separar sem coletar nada de novo. O mapa do Google devolve, em
cada busca, o nome e o CONTADOR DE AVALIAÇÕES de quem apareceu — e o
contador é a impressão digital da loja: em Cuiabá as três OrthoDontic
têm 1.222, 78 e 71 avaliações. Casando o contador do resultado com o
contador da ficha, cada aparição vira de uma loja específica.

O que isso destrava, no primeiro dia: a loja Dom Bosco NÃO APARECE em
NENHUMA das 157 buscas de Cuiabá, enquanto o plano da cidade dizia a ela
que "a sua clínica aparece". A média da cidade escondia uma loja
invisível.

Uso:
    python3 scripts/onde_cada_loja_aparece.py
    python3 scripts/onde_cada_loja_aparece.py --salvar   # → dados/portal/presenca_por_loja.json
"""
import argparse, json, pathlib, sys
from collections import defaultdict

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ/"scripts"))
from cruzamento import jsonl, identidades, conta

PORTAL = RAIZ/"dados"/"portal"
# tolerância do casamento: a ficha e o mapa podem ter sido lidos em dias
# diferentes, e o contador anda. Acima disso não é a mesma loja.
FOLGA = 6


def nosso(nome):
    # `ortho` solto marca concorrente como nosso — a chave é `orthodontic`
    return "orthodontic" in (nome or "").lower().replace(" ", "").replace("-", "")


def monta():
    ident = identidades(com_unidade=True)
    places = jsonl("places")
    ult = {}
    for r in sorted(places, key=lambda r: r.get("snapshot_date", "")):
        ult[r["local_id"]] = r

    portas = jsonl("portas")
    # É A ÚLTIMA MEDIÇÃO DE CADA PRAÇA, NÃO A ÚLTIMA DO ARQUIVO. Cortar
    # pela data global apaga toda praça que não foi medida hoje: ao abrir
    # as cinco cidades novas, as dez lojas antigas sumiram da presença —
    # Mafra inclusa — e o portal passou a dizer "sem medição" para quem
    # tinha medição. É o mesmo defeito que a captação já teve, quando
    # escreveu só para 1 das 13 praças.
    por_praca = {}
    for r in portas:
        d = r.get("snapshot_date")
        p_ = r.get("praca_id")
        if d and (p_ not in por_praca or d > por_praca[p_]):
            por_praca[p_] = d
    portas = [r for r in portas
              if r.get("snapshot_date") == por_praca.get(r.get("praca_id"))]
    corte = max(por_praca.values(), default=None)
    por_praca = defaultdict(list)
    for r in portas:
        por_praca[r.get("praca_id")].append(r)

    saida, avisos = [], []
    for p, d in sorted(ident.items()):
        lojas = [l for l in d.get("locais", []) if l.get("papel") == "proprio"]
        if not lojas:
            continue
        frases = [r for r in por_praca.get(p, [])
                  if r.get("intencao") != "RUÍDO"]
        if not frases:
            continue

        # a impressão digital de cada loja: quantas avaliações a ficha tinha
        digital = {}
        for l in lojas:
            pl = ult.get(l["local_id"]) or {}
            if pl.get("avaliacoes_total") is not None:
                digital[l["local_id"]] = pl["avaliacoes_total"]

        onde = {l["local_id"]: [] for l in lojas}
        nao_casou = 0
        for r in frases:
            for q in (r.get("mapa") or {}).get("quem") or []:
                if not nosso(q.get("nome")):
                    continue
                av = q.get("avaliacoes")
                alvo, melhor = None, None
                for lid, n in digital.items():
                    if av is None:
                        continue
                    dist = abs(n - av)
                    if dist <= FOLGA and (melhor is None or dist < melhor):
                        alvo, melhor = lid, dist
                if alvo:
                    onde[alvo].append({"frase": r["frase"],
                                       "posicao": q.get("posicao"),
                                       "intencao": r.get("intencao")})
                else:
                    nao_casou += 1

        total = len(frases)
        for l in lojas:
            lid = l["local_id"]
            achadas = onde[lid]
            # a mesma frase pode aparecer duas vezes na varredura; a conta é
            # de FRASES distintas, não de linhas
            unicas = {a["frase"]: a for a in achadas}
            aparece = len(unicas)
            saida.append({
                "local_id": lid, "praca_id": p,
                "rotulo": d.get("rotulo"),
                "unidade": l.get("nome"),
                "avaliacoes_da_ficha": digital.get(lid),
                "aparece_em": aparece,
                "de": total,
                "pct": round(100*aparece/total) if total else None,
                "melhor_posicao": min((a["posicao"] for a in unicas.values()
                                       if a.get("posicao")), default=None),
                "frases_onde_aparece": sorted(unicas.values(),
                                              key=lambda a: (a["posicao"] or 99))[:20],
                "invisivel": aparece == 0,
                "frase_do_topo": (
                    f"Esta loja **não aparece em nenhuma** das "
                    f"{conta(total, 'busca')} que testamos na cidade."
                    if aparece == 0 else
                    f"Esta loja aparece em **{aparece} das {total} buscas** "
                    f"que testamos na cidade."),
            })
        if nao_casou:
            avisos.append({"praca_id": p, "rotulo": d.get("rotulo"),
                           "aparicoes_sem_dono": nao_casou,
                           "por_que": ("resultado com nome OrthoDontic cujo "
                                       "contador de avaliações não casa com "
                                       "nenhuma ficha da praça — pode ser loja "
                                       "fora da nossa lista, ou ficha lida em "
                                       "outro dia")})

    saida.sort(key=lambda x: (x["pct"] if x["pct"] is not None else 999))
    invisiveis = [x for x in saida if x["invisivel"]]
    return {
        "o_que_e": "Em quantas buscas da cidade CADA LOJA aparece no mapa do "
                   "Google — separado por unidade, porque loja não se funde "
                   "com loja.",
        "como_separa": "O mapa devolve o contador de avaliações de cada "
                       "resultado, e o contador é a impressão digital da loja. "
                       "Casando com a ficha, a aparição vira de uma unidade.",
        "o_que_nao_e": "Não é volume de busca. É em quantas das frases "
                       "testadas a loja apareceu no mapa.",
        "corte": corte,
        "lojas_medidas": len(saida),
        "lojas_invisiveis": len(invisiveis),
        "manchete": (f"{conta(len(invisiveis), 'loja não aparece', 'lojas não aparecem')} "
                     f"em nenhuma busca da própria cidade."
                     if invisiveis else
                     "Todas as lojas medidas aparecem em pelo menos uma busca."),
        "avisos": avisos,
        "lojas": saida,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()
    d = monta()
    print(f"\n{'=' * 84}\n  ONDE CADA LOJA APARECE — por unidade, não por cidade"
          f"\n{'=' * 84}\n")
    for x in d["lojas"]:
        marca = "  ← INVISÍVEL" if x["invisivel"] else ""
        print(f"  {(x['rotulo'] or ''):<26} {(x['unidade'] or '')[:30]:<32} "
              f"{x['aparece_em']:>3}/{x['de']:<4} "
              f"{str(x['pct']) + '%':>5}{marca}")
    print(f"\n  {d['manchete']}")
    for av in d["avisos"]:
        print(f"  aviso · {av['rotulo']}: "
              + conta(av["aparicoes_sem_dono"], "aparição sem dono",
                      "aparições sem dono")
              + f" ({av['por_que'][:60]}…)")
    if a.salvar:
        PORTAL.mkdir(parents=True, exist_ok=True)
        (PORTAL/"presenca_por_loja.json").write_text(
            json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n  → dados/portal/presenca_por_loja.json "
              f"({conta(len(d['lojas']), 'loja')})")


if __name__ == "__main__":
    main()
