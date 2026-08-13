#!/usr/bin/env python3
"""
agenda_do_consultor.py — a fila vira as CONVERSAS da semana.

A diferença
-----------
A fila responde "quem merece atenção", ordenado por urgência. É um
ranking, e ranking é para olhar. O consultor não precisa olhar: ele
precisa entrar num carro na terça-feira e saber o que vai falar.

Então a mesma matéria-prima sai daqui em outra forma:

    ESTA SEMANA
    SC · Joinville · América          🔴 prioridade alta
    O que vimos      o ritmo de avaliações parou enquanto um rival mantém
                     crescimento
    O que conversar  existe rotina de pedir avaliação no fechamento do
                     atendimento?
    Leve             o número do rival, e a unidade da rede com o mesmo
                     tamanho de mercado que mantém ritmo
    Não faça         contratar mídia para corrigir isto
    Verificar em     14 dias
    [ver clínica]    [encaminhar]

Nada aqui é coleta nova: é fila + gêmeos + jornada, colados na ordem em
que a conversa acontece.

O que ela não faz
-----------------
Não marca visita, não guarda quem foi, não confirma execução. O portal não
fala com a unidade — e a única prova de que algo aconteceu continua sendo
a próxima medição.

Uso:
    python3 scripts/agenda_do_consultor.py
    python3 scripts/agenda_do_consultor.py --salvar
"""
import argparse, json, pathlib, sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ/"scripts"))
from cruzamento import conta, confianca
from insight import monta as monta_insight

PORTAL = RAIZ/"dados"/"portal"

QUANTAS_NA_SEMANA = 6      # a semana de um consultor não tem 45 visitas

# O QUE NÃO FAZER, POR GATILHO. É a parte que mais economiza dinheiro da
# rede: quase toda dor deste portal se conserta sem verba de mídia, e
# comprar mídia em cima de operação quebrada é pagar para levar mais
# gente a uma experiência ruim.
NAO_FACA = {
    "parada": "não contratar mídia para corrigir isto — o contador parou "
              "na rotina do balcão, não na entrada de gente",
    "nao_engatou": "não comparar com unidade madura: esta loja está "
                   "começando, e a régua dela é o próprio começo",
    "rival": "não responder com preço. O rival não está ganhando por "
             "preço, e a comparação medida diz em quê ele ganha",
    "posicao": "não pedir campanha antes de auditar a ficha — posição de "
               "mapa se conserta com ficha completa, e isso é de graça",
    "nota": "não pedir para apagar avaliação. Responder muda o que o "
            "próximo paciente lê; apagar não",
    "silencio": "não entrar no leilão com a palavra do produto. A cidade "
                "digita 'dentista' muito mais que 'aparelho'",
}

O_QUE_PERGUNTAR = {
    "parada": "mudou alguma coisa na rotina de pedir avaliação no fim do "
              "atendimento? Quem pedia, pede ainda?",
    "nao_engatou": "o pacote de abertura foi rodado por inteiro — ficha "
                   "completa, primeiras avaliações, frases da cidade?",
    "rival": "o que mudou na rua nos últimos meses? Este concorrente "
             "sustenta ritmo há muito tempo, não é campanha",
    "posicao": "a ficha do Google está completa: foto recente, horário, "
               "lista de serviços, resposta às avaliações?",
    "nota": "quais das avaliações negativas do trimestre já foram lidas "
            "com a equipe? A resposta pública é para o próximo paciente",
    "silencio": "existe verba de mídia local hoje, e ela está indo para "
                "onde? A cidade tem leilão cheio e a rede não está nele",
}


def carrega(nome):
    p = PORTAL/f"{nome}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def monta():
    fila = carrega("fila")
    if not fila.get("fila"):
        print("  ✗ FALHA: dados/portal/fila.json vazio.\n"
              "  rode antes: python3 scripts/fila.py --salvar")
        sys.exit(1)
    gem = {x["local_id"]: x for x in carrega("gemeos").get("lojas", [])}
    anom = {x["local_id"]: x
            for x in carrega("anomalias").get("anomalias_negativas", [])}
    jor = {x["local_id"]: x for x in carrega("jornada").get("lojas", [])}

    semana = []
    for u in fila["fila"]:
        if not u.get("acao") or not u.get("gatilhos"):
            continue
        dom = u["acao"]["por_causa_de"]
        g0 = u["gatilhos"][0]
        lid = u["local_id"]

        # O QUE LEVAR. Evidência é o que o consultor põe na mesa, e ela
        # tem de vir medida — nunca "eu acho que".
        leve = []
        if u.get("quem_avanca"):
            r = u["quem_avanca"]
            leve.append({
                "o_que": "o concorrente que corre mais",
                "texto": (f"{r['nome']} sustenta {r['ritmo']:.1f} "
                          f"avaliações/mês há "
                          f"{conta(r['meses'], 'mês', 'meses')}"),
            })
        g = gem.get(lid)
        if g and g.get("gemeos"):
            t = g["gemeos"][0]
            difs = [df for df in t.get("diferencas", [])]
            if difs:
                leve.append({
                    "o_que": "a unidade da rede com o mercado mais parecido",
                    "texto": (f"{t['rotulo']} · "
                              f"{t['unidade'].replace('OrthoDontic', '').strip(' ·')}"
                              f" — " + "; ".join(f"{df['o_que']}, {df['texto']}"
                                                 for df in difs[:2])),
                })
        j = jor.get(lid)
        if j:
            doi = [e for e in j.get("estagios", [])
                   if e.get("medido") and not e.get("amostra_curta")
                   and e.get("pct_dor")]
            doi.sort(key=lambda e: -e["pct_dor"])
            if doi:
                d0 = doi[0]
                leve.append({
                    "o_que": "onde o paciente desta loja dói",
                    "texto": (f"{d0['rotulo']}: {d0['pct_dor']}% das "
                              f"{conta(d0['avaliacoes'], 'avaliação', 'avaliações')}"
                              f" desse momento são queixa — quem resolve é "
                              f"{d0['quem_resolve']}"),
                })
        a = anom.get(lid)
        if a:
            leve.append({
                "o_que": "comparada com as semelhantes",
                "texto": a["leitura"],
            })

        ins = monta_insight(
            fonte="agenda", chave=f"{lid}|{dom}",
            titulo=u["acao"]["o_que"],
            onde=u["rotulo"] + (f" · {u['unidade_curta']}"
                                if u.get("unidade_curta") else ""),
            fato=f"{g0['titulo']}: {g0['fato']}",
            por_que_importa=(
                "esta unidade está na faixa "
                f"{u['faixa']} da fila de intervenção, e o gatilho que mais "
                f"pesa é este"),
            acao=u["acao"]["o_que"],
            o_que_perguntar=O_QUE_PERGUNTAR.get(dom),
            nao_faca=NAO_FACA.get(dom),
            revisar_em=(u.get("tarefa") or {}).get("prazo_dias"),
            publico=("consultor" if u["acao"]["dono"] == "consultor de campo"
                     else "franqueado"),
            gravidade=("alta" if u["faixa"] == "vermelha"
                       else "media" if u["faixa"] == "amarela" else "baixa"),
            evidencias=leve,
            link=f"clinicas/{lid}",
            medido_em=fila.get("corte"),
            carimbo=confianca(
                natureza="fato",
                amostra=u.get("avaliacoes"),
                unidade_amostra=("avaliação", "avaliações"),
                medicoes=(u.get("meses") or 0) and 2,
                fonte=g0.get("fonte"),
                a_favor=["o gatilho tem um número que está num arquivo"],
                contra=["o portal não sabe o que acontece dentro da "
                        "clínica: ele vê a rua"]),
        )
        semana.append({
            "local_id": lid, "praca_id": u["praca_id"],
            "rotulo": u["rotulo"], "unidade": u.get("unidade"),
            "unidade_curta": u.get("unidade_curta"),
            "faixa": u["faixa"], "urgencia": u["urgencia"],
            "prioridade": ("alta" if u["faixa"] == "vermelha"
                           else "média" if u["faixa"] == "amarela"
                           else "baixa"),
            "o_que_vimos": f"{g0['titulo']}: {g0['fato']}",
            "o_que_conversar": O_QUE_PERGUNTAR.get(dom),
            "leve": leve, "leve_total": len(leve),
            "nao_faca": NAO_FACA.get(dom),
            "acao": u["acao"],
            "revisar_em_dias": (u.get("tarefa") or {}).get("prazo_dias"),
            "tarefa": u.get("tarefa"),
            "insight": ins,
        })

    semana.sort(key=lambda x: -x["urgencia"])
    esta_semana = semana[:QUANTAS_NA_SEMANA]
    return {
        "o_que_e": "As conversas que o time de campo precisa ter esta "
                   "semana, na ordem, com o que levar em cada uma.",
        "por_que_importa": ("ranking é para olhar; agenda é para usar. A "
                            "mesma fila, na forma em que a visita "
                            "acontece"),
        "o_que_nao_e": ("não marca visita, não guarda quem foi, não "
                        "confirma execução. Quem responde se algo "
                        "aconteceu é a próxima medição"),
        "quantas_na_semana": QUANTAS_NA_SEMANA,
        "manchete": (conta(len(esta_semana), "conversa importante",
                           "conversas importantes")
                     + " para o time de campo esta semana"),
        "esta_semana": esta_semana,
        "esta_semana_total": len(esta_semana),
        "na_fila_total": len(semana),
        "frase_ver_todas": (f"ver as {len(semana)} unidades com ação aberta"
                            if len(semana) > len(esta_semana) else None),
        "medido_em": (carrega("fila") or {}).get("corte"),
    }


def imprime(d):
    print(f"\n{'='*78}\n  A AGENDA DO CONSULTOR — {d['manchete']}\n{'='*78}")
    for x in d["esta_semana"]:
        cor = {"alta": "🔴", "média": "🟡", "baixa": "🟢"}[x["prioridade"]]
        et = x["rotulo"] + (f" · {x['unidade_curta']}"
                            if x["unidade_curta"] else "")
        print(f"\n  {cor} {et}   prioridade {x['prioridade']}")
        print(f"     O que vimos      {x['o_que_vimos']}")
        if x["o_que_conversar"]:
            print(f"     O que conversar  {x['o_que_conversar']}")
        for l in x["leve"]:
            print(f"     Leve             {l['o_que']}: {l['texto'][:96]}")
        if x["nao_faca"]:
            print(f"     Não faça         {x['nao_faca']}")
        if x["revisar_em_dias"]:
            print(f"     Verificar em     {x['revisar_em_dias']} dias")
    print()
    if d["frase_ver_todas"]:
        print(f"  {d['frase_ver_todas']}\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()
    d = monta()
    imprime(d)
    if a.salvar:
        (PORTAL/"agenda.json").write_text(
            json.dumps(d, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8")
        print(f"  → dados/portal/agenda.json")


if __name__ == "__main__":
    main()
