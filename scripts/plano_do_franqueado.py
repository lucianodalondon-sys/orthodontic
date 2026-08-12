#!/usr/bin/env python3
"""
plano_do_franqueado.py — a mesma medição, escrita para quem vai fazer.

O `oportunidades_franqueado.py` fala como analista: porta, família, intenção,
posição no mapa. Está certo e é ilegível para quem precisa agir. O franqueado
é dentista, tem quarenta pacientes na agenda e quinze minutos entre um e
outro. Se ele não entender na primeira leitura, não vai fazer — e um achado
que ninguém executa não vale nada.

Este arquivo é a tradução, e ela tem regras:

  · **um número no topo, e só um.** "Você aparece em 5 das 18 buscas da sua
    cidade." É o número que ele repete para a recepcionista.
  · **no máximo cinco tarefas.** Com dez, ninguém faz nenhuma.
  · **grátis primeiro.** Gastar em anúncio antes de arrumar o cadastro é pagar
    por um clique que o perfil daria de graça.
  · **cada tarefa responde três perguntas**: o que está acontecendo (com o
    número), o que fazer (em passos), e como saber que funcionou.
  · **nenhuma palavra de jargão.** Não existe "porta", "intenção", "share",
    "SEO local". Existe "busca", "seu perfil do Google", "seu site".
  · **nada que a gente não mediu.** Se o dado não diz, a tarefa vira pergunta.

Uso:
    python3 scripts/plano_do_franqueado.py --praca londrina
    python3 scripts/plano_do_franqueado.py --todas --salvar --md
"""
import argparse, json, pathlib, re, sys, textwrap, unicodedata
from collections import Counter
import datetime as dt

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SERIE = RAIZ/"dados"/"serie"
IDENT = RAIZ/"dados"/"identidade"
PLANOS = RAIZ/"dados"/"planos"
PORTAL = RAIZ/"dados"/"portal"
sys.path.insert(0, str(RAIZ/"coleta"/"coletores"))
from portas import NAO_E_BAIRRO, frase_util     # noqa: E402  o mesmo filtro da coleta


def sem_acento(s):
    s = unicodedata.normalize("NFKD", str(s or ""))
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def jsonl(nome):
    p = SERIE/f"{nome}.jsonl"
    return [json.loads(l) for l in p.read_text(encoding="utf-8").split("\n") if l.strip()] \
        if p.exists() else []


def ultimo(rows, praca):
    rs = [r for r in rows if r.get("praca_id") == praca]
    if not rs:
        return []
    corte = max(r["snapshot_date"] for r in rs)
    return [r for r in rs if r["snapshot_date"] == corte]


def limpo(t):
    """Tira a marcação de negrito e itálico para o terminal. A ordem importa:
    tirar o itálico primeiro come um asterisco do negrito e sobra lixo."""
    return re.sub(r"\*(.+?)\*", r"\1", re.sub(r"\*\*(.+?)\*\*", r"\1", str(t)))


def n(x):
    return f"{int(x or 0):,}".replace(",", ".")


def lista(itens, ate=6):
    itens = list(itens)
    if len(itens) <= ate:
        return ", ".join(itens[:-1]) + (" e " + itens[-1] if len(itens) > 1 else "")
    return ", ".join(itens[:ate]) + f" e mais {len(itens)-ate}"


# ─────────────────────────── as tarefas ─────────────────────────────────────

def tarefa_dentista(c):
    """A maior de todas, e é de graça: aparecer na busca mais comum da cidade."""
    fam = c["por_familia"]
    d = fam.get("dentista") or {}
    total_d = (d.get("dentro") or 0) + (d.get("fora") or 0)
    if not total_d or (d.get("fora") or 0) == 0:
        return None
    fortes = [x for x in c["fora"]
              if "dentista" in sem_acento(x["frase"]) and x["mapa"].get("quem")]
    concorrentes = []
    for x in fortes[:6]:
        t = x["mapa"]["quem"][0]
        concorrentes.append(f"{t['nome']} ({n(t.get('avaliacoes'))} avaliações)")
    concorrentes = list(dict.fromkeys(concorrentes))[:3]

    bons = fam.get("aparelho", {}).get("dentro", 0) + fam.get("ortodontia", {}).get("dentro", 0)
    frase_boa = (f"Nas buscas com a palavra *aparelho* você aparece em {bons} de "
                 f"{bons + fam.get('aparelho', {}).get('fora', 0) + fam.get('ortodontia', {}).get('fora', 0)}. "
                 f"Quem já sabe que quer aparelho te encontra." if bons else "")

    dentro_d = d.get("dentro") or 0
    titulo = ("Você não aparece quando alguém procura “dentista” na sua cidade"
              if dentro_d == 0 else
              f"Você aparece em {dentro_d} das {total_d} buscas por “dentista” — "
              f"dá para subir")
    return {
        "titulo": titulo,
        "custo": "R$ 0", "tempo": "30 minutos", "quem": "você mesmo",
        "o_que_esta_acontecendo": [
            f"Testamos {total_d} buscas da sua cidade com a palavra *dentista* — "
            f"“dentista {c['rotulo'].split('· ')[-1].lower()}”, “dentista 24 horas”, "
            f"“dentista perto de mim”, e assim por diante.",
            (f"**Em {d.get('fora')} delas a sua clínica não apareceu entre as dez "
             f"primeiras do mapa do Google.**" if dentro_d == 0 else
             f"**A sua clínica aparece em {dentro_d} e fica de fora em "
             f"{d.get('fora')}** — nessas, quem procura não te encontra."),
            frase_boa,
            "São dois pacientes diferentes. Um já decidiu que quer aparelho e "
            "procura por isso. O outro só sabe que está com dor, ou que o filho "
            "precisa de dentista — e é ele que marca a avaliação."
            + (" **Hoje só o primeiro te encontra.**" if dentro_d == 0 else ""),
            (f"Quem aparece no seu lugar: {lista(concorrentes)}." if concorrentes else ""),
        ],
        "o_que_fazer": [
            "Abra o seu perfil do Google (o mesmo que mostra a nota e as fotos "
            "da clínica).",
            "Em **Categorias**, confira a categoria principal e acrescente as "
            "secundárias que a clínica realmente faz: Dentista, Ortodontista, "
            "Clínica odontológica, Odontopediatra.",
            "Em **Serviços**, escreva um por um: avaliação, aparelho fixo, "
            "aparelho estético, alinhador, manutenção de aparelho, documentação.",
            "Na **descrição**, diga em uma frase o que a clínica faz e em que "
            "bairro fica.",
        ],
        "nao_faca": "Não coloque palavra de busca no NOME da clínica no Google. "
                    "As regras do Google exigem o nome real, e perfil com nome "
                    "inflado é suspenso. Perder o perfil custa muito mais do que "
                    "qualquer busca que ele ganharia.",
        "como_saber": f"Daqui a 30 dias a gente refaz exatamente as mesmas "
                      f"{total_d} buscas. Hoje você aparece em {dentro_d} delas — "
                      f"é esse número que tem de subir.",
        "peso": 100 + (d.get("fora") or 0),
    }


def nomes_de_clinicas(praca):
    """Todo nome de clínica da praça, em pedaços.

    O detector de bairro estava devolvendo "Amor Saude", "Dntbras Buritizal",
    "Avaliacoes Sobre Naila Vivianne" — nomes de clínica e sobras do
    autocompletar. A varredura da praça já tem os nomes de TODAS as clínicas;
    é ela que separa o que é bairro do que é concorrente. O dado para
    consertar isso já estava na casa."""
    palavras = set()
    for f in ("categoria", "categoria_oportunidade"):
        for r in jsonl(f):
            if r.get("praca_id") != praca:
                continue
            for w in re.findall(r"[a-zà-úç]{3,}", sem_acento(r.get("nome"))):
                palavras.add(w)
    return palavras


def nomes_de_bairro(c, portas, praca=None):
    """Mostrar 'elkind, luzia, dumont' não ajuda ninguém.

    O bairro é 'Saul Elkind', 'Santa Luzia', 'Santos Dumont' — a palavra
    solta é pedaço de nome. Para o franqueado, o que serve é a busca inteira
    com o resto tirado: sobra o nome do bairro do jeito que a cidade escreve."""
    cidade = sem_acento(c["rotulo"].split("· ")[-1])
    corta = re.compile(r"\b(dentista|dentistas|ortodontista|aparelho|aparelhos|"
                       r"ortodontico|ortodontica|clinica|odontologica|odontologia|"
                       r"odonto|em|de|do|da|no|na|bairro|perto|mim|melhor|"
                       r"telefone|endereco|numero|whatsapp|contato|dr|dra|doutor|"
                       r"doutora|especializada|especializado|infantil|preco|valor|"
                       + r"|".join(re.escape(w) for w in cidade.split()) + r")\b")
    # Um nome de bairro tem cara de nome de lugar. "Edificio", "Center" e
    # "Alameda 503" não têm — são pedaço de endereço que o autocompletar colou.
    # Em Mafra os SEIS "bairros" que foram para o plano do franqueado eram
    # lixo, e o plano é o entregável mais lido do sistema. Um bairro inventado
    # queima a confiança mais rápido do que dez acertos a constroem.
    GENERICO = {"alameda", "avenida", "rua", "travessa", "rodovia", "estrada",
                "edificio", "edifício", "center", "centro comercial", "shopping",
                "galeria", "condominio", "condomínio", "predio", "prédio",
                "sala", "loja", "andar", "bloco", "quadra", "lote", "km",
                "clinica", "clínica", "consultorio", "consultório", "hospital",
                "posto", "unidade", "sc", "pr", "sp", "mg", "ba", "to", "ce",
                "ap", "ac", "ma", "pa", "pe"}

    def parece_bairro(nome):
        ws = [w for w in sem_acento(nome).split() if w]
        if not ws or any(any(c.isdigit() for c in w) for w in ws):
            return False           # "Alameda 503", "307 Norte"
        if len(ws) == 1 and ws[0] in GENERICO:
            return False           # "Center", "Edificio"
        if ws[0] in GENERICO and len(ws) < 3:
            return False           # "Alameda X", "Rua Y"
        if ws[-1] in GENERICO:
            return False           # "Fabiano Mafra Sc"
        return True

    # sobras do autocompletar que nunca são bairro
    LIXO = re.compile(r"\b(fotos?|avaliacoes?|avaliacao|sobre|telefone|preco|"
                      r"precos|valores|horario|whatsapp|contato|imagens?|"
                      r"encontrado|morto|reclame|aqui)\b")
    fora = []
    for d in portas:
        if not d.get("bairro_palavras"):
            continue
        resto = corta.sub(" ", sem_acento(d["frase"]))
        resto = re.sub(r"\s+", " ", resto).strip()
        if not resto or len(resto) <= 2:
            continue
        if LIXO.search(resto) or any(w in NAO_E_BAIRRO for w in resto.split()):
            continue
        if not parece_bairro(resto):
            continue
        # ⚠ Não dá para descartar pelo nome das clínicas: em Londrina a
        # clínica se chama "Odonto Excellence Gleba Palhano" e Gleba Palhano é
        # o bairro. Cortar por essa regra apagou TODOS os bairros de verdade
        # das treze praças. O que separa clínica de bairro é humano, e é por
        # isso que a lista sai como CANDIDATOS com pedido de conferência.
        fora.append(resto.title())
    # 'Leonor' e 'Jardim Leonor' são o mesmo bairro; fica o nome inteiro.
    unicos = sorted(set(fora), key=len, reverse=True)
    fica = []
    for x in unicos:
        if not any(sem_acento(x) in sem_acento(y) for y in fica):
            fica.append(x)
    return sorted(fica)


def tarefa_bairros(c, portas, praca):
    b = nomes_de_bairro(c, portas)
    # Menos de dois nomes confiáveis não sustenta a tarefa. Melhor a tarefa não
    # existir do que existir com um nome que o franqueado sabe que está errado.
    if len(b) < 2:
        return None
    return {
        "titulo": "A sua cidade procura dentista por bairro — e o seu bairro "
                  "não está escrito em lugar nenhum",
        "custo": "R$ 0", "tempo": "1 hora", "quem": "você ou quem cuida do site",
        "o_que_esta_acontecendo": [
            f"Quando alguém começa a digitar “dentista {c['rotulo'].split('· ')[-1].lower()}”, "
            f"o próprio Google completa com o nome de um bairro ou de um ponto "
            f"conhecido da cidade. Estes são os **{len(b)} candidatos** que a "
            f"busca devolveu: {lista(b, 8)}.",
            "Isso quer dizer que o paciente da sua cidade procura por perto de "
            "casa, não pela cidade inteira. Quem escreve o nome do bairro "
            "aparece; quem não escreve, não.",
            "**São candidatos, não uma lista pronta. Confira antes de usar — "
            "dois minutos.** A máquina pega o que o Google completa, e no meio "
            "vem nome de rua, de faculdade e até de clínica concorrente. Você "
            "conhece a sua cidade melhor que ela: risque os que não são bairro "
            "e fique com os que são.",
        ],
        "o_que_fazer": [
            "No perfil do Google, cite o bairro na descrição e nas publicações.",
            "No site, tenha uma página que diga o bairro e as referências de "
            "quem chega (a rua, o ponto conhecido do lado, onde estacionar).",
            "Se a clínica atende gente de mais de um bairro, cite os dois ou três "
            "de onde vem mais paciente — a recepção sabe quais são.",
        ],
        "como_saber": "Na próxima medição a gente testa a busca com o nome do "
                      "bairro e vê se a clínica passou a aparecer.",
        "peso": 60 + len(b),
    }


def tarefa_convenios(c):
    if not c["convenios"]:
        return None
    planos = []
    for x in c["convenios"]:
        for p in ("unimed", "bradesco", "amil", "sulamérica", "sulamerica", "odontoprev",
                  "metlife", "hapvida", "uniodonto", "interodonto", "porto seguro",
                  "servir"):
            if p in sem_acento(x):
                planos.append(p.capitalize())
    planos = sorted(set(planos))
    return {
        "titulo": "A cidade procura dentista por nome de convênio",
        "custo": "R$ 0", "tempo": "15 minutos", "quem": "você",
        "o_que_esta_acontecendo": [
            f"O Google completa a busca da sua cidade com nome de plano: "
            f"{lista(planos)}.",
            "**O dado público não diz quais a sua clínica aceita** — isso só "
            "você sabe. Mas diz que a cidade procura assim.",
        ],
        "o_que_fazer": [
            "Liste os convênios que a clínica aceita.",
            "Se aceita algum dos que a cidade procura, escreva no perfil do "
            "Google e no site. Aceitar e não dizer é perder paciente de graça.",
            "Se não aceita nenhum, isso também é informação: a conversa passa a "
            "ser sobre parcelamento, não sobre plano.",
        ],
        "como_saber": "Não é medição de posição: é a pergunta que a recepção "
                      "passa a ouvir menos, porque a resposta já está escrita.",
        "peso": 40 + len(planos),
    }


def tarefa_sem_dono(c):
    fracas = [x for x in c["sem_dono"] if x["mapa"]["quem"]]
    if not fracas:
        return None
    exemplos = []
    for x in fracas[:4]:
        t = x["mapa"]["quem"][0]
        exemplos.append(f"“{x['frase']}” — quem está em 1º tem {n(t.get('avaliacoes'))} "
                        f"avaliações")
    return {
        "titulo": "Tem busca importante onde o primeiro colocado é fraco",
        "custo": "R$ 0", "tempo": "junto com a primeira tarefa", "quem": "você",
        "o_que_esta_acontecendo": [
            f"Em **{len(fracas)} buscas** da sua cidade, quem está em primeiro "
            f"lugar tem menos de 300 avaliações.",
            *[f"· {e}" for e in exemplos],
            "Passar essas não é questão de verba. É questão de aparecer.",
        ],
        "o_que_fazer": [
            "Faça a primeira tarefa (categorias e serviços) — ela sozinha já "
            "coloca a clínica na disputa dessas buscas.",
            "Continue pedindo avaliação no balcão. É o que sustenta a posição "
            "depois que ela chega.",
        ],
        "como_saber": "São as buscas que mudam primeiro. Se alguma coisa vai "
                      "aparecer em 30 dias, é aqui.",
        "peso": 50 + len(fracas),
    }


def tarefa_palavras(c):
    if not c["servicos_citados"]:
        return None
    top = c["servicos_citados"][:4]
    return {
        "titulo": "O que o paciente da sua cidade diz que foi buscar",
        "custo": "R$ 0", "tempo": "meia hora, uma vez", "quem": "você e quem escreve",
        "o_que_esta_acontecendo": [
            f"Lemos **{n(c['avaliacoes_lidas'])} avaliações escritas por pacientes "
            f"das clínicas concorrentes** da sua cidade. Eles contam o que foram "
            f"fazer:",
            *[f"· {s['servico']} — {n(s['mencoes'])} menções" for s in top],
            "E as palavras que eles usam para elogiar são sempre as mesmas: "
            + lista([w for w, _ in c["vocabulario_da_praca"][:8]]) + ".",
            "**Ninguém elogia equipamento. Todo mundo elogia gente.** Anúncio e "
            "post que falam de tecnologia estão falando sozinhos.",
        ],
        "o_que_fazer": [
            "Escreva com as palavras que eles usam, não com as suas.",
            "Mostre pessoas: quem atende, quem recebe, o nome de cada um.",
            "Se dor e criança estão no topo, é por ali que o paciente entra — e "
            "o aparelho vem na conversa depois, não no anúncio.",
        ],
        "como_saber": "Não tem número de posição. O sinal é a avaliação nova "
                      "começar a repetir as mesmas palavras.",
        "peso": 30,
    }


def tarefa_ficha_dobrada(praca, ident):
    """A ficha repetida da PRÓPRIA clínica. Divide avaliação e nota ao meio."""
    nossos = {l.get("place_id") for l in ident.get("locais", [])
              if l.get("papel") == "proprio" and l.get("place_id")}
    ends = {sem_acento(l.get("endereco")).split(",")[0][:38]
            for l in ident.get("locais", []) if l.get("papel") == "proprio"
            and l.get("endereco")}
    suspeitas = []
    for r in ultimo(jsonl("categoria"), praca):
        if r.get("place_id") in nossos:
            continue
        nome = sem_acento(r.get("nome"))
        end = sem_acento(r.get("endereco")).split(",")[0][:38]
        if re.search(r"\borthodontic\b(?!s)", nome) or (end and end in ends):
            suspeitas.append({"nome": r.get("nome"), "avaliacoes": r.get("avaliacoes"),
                              "endereco": r.get("endereco")})
    if not suspeitas:
        return None
    return {
        "titulo": "Existe mais de um cadastro da sua clínica no Google",
        "custo": "R$ 0", "tempo": "15 minutos + a espera do Google", "quem": "você",
        "o_que_esta_acontecendo": [
            "Encontramos outro cadastro no mesmo endereço ou com o nome da marca:",
            *[f"· {s['nome']} — {n(s['avaliacoes']) if s['avaliacoes'] else 'nenhuma'} "
              f"avaliação" for s in suspeitas[:3]],
            "Cadastro repetido **divide a avaliação e a nota**. O paciente que "
            "avalia no perfil errado some do perfil certo.",
        ],
        "o_que_fazer": [
            "Entre no perfil do Google e peça a fusão dos cadastros duplicados.",
            "Se o cadastro extra não for seu, marque como duplicado mesmo assim — "
            "o Google avalia.",
        ],
        "como_saber": "Na próxima medição os dois viram um só, e a contagem de "
                      "avaliações soma em vez de dividir.",
        "peso": 90,
    }


def tarefa_anuncio(c):
    if not c["anuncios_ativos"]:
        return None
    return {
        "titulo": "Quem está anunciando na sua praça agora",
        "custo": "depende", "tempo": "—", "quem": "você e a agência",
        "o_que_esta_acontecendo": [
            f"**{c['anuncios_ativos']} anúncios ativos** de {lista(c['anunciantes_ativos'], 5)}.",
            "Anúncio é a última coisa da lista de propósito. As tarefas de cima "
            "custam zero e resolvem a maior parte. Verba de anúncio antes disso "
            "é pagar por um clique que o perfil daria de graça.",
        ],
        "o_que_fazer": [
            "Faça primeiro as tarefas grátis desta lista.",
            "Só depois, se quiser anunciar, comece pelas buscas onde o "
            "concorrente é forte e a intenção é de compra.",
        ],
        "como_saber": "A gente acompanha quem liga e quem desliga campanha, mês "
                      "a mês.",
        "peso": 10,
    }


# ──────────────────────────────── o plano ───────────────────────────────────

def presenca_da_loja(local_id):
    """Em quantas buscas ESTA loja aparece — não a cidade.

    O plano é a única peça que fala na segunda pessoa com o dono, e o
    dono é de UMA loja. Cuiabá tem três, que podem nem ser do mesmo
    dono, e o plano da cidade dizia a todas "a sua clínica aparece em N
    das M buscas" usando a conta somada. Para a loja Dom Bosco, que não
    aparece em NENHUMA das 151 buscas, essa frase era falsa.
    """
    a = PORTAL/"presenca_por_loja.json"
    if not a.exists():
        return None
    d = json.loads(a.read_text(encoding="utf-8"))
    return next((x for x in d.get("lojas", []) if x["local_id"] == local_id), None)


def monta(praca, local_id=None, unidade=None):
    caps = ultimo(jsonl("captacao"), praca)
    if not caps:
        return None
    c = caps[-1]
    ident = json.loads((IDENT/f"{praca}.json").read_text(encoding="utf-8"))

    ufs = ident.get("uf") or []
    portas = [d for d in ultimo(jsonl("portas"), praca)
              if d.get("intencao") != "RUÍDO"
              and frase_util(d["frase"], ufs, ident.get("cidades"))]
    tarefas = [t for t in (tarefa_dentista(c), tarefa_ficha_dobrada(praca, ident),
                           tarefa_bairros(c, portas, praca), tarefa_sem_dono(c),
                           tarefa_convenios(c), tarefa_palavras(c),
                           tarefa_anuncio(c)) if t]
    tarefas.sort(key=lambda t: -t["peso"])
    tarefas = tarefas[:5]        # com dez, ninguém faz nenhuma

    pres = presenca_da_loja(local_id) if local_id else None
    if pres:
        total, dentro = pres["de"], pres["aparece_em"]
        placar = {"aparece_em": dentro, "de": total, "pct": pres["pct"],
                  "melhor_posicao": pres.get("melhor_posicao"),
                  "invisivel": pres["invisivel"],
                  "e_desta_loja": True}
        frase = (f"A sua clínica **não aparece em nenhuma** das "
                 f"{total} buscas que testamos na cidade."
                 if pres["invisivel"] else
                 f"A sua clínica aparece em **{dentro} das {total} buscas** "
                 f"que testamos na cidade.")
    else:
        total = c["portas_medidas"]
        dentro = len(c["dentro"])
        placar = {"aparece_em": dentro, "de": total,
                  "pct": round(100*dentro/total) if total else None,
                  "e_desta_loja": False}
        frase = (f"A rede aparece em **{dentro} das {total} buscas** "
                 f"que testamos na cidade.")
    return {
        "praca_id": praca, "rotulo": c["rotulo"],
        "local_id": local_id, "unidade": unidade,
        "snapshot_date": c["snapshot_date"],
        "placar": placar,
        "frase_do_topo": frase,
        # o que vale para a loja e o que vale para a cidade inteira
        "o_que_e_da_loja": ["o placar de presença", "a ficha do Google",
                            "as avaliações e as respostas"],
        "o_que_e_da_cidade": ["os bairros que a cidade escreve",
                              "os convênios citados", "as palavras da praça",
                              "quem anuncia aparelho"],
        "gratis": sum(1 for t in tarefas if t["custo"] == "R$ 0"),
        "tarefas": tarefas,
        "ressalvas": [
            "Medimos o MAPA do Google — aquela lista de lugares que aparece com "
            "as estrelinhas. Não é a mesma coisa que o resultado de baixo nem "
            "que o anúncio pago.",
            "As buscas saem do que o próprio Google completa quando alguém "
            "digita. Não sabemos quantas pessoas por mês procuram cada uma.",
            "As palavras do paciente vêm de quem avaliou. Quem procurou e "
            "desistiu não escreve avaliação.",
        ],
    }


def imprime(p):
    print(f"\n{'='*78}\n  O SEU PLANO · {p['rotulo']}"
          f"{' · ' + p['unidade'] if p.get('unidade') else ''}\n{'='*78}")
    pl = p["placar"]
    linhas = ([f"A sua clínica NÃO APARECE em nenhuma das {pl['de']} buscas",
               "que testamos na cidade."]
              if pl.get("invisivel") else
              [f"A sua clínica aparece em {pl['aparece_em']} das {pl['de']} buscas",
               f"que testamos na cidade.  ({pl['pct']}%)"])
    largura = 70
    print(f"\n  ┌{'─'*largura}┐")
    for l in linhas:
        print(f"  │  {l.ljust(largura-3)}│")
    print(f"  └{'─'*largura}┘")
    print(f"\n  {len(p['tarefas'])} tarefas · {p['gratis']} delas custam R$ 0")

    for i, t in enumerate(p["tarefas"], 1):
        print(f"\n{'─'*78}\n  {i}. {t['titulo'].upper()}")
        print(f"     {t['custo']} · {t['tempo']} · {t['quem']}\n")
        for l in t["o_que_esta_acontecendo"]:
            if not l:
                continue
            texto = limpo(l)
            print(textwrap.fill(texto, 72, initial_indent="     ",
                                subsequent_indent="     " if not l.startswith("·") else "       "))
        print("\n     O QUE FAZER:")
        for j, l in enumerate(t["o_que_fazer"], 1):
            print(textwrap.fill(f"{j}. {limpo(l)}", 72, initial_indent="       ",
                                subsequent_indent="          "))
        if t.get("nao_faca"):
            print()
            print(textwrap.fill("NÃO FAÇA: " + limpo(t["nao_faca"]), 72,
                                initial_indent="     ⚠ ", subsequent_indent="       "))
        print()
        print(textwrap.fill("COMO SABER QUE FUNCIONOU: " + limpo(t["como_saber"]), 72,
                            initial_indent="     ", subsequent_indent="     "))

    print(f"\n{'─'*78}\n  O QUE ESTA MEDIÇÃO NÃO ENXERGA")
    for r in p["ressalvas"]:
        print(textwrap.fill("· " + limpo(r), 72, initial_indent="     ",
                            subsequent_indent="       "))
    print()


def markdown(p):
    pl = p["placar"]
    L = [f"# O seu plano — {p['rotulo']}", "",
         f"**{dt.date.fromisoformat(p['snapshot_date']).strftime('%d/%m/%Y')}**", "",
         f"> ## A sua clínica aparece em {pl['aparece_em']} das {pl['de']} buscas "
         f"que testamos na sua cidade.", "",
         f"São **{len(p['tarefas'])} tarefas**, e **{p['gratis']} delas custam R$ 0**. "
         f"A ordem é de propósito: o que é grátis vem antes do que custa.", "", "---", ""]
    for i, t in enumerate(p["tarefas"], 1):
        L += [f"## {i}. {t['titulo']}", "",
              f"`{t['custo']}` · `{t['tempo']}` · `{t['quem']}`", ""]
        for l in t["o_que_esta_acontecendo"]:
            if l:
                L += [l, ""]
        L += ["**O que fazer:**", ""]
        L += [f"{j}. {x}" for j, x in enumerate(t["o_que_fazer"], 1)]
        L.append("")
        if t.get("nao_faca"):
            L += [f"> ⚠ **Não faça:** {t['nao_faca']}", ""]
        L += [f"**Como saber que funcionou:** {t['como_saber']}", "", "---", ""]
    L += ["## O que esta medição não enxerga", ""]
    L += [f"- {r}" for r in p["ressalvas"]]
    L += ["", f"_Medido em {dt.date.fromisoformat(p['snapshot_date']).strftime('%d/%m/%Y')}. "
              f"A próxima medição repete exatamente as mesmas buscas._", ""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--praca", action="append", default=[])
    ap.add_argument("--todas", action="store_true")
    ap.add_argument("--salvar", action="store_true")
    ap.add_argument("--md", action="store_true", help="escreve o plano em markdown")
    a = ap.parse_args()

    pracas = list(a.praca) or (sorted(p.stem for p in IDENT.glob("*.json"))
                               if a.todas else [])
    if not pracas:
        sys.exit("use --praca <id> ou --todas")

    # --todas rodava na pasta de identidade inteira, e lá dentro estão também
    # as seis praças de OPORTUNIDADE — cidades onde a rede NÃO tem unidade.
    # Saíram seis planos escritos na segunda pessoa ("a SUA clínica aparece em
    # 0 das 20 buscas", "abra o SEU perfil do Google") para um franqueado que
    # não existe. O estudo daquelas cidades é outro arquivo, em
    # dados/portal/oportunidade/, e continua valendo: lá a pergunta é se vale
    # abrir, não o que o dono deve fazer na semana.
    def tem_dono(praca):
        p = IDENT/f"{praca}.json"
        return not (json.loads(p.read_text(encoding="utf-8")).get("sem_unidade")
                    if p.exists() else False)

    sem_dono = [p for p in pracas if not tem_dono(p)]
    if sem_dono and not a.praca:
        print(f"  pulando {len(sem_dono)} praça(s) sem unidade — plano de "
              f"franqueado precisa de franqueado: {', '.join(sem_dono)}")
        pracas = [p for p in pracas if tem_dono(p)]

    # UM PLANO POR LOJA. Eram sete planos para dez lojas: as três de Cuiabá
    # liam o mesmo texto, e as duas de Londrina também — donos possivelmente
    # diferentes recebendo a conta somada do vizinho como se fosse a sua.
    for praca in pracas:
        ident = json.loads((IDENT/f"{praca}.json").read_text(encoding="utf-8"))
        lojas = [l for l in ident.get("locais", []) if l.get("papel") == "proprio"]
        if not lojas:
            print(f"  {praca}: sem unidade própria na identidade")
            continue
        for l in lojas:
            p = monta(praca, l["local_id"], l.get("nome"))
            if not p:
                print(f"  {praca}: sem captação coletada — rode "
                      f"`python3 scripts/oportunidades_franqueado.py "
                      f"--praca {praca} --salvar`")
                break
            imprime(p)
            if a.salvar:
                PLANOS.mkdir(parents=True, exist_ok=True)
                (PLANOS/f"{l['local_id']}.json").write_text(
                    json.dumps(p, ensure_ascii=False, indent=2)+"\n",
                    encoding="utf-8")
                print(f"  → dados/planos/{l['local_id']}.json")
            if a.md:
                PLANOS.mkdir(parents=True, exist_ok=True)
                (PLANOS/f"{l['local_id']}.md").write_text(markdown(p),
                                                          encoding="utf-8")
                print(f"  → dados/planos/{l['local_id']}.md")


if __name__ == "__main__":
    main()
