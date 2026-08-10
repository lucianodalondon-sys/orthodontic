#!/usr/bin/env python3
"""
google_reviews.py — coletor de avaliações do Google via Apify (REST direto).

Não usa o apify-client: o cliente Python não atravessa o proxy desta máquina.
Fala com a API REST por urllib, que passa.

Grava DOIS níveis, conforme dados/CONTRATO.md:
  dados/bruto/<praca>/google/<snapshot>/<local_id>.json   imutável, o que veio
  dados/serie/places.jsonl                                append-only, a ponta
  dados/serie/reviews.jsonl                               append-only, com first_seen

De first_seen sai a VELOCITY de graça — reviews novos por mês, por clínica.
Era o dado mais forte do estudo de Mafra e era calculado à mão.

Uso:
    python3 coleta/coletores/google_reviews.py --praca mafra
    python3 coleta/coletores/google_reviews.py --praca mafra --max-reviews 150
    python3 coleta/coletores/google_reviews.py --todas --dry-run
"""
import argparse, json, os, pathlib, sys, time, urllib.error, urllib.request
import datetime as dt

RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent
IDENT = RAIZ/"dados"/"identidade"
SERIE = RAIZ/"dados"/"serie"
BRUTO = RAIZ/"dados"/"bruto"
ACTOR = "compass~crawler-google-places"
API = "https://api.apify.com/v2"

# query por local — o que o actor busca. Sem isso ele acha o lugar errado.
QUERIES = {
 "mafra": {
   "ortho_mafra": ("OrthoDontic Mafra SC", ["orthodontic"]),
   "lumiere": ("Instituto Lumière Odontologia Mafra SC", ["lumi"]),
   "oc_mafra": ("OdontoCompany Mafra SC", ["odontocompany"]),
   "oc_rionegro": ("OdontoCompany Rio Negro PR", ["odontocompany"]),
   "cuidado_prevencao": ("Clínica Cuidado e Prevenção Mafra SC", ["cuidado"]),
   "edgard_goes": ("Edgard Góes Odontologia Rio Negro PR", ["góes", "goes"]),
 },
 "londrina": {
   "ortho_souza_naves": ("OrthoDontic Londrina Souza Naves", ["orthodontic"]),
   "ortho_centro_ldn": ("OrthoDontic Londrina Rua Sergipe Centro", ["orthodontic"]),
   "odontoclinic_ldn": ("Odontoclinic Londrina", ["odontoclinic"]),
   "aline_oliver": ("Oliver Odonto Prime Londrina aparelho ortodôntico", ["oliver"]),
   "dentel_ldn": ("Clínica Dentel Saul Elkind Londrina", ["dentel"]),
 },
 "feira": {
   "ortho_fsa": ("OrthoDontic Feira de Santana", ["orthodontic"]),
   "gigante_fsa": ("Odontoclinic Feira de Santana", []),
   "oc_fsa": ("OdontoCompany Feira de Santana", ["odontocompany"]),
   "uefs_fsa": ("UEFS clínica odontológica Feira de Santana", []),
 },
 "prudente": {
   "ortho_pp": ("OrthoDontic Presidente Prudente", ["orthodontic"]),
   "dentoclinic_pp": ("Dentoclinic Presidente Prudente", ["dento"]),
   "todos_sorrindo_pp": ("Todos Sorrindo Odontologia Presidente Prudente", ["sorrindo"]),
   "nexa_pp": ("NEXA Odonto Presidente Prudente", ["nexa"]),
   "croorto_pp": ("Croorto Odontologia Presidente Prudente", ["croorto"]),
   "sorrifacil_pp": ("Sorrifácil Presidente Prudente", ["sorri"]),
 },
}


def alvos_da_praca(praca):
    """De onde sai a lista de clínicas de uma praça.

    Antes vinha do dicionário QUERIES, escrito a mão dentro deste arquivo.
    Isso tinha dois defeitos: não escalava (340 unidades não cabem num dict) e
    deixava praça de fora sem avisar — Cuiabá foi coletada inteira por script
    descartável porque `--praca cuiaba` devolvia 0 locais.

    Agora sai de dados/identidade/<praca>.json, que é a âncora do contrato.
    Quando o local tem place_id, buscamos por ele: é exato, enquanto buscar
    por nome já casou 'OrthoDontic Prudente' com a concorrente Bongiovanni.
    """
    arq = RAIZ/"dados"/"identidade"/f"{praca}.json"
    if not arq.exists():
        return {}
    ident = json.loads(arq.read_text(encoding="utf-8"))
    fora = {}
    for loc in ident.get("locais", []):
        lid = loc.get("local_id")
        if not lid:
            continue
        pid = loc.get("place_id")
        if pid:
            fora[lid] = {"place_id": pid, "rotulo": loc.get("nome") or lid, "exigidos": []}
        else:
            legado = QUERIES.get(praca, {}).get(lid)
            if legado:
                fora[lid] = {"query": legado[0], "rotulo": legado[0], "exigidos": legado[1]}
            else:
                fora[lid] = {"pendente": True, "rotulo": loc.get("nome") or lid}
    return fora


# Contas FREE de US$ 5 não atravessam uma varredura de avaliações — a de
# Prudente sozinha tem 592 para ler. A lista de tokens fica na mão e o coletor
# troca quando um estoura, em vez de parar no meio e gravar meia unidade.
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
        print(f"    ↻ token estourado, indo para o {self.i+1}º de {len(self.fila)}")
        return True


def sem_cota(d):
    return "hard limit" in str(d)


def token():
    return Cota().atual()


def post(url, body, tok, timeout=900):
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {tok}"},
        method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def get(url, tok, timeout=180):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {tok}"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def roda_lote(alvos, max_reviews, tok):
    """Manda TODAS as clínicas da praça numa corrida só.

    Antes era uma corrida por clínica, sequencial: 15 clínicas estouravam
    qualquer paciência e pagavam a taxa de início 15 vezes. O actor aceita
    várias startUrls — e como agora temos place_id de todo mundo, dá para
    mandar tudo junto.

    Só serve para alvos com place_id. Quem ainda depende de busca por nome
    continua indo um a um, porque searchStringsArray misturaria os resultados.
    """
    urls = [{"url": "https://www.google.com/maps/place/?q=place_id:" + a["place_id"]}
            for a in alvos]
    url = (f"{API}/acts/{ACTOR}/run-sync-get-dataset-items"
           f"?token={tok}&timeout=2400&memory=8192")
    return post(url, {
        "startUrls": urls, "maxCrawledPlacesPerSearch": 1, "language": "pt-BR",
        "reviewsSort": "newest", "maxReviews": max_reviews,
        "scrapeReviewsPersonalData": False, "onlyDataFromSearchPage": False,
    }, tok, timeout=2600)


def roda(alvo, max_reviews, tok):
    """Com rotação: se o token estourar no meio, troca e refaz a chamada."""
    if isinstance(tok, Cota):
        while True:
            d = _roda_uma(alvo, max_reviews, tok.atual())
            if isinstance(d, list) or not sem_cota(d) or not tok.queimou():
                return d
    return _roda_uma(alvo, max_reviews, tok)


def roda_async(corpo, tok, espera=1800):
    """Dispara o run e busca o resultado em chamadas CURTAS, para o proxy não cortar.

    O run-sync-get-dataset-items segura a conexão aberta pelo tempo inteiro do
    actor — minutos — e o proxy derruba com RemoteDisconnected. Prudente caiu
    DUAS vezes assim, com 600 e com 300 avaliações. Aqui são três chamadas
    pequenas: inicia, consulta o status a cada 15 s, baixa o dataset no fim."""
    import time as _t
    d = post(f"{API}/acts/{ACTOR}/runs?token={tok}&memory=4096", corpo, tok,
             timeout=120)
    run = (d.get("data") or {})
    rid, did = run.get("id"), run.get("defaultDatasetId")
    if not rid:
        return d
    gasto = 0
    while gasto < espera:
        _t.sleep(15); gasto += 15
        st = get(f"{API}/actor-runs/{rid}?token={tok}", tok, timeout=60)
        status = (st.get("data") or {}).get("status")
        if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            break
    if status != "SUCCEEDED":
        return {"error": f"run {status}"}
    return get(f"{API}/datasets/{did}/items?token={tok}&clean=true", tok,
               timeout=300)


def _roda_uma(alvo, max_reviews, tok):
    """Roda o actor e espera. run-sync-get-dataset-items devolve os itens direto.

    Por place_id quando existe (exato), por nome só como retaguarda.
    """
    corpo = {"maxCrawledPlacesPerSearch": 1, "language": "pt-BR",
             "reviewsSort": "newest", "maxReviews": max_reviews,
             "scrapeReviewsPersonalData": False, "onlyDataFromSearchPage": False}
    if alvo.get("place_id"):
        corpo["startUrls"] = [{"url": "https://www.google.com/maps/place/?q=place_id:"
                                      + alvo["place_id"]}]
    else:
        corpo["searchStringsArray"] = [alvo["query"]]
    return roda_async(corpo, tok)


def jsonl_le(p):
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").split("\n") if l.strip()]


def jsonl_grava(p, rows):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--praca")
    ap.add_argument("--todas", action="store_true")
    ap.add_argument("--max-reviews", type=int, default=120)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--so-local", help="só um local_id")
    args = ap.parse_args()

    pracas = list(QUERIES) if args.todas else ([args.praca] if args.praca else [])
    if not pracas:
        sys.exit("use --praca <id> ou --todas")

    hoje = dt.date.today().isoformat()
    tok = Cota()

    places = {(r["local_id"], r["snapshot_date"]): r for r in jsonl_le(SERIE/"places.jsonl")}
    reviews = {r["chave"]: r for r in jsonl_le(SERIE/"reviews.jsonl")}

    sem_credito = False
    for praca in pracas:
        if sem_credito:
            break
        alvos = alvos_da_praca(praca)
        if args.so_local:
            alvos = {k: v for k, v in alvos.items() if k == args.so_local}
        pend = [k for k, v in alvos.items() if v.get("pendente")]
        alvos = {k: v for k, v in alvos.items() if not v.get("pendente")}
        por_id = sum(1 for v in alvos.values() if v.get("place_id"))
        print(f"\n=== {praca} · {len(alvos)} locais ({por_id} por place_id) · corte {hoje} ===")
        if pend:
            print(f"  ⚠ {len(pend)} sem place_id e sem query: {', '.join(pend)}")
        # Uma corrida só para todo mundo que tem place_id; o resto vai um a um.
        lote = {k: v for k, v in alvos.items() if v.get("place_id")}
        avulsos = {k: v for k, v in alvos.items() if not v.get("place_id")}
        colhido = {}
        if lote and not args.dry_run:
            print(f"  [lote] {len(lote)} clínicas numa corrida só...")
            try:
                for it in roda_lote(list(lote.values()), args.max_reviews, tok):
                    if it.get("placeId"):
                        colhido[it["placeId"]] = it
                print(f"  [lote] voltaram {len(colhido)}")
            except Exception as e:
                print(f"  [lote FALHOU] {type(e).__name__} · {str(e)[:120]} — caindo para um a um")

        for local_id, alvo in alvos.items():
            query = alvo.get("query") or alvo.get("place_id")
            exigidos = alvo.get("exigidos", [])
            if args.dry_run:
                como = "place_id" if alvo.get("place_id") else "nome"
                print(f"  [dry] {local_id:24s} por {como:8s} {alvo['rotulo'][:40]}")
                continue
            pronto = colhido.get(alvo.get("place_id"))
            if pronto:
                itens = [pronto]
                try:
                    pass
                except Exception:
                    pass
            else:
              try:
                itens = roda(alvo, args.max_reviews, tok)
              except urllib.error.HTTPError as e:
                corpo = e.read().decode()[:300]
                # Crédito acabado não melhora na próxima clínica. Parar e dizer
                # vale mais que repetir o mesmo 402 catorze vezes.
                if e.code == 402 or "not-enough-usage" in corpo:
                    print(f"\n  [PAROU] a conta da Apify acabou.")
                    print(f"  {corpo[corpo.find('message'):][:150]}")
                    print("  Troque APIFY_TOKEN em _pipeline/.env e rode de novo:")
                    print(f"    python3 coleta/coletores/google_reviews.py --praca {praca}")
                    print("  O que já foi coletado até aqui será gravado.")
                    sem_credito = True
                    break
                print(f"  [ERRO] {local_id}: HTTP {e.code} · {corpo[:180]}")
                continue
              except Exception as e:
                print(f"  [ERRO] {local_id}: {type(e).__name__} · {str(e)[:150]}")
                continue

            if not itens:
                print(f"  [VAZIO] {local_id} · '{query}'")
                continue
            lugar = itens[0]
            titulo = lugar.get("title") or ""
            if exigidos and not any(e in titulo.lower() for e in exigidos):
                print(f"  [RECUSADO] {local_id}: achou '{titulo}', não casa com {exigidos}")
                continue

            d = BRUTO/praca/"google"/hoje
            d.mkdir(parents=True, exist_ok=True)
            (d/f"{local_id}.json").write_text(
                json.dumps(lugar, ensure_ascii=False, indent=2), encoding="utf-8")

            rs = lugar.get("reviews") or []
            novos = 0
            for r in rs:
                rid = r.get("reviewId") or r.get("reviewUrl") or f"{r.get('publishedAtDate')}|{(r.get('text') or '')[:40]}"
                chave = f"{local_id}|{rid}"
                if chave in reviews:
                    reviews[chave]["last_seen_snapshot"] = hoje
                    continue
                txt = (r.get("text") or "").strip()
                reviews[chave] = {
                    "chave": chave, "snapshot_date": hoje, "praca_id": praca,
                    "local_id": local_id, "plataforma": "google",
                    "nota": r.get("stars"), "texto": txt, "tem_texto": bool(txt),
                    "data": r.get("publishedAtDate") or r.get("publishAt"),
                    "respondida": bool(r.get("responseFromOwnerText")),
                    "resposta_data": r.get("responseFromOwnerDate"),
                    "curtidas": r.get("likesCount") or 0,
                    "first_seen_snapshot": hoje, "last_seen_snapshot": hoje,
                }
                novos += 1

            places[(local_id, hoje)] = {
                "snapshot_date": hoje, "praca_id": praca, "local_id": local_id,
                "place_id": lugar.get("placeId"), "titulo": titulo,
                "nota": lugar.get("totalScore"),
                "avaliacoes_total": lugar.get("reviewsCount"),
                "reviews_coletados": len(rs),
                "reviews_com_texto": sum(1 for r in rs if (r.get("text") or "").strip()),
                "endereco": lugar.get("address"), "categoria": lugar.get("categoryName"),
                "url": lugar.get("url"), "fonte": "apify/compass-crawler-google-places",
                "first_seen_snapshot": hoje, "last_seen_snapshot": hoje,
            }
            print(f"  {local_id:22s} {titulo[:34]:34s} {lugar.get('totalScore')} · "
                  f"{lugar.get('reviewsCount')} aval · {len(rs)} puxadas · {novos} novos")
            time.sleep(1)

    if args.dry_run:
        return
    jsonl_grava(SERIE/"places.jsonl", sorted(places.values(), key=lambda r: (r["snapshot_date"], r["local_id"])))
    jsonl_grava(SERIE/"reviews.jsonl", sorted(reviews.values(), key=lambda r: (r["local_id"], r.get("data") or "")))
    print(f"\nplaces.jsonl: {len(places)} linhas · reviews.jsonl: {len(reviews)} linhas")


if __name__ == "__main__":
    main()
