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
from cruzamento import jsonl, identidades

PORTAL = RAIZ/"dados"/"portal"


def monta():
    ident = identidades(com_unidade=False)
    nomes = {l["local_id"]: (p, d.get("rotulo"), l.get("nome"),
                             l.get("papel") == "proprio")
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
        delta = (b["avaliacoes_total"] or 0) - (a["avaliacoes_total"] or 0)
        dnota = round((b.get("nota") or 0) - (a.get("nota") or 0), 1)
        p, rotulo, nome, proprio = nomes[lid]
        ev = []
        if delta > 0:
            ev.append(f"ganhou {delta} avaliações em {dias} dia(s)")
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
            "de": ds[-2], "ate": ds[-1], "dias": dias,
            "antes": a["avaliacoes_total"], "agora": b["avaliacoes_total"],
            "delta": delta, "nota_antes": a.get("nota"), "nota_agora": b.get("nota"),
            "ritmo_do_periodo": round(delta/(dias/30.4), 1) if delta > 0 else 0.0,
            "eventos": ev,
        })

    fora = {}
    for p, d in pracas.items():
        linhas = sorted(d["linhas"], key=lambda x: -abs(x["delta"]))
        nossos = [x for x in linhas if x["proprio"]]
        quedas = [x for x in linhas if x["delta"] < 0]
        dias = max(d["dias"]) if d["dias"] else 0
        fora[p] = {
            "praca_id": p, "rotulo": d["rotulo"], "dias_medidos": dias,
            "aviso": (f"período de só {dias} dia(s) — o delta ainda diz pouco; "
                      f"a leitura engorda a cada medição"
                      if dias < 14 else None),
            "nossas": nossos,
            "quem_mais_ganhou": [x for x in linhas if x["delta"] > 0][:5],
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
