#!/usr/bin/env python3
"""
reimporta_bruto.py — recupera avaliações do bruto sem gastar cota de novo.

Por que existe
--------------
Dois coletores gravaram reviews.jsonl EM PARALELO e o segundo regravou o
arquivo por cima do primeiro: as 592 avaliações de Prudente, recém-coletadas,
sumiram sem nenhum erro na tela — o arquivo foi de 37.031 para 36.764 linhas
e ninguém viu.

A coleta custou cota do Apify, mas o payload cru foi salvo em
dados/bruto/<praça>/google/<data>/<local_id>.json ANTES da série. É a regra
do projeto pagando por si: o bruto existe exatamente para reprocessar sem
recoletar.

Uso:
    python3 scripts/reimporta_bruto.py --praca prudente --data 2026-08-10
"""
import argparse, json, pathlib, sys
import datetime as dt

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SERIE = RAIZ/"dados"/"serie"
BRUTO = RAIZ/"dados"/"bruto"
sys.path.insert(0, str(RAIZ/"scripts"))


def jsonl_le(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").split("\n") if l.strip()] \
        if p.exists() else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--praca", required=True)
    ap.add_argument("--data", required=True)
    a = ap.parse_args()

    pasta = BRUTO/a.praca/"google"/a.data
    if not pasta.exists():
        sys.exit(f"sem bruto em {pasta}")

    ja = {r["chave"] for r in jsonl_le(SERIE/"reviews.jsonl")}
    novos_r, novos_p = [], []
    for arq in sorted(pasta.glob("*.json")):
        local_id = arq.stem
        itens = json.loads(arq.read_text(encoding="utf-8"))
        if isinstance(itens, dict):
            itens = [itens]
        for lugar in itens:
            revs = lugar.get("reviews") or []
            if lugar.get("placeId") or lugar.get("totalScore") is not None:
                novos_p.append({
                    "snapshot_date": a.data, "praca_id": a.praca,
                    "local_id": local_id,
                    "nota": lugar.get("totalScore"),
                    "avaliacoes_total": lugar.get("reviewsCount"),
                    "first_seen_snapshot": a.data,
                    "last_seen_snapshot": a.data,
                    "fonte": "reimportado do bruto",
                })
            for r in revs:
                rid = r.get("reviewId") or r.get("id") or ""
                chave = f"google:{lugar.get('placeId')}:{rid}"
                if chave in ja:
                    continue
                ja.add(chave)
                novos_r.append({
                    "chave": chave, "snapshot_date": a.data,
                    "praca_id": a.praca, "local_id": local_id,
                    "plataforma": "google",
                    "nota": str(r.get("stars") or ""),
                    "texto": r.get("text") or "",
                    "tem_texto": bool((r.get("text") or "").strip()),
                    "data": (r.get("publishedAtDate") or "")[:10],
                    "respondida": bool(r.get("responseFromOwnerText")),
                    "resposta_data": (r.get("responseFromOwnerDate") or "")[:10] or None,
                    "curtidas": r.get("likesCount"),
                    "first_seen_snapshot": a.data,
                    "last_seen_snapshot": a.data,
                })

    if not novos_r and not novos_p:
        print("nada novo no bruto — tudo já está na série")
        return

    with (SERIE/"reviews.jsonl").open("a", encoding="utf-8") as f:
        for r in novos_r:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    # places do reimporte só entra se o dia ainda não tem linha para o local
    pj = jsonl_le(SERIE/"places.jsonl")
    tem = {(p.get("local_id"), p.get("snapshot_date")) for p in pj}
    add_p = [p for p in novos_p if (p["local_id"], p["snapshot_date"]) not in tem]
    with (SERIE/"places.jsonl").open("a", encoding="utf-8") as f:
        for p in add_p:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    print(f"reimportados: +{len(novos_r)} avaliações · +{len(add_p)} places "
          f"(de {pasta})")


if __name__ == "__main__":
    main()
