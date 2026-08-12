#!/usr/bin/env python3
"""
livro_de_acoes.py — o ciclo inteiro: problema → ação → medição → veredito.

ESTE É O ÚNICO ATIVO QUE NINGUÉM COPIA COLETANDO GOOGLE.

Qualquer concorrente consegue as avaliações, as fichas e os anúncios. O
que ele não tem é o histórico do que a OrthoDontic FEZ depois de ver o
problema, e o que aconteceu com a medição em seguida. Em um ano isso
permite frases que hoje ninguém no mercado consegue dizer:

    "Retomar o pedido de avaliação funcionou em 12 das 15 unidades onde
     tentamos, e em nenhuma das 3 que já tinham nota acima de 4,8."

O buraco que ele fecha: o portal gerava alerta e ação, e nunca media o
depois. `fila_historico.jsonl` já guardava o problema com data — faltava
o outro lado do arco.

COMO O LIVRO FUNCIONA

Cada linha é um ARCO, identificado por `arco_id = local_id|gatilho`.
Ele nasce quando a fila acusa o problema pela primeira vez e recebe a
medição de referência daquele dia (o "antes"). A cada nova coleta o
script confere: o gatilho ainda está aberto? A métrica mudou?

O veredito NUNCA é opinião:

    resolvido       o gatilho sumiu da fila e a métrica melhorou
    melhorou        a métrica melhorou, o gatilho continua aberto
    sem_mudanca     dentro da margem — e a margem é declarada
    piorou          a métrica caiu
    cedo_demais     menos de MIN_DIAS entre o antes e o agora

O QUE ESTE SCRIPT NÃO AFIRMA

· Não diz que a ação CAUSOU o resultado. Não temos grupo de controle e
  não temos dado interno; o que se registra é "o que fizemos" e "o que a
  medição mostrou depois". Correlação declarada como correlação.
· Não sabe se o franqueado executou. Ninguém de dentro preenche nada
  neste projeto. Por isso o campo é `acao_recomendada`, e a execução
  aparece como `execucao: "não sabemos"` até que exista sinal externo.

Uso:
    python3 scripts/livro_de_acoes.py
    python3 scripts/livro_de_acoes.py --salvar
"""
import argparse, json, pathlib, sys
import datetime as dt
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from cruzamento import conta

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SERIE = RAIZ/"dados"/"serie"
LIVRO = SERIE/"acoes.jsonl"
SAIDA = RAIZ/"dados"/"portal"/"acoes.json"

MIN_DIAS = 21           # antes disso, medir de novo não diz nada
MARGEM = {              # o que conta como mudança de verdade, por métrica
    "nota": 0.15,
    "ritmo": 0.30,
    "avaliacoes": 3,
    "posicao": 1,
}

# Cada gatilho tem a métrica que o mede e a ação que o portal recomenda.
# A ação é a MESMA que a fila já mostra — o livro não inventa outra.
GATILHOS = {
    "parada": ("ritmo", "retomar o pedido de avaliação ao fim do atendimento"),
    "nota": ("nota", "responder as avaliações abertas e tratar o motivo"),
    "posicao": ("posicao", "trabalhar ficha e presença na busca da cidade"),
    "sem_resposta": ("avaliacoes", "responder a caixa de avaliações"),
    "invisivel": ("posicao", "corrigir a ficha e as categorias do Google"),
}


def linhas(p):
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").split("\n")
            if l.strip()]


def metrica_de(item, qual):
    v = item.get(qual)
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def melhor(qual, antes, agora):
    """+1 melhorou, -1 piorou, 0 dentro da margem. None sem medida."""
    if antes is None or agora is None:
        return None
    d = agora - antes
    m = MARGEM.get(qual, 0)
    if abs(d) < m:
        return 0
    # posição é o único onde MENOR é melhor
    if qual == "posicao":
        return 1 if d < 0 else -1
    return 1 if d > 0 else -1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()
    hoje = dt.date.today()

    fila = json.loads((RAIZ/"dados"/"portal"/"fila.json").read_text(encoding="utf-8"))
    agora = {x["local_id"]: x for x in fila.get("fila", [])}
    historico = linhas(SERIE/"fila_historico.jsonl")
    livro = {r["arco_id"]: r for r in linhas(LIVRO)}

    # 1 · abre um arco para cada (loja, gatilho) que já apareceu na fila
    vistos = defaultdict(list)
    for r in sorted(historico, key=lambda r: r.get("snapshot_date", "")):
        vistos[(r["local_id"], r["gatilho"])].append(r)

    novos, fechados, atualizados = 0, 0, 0
    for (lid, gat), ocorrencias in sorted(vistos.items()):
        arco_id = f"{lid}|{gat}"
        primeira = ocorrencias[0]
        qual, acao = GATILHOS.get(gat, (None, "sem ação padrão para este gatilho"))
        item_hoje = agora.get(lid) or {}

        if arco_id not in livro:
            livro[arco_id] = {
                "arco_id": arco_id, "local_id": lid,
                "praca_id": primeira.get("praca_id"),
                "gatilho": gat,
                "problema": primeira.get("fato"),
                "evidencia": "dados/serie/fila_historico.jsonl",
                "aberto_em": primeira["snapshot_date"],
                "metrica": qual,
                # RESSALVA HONESTA: o "antes" sai da fila de HOJE, não do dia
                # em que o problema abriu — `fila_historico` guarda o gatilho e
                # o fato, não a métrica. Para os arcos que nascem junto com o
                # livro a diferença é de um dia; para os próximos, o antes será
                # o do dia da abertura, porque o arco passa a ser criado no
                # mesmo instante em que o gatilho aparece.
                "antes": metrica_de(item_hoje, qual) if item_hoje else None,
                "antes_ressalva": ("medido no dia em que o arco foi criado, "
                                   "não no dia em que o problema começou"),
                "acao_recomendada": acao,
                "execucao": "não sabemos — o portal não fala com a unidade",
                "depois": None, "medido_em": None,
                "veredito": "aberto", "dias": 0,
            }
            novos += 1
            continue

        arco = livro[arco_id]
        # o gatilho ainda está na fila de hoje?
        gatilhos_hoje = {g.get("tipo") or g.get("gatilho")
                         for g in (item_hoje.get("gatilhos") or [])}
        segue_aberto = gat in gatilhos_hoje
        depois = metrica_de(item_hoje, qual)
        dias = (dt.date.fromisoformat(hoje.isoformat())
                - dt.date.fromisoformat(arco["aberto_em"])).days
        arco["depois"] = depois
        arco["medido_em"] = hoje.isoformat()
        arco["dias"] = dias

        if dias < MIN_DIAS:
            arco["veredito"] = "cedo_demais"
        else:
            sinal = melhor(qual, arco.get("antes"), depois)
            if sinal is None:
                arco["veredito"] = "sem_medida"
            elif not segue_aberto and sinal >= 0:
                arco["veredito"] = "resolvido"
                fechados += 1
            elif sinal > 0:
                arco["veredito"] = "melhorou"
            elif sinal < 0:
                arco["veredito"] = "piorou"
            else:
                arco["veredito"] = "sem_mudanca"
        atualizados += 1

    arcos = sorted(livro.values(), key=lambda r: (r["veredito"], r["arco_id"]))
    por_veredito = defaultdict(int)
    for r in arcos:
        por_veredito[r["veredito"]] += 1

    print(f"  {conta(len(arcos), 'arco')} no livro "
          f"· {novos} aberto(s) agora · {atualizados} atualizado(s)")
    for v, q in sorted(por_veredito.items(), key=lambda x: -x[1]):
        print(f"    {v:<14}{q}")
    cedo = por_veredito.get("cedo_demais", 0) + por_veredito.get("aberto", 0)
    if cedo == len(arcos):
        print(f"\n  Nenhum arco tem {MIN_DIAS} dias ainda — o livro só começa "
              f"a responder na coleta que passar dessa distância.")

    if not a.salvar:
        print("\n  (--salvar para gravar)")
        return

    with LIVRO.open("w", encoding="utf-8") as f:
        for r in arcos:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    SAIDA.write_text(json.dumps({
        "o_que_e": "O ciclo inteiro de cada problema: o que a medição "
                   "acusou, o que recomendamos, e o que a medição mostrou "
                   "depois.",
        "o_que_nao_e": "Não é prova de causa. Não há grupo de controle e "
                       "ninguém de dentro confirma o que foi executado — o "
                       "livro registra o que fizemos e o que a medição "
                       "mostrou em seguida.",
        "por_que_importa": "Qualquer concorrente coleta o Google. Nenhum tem "
                           "o histórico do que a rede fez depois.",
        "medido_em": hoje.isoformat(),
        "minimo_de_dias": MIN_DIAS,
        "margem_por_metrica": MARGEM,
        "arcos_total": len(arcos),
        "o_que_falta_para_valer": (
            "duas coisas: distância no tempo (a primeira resposta vem na "
            "coleta seguinte) e volume (com 16 arcos não se aprende padrão "
            "de rede; com 200 sim)"),
        "por_veredito": dict(por_veredito),
        "manchete": (
            f"{conta(len(arcos), 'problema acompanhado', 'problemas acompanhados')}"
            f" · {por_veredito.get('resolvido', 0)} resolvidos, "
            f"{por_veredito.get('melhorou', 0)} melhoraram, "
            f"{por_veredito.get('piorou', 0)} pioraram"),
        "aviso_de_juventude": (
            f"O livro nasceu hoje. Nenhum arco completou {MIN_DIAS} dias, "
            f"então ainda não há veredito para ninguém — a primeira "
            f"resposta vem na coleta seguinte."
            if cedo == len(arcos) else None),
        "arcos": arcos,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n  → {LIVRO.relative_to(RAIZ)} e {SAIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
