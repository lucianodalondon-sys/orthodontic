#!/usr/bin/env python3
"""
imprensa_rss.py — coletor de imprensa local por praça. Sem credencial, sem custo.

Lê o Google News RSS por consulta e grava em dados/serie/imprensa.jsonl,
append-only, com snapshot_date · first_seen · last_seen (contrato da camada 1).

Por que importa: a joia enterrada de Riomafra — o casal de ortodontistas que
voltou pra casa — saiu de matéria em jornal local. Não foi sorte, foi busca
documental. Este coletor transforma isso em rotina semanal.

Uso:
    python3 coleta/coletores/imprensa_rss.py
    python3 coleta/coletores/imprensa_rss.py --praca riomafra
"""
import argparse, json, pathlib, sys, time, urllib.parse, urllib.request
import datetime as dt
from xml.etree import ElementTree as ET

RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent
SAIDA = RAIZ/"dados"/"serie"/"imprensa.jsonl"
UA = "Mozilla/5.0 (compatible; OrthoIntel/1.0; pesquisa de mercado)"

# Consultas por praça. Cada uma responde a uma pergunta do estudo:
#   marca      → a rede aparece na imprensa local?
#   categoria  → quem mais aparece (o concorrente com assessoria)
#   cidade     → o que a praça noticia (contexto e calendário)
CONSULTAS = {
  "riomafra": [
    ("marca",     'OrthoDontic Mafra OR "OrthoDontic" "Rio Negro"'),
    ("categoria", 'ortodontia OR dentista OR odontologia Mafra OR "Rio Negro" Paraná'),
    ("concorrente", '"Instituto Lumière" OR OdontoCompany Mafra'),
    ("cidade",    'Mafra Santa Catarina OR Riomafra'),
  ],
  "londrina": [
    ("marca",     '"OrthoDontic" Londrina'),
    ("categoria", 'ortodontia OR aparelho ortodôntico OR odontologia Londrina'),
    ("concorrente", 'Odontoclinic Londrina'),
    ("cidade",    'Londrina Paraná saúde'),
  ],
  "feira": [
    ("marca",     '"OrthoDontic" "Feira de Santana"'),
    ("categoria", 'ortodontia OR odontologia "Feira de Santana"'),
    ("cidade",    '"Feira de Santana" Bahia'),
  ],
  "prudente": [
    ("marca",     '"OrthoDontic" "Presidente Prudente"'),
    ("categoria", 'ortodontia OR odontologia "Presidente Prudente"'),
    ("cidade",    '"Presidente Prudente" São Paulo'),
  ],
}


def busca(q, n=25):
    url = ("https://news.google.com/rss/search?q="
           + urllib.parse.quote(q)
           + "&hl=pt-BR&gl=BR&ceid=BR:pt-419")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        raiz = ET.fromstring(r.read())
    itens = []
    for it in list(raiz.iterfind(".//item"))[:n]:
        fonte = it.find("source")
        itens.append({
            "titulo": (it.findtext("title") or "").strip(),
            "link": (it.findtext("link") or "").strip(),
            "publicado": (it.findtext("pubDate") or "").strip(),
            "veiculo": (fonte.text or "").strip() if fonte is not None else None,
        })
    return itens


def carrega_existentes():
    if not SAIDA.exists():
        return {}
    fora = {}
    for l in SAIDA.read_text(encoding="utf-8").splitlines():
        if not l.strip():
            continue
        r = json.loads(l)
        fora[r["chave"]] = r
    return fora


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--praca", help="só uma praça")
    args = ap.parse_args()

    hoje = dt.date.today().isoformat()
    pracas = [args.praca] if args.praca else list(CONSULTAS)
    existentes = carrega_existentes()
    novos, revistos = [], 0

    for praca in pracas:
        for camada, q in CONSULTAS.get(praca, []):
            try:
                itens = busca(q)
            except Exception as e:
                print(f"  [ERRO] {praca}/{camada}: {str(e)[:120]}", file=sys.stderr)
                continue
            for it in itens:
                chave = f"{praca}|{it['link']}"
                if chave in existentes:
                    existentes[chave]["last_seen_snapshot"] = hoje
                    revistos += 1
                    continue
                novos.append({
                    "chave": chave, "snapshot_date": hoje, "praca_id": praca,
                    "camada": camada, "consulta": q, "fonte": "google_news_rss",
                    **it,
                    "first_seen_snapshot": hoje, "last_seen_snapshot": hoje,
                })
                existentes[chave] = novos[-1]
            print(f"  {praca:10s} {camada:12s} {len(itens):3d} itens")
            time.sleep(1.2)   # cortesia com a fonte

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    with SAIDA.open("w", encoding="utf-8") as f:
        for r in existentes.values():
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"\n{len(novos)} novos · {revistos} revistos · {len(existentes)} no total")
    print(f"→ {SAIDA.relative_to(RAIZ)}")
    for r in novos[:12]:
        print(f"   [{r['praca_id']}/{r['camada']}] {r['veiculo'] or '?'} — {r['titulo'][:95]}")


if __name__ == "__main__":
    main()
