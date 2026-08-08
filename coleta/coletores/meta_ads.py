#!/usr/bin/env python3
"""
meta_ads.py — coletor da biblioteca de anúncios do Meta, via Apify (REST direto).

Grava em dados/serie/anuncios.jsonl, append-only. De first_seen/last_seen sai
`dias_no_ar` — o melhor proxy grátis de performance que existe: criativo que
sobrevive dois meses está performando.

Uso:
    python3 coleta/coletores/meta_ads.py --praca riomafra
    python3 coleta/coletores/meta_ads.py --todas
"""
import argparse, json, os, pathlib, re, sys, time, urllib.error, urllib.parse, urllib.request
import datetime as dt

RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent
SERIE = RAIZ/"dados"/"serie"
BRUTO = RAIZ/"dados"/"bruto"
ACTOR = "curious_coder~facebook-ads-library-scraper"
API = "https://api.apify.com/v2"

# Busca por palavra-chave na praça. A ausência também é dado: em Riomafra a
# unidade tinha ZERO anúncios no pico da temporada, e isso virou o alerta nº1.
BUSCAS = {
 "riomafra":  [("aparelho ortodôntico Mafra", 60), ("OrthoDontic Mafra", 40),
               ("Instituto Lumière", 40), ("OdontoCompany Mafra", 40)],
 "londrina":  [("aparelho ortodôntico Londrina", 60), ("OrthoDontic Londrina", 40),
               ("Odontoclinic Londrina", 40)],
 "feira":     [("aparelho ortodôntico Feira de Santana", 80), ("OrthoDontic Feira", 40),
               ("Moisés Suzart", 40)],
 "prudente":  [("aparelho ortodôntico Presidente Prudente", 60), ("OrthoDontic Prudente", 40)],
}

REGISTROS = [
 ("urgencia_desconto", r"últim|ultim|corr[ae]|agora mesmo|imperd|só hoje|so hoje|promo|desconto|condição especial|condicao especial|vagas limitadas|semana d"),
 ("preco_claro",       r"sem entrada|\d+x|parcel|mensalidade|a partir de|r\$"),
 ("acolhimento",       r"acolh|cuidad|sem medo|conforto|tranquil|planejament|acompanhament"),
 ("rosto_autoridade",  r"\bdra?\.|especialista|cro[- ]?\w*\d|nossa equipe|quem cuida"),
]


def token():
    t = os.environ.get("APIFY_TOKEN", "").strip()
    if not t:
        env = RAIZ/"_pipeline"/".env"
        if env.exists():
            for l in env.read_text(encoding="utf-8").splitlines():
                l = l.strip().replace("\r", "")
                if l.startswith("APIFY_TOKEN="):
                    t = l.split("=", 1)[1].strip()
    if not t:
        sys.exit("APIFY_TOKEN ausente")
    return t


def url_busca(q):
    return ("https://www.facebook.com/ads/library/?active_status=active&ad_type=all"
            f"&country=BR&q={urllib.parse.quote(q)}"
            "&search_type=keyword_unordered&media_type=all")


def roda(q, n, tok):
    # o actor exige 512MB por URL de entrada: 1 URL = memory 512, senão erra.
    url = f"{API}/acts/{ACTOR}/run-sync-get-dataset-items?token={tok}&timeout=420&memory=512"
    req = urllib.request.Request(
        url, data=json.dumps({"urls": [{"url": url_busca(q)}], "count": n,
                              "scrapePageAds.activeStatus": "active"}).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())


def registro(txt):
    t = (txt or "").lower()
    achados = [nome for nome, rx in REGISTROS if re.search(rx, t)]
    return achados or ["institucional"]


def jsonl_le(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--praca"); ap.add_argument("--todas", action="store_true")
    args = ap.parse_args()
    pracas = list(BUSCAS) if args.todas else ([args.praca] if args.praca else [])
    if not pracas:
        sys.exit("use --praca <id> ou --todas")

    hoje = dt.date.today().isoformat()
    tok = token()
    ads = {r["chave"]: r for r in jsonl_le(SERIE/"anuncios.jsonl")}

    for praca in pracas:
        print(f"\n=== {praca} · corte {hoje} ===")
        for q, n in BUSCAS.get(praca, []):
            try:
                itens = roda(q, n, tok)
            except urllib.error.HTTPError as e:
                print(f"  [ERRO] '{q}': HTTP {e.code} · {e.read().decode()[:150]}"); continue
            except Exception as e:
                print(f"  [ERRO] '{q}': {type(e).__name__} · {str(e)[:130]}"); continue

            novos = 0
            anunciantes = {}
            for a in itens:
                aid = str(a.get("ad_archive_id") or a.get("adArchiveID") or a.get("id") or "")
                if not aid:
                    continue
                sn = a.get("snapshot") or {}
                pagina = a.get("page_name") or sn.get("page_name") or "?"
                txt = ""
                for c in (sn.get("body") or {}, sn.get("cards") or [{}]):
                    if isinstance(c, dict):
                        txt += " " + (c.get("text") or c.get("markup", {}).get("__html", "") if isinstance(c.get("markup"), dict) else c.get("text") or "")
                txt = (txt or a.get("ad_creative_body") or sn.get("caption") or "").strip()
                chave = f"{praca}|{aid}"
                anunciantes[pagina] = anunciantes.get(pagina, 0) + 1
                if chave in ads:
                    ads[chave]["last_seen_snapshot"] = hoje
                    continue
                ads[chave] = {
                    "chave": chave, "snapshot_date": hoje, "praca_id": praca,
                    "ad_id": aid, "anunciante": pagina, "page_id": str(a.get("page_id") or ""),
                    "texto": txt[:1200], "registro": registro(txt),
                    "inicio_declarado": a.get("start_date_string") or a.get("startDate"),
                    "ativo": True, "consulta": q, "fonte": "meta_ad_library",
                    "first_seen_snapshot": hoje, "last_seen_snapshot": hoje,
                }
                novos += 1
            d = BRUTO/praca/"adlibrary"/hoje
            d.mkdir(parents=True, exist_ok=True)
            (d/f"{re.sub(r'[^a-z0-9]+','_',q.lower())[:50]}.json").write_text(
                json.dumps(itens, ensure_ascii=False)[:4_000_000], encoding="utf-8")
            top = sorted(anunciantes.items(), key=lambda x: -x[1])[:4]
            print(f"  '{q[:40]:40s}' {len(itens):3d} anúncios · {novos:3d} novos · "
                  + " · ".join(f"{k[:22]}({v})" for k, v in top))
            time.sleep(1)

    # Marca inativo SÓ nas praças que esta execução visitou. Anúncio de praça
    # não recoletada não é anúncio derrubado — é anúncio não verificado, e
    # tratar um como o outro inventa uma queda que não aconteceu.
    visitadas = set(pracas)
    for r in ads.values():
        if r["praca_id"] in visitadas and r["last_seen_snapshot"] != hoje and r.get("ativo"):
            r["ativo"] = False
    for r in ads.values():
        a, b = r["first_seen_snapshot"], r["last_seen_snapshot"]
        r["dias_no_ar"] = (dt.date.fromisoformat(b) - dt.date.fromisoformat(a)).days

    (SERIE/"anuncios.jsonl").parent.mkdir(parents=True, exist_ok=True)
    with (SERIE/"anuncios.jsonl").open("w", encoding="utf-8") as f:
        for r in sorted(ads.values(), key=lambda r: (r["praca_id"], r["anunciante"])):
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\nanuncios.jsonl: {len(ads)} linhas · {sum(1 for r in ads.values() if r['ativo'])} ativos")


if __name__ == "__main__":
    main()
