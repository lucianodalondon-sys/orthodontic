#!/usr/bin/env python3
"""
jornada_do_paciente.py — em QUE MOMENTO da jornada a unidade dói.

O buraco que este script fecha: havia 26.332 avaliações classificadas por
TEMA — atendimento, preço, resultado — e tema não diz onde agir. "17.358
falam de atendimento" é verdade e é inútil: atendimento na recepção,
atendimento na cadeira e atendimento no telefone são três problemas
diferentes, de três donos diferentes.

A jornada responde outra pergunta: **o problema público desta unidade é
clínico ou é de balcão?** Porque a resposta muda quem resolve.

    DESCOBERTA → CONTATO → AGENDAMENTO → RECEPÇÃO → AVALIAÇÃO →
    CONTRATAÇÃO → CLÍNICO → MANUTENÇÃO → COBRANÇA → SUPORTE → CONTENÇÃO

REGRAS QUE ESTE SCRIPT SEGUE

· É POR LOJA. A jornada de uma loja não é a média da cidade.
· A avaliação pode tocar VÁRIOS estágios — quem elogia o dentista e
  reclama da recepção conta nos dois. Por isso a soma passa de 100%.
· Estágio sem nenhuma avaliação é AUSÊNCIA DE MEDIÇÃO, não zero
  problema: sai com `medido: false` e a tela escreve isso.
· O sentimento vem da NOTA, que é medida — não de análise de texto, que
  seria inferência com cara de fato. Nota ≤ 2 é dor, ≥ 4 é elogio, 3
  fica fora dos dois.
· Amostra pequena não vira manchete: abaixo de `MIN_PARA_FALAR` o
  estágio é publicado com `amostra_curta: true`.

Uso:
    python3 scripts/jornada_do_paciente.py                # todas as lojas
    python3 scripts/jornada_do_paciente.py --salvar
    python3 scripts/jornada_do_paciente.py --loja ortho_mafra
"""
import argparse, json, pathlib, re, sys, unicodedata
import datetime as dt
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from cruzamento import reviews_unicos, identidades, conta

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SAIDA = RAIZ/"dados"/"portal"/"jornada.json"

MIN_PARA_FALAR = 8          # avaliações num estágio para ele virar frase
MIN_DOR = 5                 # avaliações de 1-2 estrelas para virar manchete
MIN_PCT_DOR = 15            # e a dor precisa pesar no estágio, não só existir

# A ORDEM IMPORTA: é a ordem em que o paciente vive, e é assim que a tela
# desenha. Cada estágio traz o rótulo de balcão e quem costuma resolver.
JORNADA = [
    ("descoberta",   "Descoberta",   "como me acharam",
     "marketing e ficha do Google"),
    ("contato",      "Contato",      "telefone e WhatsApp",
     "recepção"),
    ("agendamento",  "Agendamento",  "marcar e remarcar",
     "recepção"),
    ("recepcao",     "Recepção",     "chegar e esperar",
     "recepção"),
    ("avaliacao",    "Avaliação",    "a primeira consulta",
     "clínica"),
    ("contratacao",  "Contratação",  "preço, contrato e entrada",
     "franqueado"),
    ("clinico",      "Atendimento clínico", "a cadeira",
     "clínica"),
    ("manutencao",   "Manutenção",   "as voltas de cada mês",
     "clínica"),
    ("cobranca",     "Cobrança",     "mensalidade e multa",
     "franqueado"),
    ("suporte",      "Suporte",      "quando algo dá errado",
     "franqueado"),
    ("contencao",    "Fim e contenção", "alta e depois dela",
     "clínica"),
]

# O LÉXICO É DE BALCÃO, NÃO DE MANUAL. Estas são as palavras que o
# paciente escreve — "descolou o bracket", "fila", "não atendem o
# telefone" — não os termos que a rede usaria internamente.
PALAVRAS = {
    "descoberta": [
        r"\bindic(ou|ação|aram|ada)\b", r"\brecomend", r"\bachei no google\b",
        r"\bencontrei\b", r"\bvi (no|na) (instagram|face|google|internet)\b",
        r"\bpesquis(ei|ando)\b", r"\bpassei na frente\b", r"\banúncio\b",
    ],
    "contato": [
        r"\btelefone\b", r"\bwhats", r"\bliguei\b", r"\bligação\b",
        r"\bnão atende(m|ram)?\b", r"\bnunca atende", r"\bretorn(o|ar|aram)\b",
        r"\bmensagem\b", r"\bresponder(am)?\b", r"\bcontato\b",
    ],
    "agendamento": [
        r"\bagend", r"\bmarcar\b", r"\bmarque(i)?\b", r"\bremarc",
        r"\bhorário\b", r"\bdesmarc", r"\bencaixe\b", r"\bcancel(ou|aram|ei)\b",
        r"\bconsegui (uma )?(vaga|horário)\b",
    ],
    "recepcao": [
        r"\brecep(ção|cionista)", r"\batendente\b", r"\bsecretár",
        r"\bespera\b", r"\besperei\b", r"\bfila\b", r"\batraso\b",
        r"\batrasad", r"\bpontual", r"\bsala de espera\b", r"\bacolhi",
    ],
    "avaliacao": [
        r"\bprimeira (consulta|vez|visita)\b", r"\bavalia(ção|ções)\b",
        r"\bconsulta inicial\b", r"\borçamento\b", r"\bexplic(ou|aram|ação)\b",
        r"\bplano de tratamento\b", r"\bdocumentação\b", r"\braio.?x\b",
    ],
    "contratacao": [
        r"\bpreço\b", r"\bvalor(es)?\b", r"\bcaro\b", r"\bbarato\b",
        r"\bcontrato\b", r"\bentrada\b", r"\bparcel", r"\bfinanciamento\b",
        r"\bcusto.?benefício\b", r"\bpromoção\b", r"\bdesconto\b",
    ],
    "clinico": [
        r"\bdentista\b", r"\bdoutor|dra?\.\b", r"\bortodontista\b",
        r"\bprofissional\b", r"\bcadeira\b", r"\bproced", r"\bextra(ção|iu)\b",
        r"\bdor\b", r"\bdoeu\b", r"\bmachuc", r"\bcuidados", r"\bdelicad",
        r"\bhabilidoso\b", r"\bmão leve\b",
    ],
    "manutencao": [
        r"\bmanutenção\b", r"\bmensal", r"\bapertar\b", r"\btroca(r)? (a )?borrach",
        r"\bajuste\b", r"\bvolta(r)? (todo )?mês\b", r"\bretorno\b",
        r"\bacompanhamento\b", r"\bmanuten",
    ],
    "cobranca": [
        r"\bcobran", r"\bcobrar(am)?\b", r"\bmensalidade\b", r"\bmulta\b",
        r"\bboleto\b", r"\batrasei\b", r"\bpagamento\b", r"\bpaguei\b",
        r"\bdívida\b", r"\bnegativ(ado|aram)\b", r"\bestorno\b",
    ],
    "suporte": [
        r"\bdescol(ou|ei)\b", r"\bcaiu o (bracket|aparelho|braquete)\b",
        r"\bquebr(ou|ei)\b", r"\bmachucando\b", r"\bfio\b", r"\burgência\b",
        r"\bemergência\b", r"\bencaixe de urgência\b", r"\breclam",
        r"\bproblema\b", r"\bresolver(am)?\b",
    ],
    "contencao": [
        r"\bcontenção\b", r"\bretirad(a|o) do aparelho\b", r"\btirei o aparelho\b",
        r"\balta\b", r"\bfinaliz", r"\bterminei o tratamento\b",
        r"\bfim do tratamento\b", r"\bplaquinha\b",
    ],
}
def _sa(t):
    return "".join(c for c in unicodedata.normalize("NFD", t or "")
                   if unicodedata.category(c) != "Mn")


# O PADRÃO PERDE O ACENTO JUNTO COM O TEXTO. Compilar "recepção" e depois
# procurar em texto normalizado ("recepcao") não casa nunca — foi assim
# que metade dos estágios ficou invisível na primeira rodada.
REGEX = {k: [re.compile(_sa(p), re.I) for p in v] for k, v in PALAVRAS.items()}


sem_acento = _sa


def estagios_de(texto):
    """Todos os estágios que a avaliação toca. Pode ser nenhum."""
    if not texto:
        return []
    t = sem_acento(texto).lower()
    fora = []
    for chave, _, _, _ in JORNADA:
        for rx in REGEX[chave]:
            if rx.search(t):
                fora.append(chave)
                break
    return fora


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--loja")
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()

    ident = identidades()
    nossas, rotulo_de = {}, {}
    for pid, praca in ident.items():
        for l in praca.get("locais", []):
            if l.get("papel") == "proprio":
                nossas[l["local_id"]] = l
                # três lojas não têm `unidade` na identidade e cairiam na
                # tela como "OrthoDontic", indistinguíveis entre si
                rotulo_de[l["local_id"]] = (
                    praca.get("rotulo") or praca.get("nome") or pid)

    # por loja: estágio → {dor, elogio, neutro, exemplos}
    por_loja = defaultdict(lambda: defaultdict(
        lambda: {"dor": 0, "elogio": 0, "neutro": 0, "exemplos": []}))
    total_por_loja = defaultdict(int)
    sem_estagio = defaultdict(int)

    for r in reviews_unicos():
        lid = r.get("local_id")
        if a.loja and lid != a.loja:
            continue
        texto = (r.get("texto") or "").strip()
        if not texto:
            continue
        total_por_loja[lid] += 1
        est = estagios_de(texto)
        if not est:
            sem_estagio[lid] += 1
            continue
        # a nota vem como texto em parte da série (coletor antigo) e como
        # número no resto — comparar sem converter estoura
        try:
            nota = float(r.get("nota"))
        except (TypeError, ValueError):
            nota = None
        # O SENTIMENTO SAI DA NOTA, que é medida. Ler sentimento do texto
        # seria inferência publicada como fato.
        caixa = ("neutro" if nota is None
                 else "dor" if nota <= 2
                 else "elogio" if nota >= 4 else "neutro")
        for e in est:
            b = por_loja[lid][e]
            b[caixa] += 1
            if caixa == "dor" and len(b["exemplos"]) < 3 and len(texto) < 400:
                b["exemplos"].append({"nota": int(nota) if nota else None, "data": (r.get("data") or "")[:10],
                                      "texto": texto})

    lojas = []
    for lid, estagios in sorted(por_loja.items()):
        if lid not in nossas and not a.loja:
            continue            # a jornada publicada é das NOSSAS lojas
        linhas = []
        for chave, rotulo, oquee, dono in JORNADA:
            b = estagios.get(chave)
            n = (b["dor"] + b["elogio"] + b["neutro"]) if b else 0
            linhas.append({
                "estagio": chave, "rotulo": rotulo, "o_que_e": oquee,
                "quem_resolve": dono,
                "medido": n > 0,
                "avaliacoes": n,
                "dor": b["dor"] if b else 0,
                "elogio": b["elogio"] if b else 0,
                "pct_dor": round(100*b["dor"]/n) if n else None,
                "amostra_curta": 0 < n < MIN_PARA_FALAR,
                "exemplos": (b["exemplos"] if b else []),
                # a frase sai pronta: o casco não monta plural, e o portal
                # já escreveu "1 avaliações" na primeira tela da vida dele
                "frase": (
                    conta(n, "avaliação fala", "avaliações falam")
                    + " deste momento"
                    + (f", {conta(b['dor'], 'com nota baixa', 'com notas baixas')}"
                       if b and b["dor"] else ", nenhuma com nota baixa")
                    if n else None),
                "porque_vazio": (None if n else
                                 "nenhuma avaliação desta loja fala deste "
                                 "momento — é ausência de medição, não "
                                 "ausência de problema"),
            })
        # a manchete é o estágio com mais DOR e amostra suficiente
        # DUAS LINHAS RUINS NÃO SÃO A DOR DA UNIDADE. A primeira versão
        # elegeu "descoberta" como problema de Cuiabá Centro Norte com 2
        # avaliações em 52 — 4%. Manchete exige volume E peso.
        candidatos = [l for l in linhas
                      if l["dor"] >= MIN_DOR
                      and (l["pct_dor"] or 0) >= MIN_PCT_DOR
                      and not l["amostra_curta"]]
        pior = max(candidatos, key=lambda l: l["dor"], default=None)
        lojas.append({
            "local_id": lid,
            "unidade": (nossas.get(lid) or {}).get("unidade")
                       or (nossas.get(lid) or {}).get("nome") or lid,
            "rotulo": rotulo_de.get(lid),
            "com_texto": total_por_loja[lid],
            "sem_estagio": sem_estagio.get(lid, 0),
            "porque_sem_estagio": ("avaliações curtas do tipo 'ótimo' e "
                                   "'recomendo', que não dizem em que "
                                   "momento a pessoa estava"),
            "estagios": linhas,
            "manchete": (
                f"A dor pública desta unidade aparece em {pior['rotulo'].lower()} "
                f"— {conta(pior['dor'], 'avaliação de 1 ou 2 estrelas', 'avaliações de 1 ou 2 estrelas')} "
                f"de {conta(pior['avaliacoes'], 'que fala', 'que falam')} desse momento."
                if pior else
                "Nenhum momento da jornada concentra dor com amostra "
                "suficiente para virar manchete."),
            "quem_resolve": pior["quem_resolve"] if pior else None,
            "e_clinico": (pior["estagio"] in ("clinico", "avaliacao",
                                              "manutencao", "contencao")
                          if pior else None),
        })

    print(f"  {conta(len(lojas), 'loja')} com jornada montada")
    for l in lojas:
        print(f"\n  {(l.get('rotulo') or '')} · {l['unidade'][:40]}")
        print(f"    {l['manchete']}")
        vivos = [e for e in l["estagios"] if e["medido"]]
        print(f"    {conta(len(vivos), 'estágio medido', 'estágios medidos')} "
              f"de {len(JORNADA)} · {l['com_texto']} avaliações com texto "
              f"· {l['sem_estagio']} sem momento identificável")

    if not a.salvar:
        print("\n  (--salvar para gravar)")
        return
    SAIDA.write_text(json.dumps({
        "o_que_e": "Em que momento da jornada cada unidade dói, lido nas "
                   "avaliações públicas do Google.",
        "o_que_nao_e": "Não é análise de sentimento do texto: a dor sai da "
                       "NOTA, que é medida. O texto só diz de que momento a "
                       "pessoa estava falando.",
        "medido_em": dt.date.today().isoformat(),
        "estagios": [{"estagio": c, "rotulo": r, "o_que_e": o,
                      "quem_resolve": d} for c, r, o, d in JORNADA],
        "minimo_para_falar": MIN_PARA_FALAR,
        "lojas": lojas,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n  → {SAIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
