#!/usr/bin/env python3
"""
sazonalidade.py — a curva de procura por aparelho, por REGIÃO, 5 anos.

O buraco que este coletor fecha: a série de sazonalidade tinha QUATRO
pontos, todos de SC, tirados à mão do estudo de Mafra. O portal
declarava a ausência ("ainda não medimos a curva desta cidade") em 12 das
13 praças, e o card "Quando a procura sobe" ficava apagado.

E não se herda curva: foi Mafra que derrubou a tese nacional de
"dezembro e janeiro são pico" — lá é VALE. Por isso a coleta é por UF,
nunca uma curva só para o Brasil inteiro.

A régua da granularidade: o Google Trends publica índice por REGIÃO
(UF), não por cidade. Uma cidade de 55 mil habitantes não tem volume que
o Trends publique sozinha. Então o campo se chama `regiao` e a tela diz
"curva do estado", não "curva da cidade" — dizer cidade seria inventar
precisão que o dado não tem.

Uso:
    python3 coleta/coletores/sazonalidade.py --praca mafra
    python3 coleta/coletores/sazonalidade.py --todas
    python3 coleta/coletores/sazonalidade.py --todas --nao-salvar
"""
import argparse, json, os, pathlib, ssl, sys, urllib.error, urllib.parse, urllib.request
import datetime as dt
from collections import defaultdict

RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent
SERIE = RAIZ/"dados"/"serie"
BRUTO = RAIZ/"dados"/"bruto"
IDENT = RAIZ/"dados"/"identidade"

ACTOR = "agenscrape~google-trends-scraper"
API = "https://api.apify.com/v2"
CA = "/root/.ccr/ca-bundle.crt"

# O TERMO É O PRODUTO. "ortodontia" traz curso e congresso de dentista;
# "sorriso" traz cidade de MT e frase de anúncio. "aparelho ortodôntico" é
# o que o paciente digita quando está decidindo.
TERMO = "aparelho ortodôntico"
JANELA = "today 5-y"          # 5 anos, a mesma série do estudo de Mafra
MESES = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN",
         "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]


def tokens():
    """Todos os tokens do arquivo, na ordem. A cota gratuita é pequena e o
    projeto já paga rotação: token que estoura passa a vez para o próximo."""
    fora = []
    env = RAIZ/"_pipeline"/".env"
    if env.exists():
        for l in env.read_text(encoding="utf-8").split("\n"):
            l = l.strip().replace("\r", "")
            if l.startswith("APIFY_TOKEN") and "=" in l:
                v = l.split("=", 1)[1].strip()
                if v:
                    fora.append(v)
    t = os.environ.get("APIFY_TOKEN", "").strip()
    if t:
        fora.insert(0, t)
    if not fora:
        sys.exit("nenhum APIFY_TOKEN em _pipeline/.env")
    return fora


def ctx():
    return ssl.create_default_context(cafile=CA) if pathlib.Path(CA).exists() else None


def post(url, corpo, timeout=120):
    req = urllib.request.Request(url, data=json.dumps(corpo).encode(),
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    with urllib.request.urlopen(req, timeout=timeout, context=ctx()) as r:
        return json.loads(r.read())


def get(url, timeout=180):
    with urllib.request.urlopen(url, timeout=timeout, context=ctx()) as r:
        return json.loads(r.read())


def uma_corrida(geo, tok, espera=900):
    """Dispara e busca em chamadas CURTAS — o proxy corta a longa.

    `run-sync-get-dataset-items` segura a conexão aberta por minutos e o
    proxy derruba com RemoteDisconnected. Foi assim que a coleta de
    avaliações de Prudente caiu duas vezes, e foi assim que a primeira
    tentativa deste coletor caiu também. São três chamadas: inicia,
    pergunta o status a cada 15 s, baixa o dataset no fim.
    """
    import time as _t
    # POR QUE ESTE ATOR. O `apify~google-trends-scraper` valida `geo` contra
    # uma lista de PAÍSES — "BR-SC" volta 400 — e, pela URL do Trends, o
    # navegador dele estoura em 60 s, 8 tentativas, zero itens. Este aceita
    # `geo` como texto e devolve `interestOverTime` semanal: 262 pontos em 5
    # anos para BR-SC. Curva nacional não serve: Mafra derrubou a tese do
    # país, e é a UF que decide campanha.
    d = post(f"{API}/acts/{ACTOR}/runs?token={tok}&memory=1024",
             {"keywords": [TERMO], "geo": geo, "timeRange": JANELA,
              "includeInterestOverTime": True,
              "includeRelatedSearches": False,
              "includeRelatedTopics": False})
    run = d.get("data") or {}
    rid, did = run.get("id"), run.get("defaultDatasetId")
    if not rid:
        return None, f"o ator não devolveu id de corrida: {str(d)[:120]}"
    gasto, status = 0, None
    while gasto < espera:
        _t.sleep(15)
        gasto += 15
        st = get(f"{API}/actor-runs/{rid}?token={tok}")
        status = (st.get("data") or {}).get("status")
        if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            break
    if status != "SUCCEEDED":
        return None, f"corrida terminou como {status}"
    return get(f"{API}/datasets/{did}/items?token={tok}&clean=true",
               timeout=300), None


def roda(geo, toks):
    """Uma corrida por região, trocando de token quando a cota estoura."""
    erro = None
    for i, tok in enumerate(toks):
        try:
            itens, e = uma_corrida(geo, tok)
            if itens is not None:
                return itens
            erro = e
            print(f"    token {i+1}: {e}")
        except urllib.error.HTTPError as e:
            erro = f"HTTP {e.code}"
            if e.code not in (401, 402, 403, 429):
                raise SystemExit(f"{geo}: {erro} · "
                                 f"{e.read()[:200].decode('utf-8', 'ignore')}")
            print(f"    token {i+1} sem cota ({e.code}), tentando o próximo")
        except Exception as e:
            erro = str(e)[:120]
            print(f"    token {i+1} falhou ({erro}), tentando o próximo")
    raise SystemExit(f"{geo}: nenhum token respondeu · último erro: {erro}")


def pontos(itens):
    """De `interestOverTime`, tira (data ISO, índice).

    O ator devolve UM item por palavra, com a série semanal dentro. `time`
    é epoch em segundos; `value` é o índice 0-100 do Google. Semana
    parcial (`isPartial`) fica de fora: ela sempre parece queda, e queda
    falsa no último ponto é o tipo de erro que vira decisão errada.
    """
    fora = []
    for x in itens or []:
        if not isinstance(x, dict):
            continue
        for s in (x.get("interestOverTime") or []):
            if s.get("isPartial"):
                continue
            t, v = s.get("time"), s.get("value")
            if t is None or v is None:
                continue
            try:
                d = dt.datetime.utcfromtimestamp(int(t))
            except (ValueError, TypeError, OSError):
                continue
            fora.append((d.strftime("%Y-%m-%d"), float(v)))
    return fora


# DOIS GUARDAS, os dois pagos com dado real desta coleta.
#
# VOLUME — no Acre a série veio ZERO em onze meses e 100 num único. O Trends
# zera o que é pequeno demais para publicar: semana zerada é ausência de
# MEDIÇÃO, não ausência de procura. Publicar "o pico do Acre é outubro" a
# partir disso seria inventar precisão.
#
# ESTABILIDADE — a média de 5 anos inventa pico onde não há. Em SC o pico cai
# em AGO em 4 dos 5 anos: é estação. No PR é ABR, JAN, JUN, MAR e JUL, um mês
# diferente por ano: é ruído — e a média ia publicar "o pico do Paraná é
# janeiro". Só publica curva cujo pico SE REPETE.
MIN_SEMANAS_COM_BUSCA = 0.55       # das 261 semanas
MIN_MESES_COM_BUSCA = 9            # dos 12
MIN_ANOS_COM_O_MESMO_PICO = 3      # dos 5


def volume(pares):
    total = len(pares)
    com = sum(1 for _, v in pares if v > 0)
    meses = {d[5:7] for d, v in pares if v > 0}
    return {"semanas": total, "semanas_com_busca": com,
            "meses_com_busca": len(meses),
            "volume_ok": (total > 0
                          and com/total >= MIN_SEMANAS_COM_BUSCA
                          and len(meses) >= MIN_MESES_COM_BUSCA)}


def estabilidade(pares):
    """O pico de cada ano, e quantas vezes o mesmo mês se repete."""
    from collections import Counter
    por_ano = defaultdict(lambda: defaultdict(list))
    for d, v in pares:
        por_ano[d[:4]][d[5:7]].append(v)
    picos = {}
    for ano, meses in por_ano.items():
        if len(meses) < 8:             # ano cortado no meio não vota
            continue
        medias = {m: sum(v)/len(v) for m, v in meses.items()}
        picos[ano] = MESES[int(max(medias, key=medias.get)) - 1]
    if not picos:
        return {"anos": {}, "pico_repete_em": 0, "anos_medidos": 0,
                "pico_mais_comum": None, "estavel": False}
    c = Counter(picos.values())
    mes, vezes = c.most_common(1)[0]
    return {"anos": picos, "pico_mais_comum": mes, "anos_medidos": len(picos),
            "pico_repete_em": vezes,
            "estavel": vezes >= MIN_ANOS_COM_O_MESMO_PICO}


def curva(pares):
    """A média de cada MÊS DO ANO ao longo dos 5 anos, normalizada em 0-100."""
    por_mes = defaultdict(list)
    for data, v in pares:
        m = None
        for f in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%b %d, %Y", "%d/%m/%Y"):
            try:
                m = dt.datetime.strptime(data[:len(dt.datetime.now().strftime(f))], f).month
                break
            except ValueError:
                continue
        if m:
            por_mes[m].append(v)
    if not por_mes:
        return []
    medias = {m: sum(v)/len(v) for m, v in por_mes.items()}
    topo = max(medias.values()) or 1
    return [{"mes": MESES[m-1], "indice": round(100*medias[m]/topo),
             "medicoes": len(por_mes[m])}
            for m in sorted(medias)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--praca")
    ap.add_argument("--todas", action="store_true")
    ap.add_argument("--nao-salvar", action="store_true")
    a = ap.parse_args()

    ids = {}
    for arq in sorted(IDENT.glob("*.json")):
        d = json.loads(arq.read_text(encoding="utf-8"))
        for uf in d.get("uf") or []:
            ids.setdefault(uf, []).append(d.get("rotulo") or arq.stem)
    if a.praca:
        d = json.loads((IDENT/f"{a.praca}.json").read_text(encoding="utf-8"))
        ufs = d.get("uf") or []
    elif a.todas:
        ufs = sorted(ids)
    else:
        sys.exit("use --praca <id> ou --todas")

    hoje = dt.date.today().isoformat()
    toks = tokens()
    BRUTO.mkdir(parents=True, exist_ok=True)
    linhas, veredito = [], []

    for uf in ufs:
        print(f"\n=== {uf} · {TERMO} · 5 anos ===")
        itens = roda(f"BR-{uf}", toks)
        (BRUTO/f"sazonalidade-{uf}-{hoje}.json").write_text(
            json.dumps(itens, ensure_ascii=False)[:5_000_000], encoding="utf-8")
        pares = pontos(itens)
        vol = volume(pares)
        est = estabilidade(pares)
        if pares and not vol["volume_ok"]:
            veredito.append({"regiao": uf, **vol, **est,
                             "publicavel": False, "porque": "sem_volume"})
            print(f"  {uf}: SEM VOLUME PUBLICÁVEL — só "
                  f"{vol['semanas_com_busca']} das {vol['semanas']} semanas "
                  f"têm busca, em {vol['meses_com_busca']} meses. O Trends "
                  f"zera o que é pequeno demais. Bruto salvo, NADA gravado.")
            continue
        if pares and not est["estavel"]:
            veredito.append({"regiao": uf, **vol, **est,
                             "publicavel": False, "porque": "pico_nao_repete"})
            anos = ", ".join(f"{a}:{m}" for a, m in sorted(est["anos"].items()))
            print(f"  {uf}: CURVA INSTÁVEL — o pico muda de mês a cada ano "
                  f"({anos}). A média de 5 anos publicaria um pico que não "
                  f"existe. Bruto salvo, NADA gravado.")
            continue
        c = curva(pares)
        if not c:
            print(f"  {uf}: o ator respondeu {len(itens or [])} itens e nenhum "
                  f"virou ponto — bruto salvo, NADA gravado na série")
            continue
        veredito.append({"regiao": uf, **vol, **est, "publicavel": True,
                         "porque": None})
        pico = max(c, key=lambda x: x["indice"])
        vale = min(c, key=lambda x: x["indice"])
        print(f"  {len(pares)} leituras · pico {pico['mes']} ({pico['indice']}) "
              f"· vale {vale['mes']} ({vale['indice']})")
        # a curva inteira na tela: pico sem os outros onze meses ao lado é
        # número solto, e número solto vira tese nacional errada
        for m in c:
            barra = "█" * max(1, round(m["indice"]/4))
            print(f"     {m['mes']} {m['indice']:>3} {barra}")
        for m in c:
            linhas.append({"snapshot_date": hoje, "regiao": uf,
                           "termo": TERMO, "serie_anos": 5,
                           "mes": m["mes"], "indice": m["indice"],
                           "medicoes": m["medicoes"],
                           "pico": m["mes"] == pico["mes"],
                           "vale": m["mes"] == vale["mes"],
                           "granularidade": "estado",
                           "semanas_medidas": vol["semanas"],
                           "semanas_com_busca": vol["semanas_com_busca"],
                           "pico_repete_em": est["pico_repete_em"],
                           "anos_medidos": est["anos_medidos"],
                           "pico_por_ano": est["anos"],
                           "fonte": "Google Trends via Apify "
                                    f"({ACTOR}), geo BR-{uf}",
                           "cidades_da_rede_na_uf": ids.get(uf, [])})

    # O VEREDITO SE GRAVA MESMO QUANDO NADA PASSA. Etapa que mede e não
    # escreve é etapa perdida: sem este arquivo, a próxima sessão refaz a
    # coleta inteira para redescobrir que não dá. Zero silencioso é falha.
    (RAIZ/"dados"/"portal").mkdir(parents=True, exist_ok=True)
    (RAIZ/"dados"/"portal"/"sazonalidade.json").write_text(json.dumps({
        "o_que_e": "A curva de procura por aparelho, medida no Google Trends "
                   "por UF, 5 anos.",
        "medido_em": hoje, "termo": TERMO, "janela": JANELA,
        "granularidade_tentada": "estado (BR-UF)",
        "por_que_nao_e_por_cidade":
            "o Trends não publica índice de cidade para este termo: das 124 "
            "cidades de SC, das 186 do PR e das 108 do PR com o termo mais "
            "largo 'ortodontista', NENHUMA teve volume — Londrina e Mafra "
            "incluídas, com valor 0",
        "as_duas_travas": {
            "volume": f"pelo menos {int(MIN_SEMANAS_COM_BUSCA*100)}% das "
                      f"semanas com busca e {MIN_MESES_COM_BUSCA} meses do ano",
            "estabilidade": f"o mês de pico repetido em pelo menos "
                            f"{MIN_ANOS_COM_O_MESMO_PICO} dos anos medidos"},
        "regioes_medidas": len(veredito),
        "regioes_publicaveis": sum(1 for v in veredito if v["publicavel"]),
        "veredito": veredito,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n  → dados/portal/sazonalidade.json "
          f"({len(veredito)} regiões medidas, "
          f"{sum(1 for v in veredito if v['publicavel'])} publicáveis)")

    if not linhas:
        sys.exit("\nnenhuma curva montada — nada gravado na série")
    if a.nao_salvar:
        print(f"\n  {len(linhas)} linhas montadas · --nao-salvar, não gravei")
        return
    arq = SERIE/"sazonalidade.jsonl"
    velho = [l for l in arq.read_text(encoding="utf-8").split("\n")
             if l.strip()] if arq.exists() else []
    with arq.open("a", encoding="utf-8") as f:
        for l in linhas:
            f.write(json.dumps(l, ensure_ascii=False) + "\n")
    print(f"\n  → dados/serie/sazonalidade.jsonl +{len(linhas)} "
          f"(tinha {len(velho)})")


if __name__ == "__main__":
    main()
