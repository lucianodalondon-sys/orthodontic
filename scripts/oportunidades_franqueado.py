#!/usr/bin/env python3
"""
oportunidades_franqueado.py — o radar do franqueado: onde ele pode captar.

O radar da franqueadora responde "em que cidade abrir". Este responde a
pergunta do outro lado do balcão: **onde eu ponho os próximos mil reais para
virar consulta?**

E a resposta não é uma lista de palavras-chave. É uma lista de PORTAS — as
frases que a cidade digita — com três colunas ao lado de cada uma: quem já
está ali, se a unidade aparece, e o que fazer. Palavra-chave sem essas três
colunas é planilha; com elas, é decisão.

As cinco famílias de oportunidade, da mais barata para a mais cara:

  1. PORTA ONDE A UNIDADE SUMIU — a frase existe, a cidade digita, e a unidade
     não está nos dez primeiros do mapa. Em Londrina são doze de dezoito, e
     todas as doze têm a palavra "dentista" dentro. Conserto: ficha. Custo: R$ 0.
  2. PORTA SEM DONO — quem responde tem pouca reputação. Passar custa pouco.
  3. BAIRRO QUE A CIDADE PROCURA — o autocompletar entrega o nome do bairro
     junto com a busca. Nove em Londrina. É onde a unidade fala sozinha.
  4. CONVÊNIO PROCURADO — a cidade digita o nome do plano. Se a unidade aceita
     e não diz, está perdendo de graça; se não aceita, é decisão comercial.
  5. PALAVRA DO PACIENTE — o que os pacientes da praça escrevem nas avaliações.
     É a redação do anúncio, e ela não se inventa: se colhe.

Uso:
    python3 scripts/oportunidades_franqueado.py --praca londrina
    python3 scripts/oportunidades_franqueado.py --todas --salvar
"""
import argparse, json, pathlib, re, sys, textwrap, unicodedata
from collections import Counter, defaultdict
import datetime as dt

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SERIE = RAIZ/"dados"/"serie"
IDENT = RAIZ/"dados"/"identidade"
FRACO = 300      # abaixo disso, quem está no topo da porta não tem fortaleza
sys.path.insert(0, str(RAIZ/"coleta"/"coletores"))
from portas import NAO_E_BAIRRO, frase_util   # noqa: E402  uma regra só, num lugar só

# Palavras que aparecem em toda avaliação de dentista e não distinguem nada.
# Sem cortar, o "vocabulário do paciente" vira 'muito, ótimo, atendimento'.
VAZIAS = set("""a o e de da do que em um uma para com por na no as os um dos das
muito bem mais como mas ele ela eu me meu minha nos nas foi ser sou está esta
sempre todos toda todo tudo ja já ate até sem ao aos pela pelo isso isto la lá
aqui onde quando quem qual esse essa este aquele nao não sim tambem também
super otimo ótimo otima ótima excelente bom boa melhor maravilhoso maravilhosa
recomendo indico parabens parabéns nota atendimento clinica clínica equipe
profissional profissionais lugar local pessoal gente vez vezes dia dias hoje
tempo sempre agora antes depois toda todas ai aí so só pra pro num numa
desde ainda aqui entao então porem porém pois cada outro outra outros outras
fui fiz fazer faz feito dar dei deu ter tem tinha estava estao estão sendo
dentista dentistas dentaria dentário dentaria consulta consultas
estou estava estamos vou vai foram eram""".split())

# A contagem tira o acento para não separar "recepção" de "recepcao". Na hora
# de MOSTRAR, o acento volta — palavra sem acento num relatório que vai para o
# franqueado parece erro nosso, não escolha de método.
ACENTOS = {"recepcao": "recepção", "experiencia": "experiência",
           "atencao": "atenção", "educacao": "educação", "paciencia": "paciência",
           "explicacao": "explicação", "avaliacao": "avaliação",
           "orcamento": "orçamento", "criancas": "crianças", "crianca": "criança",
           "otimo": "ótimo", "otima": "ótima", "simpatico": "simpático",
           "simpatica": "simpática", "rapido": "rápido", "rapida": "rápida",
           "confianca": "confiança", "seguranca": "segurança", "familia": "família",
           "sorriso": "sorriso", "atendimentos": "atendimentos"}


def sem_acento(s):
    s = unicodedata.normalize("NFKD", str(s or ""))
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def jsonl(nome):
    p = SERIE/f"{nome}.jsonl"
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] \
        if p.exists() else []


def ultimo(rows, praca, chave=None):
    rs = [r for r in rows if r.get("praca_id") == praca]
    if not rs:
        return []
    corte = max(r["snapshot_date"] for r in rs)
    return [r for r in rs if r["snapshot_date"] == corte]


# ───────────────────────── 1 · as portas do mapa ────────────────────────────

def portas_do_mapa(portas):
    """Separa em três: onde estamos bem, onde sumimos, e onde não tem dono."""
    medidas = [d for d in portas if d.get("mapa")]
    dentro = [d for d in medidas if d["mapa"].get("nossa_posicao")]
    fora = [d for d in medidas if not d["mapa"].get("nossa_posicao")]
    sem_dono = [d for d in medidas
                if d["mapa"].get("quem")
                and (d["mapa"]["quem"][0].get("avaliacoes") or 0) < FRACO]
    return medidas, dentro, fora, sem_dono


def familia_da_porta(frase):
    """A palavra-raiz da porta. É ela que revela o padrão: em Londrina a
    unidade lidera TODA porta com 'ortodontia' e some de TODA porta com
    'dentista' — dois mundos, e o segundo é o mais digitado."""
    f = sem_acento(frase)
    # a ordem importa: 'aparelho ortodôntico' é porta de APARELHO, não de
    # ortodontia. Testar 'ortodont' primeiro esvaziava a família aparelho.
    if "aparelho" in f or "alinhador" in f or "invisalign" in f:
        return "aparelho"
    if "ortodont" in f:
        return "ortodontia"
    if "dentista" in f:
        return "dentista"
    return "outro"


def anuncio_e_local(a, cidades, nomes_da_praca):
    """A biblioteca de anúncios do Meta devolve anunciante de fora.

    Buscar "OrthoDontic" com filtro de país trouxe CANADIAN ORTHODONTIC
    PARTNERS CORP., DE ROODE ORTHODONTICS PA e Gerety Orthodontic Seminars
    para dentro de Londrina — a busca casa NOME DE PÁGINA e o filtro de país
    não segura. Mostrar isso como 'concorrente anunciando na sua praça' seria
    o tipo de erro que o franqueado percebe na primeira olhada e não perdoa.

    Só passa quem tem a cidade no nome ou no texto, quem aparece na varredura
    da praça, ou quem escreve em português."""
    nome = sem_acento(a.get("anunciante"))
    txt = sem_acento(a.get("texto") or "")
    for c in cidades:
        chave = sem_acento(c.split("/")[0]).split()[-1]
        if chave in nome or chave in txt:
            return True
    if nome in nomes_da_praca:
        return True
    if txt and re.search(r"\b(voce|agende|sorriso|consulta|avalia|gratuit|"
                         r"aparelho|dentista|nao|marque|clique)\b", txt):
        return True
    return False


# ───────────────────── 5 · o vocabulário do paciente ────────────────────────

def vocabulario(revs, minimo=4):
    """As palavras que os pacientes DESTA praça escrevem.

    Não é análise de sentimento: é a redação do anúncio. O paciente que
    escreveu a avaliação é o mesmo perfil de quem vai clicar, e ele já disse,
    com as palavras dele, o que veio buscar e o que achou importante."""
    txt = [r["texto"] for r in revs if r.get("texto")]
    if not txt:
        return [], 0
    conta = Counter()
    for t in txt:
        for w in re.findall(r"[a-zà-úç]{4,}", sem_acento(t)):
            if w not in VAZIAS:
                conta[w] += 1
    return ([(ACENTOS.get(w, w), n) for w, n in conta.most_common(40) if n >= minimo],
            len(txt))


def servicos_citados(revs):
    """Que tratamento o paciente nomeia. Diz o que a praça procura de verdade."""
    MAPA = {
        "aparelho": ["aparelho", "aparelhos", "ortodontia", "ortodontico", "bracket"],
        "aparelho invisível": ["invisivel", "alinhador", "invisalign", "transparente"],
        "implante": ["implante", "implantes", "protese", "prótese"],
        "clareamento": ["clareamento", "clarear", "branqueamento"],
        "canal": ["canal", "endodontia"],
        "extração / siso": ["siso", "extracao", "extrair", "arrancar"],
        "limpeza / profilaxia": ["limpeza", "profilaxia", "tartaro"],
        "estética / lentes": ["lente", "lentes", "faceta", "facetas", "resina",
                              "harmonizacao"],
        "criança": ["filho", "filha", "crianca", "bebe", "odontopediatra"],
        "urgência / dor": ["dor", "dores", "urgencia", "emergencia", "quebrou"],
    }
    txt = " ".join(sem_acento(r.get("texto") or "") for r in revs)
    fora = []
    for nome, palavras in MAPA.items():
        n = sum(len(re.findall(rf"\b{p}", txt)) for p in palavras)
        if n:
            fora.append({"servico": nome, "mencoes": n})
    return sorted(fora, key=lambda x: -x["mencoes"])


# ──────────────────────────── as oportunidades ──────────────────────────────

def monta(praca):
    ident = json.loads((IDENT/f"{praca}.json").read_text(encoding="utf-8"))
    rotulo = ident.get("rotulo") or praca
    nossos = {l["local_id"] for l in ident.get("locais", [])
              if l.get("papel") == "proprio"}

    portas = ultimo(jsonl("portas"), praca)
    # o filtro de lugar mudou depois de coletar Riomafra, onde 'dentista em
    # mafra portugal' passou. Aplicar na leitura também evita ter de recoletar
    # só por causa de uma linha de regex.
    ufs = ident.get("uf") or []
    portas = [d for d in portas
              if d.get("intencao") != "RUÍDO" and frase_util(d["frase"], ufs)]
    revs = [r for r in jsonl("reviews") if r.get("praca_id") == praca
            and r.get("local_id") not in nossos]
    revs_nossas = [r for r in jsonl("reviews") if r.get("praca_id") == praca
                   and r.get("local_id") in nossos]
    cidades = ident.get("cidades") or []
    nomes_praca = {sem_acento(l.get("nome")) for l in ident.get("locais", [])}
    nomes_praca |= {sem_acento(r.get("nome")) for r in ultimo(jsonl("categoria"), praca)}
    brutos = [a for a in ultimo(jsonl("anuncios"), praca) if a.get("ativo")]
    ads = [a for a in brutos if anuncio_e_local(a, cidades, nomes_praca)]
    de_fora = sorted({a["anunciante"] for a in brutos} -
                     {a["anunciante"] for a in ads})

    medidas, dentro, fora, sem_dono = portas_do_mapa(portas)
    por_familia = defaultdict(lambda: {"dentro": 0, "fora": 0, "frases_fora": []})
    for d in medidas:
        fam = familia_da_porta(d["frase"])
        if d["mapa"].get("nossa_posicao"):
            por_familia[fam]["dentro"] += 1
        else:
            por_familia[fam]["fora"] += 1
            por_familia[fam]["frases_fora"].append(d["frase"])

    por_int = Counter(d["intencao"] for d in portas)
    # a lista de palavras-que-não-são-bairro cresce toda vez que uma praça
    # nova ensina uma. Filtrar na LEITURA faz a correção valer para o que já
    # está gravado, sem recoletar.
    bairros = sorted({w for d in portas if d.get("bairro_palavras")
                      for w in d["bairro_palavras"] if w not in NAO_E_BAIRRO})
    convenios = sorted({d["frase"] for d in portas if d["intencao"] == "CONVÊNIO"})

    voc, n_txt = vocabulario(revs)
    voc_nosso, n_nosso = vocabulario(revs_nossas)
    servicos = servicos_citados(revs)

    return {"praca_id": praca, "rotulo": rotulo,
            "portas_total": len(portas), "portas_medidas": len(medidas),
            "dentro": dentro, "fora": fora, "sem_dono": sem_dono,
            "por_familia": dict(por_familia), "por_intencao": dict(por_int),
            "bairros": bairros, "convenios": convenios,
            "vocabulario_da_praca": voc, "avaliacoes_lidas": n_txt,
            "vocabulario_da_unidade": voc_nosso, "avaliacoes_da_unidade": n_nosso,
            "servicos_citados": servicos,
            "anunciantes_ativos": sorted({a["anunciante"] for a in ads}),
            "anuncios_ativos": len(ads),
            "anunciantes_descartados": de_fora}


def imprime(o):
    L = o["rotulo"]
    print(f"\n{'='*78}\n  ONDE CAPTAR · {L}\n{'='*78}")
    print(f"\n  {o['portas_total']} portas encontradas no autocompletar do Google, "
          f"{o['portas_medidas']} medidas no mapa.")

    # 1 — a porta onde sumimos
    if o["portas_medidas"]:
        print(f"\n  ── 1 · AS PORTAS ONDE A UNIDADE NÃO APARECE  "
              f"({len(o['fora'])} de {o['portas_medidas']})")
        fam = o["por_familia"]
        for nome in ("ortodontia", "aparelho", "dentista", "outro"):
            f = fam.get(nome)
            if not f or (f["dentro"] + f["fora"]) == 0:
                continue
            print(f"     '{nome}': aparece em {f['dentro']}, some em {f['fora']}")
        # o padrão só salta quando as famílias ficam lado a lado
        forte = [n for n, f in fam.items() if f["dentro"] and not f["fora"]]
        sumida = [n for n, f in fam.items() if f["fora"] and not f["dentro"]]
        if forte and sumida:
            print(f"\n     → A unidade é dona da porta '{forte[0]}' e não existe na "
                  f"porta '{sumida[0]}'.")
            print(f"       São dois públicos: quem já sabe que quer aparelho, e quem "
                  f"só sabe\n       que precisa de dentista. O segundo é o mais "
                  f"digitado, e é o que\n       vira consulta de avaliação.")
        for d in o["fora"][:8]:
            topo = d["mapa"]["quem"][0] if d["mapa"]["quem"] else {}
            print(f"       · {d['frase'][:46]:46s} topo: {str(topo.get('nome'))[:26]:26s}"
                  f" ({topo.get('avaliacoes')})")

    # 2 — porta sem dono
    if o["sem_dono"]:
        print(f"\n  ── 2 · PORTAS SEM DONO  ({len(o['sem_dono'])})")
        print(f"     quem está no topo tem menos de {FRACO} avaliações — passar "
              f"custa pouco:")
        for d in o["sem_dono"][:6]:
            t = d["mapa"]["quem"][0]
            print(f"       · {d['frase'][:46]:46s} {t['nome'][:26]:26s} "
                  f"({t.get('avaliacoes')} avaliações)")

    # 3 — bairros
    if o["bairros"]:
        print(f"\n  ── 3 · O QUE A CIDADE COLA NA BUSCA  ({len(o['bairros'])})")
        print("       " + " · ".join(o["bairros"]))
        print("     São bairros, faculdades, nomes de clínica e de doutor — tudo que")
        print("     a cidade digita junto e o vocabulário genérico não previa. Cada")
        print("     um é uma busca com endereço, e o bairro é o que a ficha e o site")
        print("     precisam dizer para aparecer nela.")

    # 4 — convênios
    if o["convenios"]:
        print(f"\n  ── 4 · OS CONVÊNIOS QUE A CIDADE PROCURA  ({len(o['convenios'])})")
        for c in o["convenios"][:8]:
            print(f"       · {c}")
        print("     ⚠ O dado público não diz se a unidade aceita. É a pergunta")
        print("       de uma linha para o franqueado — e ela vale dinheiro nos dois")
        print("       sentidos: se aceita e não diz, perde de graça.")

    # 5 — vocabulário
    if o["vocabulario_da_praca"]:
        print(f"\n  ── 5 · AS PALAVRAS DO PACIENTE DESTA PRAÇA")
        print(f"     de {o['avaliacoes_lidas']} avaliações escritas por pacientes "
              f"da concorrência:")
        print("       " + " · ".join(f"{w} ({n})" for w, n in o["vocabulario_da_praca"][:16]))
        if o["servicos_citados"]:
            print("     o que eles dizem que foram buscar:")
            for s in o["servicos_citados"][:6]:
                print(f"       {s['mencoes']:>5} × {s['servico']}")

    if o["anuncios_ativos"]:
        print(f"\n  ── QUEM ESTÁ ANUNCIANDO NA PRAÇA  ({o['anuncios_ativos']} anúncios)")
        print("       " + " · ".join(o["anunciantes_ativos"][:8]))
    if o["anunciantes_descartados"]:
        print(f"     ⚠ {len(o['anunciantes_descartados'])} anunciantes descartados "
              f"por não serem da praça:")
        print("       " + " · ".join(o["anunciantes_descartados"][:5]))

    print("\n  O QUE ISTO NÃO DIZ:")
    print("   · não é volume de busca. Diz que a frase existe e como se escreve.")
    print("     Volume e custo por clique exigem conta de Google Ads.")
    print("   · 'aparece no mapa' é a busca de lugares, não a página de resultados.")
    print("     A ficha resolve o mapa; o anúncio resolve o topo da página.")
    print("   · o vocabulário sai de quem AVALIOU, que não é o mesmo que quem")
    print("     procurou e desistiu. É a melhor amostra que existe de graça.\n")


def leitura_da_rede(todos):
    """Isso vale para a rede ou só para uma cidade?

    É a pergunta que separa achado de coincidência, e é a única que a
    franqueadora compra. Uma unidade fora da porta 'dentista' é problema do
    franqueado; sete unidades fora da porta 'dentista' é decisão de rede sobre
    como as fichas são cadastradas."""
    print(f"\n{'='*78}\n  ISSO VALE PARA A REDE?  ({len(todos)} praças)\n{'='*78}")
    tot = defaultdict(lambda: {"dentro": 0, "fora": 0, "pracas_fora": []})
    for o in todos:
        for fam, f in o["por_familia"].items():
            tot[fam]["dentro"] += f["dentro"]
            tot[fam]["fora"] += f["fora"]
            if f["fora"] and not f["dentro"]:
                tot[fam]["pracas_fora"].append(o["rotulo"])
    print(f"\n  {'família da porta':18s} {'aparece':>8s} {'some':>6s}   praças onde some em TODAS")
    for fam in ("aparelho", "ortodontia", "dentista", "outro"):
        f = tot.get(fam)
        if not f or (f["dentro"]+f["fora"]) == 0:
            continue
        print(f"  {fam:18s} {f['dentro']:>8d} {f['fora']:>6d}   "
              f"{len(f['pracas_fora'])} de {len(todos)}")
    d = tot.get("dentista", {})
    a = tot.get("aparelho", {})
    if d.get("fora") and a.get("dentro"):
        print(f"\n  → A rede é dona da porta 'aparelho' ({a['dentro']} aparições) e")
        print(f"    quase não existe na porta 'dentista' ({d['fora']} ausências contra")
        print(f"    {d.get('dentro', 0)} aparições).")
        print("    Um franqueado fora dessa porta é problema dele. A rede inteira fora")
        print("    dela é decisão de como a ficha do Google é cadastrada — e isso a")
        print("    franqueadora resolve uma vez, para as 340.")

    bairros = {o["rotulo"]: len(o["bairros"]) for o in todos if o["bairros"]}
    if bairros:
        print(f"\n  BAIRROS que a cidade digita, por praça:")
        for r, n in sorted(bairros.items(), key=lambda x: -x[1]):
            print(f"    {n:>3d}  {r}")

    conv = Counter()
    for o in todos:
        for c in o["convenios"]:
            for plano in ("unimed", "amil", "bradesco", "sulamerica", "odontoprev",
                          "metlife", "hapvida", "uniodonto", "interodonto", "porto"):
                if plano in sem_acento(c):
                    conv[plano] += 1
    if conv:
        print(f"\n  CONVÊNIOS procurados, em quantas praças:")
        print("    " + " · ".join(f"{p} ({n})" for p, n in conv.most_common(8)))
        print("    A rede sabe quais unidades aceitam quais planos. Nós não — e é")
        print("    cruzamento de uma planilha só.")

    serv = Counter()
    for o in todos:
        for s in o["servicos_citados"][:3]:
            serv[s["servico"]] += 1
    if serv:
        print(f"\n  O QUE O PACIENTE DIZ QUE FOI BUSCAR — top 3 de cada praça:")
        print("    " + " · ".join(f"{s} ({n} praças)" for s, n in serv.most_common(6)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--praca", action="append", default=[])
    ap.add_argument("--todas", action="store_true")
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()

    pracas = list(a.praca)
    if a.todas:
        pracas = sorted(p.stem for p in IDENT.glob("*.json"))
    if not pracas:
        sys.exit("use --praca <id> ou --todas")

    fora = []
    for p in pracas:
        try:
            o = monta(p)
        except FileNotFoundError:
            print(f"  {p}: sem identidade"); continue
        if not o["portas_total"]:
            print(f"\n  {o['rotulo']}: nenhuma porta coletada ainda — rode "
                  f"`python3 coleta/coletores/portas.py --praca {p} --salvar`")
            continue
        imprime(o)
        fora.append(o)

    if len(fora) > 1:
        leitura_da_rede(fora)

    if a.salvar and fora:
        hoje = dt.date.today().isoformat()
        SERIE.mkdir(parents=True, exist_ok=True)
        with (SERIE/"captacao.jsonl").open("a", encoding="utf-8") as f:
            for o in fora:
                f.write(json.dumps({"snapshot_date": hoje, **o}, ensure_ascii=False)+"\n")
        print(f"  → dados/serie/captacao.jsonl +{len(fora)}\n")


if __name__ == "__main__":
    main()
