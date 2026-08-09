#!/usr/bin/env python3
"""
instagram.py — o que cada unidade e cada concorrente publica, via Apify (REST direto).

Mede o achado que aparece nas quatro praças: "o feed abandonou a especialidade"
e "o feed esconde as pessoas". Aqui isso vira número — share de post por tema e
share de post com rosto — em vez de impressão de quem olhou o perfil.

Grava em dados/serie/posts.jsonl (append-only, first_seen/last_seen).

Uso:
    python3 coleta/coletores/instagram.py --praca mafra
    python3 coleta/coletores/instagram.py --todas --posts 15
"""
import argparse, json, os, pathlib, re, sys, time, urllib.error, urllib.request
import datetime as dt

RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent
SERIE = RAIZ/"dados"/"serie"
BRUTO = RAIZ/"dados"/"bruto"
ACTOR = "apify~instagram-scraper"
API = "https://api.apify.com/v2"

# só própria e concorrente direto — os perfis de território ficam para a coleta
# de vozes, que é outra pergunta e outro custo.
PERFIS = {
 "mafra": [("orthodontic.mafra", "proprio", "ortho_mafra"),
              ("odontocompanyriomafra", "concorrente", "oc_mafra")],
 "londrina": [("orthodontic.londrinasouzanaves", "proprio", "ortho_souza_naves"),
              ("orthodontic.londrinacentro", "proprio", "ortho_centro_ldn"),
              ("odontocliniclondrina", "concorrente", "odontoclinic_ldn")],
 "feira":    [("orthodontic.feira", "proprio", "ortho_fsa"),
              ("clinicamoises.suzart", "concorrente", "gigante_fsa")],
 "prudente": [("orthodontic.presidenteprudente", "proprio", "ortho_pp")],
}

# tema do post — a pergunta é: a clínica "Especializada em Aparelho" fala de aparelho?
TEMAS = [
 ("ortodontia",  r"aparelh|ortodont|bracket|alinhad|contenç|contenc|manutenç|manutenc|borrachinha|sorriso alinhad"),
 ("outros_servicos", r"implant|facet|lentes de contato|clareament|prótes|protes|canal|endodont|extraç|extrac|periodont|limpeza"),
 ("institucional", r"nossa missão|nossa missao|nossa equipe|somos|anos de|rede|unidade|bem-vind"),
 ("promocao",    r"promo|desconto|condição|condicao|últim|ultim|imperd|sem entrada|\d+x|a partir de|r\$"),
 ("educativo",   r"você sabia|voce sabia|dica|mito|verdade|por que|entenda|saiba"),
 ("pessoas",     r"\bdra?\.|nossa recepç|nossa recepc|conheça|conheca|nosso time|especialista|paciente"),
]


def token():
    t = os.environ.get("APIFY_TOKEN", "").strip()
    if not t:
        env = RAIZ/"_pipeline"/".env"
        if env.exists():
            for l in env.read_text(encoding="utf-8").split("\n"):
                l = l.strip().replace("\r", "")
                if l.startswith("APIFY_TOKEN="):
                    t = l.split("=", 1)[1].strip()
    if not t:
        sys.exit("APIFY_TOKEN ausente")
    return t


def roda(handles, n, tok):
    url = f"{API}/acts/{ACTOR}/run-sync-get-dataset-items?token={tok}&timeout=420&memory=1024"
    req = urllib.request.Request(url, data=json.dumps({
        "directUrls": [f"https://www.instagram.com/{h}/" for h in handles],
        "resultsType": "posts", "resultsLimit": n,
        "addParentData": False,
    }).encode(), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())


def temas(txt):
    t = (txt or "").lower()
    a = [nome for nome, rx in TEMAS if re.search(rx, t)]
    return a or ["sem_tema"]


def jsonl_le(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").split("\n") if l.strip()] if p.exists() else []


def perfis_da_identidade(praca):
    """Tenta adivinhar o @ da unidade a partir do nome da praça.

    É palpite, e palpite marcado como tal: os @ da rede seguem o padrão
    'orthodontic.<cidade><bairro>', mas não há regra garantida. O que não
    existir volta como not_found, e aí alguém procura à mão uma vez só.
    """
    arq = RAIZ/"dados"/"identidade"/f"{praca}.json"
    if not arq.exists():
        return []
    ident = json.loads(arq.read_text(encoding="utf-8"))
    import unicodedata, re
    # mesma forma de PERFIS: (handle, papel, local_id)
    proprio = next((l["local_id"] for l in ident.get("locais", [])
                    if l.get("papel") == "proprio"), f"ortho_{praca}")
    fora = []
    for c in (ident.get("cidades") or []):
        n = unicodedata.normalize("NFKD", c.split("/")[0])
        n = re.sub(r"[^a-z0-9]", "", "".join(x for x in n if not unicodedata.combining(x)).lower())
        for h in (f"orthodontic.{n}", f"orthodontic{n}", f"orthodonticbrasil{n}"):
            fora.append((h, "proprio", proprio))
    return fora


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--praca"); ap.add_argument("--todas", action="store_true")
    ap.add_argument("--posts", type=int, default=15)
    args = ap.parse_args()
    pracas = list(PERFIS) if args.todas else ([args.praca] if args.praca else [])
    if not pracas:
        sys.exit("use --praca <id> ou --todas")

    hoje = dt.date.today().isoformat()
    tok = token()
    posts = {r["chave"]: r for r in jsonl_le(SERIE/"posts.jsonl")}

    for praca in pracas:
        alvos = PERFIS.get(praca) or perfis_da_identidade(praca)
        if not alvos:
            print(f"  [SEM PERFIL] {praca}: nenhum perfil conhecido. "
                  f"Procure o @ da unidade e acrescente em PERFIS.")
            continue
        if not alvos:
            continue
        handles = [h for h, _, _ in alvos]
        meta = {h: (papel, lid) for h, papel, lid in alvos}
        print(f"\n=== {praca} · {len(handles)} perfis · corte {hoje} ===")
        try:
            itens = roda(handles, args.posts, tok)
        except urllib.error.HTTPError as e:
            print(f"  [ERRO] HTTP {e.code} · {e.read().decode()[:200]}"); continue
        except Exception as e:
            print(f"  [ERRO] {type(e).__name__} · {str(e)[:160]}"); continue

        d = BRUTO/praca/"instagram"/hoje
        d.mkdir(parents=True, exist_ok=True)
        (d/"posts.json").write_text(json.dumps(itens, ensure_ascii=False)[:8_000_000], encoding="utf-8")

        por_perfil = {}
        for it in itens:
            h = (it.get("ownerUsername") or "").lower()
            if h not in meta:
                continue
            pid = it.get("shortCode") or it.get("id")
            chave = f"{h}|{pid}"
            cap = (it.get("caption") or "").strip()
            papel, lid = meta[h]
            if chave in posts:
                posts[chave]["last_seen_snapshot"] = hoje
                posts[chave]["curtidas"] = it.get("likesCount")
                posts[chave]["comentarios"] = it.get("commentsCount")
            else:
                posts[chave] = {
                    "chave": chave, "snapshot_date": hoje, "praca_id": praca,
                    "local_id": lid, "papel": papel, "handle": h, "post_id": pid,
                    "data": (it.get("timestamp") or "")[:10],
                    "tipo": it.get("type"), "legenda": cap[:1500],
                    "temas": temas(cap),
                    "curtidas": it.get("likesCount"), "comentarios": it.get("commentsCount"),
                    "url": it.get("url"), "fonte": "apify/instagram-scraper",
                    "first_seen_snapshot": hoje, "last_seen_snapshot": hoje,
                }
            por_perfil.setdefault(h, []).append(posts[chave])

        for h, (papel, lid) in meta.items():
            g = por_perfil.get(h, [])
            if not g:
                print(f"  {h:34s} — sem posts (perfil privado, renomeado ou sem retorno)")
                continue
            orto = sum(1 for p in g if "ortodontia" in p["temas"])
            outros = sum(1 for p in g if "outros_servicos" in p["temas"])
            pess = sum(1 for p in g if "pessoas" in p["temas"])
            med = sorted(p["curtidas"] or 0 for p in g)[len(g)//2]
            print(f"  {h:34s} {len(g):3d} posts · orto {orto:2d} ({round(100*orto/len(g)):3d}%) · "
                  f"outros serviços {outros:2d} · com pessoas {pess:2d} · mediana {med} curtidas")
        time.sleep(1)

    with (SERIE/"posts.jsonl").open("w", encoding="utf-8") as f:
        for r in sorted(posts.values(), key=lambda r: (r["praca_id"], r["handle"], r.get("data") or "")):
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\nposts.jsonl: {len(posts)} linhas")


if __name__ == "__main__":
    main()
