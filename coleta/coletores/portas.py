#!/usr/bin/env python3
"""
portas.py — as frases que a cidade digita no Google, e quem responde por elas.

O franqueado não precisa de lista de palavra-chave. Ele precisa saber **por
qual porta o paciente da cidade dele entra, e em qual dessas portas não tem
ninguém**. Isso é uma coisa diferente, e dá para medir de graça.

A fonte é o autocompletar do Google — o mesmo que aparece embaixo da barra de
busca. Ele não é opinião: é o que gente de verdade digitou o suficiente para
virar sugestão. E ele é local: buscar "dentista londrina " devolveu

    dentista londrina centro · dentista londrina barato · dentista londrina
    saul elkind · dentista londrina 24 horas · dentista londrina gratuito ·
    dentista londrina unimed · dentista londrina bem avaliados

Sete portas diferentes numa cidade só — bairro, preço, urgência, convênio,
reputação. Nenhuma delas está no material da rede.

O que este coletor NÃO é, e precisa estar dito:
  · **não é volume de busca.** O autocompletar diz que a frase EXISTE e como
    ela é escrita; não diz quantas pessoas por mês. Volume e custo por clique
    só vêm do Planejador de Palavras-chave, que exige conta de Google Ads.
  · **não é a página de resultados.** Quem responde é medido pela busca de
    lugares do Google — ou seja, o MAPA. É onde boa parte da busca local
    converte, mas não é o anúncio nem o resultado orgânico.

Uso:
    python3 coleta/coletores/portas.py --praca londrina
    python3 coleta/coletores/portas.py --cidade "Macapá/AP" --sem-quem-responde
"""
import argparse, json, os, pathlib, re, subprocess, sys, time, unicodedata
import urllib.parse
import datetime as dt

RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent
IDENT = RAIZ/"dados"/"identidade"
SERIE = RAIZ/"dados"/"serie"
SUG = "https://suggestqueries.google.com/complete/search"
API = "https://places.googleapis.com/v1/places:searchText"
CAMPOS = ("places.id,places.displayName,places.userRatingCount,places.rating,"
          "places.formattedAddress,places.websiteUri")

# As sementes. São as dez maneiras de a pessoa começar a frase — e não são
# sinônimos: quem digita "quanto custa aparelho" está numa etapa da decisão,
# quem digita "manutenção de aparelho" está em outra.
SEMENTES = [
    ("aparelho ortodôntico", True), ("aparelho nos dentes", False),
    ("ortodontista", True), ("dentista", True),
    ("aparelho invisível", False), ("alinhador invisível", False),
    ("manutenção de aparelho", False), ("colocar aparelho", False),
    ("quanto custa aparelho", False), ("clínica odontológica", False),
]
LETRAS = "abcdefghijlmnopqrstuv"      # sem k, w, x, y, z: quase não abrem nada
PERGUNTAS = ["quanto custa {s} em {c}", "onde colocar {s} em {c}",
             "melhor {s} {c}", "{s} {c} preço", "{s} perto de mim {c}"]

# O que a frase quer. A ordem importa: a primeira que casar ganha, e preço
# vence convênio porque "aparelho barato unimed" é conversa de preço.
INTENCAO = [
    ("RUÍDO", ["vaga", "emprego", "salario", "curso", "faculdade", "concurso",
               "cro ", "residencia", "especializacao", "apostila", "prova"]),
    ("PREÇO", ["quanto custa", "preco", "preço", "valor", "barato", "promocao",
               "parcelad", "quanto fica", "quanto sai", "custo", "mais barato"]),
    ("GRATUITO", ["gratuito", "gratis", "sus", "popular", "de graca", "publico"]),
    ("CONVÊNIO", ["unimed", "amil", "bradesco", "sulamerica", "odontoprev",
                  "convenio", "plano", "servir", "ipe", "cassi", "hapvida",
                  "uniodonto", "metlife", "porto seguro", "interodonto"]),
    ("URGÊNCIA", ["24 horas", "urgencia", "emergencia", "plantao", "aberto agora",
                  "domingo", "sabado", "feriado", "hoje", "agora"]),
    ("TIPO DE APARELHO", ["invisivel", "transparente", "autoligado", "safira",
                          "estetico", "lingual", "metalico", "alinhador",
                          "movel", "removivel", "contencao", "invisalign"]),
    ("CRIANÇA", ["infantil", "kids", "crianca", "bebe", "odontopediatra",
                 "pediatra", "adolescente"]),
    ("REPUTAÇÃO", ["melhor", "bem avaliad", "top ", "ranking", "indicacao",
                   "recomendad", "confiavel", "bom "]),
    ("DÚVIDA", ["como ", "o que e", "doi ", "doe ", "quanto tempo", "pode ",
                "qual ", "porque", "por que", "vale a pena", "funciona",
                "cuidados", "quantos anos", "idade"]),
]

# Palavras que aparecem sobrando na frase mas NÃO são bairro: são modificadores
# comuns que o autocompletar cola. Sem esta lista, 'abertos' e 'avaliados'
# viravam nome de bairro.
NAO_E_BAIRRO = {"abertos", "aberto", "avaliados", "avaliado", "rua", "avenida",
                "dentro", "perto", "proximo", "melhores", "bons", "boa", "atende",
                "atendimento", "clinicas", "consultorio", "consultorios", "onde",
                "tem", "fica", "ficam", "sao", "hoje", "agora", "horas", "hora",
                "particular", "especializado", "especializada", "especialista",
                "geral", "adulto", "adultos", "mulher", "homem", "noturno",
                "manha", "tarde", "noite", "brasil", "cirurgiao", "cirurgia",
                "doutor", "doutora", "melhores", "otimo", "barato", "barata",
                "urgente", "emergencia", "convenio", "plano", "planos"}


# Existe Mafra em Portugal, e "dentista em mafra portugal" entrou na coleta de
# Mafra. Existe rua Conselheiro Mafra em Joinville. Nome de cidade brasileira
# repete e cruza fronteira — é a mesma armadilha que contaminou Cuiabá com
# Várzea Paulista, e ela volta em toda fonte nova.
OUTRO_LUGAR = (r"\b(portugal|lisboa|coimbra|braga|espanha|argentina|paraguai|"
               r"estados unidos|eua|florida|orlando|sao paulo|curitiba|goiania|"
               r"belo horizonte|rio de janeiro|porto alegre|salvador|recife|"
               r"fortaleza|brasilia|campinas|maringa|limeira|uberlandia|"
               r"joinville|blumenau|florianopolis)\b")


UFS = ("ac al ap am ba ce df es go ma mt ms mg pa pb pr pe pi rj rn rs ro rr "
       "sc sp se to").split()

# Nome de cidade brasileira também é nome de cidade lá fora. Expandindo
# "dentista Palmas" pelo alfabeto vieram Las Palmas de Gran Canaria, Palmas
# em Ixtapaluca (México), e um "dottor palmas dentista in romania". O
# autocompletar ignora hl=pt-BR&gl=br quando o nome é internacional.
# Só entram tokens que NÃO existem em português — 'barato' e 'melhor' ficam
# de fora da lista de propósito, porque são palavras nossas também.
ESTRANGEIRO = (r"\b(las|los|del|abierto|colegio|adeslas|cerca|dottor|"
               r"recensioni|sardo|moldavia|romania|bergamo|canaria|triana|"
               r"tijuana|juarez|ixtapaluca|dentist|dentists|clinic|near|best|"
               r"cheap|smile care|mesa y lopez|prezzi|studio dentistico|"
               r"en allen|en catriel|allen|catriel|adeslas|conselheiro mafra|"
               r"en viedma|viedma|young|rosario|neuquen|cordoba|mendoza)\b"
               r"|\ben\s")


def frase_util(frase, ufs, cidades=None):
    """O filtro único, usado na coleta E na leitura.

    Estava em três lugares e os três divergiram: a coleta filtrava uma coisa,
    o radar do franqueado outra, e o plano do franqueado nenhuma — então a
    lista de bairros de Palmas saía com Ixtapaluca e Las Adeslas dentro. Uma
    regra só, num lugar só.

    `cidades` É OBRIGATÓRIO QUANDO A PRAÇA É CIDADE GRANDE. A lista
    OUTRO_LUGAR nasceu para tirar "dentista São Paulo" de dentro da coleta
    de Mafra, e traz joinville, curitiba, goiania e porto alegre. No dia em
    que essas cidades viraram praça, o filtro passou a reprovar as 160
    portas de Joinville — inclusive "aparelho ortodontico joinville" — e a
    captação saiu vazia nas cinco. Cidade só é OUTRO lugar quando não é a
    NOSSA."""
    f = sem_acento(frase)
    proprias = {sem_acento(str(c).split("/")[0]).strip()
                for c in (cidades or []) if c}
    fora = OUTRO_LUGAR
    for c in proprias:
        if c and c in fora:
            # tira a própria cidade da lista de "outro lugar", com as
            # barras de palavra intactas
            fora = fora.replace(f"{c}|", "").replace(f"|{c}", "")
    if re.search(fora, f) or re.search(ESTRANGEIRO, f):
        return False
    ufs = [u for u in (ufs or []) if u]
    if ufs and all(uf_errada(frase, u) for u in ufs):
        return False
    return True


def uf_errada(frase, uf):
    """Palmas existe no TO e no PR, e Palmas de Monte Alto existe na BA.

    'dentista palmas pr' entrou na coleta de Palmas/TO e mediu o mapa da
    cidade errada. É a terceira vez que cidade homônima contamina uma fonte
    neste projeto — em canais.py, em google_places.py e agora aqui. A regra é
    sempre a mesma: se aparece uma UF na frase e não é a nossa, não é nossa."""
    f = " " + sem_acento(frase) + " "
    if not uf:
        return False
    alvo = sem_acento(uf)
    for u in UFS:
        if u != alvo and re.search(rf"\b{u}\b", f):
            return True
    return bool(re.search(r"\bde monte alto\b", f))


def sem_acento(s):
    s = unicodedata.normalize("NFKD", str(s or ""))
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def chave():
    k = os.environ.get("GOOGLE_API_KEY", "").strip()
    if not k:
        env = RAIZ/"_pipeline"/".env"
        if env.exists():
            for l in env.read_text(encoding="utf-8").split("\n"):
                if l.strip().startswith("GOOGLE_API_KEY="):
                    k = l.split("=", 1)[1].strip().replace("\r", "")
    return k


def sugere(q, tent=2):
    """O autocompletar devolve latin-1 mesmo pedindo utf-8. Decodificar errado
    transforma 'ortodôntico' em lixo e o termo some do relatório."""
    u = (f"{SUG}?client=firefox&hl=pt-BR&gl=br&q={urllib.parse.quote(q)}")
    for i in range(tent):
        r = subprocess.run(["curl", "-sS", "-m", "20", "-H", "User-Agent: Mozilla/5.0", u],
                           capture_output=True)
        bruto = r.stdout or b""
        if bruto.strip():
            try:
                txt = bruto.decode("utf-8")
            except UnicodeDecodeError:
                txt = bruto.decode("latin-1")
            try:
                return json.loads(txt)[1]
            except Exception:
                pass
        time.sleep(1.5*(i+1))
    return []


def intencao(frase):
    """Casa por borda de palavra quando a chave é uma palavra inteira.

    Sem isso, 'doi' (de 'dói') casava com 'dentista dois irmãos londrina' e um
    BAIRRO virava DÚVIDA. É o mesmo erro de 'orthodontics' contendo
    'orthodontic': comparar por 'contém' erra calado."""
    f = " " + sem_acento(frase) + " "
    for nome, palavras in INTENCAO:
        for p in palavras:
            alvo = sem_acento(p)
            if alvo.endswith(" ") or " " in alvo.strip():
                if alvo in f:
                    return nome
            elif re.search(rf"\b{re.escape(alvo)}", f):
                return nome
    return "GENÉRICO"


def acha_bairros(portas, cidade):
    """O bairro só aparece olhando o conjunto, nunca a frase sozinha.

    'dentista londrina saul elkind' é indistinguível de 'dentista londrina bem
    avaliados' para um classificador de palavra-chave. O que separa os dois é
    que 'saul' e 'elkind' não estão em vocabulário nenhum e voltam juntos em
    mais de uma busca. Foi assim que saíram nove bairros de Londrina — Zona
    Norte, Gleba, Centro, Lindóia, Dois Irmãos, Santa Luzia, Saul Elkind,
    Santos Dumont e a UEL — e nenhum deles estava em lista feita à mão."""
    conhecidas = set(NAO_E_BAIRRO)
    for _, palavras in INTENCAO:
        for pl in palavras:
            conhecidas.update(sem_acento(pl).split())
    conhecidas.update(sem_acento(" ".join(x for x, _ in SEMENTES)).split())
    conhecidas.update(sem_acento(cidade.replace("/", " ")).split())
    conhecidas.update(["aparelho", "aparelhos", "dentista", "dentistas",
                       "ortodontista", "ortodontistas", "dente", "dentes",
                       "clinica", "odontologica", "odontologia", "odonto",
                       "em", "de", "da", "do", "no", "na", "com", "para", "por",
                       "que", "mim", "e", "a", "o", "os", "as", "um", "uma",
                       "mais", "menos", "ou", "meu", "minha", "pra"])
    conta = {}
    for d in portas:
        if d["intencao"] == "RUÍDO":
            continue
        for w in re.findall(r"[a-zà-ú]{3,}", sem_acento(d["frase"])):
            if w not in conhecidas:
                conta[w] = conta.get(w, 0) + 1
    # uma palavra desconhecida que só apareceu uma vez pode ser erro de digitação
    candidatas = {w for w, n in conta.items() if n >= 2}
    for d in portas:
        if d["intencao"] not in ("GENÉRICO", "REPUTAÇÃO"):
            continue
        achadas = [w for w in re.findall(r"[a-zà-ú]{3,}", sem_acento(d["frase"]))
                   if w in candidatas]
        if achadas:
            d["intencao"] = "BAIRRO"
            d["bairro_palavras"] = achadas
    return sorted(conta.items(), key=lambda x: -x[1])


def descobre(cidade, pausa=0.25):
    """Expande as sementes até a frase parar de crescer.

    A expansão por letra é o que acha o que ninguém pensou em procurar: foi
    assim que apareceram 'saul elkind' (um bairro de Londrina) e 'servir' (o
    plano de saúde dos servidores em Palmas). Nenhum dos dois estaria numa
    lista feita à mão."""
    nome = cidade.split("/")[0].strip()
    achadas, feitas = {}, 0

    def guarda(frase, de_onde):
        f = frase.strip()
        if f and f.lower() not in achadas:
            achadas[f.lower()] = {"frase": f, "descoberta_em": de_onde}

    for semente, fundo in SEMENTES:
        for base in (f"{semente} {nome}", f"{semente} em {nome}"):
            for s in sugere(base):
                guarda(s, base)
            feitas += 1
            time.sleep(pausa)
        if fundo:
            for letra in LETRAS:
                for s in sugere(f"{semente} {nome} {letra}"):
                    guarda(s, f"{semente} {nome} {letra}…")
                feitas += 1
                time.sleep(pausa)
    for molde in PERGUNTAS:
        for semente, _ in SEMENTES[:5]:
            q = molde.format(s=semente, c=nome)
            for s in sugere(q):
                guarda(s, q)
            feitas += 1
            time.sleep(pausa)

    # Só interessa o que fala da cidade OU o que é dúvida/preço genérica —
    # "aparelho invisivel limeira" apareceu buscando Londrina e não é nossa.
    chave_cidade = sem_acento(nome).split()[-1]
    fora = []
    for d in achadas.values():
        f = sem_acento(d["frase"])
        local = chave_cidade in f
        outra_cidade = bool(re.search(OUTRO_LUGAR, f))
        if outra_cidade and not local:
            continue
        if uf_errada(d["frase"], (cidade.split("/") + [""])[1]):
            continue
        if re.search(ESTRANGEIRO, f):
            continue
        d["local"] = local
        d["intencao"] = intencao(d["frase"])
        fora.append(d)
    return fora, feitas


def quem_responde(frase, cidade, key, nossos):
    """Quem o Google mostra no MAPA para essa frase, e em que posição estamos.

    Não é a página de resultados nem o anúncio — é a busca de lugares. Dizer
    que é a mesma coisa seria mentira, e a diferença muda a recomendação: a
    ficha resolve o mapa, o anúncio resolve o topo da página."""
    corpo = {"textQuery": f"{frase} {cidade}" if sem_acento(cidade.split('/')[0]).split()[-1]
             not in sem_acento(frase) else frase,
             "languageCode": "pt-BR", "maxResultCount": 10}
    r = subprocess.run(["curl", "-sS", "-m", "40", "-X", "POST", API,
                        "-H", "Content-Type: application/json",
                        "-H", f"X-Goog-Api-Key: {key}",
                        "-H", f"X-Goog-FieldMask: {CAMPOS}",
                        "-d", json.dumps(corpo, ensure_ascii=False)],
                       capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
    except Exception:
        return None
    if "error" in d:
        return None
    lst = d.get("places", [])
    pos, quem = None, []
    for i, p in enumerate(lst[:10], 1):
        n = p.get("displayName", {}).get("text") or ""
        quem.append({"posicao": i, "nome": n,
                     "avaliacoes": p.get("userRatingCount"), "nota": p.get("rating")})
        if p.get("id") in nossos and pos is None:
            pos = i
    return {"nossa_posicao": pos, "resultados": len(lst), "quem": quem[:5]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--praca", help="praca_id de dados/identidade")
    ap.add_argument("--cidade", help='ex: "Macapá/AP" — para praça que ainda não existe')
    ap.add_argument("--sem-quem-responde", action="store_true",
                    help="só o autocompletar, custo zero")
    ap.add_argument("--quantas", type=int, default=25,
                    help="quantas frases medir no mapa (US$ 0,032 cada)")
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()

    if a.praca:
        ident = json.loads((IDENT/f"{a.praca}.json").read_text(encoding="utf-8"))
        cidades = ident.get("cidades") or []
        praca_id = a.praca
        nossos = {l.get("place_id") for l in ident.get("locais", [])
                  if l.get("papel") == "proprio" and l.get("place_id")}
        rotulo = ident.get("rotulo") or praca_id
    elif a.cidade:
        cidades = [a.cidade]
        praca_id = re.sub(r"[^a-z0-9]+", "_", sem_acento(a.cidade.split("/")[0])).strip("_")
        nossos, rotulo = set(), a.cidade
    else:
        sys.exit("use --praca <id> ou --cidade \"Nome/UF\"")

    hoje = dt.date.today().isoformat()
    print(f"\n{'='*78}\n  AS PORTAS DA CIDADE · {rotulo}\n{'='*78}")

    todas = []
    for cidade in cidades:
        portas, feitas = descobre(cidade)
        print(f"\n  {cidade}: {feitas} buscas no autocompletar → {len(portas)} frases")
        for d in portas:
            d["cidade"] = cidade
        todas += portas

    novas_global = acha_bairros(todas, cidades[0])
    por_int = {}
    for d in todas:
        por_int.setdefault(d["intencao"], []).append(d)
    ruido = por_int.pop("RUÍDO", [])

    print(f"\n  {len(todas)-len(ruido)} frases de paciente, "
          f"{len(ruido)} descartadas como ruído (vaga, curso, concurso)\n")
    for nome, _ in INTENCAO + [("BAIRRO", None), ("GENÉRICO", None)]:
        ds = por_int.get(nome)
        if not ds:
            continue
        locais = [d for d in ds if d["local"]]
        print(f"  ── {nome}  ({len(ds)} frases, {len(locais)} citam a cidade)")
        for d in (locais or ds)[:6]:
            print(f"       {d['frase']}")

    novas = [(w, n) for w, n in novas_global if n > 1 and w not in NAO_E_BAIRRO]
    if novas:
        print(f"\n  ── PALAVRAS QUE A CIDADE DIGITA E NÓS NÃO CONHECÍAMOS")
        print("     bairro, convênio, rua, marca — cada uma é uma porta com endereço:")
        print("       " + " · ".join(f"{w} ({n})" for w, n in novas[:18] if n > 1))

    medidas = []
    if not a.sem_quem_responde:
        key = chave()
        if not key:
            print("\n  ⚠ sem GOOGLE_API_KEY — pulei a medição de quem responde")
        else:
            alvo = [d for d in todas if d["intencao"] != "RUÍDO" and d["local"]][:a.quantas]
            print(f"\n  ── QUEM RESPONDE NO MAPA  ({len(alvo)} frases · "
                  f"US$ {0.032*len(alvo):.2f})")
            for d in alvo:
                q = quem_responde(d["frase"], d["cidade"], key, nossos)
                if not q:
                    continue
                d["mapa"] = q
                medidas.append(d)
                marca = (f"{q['nossa_posicao']}º" if q["nossa_posicao"]
                         else ("FORA" if nossos else "—"))
                topo = q["quem"][0]["nome"][:34] if q["quem"] else "(vazio)"
                print(f"       {marca:>4s}  {d['frase'][:44]:44s} topo: {topo}")

    if a.salvar:
        SERIE.mkdir(parents=True, exist_ok=True)
        with (SERIE/"portas.jsonl").open("a", encoding="utf-8") as f:
            for d in todas:
                f.write(json.dumps({"snapshot_date": hoje, "praca_id": praca_id,
                                    "rotulo": rotulo, **d,
                                    "fonte": "google autocomplete + places textsearch"},
                                   ensure_ascii=False)+"\n")
        print(f"\n  → dados/serie/portas.jsonl +{len(todas)}")

    print("\n  O QUE ISTO NÃO DIZ:")
    print("   · não é volume de busca. Diz que a frase EXISTE e como se escreve.")
    print("     Volume e custo por clique só com conta de Google Ads.")
    print("   · 'quem responde' é o MAPA do Google, não a página de resultados")
    print("     nem o anúncio. A ficha resolve o mapa; o anúncio resolve o topo.\n")


if __name__ == "__main__":
    main()
