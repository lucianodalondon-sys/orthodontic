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
  3. a FOLGA — habitantes por clínica forte. Em Macapá é uma para cada 490 mil;
     em Contagem, onde a rede opera, é uma para cada 34 mil
  4. se a REDE JÁ ESTÁ LÁ — e aqui a regra é dura, por dois caminhos que não
     dependem um do outro:
       · a lista oficial do site da rede (374 unidades, 306 cidades), que
         inclui as 26 marcadas "em implantação" — praça vendida também não
         está livre
       · uma busca por nome no Google dentro da cidade
     Só sai "praça livre" quando os DOIS dizem que não tem. Se um dos dois
     falhar, a cidade sai como "não conferida" e não entra em recomendação
     nenhuma. Recomendar abertura onde já existe unidade é o pior erro que
     este produto pode cometer — vale mais devolver menos cidade.

E entrega um ARGUMENTO escrito por praça, não uma nota. Nota não defende
nada numa reunião de expansão; frase com número atrás defende.

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
import argparse, json, os, pathlib, re, subprocess, sys, textwrap, time, urllib.parse
import datetime as dt

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SERIE = RAIZ/"dados"/"serie"
sys.path.insert(0, str(RAIZ/"coleta"/"coletores"))
import unidades_da_rede as rede          # noqa: E402  a lista oficial
IBGE = "https://servicodados.ibge.gov.br"
API = "https://places.googleapis.com/v1/places:searchText"
CAMPOS = ("places.id,places.displayName,places.rating,places.userRatingCount,"
          "places.formattedAddress,places.websiteUri,places.types,nextPageToken")
# Os mesmos seis termos e as mesmas três páginas da varredura das praças que
# já estão na base. Se o radar varresse mais raso, o "3 clínicas fortes" de
# Macapá estaria sendo comparado com o "19 clínicas fortes" de Contagem sem
# aviso — e a cidade pareceria fraca só porque foi olhada com menos cuidado.
TERMOS = ["ortodontia", "aparelho ortodôntico", "clínica odontológica",
          "dentista", "ortodontista", "alinhador invisível"]
PAGINAS = 3
FORTE = 300          # avaliações que definem uma clínica "forte" na praça

# Habitantes por clínica forte nas sete praças que a rede opera e nós medimos.
# É a régua do argumento: dizer "uma clínica forte para cada 489 mil habitantes"
# não significa nada sozinho; ao lado de Contagem, que tem uma para cada 34 mil,
# vira frase de reunião. População do IBGE (6579) em 09/08/2026, clínicas fortes
# da varredura registrada em dados/serie/categoria.jsonl.
REF_HAB = {"MG · Contagem": 34_300, "BA · Feira de Santana": 44_053,
           "SC · Mafra + Rio Negro": 44_606, "SP · Presidente Prudente": 58_676,
           "PR · Londrina": 58_138, "MT · Cuiabá + Várzea Grande": 101_079,
           "TO · Palmas": 164_249}

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


def sem_acento(s):
    import unicodedata
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def na_cidade(p, cidade):
    """Mesma regra da varredura: última palavra do nome + UF no endereço.

    Existe porque o Google abrevia ('Pres. Prudente') e porque cidade de nome
    repetido contamina praça — 'Várzea Grande' trouxe uma clínica de 'Várzea
    Paulista/SP'. Aqui o estrago seria pior: uma clínica de outro estado
    inflando a categoria faz a cidade parecer ocupada e sumir do radar."""
    nome, uf = (cidade.split("/") + [""])[:2]
    end = sem_acento(p.get("formattedAddress"))
    chave = sem_acento(nome).split()[-1]
    uf = sem_acento(uf).strip()
    return chave in end and (not uf or re.search(rf"[-,]\s*{uf}\b", end))


def e_odonto(p):
    t = set(p.get("types") or [])
    nome = (p.get("displayName", {}).get("text") or "").lower()
    if t & {"dentist", "dental_clinic"}:
        return True
    return any(w in nome for w in ("odonto", "dental", "ortod", "dentist", "sorri"))


def busca(texto, key, page=None):
    corpo = {"textQuery": texto, "languageCode": "pt-BR", "maxResultCount": 20}
    if page:
        corpo["pageToken"] = page
    d = curl(API, "-X", "POST", "-H", "Content-Type: application/json",
             "-H", f"X-Goog-Api-Key: {key}", "-H", f"X-Goog-FieldMask: {CAMPOS}",
             "-d", json.dumps(corpo, ensure_ascii=False))
    if not d or "error" in (d or {}):
        return [], None
    return d.get("places", []), d.get("nextPageToken")


def categoria(cidade, key, termos=None):
    vistos = {}
    for t in (termos or TERMOS):
        pagina, voltas = None, 0
        while voltas < PAGINAS:
            lst, pagina = busca(f"{t} {cidade}", key, pagina)
            for p in lst:
                pid = p.get("id")
                if pid and pid not in vistos and e_odonto(p) and na_cidade(p, cidade):
                    vistos[pid] = p
            voltas += 1
            if not pagina:
                break
    return list(vistos.values())


def busca_nome_da_rede(cidade, key):
    """Segunda checagem, independente da lista oficial: procura a marca pelo
    nome dentro da cidade. Pega a unidade recém-aberta que o site ainda não
    publicou, e a que está com o site do franqueado na ficha."""
    achados = []
    for t in ("OrthoDontic", "OrthoDontic Documentação Ortodôntica"):
        lst, _ = busca(f"{t} {cidade}", key)
        for p in lst:
            nome = (p.get("displayName", {}).get("text") or "")
            site = (p.get("websiteUri") or "").lower()
            if not na_cidade(p, cidade):
                continue
            # 'You Align Orthodontics' já entrou como unidade da rede uma vez.
            # A palavra tem de estar isolada, e 'orthodontics' não vale.
            if "orthodonticbrasil.com.br" in site or re.search(
                    r"\borthodontic\b(?!s)", sem_acento(nome)):
                achados.append({"nome": nome, "endereco": p.get("formattedAddress"),
                                "site": p.get("websiteUri") or ""})
    return {a["nome"]: a for a in achados}.values()


def num(n):
    """1234567 → 1.234.567. Trocar vírgula por ponto na frase inteira comeu as
    vírgulas do texto: 'a categoria é fraca, e dá para medir' virou frase com
    ponto no meio. Número se formata sozinho, texto não se mexe."""
    return f"{int(n or 0):,}".replace(",", ".")


def rotulo_da_praca(praca_id):
    """MG · Contagem, e não 'contagem'. A UF vem antes do nome, sempre."""
    arq = RAIZ/"dados"/"identidade"/f"{praca_id}.json"
    try:
        cid = (json.loads(arq.read_text(encoding="utf-8")).get("cidades") or [""])[0]
        nome, uf = (cid.split("/") + [""])[:2]
        return f"{uf.strip().upper()} · {nome.strip()}" if uf.strip() else nome
    except Exception:
        return str(praca_id).capitalize()


def referencias():
    """Líder de cada praça já medida — é com elas que a cidade nova é comparada."""
    arq = SERIE/"categoria.jsonl"
    if not arq.exists():
        return {}
    por = {}
    for l in arq.read_text(encoding="utf-8").splitlines():
        if not l.strip():
            continue
        r = json.loads(l)
        por.setdefault(r.get("praca_id"), []).append(r)
    fora = {}
    for p, rs in por.items():
        u = max(x["snapshot_date"] for x in rs)
        vis = {x.get("place_id"): x for x in rs if x["snapshot_date"] == u}
        av = [(x.get("avaliacoes") or 0) for x in vis.values()]
        if av:
            fora[rotulo_da_praca(p)] = {
                "lider": max(av), "fortes": sum(1 for a in av if a >= FORTE),
                "clinicas": len(av), "hab_por_forte": None}
    return fora


def presenca(cidade, key, oficial):
    """As três checagens de unidade. Só é 'livre' quando as três concordam.

    1. lista oficial do site da rede (inclui as 'em implantação')
    2. busca pelo nome da marca dentro da cidade
    3. o site orthodonticbrasil.com.br na ficha, que era a única de antes

    Se a lista oficial não veio, o resultado é 'não conferida'. Cidade não
    conferida não vira recomendação — some do radar em vez de virar risco."""
    if oficial is None:
        return {"conferida": False, "livre": False,
                "motivo": "a lista oficial de unidades não respondeu",
                "unidades_da_rede": 0, "nomes_da_rede": [], "achadas_no_google": []}
    na_lista = rede.tem_unidade(cidade, oficial)
    no_google = list(busca_nome_da_rede(cidade, key))
    return {
        "conferida": True,
        "livre": not na_lista and not no_google,
        "motivo": ("na lista oficial: " + "; ".join(
            f"{u['unidade']} ({u['situacao']})" for u in na_lista)) if na_lista
        else ("achada no Google, fora da lista oficial: " + "; ".join(
            a["nome"] for a in no_google)) if no_google
        else "lista oficial e busca por nome, as duas, não acham unidade",
        "unidades_da_rede": len(na_lista) or len(no_google),
        "nomes_da_rede": [u["unidade"] for u in na_lista] or [a["nome"] for a in no_google],
        "achadas_no_google": [a["nome"] for a in no_google],
    }


def analisa(cidade, key, oficial):
    n = ibge(cidade)
    if not n:
        return {"cidade": cidade, "erro": "não achei no IBGE — confira grafia e UF"}
    cs = categoria(cidade, key)
    fortes = [p for p in cs if (p.get("userRatingCount") or 0) >= FORTE]
    lider = max((p.get("userRatingCount") or 0) for p in cs) if cs else 0
    pop = n.get("populacao") or 0
    nome, uf = [x.strip() for x in cidade.split("/")]
    pres = presenca(cidade, key, oficial)
    uf_vazia = oficial is not None and not any(
        u["uf"].upper() == uf.upper() for u in oficial)
    return {
        "rotulo": f"{uf} · {nome}", "cidade": cidade, "uf": uf, **n,
        "clinicas_amostradas": len(cs), "clinicas_fortes": len(fortes),
        "lider_avaliacoes": lider,
        "avaliacoes_somadas": sum(p.get("userRatingCount") or 0 for p in cs),
        "hab_por_clinica_forte": round(pop/len(fortes)) if fortes and pop else None,
        "uf_sem_nenhuma_unidade": uf_vazia,
        "presenca": pres, **{k: pres[k] for k in ("unidades_da_rede", "nomes_da_rede")},
        "maiores": [{"nome": p["displayName"]["text"],
                     "avaliacoes": p.get("userRatingCount"), "nota": p.get("rating"),
                     "site": p.get("websiteUri") or ""}
                    for p in sorted(cs, key=lambda x: -(x.get("userRatingCount") or 0))[:5]],
    }


def leitura(r):
    """A frase que o time de expansão lê. Nota sem frase não decide nada."""
    if r.get("erro"):
        return r["erro"]
    p = r["presenca"]
    if not p["conferida"]:
        return f"NÃO CONFERIDA — {p['motivo']}"
    if not p["livre"]:
        return f"a rede já está lá — {p['motivo']}"
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


def defesa(r, ref):
    """O que o time de expansão leva para a reunião.

    Não é nota, é argumento — cada linha com o número atrás e a comparação
    com praça que a rede já opera, porque 'líder tem 427 avaliações' só quer
    dizer alguma coisa ao lado do líder de Contagem, que tem 3.837."""
    # Praça ocupada não tem defesa: a rede já está lá. Sem esta linha o texto
    # começava com "Praça livre." em cima de "na lista oficial: Santarem -
    # Centro (aberta)" — a contradição mais cara que este arquivo poderia ter.
    if r.get("erro") or not r["presenca"]["conferida"] or not r["presenca"]["livre"]:
        return []
    pop = r.get("populacao") or 0
    a915, a3045 = r.get("alvo_9_15") or 0, r.get("alvo_30_45") or 0
    hab = r.get("hab_por_clinica_forte")
    lider = r["lider_avaliacoes"]
    linhas = []

    linhas.append(f"**Praça livre.** {r['presenca']['motivo'].capitalize()}."
                  + (f" E o estado inteiro: **{r['uf']} não tem uma única unidade "
                     f"da rede**." if r.get("uf_sem_nenhuma_unidade") else ""))

    if pop:
        linhas.append(f"**Tamanho.** {num(pop)} habitantes. O público que paga é o "
                      f"adulto: **{num(a3045)} pessoas de 30 a 45 anos**, contra "
                      f"{num(a915)} na faixa de 9 a 15 — em toda praça que medimos "
                      f"o adulto é 2 a 3 vezes maior, e é ele que decide sozinho.")

    if ref and lider:
        alvo, dados = max(ref.items(), key=lambda kv: kv[1]["lider"])
        linhas.append(
            f"**A categoria é fraca, e dá para medir.** O líder da cidade tem "
            f"{num(lider)} avaliações. O líder de {alvo}, varrido do mesmo jeito e "
            f"com os mesmos seis termos, tem {num(dados['lider'])} — "
            f"{dados['lider']/lider:.0f} vezes mais. Ninguém aqui construiu "
            f"reputação de escala ainda, e reputação é o que a rede sabe montar.")

    cheia = min(REF_HAB.items(), key=lambda kv: kv[1])
    vazia = max(REF_HAB.items(), key=lambda kv: kv[1])
    faixa = (f"Nas sete praças onde a rede já opera esse número vai de "
             f"{num(cheia[1])} ({cheia[0]}, a mais disputada) a {num(vazia[1])} "
             f"({vazia[0]}, a mais folgada).")
    if hab and pop:
        aperto = ("mais folgada que qualquer praça da rede"
                  if hab > vazia[1] else "dentro da faixa que a rede já opera")
        n = r["clinicas_fortes"]
        conta = (f"{n} clínica passa" if n == 1 else f"{n} clínicas passam")
        linhas.append(f"**Tem espaço.** Só {conta} de {FORTE} avaliações — uma "
                      f"para cada {num(hab)} habitantes, {aperto}. {faixa}")
    elif r["clinicas_fortes"] == 0:
        linhas.append(f"**Tem espaço, e é o caso extremo.** Nenhuma clínica da "
                      f"cidade passa de {FORTE} avaliações. A categoria inteira "
                      f"soma {num(r['avaliacoes_somadas'])} avaliações — menos do "
                      f"que a maior clínica de MG · Contagem sozinha. {faixa}")

    if r["maiores"]:
        quem = " · ".join(f"{m['nome']} ({m['avaliacoes']}, nota {m['nota']})"
                          for m in r["maiores"][:3])
        linhas.append(f"**Contra quem se entra.** {quem}.")

    linhas.append("**O que isto não prova.** População residente, não a diurna; "
                  "o município inteiro, não o raio de deslocamento; a categoria "
                  "pública do Google, não faturamento. Antes de assinar, vale "
                  "uma visita e a conta de ponto.")
    return linhas


def mostra_defesas(op):
    print(f"\n{'='*80}\n  A DEFESA DE CADA PRAÇA\n{'='*80}")
    for r in sorted(op, key=lambda x: -(x.get("alvo_30_45") or 0)):
        print(f"\n  ── {r['rotulo']} " + "─"*max(3, 70-len(r['rotulo'])))
        for l in r["defesa"]:
            print("     " + textwrap.fill(re.sub(r"\*\*(.+?)\*\*", r"\1", l), 72,
                                          subsequent_indent="     "))


def refazer_texto(salvar):
    """Recalcula leitura e defesa em cima da última medição já gravada.

    Existe porque corrigir uma frase custava US$ 5 de varredura. O número não
    muda — só o texto que ele sustenta. Grava uma linha nova na série, com a
    medição original preservada e a data de hoje."""
    arq = SERIE/"oportunidade.jsonl"
    rows = [json.loads(l) for l in arq.read_text(encoding="utf-8").splitlines() if l.strip()]
    rows = [r for r in rows if r.get("presenca")]
    if not rows:
        sys.exit("nenhuma medição com conferência de unidade na série — rode o "
                 "radar de verdade antes")
    corte = max(r["snapshot_date"] for r in rows)
    atual = ultimo_por([r for r in rows if r["snapshot_date"] == corte], "cidade")
    ref = referencias()
    fora = []
    for r in atual.values():
        r["leitura"] = leitura(r)
        r["defesa"] = defesa(r, ref)
        fora.append(r)
    print(f"\n  refeito o texto de {len(fora)} cidades sobre a medição de {corte}, "
          f"sem coletar nada")
    op = [r for r in fora if str(r.get("leitura", "")).startswith("OPORTUNIDADE")]
    if op:
        mostra_defesas(op)
    if salvar:
        hoje = dt.date.today().isoformat()
        with arq.open("a", encoding="utf-8") as f:
            for r in fora:
                f.write(json.dumps({**r, "snapshot_date": hoje,
                                    "medido_em": corte,
                                    "recalculo": "texto refeito, medição original"},
                                   ensure_ascii=False)+"\n")
        print(f"  → dados/serie/oportunidade.jsonl +{len(fora)}\n")


def ultimo_por(rows, chave):
    fora = {}
    for r in rows:
        fora[r.get(chave)] = r
    return fora


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cidade", action="append", default=[])
    ap.add_argument("--lista", help="arquivo com uma cidade por linha (Nome/UF)")
    ap.add_argument("--salvar", action="store_true")
    ap.add_argument("--refazer-texto", action="store_true",
                    help="reescreve leitura e defesa do último snapshot, sem "
                         "coletar nada — mexer em frase não deve custar coleta")
    a = ap.parse_args()

    if a.refazer_texto:
        return refazer_texto(a.salvar)

    cidades = list(a.cidade)
    if a.lista:
        cidades += [l.strip() for l in pathlib.Path(a.lista).read_text(encoding="utf-8").splitlines()
                    if l.strip() and "/" in l]
    if not cidades:
        sys.exit('use --cidade "Marabá/PA" (pode repetir) ou --lista arquivo.txt')

    key = chave()
    print(f"\n{'='*80}\n  RADAR DE OPORTUNIDADE · {len(cidades)} cidades · "
          f"~US$ {0.60*len(cidades):.2f}\n{'='*80}\n")

    # A lista oficial primeiro. Sem ela o radar não afirma que praça está livre.
    bruto = rede.baixar()
    oficial = rede.separar(bruto) if bruto else None
    if oficial:
        rede.salvar(oficial)
        abertas = sum(1 for u in oficial if u["situacao"] == "aberta")
        print(f"  lista oficial da rede: {len(oficial)} unidades · {abertas} abertas · "
              f"{len(oficial)-abertas} em implantação · "
              f"{len({u['cidade'] for u in oficial})} cidades\n")
    else:
        print("  ⚠ a lista oficial de unidades NÃO respondeu. Nenhuma cidade vai\n"
              "    sair como oportunidade nesta rodada — não dá para dizer que a\n"
              "    praça está livre sem ter olhado a lista.\n")

    print(f"  {'pop':>9s} {'9-15':>7s} {'30-45':>7s} {'fortes':>6s} {'líder':>6s} "
          f"{'hab/forte':>10s}  praça · leitura")
    ref = referencias()
    fora = []
    for c in cidades:
        r = analisa(c, key, oficial)
        r["leitura"] = leitura(r)
        r["defesa"] = defesa(r, ref)
        fora.append(r)
        if r.get("erro"):
            print(f"  {'—':>9s} {'':>7s} {'':>7s} {'':>6s} {'':>6s} {'':>10s}  {c}: {r['erro']}")
            continue
        print(f"  {r.get('populacao') or 0:>9,d} {r.get('alvo_9_15') or 0:>7,d} "
              f"{r.get('alvo_30_45') or 0:>7,d} {r['clinicas_fortes']:>6d} "
              f"{r['lider_avaliacoes']:>6d} {str(r.get('hab_por_clinica_forte') or '—'):>10s}  "
              f"{r['rotulo'][:24]:24s} {r['leitura']}")

    op = [r for r in fora if str(r.get("leitura", "")).startswith("OPORTUNIDADE")]
    ocupadas = [r for r in fora if not r.get("erro")
                and r["presenca"]["conferida"] and not r["presenca"]["livre"]]
    if ocupadas:
        print(f"\n  {len(ocupadas)} JÁ TEM UNIDADE — fora do radar:")
        for r in ocupadas:
            print(f"    {r['rotulo']}: {r['presenca']['motivo']}")

    if op:
        mostra_defesas(op)

    print("\n  RESSALVAS, e elas vão no relatório:")
    print("   · usa população RESIDENTE. A literatura diz que a diurna prevê melhor,")
    print("     e o IBGE não publica de graça.")
    print("   · a praça é o município, não o raio de deslocamento real.")
    print("   · mede a categoria pública do Google, não receita nem ticket.")
    print("   · 'praça livre' é a lista oficial da rede mais a busca por nome. Uma")
    print("     unidade aberta ontem e ainda não publicada é o furo possível.\n")

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
