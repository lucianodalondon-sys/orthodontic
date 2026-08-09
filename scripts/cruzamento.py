#!/usr/bin/env python3
"""
cruzamento.py — a leitura da REDE, que é o que a franqueadora compra.

O inteligencia.py lê uma praça. Este lê todas juntas, e responde uma pergunta
diferente: **o que vale para a rede e o que vale só para uma cidade?**

É a diferença entre consultoria e sistema. Um estudo diz "sua unidade de
Riomafra está parada". Um sistema diz "trinta e sete unidades pararam este mês,
e as sete que não pararam fazem a mesma coisa".

Seis leituras:

  1. O PLACAR DA REDE — todas as unidades, ordenadas, com a posição de cada uma
     dentro da própria praça. Estar em 1º numa cidade fraca não é o mesmo que
     estar em 3º numa cidade brigada.

  2. QUEM PAROU, QUEM LIGOU — o alerta que só existe olhando junto. A matriz de
     Londrina fez a maior campanha da cidade e desligou, e ninguém percebeu
     porque ninguém comparava com ela mesma.

  3. O QUE SE REPETE — cada padrão com o número de praças em que aparece, e o
     degrau na escada. Um padrão visto em 3 regiões diferentes vale mais que um
     visto em 3 cidades vizinhas.

  4. O TERRITÓRIO VAZIO DA REDE — o canal que falta em muitas praças ao mesmo
     tempo é decisão de franqueadora, não de unidade.

  5. AS UNIDADES PARECIDAS — comparar unidade com a rede inteira é injusto.
     Compara-se com quem tem porte e praça parecidos.

  6. O QUE PESA CONTRA — a praça que contraria cada padrão, sempre nomeada.

Uso:
    python3 scripts/cruzamento.py
    python3 scripts/cruzamento.py --salvar     # grava em dados/portal/rede.json
"""
import argparse, json, math, pathlib, re, statistics as st
from collections import defaultdict, Counter

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SERIE = RAIZ/"dados"/"serie"
IDENT = RAIZ/"dados"/"identidade"


def jsonl(nome):
    p = SERIE/f"{nome}.jsonl"
    return [json.loads(l) for l in p.read_text(encoding="utf-8").split("\n") if l.strip()] \
        if p.exists() else []


def id_da_avaliacao(chave):
    """O identificador que o Google dá à avaliação, seja qual for o coletor.

    Em 07/08 um coletor gravou `local_id|<id>`; em 08/08 outro gravou
    `google:<place_id>:<id>`. As chaves nunca casaram, então a deduplicação
    por chave não pegou nada e cinco clínicas ficaram com as MESMAS avaliações
    gravadas duas vezes — 981 linhas, 2,7% da base, concentradas justamente em
    Souza Naves e Mafra, que abrem e fecham o placar. O `<id>` é o último
    pedaço nos dois formatos, e é ele que identifica a avaliação de verdade."""
    return re.split(r"[|:]", chave or "")[-1] or None


def reviews_unicos():
    """As avaliações sem a contagem em dobro. Todo cálculo de ritmo passa aqui.

    Mantém a linha mais recente de cada avaliação — a do coletor novo, que traz
    data em formato ISO limpo — e preserva o primeiro snapshot em que ela
    apareceu, senão a série perde o histórico de quando a avaliação entrou."""
    vistos = {}
    for r in jsonl("reviews"):
        rid = id_da_avaliacao(r.get("chave"))
        k = (r.get("local_id"), rid) if rid else (r.get("chave"), id(r))
        ant = vistos.get(k)
        if ant is None:
            vistos[k] = r
        else:
            novo = r if r.get("snapshot_date", "") >= ant.get("snapshot_date", "") else ant
            velho = ant if novo is r else r
            novo = dict(novo)
            novo["first_seen_snapshot"] = min(
                x for x in (novo.get("first_seen_snapshot"), velho.get("first_seen_snapshot"),
                            novo.get("snapshot_date"), velho.get("snapshot_date")) if x)
            vistos[k] = novo
    return list(vistos.values())


def identidades(com_unidade=True):
    """As praças da REDE. Praça de oportunidade (sem unidade) fica de fora.

    Sem esta trava, as seis praças que o Radar encontrou entrariam no placar
    como unidades sem movimento — e o "3 de 10 sustentam, 5 pararam" viraria
    "3 de 16, 11 pararam". Seria mentira em cima do número que a franqueadora
    mais olha."""
    todas = {p.stem: json.loads(p.read_text(encoding="utf-8"))
             for p in sorted(IDENT.glob("*.json"))}
    if not com_unidade:
        return todas
    return {k: v for k, v in todas.items() if not v.get("sem_unidade")}


def ritmo_e_meses(datas, hoje=None):
    """Mesma conta do inteligencia.py, para os números baterem entre as telas."""
    import datetime as dt
    if len(datas) < 5:
        return None, 0
    ds = sorted(datas)
    dias = max((dt.date.fromisoformat(ds[-1]) - dt.date.fromisoformat(ds[0])).days, 1)
    ritmo = round(len(ds)/(dias/30.4), 1)
    hoje = hoje or dt.date.today()
    c = Counter(d[:7] for d in ds)
    tipico = st.median(list(c.values())) or 1
    seguidos, ano, mes = 0, hoje.year, hoje.month - 1
    if mes == 0:
        ano, mes = ano-1, 12
    for _ in range(36):
        if c.get(f"{ano:04d}-{mes:02d}", 0) < max(2, tipico*0.3):
            break
        seguidos += 1
        mes -= 1
        if mes == 0:
            ano, mes = ano-1, 12
    return ritmo, seguidos


def coleta():
    ident = identidades()
    revs = defaultdict(list)
    for r in reviews_unicos():
        if r.get("data"):
            revs[(r.get("praca_id"), r.get("local_id"))].append(str(r["data"])[:10])
    places = {}
    for p in jsonl("places"):
        k = (p.get("praca_id"), p.get("local_id"))
        if k not in places or p["snapshot_date"] >= places[k]["snapshot_date"]:
            places[k] = p

    linhas = []
    for praca, d in ident.items():
        for l in d.get("locais", []):
            k = (praca, l["local_id"])
            ritmo, meses = ritmo_e_meses(revs.get(k, []))
            pl = places.get(k, {})
            linhas.append({
                "praca": praca, "rotulo": d.get("rotulo") or d.get("nome"),
                "uf": (d.get("uf") or [None])[0],
                "local_id": l["local_id"], "nome": l.get("nome"),
                "papel": l.get("papel"),
                "total": pl.get("avaliacoes", pl.get("avaliacoes_total")) or l.get("avaliacoes_google"),
                "nota": pl.get("nota") or l.get("nota_google"),
                "ritmo": ritmo, "meses": meses,
            })
    # posição de cada um dentro da própria praça
    for praca in ident:
        na_praca = sorted([x for x in linhas if x["praca"] == praca and x["ritmo"] is not None],
                          key=lambda x: -x["ritmo"])
        for i, x in enumerate(na_praca, 1):
            x["posicao"] = i
            x["de"] = len(na_praca)
    return ident, linhas


def selo(m):
    if m is None:
        return "?"
    if m >= 10:
        return "OPERAÇÃO"
    if m >= 3:
        return "campanha"
    return "parada"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()
    ident, linhas = coleta()
    nossas = [x for x in linhas if x["papel"] == "proprio" and x["ritmo"] is not None]
    todas = [x for x in linhas if x["ritmo"] is not None]

    print(f"\n{'='*78}\n  A REDE — {len(ident)} praças · {len(nossas)} unidades medidas · "
          f"{len(todas)} clínicas\n{'='*78}")

    # ---------------------------------------------------------------- 1
    print("\n## 1 · O PLACAR DA REDE")
    print("  Posição é dentro da PRÓPRIA praça. 1º numa cidade fraca não é o")
    print("  mesmo que 3º numa cidade brigada — por isso as duas colunas.\n")
    print(f"  {'ritmo':>6s} {'meses':>6s} {'posição':>9s} {'total':>6s}  praça · unidade")
    for x in sorted(nossas, key=lambda x: -x["ritmo"]):
        pos = f"{x['posicao']}º de {x['de']}"
        # praça com mais de uma unidade precisa do nome, senão vira duas linhas iguais
        nome = (x["nome"] or "").replace("OrthoDontic", "").strip(" -–—")
        etiq = f"{x['rotulo']}" + (f" · {nome}" if nome else "")
        print(f"  {x['ritmo']:>6.1f} {x['meses']:>6d} {pos:>9s} {str(x['total']):>6s}  "
              f"{etiq[:40]:40s} {selo(x['meses'])}")

    # ---------------------------------------------------------------- 2
    print("\n## 2 · QUEM SUSTENTA E QUEM NÃO")
    op = [x for x in nossas if x["meses"] >= 10]
    camp = [x for x in nossas if 3 <= x["meses"] < 10]
    par = [x for x in nossas if x["meses"] < 3]
    print(f"  OPERAÇÃO (10+ meses seguidos): {len(op)} de {len(nossas)}")
    def etiqueta(x):
        n = (x["nome"] or "").replace("OrthoDontic", "").strip(" -–—")
        return (f"{x['rotulo']}" + (f" · {n}" if n else ""))[:38]
    for x in op:
        print(f"    {etiqueta(x):38s} {x['ritmo']:>5.1f}/mês · {x['meses']} meses")
    if camp:
        print(f"  campanha (3 a 9 meses): {len(camp)}")
        for x in camp:
            print(f"    {etiqueta(x):38s} {x['ritmo']:>5.1f}/mês · {x['meses']} meses")
    if par:
        print(f"  ⚫ PARADA (menos de 3 meses): {len(par)}")
        for x in par:
            print(f"    {etiqueta(x):38s} {x['ritmo']:>5.1f}/mês · {x['posicao']}º de {x['de']}")
    # e o mercado?
    conc = [x for x in todas if x["papel"] != "proprio"]
    op_c = sum(1 for x in conc if x["meses"] >= 10)
    print(f"\n  Na concorrência: {op_c} de {len(conc)} sustentam ({100*op_c//max(len(conc),1)}%)")
    print(f"  Na rede:         {len(op)} de {len(nossas)} sustentam "
          f"({100*len(op)//max(len(nossas),1)}%)")
    if len(nossas) and len(conc):
        if 100*len(op)/len(nossas) > 100*op_c/len(conc):
            print("  → A rede sustenta MAIS que o mercado. É o ativo dela.")

    # ---------------------------------------------------------------- 3
    print("\n## 3 · O TERRITÓRIO VAZIO DA REDE")
    print("  Canal que falta em muitas praças ao mesmo tempo é decisão de")
    print("  franqueadora, não de unidade.\n")
    C = jsonl("canais")
    tipos = defaultdict(lambda: {"tem": set(), "falta": set()})
    for c in C:
        t = c.get("tipo")
        if not t:
            continue
        if c.get("handle"):
            tipos[t]["tem"].add(c["praca_id"])
        elif c.get("status") == "nao_encontrado":
            tipos[t]["falta"].add(c["praca_id"])
    for t, v in sorted(tipos.items(), key=lambda x: -len(x[1]["falta"])):
        if not v["falta"]:
            continue
        marca = "  ←— " + ("É ELA QUEM DECIDE O APARELHO" if t == "mae" else
                           "9-15 COM OS PAIS JUNTO" if t == "esporte_base" else "")
        print(f"  {t:18s} falta em {len(v['falta'])} praças: "
              f"{', '.join(sorted(v['falta']))[:44]}{marca.rstrip()}")

    # ---------------------------------------------------------------- 4
    print("\n## 4 · AS UNIDADES PARECIDAS")
    print("  Comparar unidade com a rede inteira é injusto. Compara-se com quem")
    print("  tem porte de praça parecido.\n")
    def porte(x):
        d = ident[x["praca"]]
        pop = 0
        for n in d.get("ibge", []):
            try:
                pop += int((n.get("populacao_estimada") or {}).get("valor") or 0)
            except Exception:
                pass
        return ("acima de 500 mil" if pop >= 500_000 else
                "200 a 500 mil" if pop >= 200_000 else "até 200 mil")
    grupos = defaultdict(list)
    for x in nossas:
        grupos[porte(x)].append(x)
    for g, xs in sorted(grupos.items()):
        med = st.median([x["ritmo"] for x in xs])
        print(f"  {g:18s} {len(xs)} unidades · mediana {med:.1f}/mês")
        for x in sorted(xs, key=lambda x: -x["ritmo"]):
            n = (x["nome"] or "").replace("OrthoDontic", "").strip(" -–—")
            et = (f"{x['rotulo']}" + (f" · {n}" if n else ""))[:36]
            sinal = "acima" if x["ritmo"] > med else ("abaixo" if x["ritmo"] < med else "na mediana")
            print(f"      {et:36s} {x['ritmo']:>5.1f}  {sinal}")

    # ---------------------------------------------------------------- 5
    print("\n## 5 · O QUE PESA CONTRA")
    contra = []
    if op:
        piores = [x for x in op if x["posicao"] > x["de"]/2]
        for x in piores:
            contra.append(f"{x['rotulo']} sustenta há {x['meses']} meses e mesmo assim é "
                          f"{x['posicao']}º de {x['de']} — constância não basta")
    for x in nossas:
        if x["meses"] < 3 and (x["total"] or 0) > 300:
            contra.append(f"{x['rotulo']} tem {x['total']} avaliações acumuladas e parou — "
                          "o problema não é falta de base")
    fortes = [x for x in conc if x["meses"] >= 10 and x["ritmo"] > (st.median([y['ritmo'] for y in nossas]) if nossas else 0)]
    if fortes:
        contra.append(f"{len(fortes)} concorrentes sustentam E correm mais que a mediana da rede")
    for c in (contra or ["(nada encontrado — o que é motivo de desconfiança, não de comemoração)"]):
        print(f"  · {c}")

    # ---------------------------------------------------------------- 6
    print("\n## 6 · O QUE ISSO NÃO VÊ")
    off = jsonl("midia_offline")
    com = {o["praca_id"] for o in off}
    sem = set(ident) - com
    if sem:
        print(f"  ⚠ {len(sem)} praças sem canal offline declarado: {', '.join(sorted(sem))}")
    print(f"  A rede tem 340 unidades e esta leitura vê {len(nossas)}. "
          f"Tudo aqui é {100*len(nossas)//340}% da rede.")
    print("  Nenhum número aqui vem de dado interno.\n")

    if a.salvar:
        dst = RAIZ/"dados"/"portal"
        dst.mkdir(parents=True, exist_ok=True)
        (dst/"rede_cruzamento.json").write_text(json.dumps({
            "gerado_em": __import__("datetime").date.today().isoformat(),
            "pracas": len(ident), "unidades": len(nossas), "clinicas": len(todas),
            "placar": sorted(nossas, key=lambda x: -x["ritmo"]),
            "sustentam": len(op), "campanha": len(camp), "paradas": len(par),
            "territorio_vazio": {t: sorted(v["falta"]) for t, v in tipos.items() if v["falta"]},
            "pesa_contra": contra,
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  → dados/portal/rede_cruzamento.json\n")


if __name__ == "__main__":
    main()
