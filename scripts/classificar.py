#!/usr/bin/env python3
"""
classificar.py — classifica as vozes coletadas por tema, do jeito do protocolo.

Regras que tornam o número comparável entre coletas (e que já custaram caro
quando não foram seguidas):

1. **Taxonomia base + extensão.** `metodologia/taxonomia.yaml` é a base; o
   `lexico_orthodontic.yaml` só ESTENDE alguns temas. Classificar com a extensão
   sozinha derruba o índice de atendimento de ~60% para ~13% — foi o que
   aconteceu na primeira tentativa.
2. **Normalizar acento.** O léxico é sem acento e o texto do paciente tem. Sem
   normalizar, "atencao" nunca casa com "atenção".
3. **Palavra inteira**, minúscula, multi-palavra permitido.
4. **Hash da taxonomia em toda linha.** Se o léxico mudar, o número muda — e
   sem o hash ninguém descobre que a série foi reescrita por baixo.

Saída: dados/serie/temas.jsonl (append-only, um registro por praça × tema ×
snapshot) e dados/serie/reviews_classificados.jsonl.

Uso:  python3 scripts/classificar.py
"""
import hashlib, json, pathlib, re, sys, unicodedata
import datetime as dt
from collections import defaultdict

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SERIE = RAIZ/"dados"/"serie"
BASE = RAIZ/"pesquisas"/"_metodo"/"metodologia"/"taxonomia.yaml"
EXT = RAIZ/"pesquisas"/"_metodo"/"config"/"lexico_orthodontic.yaml"


def normalizar(t):
    t = unicodedata.normalize("NFKD", t or "")
    return "".join(c for c in t if not unicodedata.combining(c)).lower()


def carrega_taxonomia():
    import yaml
    temas, versoes, h = defaultdict(list), [], hashlib.sha256()
    for arq in (BASE, EXT):
        if not arq.exists():
            sys.exit(f"falta {arq} — sem ela o número não é comparável")
        d = yaml.safe_load(arq.read_text(encoding="utf-8")) or {}
        h.update(arq.read_bytes())
        versoes.append(f"{arq.name} v{d.get('versao','?')}")
        for k, v in (d.get("temas") or {}).items():
            termos = v.get("termos") if isinstance(v, dict) else v
            for t in (termos or []):
                n = normalizar(t)
                if n not in temas[k]:
                    temas[k].append(n)
    return dict(temas), " + ".join(versoes), h.hexdigest()[:12]


def compila(temas):
    return {k: re.compile(r"\b(?:" + "|".join(re.escape(t) for t in v) + r")\b")
            for k, v in temas.items() if v}


def jsonl(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").split("\n") if l.strip()] if p.exists() else []


def main():
    temas, versao, hsh = carrega_taxonomia()
    rx = compila(temas)
    print(f"taxonomia: {versao} · hash {hsh}")
    print("temas: " + " · ".join(f"{k}({len(v)})" for k, v in temas.items()))

    R = jsonl(SERIE/"reviews.jsonl")
    com_texto = [r for r in R if r.get("tem_texto")]
    if not com_texto:
        sys.exit("nenhuma avaliação com texto em dados/serie/reviews.jsonl")

    classificados = []
    for r in com_texto:
        n = normalizar(r["texto"])
        achados = [k for k, c in rx.items() if c.search(n)]
        classificados.append({**{k: r[k] for k in
                                 ("chave", "snapshot_date", "praca_id", "local_id", "nota", "data")},
                              "temas": achados, "taxonomia_versao": versao, "taxonomia_hash": hsh})

    with (SERIE/"reviews_classificados.jsonl").open("w", encoding="utf-8") as f:
        for c in classificados:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    # agrega por praça × tema, e grava sem apagar o que já estava lá
    hoje = dt.date.today().isoformat()
    antigos = [t for t in jsonl(SERIE/"temas.jsonl") if t.get("snapshot_date") != hoje]
    novos = []
    por_praca = defaultdict(list)
    for c in classificados:
        por_praca[c["praca_id"]].append(c)
    print(f"\n{'PRAÇA':12s} {'N':>5s}  " + "  ".join(f"{k[:11]:>11s}" for k in temas))
    for p, g in sorted(por_praca.items()):
        linha = f"{p:12s} {len(g):5d}  "
        for k in temas:
            n = sum(1 for c in g if k in c["temas"])
            pct = n/len(g)
            novos.append({"snapshot_date": hoje, "praca_id": p, "tema": k,
                          "pct": round(pct, 4), "n": len(g), "base": "reviews_com_texto",
                          "taxonomia_versao": versao, "taxonomia_hash": hsh,
                          "fonte": "dados/serie/reviews.jsonl"})
            linha += f"{round(100*pct):10d}%  "
        print(linha)

    with (SERIE/"temas.jsonl").open("w", encoding="utf-8") as f:
        for t in antigos + novos:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")
    print(f"\ntemas.jsonl: {len(antigos)+len(novos)} linhas · classificados {len(classificados)}")


if __name__ == "__main__":
    main()
