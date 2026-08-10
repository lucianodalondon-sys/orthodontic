#!/usr/bin/env python3
"""
o_que_mudou.py — o movimento entre a penúltima e a última medição.

É a resposta à pergunta que decide se o produto sobrevive ao terceiro mês:
"o que mudou desde a última vez?". Fotografia se encomenda uma vez;
movimento se assina.

Como se lê
----------
Para cada ficha (nossa e rival), compara as duas últimas medições do
contador do Google:

  ganhou N    o contador subiu — N avaliações novas no período
  perdeu N    o contador CAIU — avaliação removida ou moderada. Não é ruído:
              queda de contador é evento raro e vale investigação
  nota ±x     a nota mudou
  fechou      a ficha saiu de OPERATIONAL

O ritmo aqui é o do PERÍODO (novas ÷ dias), não o da vida inteira — os dois
convivem: o da vida mede constância, o do período mede agora.

Honestidade do delta: cada praça carrega os dias medidos. Um delta de 2 dias
diz pouco e a tela é obrigada a dizer isso; o de 26 dias já é leitura.

Uso:
    python3 scripts/o_que_mudou.py
    python3 scripts/o_que_mudou.py --salvar   # → dados/portal/o_que_mudou.json
                                              #   e injeta nas fichas de praça
"""
import argparse, json, pathlib, sys
import datetime as dt
from collections import defaultdict

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ/"scripts"))
from cruzamento import jsonl, identidades, disputa_aparelho, conta

PORTAL = RAIZ/"dados"/"portal"


def monta():
    ident = identidades(com_unidade=False)
    nomes = {l["local_id"]: (p, d.get("rotulo"), l.get("nome"),
                             l.get("papel") == "proprio", disputa_aparelho(l))
             for p, d in ident.items() for l in d.get("locais", [])}

    # O total mora em DOIS nomes de campo: `avaliacoes_total` num coletor e
    # `avaliacoes` no outro — a mesma família de bug da chave das avaliações.
    # Sem normalizar, Cuiabá inteira (29 fichas) saía do movimento calada.
    por = defaultdict(dict)
    for x in jsonl("places"):
        tot = x.get("avaliacoes_total")
        if tot is None:
            tot = x.get("avaliacoes")
        if tot is None:
            continue
        x = dict(x, avaliacoes_total=tot)
        por[x["local_id"]][x["snapshot_date"]] = x

    pracas = defaultdict(lambda: {"linhas": [], "dias": set()})
    for lid, snaps in por.items():
        if lid not in nomes or len(snaps) < 2:
            continue
        ds = sorted(snaps)
        a, b = snaps[ds[-2]], snaps[ds[-1]]
        dias = max((dt.date.fromisoformat(ds[-1]) -
                    dt.date.fromisoformat(ds[-2])).days, 1)
        # O delta curto compara as DUAS ÚLTIMAS medições — é o que a semana
        # mudou. Mas quatro praças (Mafra, Londrina, Feira, Prudente) são
        # medidas desde 15/jul, e comparar só as duas últimas apagava esse
        # histórico: a tela chamava de "período de só 3 dias" justamente as
        # praças com mais tempo de medição. O período inteiro vai junto.
        primeiro = snaps[ds[0]]
        dias_hist = max((dt.date.fromisoformat(ds[-1]) -
                         dt.date.fromisoformat(ds[0])).days, 1)
        delta_hist = ((b["avaliacoes_total"] or 0) -
                      (primeiro["avaliacoes_total"] or 0))
        historico = {
            "desde": ds[0], "ate": ds[-1], "dias": dias_hist,
            "medicoes": len(ds),
            "antes": primeiro["avaliacoes_total"],
            "agora": b["avaliacoes_total"],
            "delta": delta_hist,
            "ritmo_do_periodo": (round(delta_hist/(dias_hist/30.4), 1)
                                 if delta_hist > 0 else 0.0),
            "nota_antes": primeiro.get("nota"), "nota_agora": b.get("nota"),
        }
        delta = (b["avaliacoes_total"] or 0) - (a["avaliacoes_total"] or 0)
        dnota = round((b.get("nota") or 0) - (a.get("nota") or 0), 1)
        p, rotulo, nome, proprio, aparelho = nomes[lid]
        ev = []
        if delta > 0:
            ev.append(f"ganhou {conta(delta, 'avaliação', 'avaliações')} "
                      f"em {conta(dias, 'dia')}")
        elif delta < 0:
            ev.append(f"o contador CAIU {-delta} — avaliação removida")
        if dnota:
            ev.append(f"nota foi de {a.get('nota')} para {b.get('nota')}")
        if b.get("situacao_google") and b["situacao_google"] != "OPERATIONAL":
            ev.append(f"a ficha saiu do ar: {b['situacao_google']}")
        pracas[p]["rotulo"] = rotulo
        pracas[p]["dias"].add(dias)
        pracas[p]["linhas"].append({
            "local_id": lid, "nome": nome, "proprio": proprio,
            "aparelho": aparelho,
            "de": ds[-2], "ate": ds[-1], "dias": dias,
            "antes": a["avaliacoes_total"], "agora": b["avaliacoes_total"],
            "delta": delta, "nota_antes": a.get("nota"), "nota_agora": b.get("nota"),
            "ritmo_do_periodo": round(delta/(dias/30.4), 1) if delta > 0 else 0.0,
            "historico": historico,
            "eventos": ev,
        })

    fora = {}
    for p, d in pracas.items():
        linhas = sorted(d["linhas"], key=lambda x: -abs(x["delta"]))
        nossos = [x for x in linhas if x["proprio"]]
        quedas = [x for x in linhas if x["delta"] < 0]
        dias = max(d["dias"]) if d["dias"] else 0
        hs = [x["historico"] for x in linhas if x.get("historico")]
        desde = min((h["desde"] for h in hs), default=None)
        dias_hist = max((h["dias"] for h in hs), default=0)
        medicoes = max((h["medicoes"] for h in hs), default=0)
        fora[p] = {
            "praca_id": p, "rotulo": d["rotulo"], "dias_medidos": dias,
            # o que a praça tem de histórico, que não é a janela do delta
            "medida_desde": desde,
            "dias_de_historico": dias_hist,
            "medicoes": medicoes,
            "janela_do_delta": (f"o delta compara as duas últimas medições "
                                f"({conta(dias, 'dia')})"),
            # O aviso é sobre o HISTÓRICO da praça, não sobre a janela curta.
            # Antes ele dizia "período de só 3 dias" para praça medida desde
            # 15/jul — a mais medida da rede aparecia como a menos medida.
            "aviso": (f"a praça é medida há {conta(dias_hist, 'dia')} "
                      f"({conta(medicoes, 'medição', 'medições')}) — a leitura "
                      f"ainda diz pouco e engorda a cada coleta"
                      if dias_hist < 14 else None),
            "nossas": nossos,
            # Destaque de confronto é só entre quem disputa APARELHO — a
            # clínica geral que ganhou avaliações é movimento da rua, não
            # ameaça ao produto. Ela segue nas `linhas`, marcada.
            "quem_mais_ganhou": [x for x in linhas
                                 if x["delta"] > 0 and x["aparelho"]][:5],
            "contador_caiu": quedas,
            "linhas": linhas,
        }
    return fora


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()
    fora = monta()

    print(f"\n{'='*78}\n  O QUE MUDOU — penúltima medição → última\n{'='*78}")
    for p, d in sorted(fora.items()):
        print(f"\n  {d['rotulo']}  ({d['dias_medidos']} dia(s) medidos)"
              + ("  ⚠ " + d["aviso"] if d["aviso"] else ""))
        for x in d["nossas"]:
            seta = "▲" if x["delta"] > 0 else ("▼" if x["delta"] < 0 else "·")
            print(f"    {seta} NOSSA {(x['nome'] or '')[:36]:36s} "
                  f"{x['antes']} → {x['agora']}  ({x['delta']:+d})")
        for x in d["quem_mais_ganhou"][:2]:
            if not x["proprio"]:
                print(f"    ▲ rival {(x['nome'] or '')[:36]:36s} "
                      f"{x['antes']} → {x['agora']}  (+{x['delta']})")
        for x in d["contador_caiu"]:
            print(f"    ▼ QUEDA {(x['nome'] or '')[:36]:36s} "
                  f"{x['antes']} → {x['agora']}  ({x['delta']})")

    if a.salvar:
        (PORTAL/"o_que_mudou.json").write_text(json.dumps({
            "o_que_e": "O movimento entre a penúltima e a última medição do "
                       "contador público, ficha a ficha.",
            "como_ler": "ganhou = avaliações novas · o contador CAIU = avaliação "
                        "removida, evento raro que vale investigação · o ritmo é "
                        "do período, não da vida.",
            "pracas": fora}, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n  → dados/portal/o_que_mudou.json ({len(fora)} praças)")
        # injeta o bloco na ficha de cada praça publicada
        n = 0
        for p, d in fora.items():
            arq = PORTAL/"pracas"/f"{p}.json"
            if not arq.exists():
                continue
            ficha = json.loads(arq.read_text(encoding="utf-8"))
            ficha["o_que_mudou"] = {"dias_medidos": d["dias_medidos"],
                                    "aviso": d["aviso"], "nossas": d["nossas"],
                                    "quem_mais_ganhou": d["quem_mais_ganhou"],
                                    "contador_caiu": d["contador_caiu"]}
            arq.write_text(json.dumps(ficha, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
            n += 1
        print(f"  → o_que_mudou injetado em {n} fichas de praça")


if __name__ == "__main__":
    main()
