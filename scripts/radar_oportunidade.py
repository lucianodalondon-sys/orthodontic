#!/usr/bin/env python3
"""
radar_oportunidade.py — onde a rede deveria estar e não está.

É o único produto do projeto que entra na RECEITA da franqueadora em vez da
despesa: ela vive de vender franquia, e a pergunta do time de expansão é uma só
— onde vale abrir?

Lá fora isso se chama white space analysis e custa caro (SiteSeer, GrowthFactor,
FranConnect). A diferença é que essas ferramentas medem demografia e
concorrência de fora; nós medimos a **categoria real da cidade**, clínica por
clínica, com nota e volume.

Mede quatro coisas por cidade, todas públicas:

  1. o TAMANHO — população, e o alvo por faixa de idade (o adulto de 30-45 é
     2,5 a 3× maior que o adolescente em toda praça que medimos)
  2. a FORÇA DA CATEGORIA — quantas clínicas passam de 300 avaliações, e qual
     o volume do líder
  3. a FOLGA — habitantes por clínica forte. Em Marabá é uma para cada 97 mil;
     em Contagem, uma para cada 15 mil
  4. se a REDE JÁ ESTÁ LÁ — pelo site orthodonticbrasil.com.br, que é exato

E não mede, de propósito:
  · população diurna, que a literatura diz prever melhor a demanda e que o IBGE
    não publica de graça
  · tempo de deslocamento real, que precisaria de API de rotas
  Os dois viram ressalva no relatório, não silêncio.

Uso:
    python3 scripts/radar_oportunidade.py --cidade "Marabá/PA"
    python3 scripts/radar_oportunidade.py --lista cidades.txt --salvar
    python3 scripts/radar_oportunidade.py --top-mg          # exemplo de lote
"""
import argparse, json, os, pathlib, re, subprocess, sys, time, urllib.parse
import datetime as dt

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SERIE = RAIZ/"dados"/"serie"
IBGE = "https://servicodados.ibge.gov.br"
API = "https://places.googleapis.com/v1/places:searchText"
CAMPOS = ("places.id,places.displayName,places.rating,places.userRatingCount,"
          "places.formattedAddress,places.websiteUri")
TERMOS = ["ortodontia", "aparelho ortodôntico", "clínica odontológica", "dentista"]
FORTE = 300          # avaliações que definem uma clínica "forte" na praça

# Faixas do Censo 2022 (agregado 9514) — o alvo real
FAIXAS = {"93084": "5a9", "93085": "10a14", "93086": "15a19",
          "93089": "30a34", "93090": "35a39", "93091": "40a44"}


def chave():
    k = os.environ.get("GOOGLE_API_KEY", "").strip()
    if not k:
        env = RAIZ/"_pipeline"/".env"
        if env.exists():
            for l in env.read_text(encoding="utf-8").splitlines():
                l = l.strip().replace("\r", "")
                if l.startswith("GOOGLE_API_KEY="):
                    k = l.split("=", 1)[1].strip()
    if not k:
        sys.exit("GOOGLE_API_KEY ausente em _pipeline/.env")
    return k


def curl(url, *a, tent=3):
    for i in range(tent):
        r = subprocess.run(["curl", "-sS", "-m", "40", "-H", "User-Agent: Mozilla/5.0",
                            *a, url], capture_output=True, text=True)
        if r.stdout.strip():
            try:
                return json.loads(r.stdout)
            except Exception:
                return None
        time.sleep(2*(i+1))
    return None


def ibge(cidade):
    nome, uf = [x.strip() for x in cidade.split("/")]
    d = curl(f"{IBGE}/api/v1/localidades/municipios?nome={urllib.parse.quote(nome)}")
    mid = None
    for m in (d or []):
        if (m["nome"].lower() == nome.lower()
                and m["microrregiao"]["mesorregiao"]["UF"]["sigla"].upper() == uf.upper()):
            mid = m["id"]; break
    if not mid:
        return None
    fora = {"ibge_id": mid}
    p = curl(f"{IBGE}/api/v3/agregados/6579/periodos/-1/variaveis/9324?localidades=N6%5B{mid}%5D")
    try:
        fora["populacao"] = int(list(p[0]["resultados"][0]["series"][0]["serie"].values())[-1])
    except Exception:
        fora["populacao"] = None
    q = curl(f"{IBGE}/api/v3/agregados/9514/periodos/2022/variaveis/93"
             f"?localidades=N6%5B{mid}%5D&classificacao=287%5B{','.join(FAIXAS)}%5D")
    faixa = {}
    for r in (q or [{}])[0].get("resultados", []):
        cat = r.get("classificacoes", [{}])[0].get("categoria", {})
        for cod in cat:
            try:
                faixa[FAIXAS[cod]] = int(list(r["series"][0]["serie"].values())[0])
            except Exception:
                pass
    if faixa:
        fora["alvo_9_15"] = round(faixa.get("5a9", 0)*0.2 + faixa.get("10a14", 0)
                                  + faixa.get("15a19", 0)*0.2)
        fora["alvo_30_45"] = (faixa.get("30a34", 0) + faixa.get("35a39", 0)
                              + faixa.get("40a44", 0))
    return fora


def categoria(cidade, key):
    vistos = {}
    for t in TERMOS:
        d = curl(f"{API}", "-X", "POST", "-H", "Content-Type: application/json",
                 "-H", f"X-Goog-Api-Key: {key}", "-H", f"X-Goog-FieldMask: {CAMPOS}",
                 "-d", json.dumps({"textQuery": f"{t} {cidade}", "languageCode": "pt-BR",
                                   "maxResultCount": 20}, ensure_ascii=False))
        for p in (d or {}).get("places", []):
            pid = p.get("id")
            end = (p.get("formattedAddress") or "").lower()
            nome_cid = cidade.split("/")[0].lower()
            if pid and pid not in vistos and nome_cid.split()[-1] in end:
                vistos[pid] = p
    return list(vistos.values())


def analisa(cidade, key):
    n = ibge(cidade)
    if not n:
        return {"cidade": cidade, "erro": "não achei no IBGE — confira grafia e UF"}
    cs = categoria(cidade, key)
    fortes = [p for p in cs if (p.get("userRatingCount") or 0) >= FORTE]
    lider = max((p.get("userRatingCount") or 0) for p in cs) if cs else 0
    da_rede = [p for p in cs
               if "orthodonticbrasil.com.br" in (p.get("websiteUri") or "").lower()]
    pop = n.get("populacao") or 0
    nome, uf = [x.strip() for x in cidade.split("/")]
    return {
        "rotulo": f"{uf} · {nome}", "cidade": cidade, **n,
        "clinicas_amostradas": len(cs), "clinicas_fortes": len(fortes),
        "lider_avaliacoes": lider,
        "avaliacoes_somadas": sum(p.get("userRatingCount") or 0 for p in cs),
        "hab_por_clinica_forte": round(pop/len(fortes)) if fortes and pop else None,
        "unidades_da_rede": len(da_rede),
        "nomes_da_rede": [p["displayName"]["text"] for p in da_rede],
        "maiores": [{"nome": p["displayName"]["text"],
                     "avaliacoes": p.get("userRatingCount"), "nota": p.get("rating")}
                    for p in sorted(cs, key=lambda x: -(x.get("userRatingCount") or 0))[:5]],
    }


def leitura(r):
    """A frase que o time de expansão lê. Nota sem frase não decide nada."""
    if r.get("erro"):
        return r["erro"]
    if r["unidades_da_rede"]:
        return f"a rede já está lá ({r['unidades_da_rede']} unidade(s))"
    pop, hab = r.get("populacao") or 0, r.get("hab_por_clinica_forte")
    if pop < 80_000:
        return "cidade pequena — mercado pode não sustentar"
    if r["lider_avaliacoes"] >= 1500:
        return "mercado brigado — entrar custa caro"
    if hab and hab >= 60_000 and pop >= 150_000:
        return "OPORTUNIDADE — cidade grande com categoria fraca"
    if r["clinicas_fortes"] <= 2 and pop >= 100_000:
        return "OPORTUNIDADE — quase ninguém forte na praça"
    return "mercado normal"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cidade", action="append", default=[])
    ap.add_argument("--lista", help="arquivo com uma cidade por linha (Nome/UF)")
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()
    cidades = list(a.cidade)
    if a.lista:
        cidades += [l.strip() for l in pathlib.Path(a.lista).read_text(encoding="utf-8").splitlines()
                    if l.strip() and "/" in l]
    if not cidades:
        sys.exit('use --cidade "Marabá/PA" (pode repetir) ou --lista arquivo.txt')

    key = chave()
    print(f"\n{'='*80}\n  RADAR DE OPORTUNIDADE · {len(cidades)} cidades · "
          f"~US$ {0.05*len(cidades):.2f}\n{'='*80}\n")
    print(f"  {'pop':>9s} {'9-15':>7s} {'30-45':>7s} {'fortes':>6s} {'líder':>6s} "
          f"{'hab/forte':>10s}  praça · leitura")
    fora = []
    for c in cidades:
        r = analisa(c, key)
        r["leitura"] = leitura(r)
        fora.append(r)
        if r.get("erro"):
            print(f"  {'—':>9s} {'':>7s} {'':>7s} {'':>6s} {'':>6s} {'':>10s}  {c}: {r['erro']}")
            continue
        print(f"  {r.get('populacao') or 0:>9,d} {r.get('alvo_9_15') or 0:>7,d} "
              f"{r.get('alvo_30_45') or 0:>7,d} {r['clinicas_fortes']:>6d} "
              f"{r['lider_avaliacoes']:>6d} {str(r.get('hab_por_clinica_forte') or '—'):>10s}  "
              f"{r['rotulo'][:24]:24s} {r['leitura']}")

    op = [r for r in fora if str(r.get("leitura", "")).startswith("OPORTUNIDADE")]
    if op:
        print(f"\n  {len(op)} OPORTUNIDADE(S):")
        for r in sorted(op, key=lambda x: -(x.get("alvo_30_45") or 0)):
            print(f"    {r['rotulo']} — {r.get('populacao') or 0:,} hab · "
                  f"{r.get('alvo_30_45') or 0:,} adultos de 30-45 · "
                  f"líder tem só {r['lider_avaliacoes']} avaliações")
            for m in r["maiores"][:3]:
                print(f"        {m['avaliacoes']:>5} {str(m['nota']):>4}  {m['nome'][:44]}")

    print("\n  RESSALVAS, e elas vão no relatório:")
    print("   · usa população RESIDENTE. A literatura diz que a diurna prevê melhor,")
    print("     e o IBGE não publica de graça.")
    print("   · a praça é o município, não o raio de deslocamento real.")
    print("   · mede a categoria pública do Google, não receita nem ticket.\n")

    if a.salvar:
        hoje = dt.date.today().isoformat()
        SERIE.mkdir(parents=True, exist_ok=True)
        with (SERIE/"oportunidade.jsonl").open("a", encoding="utf-8") as f:
            for r in fora:
                f.write(json.dumps({"snapshot_date": hoje, **r,
                                    "fonte": "google places api + ibge",
                                    "filtro": "|".join(TERMOS)}, ensure_ascii=False)+"\n")
        print(f"  → dados/serie/oportunidade.jsonl +{len(fora)}\n")


if __name__ == "__main__":
    main()
