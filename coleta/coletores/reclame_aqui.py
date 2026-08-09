#!/usr/bin/env python3
"""
reclame_aqui.py — reclamações da marca no Reclame Aqui, via Apify (REST direto).

É a ÚNICA medição pública de operação que existe: volume de reclamação, índice
de resposta, tempo e taxa de solução. Os quatro estudos concluíram que a ferida
da rede é operação, e nenhuma outra fonte mede isso.

O actor mudou em 08/08/2026, e a troca corrigiu um erro grave: o anterior
(viralanalyzer) devolvia sempre 3 reclamações, e com 3 a gente concluiu que
"a marca não responde". Os números reais são 3.133 reclamações, 98,6%
respondidas e 63,3% que voltariam a fazer negócio. Amostra de três não
descreve uma rede de 340 unidades.

Duas armadilhas descobertas na construção:
  · o site é protegido por Cloudflare — acesso direto devolve 403. Precisa do
    actor com PROXY RESIDENCIAL declarado (o plano grátis tem 20 GB).
  · o run precisa de timeout longo (>=600s); com 280s o actor devolve um
    diagnóstico em vez de dados, e ainda por cima busca o slug errado se
    `companies` não for passado.

O slug é da MARCA, não da unidade — o Reclame Aqui não separa por franquia.
Então este número é da rede inteira, e é assim que ele deve ser lido.

Uso:
    python3 coleta/coletores/reclame_aqui.py --n 25
    python3 coleta/coletores/reclame_aqui.py --empresa odontocompany --n 15
"""
import argparse, json, os, pathlib, re, sys, urllib.request
import datetime as dt
from collections import Counter

RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent
SERIE = RAIZ/"dados"/"serie"
BRUTO = RAIZ/"dados"/"bruto"
ACTOR = "webdata_labs~reclameaqui-scraper"
API = "https://api.apify.com/v2"


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


def limpa(h):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h or "")).strip()


def jsonl(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--empresa", default="orthodontic", help="slug no Reclame Aqui")
    ap.add_argument("--n", type=int, default=20, help="máx. reclamações por empresa (teto 20)")
    ap.add_argument("--tambem", action="append", default=[],
                    help="outra empresa na mesma corrida (comparar sem comparar é inútil)")
    args = ap.parse_args()

    hoje = dt.date.today().isoformat()
    tok = token()
    empresas = [args.empresa] + args.tambem
    print(f"{len(empresas)} empresa(s): {', '.join(empresas)} · até {args.n} reclamações cada")

    # maxItems é obrigatório: o actor cobra por resultado e recusa rodar sem teto.
    teto = len(empresas) * (min(args.n, 20) + 1)
    url = (f"{API}/acts/{ACTOR}/run-sync-get-dataset-items"
           f"?token={tok}&timeout=900&memory=2048&maxItems={teto}")
    # O formato é do webdata_labs, que substituiu o viralanalyzer em 08/08/2026.
    # Trocar o actor sem trocar o pedido devolve HTTP 400 — aconteceu.
    req = urllib.request.Request(url, data=json.dumps({
        "companies": empresas,
        "maxComplaintsPerCompany": min(args.n, 20),
        "includeCompanyRecord": True, "includeBreakdowns": True, "delayMs": 1200,
    }).encode(), headers={"Content-Type": "application/json"}, method="POST")
    try:
        itens = json.loads(urllib.request.urlopen(req, timeout=900).read())
    except Exception as e:
        sys.exit(f"falhou: {type(e).__name__} · {str(e)[:200]}")

    # O webdata_labs devolve um registro por EMPRESA (recordType=company) e um
    # por reclamação. O actor anterior devolvia tudo achatado — reaproveitar o
    # parsing antigo fazia o dado chegar e não ser gravado, calado.
    fichas = [i for i in itens if i.get("recordType") == "company"]
    reclam = [i for i in itens if i.get("recordType") != "company" and i.get("id")]
    if not fichas:
        print("nenhuma ficha de empresa — retorno:")
        print(json.dumps(itens[:1], ensure_ascii=False, indent=1)[:600])
        return

    d = BRUTO/"_rede"/"reclame_aqui"/hoje
    d.mkdir(parents=True, exist_ok=True)
    (d/f"{'_'.join(empresas)[:60]}.json").write_text(
        json.dumps(itens, ensure_ascii=False, indent=1), encoding="utf-8")

    # append-only, como manda o contrato. Reescrever o arquivo já apagou dado
    # do mesmo dia uma vez.
    vistas = {r.get("chave") for r in jsonl(SERIE/"reclamacoes.jsonl")}
    novas = 0
    with (SERIE/"reclamacoes.jsonl").open("a", encoding="utf-8") as f:
        for r in reclam:
            chave = f"{r.get('companySlug')}|{r.get('id')}"
            if chave in vistas:
                continue
            vistas.add(chave)
            f.write(json.dumps({
                "chave": chave, "snapshot_date": hoje, "empresa": r.get("companySlug"),
                "complaint_id": r.get("id"), "titulo": r.get("title"),
                "descricao": limpa(r.get("description"))[:1500],
                "status": r.get("status"), "resolvida": r.get("solved"),
                "avaliada": r.get("evaluated"), "criada_em": r.get("created"),
                "url": r.get("url"),
                "first_seen_snapshot": hoje, "last_seen_snapshot": hoje,
            }, ensure_ascii=False) + "\n")
            novas += 1

    with (SERIE/"reclamacoes_agregado.jsonl").open("a", encoding="utf-8") as f:
        for e in fichas:
            i12 = e.get("companyIndex12Months") or {}
            f.write(json.dumps({
                "snapshot_date": hoje, "escopo": "marca",
                "empresa": e.get("companySlug"), "nome": e.get("companyName"),
                "nota_ra": e.get("consumerScore"), "nota_12m": i12.get("finalScore"),
                "selo_12m": i12.get("status"),
                "reclamacoes_total": e.get("complaintsTotal"),
                "reclamacoes_12m": i12.get("totalComplains"),
                "reclamacoes_30d": i12.get("totalComplains30"),
                "respondidas_pct": i12.get("answeredPercentual"),
                "resolvidas_pct": i12.get("solvedPercentual"),
                "voltaria_pct": i12.get("dealAgainPercentual"),
                "tempo_resposta_h": round((i12.get("averageAnswerTime") or 0)/3600, 1),
                "nao_respondidas_12m": i12.get("totalNotAnswered"),
                "segmento": e.get("mainSegment"), "amostra_n": min(args.n, 20),
                "fonte": f"apify {ACTOR}",
                "filtro": f"maxComplaintsPerCompany={min(args.n,20)} includeBreakdowns",
            }, ensure_ascii=False) + "\n")

    print(f"\n{'nota':>5s} {'total':>7s} {'resp':>6s} {'resolv':>7s} {'volta':>6s}  selo · empresa")
    for e in sorted(fichas, key=lambda x: -(x.get("complaintsTotal") or 0)):
        i12 = e.get("companyIndex12Months") or {}
        print(f"{str(e.get('consumerScore')):>5s} {str(e.get('complaintsTotal')):>7s} "
              f"{str(i12.get('answeredPercentual')):>5s}% {str(i12.get('solvedPercentual')):>6s}% "
              f"{str(i12.get('dealAgainPercentual')):>5s}%  {i12.get('status')} · {e.get('companyName')}")
    print(f"\n{novas} reclamações novas na série · {len(fichas)} fichas de empresa")


if __name__ == "__main__":
    main()
