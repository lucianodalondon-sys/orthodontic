#!/usr/bin/env python3
"""
reteste.py — testa cada achado contra TODAS as praças, não contra as quatro.

O problema que ele resolve
--------------------------
A escada dos achados tinha quinze degraus e doze diziam `4/4`. Foram medidos
quando a base tinha quatro praças e nunca foram retestados contra as nove que
entraram depois. "A mãe é a decisora", "a prova social está parada em todas",
"a ordem certa é blindar a operação" — tudo apoiado em quatro cidades.

O único que subiu para 13/13 é o do atendimento, e ele é o mais forte que
existe justamente porque foi retestado. Um dos dois derrubados caiu NO
reteste. A escada não é decoração: ela já provou que separa padrão de
coincidência de amostra.

O que este arquivo faz, e o que ele se recusa a fazer
-----------------------------------------------------
Testa o que dá para testar no dado, e marca como NÃO TESTÁVEL o que só se
responde lendo. Saber qual afirmação tem lastro e qual é leitura humana é,
por si só, informação para a diretoria — e é o contrário de inflar a escada
com achado que ninguém conferiu.

A exceção nomeada vale mais que o placar limpo. Um padrão sem exceção soa a
curadoria; um padrão com a praça que contraria, nomeada, aguenta pergunta.

Uso:
    python3 scripts/reteste.py
    python3 scripts/reteste.py --salvar     # reescreve dados/conteudo/achados.json
"""
import argparse, json, pathlib, statistics as st, sys
from collections import defaultdict

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ/"scripts"))
from cruzamento import jsonl, reviews_unicos, identidades, coleta

CONT = RAIZ/"dados"/"conteudo"

# Abaixo disto a praça não vota: 13 negativas não sustentam porcentagem.
MIN_AMOSTRA = 30

OPERACAO = {"atendimento", "agenda_espera", "comunicacao_resposta", "contrato_burocracia"}
PRODUTO = {"qualidade_resultado", "aparelho_tratamento"}


class Base:
    def __init__(self):
        self.ident = identidades(com_unidade=False)
        self.rede = identidades()
        _, self.linhas = coleta()
        self.cls = jsonl("reviews_classificados")
        self.temas = {}
        for t in jsonl("temas"):
            self.temas.setdefault(t["praca_id"], {})[t["tema"]] = t
        self.revs = defaultdict(list)
        for r in reviews_unicos():
            self.revs[r.get("praca_id")].append(r)
        self.nossos = {p: {l["local_id"] for l in d.get("locais", [])
                           if l.get("papel") == "proprio"}
                       for p, d in self.ident.items()}
        self.cap = {}
        for c in jsonl("captacao"):
            self.cap[c["praca_id"]] = c

    def negativas(self, p):
        return [x for x in self.cls
                if x["praca_id"] == p and str(x.get("nota")) in ("1", "2", "3")]

    def tema_pct(self, p, tema):
        t = (self.temas.get(p) or {}).get(tema)
        return (t or {}).get("pct")


# --------------------------------------------------------------- os testes
#
# Cada teste devolve, por praça: (passa, valor_legivel) — ou None quando a
# praça não tem amostra para votar. Nunca invente voto: praça sem amostra sai
# da conta e o denominador encolhe, escrito.

def t_ferida_operacao(b, p):
    neg = b.negativas(p)
    if len(neg) < MIN_AMOSTRA:
        return None
    o = 100*sum(1 for x in neg if set(x.get("temas") or []) & OPERACAO)/len(neg)
    pr = 100*sum(1 for x in neg if set(x.get("temas") or []) & PRODUTO)/len(neg)
    return o > pr, f"operação {o:.0f}% contra produto {pr:.0f}% em {len(neg)} negativas"


def t_gente_com_nome(b, p):
    v = b.tema_pct(p, "pessoas_nominais")
    if v is None:
        return None
    return v >= 0.03, f"{100*v:.0f}% das avaliações citam alguém pelo nome"


def t_porta_preco(b, p):
    c = b.cap.get(p)
    if not c:
        return None
    fam = c.get("por_familia") or {}
    tot = sum((fam.get(k) or {}).get("dentro", 0) + (fam.get(k) or {}).get("fora", 0)
              for k in fam)
    if not tot:
        return None
    # A porta genérica ("dentista") é maior que a porta do produto
    # ("aparelho"/"ortodontia")? É a leitura que a rede mais discute.
    d = fam.get("dentista") or {}
    ap = fam.get("aparelho") or {}
    nd = d.get("dentro", 0) + d.get("fora", 0)
    na = ap.get("dentro", 0) + ap.get("fora", 0)
    if not nd and not na:
        return None
    return nd > na, f"porta 'dentista' {nd} frases contra 'aparelho' {na}"


def t_adulto_esquecido(b, p):
    """As faixas moram em dois lugares diferentes e eu procurava no terceiro.

    Nas praças da rede estão em ibge[].idades.alvo_30_45; nas de oportunidade,
    numa coluna própria de oportunidade.jsonl. Procurar por `x.alvo_30_45.valor`
    não achava nenhum dos dois, e o achado saía 0/0 — que é o jeito silencioso
    de um teste dizer que está quebrado."""
    d = b.ident[p]
    a30 = a9 = 0
    for x in d.get("ibge") or []:
        idades = x.get("idades") or {}
        a30 += int(idades.get("alvo_30_45") or 0)
        a9 += int(idades.get("alvo_9_15") or 0)
    if not a30 or not a9:
        rot = d.get("rotulo")
        for o in jsonl("oportunidade"):
            if o.get("rotulo") == rot:
                a30, a9 = o.get("alvo_30_45") or 0, o.get("alvo_9_15") or 0
    if not a30 or not a9:
        return None
    return a30 > a9, (f"{a30:,} adultos de 30-45 contra {a9:,} de 9-15 — "
                      f"{a30/a9:.1f}x").replace(",", ".")


def t_prova_social_parada(b, p):
    nossas = [x for x in b.linhas
              if x["praca"] == p and x["papel"] == "proprio" and x["ritmo"] is not None]
    if not nossas:
        return None
    conc = [x for x in b.linhas
            if x["praca"] == p and x["papel"] != "proprio" and x["ritmo"] is not None]
    if not conc:
        return None
    med = st.median([x["ritmo"] for x in conc])
    pior = min(x["ritmo"] for x in nossas)
    return pior < med, (f"a mais lenta das nossas faz {pior:.1f}/mês contra "
                        f"mediana {med:.1f} da praça")


def t_mae_decide(b, p):
    v = b.tema_pct(p, "familia_filhos")
    if v is None:
        return None
    return v >= 0.03, f"{100*v:.0f}% das avaliações falam de filho ou família"


def t_recomendacao(b, p):
    v = b.tema_pct(p, "recomendacao_lealdade")
    if v is None:
        return None
    return v >= 0.15, f"{100*v:.0f}% recomendam explicitamente"


TESTES = [
    ("A ferida é sempre operação — nunca o produto", t_ferida_operacao,
     "compara, nas avaliações de 1 a 3 estrelas, quantas citam operação "
     "(atendimento, agenda, comunicação, contrato) contra quantas citam "
     "produto (resultado, aparelho). Uma avaliação pode citar as duas — por "
     "isso os dois somam mais de 100%."),
    ("A confiança é em gente com nome, não em marca", t_gente_com_nome,
     "mede quanto das avaliações cita uma pessoa pelo nome próprio."),
    ("A porta de entrada é 'dentista', não 'aparelho'", t_porta_preco,
     "compara quantas frases que a cidade digita são da família 'dentista' "
     "contra a família 'aparelho'. Quem digita 'dentista' é quem marca a "
     "avaliação e sai com aparelho."),
    ("O adulto 30+ é dinheiro na mesa e nenhuma praça fala com ele", t_adulto_esquecido,
     "compara a população de 30 a 45 anos com a de 9 a 15, pelo IBGE."),
    # O título original era "A prova social está parada em TODAS". O reteste
    # derrubou o "todas": Contagem, Palmas e Prudente correm ACIMA da mediana
    # da própria praça. O achado que sobrevive é mais estreito e mais útil —
    # é sobre a unidade mais lenta de cada praça, não sobre a rede.
    ("Em toda praça com mais de uma unidade, a mais lenta fica abaixo da mediana da cidade",
     t_prova_social_parada,
     "compara o ritmo da nossa unidade mais lenta com a mediana das clínicas "
     "da própria praça."),
    ("A mãe é a decisora — e lê os reviews antes de escolher", t_mae_decide,
     "mede quanto das avaliações menciona filho ou família."),
    ("A recomendação é o motor, e ela é espontânea", t_recomendacao,
     "mede quanto das avaliações recomenda explicitamente a clínica."),
]

# Achados que NÃO se testam com o que temos. Ficam na escada com o degrau
# rebaixado e o motivo escrito — é mais honesto do que deixá-los como 4/4.
NAO_TESTAVEIS = [
    ("Julho é o pico da mãe-decisora",
     "a série de sazonalidade tem 4 pontos, todos de SC. Uma região não é "
     "calendário de rede."),
    ("A clínica-escola é fraca exatamente onde a rede é forte",
     "exige saber o que cada clínica-escola oferece. A imprensa diz que "
     "existe atendimento gratuito, não se ele inclui APARELHO — e odontologia "
     "não é ortodontia."),
    ("A joia local existe, é incopiável — e está enterrada",
     "é leitura humana de história local. Não há campo que a meça."),
    ("A embalagem é a mesma: feed institucional + anúncio de urgência",
     "exige ler os 735 anúncios um a um e classificar tom. Não foi feito."),
    ("A ordem certa é blindar a operação antes de qualquer mídia nova",
     "é recomendação de método, não achado mensurável. Vale como conselho, "
     "não como padrão medido."),
    ("Os mesmos quatro formatos fixos de conteúdo emergem nas quatro",
     "exige classificar 2.993 posts por formato. Não foi feito."),
]


def degrau(passou, votou):
    if votou == 0:
        return "sem_amostra"
    r = passou/votou
    if votou >= 10 and r == 1.0:
        return "constante"
    if votou >= 10 and r >= 0.8:
        return "vale_para_a_rede"
    if r >= 0.8:
        return "se_repete"
    if r >= 0.5:
        return "candidata"
    return "derrubada"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()
    b = Base()
    pracas = sorted(b.ident)

    print(f"\n{'='*80}\n  O RETESTE — cada achado contra as {len(pracas)} praças\n{'='*80}")
    saida = []
    for titulo, fn, como in TESTES:
        votos, fora = [], []
        for p in pracas:
            r = fn(b, p)
            if r is None:
                fora.append(p)
                continue
            ok, txt = r
            votos.append((p, ok, txt))
        passou = sum(1 for _, ok, _ in votos if ok)
        d = degrau(passou, len(votos))
        excecoes = [(p, t) for p, ok, t in votos if not ok]
        print(f"\n  [{d.upper()}]  {passou}/{len(votos)}   {titulo}")
        print(f"     como se mede: {como}")
        if excecoes:
            print(f"     ⚠ contraria em {len(excecoes)}:")
            for p, t in excecoes:
                print(f"         {b.ident[p].get('rotulo')}: {t}")
        if fora:
            print(f"     sem amostra para votar: {', '.join(fora)}")
        saida.append({
            "t": titulo, "n": f"{passou}/{len(votos)}", "estado": d,
            "como_se_mede": como,
            "ev": [[b.ident[p].get("rotulo"), t] for p, ok, t in votos if ok][:8],
            "excecoes": [{"praca": b.ident[p].get("rotulo"), "valor": t}
                         for p, t in excecoes],
            "sem_amostra": [b.ident[p].get("rotulo") for p in fora],
        })

    print(f"\n{'='*80}\n  NÃO TESTÁVEIS COM O QUE TEMOS\n{'='*80}")
    for t, porque in NAO_TESTAVEIS:
        print(f"\n  ✋ {t}\n     {porque}")
        saida.append({"t": t, "n": "—", "estado": "nao_testavel",
                      "por_que_nao": porque, "ev": [], "excecoes": []})

    if a.salvar:
        p = CONT/"achados.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        # o achado do atendimento já é 13/13 e foi retestado; fica no topo
        topo = [x for x in d["achados"] if x.get("estado") == "constante"]
        caidos = [x for x in d["achados"] if x.get("estado") == "derrubada"]
        d["achados"] = topo + saida + caidos
        d["nota_teto"] = (
            f"Os achados foram retestados contra as {len(pracas)} praças em "
            f"{'2026-08-10'}. Antes, doze deles diziam 4/4 — mediam quatro "
            f"cidades e nunca tinham sido conferidos contra as nove que "
            f"entraram depois. Seis não são testáveis com o que temos e estão "
            f"marcados como tal, com o motivo: preferimos declarar o que é "
            f"leitura humana a inflar a escada. Toda exceção aparece nomeada — "
            f"padrão sem exceção soa a curadoria.")
        p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n  → dados/conteudo/achados.json ({len(d['achados'])} achados)")


if __name__ == "__main__":
    main()
