#!/usr/bin/env python3
"""
a_oferta_do_rival.py — QUAL É A GUERRA COMERCIAL DESTA CIDADE.

O buraco que este script fecha: o portal contava anunciantes. "10
anunciantes, 45 anúncios" não muda decisão nenhuma — o franqueado não faz
nada diferente sabendo disso. O que muda decisão é **o que eles estão
vendendo**: se a cidade inteira grita preço, entrar com preço é entrar na
briga mais cara que existe; se ninguém fala de adulto, há posição vaga.

O texto dos anúncios já estava no disco desde a primeira coleta — 614 dos
735 têm criativo — e nunca tinha sido lido.

O QUE ESTE SCRIPT NÃO FAZ

· Não mede investimento. A Biblioteca do Meta não publica verba, e
  quantidade de anúncio não é dinheiro gasto. Quem disser isso está
  inventando.
· Não fala de quem não disputa aparelho. A régua do produto vale aqui
  igual: universidade que faz limpeza e advogado tributarista saem, e
  saem CONTADOS, com o motivo.
· Não infere estratégia. Diz o que o anúncio ESCREVE. "Sem entrada"
  aparece porque a palavra está lá, não porque alguém deduziu.

Uso:
    python3 scripts/a_oferta_do_rival.py
    python3 scripts/a_oferta_do_rival.py --salvar
"""
import argparse, json, pathlib, re, sys, unicodedata
import datetime as dt
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from cruzamento import identidades, conta

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SERIE = RAIZ/"dados"/"serie"/"anuncios.jsonl"
SAIDA = RAIZ/"dados"/"portal"/"oferta.json"

MIN_PARA_TESE = 4       # anúncios de aparelho na cidade para arriscar a tese


def sa(t):
    return "".join(c for c in unicodedata.normalize("NFD", str(t or ""))
                   if unicodedata.category(c) != "Mn").lower()


# ODONTOLOGIA NÃO É ORTODONTIA — a mesma régua do resto do projeto.
E_APARELHO = re.compile(
    sa(r"aparelho|ortodont|braquete|bracket|alinhador|invisalign|"
       r"contencao|aparelho fixo|autoligado"), re.I)

# CADA EIXO É UMA PERGUNTA DE NEGÓCIO, não uma etiqueta bonita.
EIXOS = [
    # (chave, rótulo de tela, o que a presença dele significa, padrões)
    ("preco", "Preço na frente",
     "a cidade disputa por número; entrar aqui é entrar na briga mais cara",
     [r"\br\$\s?\d", r"\ba partir de\b", r"\bpor apenas\b", r"\bpreco\b",
      r"\bvalor promocional\b", r"\bmais barato\b"]),
    ("sem_entrada", "Sem entrada",
     "tira a barreira do primeiro pagamento — ataca quem não tem reserva",
     [r"\bsem entrada\b", r"\bentrada gratis\b", r"\bzero de entrada\b",
      r"\bsem taxa de instalacao\b"]),
    ("parcelamento", "Parcelamento",
     "vende a mensalidade, não o tratamento",
     [r"\bparcel", r"\b\d+x\b", r"\bmensalidade\b", r"\bno cartao\b",
      r"\bsuave\b", r"\bcabe no bolso\b"]),
    ("avaliacao_gratis", "Avaliação grátis",
     "compra a visita, não a venda — é isca de agenda",
     [r"\bavaliacao (gratis|gratuita|sem custo)\b", r"\bconsulta gratis\b",
      r"\bagende sua avaliacao\b", r"\bprimeira consulta gratis\b"]),
    ("alinhador", "Alinhador invisível",
     "produto de ticket alto e público adulto",
     [r"\balinhador", r"\binvisalign\b", r"\baparelho invisivel\b",
      r"\btransparente\b"]),
    ("estetico", "Aparelho estético",
     "vende discrição — público que trabalha de frente",
     [r"\bestetico\b", r"\bporcelana\b", r"\bsafira\b", r"\bdiscreto\b"]),
    ("publico_adulto", "Falado para adulto",
     "disputa o adulto que adiou o tratamento",
     [r"\badulto", r"\bnunca e tarde\b", r"\bdepois dos \d+\b",
      r"\bna sua idade\b"]),
    ("publico_infantil", "Falado para criança e adolescente",
     "disputa a decisão da mãe, não a do paciente",
     [r"\binfantil\b", r"\bcrianca", r"\bseu filho\b", r"\bsua filha\b",
      r"\badolescent", r"\bodontopediatr"]),
    ("urgencia", "Urgência e escassez",
     "empurra a decisão para hoje — sinal de campanha de rajada",
     [r"\bultim(as|os) (vagas|dias)\b", r"\bso ate\b", r"\bcorra\b",
      r"\bvagas limitadas\b", r"\bpromocao termina\b",
      r"\bpor tempo limitado\b", r"\bnao perca\b"]),
    # "agora" e "hoje" ficaram de fora de propósito: "agende agora" é o CTA mais
    # banal que existe e inflou urgência para 80% em Londrina — virou
    # manchete de uma guerra comercial que não estava acontecendo.
    ("prova_social", "Prova social",
     "vende confiança em vez de preço",
     [r"\bdepoiment", r"\bantes e depois\b", r"\bmais de \d+ (pacientes|sorrisos)\b",
      r"\bavaliacao 5 estrelas\b", r"\bquem ja fez\b"]),
    ("autoridade", "Autoridade técnica",
     "vende o profissional — difícil de copiar, caro de construir",
     [r"\bespecialista\b", r"\bcro\b", r"\bmestre\b", r"\bdoutor",
      r"\banos de experiencia\b", r"\bclinica referencia\b"]),
    ("rapidez", "Rapidez do resultado",
     "vende tempo, e tempo é a objeção número um do aparelho",
     [r"\bem \d+ meses\b", r"\brapido\b", r"\bmais rapido\b",
      r"\bresultado em\b", r"\bmenos tempo\b"]),
]
RX = {c: [re.compile(sa(p), re.I) for p in ps] for c, _, _, ps in EIXOS}


def eixos_de(texto):
    t = sa(texto)
    return [c for c, _, _, _ in EIXOS if any(r.search(t) for r in RX[c])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()

    linhas = [json.loads(l) for l in SERIE.read_text(encoding="utf-8").split("\n")
              if l.strip()]
    # a ponta de cada anúncio, para não contar o mesmo três vezes
    ult = {}
    for r in sorted(linhas, key=lambda r: r.get("snapshot_date", "")):
        ult[(r.get("praca_id"), r.get("ad_id"))] = r
    anuncios = list(ult.values())

    # `identidades()` só devolve praça da rede; as seis do Radar têm
    # identidade igual e ficavam na tela como "maraba", em minúscula
    ident = dict(identidades())
    for arq in sorted((RAIZ/"dados"/"identidade").glob("*.json")):
        ident.setdefault(arq.stem, json.loads(arq.read_text(encoding="utf-8")))
    por_praca = defaultdict(lambda: {"aparelho": [], "fora": 0,
                                     "sem_texto": 0, "anunciantes": set()})
    for r in anuncios:
        praca = r.get("praca_id")
        texto = (r.get("texto") or "").strip()
        b = por_praca[praca]
        if not texto:
            b["sem_texto"] += 1
            continue
        if not E_APARELHO.search(sa(texto)):
            b["fora"] += 1
            continue
        b["aparelho"].append(r)
        b["anunciantes"].add(r.get("anunciante"))

    fora = []
    for praca, b in sorted(por_praca.items()):
        n = len(b["aparelho"])
        contagem = {c: 0 for c, _, _, _ in EIXOS}
        por_anunciante = defaultdict(lambda: defaultdict(int))
        for r in b["aparelho"]:
            for e in eixos_de(r.get("texto")):
                contagem[e] += 1
                por_anunciante[r.get("anunciante")][e] += 1

        eixos = []
        for c, rotulo, significa, _ in EIXOS:
            q = contagem[c]
            eixos.append({
                "eixo": c, "rotulo": rotulo, "o_que_significa": significa,
                "anuncios": q,
                "pct": round(100*q/n) if n else None,
                "frase": (conta(q, "anúncio de aparelho fala",
                                "anúncios de aparelho falam") + " disso"
                          if q else "nenhum anúncio de aparelho fala disso"),
            })
        eixos.sort(key=lambda e: -e["anuncios"])
        topo = [e for e in eixos if e["anuncios"] > 0][:3]
        vazios = [e for e in eixos if e["anuncios"] == 0]

        # A TESE SÓ SAI COM AMOSTRA. Com dois anúncios não há guerra
        # comercial nenhuma para descrever.
        if n >= MIN_PARA_TESE and topo:
            tese = ("A disputa desta cidade é por "
                    + topo[0]["rotulo"].lower()
                    + f" — {topo[0]['anuncios']} dos "
                    + conta(n, "anúncio de aparelho medido",
                            "anúncios de aparelho medidos") + " falam disso"
                    + (f", seguido de {topo[1]['rotulo'].lower()}"
                       if len(topo) > 1 else "") + ".")
            vaga = (f"Ninguém está falando de {vazios[0]['rotulo'].lower()}"
                    f" — {vazios[0]['o_que_significa']}." if vazios else None)
        else:
            tese = (f"Ainda não dá para descrever a disputa desta cidade: "
                    f"só {conta(n, 'anúncio de aparelho', 'anúncios de aparelho')} "
                    f"com texto medido.")
            vaga = None

        fora.append({
            "praca_id": praca,
            "rotulo": (ident.get(praca) or {}).get("rotulo") or praca,
            "anuncios_de_aparelho": n,
            "anunciantes": len(b["anunciantes"]),
            "fora_do_produto": b["fora"],
            "porque_fora": ("falam de implante, clareamento, lente, harmonização "
                            "— e um advogado tributarista. Outro tratamento, "
                            "outro ticket, outra decisão."),
            "sem_texto": b["sem_texto"],
            "amostra_curta": n < MIN_PARA_TESE,
            "tese": tese,
            "posicao_vaga": vaga,
            "eixos": eixos,
            "por_anunciante": [
                {"anunciante": k,
                 "eixos": sorted([e for e, q in v.items() if q],
                                 key=lambda e: -v[e])[:3]}
                for k, v in sorted(por_anunciante.items(),
                                   key=lambda kv: -sum(kv[1].values()))[:8]],
        })

    fora.sort(key=lambda x: -x["anuncios_de_aparelho"])
    for x in fora:
        print(f"\n  {x['rotulo']}")
        print(f"    {x['tese']}")
        if x["posicao_vaga"]:
            print(f"    {x['posicao_vaga']}")
        print(f"    {x['anuncios_de_aparelho']} de aparelho · "
              f"{x['fora_do_produto']} fora do produto · "
              f"{x['sem_texto']} sem texto")

    if not a.salvar:
        print("\n  (--salvar para gravar)")
        return
    SAIDA.write_text(json.dumps({
        "o_que_e": "O que os anúncios de aparelho de cada cidade estão "
                   "vendendo, lido no texto do próprio anúncio.",
        "o_que_nao_e": "Não é investimento. A Biblioteca do Meta não publica "
                       "verba, e quantidade de anúncio não é dinheiro gasto.",
        "medido_em": dt.date.today().isoformat(),
        "minimo_para_tese": MIN_PARA_TESE,
        "eixos": [{"eixo": c, "rotulo": r, "o_que_significa": s}
                  for c, r, s, _ in EIXOS],
        "pracas": fora,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n  → {SAIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
