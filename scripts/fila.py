#!/usr/bin/env python3
"""
fila.py — A FILA DE INTERVENÇÃO. A única tela que a franqueadora precisa abrir.

Por que ela existe
------------------
Uma revisão externa leu esta base inteira e disse a mesma coisa por dois
caminhos diferentes:

  "O produto entrega inteligência como ACERVO. O valor está em decidir ONDE
   INTERVIR ANTES que uma unidade perca relevância local. O portal responde
   pedaços — quem parou, presença na busca, ficha de praça. Não entrega uma
   lista única, ordenada por urgência, com unidade ameaçada, concorrente que
   está tomando espaço, evidência da mudança e intervenção recomendada."

E disse qual é o risco de o produto morrer no terceiro mês:

  "Não conseguir demonstrar que NENHUMA decisão ou resultado mudou por causa
   dele."

Este arquivo responde aos dois. Ele não coleta nada novo: lê o que já foi
pago e coletado e transforma em uma fila com dono, prazo e — a parte que não
existia — um registro de CICLO, onde cada alerta guarda o que foi feito e o
que aconteceu depois. Esse histórico alerta → ação → resultado é o único
ativo aqui que um concorrente não copia raspando as mesmas fontes públicas.

O que a fila NÃO é
------------------
Não é ranking de faturamento. Nada aqui vem de dado interno. "Perder atenção"
significa participação observável em busca, avaliações, publicidade e
atividade digital. Está escrito em cada linha, e a tela é obrigada a mostrar.

Uso:
    python3 scripts/fila.py
    python3 scripts/fila.py --salvar     # grava dados/portal/fila.json
"""
import argparse, datetime as dt, json, pathlib, re, statistics as st
import unicodedata
from collections import defaultdict, Counter

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SERIE = RAIZ/"dados"/"serie"
PORTAL = RAIZ/"dados"/"portal"

import sys
sys.path.insert(0, str(RAIZ/"scripts"))
from cruzamento import coleta, jsonl, reviews_unicos, conta   # mesma conta, mesmos números


# --------------------------------------------------------------- os gatilhos
#
# Cada gatilho é uma pergunta de sim ou não que se responde com um número que
# está num arquivo. Peso alto = o consultor precisa sair do lugar. Nenhum
# gatilho é opinião: se não der para apontar o arquivo, não entra.
#
GATILHOS = {
    "parada":   {"peso": 30, "titulo": "O contador de avaliações parou"},
    "nao_engatou": {"peso": 20, "titulo": "Unidade nova que ainda não engatou"},
    "rival":    {"peso": 25, "titulo": "Um rival de aparelho sustenta e corre mais"},
    "posicao":  {"peso": 20, "titulo": "Está na metade de baixo da própria praça"},
    "nota":     {"peso": 15, "titulo": "Nota abaixo da mediana da praça"},
    "silencio": {"peso": 15, "titulo": "Silêncio publicitário com leilão cheio"},
}
FAIXA = [(60, "vermelha"), (30, "amarela"), (0, "verde")]

# Quando um leilão tem menos anunciantes que isto, não estar nele não é
# silêncio — é praça vazia, que é oportunidade e não ameaça. Mafra tem
# ZERO anunciantes: cobrar campanha lá seria inventar um problema.
LEILAO_CHEIO = 5

# Diferença de nota abaixo disto não é achado, é arredondamento. Sem esta
# trava, 4,9 contra mediana 5,0 vira "alerta" e o consultor perde a viagem.
NOTA_MINIMA_DE_DIFERENCA = 0.3

# Unidade cujo primeiro review é recente não está parada — está começando.
# São diagnósticos opostos e a ação é outra.
MESES_PARA_DEIXAR_DE_SER_NOVA = 12


def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s or "")
                   if unicodedata.category(c) != "Mn").lower()


def nosso(nome):
    """'Clínica Ortho Mais' NÃO é nossa. 'OrthoDontic em Contagem' é.

    O erro de deixar 'ortho' solto marcaria três concorrentes como unidades da
    rede e apagaria o alerta de silêncio publicitário justamente onde ele é
    verdadeiro."""
    return "orthodontic" in re.sub(r"[^a-z]", "", sem_acento(nome))


def faixa(u):
    for corte, nome in FAIXA:
        if u >= corte:
            return nome
    return "verde"


def ultimo_por(nome, chave="praca_id"):
    ult = {}
    for x in jsonl(nome):
        k = x.get(chave)
        if k and (k not in ult or x.get("snapshot_date", "") >= ult[k].get("snapshot_date", "")):
            ult[k] = x
    return ult


# --------------------------------------------------------------------- ações
#
# A ação vem do gatilho que pesa mais, não de um texto genérico. Prazo e dono
# são obrigatórios — alerta sem dono é boletim, e boletim ninguém executa.
#
# O prazo de cada gatilho em dias — é dele que nasce o status da tarefa
# (aberta → vencida). "rival" não tem prazo em dias: o prazo é a próxima
# visita do consultor, e cobrar calendário aí seria inventar precisão.
PRAZO_DIAS = {"parada": 14, "nao_engatou": 60, "rival": None,
              "posicao": 7, "nota": 10, "silencio": 30}

ACAO = {
    "parada": ("Religar a rotina de pedido de avaliação no fim do atendimento",
               "14 dias", "franqueado", "sem custo de mídia"),
    "nao_engatou": ("Rodar o pacote de abertura — ficha completa, primeiras 50 "
                    "avaliações, frases da cidade no leilão",
                    "60 dias", "consultor de campo", "verba de abertura"),
    "rival": ("Levar a comparação impressa com {rival} para a visita e combinar a resposta",
              "próxima visita", "consultor de campo", "sem custo de mídia"),
    "posicao": ("Auditar a ficha do Google — foto, horário, serviços, resposta a avaliação",
                "7 dias", "franqueado", "sem custo de mídia"),
    "nota": ("Ler as avaliações negativas do trimestre com o franqueado e responder todas",
             "10 dias", "consultor de campo", "sem custo de mídia"),
    "silencio": ("Entrar no leilão com as frases que a cidade digita — a lista está na praça",
                 "30 dias", "franqueado", "verba de mídia"),
}


# Como cada gatilho prova que foi resolvido. `valor` é o número que o abriu,
# `base` é contra o que ele foi comparado. Se a base mudou, a comparação não
# existe — e isso é diferente de o problema ter voltado ou continuado.
def julga_resolucao(gatilho, antes, agora, dias):
    """(resolveu?, leitura). Só devolve True quando dá para provar."""
    if dias <= 0:
        return False, ("abriu e saiu na mesma data — é releitura da mesma "
                       "rodada, não resultado")
    v0, b0 = antes.get("valor"), antes.get("base")
    if v0 is None or b0 is None:
        return False, ("o alerta é anterior ao registro do número que o abriu "
                       "— não dá para comparar")
    if not agora:
        return False, "a unidade não foi medida nesta rodada"
    v1, b1 = agora
    if v1 is None or b1 is None:
        return False, ("o número que abriu o alerta não foi medido nesta "
                       "rodada — deixou de ser visível, não de existir")

    if gatilho == "posicao":
        if b1 != b0:
            return False, (f"o ranking mudou de tamanho ({b0} → {b1} clínicas "
                           f"medidas) — a posição de hoje não se compara com a "
                           f"de antes")
        return (v1 < v0), (f"subiu de {v0}º para {v1}º entre as mesmas {b1} "
                           f"clínicas medidas" if v1 < v0 else
                           f"saiu da metade de baixo sem subir ({v0}º → {v1}º)")
    if gatilho in ("nao_engatou", "parada"):
        if b1 < b0:
            return False, ("a amostra lida encolheu — o contador de meses com "
                           "movimento não se compara")
        if b1 > b0 and v1 == v0:
            return False, ("o contador de avaliações não andou; o que cresceu "
                           "foi o quanto lemos dele")
        return (v1 > v0), (f"o contador saiu de {v0} para {v1} avaliações"
                           if v1 > v0 else
                           "o contador não andou")
    if gatilho == "nota":
        return (v1 > v0), (f"a nota subiu de {v0} para {v1}" if v1 > v0 else
                           "a nota não subiu — quem se moveu foi a mediana "
                           "da praça")
    if gatilho == "silencio":
        if b1 < LEILAO_CHEIO:
            return False, (f"o leilão esvaziou ({b0} → {b1} anunciantes) — "
                           f"não estar nele deixou de ser silêncio")
        return bool(v1), ("a rede entrou no leilão da cidade" if v1 else
                          "continua fora do leilão")
    if gatilho == "rival":
        return (v1 > v0), (f"o ritmo da unidade subiu de {v0:.1f} para "
                           f"{v1:.1f}/mês" if v1 > v0 else
                           "quem parou de correr foi o rival, não quem "
                           "acelerou foi a unidade")
    return False, "gatilho sem régua de resolução"


def monta():
    ident, linhas = coleta()
    nossas = [x for x in linhas if x["papel"] == "proprio" and x["ritmo"] is not None]
    por_praca = defaultdict(list)
    for x in linhas:
        if x["ritmo"] is not None:
            por_praca[x["praca"]].append(x)

    cap = ultimo_por("captacao")
    hoje = dt.date.today().isoformat()

    # primeira avaliação de cada clínica — é o que separa "parou" de "abriu"
    primeira = {}
    for r in reviews_unicos():
        if r.get("data"):
            k = (r.get("praca_id"), r.get("local_id"))
            d10 = str(r["data"])[:10]
            if k not in primeira or d10 < primeira[k]:
                primeira[k] = d10

    fila = []
    medidas_hoje = {}

    for u in nossas:
        vizinhos = por_praca[u["praca"]]
        # Rival nomeado é só quem disputa APARELHO. Posição e nota continuam
        # contra a praça inteira — ali a conta é de visibilidade na porta
        # ("dentista" é o que o paciente digita), não de produto.
        conc = [x for x in vizinhos if x["papel"] != "proprio" and x.get("aparelho")]
        gat, urg = [], 0

        def marca(chave, fato, fonte, extra=None):
            nonlocal urg
            g = dict(GATILHOS[chave], chave=chave, fato=fato, fonte=fonte)
            if extra:
                g.update(extra)
            gat.append(g)
            urg += GATILHOS[chave]["peso"]

        # 1 · o contador parou — ou nunca chegou a andar
        p1 = primeira.get((u["praca"], u["local_id"]))
        idade = None
        if p1:
            idade = (dt.date.fromisoformat(hoje) - dt.date.fromisoformat(p1)).days // 30
        nova = idade is not None and idade < MESES_PARA_DEIXAR_DE_SER_NOVA
        if u["meses"] < 3:
            if nova:
                marca("nao_engatou",
                      f"a primeira avaliação é de {p1}, há {idade} meses, e o ritmo "
                      f"medido é {u['ritmo']:.1f}/mês — a unidade ainda não engatou",
                      "dados/serie/reviews.jsonl",
                      {"valor": u.get("total"), "base": u["meses"]})
            else:
                marca("parada",
                      f"apenas {conta(u['meses'], 'mês', 'meses')} "
                      f"{'seguido' if u['meses'] == 1 else 'seguidos'} com "
                      f"movimento acima do típico da própria unidade; o ritmo "
                      f"medido é {u['ritmo']:.1f} avaliações/mês",
                      "dados/serie/reviews.jsonl",
                      {"valor": u.get("total"), "base": u["meses"]})

        # 2 · o rival que avança, nomeado
        mediana = st.median([x["ritmo"] for x in nossas]) if nossas else 0
        avanca = sorted([c for c in conc
                         if c["meses"] >= 10 and c["ritmo"] > max(u["ritmo"], mediana)],
                        key=lambda x: -x["ritmo"])
        rival = avanca[0] if avanca else None
        if rival:
            marca("rival",
                  f"{rival['nome']} sustenta há {rival['meses']} meses a "
                  f"{rival['ritmo']:.1f}/mês, contra {u['ritmo']:.1f}/mês desta unidade",
                  "dados/serie/reviews.jsonl",
                  {"valor": u["ritmo"], "base": rival["ritmo"]})

        # 3 · a metade de baixo da própria praça
        #
        # Loja lida pela metade não tem posição, e não ter posição não é
        # estar mal colocada: abrir alerta de "metade de baixo" para quem
        # sequer entrou no ranking seria inventar o gatilho a partir de uma
        # falha de coleta.
        if u["de"] and u["posicao"] and u["de"] > 2 and u["posicao"] > u["de"]/2:
            marca("posicao",
                  f"{u['posicao']}º lugar de {u['de']} clínicas medidas na praça",
                  "dados/portal/rede_cruzamento.json",
                  {"valor": u["posicao"], "base": u["de"]})

        # 4 · a nota
        notas = [x["nota"] for x in vizinhos if x.get("nota")]
        med_nota = st.median(notas) if notas else None
        if med_nota and u.get("nota") and med_nota - u["nota"] >= NOTA_MINIMA_DE_DIFERENCA:
            marca("nota",
                  f"nota {u['nota']} contra mediana {med_nota:.1f} das "
                  f"{len(notas)} clínicas medidas na praça",
                  "dados/serie/places.jsonl",
                  {"valor": u["nota"], "base": round(med_nota, 2)})

        # 5 · o silêncio publicitário — só quando o leilão está cheio
        c = cap.get(u["praca"]) or {}
        anun = c.get("anunciantes_ativos") or []
        if len(anun) >= LEILAO_CHEIO and not any(nosso(a) for a in anun):
            marca("silencio",
                  f"{c.get('anuncios_ativos')} anúncios no ar de {len(anun)} "
                  f"anunciantes, e nenhum é da rede",
                  "dados/serie/captacao.jsonl",
                  {"valor": 0, "base": len(anun)})

        gat.sort(key=lambda g: -g["peso"])
        urg = min(urg, 100)
        dom = gat[0]["chave"] if gat else None
        o_que, prazo, dono, custo = ACAO.get(dom, (None,)*4) if dom else (None,)*4
        if o_que and rival:
            o_que = o_que.format(rival=rival["nome"])

        nome_curto = (u["nome"] or "").replace("OrthoDontic", "").strip(" ·-–—")
        # "OrthoDontic Feira de Santana" numa praça de uma unidade só vira
        # "BA · Feira de Santana · Feira de Santana" na tela — repetir a
        # cidade ao lado dela mesma é ruído. E "Cuiabá Dom Bosco" começa
        # com a cidade: fica só o que distingue a loja ("Dom Bosco").
        cidade = (u["rotulo"] or "").split("·")[-1].strip()
        if nome_curto.lower() == cidade.lower():
            nome_curto = ""
        elif nome_curto.lower().startswith(cidade.lower() + " "):
            nome_curto = nome_curto[len(cidade):].strip(" ·-–—")
        # o número de HOJE de cada gatilho, na mesma escala em que ele foi
        # aberto. É o que permite dizer se um alerta que sumiu foi resolvido
        # ou apenas deixou de ser medido do mesmo jeito.
        medidas_hoje[u["local_id"]] = {
            "nao_engatou": (u.get("total"), u["meses"]),
            "parada":      (u.get("total"), u["meses"]),
            "rival":       (u["ritmo"], rival["ritmo"] if rival else None),
            "posicao":     (u.get("posicao"), u.get("de")),
            "nota":        (u.get("nota"), round(med_nota, 2) if med_nota else None),
            "silencio":    (1 if any(nosso(a) for a in anun) else 0, len(anun)),
        }
        fila.append({
            "local_id": u["local_id"],
            "praca_id": u["praca"],
            "rotulo": u["rotulo"],
            "unidade": u["nome"],
            # vazio quando a praça tem uma unidade só: repetir o rótulo ao lado
            # dele mesmo ("MG · Contagem · MG · Contagem") é ruído de tela.
            "unidade_curta": nome_curto or None,
            "idade_meses": idade,
            "urgencia": urg,
            "faixa": faixa(urg),
            "ritmo": u["ritmo"], "meses": u["meses"],
            "nota": u.get("nota"), "avaliacoes": u.get("total"),
            "posicao": u.get("posicao"), "de": u.get("de"),
            "quem_avanca": ({"nome": rival["nome"], "ritmo": rival["ritmo"],
                             "meses": rival["meses"], "nota": rival.get("nota"),
                             "posicao": rival.get("posicao")} if rival else None),
            "gatilhos": gat,
            "acao": ({"o_que": o_que, "prazo": prazo, "dono": dono, "custo": custo,
                      "por_causa_de": dom} if o_que else None),
        })

    fila.sort(key=lambda x: (-x["urgencia"], -(x["posicao"] or 0)))
    for i, x in enumerate(fila, 1):
        x["pos"] = i

    # ------------------------------------------------- o ciclo de vida (tarefa)
    #
    # A disciplina que veio da Salesforce: alerta não é boletim, é TAREFA com
    # dono, prazo e estado. O histórico é append-only (dados/serie/
    # fila_historico.jsonl): cada rodada grava os gatilhos abertos, e o
    # status nasce da comparação entre rodadas — ninguém preenche nada:
    #
    #   aberta     o gatilho está ativo e dentro do prazo da ação
    #   vencida    o prazo passou e o gatilho segue ativo
    #   resolvida  o gatilho sumiu numa medição nova — o dado EXTERNO
    #              fechou o loop, sem depender de ninguém confirmar
    hist = jsonl("fila_historico")
    visto = defaultdict(list)          # (local_id, gatilho) -> [registros]
    for h in hist:
        visto[(h["local_id"], h["gatilho"])].append(h)

    abertos_hoje = set()
    for x in fila:
        for g in x["gatilhos"]:
            abertos_hoje.add((x["local_id"], g["chave"]))
        dom = x["acao"]["por_causa_de"] if x["acao"] else None
        if not dom:
            x["tarefa"] = None
            continue
        datas = [r["snapshot_date"] for r in visto.get((x["local_id"], dom), [])]
        aberta_em = min(datas) if datas else hoje
        dias = (dt.date.fromisoformat(hoje) - dt.date.fromisoformat(aberta_em)).days
        prazo = PRAZO_DIAS.get(dom)
        x["tarefa"] = {
            "status": "vencida" if prazo is not None and dias > prazo else "aberta",
            "aberta_em": aberta_em, "dias_aberta": dias, "prazo_dias": prazo,
            "vence_em": ((dt.date.fromisoformat(aberta_em)
                          + dt.timedelta(days=prazo)).isoformat()
                         if prazo is not None else None),
        }

    # resolvidas: estavam no histórico e não voltaram nesta rodada.
    #
    # E "não voltou" NÃO É "resolveu". A primeira versão desta lista publicou
    # 22 vitórias num dia em que nada foi resolvido:
    #
    #   · nove abriram e fecharam na MESMA data — releitura da mesma rodada;
    #   · sete de "posição" sumiram porque o ranking mudou de tamanho quando
    #     a amostra truncada saiu da comparação: Joinville · Aventureiro
    #     saltou da metade de baixo para 1º de 15 em um dia;
    #   · seis de "não engatou" sumiram porque a varredura leu mais avaliações
    #     e o contador de meses com movimento cresceu sozinho.
    #
    # Nenhuma dessas é resultado. São mudança de método e de amostra, e
    # publicá-las como vitória é o pior defeito possível num produto cujo
    # único ativo é o ciclo alerta → ação → resultado.
    #
    # A régua agora: o gatilho só é RESOLVIDO quando (a) esteve ativo num dia
    # anterior a este, (b) a base de comparação é a mesma, e (c) o número que
    # o abriu se moveu na direção certa. Tudo o mais é descartado COM MOTIVO
    # NA TELA — "não sabemos" nunca vira "aconteceu".
    rotulos = {x["local_id"]: x["rotulo"] for x in fila}
    nomes = {x["local_id"]: x.get("unidade_curta") for x in fila}
    resolvidas, descartadas = [], []
    for (lid, g), regs in sorted(visto.items()):
        datas = [r["snapshot_date"] for r in regs]
        if (lid, g) in abertos_hoje or lid not in rotulos:
            continue
        ult = max(regs, key=lambda r: r["snapshot_date"])
        item = {
            "local_id": lid, "rotulo": rotulos[lid],
            "unidade_curta": nomes.get(lid), "gatilho": g,
            "titulo": GATILHOS.get(g, {}).get("titulo", g),
            "aberta_em": min(datas), "ultima_vez_ativa": max(datas),
            "dias": (dt.date.fromisoformat(hoje)
                     - dt.date.fromisoformat(max(datas))).days,
        }
        ok, leitura = julga_resolucao(
            g, ult, medidas_hoje.get(lid, {}).get(g), item["dias"])
        item["leitura"] = leitura
        (resolvidas if ok else descartadas).append(item)

    motivos = Counter(x["leitura"] for x in descartadas)

    vermelhas = [x for x in fila if x["faixa"] == "vermelha"]
    return {
        "gerado_em": hoje,
        "corte": max([x.get("snapshot_date", "") for x in jsonl("places")] or [hoje]),
        "pergunta": "Em quais unidades a OrthoDontic está perdendo atenção local, "
                    "para qual concorrente, e onde intervir primeiro neste mês?",
        "o_que_e_atencao": "participação observável em busca, avaliações, publicidade e "
                           "atividade digital. Não é faturamento — nenhum número desta "
                           "tela vem de dado interno da rede.",
        "unidades": len(fila),
        "em_risco": len(vermelhas),
        "manchete": (f"{len(vermelhas)} de {len(fila)} unidades medidas "
                     f"{'está' if len(vermelhas) == 1 else 'estão'} em faixa "
                     f"vermelha. A primeira é {vermelhas[0]['rotulo']}."
                     if vermelhas else
                     f"Nenhuma das {len(fila)} unidades medidas está em faixa vermelha."),
        "criterio": [{"chave": k, **v} for k, v in
                     sorted(GATILHOS.items(), key=lambda x: -x[1]["peso"])],
        "faixas": [{"de": c, "nome": n} for c, n in FAIXA],
        "fila": fila,
        "tarefas_vencidas": sum(1 for x in fila
                                if (x.get("tarefa") or {}).get("status") == "vencida"),
        "tarefas_resolvidas": resolvidas,
        "resolvidas_total": len(resolvidas),
        # O DESCARTE É A PARTE QUE SE PUBLICA. Esconder que 22 alertas
        # sumiram sem prova é o mesmo que publicá-los como vitória.
        "resolucoes_descartadas": len(descartadas),
        "porque_descartadas": [{"motivo": m, "quantas": q}
                               for m, q in motivos.most_common()],
        "frase_resolvidas": (
            f"{conta(len(resolvidas), 'alerta fechado com prova', 'alertas fechados com prova')}"
            + (f" · {conta(len(descartadas), 'sumiu', 'sumiram')} sem prova "
               f"de resultado" if descartadas else "")),
        "o_que_conta_como_resolvido": (
            "o alerta esteve ativo num dia anterior, a base de comparação é a "
            "mesma, e o número que o abriu se moveu na direção certa. Sumir "
            "da lista não basta — ranking que muda de tamanho e amostra que "
            "engorda fazem alerta sumir sem nada ter melhorado."),
        "o_que_isso_nao_ve": [
            f"A rede tem 374 unidades e esta fila mede {len(fila)}. É "
            f"{100*len(fila)//374}% da rede.",
            "Nenhum contrato, lead, agendamento ou receita entra aqui. A fila diz "
            "onde a atenção está escorrendo, não quanto isso custou.",
            "O status da tarefa (aberta → vencida → resolvida) vem do próprio "
            "dado: 'resolvida' é gatilho que sumiu na medição seguinte. Ninguém "
            "de dentro confirma nada — e é por isso que vale.",
        ],
    }


def imprime(d):
    print(f"\n{'='*78}\n  A FILA DE INTERVENÇÃO — {d['gerado_em']}\n{'='*78}")
    print(f"\n  {d['pergunta']}\n")
    print(f"  {d['manchete']}\n")
    for x in d["fila"]:
        cor = {"vermelha": "🔴", "amarela": "🟡", "verde": "🟢"}[x["faixa"]]
        et = x["rotulo"] + (f" · {x['unidade_curta']}" if x["unidade_curta"] else "")
        print(f"  {x['pos']:>2d}. {cor} {x['urgencia']:>3d}  {et}")
        for g in x["gatilhos"]:
            print(f"          · {g['titulo']}: {g['fato']}")
        if x["acao"]:
            a = x["acao"]
            print(f"       → {a['o_que']}")
            print(f"         {a['prazo']} · {a['dono']} · {a['custo']}")
        print()
    print("  O QUE ISSO NÃO VÊ")
    for l in d["o_que_isso_nao_ve"]:
        print(f"  · {l}")
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()
    d = monta()
    imprime(d)
    if a.salvar:
        PORTAL.mkdir(parents=True, exist_ok=True)
        (PORTAL/"fila.json").write_text(json.dumps(d, ensure_ascii=False, indent=1),
                                        encoding="utf-8")
        print(f"  → dados/portal/fila.json  ({len(d['fila'])} unidades)")
        # o histórico que dá vida ao status: grava os gatilhos abertos de hoje
        # (append-only; rodar duas vezes no dia não duplica)
        ja = {(h["local_id"], h["gatilho"]) for h in jsonl("fila_historico")
              if h["snapshot_date"] == d["gerado_em"]}
        n = 0
        with (SERIE/"fila_historico.jsonl").open("a", encoding="utf-8") as f:
            for x in d["fila"]:
                for g in x["gatilhos"]:
                    if (x["local_id"], g["chave"]) in ja:
                        continue
                    f.write(json.dumps(
                        {"snapshot_date": d["gerado_em"],
                         "local_id": x["local_id"], "praca_id": x["praca_id"],
                         "gatilho": g["chave"], "fato": g["fato"],
                         # o número que abriu o alerta e a base contra a qual
                         # ele foi comparado — sem os dois, "resolveu" é
                         # palpite (ver julga_resolucao)
                         "valor": g.get("valor"), "base": g.get("base")},
                        ensure_ascii=False) + "\n")
                    n += 1
        print(f"  → dados/serie/fila_historico.jsonl (+{n})\n")


if __name__ == "__main__":
    main()
