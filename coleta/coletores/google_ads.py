#!/usr/bin/env python3
"""
google_ads.py — Centro de Transparência de Anúncios do Google, via Apify (REST).

Fecha o maior buraco de mídia do projeto: TODA a análise de anúncios dos quatro
estudos foi feita na biblioteca do Meta. Se o concorrente compra
"aparelho ortodôntico <cidade>" no Google, ele está invisível — e é justamente
onde a intenção de compra é maior, porque ali o paciente está PROCURANDO.

Grava em dados/serie/anuncios.jsonl, o mesmo arquivo do Meta, com o campo
`plataforma` separando as duas. Assim o portal soma as duas mídias sem
precisar de outra tela.

Uso:
    python3 coleta/coletores/google_ads.py --praca mafra
    python3 coleta/coletores/google_ads.py --todas
"""
import argparse, json, os, pathlib, re, sys, time, urllib.error, urllib.request
import datetime as dt
from collections import Counter

RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent
SERIE = RAIZ/"dados"/"serie"
BRUTO = RAIZ/"dados"/"bruto"
ACTOR = "solidcode~ads-transparency-scraper"
API = "https://api.apify.com/v2"

BUSCAS = {
 "mafra": ["OrthoDontic", "Instituto Lumière", "OdontoCompany"],
 "londrina": ["OrthoDontic", "Odontoclinic", "Classdent"],
 "feira":    ["OrthoDontic", "Moisés Suzart", "OdontoCompany"],
 "prudente": ["OrthoDontic", "NEXA Odonto", "Sorrifácil"],
}

REGISTROS = [
 ("urgencia_desconto", r"últim|ultim|agora|imperd|só hoje|so hoje|promo|desconto|condição|condicao|vagas limitadas"),
 ("preco_claro",       r"sem entrada|\d+ ?x|parcel|mensalidade|a partir de|r\$"),
 ("acolhimento",       r"acolh|cuidad|sem medo|conforto|tranquil|planejament|acompanhament"),
 ("rosto_autoridade",  r"\bdra?\.|especialista|cro[- ]?\w*\d|nossa equipe"),
]


def token():
    """A credencial sai do rodízio COM CHECAGEM DE SAÚDE (coleta/tokens.py).

    Antes cada coletor lia a primeira linha `APIFY_TOKEN=` do arquivo — e
    justamente as duas primeiras estão mortas (401 e 403). O módulo
    `tokens.vivos()` pergunta ao Apify quanto resta em cada conta e
    devolve da mais folgada para a mais apertada; já era usado só pelo
    coletor de avaliações. Agora vale para todos.
    """
    import sys as _s, pathlib as _p
    _s.path.insert(0, str(_p.Path(__file__).resolve().parent.parent))
    from tokens import vivos as _v
    fila = _v(quieto=True)
    if not fila:
        _s.exit("nenhum token Apify com cota — rode python3 coleta/tokens.py")
    return fila[0]["token"]



def roda(q, n, tok):
    url = f"{API}/acts/{ACTOR}/run-sync-get-dataset-items?token={tok}&timeout=420&memory=1024"
    req = urllib.request.Request(url, data=json.dumps({
        "searchQuery": q, "maxResults": n, "region": "BR",
    }).encode(), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())


def registro(txt):
    t = (txt or "").lower()
    a = [k for k, rx in REGISTROS if re.search(rx, t)]
    return a or ["institucional"]


def jsonl(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").split("\n") if l.strip()] if p.exists() else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--praca"); ap.add_argument("--todas", action="store_true")
    ap.add_argument("--n", type=int, default=20)
    args = ap.parse_args()
    pracas = list(BUSCAS) if args.todas else ([args.praca] if args.praca else [])
    if not pracas:
        sys.exit("use --praca <id> ou --todas")

    hoje = dt.date.today().isoformat()
    tok = token()
    ads = {r["chave"]: r for r in jsonl(SERIE/"anuncios.jsonl")}

    for praca in pracas:
        print(f"\n=== {praca} · Google Ads · corte {hoje} ===")
        for q in BUSCAS.get(praca, []):
            try:
                itens = roda(q, args.n, tok)
            except urllib.error.HTTPError as e:
                print(f"  [ERRO] '{q}': HTTP {e.code} · {e.read().decode()[:150]}"); continue
            except Exception as e:
                print(f"  [ERRO] '{q}': {type(e).__name__} · {str(e)[:130]}"); continue

            d = BRUTO/praca/"google_ads"/hoje
            d.mkdir(parents=True, exist_ok=True)
            (d/f"{re.sub(r'[^a-z0-9]+','_',q.lower())[:40]}.json").write_text(
                json.dumps(itens, ensure_ascii=False)[:4_000_000], encoding="utf-8")

            novos, anunciantes = 0, Counter()
            for a in itens:
                aid = str(a.get("adId") or a.get("creativeId") or a.get("id") or "")
                anunciante = a.get("advertiserName") or a.get("advertiser") or "?"
                if not aid:
                    continue
                txt = " ".join(str(a.get(k) or "") for k in
                               ("headline", "description", "text", "body", "adText"))[:1200].strip()
                anunciantes[anunciante] += 1
                chave = f"{praca}|gads|{aid}"
                if chave in ads:
                    ads[chave]["last_seen_snapshot"] = hoje
                    continue
                ads[chave] = {
                    "chave": chave, "snapshot_date": hoje, "praca_id": praca,
                    "plataforma": "google_ads", "ad_id": aid, "anunciante": anunciante,
                    "texto": txt, "registro": registro(txt),
                    "formato": a.get("format") or a.get("adFormat"),
                    "primeira_exibicao": a.get("firstShown") or a.get("startDate"),
                    "ultima_exibicao": a.get("lastShown") or a.get("endDate"),
                    "ativo": True, "consulta": q, "fonte": "google_ads_transparency",
                    "first_seen_snapshot": hoje, "last_seen_snapshot": hoje,
                }
                novos += 1
            top = " · ".join(f"{k[:24]}({v})" for k, v in anunciantes.most_common(4))
            print(f"  '{q[:26]:26s}' {len(itens):3d} anúncios · {novos:3d} novos · {top or '—'}")
            time.sleep(1)

    for r in ads.values():
        a, b = r["first_seen_snapshot"], r["last_seen_snapshot"]
        r["dias_no_ar"] = (dt.date.fromisoformat(b) - dt.date.fromisoformat(a)).days
        r.setdefault("plataforma", "meta")

    with (SERIE/"anuncios.jsonl").open("w", encoding="utf-8") as f:
        for r in sorted(ads.values(), key=lambda r: (r["praca_id"], r.get("plataforma",""), r["anunciante"])):
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    g = sum(1 for r in ads.values() if r.get("plataforma") == "google_ads")
    print(f"\nanuncios.jsonl: {len(ads)} linhas · {g} do Google · {len(ads)-g} do Meta")


if __name__ == "__main__":
    main()
