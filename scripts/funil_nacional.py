#!/usr/bin/env python3
"""
funil_nacional.py — as melhores cidades do Brasil ANTES de gastar coleta.

A ideia veio do fluxo da GeoFusion para expansão de franquia: primeiro uma
régua barata sobre todos os municípios, depois o estudo caro só em quem
passa. Hoje o Radar estuda 6 cidades a fundo e não diz nada sobre as
outras ~5.560 — este funil é a resposta para "por que ESSAS seis?".

Duas leituras, as duas com a rede como benchmark:

1 · AS CANDIDATAS — municípios sem unidade na lista oficial, dentro da
    faixa de tamanho onde a rede já prospera, ordenados por
    alvo × renda relativa:
      alvo           = alvo 9-15 (quem usa) + alvo 30-45 (quem paga)
      renda relativa = massa salarial per capita ÷ mediana nacional
    Nada de "potencial de consumo" proprietário: população, idade e massa
    salarial do IBGE carregam o grosso do sinal para UM produto.

2 · ONDE CABEM MAIS — a proporção habitantes/unidade das cidades onde a
    rede JÁ opera, por faixa de cidade, aplicada de volta: cidade nossa
    com folga de 2+ unidades é expansão dentro de casa (white space
    interno), sem estudo novo.

O que isto NÃO é: promessa de faturamento. É régua de PRIORIDADE — quem
passa no funil ganha o estudo profundo (radar), que aí sim confere
concorrência, canais e busca com duas fontes.

Uso:
    python3 scripts/funil_nacional.py
    python3 scripts/funil_nacional.py --salvar   # → dados/portal/funil_nacional.json
"""
import argparse, json, pathlib, re, statistics as st, sys, unicodedata
from collections import Counter, defaultdict

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ/"scripts"))
from cruzamento import jsonl

PORTAL = RAIZ/"dados"/"portal"

TOP = 50
FAIXAS_DE_CIDADE = [(0, 50_000, "até 50 mil"),
                    (50_000, 100_000, "50–100 mil"),
                    (100_000, 200_000, "100–200 mil"),
                    (200_000, 500_000, "200–500 mil"),
                    (500_000, 1_000_000, "500 mil–1 mi"),
                    (1_000_000, 10**9, "acima de 1 mi")]

# as 6 que o Radar já estudou a fundo — o funil marca, não repete o estudo
JA_ESTUDADAS = {"macapa", "maraba", "parauapebas", "imperatriz",
                "juazeiro_do_norte", "rio_branco"}


def norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


def faixa_de(pop):
    for a, b, nome in FAIXAS_DE_CIDADE:
        if a <= pop < b:
            return nome
    return FAIXAS_DE_CIDADE[-1][2]


def monta():
    # IBGE: a foto mais recente de cada município
    ibge = {}
    for x in jsonl("ibge_municipios"):
        k = x["ibge_id"]
        if k not in ibge or x["snapshot_date"] >= ibge[k]["snapshot_date"]:
            ibge[k] = x
    if not ibge:
        sys.exit("dados/serie/ibge_municipios.jsonl vazio — rode "
                 "coleta/coletores/ibge_nacional.py --salvar")
    por_nome = {(norm(x["municipio"]), x["uf"]): x for x in ibge.values()}

    # a rede: unidades por cidade (a lista oficial é a fonte)
    rede = Counter()
    for u in jsonl("unidades_rede"):
        nome, uf = [t.strip() for t in u["cidade"].split("/")]
        rede[(norm(nome), uf)] += 1
    sem_ibge = [k for k in rede if k not in por_nome]

    # renda relativa: massa salarial per capita ÷ mediana nacional
    pcs = [x["massa_salarial_mil_reais"]/x["populacao"]
           for x in ibge.values()
           if x.get("massa_salarial_mil_reais") and x["populacao"]]
    pc_mediana = st.median(pcs)

    def renda_rel(x):
        if not x.get("massa_salarial_mil_reais"):
            return None
        return round((x["massa_salarial_mil_reais"]/x["populacao"])/pc_mediana, 2)

    # 1 · a régua da rede: hab/unidade por faixa, nas cidades onde já operamos
    por_faixa = defaultdict(list)
    cidades_da_rede = []
    for k, n in rede.items():
        x = por_nome.get(k)
        if not x:
            continue
        f = faixa_de(x["populacao"])
        por_faixa[f].append(x["populacao"]/n)
        cidades_da_rede.append((k, x, n, f))
    regua = {f: round(st.median(v)) for f, v in por_faixa.items() if v}
    pops_rede = sorted(x["populacao"] for _, x, _, _ in cidades_da_rede)
    piso = pops_rede[max(len(pops_rede)//10 - 1, 0)]   # décimo percentil

    # 2 · onde cabem mais — nas nossas cidades
    sub = []
    for k, x, n, f in cidades_da_rede:
        if f not in regua:
            continue
        comporta = int(x["populacao"]//regua[f])
        folga = comporta - n
        if folga >= 2:
            sub.append({
                "rotulo": f"{x['uf']} · {x['municipio']}",
                "populacao": x["populacao"], "faixa": f,
                "unidades_hoje": n, "comporta_pela_regua": comporta,
                "folga": folga, "renda_relativa": renda_rel(x),
                "leitura": (f"{n} unidade(s) para {x['populacao']:,} habitantes; "
                            f"a régua da rede nessa faixa é 1 para "
                            f"{regua[f]:,}").replace(",", "."),
            })
    sub.sort(key=lambda s: -s["folga"])

    # 3 · as candidatas — sem unidade na lista oficial, do piso para cima
    cands = []
    for x in ibge.values():
        k = (norm(x["municipio"]), x["uf"])
        if k in rede or x["populacao"] < piso:
            continue
        if not (x.get("alvo_9_15") and x.get("alvo_30_45")):
            continue
        rr = renda_rel(x)
        if rr is None:
            continue
        # A renda entra com TETO de 2x a mediana. Sem o teto, cidade de
        # royalty (Maricá 21x, Saquarema 23x — massa salarial formal
        # inflada) engole o alvo e o ranking vira mapa do petróleo.
        alvo = x["alvo_9_15"] + x["alvo_30_45"]
        f = faixa_de(x["populacao"])
        cands.append({
            "rotulo": f"{x['uf']} · {x['municipio']}",
            "municipio": x["municipio"], "uf": x["uf"],
            "populacao": x["populacao"], "faixa": f,
            "alvo_9_15": x["alvo_9_15"], "alvo_30_45": x["alvo_30_45"],
            "renda_relativa": rr,
            "score": round(alvo * min(rr, 2.0)),
            "comporta_pela_regua": (int(x["populacao"]//regua[f])
                                    if f in regua else None),
            "ja_estudada": norm(x["municipio"]) in JA_ESTUDADAS,
        })
    cands.sort(key=lambda c: -c["score"])
    cands = cands[:TOP]

    return {
        "o_que_e": "A régua barata sobre os 5.570 municípios, antes do estudo "
                   "caro: onde vale estudar a próxima cidade, e onde a própria "
                   "rede tem folga.",
        "metodo": {
            "score": "alvo (9-15 + 30-45 anos, Censo 2022) × renda relativa "
                     "(massa salarial per capita ÷ mediana nacional, com teto "
                     "de 2x — acima disso mais renda não muda a decisão)",
            "piso_populacao": piso,
            "piso_porque": "décimo percentil das cidades onde a rede já opera — "
                           "abaixo disso a rede quase não entra",
            "regua_hab_por_unidade": [
                {"faixa": f, "mediana_hab_por_unidade": v,
                 "cidades_da_rede_na_faixa": len(por_faixa[f])}
                for f, v in sorted(regua.items(),
                                   key=lambda kv: -kv[1])],
            "fonte": "IBGE (agregados 6579, 5938, 9514) + lista oficial de "
                     "unidades",
        },
        "candidatas": cands,
        "onde_cabem_mais": sub[:20],
        "o_que_isso_nao_ve": [
            "Score é régua de PRIORIDADE, não promessa de faturamento. Quem "
            "passa ganha o estudo profundo (concorrência, canais, busca) — o "
            "funil sozinho não aprova cidade nenhuma.",
            "'Sem unidade' aqui é UMA fonte (a lista oficial). A conferência "
            "com duas fontes acontece no estudo profundo.",
            "Fluxo de pessoas e dados de transação não existem em fonte "
            "aberta — o proxy de movimento continua sendo avaliações e "
            "anúncios, medidos só nas cidades estudadas.",
            f"{len(sem_ibge)} cidade(s) da rede não casaram com o IBGE pelo "
            f"nome e ficaram fora da régua." if sem_ibge else
            "Todas as cidades da rede casaram com o IBGE.",
        ],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()
    d = monta()

    print(f"\n{'='*78}\n  O FUNIL NACIONAL — a régua antes do estudo\n{'='*78}")
    print("\n  A régua da rede (hab por unidade, mediana da faixa):")
    for r in d["metodo"]["regua_hab_por_unidade"]:
        print(f"    {r['faixa']:14s} 1 : {r['mediana_hab_por_unidade']:>8,d} "
              f"({r['cidades_da_rede_na_faixa']} cidades)".replace(",", "."))
    print(f"\n  TOP 15 CANDIDATAS (de {len(d['candidatas'])} publicadas):")
    for c in d["candidatas"][:15]:
        print(f"    {c['rotulo']:28s} {c['populacao']:>9,d} hab · score "
              f"{c['score']:>7,d} · renda {c['renda_relativa']}x"
              .replace(",", ".")
              + ("  · JÁ ESTUDADA" if c["ja_estudada"] else ""))
    print(f"\n  ONDE CABEM MAIS (nossas cidades com folga ≥ 2):")
    for s in d["onde_cabem_mais"][:10]:
        print(f"    {s['rotulo']:28s} {s['unidades_hoje']} hoje · comporta "
              f"{s['comporta_pela_regua']} · folga {s['folga']}")

    if a.salvar:
        (PORTAL/"funil_nacional.json").write_text(
            json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n  → dados/portal/funil_nacional.json "
              f"({len(d['candidatas'])} candidatas · "
              f"{len(d['onde_cabem_mais'])} cidades com folga)")


if __name__ == "__main__":
    main()
