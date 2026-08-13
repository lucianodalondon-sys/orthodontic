#!/usr/bin/env python3
"""
backfill_observacoes_de_anuncio.py — o que estava no ar em cada rodada.

O BURACO. `anuncios.jsonl` é um LEDGER: uma linha por anúncio, com
`first_seen_snapshot` e `last_seen_snapshot`, reescrita a cada coleta. Ele
responde "há quantos dias este anúncio está no ar". Não responde "o que
estava no ar no dia 8" — e sem essa segunda resposta não existe "entrou",
"saiu", "voltou" nem "a pressão aumentou". O detector de mercado
comparava conjuntos por `snapshot_date` que o arquivo nunca guardou.

`meta_ads.py` passou a gravar `anuncios_observados.jsonl` daqui para a
frente. Este script recupera o passado que o ledger já contém.

O QUE DÁ PARA RECONSTRUIR, E O QUE NÃO DÁ

O ledger diz que um anúncio foi visto em `first_seen` e em `last_seen`.
Entre as duas datas ele esteve no ar — o coletor só atualiza `last_seen`
quando reencontra o anúncio. Então:

    anúncio presente em D  ⟺  first_seen ≤ D ≤ last_seen
                              E a praça foi consultada em D

A segunda condição é o que impede a invenção. As datas em que uma praça
foi consultada saem das próprias pontas: toda data que aparece como
`first_seen` ou `last_seen` de algum anúncio dela é uma rodada que
existiu. Data em que a praça não foi consultada NÃO ganha linha — e
ausência de linha continua significando "não verificado", nunca "não
havia anúncio".

Toda linha reconstruída vai marcada com `reconstruido: true` e o motivo.
Quem lê precisa saber que aquilo é dedução do ledger, não observação
gravada na hora.

Uso:
    python3 scripts/backfill_observacoes_de_anuncio.py
    python3 scripts/backfill_observacoes_de_anuncio.py --salvar
"""
import argparse, json, pathlib
from collections import defaultdict

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SERIE = RAIZ/"dados"/"serie"
LEDGER = SERIE/"anuncios.jsonl"
OBS = SERIE/"anuncios_observados.jsonl"
RODADAS = SERIE/"anuncios_rodadas.jsonl"


def le(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").split("\n")
            if l.strip()] if p.exists() else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()

    ads = le(LEDGER)
    if not ads:
        print("  ✗ FALHA: anuncios.jsonl vazio — nada a reconstruir")
        return

    # as rodadas que existiram, por praça
    datas = defaultdict(set)
    for r in ads:
        p = r.get("praca_id")
        for k in ("first_seen_snapshot", "last_seen_snapshot", "snapshot_date"):
            if r.get(k):
                datas[p].add(r[k])

    # A IDENTIDADE DO ANÚNCIO É A `chave`, NÃO O `ad_id`.
    #
    # Os anúncios coletados pelo scraper antigo têm `ad_id: null` — 48 de
    # Cuiabá, com 48 chaves distintas, colapsavam num só e a reconstrução
    # dizia "1 anúncio no ar" onde havia 48. É a mesma armadilha de
    # `id_da_avaliacao`: dois coletores, dois formatos de id, e a chave
    # comum é a que sempre existe.
    def ident(r):
        return r.get("chave") or f"{r.get('praca_id')}|{r.get('ad_id')}"

    ja = {(o["snapshot_date"], o["praca_id"], ident(o)) for o in le(OBS)}
    novas, por_praca = [], defaultdict(lambda: defaultdict(int))
    for r in ads:
        p, a0 = r.get("praca_id"), r.get("first_seen_snapshot")
        a1 = r.get("last_seen_snapshot") or a0
        if not (p and a0):
            continue
        for d in sorted(datas[p]):
            if not (a0 <= d <= a1):
                continue
            k = (d, p, ident(r))
            if k in ja:
                continue
            ja.add(k)
            novas.append({
                "snapshot_date": d, "praca_id": p, "ad_id": r.get("ad_id"),
                "chave": r.get("chave"), "anunciante": r.get("anunciante"),
                "page_id": r.get("page_id"), "consulta": r.get("consulta"),
                "fonte": r.get("fonte") or "meta_ad_library",
                "reconstruido": True,
                "porque": ("deduzido de anuncios.jsonl: o anúncio foi visto "
                           f"em {a0} e em {a1}, e a praça foi consultada "
                           f"em {d}"),
            })
            por_praca[p][d] += 1

    print(f"  {len(ads)} anúncios no ledger · {len(novas)} observações "
          f"reconstruídas em {len(por_praca)} praças\n")
    print(f"  {'praça':<22}{'rodadas':>8}   anúncios no ar por rodada")
    for p in sorted(por_praca):
        ds = sorted(por_praca[p])
        print(f"  {p:<22}{len(ds):>8}   "
              + " · ".join(f"{d[5:]}:{por_praca[p][d]}" for d in ds))

    if not a.salvar:
        print("\n  (--salvar para gravar)")
        return

    with OBS.open("a", encoding="utf-8") as f:
        for r in novas:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    ja_rod = {(x["snapshot_date"], x["praca_id"]) for x in le(RODADAS)}
    with RODADAS.open("a", encoding="utf-8") as f:
        for p in sorted(por_praca):
            for d in sorted(por_praca[p]):
                if (d, p) in ja_rod:
                    continue
                f.write(json.dumps({
                    "snapshot_date": d, "praca_id": p,
                    "anuncios_vistos": por_praca[p][d],
                    "consultas": [], "fonte": "meta_ad_library",
                    "reconstruido": True,
                    "porque": "rodada deduzida das pontas do ledger",
                }, ensure_ascii=False) + "\n")
    print(f"\n  → dados/serie/anuncios_observados.jsonl +{len(novas)}")
    print(f"  → dados/serie/anuncios_rodadas.jsonl")


if __name__ == "__main__":
    main()
