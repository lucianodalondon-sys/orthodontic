#!/usr/bin/env python3
"""
descobrir_praca.py — a etapa 1 e a etapa 4 de uma praça nova, automáticas.

Faz o que dá para fazer sozinho quando se entra numa cidade nova:
  · resolve a cidade no IBGE e traz população, renda e comparação com o estado
  · acha as clínicas de ortodontia da cidade, com nota, volume e place_id
  · acha os veículos de imprensa que cobrem a cidade
  · monta o esqueleto de dados/identidade/<praca>.json e coleta/alvos/<praca>.yaml
  · imprime o que sobra para uma pessoa fazer (achar os perfis da cidade)

O que ele NÃO faz, de propósito: achar os influenciadores. Isso é a etapa 2 do
coleta/NOVA-PRACA.md e continua sendo humano — é onde o método ganha ou perde.

Uso:
    python3 coleta/descobrir_praca.py --cidade "Bauru/SP"
    python3 coleta/descobrir_praca.py --cidade "Mafra/SC" --mais "Rio Negro/PR" --id riomafra
    python3 coleta/descobrir_praca.py --cidade "Bauru/SP" --sem-clinicas   # só IBGE, custo zero
"""
import argparse, json, os, pathlib, re, subprocess, sys, time, unicodedata, urllib.parse
import datetime as dt
from xml.etree import ElementTree as ET

RAIZ = pathlib.Path(__file__).resolve().parent.parent
IBGE = "https://servicodados.ibge.gov.br"
API_APIFY = "https://api.apify.com/v2"
ACTOR = "compass~crawler-google-places"


def curl(url, timeout=30, tentativas=3):
    """A rede desta máquina derruba urllib no IBGE; curl passa.

    E o IBGE corta conexão em rajada, então tenta de novo antes de desistir.
    Sem isso, um reset de rede vira 'a cidade não tem esse número' — e a
    gente conclui coisa errada sobre a praça por causa de um soluço de rede.
    """
    erro = "sem resposta"
    for i in range(tentativas):
        if i:
            time.sleep(1.5 * i)
        r = subprocess.run(["curl", "-sS", "-m", str(timeout), "--retry", "2",
                            "-H", "User-Agent: Mozilla/5.0", url],
                           capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout
        erro = (r.stderr or "resposta vazia").strip()[:120]
    raise RuntimeError(f"curl falhou depois de {tentativas} tentativas: {erro}")


def jget(url, timeout=30):
    return json.loads(curl(url, timeout))


def slug(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


def resolve(cidade):
    nome, uf = [x.strip() for x in cidade.split("/")]
    d = jget(f"{IBGE}/api/v1/localidades/municipios?nome={urllib.parse.quote(nome)}")
    for m in d:
        if (m["nome"].lower() == nome.lower()
                and m["microrregiao"]["mesorregiao"]["UF"]["sigla"].upper() == uf.upper()):
            return m
    sys.exit(f"não achei '{cidade}' no IBGE. Confira a grafia e a UF.")


def serie(agregado, variavel, mid, periodo="-1"):
    """O IBGE derruba chamada em rajada. Tenta 3 vezes antes de desistir —
    e quando desiste, DIZ. Número que some calado é pior que número errado."""
    erro = None
    for tentativa in range(3):
        if tentativa:
            time.sleep(1.5 * tentativa)
        try:
            p = jget(f"{IBGE}/api/v3/agregados/{agregado}/periodos/{periodo}"
                     f"/variaveis/{variavel}?localidades=N6%5B{mid}%5D")
            s = p[0]["resultados"][0]["series"][0]["serie"]
            ano, val = list(s.items())[-1]
            if val in (None, "", "-", "..."):
                return None, None, None, "o IBGE não publica esse número para o município"
            return ano, val, p[0].get("unidade", ""), None
        except Exception as e:
            erro = str(e)[:90]
    return None, None, None, erro


# Censo 2022 por faixa de idade. Os códigos são do agregado 9514.
FAIXAS = {"93070":"0a4","93084":"5a9","93085":"10a14","93086":"15a19","93087":"20a24",
          "93088":"25a29","93089":"30a34","93090":"35a39","93091":"40a44","93092":"45a49",
          "93093":"50a54","93094":"55a59","93095":"60a64"}


def idades(mid):
    """O tamanho REAL do alvo, que o processo mandava buscar à mão.

    São dois públicos e eles não se parecem: o adolescente de 9-15, que usa o
    aparelho, e o adulto de 30-45, que é o alvo maior e o menos falado. Em
    Riomafra são ~7.700 contra ~21.000 — foi esse número que mostrou que a
    comunicação estava mirando o menor dos dois.
    """
    cods = ",".join(FAIXAS)
    try:
        d = jget(f"{IBGE}/api/v3/agregados/9514/periodos/2022/variaveis/93"
                 f"?localidades=N6%5B{mid}%5D&classificacao=287%5B{cods}%5D")
        fora = {}
        for r in d[0]["resultados"]:
            cat = r.get("classificacoes", [{}])[0].get("categoria", {})
            for cod in cat:
                val = list(r["series"][0]["serie"].values())[0]
                fora[FAIXAS.get(cod, cod)] = int(val)
        # 9-15 é metade de 5-9 mais 10-14 mais um quinto de 15-19
        jovem = round(fora.get("5a9", 0)*0.2 + fora.get("10a14", 0) + fora.get("15a19", 0)*0.2)
        adulto = fora.get("30a34", 0) + fora.get("35a39", 0) + fora.get("40a44", 0)
        return {"por_faixa": fora, "alvo_9_15": jovem, "alvo_30_45": adulto}
    except Exception:
        return None


def numeros_da_cidade(m):
    mid = m["id"]
    uf = m["microrregiao"]["mesorregiao"]["UF"]
    out = {"municipio": m["nome"], "uf": uf["sigla"], "uf_nome": uf["nome"],
           "ibge_id": mid, "mesorregiao": m["microrregiao"]["mesorregiao"]["nome"]}
    faltou = []
    for chave, ag, var, per in [("populacao_estimada", 6579, 9324, "-1"),
                                ("populacao_censo_2022", 4709, 93, "2022"),
                                ("massa_salarial_mil_reais", 5938, 37, "-1")]:
        ano, val, un, erro = serie(ag, var, mid, per)
        if val:
            out[chave] = {"ano": ano, "valor": val, "unidade": un}
        else:
            faltou.append((chave, erro or "não veio"))
    if faltou:
        out["nao_veio"] = {k: v for k, v in faltou}
    idd = idades(mid)
    if idd:
        out["idades"] = idd
    return out


def imprensa(cidade):
    q = urllib.parse.quote(f'"{cidade.split("/")[0]}" {cidade.split("/")[1]}')
    url = f"https://news.google.com/rss/search?q={q}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    try:
        raiz = ET.fromstring(curl(url))
    except Exception as e:
        return [], str(e)[:80]
    veic = {}
    for it in list(raiz.iterfind(".//item"))[:40]:
        f = it.find("source")
        if f is not None and f.text:
            veic[f.text.strip()] = veic.get(f.text.strip(), 0) + 1
    return sorted(veic.items(), key=lambda x: -x[1]), None


def token():
    t = os.environ.get("APIFY_TOKEN", "").strip()
    if not t:
        env = RAIZ/"_pipeline"/".env"
        if env.exists():
            for l in env.read_text(encoding="utf-8").splitlines():
                l = l.strip().replace("\r", "")
                if l.startswith("APIFY_TOKEN="):
                    t = l.split("=", 1)[1].strip()
    return t


def clinicas(cidade, tok, n=12):
    """Busca as clínicas de ortodontia da cidade — o placar inicial."""
    url = (f"{API_APIFY}/acts/{ACTOR}/run-sync-get-dataset-items"
           f"?token={tok}&timeout=420&memory=1024")
    body = json.dumps({
        "searchStringsArray": [f"ortodontia aparelho ortodôntico {cidade}"],
        "maxCrawledPlacesPerSearch": n, "language": "pt-BR",
        "maxReviews": 0, "onlyDataFromSearchPage": True,
    })
    r = subprocess.run(["curl", "-sS", "-m", "600", "-X", "POST", url,
                        "-H", "Content-Type: application/json", "-d", body],
                       capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
    except Exception:
        return [], (r.stdout or r.stderr)[:160]
    if isinstance(d, dict):
        return [], str(d)[:160]
    fora = []
    for p in d:
        fora.append({"nome": p.get("title"), "nota": p.get("totalScore"),
                     "avaliacoes": p.get("reviewsCount"), "place_id": p.get("placeId"),
                     "categoria": p.get("categoryName"), "endereco": p.get("address")})
    fora.sort(key=lambda x: -(x["avaliacoes"] or 0))
    return fora, None


TIPOS_CANAL = [
 ("voz_da_cidade", "o maior perfil local", "busque o nome da cidade no Instagram e pegue o de maior seguidor"),
 ("imprensa", "a notícia e a joia enterrada", "os veículos que apareceram acima"),
 ("mae", "É ELA QUEM DECIDE O APARELHO", "maternidade <cidade>, mães de <cidade>"),
 ("preco_achadinho", "como a cidade fala de dinheiro", "ofertas <cidade>, promoções, supermercado"),
 ("humor", "o que viraliza, a língua solta", "humor <cidade>, memes <cidade>"),
 ("jovem", "o público de 15-25", "festa, faculdade, evento"),
 ("gastronomia", "onde a indicação converte", "onde comer <cidade>"),
 ("prefeitura", "onde o cidadão reclama e celebra", "perfil oficial"),
 ("esporte_base", "O PÚBLICO DE 9-15 COM OS PAIS JUNTO", "escolinha de futsal, futebol, vôlei"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cidade", required=True, help='ex: "Bauru/SP"')
    ap.add_argument("--mais", action="append", default=[], help="outra cidade da mesma praça")
    ap.add_argument("--id", help="praca_id (padrão: derivado do nome)")
    ap.add_argument("--sem-clinicas", action="store_true", help="só IBGE e imprensa, custo zero")
    ap.add_argument("--sobrescrever", action="store_true",
                    help="apaga e refaz uma praça que já existe (cuidado: perde o trabalho à mão)")
    args = ap.parse_args()

    cidades = [args.cidade] + args.mais
    praca_id = args.id or slug(args.cidade.split("/")[0])
    hoje = dt.date.today().isoformat()

    # Antes de gastar rede e crédito: essa praça já existe?
    d = RAIZ/"dados"/"identidade"
    a = RAIZ/"coleta"/"alvos"
    ja_existe = [str(p.relative_to(RAIZ)) for p in (d/f"{praca_id}.json", a/f"{praca_id}.yaml")
                 if p.exists()]
    if ja_existe and not args.sobrescrever:
        sys.exit(f"\n  PAREI. A praça '{praca_id}' já existe:\n    "
                 + "\n    ".join(ja_existe)
                 + "\n\n  Esses arquivos têm trabalho humano dentro (os canais da cidade,\n"
                   "  o tipo de cada concorrente). Gerar de novo apaga tudo isso.\n"
                   "  Use --id <outro_nome> para uma praça nova, ou --sobrescrever se é\n"
                   "  isso mesmo que você quer.\n")

    print(f"\n{'='*66}\n  PRAÇA NOVA · {praca_id}  ·  {' + '.join(cidades)}\n{'='*66}")

    # ---- etapa 1
    print("\n## 1 · A CIDADE EM NÚMEROS (IBGE)")
    nums = []
    for c in cidades:
        m = resolve(c)
        n = numeros_da_cidade(m)
        nums.append(n)
        pop = (n.get("populacao_estimada") or {}).get("valor")
        cen = (n.get("populacao_censo_2022") or {}).get("valor")
        sal = (n.get("massa_salarial_mil_reais") or {}).get("valor")
        print(f"  {n['municipio']}/{n['uf']} · IBGE {n['ibge_id']} · {n['mesorregiao']}")
        print(f"    população estimada {pop or '—'} · censo 2022 {cen or '—'} · "
              f"massa salarial {sal or '—'} mil reais")
        for chave, motivo in (n.get("nao_veio") or {}).items():
            print(f"    ⚠ {chave} não veio: {motivo}")
    total = sum(int((n.get("populacao_estimada") or {}).get("valor") or 0) for n in nums)
    if len(cidades) > 1:
        print(f"  → praça somada: {total} habitantes")
    jovens = sum((n.get("idades") or {}).get("alvo_9_15", 0) for n in nums)
    adultos = sum((n.get("idades") or {}).get("alvo_30_45", 0) for n in nums)
    if jovens or adultos:
        print(f"  ALVO REAL: {jovens} de 9-15 anos · {adultos} de 30-45 anos"
              + (f" — o adulto é {adultos/jovens:.1f}× maior" if jovens else ""))
        print("  Os dois públicos não se parecem, e o maior costuma ser o menos falado.")
    else:
        print("  FALTA À MÃO: quantos de 9-15 e de 30-45 anos. É o tamanho real do alvo.")

    # ---- imprensa
    print("\n## 2 · QUEM NOTICIA A CIDADE")
    for c in cidades:
        veic, err = imprensa(c)
        if err:
            print(f"  {c}: falhou · {err}")
            continue
        print(f"  {c}:")
        for nome, q in veic[:8]:
            print(f"    {q:3d}× {nome}")
        if not veic:
            print("    (nenhum veículo local identificado — já é informação)")

    # ---- etapa 4
    clin = []
    if not args.sem_clinicas:
        tok = token()
        if not tok:
            print("\n## 3 · CLÍNICAS — pulado (APIFY_TOKEN ausente)")
        else:
            print("\n## 3 · O PLACAR INICIAL DA CATEGORIA")
            for c in cidades:
                lst, err = clinicas(c, tok)
                if err:
                    print(f"  {c}: falhou · {err}"); continue
                for p in lst:
                    p["cidade"] = c
                clin += lst
                for p in lst[:12]:
                    print(f"    {str(p['nota'] or '?'):>4s} · {str(p['avaliacoes'] or 0):>5s}  "
                          f"{(p['nome'] or '?')[:44]:44s} {(p['categoria'] or '')[:22]}")
            print("\n  LER ASSIM: quem lidera em VOLUME, não em nota. E que TIPO de")
            print("  concorrente é cada um — rede popular, clínica geral, doutor com nome")
            print("  próprio, clínica-escola, startup de tráfego. Muda toda a estratégia.")

    # ---- esqueleto
    ident = {"praca_id": praca_id, "nome": praca_id.replace("_", " ").title(),
             "cidades": cidades, "uf": sorted({n["uf"] for n in nums}),
             "criada_em": hoje, "ibge": nums,
             "nota_geografia": "PREENCHER: por que estas cidades são uma praça só (ou não).",
             "locais": [{"local_id": "ortho_" + praca_id, "papel": "proprio",
                         "nome": "OrthoDontic " + cidades[0].split("/")[0],
                         "tipo": "franquia", "place_id": None, "chave_pendente": True}]
             + [{"local_id": slug(p["nome"] or "")[:28], "papel": "concorrente",
                 "nome": p["nome"], "tipo_concorrente": "PREENCHER",
                 "place_id": p["place_id"], "cidade": p["cidade"]}
                for p in clin[:8]]}

    # --sobrescrever refaz os números da cidade, NÃO apaga as clínicas já
    # ancoradas. Aprendido do jeito difícil: rodar de novo em Palmas só para
    # atualizar a idade apagou os 14 locais com place_id.
    arq = d/f"{praca_id}.json"
    if arq.exists():
        antigo = json.loads(arq.read_text(encoding="utf-8"))
        ancorados = [l for l in antigo.get("locais", []) if l.get("place_id")]
        if ancorados:
            ident["locais"] = ancorados
            ident["nota_geografia"] = antigo.get("nota_geografia", ident["nota_geografia"])
            print(f"  (mantidos {len(ancorados)} locais já ancorados)")
    d.mkdir(parents=True, exist_ok=True)
    arq.write_text(json.dumps(ident, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")


    linhas = [f"# ALVOS DE COLETA — {praca_id}",
              f"# Esqueleto gerado em {hoje}. A etapa 2 (os perfis da cidade) é HUMANA.",
              f"# Ver coleta/NOVA-PRACA.md\n",
              f"praca_id: {praca_id}", f"cidades: {json.dumps(cidades, ensure_ascii=False)}",
              "alvos:"]
    for p in clin[:8]:
        linhas += [f"  - name: {slug(p['nome'] or '')[:28]}_google", "    layer: concorrente",
                   "    platform: google", f"    query: \"{p['nome']} {p['cidade']}\"",
                   "    status: roda"]
    linhas.append("\n# ---- PREENCHER À MÃO: os canais da cidade (etapa 2) ----")
    for tipo, oque, como in TIPOS_CANAL:
        linhas += [f"  # - name: {tipo}_ig            # {oque}",
                   f"  #   layer: territorio         # como achar: {como}",
                   "  #   platform: instagram", "  #   handle: \"\"", "  #   status: pendente"]
    (a/f"{praca_id}.yaml").write_text("\n".join(linhas)+"\n", encoding="utf-8")

    print(f"\n{'='*66}\n  ESQUELETO GRAVADO")
    print(f"    dados/identidade/{praca_id}.json   ({len(ident['locais'])} locais)")
    print(f"    coleta/alvos/{praca_id}.yaml")
    print(f"\n  AGORA É COM VOCÊ (etapa 2, ~1h30) — ache 8 a 14 canais da cidade:")
    for i, (tipo, oque, como) in enumerate(TIPOS_CANAL, 1):
        print(f"    {i}. {tipo:18s} {oque}")
        print(f"       {como}")
    print("\n  E ANOTE OS QUE NÃO EXISTEM. Canal que falta é território vazio —")
    print("  quem chegar primeiro fala sozinho. Em Riomafra faltam três.")
    print(f"{'='*66}\n")


if __name__ == "__main__":
    main()
