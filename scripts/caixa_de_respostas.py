#!/usr/bin/env python3
"""
caixa_de_respostas.py — as avaliações negativas sem resposta, uma a uma.

A única leitura que a revisão externa classificou como "SIM" sem ressalva:
responder reclamação pública é objetivo, tem dono, tem prazo, e o dado traz
tudo — texto, nota, data, se foi respondida e quando. Não é score: é a lista
do que está aberto, da mais recente para a mais antiga.

Regra de escopo: SÓ unidades da rede. Praça de estudo não tem franqueado para
responder — entra aqui e vira o erro dos seis planos de novo.

O que o histórico completo mudou: a fila saltou de 75 para o número real.
Com amostra truncada, a maior parte das negativas antigas simplesmente não
estava no disco.

Uso:
    python3 scripts/caixa_de_respostas.py
    python3 scripts/caixa_de_respostas.py --salvar
"""
import argparse, datetime as dt, json, pathlib, re, sys
from collections import defaultdict

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ/"scripts"))
from cruzamento import reviews_unicos, identidades, conta, confianca
from insight import monta as monta_insight

PORTAL = RAIZ/"dados"/"portal"

# A janela que decide a prioridade. Fora dela a reclamação continua aberta
# e continua contada — só não é urgência: ninguém escolhe clínica lendo
# uma avaliação de 2015.
JANELA_QUE_PESA = 180


# O ASSUNTO DA RECLAMAÇÃO, quando o texto diz. Não é análise de
# sentimento — é procurar a palavra que nomeia o momento, para o
# franqueado saber do que se trata antes de abrir uma a uma.
ASSUNTOS = [
    ("cobrança", r"cobr|pagamento|boleto|multa|parcel|financeir"),
    ("contato", r"telefone|liga(r|ção)|whats|n[ãa]o atende|responde"),
    ("agendamento", r"agenda|remarc|desmarc|hor[áa]rio|atras"),
    ("recepção", r"recep|atendente|secret|balc[ãa]o|mal educad"),
    ("atendimento clínico", r"dentist|doutor|dr[a]?\.|procedimento|"
                            r"machuc|dor|aparelho"),
]


def _assuntos(itens):
    achados = []
    for rotulo, rx in ASSUNTOS:
        n = sum(1 for x in itens
                if x.get("texto") and re.search(rx, x["texto"], re.I))
        if n:
            achados.append({"assunto": rotulo, "quantas": n,
                            "frase": conta(n, "avaliação", "avaliações")})
    achados.sort(key=lambda a: -a["quantas"])
    return achados[:3]


def lid_de(u):
    return u["local_id"]


def _nota(x):
    """A nota vem como texto na série ('1'); comparar com número explode."""
    try:
        return int(str(x.get("nota")))
    except (TypeError, ValueError):
        return 5


def monta():
    ident = identidades()          # SÓ rede — praça de estudo fica fora
    nossos = {}
    for p, d in ident.items():
        for l in d.get("locais", []):
            if l.get("papel") == "proprio":
                nossos[l["local_id"]] = {"praca_id": p, "rotulo": d.get("rotulo"),
                                         # `unidade` é o nome de tela, desambiguado por
                                         # `nome_da_loja.py`; `nome` é o
                                         # cadastro cru, e sete unidades de
                                         # Porto Alegre se chamam OrthoDontic
                                         "unidade": l.get("unidade") or l.get("nome")}

    caixa = defaultdict(list)
    respondidas = defaultdict(int)
    for r in reviews_unicos():
        lid = r.get("local_id")
        if lid not in nossos:
            continue
        if str(r.get("nota")) not in ("1", "2", "3"):
            continue
        if r.get("respondida"):
            respondidas[lid] += 1
            continue
        caixa[lid].append({
            "nota": r.get("nota"), "data": str(r.get("data") or "")[:10],
            "texto": (r.get("texto") or "").strip() or None,
            "tem_texto": bool((r.get("texto") or "").strip()),
        })

    unidades = []
    for lid, itens in caixa.items():
        itens.sort(key=lambda x: x["data"] or "", reverse=True)
        m = nossos[lid]
        unidades.append({
            **m, "local_id": lid,
            "abertas": len(itens),
            "com_texto": sum(1 for x in itens if x["tem_texto"]),
            "ja_respondidas": respondidas.get(lid, 0),
            "itens": itens,
        })
    # ------------------------------------------------ de acervo para TRABALHO
    #
    # "399 avaliações esperando resposta" impressiona e não ajuda: ninguém
    # responde 399. O que resolve trabalho é PRIORIDADE — qual unidade tem
    # crítica de 1 estrela parada há mais tempo, e o que dizer sobre ela.
    #
    # A ordem é por gravidade: quantas de uma estrela, e há quantos dias a
    # mais antiga está aberta. Volume puro colocaria na frente a loja
    # grande, que tem mais de tudo só por ser grande.
    hoje = dt.date.today()
    limite = (hoje - dt.timedelta(days=JANELA_QUE_PESA)).isoformat()
    for u in unidades:
        criticas = [x for x in u["itens"] if _nota(x) <= 2]
        # RECLAMAÇÃO DE ONZE ANOS NÃO É URGÊNCIA. A primeira ordenação usou
        # "há quantos dias a mais antiga espera" e pôs na frente uma de
        # 4.172 dias — verdade, e inútil: ninguém lê 2015 na ficha. As 40
        # unidades saíram todas em vermelho, ou seja, a régua não separava
        # nada. O que pesa é a crítica RECENTE, que é a que o próximo
        # paciente encontra no topo.
        recentes = [x for x in criticas if (x["data"] or "") >= limite]
        datas = [x["data"] for x in u["itens"] if x["data"]]
        mais_antiga = min(datas) if datas else None
        dias = ((hoje - dt.date.fromisoformat(mais_antiga)).days
                if mais_antiga else None)
        u["criticas"] = len(criticas)
        u["criticas_recentes"] = len(recentes)
        u["janela_que_pesa_dias"] = JANELA_QUE_PESA
        u["mais_antiga_em"] = mais_antiga
        u["dias_da_mais_antiga"] = dias
        # o que o paciente estava reclamando, quando o texto diz
        u["assuntos"] = _assuntos(recentes or u["itens"])
        u["frase"] = (
            conta(len(recentes), "crítica sem resposta", "críticas sem resposta")
            + f" nos últimos {JANELA_QUE_PESA} dias"
            + (f" · {conta(u['criticas'], 'aberta', 'abertas')} no total"
               if u["criticas"] > len(recentes) else ""))
        u["gravidade"] = ("alta" if len(recentes) >= 2
                          else "media" if recentes else "baixa")
        u["insight"] = None if u["gravidade"] == "baixa" else monta_insight(
            fonte="respostas", chave=lid_de(u),
            titulo="Avaliações críticas esperando resposta",
            onde=u["rotulo"] + (f" · {u['unidade']}" if u.get("unidade") else ""),
            fato=u["frase"],
            o_que_perguntar=("quem responde as avaliações hoje, e com que "
                             "frequência?"),
            por_que_importa=("a reclamação sem resposta é a versão do "
                             "paciente dos fatos, e é ela que o próximo "
                             "lê antes de escolher"),
            acao=("responder as críticas com texto em 48 horas, começando "
                  "pela mais antiga"),
            publico="franqueado",
            gravidade=u["gravidade"],
            evidencias=[{"o_que": f"{x['nota']}★ · {x['data']}",
                         "texto": (x["texto"] or "")[:180]}
                        for x in u["itens"] if x["tem_texto"]][:3],
            nao_faca=("não pedir para apagar avaliação: responder muda o "
                      "que o próximo paciente lê, apagar não"),
            revisar_em=14,
            link=f"clinicas/{lid_de(u)}",
            carimbo=confianca(
                natureza="fato",
                amostra=u["abertas"],
                unidade_amostra=("avaliação aberta", "avaliações abertas"),
                fonte="dados/serie/reviews.jsonl",
                a_favor=["cada item tem nota, data e texto do próprio "
                         "paciente"],
                contra=["o portal vê a resposta pública; conversa por "
                        "telefone ou no balcão ele não vê"]),
        )
    # gravidade primeiro, depois quanto tempo a mais antiga está parada
    _peso = {"alta": 0, "media": 1, "baixa": 2}
    unidades.sort(key=lambda u: (_peso[u["gravidade"]],
                                 -u["criticas_recentes"],
                                 -u["criticas"], -u["abertas"]))

    total = sum(u["abertas"] for u in unidades)
    com_texto = sum(u["com_texto"] for u in unidades)
    return {
        "o_que_e": "Toda avaliação de 1 a 3 estrelas das unidades da rede que "
                   "está SEM resposta, da mais recente para a mais antiga.",
        "a_regra": "Responder não é o que faz a unidade sustentar — Cuiabá "
                   "sustenta há 26 meses respondendo 1%. Responder é higiene "
                   "de reputação: a mãe lê os comentários antes de escolher, "
                   "e a reclamação sem resposta é a versão dela dos fatos.",
        "prazo_sugerido": "48 horas para as com texto; as só-estrela podem "
                          "receber resposta padrão.",
        "dono": "franqueado; o consultor cobra na visita",
        "total_abertas": total,
        "com_texto": com_texto,
        "manchete": (
            conta(sum(1 for u in unidades if u["gravidade"] == "alta"),
                  "unidade precisa responder agora",
                  "unidades precisam responder agora")
            + f" — {total} avaliações negativas abertas na rede medida, "
            + f"{com_texto} com o paciente explicando o motivo."),
        "ordem": (f"gravidade primeiro: críticas de 1 ou 2 estrelas sem "
                  f"resposta nos últimos {JANELA_QUE_PESA} dias. O acervo "
                  f"antigo continua contado, mas não é urgência — ninguém "
                  f"escolhe clínica lendo uma avaliação de 2015."),
        "janela_que_pesa_dias": JANELA_QUE_PESA,
        # LISTA DE ID NÃO DESENHA LINHA. A primeira versão mandava só os
        # `local_id` daqui, e a tela desenhou 20 linhas VAZIAS: o casco não
        # pode ir buscar o resto, porque procurar registro por id é
        # trabalho de banco, não de tela. Quem publica uma lista publica os
        # registros dela.
        # E A LISTA DE PRIORIDADE NÃO CARREGA O ACERVO INTEIRO. Mandar as
        # unidades com TODAS as avaliações abertas dobrou o arquivo para
        # 592 KB. Aqui vão as críticas da janela que pesa — que são as que
        # a tela desenha — com o total ao lado para o "ver todas".
        "precisam_agora": [
            dict(u, itens=[x for x in u["itens"]
                           if _nota(x) <= 2 and (x["data"] or "") >= limite][:12],
                 itens_total=len(u["itens"]),
                 frase_ver_todas=f"ver as {len(u['itens'])} abertas desta unidade")
            for u in unidades if u["gravidade"] == "alta"],
        "precisam_agora_total": sum(1 for u in unidades
                                    if u["gravidade"] == "alta"),
        # a tela não conta lista: "lojas com fila" e o tamanho de cada fila
        # saem contados daqui
        "lojas_com_fila": len(unidades),
        "unidades": [dict(u, itens_total=len(u.get("itens") or []))
                     for u in unidades],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()
    d = monta()
    print(f"\n  {d['manchete']}\n")
    for u in d["unidades"][:10]:
        cor = {"alta": "🔴", "media": "🟡", "baixa": "🟢"}[u["gravidade"]]
        print(f"  {cor} {u['rotulo']} · {u['unidade']}")
        print(f"       {u['frase']}")
        if u["assuntos"]:
            print("       assuntos: "
                  + ", ".join(f"{a['assunto']} ({a['quantas']})"
                              for a in u["assuntos"]))
    if a.salvar:
        (PORTAL/"caixa_de_respostas.json").write_text(
            json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n  → dados/portal/caixa_de_respostas.json")


if __name__ == "__main__":
    main()
