#!/usr/bin/env python3
"""
timeline_da_loja.py — a vida de cada loja, em ordem, num lugar só.

A ideia veio da "activity timeline" da Salesforce: a página da conta mostra
tudo que aconteceu com aquele cliente numa linha do tempo única. Aqui a
conta é a LOJA (a unidade é a menor conta, e loja não se funde com loja),
e os eventos são os OBSERVÁVEIS — nada de dado interno:

  · avaliação negativa chegou (com o trecho, e se foi respondida)
  · o contador subiu / CAIU (queda é avaliação apagada, evento raro)
  · a nota mudou · a ficha saiu do ar
  · alerta da fila abriu / venceu / resolveu (do histórico da fila)
  · rival de APARELHO da praça se moveu — só quem disputa o produto;
    clínica geral ganhando avaliação é movimento da rua, não evento

Uso:
    python3 scripts/timeline_da_loja.py
    python3 scripts/timeline_da_loja.py --salvar   # → dados/portal/timeline.json
"""
import argparse, datetime as dt, json, pathlib, sys
from collections import defaultdict

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ/"scripts"))
from cruzamento import coleta, jsonl, reviews_unicos, disputa_aparelho, conta

PORTAL = RAIZ/"dados"/"portal"

DIAS_DE_JANELA = 90     # avaliação mais velha que isso é acervo, não evento
MAX_EVENTOS = 40        # timeline é leitura, não é dump

GATILHO_TITULO = {
    "parada": "O contador de avaliações parou",
    "nao_engatou": "Unidade nova que ainda não engatou",
    "rival": "Um rival de aparelho sustenta e corre mais",
    "posicao": "Está na metade de baixo da própria praça",
    "nota": "Nota abaixo da mediana da praça",
    "silencio": "Silêncio publicitário com leilão cheio",
}


def eventos_de_places(rows_por_ficha):
    """Pares consecutivos de medição → eventos de contador/nota/situação."""
    fora = defaultdict(list)
    for (praca, lid), snaps in rows_por_ficha.items():
        ds = sorted(snaps)
        for a_d, b_d in zip(ds, ds[1:]):
            a, b = snaps[a_d], snaps[b_d]
            delta = (b.get("avaliacoes_total") or 0) - (a.get("avaliacoes_total") or 0)
            dnota = round((b.get("nota") or 0) - (a.get("nota") or 0), 1)
            if delta > 0:
                fora[(praca, lid)].append((b_d, "contador",
                    f"ganhou {conta(delta, 'avaliação', 'avaliações')} "
                    f"({a['avaliacoes_total']} → {b['avaliacoes_total']})"))
            elif delta < 0:
                fora[(praca, lid)].append((b_d, "queda",
                    f"o contador CAIU {-delta} ({a['avaliacoes_total']} → "
                    f"{b['avaliacoes_total']}) — avaliação apagada"))
            if dnota:
                fora[(praca, lid)].append((b_d, "nota",
                    f"a nota foi de {a.get('nota')} para {b.get('nota')}"))
            if (b.get("situacao_google") or "OPERATIONAL") != "OPERATIONAL":
                fora[(praca, lid)].append((b_d, "fechou",
                    f"a ficha saiu do ar: {b['situacao_google']}"))
    return fora


def monta():
    ident, linhas = coleta()
    hoje = dt.date.today()
    corte_rev = (hoje - dt.timedelta(days=DIAS_DE_JANELA)).isoformat()

    # medições agrupadas por ficha, uma por dia (a última do dia vale)
    por_ficha = defaultdict(dict)
    for x in jsonl("places"):
        tot = x.get("avaliacoes_total")
        if tot is None:
            tot = x.get("avaliacoes")
        if tot is None:
            continue
        por_ficha[(x.get("praca_id"), x["local_id"])][x["snapshot_date"]] = \
            dict(x, avaliacoes_total=tot)
    ev_places = eventos_de_places(por_ficha)

    # avaliações negativas recentes das NOSSAS lojas
    negativas = defaultdict(list)
    for r in reviews_unicos():
        d10 = str(r.get("data") or "")[:10]
        try:
            nota = float(r.get("nota"))
        except (TypeError, ValueError):
            continue
        if nota <= 3 and d10 >= corte_rev:
            negativas[(r.get("praca_id"), r.get("local_id"))].append(
                dict(r, nota=int(nota)))

    # histórico da fila: primeira vez de cada gatilho é um evento
    fila_hist = defaultdict(list)
    for h in jsonl("fila_historico"):
        fila_hist[(h["local_id"], h["gatilho"])].append(h["snapshot_date"])

    # a fila publicada dá o estado atual da tarefa
    fila_pub = {}
    arq = PORTAL/"fila.json"
    if arq.exists():
        for x in json.loads(arq.read_text(encoding="utf-8")).get("fila", []):
            fila_pub[x["local_id"]] = x

    # a caixa dá o saldo de sem-resposta
    caixa = {}
    arq = PORTAL/"caixa_de_respostas.json"
    if arq.exists():
        for u in json.loads(arq.read_text(encoding="utf-8")).get("unidades", []):
            caixa[u.get("local_id")] = u

    rivais_da_praca = defaultdict(list)   # praca -> [(lid, nome)] só aparelho
    nomes = {}
    for p, d in ident.items():
        for l in d.get("locais", []):
            nomes[(p, l["local_id"])] = l.get("nome")
            if l.get("papel") != "proprio" and disputa_aparelho(l):
                rivais_da_praca[p].append(l["local_id"])

    lojas = []
    for u in [x for x in linhas if x["papel"] == "proprio"]:
        p, lid = u["praca"], u["local_id"]
        ev = []
        for d10, tipo, txt in ev_places.get((p, lid), []):
            ev.append({"data": d10, "tipo": tipo, "quem": "nossa",
                       "texto": txt, "fonte": "dados/serie/places.jsonl"})
        for r in negativas.get((p, lid), []):
            trecho = (r.get("texto") or "").strip().replace("\n", " ")
            ev.append({"data": str(r["data"])[:10], "tipo": "avaliacao_negativa",
                       "quem": "paciente",
                       "texto": (f"avaliação de {r['nota']}★"
                                 + (f": “{trecho[:90]}…”" if len(trecho) > 90
                                    else (f": “{trecho}”" if trecho else ""))
                                 + (" · respondida" if r.get("respondida")
                                    else " · SEM RESPOSTA")),
                       "fonte": "dados/serie/reviews.jsonl"})
        for (hl, g), datas in fila_hist.items():
            if hl != lid:
                continue
            ev.append({"data": min(datas), "tipo": "alerta",
                       "quem": "fila",
                       "texto": f"alerta aberto: {GATILHO_TITULO.get(g, g)}",
                       "fonte": "dados/serie/fila_historico.jsonl"})
        for rl in rivais_da_praca.get(p, []):
            for d10, tipo, txt in ev_places.get((p, rl), []):
                if tipo in ("contador", "queda", "fechou"):
                    ev.append({"data": d10, "tipo": f"rival_{tipo}",
                               "quem": "rival", "nome": nomes.get((p, rl)),
                               "texto": f"{nomes.get((p, rl))}: {txt}",
                               "fonte": "dados/serie/places.jsonl"})

        ev.sort(key=lambda e: e["data"], reverse=True)
        cx = caixa.get(lid) or {}
        fp = fila_pub.get(lid) or {}
        lojas.append({
            "local_id": lid, "praca_id": p, "rotulo": u["rotulo"],
            "unidade": u["nome"],
            "cabecalho": {"nota": u.get("nota"), "avaliacoes": u.get("total"),
                          "ritmo": u.get("ritmo"), "meses_seguidos": u.get("meses"),
                          "posicao": u.get("posicao"), "de": u.get("de"),
                          # A TELA PRECISA DIZER DE QUANTO SAIU O RITMO.
                          # Uma loja lida pela metade tem ritmo dos últimos
                          # dias, não do histórico, e não entra na
                          # classificação da praça — mas o número continua
                          # aparecendo, então ele vai acompanhado do que é.
                          "amostra_lida": u.get("amostra_lida"),
                          "amostra_dias": u.get("amostra_dias"),
                          "amostra_truncada": u.get("amostra_truncada"),
                          "ritmo_comparavel": u.get("ritmo_comparavel"),
                          "porque_fora_do_ranking": u.get("porque_fora_do_ranking")},
            "tarefa": fp.get("tarefa"),
            "acao": fp.get("acao"),
            "faixa": fp.get("faixa"),
            "sem_resposta": {"abertas": cx.get("abertas"),
                             "com_texto": cx.get("com_texto")} if cx else None,
            "eventos": ev[:MAX_EVENTOS],
            "eventos_alem_da_janela": max(len(ev) - MAX_EVENTOS, 0),
        })

    lojas.sort(key=lambda l: (l["rotulo"] or "", l["local_id"]))
    return {
        "o_que_e": "A linha do tempo de cada loja: tudo que aconteceu de "
                   "observável, em ordem, num lugar só — avaliações, "
                   "contadores, alertas e os rivais de aparelho da praça.",
        "como_ler": "Cada evento tem data, fonte e de quem é (nossa · paciente "
                    "· fila · rival). Rival aqui é só quem disputa APARELHO. "
                    f"Avaliações entram na janela de {DIAS_DE_JANELA} dias; "
                    "medições e alertas entram inteiros.",
        "lojas": lojas,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()
    d = monta()

    print(f"\n{'='*78}\n  A VIDA DE CADA LOJA — timeline\n{'='*78}")
    for l in d["lojas"]:
        c = l["cabecalho"]
        print(f"\n  {l['rotulo']} · {l['unidade']}")
        print(f"    nota {c['nota']} · {c['avaliacoes']} avaliações · "
              f"{c['ritmo']}/mês · {c['posicao']}º de {c['de']}"
              + (f" · tarefa {l['tarefa']['status']}" if l.get("tarefa") else ""))
        for e in l["eventos"][:6]:
            print(f"    {e['data']}  [{e['quem']:8s}] {e['texto'][:74]}")
        resto = len(l["eventos"]) - 6
        if resto > 0:
            print(f"    … +{resto} eventos")

    if a.salvar:
        (PORTAL/"timeline.json").write_text(
            json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        tot = sum(len(l["eventos"]) for l in d["lojas"])
        print(f"\n  → dados/portal/timeline.json "
              f"({len(d['lojas'])} lojas · {tot} eventos)")


if __name__ == "__main__":
    main()
