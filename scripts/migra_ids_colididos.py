#!/usr/bin/env python3
"""
migra_ids_colididos.py — separa lojas que dividiram o mesmo `local_id`.

QUANDO ISTO É PRECISO. O `local_id` nasceu do nome. Toda unidade da rede
se chama "OrthoDontic", e rede de concorrente repete nome de cidade em
cidade — Sorridents está em três praças, Oral Unic em duas. Sem a praça
dentro do id, quatro lojas diferentes viram uma só, e a série (que é
chaveada por `local_id` no projeto INTEIRO) mistura os contadores.

O gerador já foi corrigido para pôr a praça no id desde o nascimento.
Este script conserta o que nasceu antes disso.

O QUE ELE FAZ, E O QUE NÃO FAZ

· Renomeia SÓ os ids que aparecem em mais de uma praça. Id único fica
  como está — trocar id sem necessidade quebra histórico de graça.
· Leva junto TODA série chaveada por `local_id`, casando por
  (local_id antigo + praca_id), que é o par que identifica a loja certa.
· Corrige também o prefixo da `chave`, porque ela carrega o id na frente.
· Não apaga linha nenhuma. Não muda `snapshot_date`. Não inventa dado.
· Não toca em `place_id`: ele já era único e é a âncora do casamento.

Uso:
    python3 scripts/migra_ids_colididos.py            # só mostra
    python3 scripts/migra_ids_colididos.py --salvar
"""
import argparse, json, pathlib, re, unicodedata
from collections import defaultdict

RAIZ = pathlib.Path(__file__).resolve().parent.parent
IDENT = RAIZ/"dados"/"identidade"
SERIE = RAIZ/"dados"/"serie"

# as séries que guardam local_id — descobertas lendo a primeira linha de cada
SERIES = ["places", "reviews", "reviews_classificados", "fila_historico",
          "funil", "acoes"]


def slug(s):
    s = unicodedata.normalize("NFKD", str(s or ""))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()

    ids = {arq.stem: json.loads(arq.read_text(encoding="utf-8"))
           for arq in sorted(IDENT.glob("*.json"))}

    onde = defaultdict(set)
    for praca, d in ids.items():
        for l in d.get("locais", []):
            onde[l.get("local_id")].add(praca)
    colididos = {k for k, v in onde.items() if len(v) > 1}
    if not colididos:
        print("  nenhum local_id repetido entre praças — nada a migrar")
        return

    print(f"  {len(colididos)} ids em mais de uma praça:")
    for k in sorted(colididos):
        print(f"    {k:<34}{sorted(onde[k])}")

    # de_para[(id_antigo, praca)] = id_novo
    de_para, usados = {}, set()
    for praca, d in ids.items():
        for l in d.get("locais", []):
            usados.add(l.get("local_id"))
    for praca, d in ids.items():
        pref = slug(praca)[:12]
        for l in d.get("locais", []):
            velho = l.get("local_id")
            if velho not in colididos:
                continue
            novo = f"{pref}_{velho}"[:56]
            i = 2
            while novo in usados:
                novo = f"{pref}_{velho}_{i}"[:56]
                i += 1
            usados.add(novo)
            de_para[(velho, praca)] = novo

    print(f"\n  {len(de_para)} locais serão renomeados")
    for (velho, praca), novo in sorted(de_para.items())[:10]:
        print(f"    {praca:<16}{velho[:28]:<30} → {novo}")

    if not a.salvar:
        print("\n  (--salvar para gravar)")
        return

    # identidades
    for praca, d in ids.items():
        mudou = False
        for l in d.get("locais", []):
            novo = de_para.get((l.get("local_id"), praca))
            if novo:
                l["local_id"] = novo
                mudou = True
        if mudou:
            (IDENT/f"{praca}.json").write_text(
                json.dumps(d, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

    # séries
    for nome in SERIES:
        p = SERIE/f"{nome}.jsonl"
        if not p.exists():
            continue
        linhas = [json.loads(l) for l in p.read_text(encoding="utf-8").split("\n")
                  if l.strip()]
        n = 0
        for r in linhas:
            novo = de_para.get((r.get("local_id"), r.get("praca_id")))
            if not novo:
                continue
            velho = r["local_id"]
            r["local_id"] = novo
            # a chave carrega o id na frente: sem isto a dedup quebra
            if isinstance(r.get("chave"), str) and r["chave"].startswith(velho + "|"):
                r["chave"] = novo + r["chave"][len(velho):]
            n += 1
        if n:
            with p.open("w", encoding="utf-8") as f:
                for r in linhas:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            print(f"  série {nome}: {n} linhas migradas")

    # planos, que são um arquivo por local_id
    planos = RAIZ/"dados"/"planos"
    for (velho, praca), novo in de_para.items():
        for ext in ("json", "md"):
            velho_arq = planos/f"{velho}.{ext}"
            if velho_arq.exists():
                velho_arq.rename(planos/f"{novo}.{ext}")
                print(f"  plano renomeado: {velho}.{ext} → {novo}.{ext}")
    print("\n  → identidades, séries e planos migrados")


if __name__ == "__main__":
    main()
