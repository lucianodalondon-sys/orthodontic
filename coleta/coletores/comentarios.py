#!/usr/bin/env python3
"""
comentarios.py — o texto dos comentários, que contávamos e nunca líamos.

Por que existe
--------------
`posts.jsonl` guarda QUANTOS comentários cada post teve. São 54.962 — mais do
que as 35.538 avaliações da base inteira. O texto de nenhum deles foi lido.

E é uma voz diferente da avaliação. Quem avalia uma clínica já foi paciente.
Quem comenta no perfil de humor, no de achadinho ou no da mãe é a cidade
falando antes de escolher — e às vezes é o paciente do concorrente dizendo,
embaixo do post dele, o que deu errado.

A ideia é do cliente, e é a melhor deste projeto: "ouvir as pessoas que
comentam nos canais da concorrência, e descobrir o que a concorrência faz que
dá certo".

O que ele coleta, e em que ordem
---------------------------------
Não dá para ler 54.962 comentários com US$ 50 de cota. Então ele prioriza:

  1. posts de canal da nossa praça com MAIS comentários — onde a cidade falou
  2. dentro deles, os que têm legenda com texto (post mudo não gera conversa
     sobre nada)

O que ele NÃO faz
-----------------
Não coleta nome, foto nem @ de quem comentou. O que interessa é o que a cidade
diz, não quem disse — e guardar identidade de pessoa comum num repositório de
cliente é risco sem contrapartida. Só o texto, a data e o post de origem.

Uso:
    python3 coleta/coletores/comentarios.py --praca contagem --posts 40
    python3 coleta/coletores/comentarios.py --todas --posts 25
"""
import argparse, json, pathlib, subprocess, sys, time
import datetime as dt
from collections import defaultdict

RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent
SERIE = RAIZ/"dados"/"serie"
BRUTO = RAIZ/"dados"/"bruto"
API = "https://api.apify.com/v2"
ACTOR = "apify~instagram-comment-scraper"

sys.path.insert(0, str(RAIZ/"coleta"))
from tokens import vivos as _vivos


class Cota:
    def __init__(self):
        self.fila = _vivos(quieto=True)
        if not self.fila:
            sys.exit("nenhum token Apify com cota — rode python3 coleta/tokens.py")
        self.i = 0

    def atual(self):
        return self.fila[self.i]["token"]

    def queimou(self):
        self.i += 1
        if self.i >= len(self.fila):
            return False
        print(f"  ↻ token estourado, indo para o {self.i+1}º de {len(self.fila)}")
        return True


def curl(url, corpo, tent=3):
    for i in range(tent):
        r = subprocess.run(["curl", "-sS", "-m", "1200", url, "-X", "POST",
                            "-H", "Content-Type: application/json",
                            "-d", json.dumps(corpo, ensure_ascii=False)],
                           capture_output=True, text=True)
        if r.stdout.strip():
            try:
                return json.loads(r.stdout)
            except Exception:
                pass
        time.sleep(3 * (i + 1))
    return {"error": "sem resposta"}


def jsonl(nome):
    p = SERIE/f"{nome}.jsonl"
    return [json.loads(l) for l in p.read_text(encoding="utf-8").split("\n") if l.strip()] \
        if p.exists() else []


def alvos(praca, n):
    """Os posts que mais renderam conversa, na praça pedida.

    Ordena por número de comentários porque é lá que a cidade falou. Post com
    500 comentários ensina mais que vinte posts com 3."""
    P = [x for x in jsonl("posts") if x.get("praca_id") == praca
         and (x.get("comentarios") or 0) >= 3 and x.get("post_id")]
    # o mesmo post pode ter sido coletado em dois snapshots
    por_id = {}
    for x in sorted(P, key=lambda y: y.get("snapshot_date", "")):
        por_id[x["post_id"]] = x
    return sorted(por_id.values(), key=lambda x: -(x.get("comentarios") or 0))[:n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--praca")
    ap.add_argument("--todas", action="store_true")
    ap.add_argument("--posts", type=int, default=25, help="posts por praça")
    ap.add_argument("--por-post", type=int, default=40, help="comentários por post")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    pracas = ([a.praca] if a.praca else
              sorted({x["praca_id"] for x in jsonl("posts") if x.get("praca_id")})
              if a.todas else [])
    if not pracas:
        sys.exit("use --praca <id> ou --todas")

    cota = None if a.dry_run else Cota()
    hoje = dt.date.today().isoformat()
    ja = {x.get("chave") for x in jsonl("comentarios")}
    total = 0

    for praca in pracas:
        alv = alvos(praca, a.posts)
        if not alv:
            print(f"\n  {praca}: nenhum post com comentário. Rode "
                  f"escutar_cidade.py --praca {praca} antes.")
            continue
        soma = sum(x.get("comentarios") or 0 for x in alv)
        print(f"\n=== {praca} · {len(alv)} posts · {soma} comentários declarados ===")
        for x in alv[:5]:
            print(f"    @{(x.get('handle') or '')[:26]:26s} "
                  f"{x.get('comentarios'):>5} coment · {(x.get('tipo_canal') or '?')}")
        if a.dry_run:
            continue

        urls = [{"url": f"https://www.instagram.com/p/{x['post_id']}/"}
                if not str(x["post_id"]).startswith("http")
                else {"url": x["post_id"]} for x in alv]
        de_post = {x["post_id"]: x for x in alv}

        while True:
            d = curl(f"{API}/acts/{ACTOR}/run-sync-get-dataset-items"
                     f"?token={cota.atual()}&timeout=1800&memory=4096",
                     {"directUrls": [u["url"] for u in urls],
                      "resultsLimit": a.por_post})
            if isinstance(d, list):
                break
            if "hard limit" in str(d) and cota.queimou():
                continue
            print(f"  [FALHOU] {str(d)[:160]}")
            d = None
            break
        if not d:
            continue

        dst = BRUTO/praca/"comentarios"/hoje
        dst.mkdir(parents=True, exist_ok=True)
        (dst/"comentarios.json").write_text(json.dumps(d, ensure_ascii=False),
                                            encoding="utf-8")
        n = 0
        with (SERIE/"comentarios.jsonl").open("a", encoding="utf-8") as f:
            for c in d:
                txt = (c.get("text") or "").strip()
                if not txt:
                    continue
                pid = c.get("postUrl") or c.get("postId") or ""
                chave = f"instagram:coment:{c.get('id')}"
                if chave in ja:
                    continue
                ja.add(chave)
                origem = next((v for k, v in de_post.items() if str(k) in str(pid)), {})
                f.write(json.dumps({
                    "chave": chave, "snapshot_date": hoje, "praca_id": praca,
                    "plataforma": "instagram",
                    # NÃO guardamos quem comentou: nome, @ e foto ficam de fora.
                    # Interessa o que a cidade diz, não quem disse.
                    "texto": txt,
                    "curtidas": c.get("likesCount"),
                    "data": (c.get("timestamp") or "")[:10],
                    "post_url": pid,
                    "handle_do_post": origem.get("handle"),
                    "tipo_canal": origem.get("tipo_canal"),
                    "fonte": f"apify {ACTOR}",
                    "first_seen_snapshot": hoje,
                }, ensure_ascii=False) + "\n")
                n += 1
        total += n
        print(f"  comentarios.jsonl +{n} comentários com texto")

    if total:
        print(f"\n  {total} comentários novos · "
              f"agora rode: python3 scripts/classificar.py")


if __name__ == "__main__":
    main()
