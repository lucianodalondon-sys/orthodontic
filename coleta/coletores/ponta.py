#!/usr/bin/env python3
"""
ponta.py — a ponta da série: nota e contador de TODAS as clínicas, hoje.

O que ele é
-----------
A segunda coleta mais barata que existe. Para cada local das 13 praças —
nossos e concorrentes, 229 fichas — pergunta ao Google a nota, o total de
avaliações e se a ficha segue aberta. Uma chamada por ficha, sem Apify.

É este arquivo que faz a série virar SÉRIE. O "o que mudou" de cada praça
compara a ponta de hoje com a anterior: quem ganhou avaliações, quem perdeu
(avaliação removida), de quem a nota caiu, qual ficha fechou. Sem uma
segunda ponta, o portal é fotografia; com ela, é movimento.

Não confundir com a varredura profunda (google_reviews.py), que baixa o
TEXTO das avaliações e custa cota do Apify. Aqui é só o contador — mas o
contador é o que detecta onde vale gastar a varredura cara.

Uso:
    python3 coleta/coletores/ponta.py            # mostra sem gravar
    python3 coleta/coletores/ponta.py --salvar
"""
import argparse, json, os, pathlib, subprocess, sys, time
import datetime as dt

RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent
SERIE = RAIZ/"dados"/"serie"
sys.path.insert(0, str(RAIZ/"scripts"))
from cruzamento import identidades, jsonl


def chave():
    k = os.environ.get("GOOGLE_API_KEY", "").strip()
    if not k:
        env = RAIZ/"_pipeline"/".env"
        if env.exists():
            for l in env.read_text(encoding="utf-8").split("\n"):
                if l.strip().startswith("GOOGLE_API_KEY="):
                    k = l.split("=", 1)[1].strip()
    if not k:
        sys.exit("GOOGLE_API_KEY ausente")
    return k


def detalhe(place_id, k):
    r = subprocess.run(
        ["curl", "-sS", "-m", "30",
         f"https://places.googleapis.com/v1/places/{place_id}",
         "-H", f"X-Goog-Api-Key: {k}",
         "-H", "X-Goog-FieldMask: rating,userRatingCount,businessStatus"],
        capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    ap.add_argument("--praca", help="só uma praça")
    a = ap.parse_args()

    ident = identidades(com_unidade=False)   # rede E estudo: a ponta é de todos
    k = chave()
    hoje = dt.date.today().isoformat()

    ja_hoje = {x["local_id"] for x in jsonl("places") if x["snapshot_date"] == hoje}
    novas, erros = [], 0
    # locais da praça + vizinhos (cidade colada, medida mas fora das contas):
    # a série deles continua viva mesmo sem entrarem em nenhuma análise
    alvos = [(p, l) for p, d in sorted(ident.items())
             for l in d.get("locais", []) + d.get("vizinhos", [])
             if l.get("place_id")
             if not a.praca or p == a.praca]
    print(f"\n  {len(alvos)} fichas · corte {hoje} · "
          f"{len(ja_hoje)} já medidas hoje (puladas)\n")

    for i, (p, l) in enumerate(alvos, 1):
        if l["local_id"] in ja_hoje:
            continue
        d = detalhe(l["place_id"], k)
        if not d or "error" in d:
            erros += 1
            print(f"  {i:>3d}/{len(alvos)} ✗ {l['local_id'][:34]} "
                  f"{str(d.get('error', {}).get('status', 'sem resposta'))[:30]}")
            continue
        novas.append({
            # o place_id vai junto: sem ele, duas lojas que um dia dividirem
            # local_id por engano ficam impossíveis de separar depois
            "snapshot_date": hoje, "praca_id": p, "local_id": l["local_id"],
            "place_id": l["place_id"],
            "nota": d.get("rating"), "avaliacoes_total": d.get("userRatingCount"),
            "situacao_google": d.get("businessStatus"),
            "first_seen_snapshot": hoje, "last_seen_snapshot": hoje,
            "fonte": "google places · details",
        })
        if i % 40 == 0:
            print(f"  {i:>3d}/{len(alvos)} …")
        time.sleep(0.1)

    print(f"\n  {len(novas)} medidas novas · {erros} erro(s)")
    if erros and not novas:
        sys.exit("  ✗ nada medido — zero silencioso é falha")

    if a.salvar and novas:
        with (SERIE/"places.jsonl").open("a", encoding="utf-8") as f:
            for x in novas:
                f.write(json.dumps(x, ensure_ascii=False) + "\n")
        print(f"  → dados/serie/places.jsonl (+{len(novas)})")


if __name__ == "__main__":
    main()
