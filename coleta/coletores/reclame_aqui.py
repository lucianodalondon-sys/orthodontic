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
    ap.add_argument("--n", type=int, default=25, help="máx. reclamações (US$ 0,09 cada)")
    args = ap.parse_args()

    hoje = dt.date.today().isoformat()
    tok = token()
    print(f"empresa '{args.empresa}' · até {args.n} reclamações · custo estimado US$ {args.n*0.09:.2f}")

    url = f"{API}/acts/{ACTOR}/run-sync-get-dataset-items?token={tok}&timeout=700&memory=1024"
    req = urllib.request.Request(url, data=json.dumps({
        "companies": [args.empresa], "maxComplaints": args.n,
        "includeCompanyStats": True,
        "proxyConfiguration": {"useApifyProxy": True, "apifyProxyGroups": ["RESIDENTIAL"]},
    }).encode(), headers={"Content-Type": "application/json"}, method="POST")
    try:
        itens = json.loads(urllib.request.urlopen(req, timeout=900).read())
    except Exception as e:
        sys.exit(f"falhou: {type(e).__name__} · {str(e)[:200]}")

    reais = [i for i in itens if i.get("complaint_id")]
    if not reais:
        print("nenhuma reclamação — retorno de diagnóstico:")
        print(json.dumps(itens[:1], ensure_ascii=False, indent=1)[:800])
        return

    d = BRUTO/"_rede"/"reclame_aqui"/hoje
    d.mkdir(parents=True, exist_ok=True)
    (d/f"{args.empresa}.json").write_text(json.dumps(itens, ensure_ascii=False, indent=1), encoding="utf-8")

    # agregado da empresa — vem repetido em cada reclamação
    a = reais[0]
    agregado = {
        "snapshot_date": hoje, "escopo": "marca", "empresa": args.empresa,
        "nome": a.get("company_name"), "nota_ra": a.get("company_score"),
        "reclamacoes_total": a.get("company_total_complaints"),
        "voltaria_a_fazer_negocio_pct": a.get("company_would_buy_again"),
        "indice_resposta_declarado": a.get("company_response_rate"),
        "taxa_solucao_declarada": a.get("company_resolve_rate"),
        "amostra_n": len(reais),
        "amostra_nao_respondidas": sum(1 for r in reais if (r.get("status") or "").lower().startswith("não resp")),
        "amostra_resolvidas": sum(1 for r in reais if r.get("is_resolved")),
        "categorias": dict(Counter(r.get("category") or "?" for r in reais)),
        "fonte": "apify/viralanalyzer-reclameaqui",
    }

    recs = {r["chave"]: r for r in jsonl(SERIE/"reclamacoes.jsonl")}
    novas = 0
    for r in reais:
        chave = f"{args.empresa}|{r['complaint_id']}"
        if chave in recs:
            recs[chave]["last_seen_snapshot"] = hoje
            recs[chave]["status"] = r.get("status")
            recs[chave]["resolvida"] = bool(r.get("is_resolved"))
            continue
        recs[chave] = {
            "chave": chave, "snapshot_date": hoje, "empresa": args.empresa,
            "complaint_id": r["complaint_id"], "titulo": r.get("title"),
            "descricao": limpa(r.get("description"))[:900],
            "categoria": r.get("category"), "status": r.get("status"),
            "resolvida": bool(r.get("is_resolved")),
            "respondida": bool(r.get("company_response")),
            "criada_em": r.get("created_at"), "url": r.get("url"),
            "first_seen_snapshot": hoje, "last_seen_snapshot": hoje,
        }
        novas += 1

    with (SERIE/"reclamacoes.jsonl").open("w", encoding="utf-8") as f:
        for r in sorted(recs.values(), key=lambda r: r.get("criada_em") or ""):
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    ag = [x for x in jsonl(SERIE/"reclamacoes_agregado.jsonl") if x.get("snapshot_date") != hoje]
    with (SERIE/"reclamacoes_agregado.jsonl").open("w", encoding="utf-8") as f:
        for x in ag + [agregado]:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")

    print(f"\n{agregado['nome']} · nota {agregado['nota_ra']} · "
          f"{agregado['reclamacoes_total']} reclamações no total")
    print(f"voltaria a fazer negócio: {agregado['voltaria_a_fazer_negocio_pct']}%")
    print(f"amostra: {len(reais)} · não respondidas {agregado['amostra_nao_respondidas']} · "
          f"resolvidas {agregado['amostra_resolvidas']} · {novas} novas na série")
    print("\ncategorias:")
    for k, v in Counter(r.get("category") or "?" for r in reais).most_common():
        print(f"  {k:34s} {v:3d}  {round(100*v/len(reais)):3d}%")
    print("\nas mais recentes:")
    for r in sorted(reais, key=lambda r: r.get("created_at") or "", reverse=True)[:6]:
        print(f"  [{(r.get('status') or '?')[:16]:16s}] {(r.get('created_at') or '')[:10]} {r.get('title','')[:78]}")


if __name__ == "__main__":
    main()
