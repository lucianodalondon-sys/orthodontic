#!/usr/bin/env python3
"""
estudar_oportunidade.py — a praça de oportunidade estudada por inteiro, e
comparada com uma praça onde a rede já opera.

O radar diz ONDE. Este diz O QUE TEM LÁ, e responde a pergunta que o time de
expansão faz em seguida: **essa cidade dá quanto?**

Ninguém assina franquia por causa de "1 clínica forte para cada 490 mil
habitantes". Assina quando alguém diz: *"esta cidade se parece com Palmas, e
em Palmas a unidade faz 14 avaliações por mês há onze meses seguidos e é a
terceira em ritmo entre as clínicas acompanhadas da praça."* Isso é âncora, não promessa — e a diferença entre
as duas coisas está escrita no relatório.

Três partes, nesta ordem:

  1. A CIDADE — IBGE inteiro: população, censo, massa salarial, e as treze
     faixas etárias. O alvo de verdade são dois e eles não se parecem: o
     adolescente de 9-15, que usa o aparelho, e o adulto de 30-45, que é 2 a
     3× maior e decide sozinho. Mais os veículos de imprensa que cobrem a
     cidade.

  2. A CONCORRÊNCIA — a categoria varrida inteira, com os mesmos seis termos
     e três páginas das praças da base. Não é lista de nomes: é a ESTRUTURA
     — quantas fortes, quanto o topo concentra, quantas são de rede nacional,
     quantas nem site têm, e quais endereços aparecem duas vezes.

  3. A GÊMEA — a praça da rede mais parecida, medida em seis eixos ao mesmo
     tempo, e o que a unidade OrthoDontic faz lá de verdade. Vem com a
     distância em cada eixo, porque gêmea que só bate em um eixo é coincidência.

Uso:
    python3 scripts/estudar_oportunidade.py --cidade "Macapá/AP" --salvar
    python3 scripts/estudar_oportunidade.py --todas --salvar
    python3 scripts/estudar_oportunidade.py --cidade "Marabá/PA" --dossie
"""
import argparse, json, math, pathlib, re, sys, textwrap
import datetime as dt

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SERIE = RAIZ/"dados"/"serie"
SAIDA = RAIZ/"dados"/"oportunidade"
DOSSIES = RAIZ/"pesquisas"/"_dossies"
sys.path.insert(0, str(RAIZ/"scripts"))
sys.path.insert(0, str(RAIZ/"coleta"))
sys.path.insert(0, str(RAIZ/"coleta"/"coletores"))
import radar_oportunidade as radar          # noqa: E402  varredura e conferência
import descobrir_praca as desc              # noqa: E402  IBGE e imprensa
import cruzamento as cruz                   # noqa: E402  o que a unidade faz em cada praça
import inteligencia as intel               # noqa: E402  o ritmo pelo contador, que é o que vale
import unidades_da_rede as rede             # noqa: E402  a lista oficial

FORTE = radar.FORTE

# Redes nacionais de odontologia. Concorrente de rede não é igual a consultório
# de bairro: tem verba, padrão de captação e time de vendas. Numa praça, saber
# QUANTAS são de rede muda o plano de entrada mais que o número total.
# 'sorriso' saiu da lista: casa com meia dúzia de consultórios de bairro que
# não são rede nenhuma, e inflava a contagem em toda praça do Nordeste.
REDES = ["odontocompany", "sorridents", "oral sin", "odontoclinic", "sorrifacil",
         "orthodontic", "orthopride", "oral unic", "amorsaude", "vamos sorrir",
         "odontoprev", "uniodonto", "sorrimais", "imperial odonto"]

# Os eixos da gêmea. Peso alto no que muda o tamanho do negócio (público adulto
# e força do líder); peso menor no que só descreve a cidade.
EIXOS = [
    ("populacao",             "habitantes",                 1.0),
    ("alvo_30_45",            "adultos de 30 a 45",         1.5),
    ("alvo_9_15",             "jovens de 9 a 15",           0.8),
    ("renda_per_capita",      "massa salarial por pessoa",  1.0),
    ("clinicas_fortes_ajust", "clínicas fortes",            1.2),
    ("lider_avaliacoes",      "volume do líder",            1.5),
]


def num(n):
    return f"{int(n or 0):,}".replace(",", ".")


def dec(x, casas=1):
    return f"{x:.{casas}f}".replace(".", ",")


# ───────────────────────────── 1 · a cidade ─────────────────────────────────

def a_cidade(cidade):
    m = desc.resolve(cidade)
    n = desc.numeros_da_cidade(m)
    veic, erro = desc.imprensa(cidade)
    n["imprensa"] = [{"veiculo": v, "materias": q} for v, q in veic[:12]]
    if erro:
        n["imprensa_erro"] = erro
    pop = int((n.get("populacao_estimada") or {}).get("valor") or 0)
    massa = float((n.get("massa_salarial_mil_reais") or {}).get("valor") or 0)
    # massa salarial vem em MIL reais e é anual: vira reais por habitante/mês
    n["renda_per_capita"] = round(massa*1000/pop/12) if pop and massa else None
    n["populacao"] = pop or None
    return n


# ────────────────────────── 2 · a concorrência ──────────────────────────────

def e_de_rede(nome):
    """Casa a marca com borda de palavra.

    Sem a borda, 'odontoclinic' engolia 'Odontoclínica Dr. Álvaro Bacellar' em
    Marabá — um consultório de um dentista só virava rede nacional. É o mesmo
    erro de 'You Align Orthodontics', e ele volta toda vez que se compara
    nome por 'contém'."""
    alvo = radar.sem_acento(nome)
    return any(re.search(rf"\b{re.escape(r)}\b", alvo) for r in REDES)


def a_concorrencia(cidade, key):
    cs = radar.categoria(cidade, key)
    av = [(p.get("userRatingCount") or 0) for p in cs]
    total = sum(av)
    ordenadas = sorted(cs, key=lambda p: -(p.get("userRatingCount") or 0))
    top5 = sum((p.get("userRatingCount") or 0) for p in ordenadas[:5])

    def nome(p):
        return (p.get("displayName", {}).get("text") or "")

    de_rede = [p for p in cs if e_de_rede(nome(p))]
    com_site = [p for p in cs if (p.get("websiteUri") or "").strip()]
    # Endereço repetido = ficha duplicada. Divide avaliação e reputação, e a
    # rede já tem uma assim em Feira. Numa praça nova é mapa de quem está
    # desarrumado — e de quem vai ser fácil passar.
    por_end = {}
    for p in cs:
        e = radar.sem_acento(p.get("formattedAddress")).split(",")[0][:40]
        if e:
            por_end.setdefault(e, []).append(nome(p))
    dobradas = {k: v for k, v in por_end.items() if len(v) > 1}

    notas = [p.get("rating") for p in cs if p.get("rating")]
    fortes = [p for p in ordenadas if (p.get("userRatingCount") or 0) >= FORTE]
    return {
        "varridas": len(cs),
        "avaliacoes_somadas": total,
        "nota_mediana": round(sorted(notas)[len(notas)//2], 2) if notas else None,
        "fortes": len(fortes),
        "medias": sum(1 for a in av if 100 <= a < FORTE),
        "fracas": sum(1 for a in av if a < 100),
        "lider_avaliacoes": max(av) if av else 0,
        "concentracao_top5": round(top5/total, 3) if total else None,
        "de_rede_nacional": len(de_rede),
        "nomes_de_rede": sorted({nome(p) for p in de_rede})[:10],
        "com_site": len(com_site),
        "sem_site_pct": round(100*(len(cs)-len(com_site))/len(cs)) if cs else None,
        "enderecos_com_ficha_dobrada": len(dobradas),
        "exemplos_dobrados": [{"endereco": k, "fichas": v} for k, v in list(dobradas.items())[:5]],
        "maiores": [{"nome": nome(p), "avaliacoes": p.get("userRatingCount"),
                     "nota": p.get("rating"), "site": p.get("websiteUri") or "",
                     "endereco": p.get("formattedAddress")} for p in ordenadas[:10]],
        "_bruto": cs,
    }


def salvar_categoria(praca_id, cidade, cs):
    """Grava a varredura inteira, não só os dez maiores.

    Arquivo separado de propósito: categoria.jsonl é das praças da rede, e
    misturar cidade sem unidade lá dentro estragaria o cruzamento — o
    'a rede sustenta 30% contra 13% do mercado' passaria a contar praça que
    a rede nem opera."""
    hoje = dt.date.today().isoformat()
    arq = SERIE/"categoria_oportunidade.jsonl"
    ja = set()
    if arq.exists():
        for l in arq.read_text(encoding="utf-8").split("\n"):
            if l.strip():
                r = json.loads(l)
                ja.add((r["snapshot_date"], r["praca_id"], r["place_id"]))
    n = 0
    with arq.open("a", encoding="utf-8") as f:
        for p in cs:
            k = (hoje, praca_id, p.get("id"))
            if k in ja:
                continue
            ja.add(k)
            f.write(json.dumps({
                "snapshot_date": hoje, "praca_id": praca_id, "cidade": cidade,
                "place_id": p.get("id"),
                "nome": p.get("displayName", {}).get("text"),
                "nota": p.get("rating"), "avaliacoes": p.get("userRatingCount"),
                "endereco": p.get("formattedAddress"),
                "site": p.get("websiteUri") or "",
                "tipos": p.get("types") or [],
                "fonte": "google places api",
                "filtro": "|".join(radar.TERMOS),
            }, ensure_ascii=False)+"\n")
            n += 1
    return n


# ──────────────────────────── 3 · a gêmea ───────────────────────────────────

def ritmos_por_contador():
    """O ritmo que vale: quanto o contador do Google subiu entre duas coletas.

    A conta pelo intervalo da amostra é estimativa e já errou feio — em
    Presidente Prudente ela diz 18,1 por mês e o contador diz 13,2. A gêmea é
    a promessa que o time de expansão vai levar para uma reunião; ela tem de
    carregar o número observado, não o inferido."""
    hist = {}
    for p in cruz.jsonl("places"):
        v = p.get("avaliacoes", p.get("avaliacoes_total"))
        if v is not None:
            hist.setdefault((p.get("praca_id"), p.get("local_id")), {})[p["snapshot_date"]] = v
    fora = {}
    for k, h in hist.items():
        r, dias = intel.ritmo_por_delta(h)
        if r is None:
            continue
        if r < 0:
            # O contador CAIU. Em Feira a unidade foi de 173 para 170 em 23
            # dias. Isso não é ritmo negativo — é avaliação removida, e virar
            # "-4,0 por mês" numa tabela de expansão seria inventar uma
            # métrica que não existe. Vira zero, com o fato escrito ao lado.
            ds = sorted(h)
            fora[k] = (0.0, dias, f"⚠ o contador CAIU {h[ds[0]]-h[ds[-1]]} "
                                  f"avaliações em {dias} dias — avaliação removida "
                                  f"ou ficha mexida")
        else:
            fora[k] = (r, dias, f"contador do Google em {dias} dias")
    return fora


def pracas_da_rede():
    """O perfil e o desempenho real de cada praça onde a rede opera."""
    ident, linhas = cruz.coleta()
    contador = ritmos_por_contador()
    for x in linhas:
        obs = contador.get((x["praca"], x["local_id"]))
        x["ritmo_estimado"] = x["ritmo"]
        if obs:
            x["ritmo"], x["ritmo_dias"], x["ritmo_fonte"] = obs
        else:
            x["ritmo_fonte"] = "intervalo da amostra (~estimado)"
    por_praca = {}
    for praca, d in ident.items():
        ibge = d.get("ibge") or []
        pop = sum(int((x.get("populacao_estimada") or {}).get("valor") or 0) for x in ibge)
        massa = sum(float((x.get("massa_salarial_mil_reais") or {}).get("valor") or 0)
                    for x in ibge)
        a30 = sum((x.get("idades") or {}).get("alvo_30_45") or 0 for x in ibge)
        a915 = sum((x.get("idades") or {}).get("alvo_9_15") or 0 for x in ibge)

        cat = [r for r in cruz.jsonl("categoria") if r.get("praca_id") == praca]
        if cat:
            u = max(r["snapshot_date"] for r in cat)
            vistos = {r["place_id"]: r for r in cat if r["snapshot_date"] == u}
            av = [(r.get("avaliacoes") or 0) for r in vistos.values()]
        else:
            av = []
        fortes = sum(1 for a in av if a >= FORTE)

        nossos = [x for x in linhas if x["praca"] == praca and x["papel"] == "proprio"]
        nossos.sort(key=lambda x: -(x.get("total") or 0))
        por_praca[praca] = {
            "praca_id": praca, "rotulo": d.get("rotulo") or d.get("nome"),
            "cidades": d.get("cidades_rotulo") or d.get("cidades", []),
            "populacao": pop or None, "alvo_30_45": a30 or None, "alvo_9_15": a915 or None,
            "renda_per_capita": round(massa*1000/pop/12) if pop and massa else None,
            "clinicas_varridas": len(av), "clinicas_fortes": fortes,
            "lider_avaliacoes": max(av) if av else 0,
            "hab_por_clinica_forte": round(pop/fortes) if fortes and pop else None,
            "unidades": [{"nome": x["nome"], "total": x["total"], "nota": x["nota"],
                          "ritmo": x["ritmo"], "meses": x["meses"],
                          "ritmo_fonte": x.get("ritmo_fonte"),
                          "ritmo_estimado": x.get("ritmo_estimado"),
                          "selo": cruz.selo(x["meses"]),
                          "posicao": x.get("posicao"), "de": x.get("de")}
                         for x in nossos],
        }
    return por_praca


def ajusta_fortes(fortes, varridas, varridas_ref):
    """Comparar 'clínicas fortes' entre praças varridas com profundidades
    diferentes engana. As praças da base foram varridas com o mesmo método,
    mas trazem números de clínicas diferentes (87 em Riomafra, 243 em Cuiabá)
    porque a cidade tem o que tem. Aqui a conta vira DENSIDADE — fortes por
    cem clínicas varridas — e volta à escala da praça de referência."""
    if not varridas:
        return 0.0
    return fortes/varridas*varridas_ref


def razao(x, y, campo):
    if campo == "clinicas_fortes_ajust":
        x, y = (x or 0) + 0.5, (y or 0) + 0.5
    return round(x/y, 2) if x and y else None


def gemea(perfil, base):
    """A praça mais parecida, em seis eixos ao mesmo tempo.

    A distância é a média das diferenças em LOG. Log porque o que importa é a
    razão, não a diferença: 400 mil contra 500 mil habitantes é quase igual;
    30 mil contra 130 mil não é.

    ⚠ E aqui mora a armadilha que já mordeu: **praça com eixo faltando é mais
    fácil de casar.** Quatro das sete praças da base não tinham nada do IBGE, e
    Juazeiro do Norte (305 mil habitantes) casou com Riomafra (89 mil) porque
    Riomafra só tinha dois dos seis eixos — média de dois números pequenos é
    menor que média de seis. Agora quem não tem os três eixos obrigatórios
    (habitantes, adultos de 30-45 e volume do líder) sai da disputa com o
    motivo escrito, em vez de vencer por falta de dado."""
    OBRIGATORIOS = ("populacao", "alvo_30_45", "lider_avaliacoes")
    fora, descartadas = [], []
    for p in base.values():
        ref_varr = p["clinicas_varridas"] or 1
        a = dict(perfil)
        b = dict(p)
        a["clinicas_fortes_ajust"] = ajusta_fortes(
            perfil["clinicas_fortes"], perfil["clinicas_varridas"], ref_varr)
        b["clinicas_fortes_ajust"] = float(p["clinicas_fortes"])
        difs, pesos, faltando = [], [], []
        for campo, rotulo, peso in EIXOS:
            x, y = a.get(campo), b.get(campo)
            # 'zero clínicas fortes' é informação, não ausência — e é o achado
            # de Imperatriz. Log não aceita zero, então as contagens levam meio
            # ponto dos dois lados em vez de sumirem do cálculo.
            if campo == "clinicas_fortes_ajust":
                x, y = (x or 0) + 0.5, (y or 0) + 0.5
            if not x or not y or x <= 0 or y <= 0:
                faltando.append(rotulo)
                continue
            difs.append(peso*abs(math.log(x/y)))
            pesos.append(peso)
        vazios = [c for c in OBRIGATORIOS if not a.get(c) or not b.get(c)]
        if vazios or not pesos:
            descartadas.append({"rotulo": p["rotulo"], "sem": vazios or ["tudo"]})
            continue
        fora.append({
            "praca_id": p["praca_id"], "rotulo": p["rotulo"],
            "distancia": round(sum(difs)/sum(pesos), 3),
            "eixos_usados": len(pesos), "eixos_sem_dado": faltando,
            "eixos": [{"eixo": rotulo,
                       "aqui": a.get(campo), "la": b.get(campo),
                       "razao": razao(a.get(campo), b.get(campo), campo)}
                      for campo, rotulo, _ in EIXOS],
            "perfil": p,
        })
    # Empate técnico entre praças com número de eixos diferente vai para a que
    # foi medida em mais eixos. Comparação mais completa ganha da mais barata.
    fora.sort(key=lambda x: (x["distancia"], -x["eixos_usados"]))
    return fora, descartadas


def frase_da_gemea(g, perfil):
    """A frase que o time de expansão leva. Sem ela, os seis eixos são planilha.

    E ela muda conforme o que a unidade da gêmea está fazendo. Dizer "tem
    capacidade de performar como Riomafra" quando a unidade de Riomafra está
    parada há meses seria vender um número que ninguém está entregando."""
    p = g["perfil"]
    us = [u for u in p["unidades"] if u.get("total")]
    if not us:
        return (f"{g['rotulo']} é a praça mais parecida, mas a unidade de lá ainda "
                f"não tem medição suficiente para servir de âncora.")
    u = max(us, key=lambda x: (x.get("meses") or 0, x.get("ritmo") or 0))
    meses = u.get("meses") or 0
    quanto = (f"{dec(u['ritmo'])} avaliações por mês" if u.get("ritmo")
              else "ritmo ainda não medido")
    posic = (f", {u['posicao']}ª em ritmo entre as {u['de']} clínicas "
             f"acompanhadas na praça" if u.get("posicao") else "")
    cabeca = f"**{perfil['rotulo']} tem o perfil de {g['rotulo']}.**"
    corpo = (f"Lá a unidade OrthoDontic tem {num(u['total'])} avaliações, nota "
             f"{dec(float(u['nota']))} e faz {quanto}")
    if meses >= 10:
        return (f"{cabeca} {corpo} **há {meses} meses seguidos**{posic} — é operação, "
                f"não campanha, e é o tipo de resultado que se copia.")
    if meses >= 3:
        return (f"{cabeca} {corpo} há {meses} meses{posic}. É campanha, não operação: "
                f"serve de teto do que a praça comporta, não de piso do que ela entrega.")
    return (f"{cabeca} {corpo}{posic} — mas **a unidade de lá está parada**. "
            f"Esta gêmea diz que a cidade comporta uma unidade deste tamanho; "
            f"não diz que ela anda sozinha.")


def faixa_das_parecidas(gs, quantas=3):
    """O que as praças parecidas entregam, da pior à melhor.

    Uma gêmea só é um caso. Riomafra está parada e Palmas sustenta há onze
    meses — as duas parecem com Juazeiro. Mostrar a faixa evita que a escolha
    do vizinho mais próximo vire a previsão inteira."""
    fora = []
    for g in gs[:quantas]:
        for u in g["perfil"]["unidades"]:
            if u.get("ritmo") is not None:
                fora.append({"praca": g["rotulo"], "unidade": u["nome"],
                             "ritmo": u["ritmo"], "meses": u.get("meses") or 0,
                             "total": u.get("total"), "selo": u.get("selo"),
                             "fonte": u.get("ritmo_fonte"),
                             "distancia": g["distancia"]})
    fora.sort(key=lambda x: x["ritmo"])
    return fora


def como_diferem(g):
    """O que NÃO bate. Gêmea sem ressalva é venda, não análise."""
    fora = []
    for e in g["eixos"]:
        if not e.get("razao"):
            continue
        r = e["razao"]
        if r >= 1.25:
            fora.append(f"{e['eixo']}: {dec(r, 1)}× maior aqui "
                        f"({num(e['aqui'])} contra {num(e['la'])})")
        elif r <= 0.8:
            fora.append(f"{e['eixo']}: {dec(1/r, 1)}× menor aqui "
                        f"({num(e['aqui'])} contra {num(e['la'])})")
    return fora


# ──────────────────────────────── estudo ────────────────────────────────────

def estuda(cidade, key, base, oficial):
    nome, uf = [x.strip() for x in cidade.split("/")]
    praca_id = desc.slug(nome)
    pres = radar.presenca(cidade, key, oficial)

    n = a_cidade(cidade)
    c = a_concorrencia(cidade, key)
    bruto = c.pop("_bruto")
    idades = (n.get("idades") or {})
    perfil = {
        "praca_id": praca_id, "rotulo": f"{uf} · {nome}", "cidade": cidade, "uf": uf,
        "populacao": n.get("populacao"),
        "alvo_30_45": idades.get("alvo_30_45"), "alvo_9_15": idades.get("alvo_9_15"),
        "renda_per_capita": n.get("renda_per_capita"),
        "clinicas_varridas": c["varridas"], "clinicas_fortes": c["fortes"],
        "lider_avaliacoes": c["lider_avaliacoes"],
        "hab_por_clinica_forte": (round(n["populacao"]/c["fortes"])
                                  if c["fortes"] and n.get("populacao") else None),
    }
    gs, descartadas = gemea(perfil, base)
    return {"praca_id": praca_id, **perfil, "conferencia": pres,
            "cidade_numeros": n, "concorrencia": c,
            "gemeas": [{k: v for k, v in g.items() if k != "perfil"} for g in gs[:3]],
            "gemeas_descartadas": descartadas,
            "faixa_das_parecidas": faixa_das_parecidas(gs),
            "gemea": ({"rotulo": gs[0]["rotulo"], "praca_id": gs[0]["praca_id"],
                       "distancia": gs[0]["distancia"],
                       "eixos_usados": gs[0]["eixos_usados"],
                       "frase": frase_da_gemea(gs[0], perfil),
                       "unidades_de_la": gs[0]["perfil"]["unidades"],
                       "onde_difere": como_diferem(gs[0])} if gs else None),
            "_bruto": bruto, "_gs": gs}


# ──────────────────────────────── saída ─────────────────────────────────────

def imprime(e):
    print(f"\n{'='*78}\n  {e['rotulo']}\n{'='*78}")
    p = e["conferencia"]
    print(f"\n  UNIDADE DA REDE: {'nenhuma — ' if p['livre'] else ''}{p['motivo']}")

    n, c = e["cidade_numeros"], e["concorrencia"]
    print(f"\n  ── A CIDADE {'─'*60}")
    print(f"    {num(e['populacao'])} habitantes · {n.get('mesorregiao')}")
    print(f"    alvo adulto (30-45): {num(e['alvo_30_45'])}   "
          f"alvo jovem (9-15): {num(e['alvo_9_15'])}   "
          f"= {dec((e['alvo_30_45'] or 0)/(e['alvo_9_15'] or 1))}× maior")
    if e.get("renda_per_capita"):
        print(f"    massa salarial: R$ {num(e['renda_per_capita'])} por habitante/mês")
    if n.get("nao_veio"):
        for k, v in n["nao_veio"].items():
            print(f"    ⚠ {k} não veio: {v}")
    if n.get("imprensa"):
        print(f"    imprensa que cobre: "
              + ", ".join(f"{i['veiculo']} ({i['materias']})" for i in n["imprensa"][:6]))

    print(f"\n  ── A CONCORRÊNCIA {'─'*54}")
    print(f"    {c['varridas']} clínicas varridas · {num(c['avaliacoes_somadas'])} "
          f"avaliações somadas · nota mediana {c['nota_mediana']}")
    print(f"    {c['fortes']} fortes (300+) · {c['medias']} médias (100-299) · "
          f"{c['fracas']} fracas (<100)")
    if c["concentracao_top5"] is not None:
        print(f"    as 5 maiores concentram {round(c['concentracao_top5']*100)}% "
              f"das avaliações da praça")
    print(f"    {c['de_rede_nacional']} são de rede nacional"
          + (f" ({', '.join(c['nomes_de_rede'][:3])}…)" if c["nomes_de_rede"] else ""))
    print(f"    {c['sem_site_pct']}% não têm site na ficha · "
          f"{c['enderecos_com_ficha_dobrada']} endereços com ficha duplicada")
    print("    os maiores:")
    for m in c["maiores"][:6]:
        print(f"      {m['avaliacoes']:>5} {str(m['nota']):>4}  {m['nome'][:52]}")

    g = e.get("gemea")
    if g:
        print(f"\n  ── A GÊMEA {'─'*61}")
        print("     " + textwrap.fill(re.sub(r"\*\*(.+?)\*\*", r"\1", g["frase"]), 72,
                                      subsequent_indent="     "))
        print(f"\n     os seis eixos (aqui × {g['rotulo']}, distância "
              f"{dec(g['distancia'], 2)}):")
        for x in e["_gs"][0]["eixos"]:
            if x.get("razao"):
                print(f"       {x['eixo']:26s} {num(x['aqui']):>9s} × {num(x['la']):>9s}"
                      f"   {dec(x['razao'], 2)}×")
        if g["onde_difere"]:
            print("\n     onde NÃO bate — e isso vale mais que onde bate:")
            for d in g["onde_difere"]:
                print(f"       · {d}")
        print(f"\n     as outras duas mais parecidas: "
              + " · ".join(f"{x['rotulo']} ({dec(x['distancia'], 2)})"
                           for x in e["gemeas"][1:3]))
        faixa = e.get("faixa_das_parecidas") or []
        if len(faixa) > 1:
            print("\n     a FAIXA das três parecidas — uma gêmea é um caso, "
                  "três são uma faixa:")
            for f in faixa:
                print(f"       {dec(f['ritmo']):>6s}/mês  {f['meses']:>2d} meses  "
                      f"{f['selo']:9s} {f['unidade'][:30]:30s} "
                      f"{f['praca'][:20]:20s} {f.get('fonte') or ''}")
        if e.get("gemeas_descartadas"):
            print("\n     fora da comparação por falta de dado: "
                  + " · ".join(f"{d['rotulo']} (sem {', '.join(d['sem'])})"
                               for d in e["gemeas_descartadas"]))


def serie(nome, praca):
    arq = SERIE/f"{nome}.jsonl"
    if not arq.exists():
        return []
    rs = [json.loads(l) for l in arq.read_text(encoding="utf-8").split("\n")
          if l.strip() and f'"{praca}"' in l]
    rs = [r for r in rs if r.get("praca_id") == praca]
    if not rs:
        return []
    corte = max(r["snapshot_date"] for r in rs)
    return [r for r in rs if r["snapshot_date"] == corte]


def PREENCHER(pergunta, porque):
    return [f"> ⬜ **PREENCHER — {pergunta}**", ">",
            f"> {porque}", ""]


def dossie(e):
    """As dezoito seções do dossiê de Mafra, menos a de dados internos.

    O erro que isto conserta: o estudo de oportunidade saía com três seções —
    IBGE, concorrência e a gêmea. O dossiê de Mafra tem dezoito, e o que
    faltava era justamente a metade que decide a entrada: quem fala com a
    cidade, o que a cidade diz com as palavras dela, qual é a ferida da praça,
    que canal está vago e o que jamais dizer ali.

    O que a máquina mede, ela preenche. O que é leitura humana entra como
    PREENCHER com a pergunta exata — nunca como texto plausível inventado,
    que é o jeito de um dossiê parecer completo e não ser."""
    g, c, n = e.get("gemea"), e["concorrencia"], e["cidade_numeros"]
    praca = e["praca_id"]
    canais = serie("canais", praca)
    posts = serie("posts", praca)
    imprensa = serie("imprensa", praca)
    ads = [a for a in serie("anuncios", praca) if a.get("ativo")]
    revs = serie("reviews", praca)
    hoje = dt.date.today().strftime("%d/%m/%Y")

    L = [f"# DOSSIÊ — {e['rotulo']} — praça de oportunidade (sem unidade)", "",
         f"**{hoje}** · Mesmo processo das praças da rede, menos a parte que "
         f"depende de unidade: aqui não existe unidade ainda.", ""]
    if g:
        L += ["> " + g["frase"], ""]
    L += ["---", "", "## 1 · IDENTIDADE", "",
          f"- **Praça:** {e['rotulo']}",
          f"- **Município:** {e['cidade']} · {n.get('mesorregiao')}",
          f"- **Unidade da rede:** nenhuma. {e['conferencia']['motivo'].capitalize()}, "
          f"conferido em duas fontes independentes.",
          f"- **Por que esta praça:** {(g or {}).get('frase', '—')}", ""]
    L += PREENCHER("o raio real da praça",
                   "Até onde vem o paciente? Tem cidade grudada do outro lado de "
                   "rio, divisa ou rodovia? O ônibus urbano sai do município? "
                   "Riomafra ensinou que duas cidades podem ser uma praça só, e "
                   "Londrina que uma cidade pode ser duas.")

    L += ["---", "", "## 2 · COLETA E MÉTODO", "",
          "| Fonte | O que rendeu |", "|---|---:|",
          f"| Varredura da categoria (Google Places) | {c['varridas']} clínicas |",
          f"| Avaliações com data | {len(revs)} |",
          f"| Canais da cidade mapeados | {len(canais)} |",
          f"| Vozes coletadas (posts e comentários) | {len(posts)} |",
          f"| Matérias de imprensa | {len(imprensa)} |",
          f"| Anúncios ativos na praça | {len(ads)} |", ""]
    if len(posts) < 800:
        L += [f"> ⚠ **{len(posts)} vozes.** O método pede 800+ para a persona da "
              f"cidade sustentar. Abaixo disso, o que sair da seção 5 é hipótese, "
              f"não leitura.", ""]

    L += ["---", "", "## 3 · A CIDADE EM NÚMEROS", "",
          "| | |", "|---|---:|",
          f"| Habitantes | **{num(e['populacao'])}** |",
          f"| Adultos de 30 a 45 | **{num(e['alvo_30_45'])}** |",
          f"| Jovens de 9 a 15 | {num(e['alvo_9_15'])} |",
          f"| Massa salarial por habitante/mês | R$ {num(e.get('renda_per_capita'))} |", "",
          f"O alvo adulto é **{dec((e['alvo_30_45'] or 0)/(e['alvo_9_15'] or 1))}× "
          f"maior que o adolescente** — e decide sozinho. A proporção se repete "
          f"nas sete praças medidas.", ""]

    L += ["---", "", "## 4 · QUEM FALA COM A CIDADE", ""]
    if canais:
        L += ["| Tipo | Canal | Seguidores |", "|---|---|---:|"]
        for x in sorted(canais, key=lambda r: -(r.get("seguidores") or 0))[:14]:
            L.append(f"| {x.get('tipo')} | @{x.get('handle')} — {x.get('nome')} "
                     f"| {num(x.get('seguidores'))} |")
        L.append("")
        tipos = {x.get("tipo") for x in canais}
        NOVE = ["voz_da_cidade", "jornal_local", "prefeitura", "mae", "humor",
                "esporte_base", "gastronomia", "radio", "classificados"]
        faltam = [t for t in NOVE if t not in tipos]
        if faltam:
            L += [f"**As lacunas — {len(faltam)} dos nove tipos não existem nesta "
                  f"praça:** {', '.join(faltam)}.", "",
                  "Canal que falta é **território vago**: quem chegar primeiro fala "
                  "sozinho. Em Mafra faltavam três, e foi o achado mais acionável "
                  "do dossiê.", ""]
    else:
        L += ["⚠ Nenhum canal mapeado ainda.", ""]
    L += PREENCHER("conferir os canais à mão — 1h",
                   "Em Palmas, 31% do que a busca automática achou era de outra "
                   "cidade ou outro assunto. A máquina propõe; quem conhece a "
                   "praça confirma. E ANOTE OS QUE NÃO EXISTEM.")

    L += ["---", "", "## 5 · PERSONA DA CIDADE", ""]
    L += PREENCHER("identidade de base",
                   "A história que a cidade conta de si. Mafra: 'uma colônia de "
                   "1829 partida pela divisa dos estados, a maior colônia bucovina "
                   "do mundo'. Sai da imprensa e do que a cidade repete.")
    L += PREENCHER("temperamento",
                   "Como a cidade se comporta em público. Mafra: 'discreto, "
                   "comunitário, desconfia de promessa grande; comenta pouco — o "
                   "silêncio digital é característica, não ausência de opinião'.")
    L += PREENCHER("léxico real — as palavras da praça",
                   "As gírias e expressões que só existem ali. Mafra: piá, "
                   "piazada, vina, chimarrão, geia. Sai dos posts e das "
                   "avaliações, nunca de suposição regional.")
    L += PREENCHER("valores, orgulhos e A FERIDA da cidade",
                   "A ferida é o que mais decide comunicação. Em Mafra é SAÚDE: "
                   "'esperar, viajar 2h ou desistir' — e a unidade que resolve "
                   "isso fala com a cidade inteira.")
    L += PREENCHER("sub-segmentos e como cada um fala",
                   "A mãe decisora, o adolescente, o trabalhador, o interior "
                   "rural, o idoso. Em Mafra cada um tem canal e linguagem "
                   "próprios, e a concorrência já anuncia por cidade do interior.")
    L += PREENCHER("calendário cultural",
                   "As festas e as férias escolares do estado. Mafra: Bucovina "
                   "Fest em julho, Mafra Fest de 5 a 8 de setembro com 18 mil "
                   "pessoas. É onde a unidade nova aparece antes de existir.")
    L += PREENCHER("PROIBIÇÕES DE TOM — o que JAMAIS dizer aqui",
                   "A seção mais valiosa do dossiê de Mafra: 'jamais gíria "
                   "gaúcha, jamais estética de Oktoberfest, jamais urgência de "
                   "liquidação — o radar antivigarista da colônia queima a marca'.")

    if posts:
        L += ["### O que a cidade publicou (amostra da coleta)", ""]
        for x in sorted(posts, key=lambda r: -((r.get("curtidas") or 0)))[:6]:
            t = re.sub(r"\s+", " ", (x.get("legenda") or ""))[:150]
            if t:
                L.append(f"- *\"{t}…\"* — @{x.get('handle')} "
                         f"({num(x.get('curtidas'))} curtidas)")
        L.append("")

    L += ["---", "", "## 6 · PERSONA DO PACIENTE", ""]
    if revs:
        L += [f"De **{num(len(revs))} avaliações** escritas por pacientes das "
              f"clínicas desta praça.", ""]
    L += PREENCHER("quem decide",
                   "Em todas as praças medidas é a mãe. Confirme aqui: as "
                   "avaliações falam de filho, ou de si?")
    L += PREENCHER("elogios-assinatura — verbatim",
                   "As frases que a praça repete quando elogia. São a redação do "
                   "anúncio, e não se inventam: se colhem das avaliações.")
    L += PREENCHER("dores → antídotos",
                   "O que a praça reclama, e o que a unidade nova faz em resposta. "
                   "Uma linha para cada.")
    L += PREENCHER("objeções reais",
                   "As perguntas que a praça faz antes de fechar. Preço, tempo, "
                   "dor, convênio — na ordem em que aparecem ali.")

    L += ["---", "", "## 7 · O QUE A UNIDADE NOVA VAI ENCONTRAR", "",
          "*(nas praças da rede esta seção é o raio-x da unidade; aqui não há "
          "unidade, então é o que ela encontraria no primeiro dia)*", ""]
    L += PREENCHER("o ponto",
                   "Onde abrir dentro da cidade. O dossiê mede o município "
                   "inteiro; a escolha do ponto é outro trabalho, e a seção 4 "
                   "dos bairros do plano de captação é a pista.")

    L += ["---", "", "## 8 · CONCORRÊNCIA", "",
          f"Varredura com os mesmos seis termos e três páginas das praças da "
          f"rede: **{c['varridas']} clínicas**, {num(c['avaliacoes_somadas'])} "
          f"avaliações somadas, nota mediana {c['nota_mediana']}.", "",
          "| | |", "|---|---:|",
          f"| Passam de {FORTE} avaliações | **{c['fortes']}** |",
          f"| Entre 100 e {FORTE-1} | {c['medias']} |",
          f"| Abaixo de 100 | {c['fracas']} |",
          f"| Líder | {num(c['lider_avaliacoes'])} |",
          f"| As 5 maiores concentram | {round((c['concentracao_top5'] or 0)*100)}% |",
          f"| De rede nacional | {c['de_rede_nacional']} |",
          f"| Sem site na ficha | {c['sem_site_pct']}% |",
          f"| Endereços com ficha duplicada | {c['enderecos_com_ficha_dobrada']} |", "",
          "### O líder e quem vem atrás", "",
          "| Clínica | Avaliações | Nota |", "|---|---:|---:|"]
    for m in c["maiores"][:10]:
        L.append(f"| {m['nome']} | {num(m['avaliacoes'])} | {m['nota']} |")
    L.append("")
    L += PREENCHER("o playbook do líder, passo a passo",
                   "Como o líder ganhou a praça. Em Mafra o líder vence 'com o "
                   "dono respondendo cada avaliação e carinho com idosos' — isso "
                   "não sai de número, sai de ler o que ele faz.")
    L += PREENCHER("o tipo de cada concorrente",
                   "Rede popular, doutor com nome próprio, clínica-escola, "
                   "startup de tráfego. Muda toda a estratégia de entrada.")
    L += PREENCHER("a concorrência gratuita",
                   "Tem clínica-escola ou atendimento público na cidade? A brecha "
                   "de sempre: quase nunca fazem aparelho de adolescente e "
                   "adulto. Confirmar por telefone antes de usar.")
    if ads:
        L += ["### A mídia ativa na praça", "",
              f"**{len(ads)} anúncios ativos** de "
              + ", ".join(sorted({a['anunciante'] for a in ads})[:6]) + ".", ""]
        for a in ads[:5]:
            t = re.sub(r"\s+", " ", (a.get("texto") or ""))[:130]
            if t:
                L.append(f"- **{a['anunciante']}**: *\"{t}…\"*")
        L.append("")
    else:
        L += ["### A mídia ativa na praça", "",
              "Nenhum anúncio ativo encontrado na biblioteca pública. "
              "**Território de mídia paga vazio** — ou a coleta não alcançou.", ""]

    L += ["---", "", "## 9 · MERCADO", "",
          f"- **Renda:** R$ {num(e.get('renda_per_capita'))} de massa salarial por "
          f"habitante/mês.",
          f"- **Público-alvo:** {num(e['alvo_30_45'])} adultos de 30-45 e "
          f"{num(e['alvo_9_15'])} jovens de 9-15.",
          f"- **Folga da categoria:** "
          + (f"uma clínica forte para cada {num(e['hab_por_clinica_forte'])} habitantes."
             if e.get("hab_por_clinica_forte") else
             f"nenhuma clínica passa de {FORTE} avaliações."), ""]
    L += PREENCHER("âncora de preço da praça",
                   "Quanto custa aparelho nesta cidade, hoje, segundo os "
                   "diretórios e sites locais. É o número que define se a rede "
                   "entra por preço ou por reputação.")
    L += PREENCHER("sazonalidade",
                   "As férias escolares do estado e as duas ondas de matrícula. "
                   "Sai do calendário oficial da secretaria de educação.")

    L += ["---", "", "## 10 · A JOIA ENTERRADA", ""]
    if imprensa:
        L += [f"{len(imprensa)} matérias coletadas. Os veículos que cobrem a cidade:",
              "", ", ".join(sorted({x.get("veiculo") for x in imprensa if x.get("veiculo")})[:10]), ""]
        L += ["Títulos recentes, para garimpo:", ""]
        for x in imprensa[:8]:
            L.append(f"- {x.get('titulo')} — *{x.get('veiculo')}*")
        L.append("")
    L += PREENCHER("a joia — ou a declaração de que não tem",
                   "O ativo local que ninguém copia. Em Mafra, o prêmio de "
                   "melhores do ano é por ADESÃO e um concorrente já foi 'eleito "
                   "ortodontista destaque' por essa via — se a especialista de "
                   "verdade não ocupa o título, ele fica com quem chegar primeiro. "
                   "A imprensa costuma ter a pista.")

    L += ["---", "", "## 11 · TERRITÓRIOS DE CAMPANHA E TOM", ""]
    L += PREENCHER("os territórios de campanha",
                   "Três ou quatro ideias que cabem nesta praça e em nenhuma "
                   "outra. Saem do cruzamento entre a ferida da cidade, as "
                   "lacunas de canal e o que o líder não faz.")

    L += ["---", "", "## 12 · PLANO DE ENTRADA", ""]
    L += PREENCHER("o que fazer nos primeiros 90 dias",
                   "Em ordem, do que custa zero para o que custa verba. A ficha "
                   "do Google e os canais vagos vêm antes de qualquer anúncio.")

    L += ["---", "", "## 13 · A GÊMEA — quanto esta praça pode entregar", ""]
    if g:
        L += [g["frase"], "",
              f"Seis eixos comparados ao mesmo tempo (distância "
              f"{dec(g['distancia'], 2)}):", "",
              f"| Eixo | {e['rotulo']} | {g['rotulo']} | Razão |", "|---|---:|---:|---:|"]
        for x in e["_gs"][0]["eixos"]:
            if x.get("razao"):
                L.append(f"| {x['eixo']} | {num(x['aqui'])} | {num(x['la'])} "
                         f"| {dec(x['razao'], 2)}× |")
        L.append("")
        faixa = e.get("faixa_das_parecidas") or []
        if len(faixa) > 1:
            L += ["**Uma gêmea é um caso; três são uma faixa.**", "",
                  "| Ritmo/mês | Meses | Selo | Unidade | Praça | De onde vem |",
                  "|---:|---:|---|---|---|---|"]
            for f in faixa:
                L.append(f"| {dec(f['ritmo'])} | {f['meses']} | {f['selo']} "
                         f"| {f['unidade']} | {f['praca']} | {f.get('fonte') or '—'} |")
            L += ["", f"A faixa vai de **{dec(faixa[0]['ritmo'])}** a "
                      f"**{dec(faixa[-1]['ritmo'])} por mês** em praças de perfil "
                      f"parecido. **A diferença entre as pontas não é a cidade — é "
                      f"a operação.**", ""]
        if g["onde_difere"]:
            L += ["**Onde NÃO bate** — e isto vale mais que onde bate:", ""]
            L += [f"- {d}" for d in g["onde_difere"]] + [""]

    L += ["---", "", "## 14 · O QUE NÃO ESTAMOS VENDO", "",
          "- **A coleta enxerga o digital público.** Não vê rádio, TV, outdoor, "
          "patrocínio de escolinha, parceria com escola nem indicação boca a "
          "boca — que os estudos apontam como *o* canal de decisão.",
          "- **População residente, não diurna.** A literatura de território diz "
          "que a diurna prevê melhor; o IBGE não a publica de graça.",
          "- **A praça é o município inteiro**, não o raio real de deslocamento.",
          "- **Mede a categoria pública do Google** — volume e nota, não "
          "faturamento, ticket nem convênio.",
          "- **A gêmea compara perfil, não gestão.** Em MT · Cuiabá três unidades "
          "da mesma marca, na mesma cidade, fazem 46,4 · 3,7 · 0,7 por mês.", "",
          "**A pergunta que fecha o buraco custa nada:** *o que se faz de mídia "
          "nesta cidade que não está na internet?*", ""]

    L += ["---", "", "## 15 · O CHECKLIST DESTA PRAÇA", "",
          f"- [{'x' if canais else ' '}] canais da cidade mapeados ({len(canais)})",
          "- [ ] canais **conferidos à mão**, e os que NÃO existem anotados",
          f"- [{'x' if len(posts) >= 800 else ' '}] 800+ vozes coletadas ({len(posts)})",
          f"- [{'x' if revs else ' '}] avaliações com data ({len(revs)})",
          "- [ ] o tipo de cada concorrente preenchido",
          "- [ ] a ferida da cidade escrita",
          "- [ ] as proibições de tom escritas",
          "- [ ] a joia enterrada — ou a declaração de que não tem",
          "- [ ] o calendário: férias escolares do estado + festas da cidade",
          f"- [{'x' if imprensa else ' '}] imprensa local ({len(imprensa)} matérias)",
          f"- [{'x' if ads else ' '}] mídia ativa dos concorrentes ({len(ads)})",
          "- [ ] o plano de entrada dos 90 dias", "",
          "---", "",
          f"_Coletado até {hoje}. Radar de Oportunidade + o mesmo processo de "
          f"`coleta/NOVA-PRACA.md` usado nas praças da rede, menos o que depende "
          f"de unidade. Dados em `dados/oportunidade/{praca}.json` e "
          f"`dados/serie/`._", ""]
    return "\n".join(L)


def refazer(salvar, escrever_dossie):
    """Recalcula a gêmea em cima do estudo já gravado, sem coletar nada.

    A varredura custa; a comparação não. Quando o problema é a régua — e foi:
    quatro praças da base estavam sem os números do IBGE e a gêmea saiu errada
    — refazer a conta não pode custar outra rodada de US$ 4."""
    arqs = sorted(SAIDA.glob("*.json"))
    if not arqs:
        sys.exit("nenhum estudo gravado em dados/oportunidade/")
    base = pracas_da_rede()
    varridas = {}
    arqv = SERIE/"categoria_oportunidade.jsonl"
    if arqv.exists():
        for l in arqv.read_text(encoding="utf-8").split("\n"):
            if l.strip():
                r = json.loads(l)
                varridas.setdefault(r["praca_id"], {})[r["place_id"]] = r
    print(f"\n  refazendo a gêmea de {len(arqs)} praças contra {len(base)} da rede, "
          f"sem coletar nada")
    feitos = []
    for arq in arqs:
        e = json.loads(arq.read_text(encoding="utf-8"))
        perfil = {k: e.get(k) for k in
                  ("praca_id", "rotulo", "cidade", "uf", "populacao", "alvo_30_45",
                   "alvo_9_15", "renda_per_capita", "clinicas_varridas",
                   "clinicas_fortes", "lider_avaliacoes", "hab_por_clinica_forte")}
        # a contagem de rede nacional é feita por nome e o casamento já errou:
        # refazer aqui evita outra varredura só para consertar uma lista
        vs = varridas.get(e["praca_id"]) or {}
        if vs:
            nomes = [v.get("nome") or "" for v in vs.values()]
            e["concorrencia"]["de_rede_nacional"] = sum(1 for x in nomes if e_de_rede(x))
            e["concorrencia"]["nomes_de_rede"] = sorted({x for x in nomes if e_de_rede(x)})[:10]
        gs, descartadas = gemea(perfil, base)
        e["gemeas"] = [{k: v for k, v in g.items() if k != "perfil"} for g in gs[:3]]
        e["gemeas_descartadas"] = descartadas
        e["faixa_das_parecidas"] = faixa_das_parecidas(gs)
        e["gemea"] = ({"rotulo": gs[0]["rotulo"], "praca_id": gs[0]["praca_id"],
                       "distancia": gs[0]["distancia"],
                       "eixos_usados": gs[0]["eixos_usados"],
                       "frase": frase_da_gemea(gs[0], perfil),
                       "unidades_de_la": gs[0]["perfil"]["unidades"],
                       "onde_difere": como_diferem(gs[0])} if gs else None)
        e["_gs"] = gs
        feitos.append(e)
        imprime(e)
        if salvar:
            arq.write_text(json.dumps({k: v for k, v in e.items()
                                       if not k.startswith("_")},
                                      ensure_ascii=False, indent=2)+"\n",
                           encoding="utf-8")
        if escrever_dossie:
            d = DOSSIES/f"OPORTUNIDADE-{e['praca_id']}.md"
            d.write_text(dossie(e), encoding="utf-8")
            print(f"  → {d.relative_to(RAIZ)}")
    rep = alerta_gemea_repetida(feitos)
    if rep:
        print(f"\n  ⚠ {rep[1]} das {rep[2]} cidades casaram com {rep[0]} — a rede "
              f"quase não\n    opera praça deste perfil. A âncora existe, mas é UMA.")


def alerta_gemea_repetida(estudos):
    """Quando a mesma praça vira gêmea de quase todas, o problema é a base.

    Cinco das seis cidades do radar casaram com TO · Palmas. Não é coincidência
    e não é erro de conta: é que a rede quase não tem praça deste perfil —
    cidade de 300 a 500 mil habitantes com categoria fraca. Isso é achado sobre
    a REDE, e precisa aparecer, senão a repetição parece robustez."""
    from collections import Counter
    c = Counter(e["gemea"]["rotulo"] for e in estudos if e.get("gemea"))
    for rotulo, n in c.most_common(1):
        if n >= 3 and n >= len(estudos)*0.5:
            return (rotulo, n, len(estudos))
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cidade", action="append", default=[])
    ap.add_argument("--todas", action="store_true",
                    help="todas as cidades livres já medidas pelo radar")
    ap.add_argument("--salvar", action="store_true")
    ap.add_argument("--dossie", action="store_true", help="escreve o .md do dossiê")
    ap.add_argument("--refazer-gemea", action="store_true",
                    help="recalcula a gêmea sobre o estudo já gravado, sem coletar")
    a = ap.parse_args()

    if a.refazer_gemea:
        return refazer(a.salvar, a.dossie)

    cidades = list(a.cidade)
    if a.todas:
        arq = SERIE/"oportunidade.jsonl"
        rows = [json.loads(l) for l in arq.read_text(encoding="utf-8").split("\n")
                if l.strip()]
        rows = [r for r in rows if r.get("presenca", {}).get("livre")
                and str(r.get("leitura", "")).startswith("OPORTUNIDADE")]
        corte = max((r["snapshot_date"] for r in rows), default=None)
        vistas = {r["cidade"] for r in rows if r["snapshot_date"] == corte}
        cidades += sorted(vistas)
    if not cidades:
        sys.exit('use --cidade "Macapá/AP" (pode repetir) ou --todas')

    key = radar.chave()
    bruto = rede.baixar()
    oficial = rede.separar(bruto) if bruto else None
    if oficial is None:
        sys.exit("a lista oficial de unidades não respondeu — sem ela não afirmo "
                 "que praça nenhuma está livre.")
    rede.salvar(oficial)

    print(f"\n{'='*78}\n  ESTUDO DE PRAÇA DE OPORTUNIDADE · {len(cidades)} cidades · "
          f"~US$ {0.60*len(cidades):.2f}\n{'='*78}")
    base = pracas_da_rede()
    print(f"  comparando com {len(base)} praças da rede: "
          + ", ".join(sorted(p["rotulo"] for p in base.values())))

    feitos = []
    for c in cidades:
        e = estuda(c, key, base, oficial)
        feitos.append(e)
        imprime(e)
        if a.salvar:
            SAIDA.mkdir(parents=True, exist_ok=True)
            n = salvar_categoria(e["praca_id"], c, e["_bruto"])
            gravar = {k: v for k, v in e.items() if not k.startswith("_")}
            gravar["snapshot_date"] = dt.date.today().isoformat()
            (SAIDA/f"{e['praca_id']}.json").write_text(
                json.dumps(gravar, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
            print(f"\n  → dados/oportunidade/{e['praca_id']}.json · "
                  f"categoria_oportunidade.jsonl +{n}")
        if a.dossie:
            DOSSIES.mkdir(parents=True, exist_ok=True)
            arq = DOSSIES/f"OPORTUNIDADE-{e['praca_id']}.md"
            arq.write_text(dossie(e), encoding="utf-8")
            print(f"  → {arq.relative_to(RAIZ)}")

    rep = alerta_gemea_repetida(feitos)
    if rep:
        rotulo, n, tot = rep
        print(f"\n  ⚠ {n} DAS {tot} CIDADES CASARAM COM A MESMA PRAÇA ({rotulo}).")
        print("    Isso diz mais sobre a base do que sobre as cidades: a rede quase")
        print("    não opera praça deste perfil — 300 a 500 mil habitantes com")
        print("    categoria fraca. A âncora existe, mas é UMA. Vale entrar numa")
        print("    praça assim na próxima rodada de coleta, para a comparação")
        print("    deixar de depender de um caso só.")

    print("\n  RESSALVAS, e vão no relatório:")
    print("   · população RESIDENTE, não diurna · município, não raio de")
    print("     deslocamento · categoria pública do Google, não faturamento")
    print("   · a gêmea compara PERFIL, não gestão. Em Cuiabá três unidades da")
    print("     mesma marca fazem 46,4 · 3,7 · 0,7 por mês.\n")


if __name__ == "__main__":
    main()
