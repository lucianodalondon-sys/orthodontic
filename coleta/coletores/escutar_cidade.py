#!/usr/bin/env python3
"""
escutar_cidade.py — a etapa 3 do coleta/NOVA-PRACA.md, que faltava.

O canais.py descobre QUEM fala com a cidade. Este aqui vai ouvir o que eles
dizem — e é uma coisa diferente. Palmas entrou na base com 13 canais mapeados
e zero vozes coletadas: a gente sabia o endereço da conversa e nunca tinha
entrado nela.

O que sai daqui, e não sai de nenhuma outra fonte:
  · as palavras da cidade — como ela fala, não como a gente escreve
  · o que ela premia e o que ela detesta
  · o QUE NUNCA DIZER: o "axé litorâneo" que soaria falso em Feira, a gíria
    gaúcha que queimaria em Mafra

Meta: 800 a 1.400 vozes por praça. Foi o que as quatro primeiras renderam.

Uso:
    python3 coleta/coletores/escutar_cidade.py --praca palmas
    python3 coleta/coletores/escutar_cidade.py --praca palmas --posts 30
    python3 coleta/coletores/escutar_cidade.py --todas --dry-run
"""
import argparse, json, os, pathlib, subprocess, sys, time
import datetime as dt

RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent
SERIE = RAIZ/"dados"/"serie"
BRUTO = RAIZ/"dados"/"bruto"
IDENT = RAIZ/"dados"/"identidade"
ACTOR = "apify~instagram-scraper"
API = "https://api.apify.com/v2"


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


def curl(u, *a, tent=4):
    for i in range(tent):
        r = subprocess.run(["curl", "-sS", "-m", "300", *a, u], capture_output=True, text=True)
        if r.stdout.strip():
            try:
                return json.loads(r.stdout)
            except Exception:
                return None
        time.sleep(5*(i+1))
    return None


def canais(praca):
    """Os canais que o canais.py achou, do snapshot mais recente."""
    arq = SERIE/"canais.jsonl"
    if not arq.exists():
        return []
    linhas = [json.loads(l) for l in arq.read_text(encoding="utf-8").split("\n") if l.strip()]
    da_praca = [c for c in linhas if c.get("praca_id") == praca and c.get("handle")]
    if not da_praca:
        return []
    ultimo = max(c["snapshot_date"] for c in da_praca)
    vistos, fora = set(), []
    for c in da_praca:
        if c["snapshot_date"] == ultimo and c["handle"] not in vistos:
            vistos.add(c["handle"])
            fora.append(c)
    return fora


def roda(praca, n_posts, tok, dry=False):
    cs = canais(praca)
    if not cs:
        print(f"  {praca}: nenhum canal mapeado. Rode canais.py --praca {praca} antes.")
        return
    hoje = dt.date.today().isoformat()
    ident = json.loads((IDENT/f"{praca}.json").read_text(encoding="utf-8"))
    rot = ident.get("rotulo") or praca.upper()
    print(f"\n{'='*70}\n  ESCUTANDO {rot} · {len(cs)} canais · {n_posts} posts cada\n{'='*70}")
    for c in cs:
        print(f"  @{c['handle'][:28]:28s} {str(c.get('tipo') or '?'):16s} {c.get('seguidores') or 0:>8}")
    if dry:
        return

    corpo = {"directUrls": [f"https://www.instagram.com/{c['handle']}/" for c in cs],
             "resultsType": "posts", "resultsLimit": n_posts, "addParentData": True}
    d = curl(f"{API}/acts/{ACTOR}/run-sync-get-dataset-items?token={tok}&timeout=1800&memory=4096",
             "-X", "POST", "-H", "Content-Type: application/json",
             "-d", json.dumps(corpo, ensure_ascii=False))
    if not isinstance(d, list):
        print(f"  [FALHOU] {str(d)[:180]}")
        return

    tipo_de = {c["handle"]: c.get("tipo") for c in cs}
    dst = BRUTO/praca/"escuta"/hoje
    dst.mkdir(parents=True, exist_ok=True)
    (dst/"posts.json").write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")

    n = vozes = 0
    with (SERIE/"posts.jsonl").open("a", encoding="utf-8") as f:
        for p in d:
            if p.get("error"):
                continue
            u = p.get("ownerUsername") or ""
            leg = (p.get("caption") or "").strip()
            f.write(json.dumps({
                "snapshot_date": hoje, "praca_id": praca, "plataforma": "instagram",
                "camada": "territorio", "tipo_canal": tipo_de.get(u),
                "handle": u, "post_id": p.get("id"), "data": (p.get("timestamp") or "")[:10],
                "tipo": p.get("type"), "curtidas": p.get("likesCount"),
                "comentarios": p.get("commentsCount"), "legenda": leg[:1500],
                "tem_texto": bool(leg),
                "fonte": f"apify {ACTOR}", "filtro": f"resultsType=posts limit={n_posts}",
                "first_seen_snapshot": hoje}, ensure_ascii=False)+"\n")
            n += 1
            if leg:
                vozes += 1
    print(f"\n  posts.jsonl +{n} posts, {vozes} com texto")
    if vozes < 800:
        print(f"  ⚠ {vozes} vozes. A meta do método é 800 a 1.400 — as quatro")
        print(f"    primeiras praças renderam isso. Suba o --posts ou mapeie mais canais.")
    print("  Agora rode: python3 scripts/classificar.py")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--praca")
    ap.add_argument("--todas", action="store_true")
    ap.add_argument("--posts", type=int, default=40, help="posts por canal")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    pracas = ([p.stem for p in sorted(IDENT.glob("*.json"))] if a.todas
              else [a.praca] if a.praca else None)
    if not pracas:
        sys.exit("use --praca <id> ou --todas")
    tok = "" if a.dry_run else token()
    for p in pracas:
        roda(p, a.posts, tok, a.dry_run)
    print()


if __name__ == "__main__":
    main()
