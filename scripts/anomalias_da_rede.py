#!/usr/bin/env python3
"""
anomalias_da_rede.py — quem está muito diferente do que DEVERIA estar.

A troca de pergunta
-------------------
A fila pergunta "quem tem nota baixa, quem parou, quem está atrás". É a
pergunta operacional, e ela está certa. Esta aqui é outra:

    quem está muito longe do que os semelhantes conseguem?

As duas respostas não coincidem. Uma unidade pode ter 4,8 e parecer ótima
enquanto todas as comparáveis ganham dez avaliações por mês e ela ganha
uma — ela não está mal, está ANÔMALA. E uma unidade com 4,6 pode estar
subindo mais rápido que qualquer semelhante: essa merece ser estudada, não
visitada.

Daí as duas categorias:

    ANOMALIA NEGATIVA   "esta unidade deveria estar melhor do que está"
    FORA DA CURVA       "esta unidade está fazendo algo que precisamos
                         entender"

A segunda é a que revela boa prática escondida na rede — e boa prática
escondida é exatamente o que uma franqueadora não consegue comprar.

Contra o que se compara
-----------------------
Contra os GÊMEOS, nunca contra a rede inteira. Comparar uma loja de Mafra
com a mediana de 45 unidades — metade delas em capital — produziria
"anomalia" para toda cidade pequena. Os gêmeos saem de
`comparador_de_lojas.py`, escolhidos por mercado.

O limite, dito antes que alguém pergunte
----------------------------------------
Três gêmeos são três pontos. Isto NÃO é significância estatística, e o
carimbo de cada linha diz isso. É um holofote para o consultor apontar,
não um veredito.

Uso:
    python3 scripts/anomalias_da_rede.py
    python3 scripts/anomalias_da_rede.py --salvar
"""
import argparse, json, pathlib, statistics as st, sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ/"scripts"))
from cruzamento import conta, confianca

PORTAL = RAIZ/"dados"/"portal"

# Quanto a loja precisa estar longe dos semelhantes para ser anomalia.
# Abaixo disto é variação normal entre lojas parecidas.
MUITO_ABAIXO = 0.5      # metade do ritmo dos gêmeos
MUITO_ACIMA = 2.0       # o dobro
MIN_GEMEOS = 2          # com um gêmeo só não há curva para estar fora


def monta():
    p = PORTAL/"gemeos.json"
    if not p.exists():
        print("  ✗ FALHA: dados/portal/gemeos.json não existe.\n"
              "  rode antes: python3 scripts/comparador_de_lojas.py --salvar")
        sys.exit(1)
    g = json.loads(p.read_text(encoding="utf-8"))
    perfil = {x["local_id"]: x["perfil"] for x in g["lojas"]}

    negativas, fora_da_curva, sem_base = [], [], []
    for x in g["lojas"]:
        eu = x["perfil"]
        # ritmo truncado não compara com nada — a amostra de uma loja
        # grande cobre poucas semanas e a de uma pequena, a vida inteira
        if not eu.get("ritmo_comparavel") or eu.get("ritmo") is None:
            sem_base.append({"local_id": x["local_id"], "rotulo": x["rotulo"],
                             "unidade": x["unidade"],
                             "porque": "o ritmo desta loja não é comparável: "
                                       "a leitura de avaliações foi truncada"})
            continue
        pares = [perfil[t["local_id"]] for t in x["gemeos"]
                 if perfil.get(t["local_id"], {}).get("ritmo_comparavel")
                 and perfil[t["local_id"]].get("ritmo") is not None]
        if len(pares) < MIN_GEMEOS:
            sem_base.append({"local_id": x["local_id"], "rotulo": x["rotulo"],
                             "unidade": x["unidade"],
                             "porque": (f"só {conta(len(pares), 'gêmeo', 'gêmeos')} "
                                        f"com ritmo comparável — sem curva "
                                        f"para dizer que está fora dela")})
            continue

        ref = st.median([q["ritmo"] for q in pares])
        razao = (eu["ritmo"]/ref) if ref else None
        if razao is None:
            continue
        item = {
            "local_id": x["local_id"], "praca_id": x["praca_id"],
            "rotulo": x["rotulo"], "unidade": x["unidade"],
            "ritmo": eu["ritmo"], "ritmo_dos_semelhantes": round(ref, 1),
            "razao": round(razao, 2),
            "nota": eu.get("nota"), "avaliacoes": eu.get("avaliacoes"),
            "gemeos": [{"rotulo": q["rotulo"], "unidade": q["unidade"],
                        "ritmo": q["ritmo"]} for q in pares],
            "carimbo": confianca(
                natureza="inferencia",
                amostra=len(pares), unidade_amostra=("loja semelhante",
                                                     "lojas semelhantes"),
                a_favor=["a comparação é contra lojas de mercado parecido, "
                         "não contra a mediana da rede"],
                contra=[f"{len(pares)} pontos de comparação não são "
                        f"significância estatística — isto aponta onde "
                        f"olhar, não o que concluir"],
                o_que_aumentaria="medir mais unidades da rede, para que "
                                 "cada loja tenha mais semelhantes"),
        }
        if razao <= MUITO_ABAIXO:
            item["leitura"] = (
                f"ganha {eu['ritmo']:.1f} avaliações por mês onde as "
                f"semelhantes ganham {ref:.1f}"
                + (f", e ainda assim tem nota {eu['nota']}"
                   if (eu.get("nota") or 0) >= 4.5 else ""))
            item["o_que_perguntar"] = (
                "o que mudou na rotina de pedir avaliação no fim do "
                "atendimento? As semelhantes fazem o dobro com o mesmo "
                "tamanho de cidade.")
            # o que dá para ver de fora que pode estar por trás — DIFERENÇA,
            # nunca causa
            item["diferencas_visiveis"] = _difs(eu, pares)
            negativas.append(item)
        elif razao >= MUITO_ACIMA:
            item["leitura"] = (
                f"ganha {eu['ritmo']:.1f} avaliações por mês onde as "
                f"semelhantes ganham {ref:.1f}")
            item["o_que_perguntar"] = (
                "o que esta unidade faz que as semelhantes não fazem? "
                "Vale entender antes de virar recomendação de rede.")
            item["diferencas_visiveis"] = _difs(eu, pares)
            fora_da_curva.append(item)

    negativas.sort(key=lambda x: x["razao"])
    fora_da_curva.sort(key=lambda x: -x["razao"])

    return {
        "o_que_e": "As unidades que estão muito longe do que as "
                   "semelhantes conseguem — para baixo e para cima.",
        "por_que_importa": ("nota baixa a fila já mostra. O que ninguém vê "
                            "é a loja que parece bem e está muito abaixo "
                            "do que o mercado dela comporta — e a que está "
                            "muito acima e ninguém foi perguntar por quê"),
        "o_que_nao_e": ("não é causa e não é significância: são três "
                        "pontos de comparação. Serve para escolher onde "
                        "olhar, não para concluir"),
        "contra_o_que_compara": ("contra os gêmeos de cada loja — mercado "
                                 "parecido —, nunca contra a mediana da "
                                 "rede, que misturaria capital com cidade "
                                 "de 80 mil"),
        "cortes": {"muito_abaixo": MUITO_ABAIXO, "muito_acima": MUITO_ACIMA,
                   "minimo_de_gemeos": MIN_GEMEOS},
        "manchete": (
            conta(len(negativas), "unidade que deveria estar melhor",
                  "unidades que deveriam estar melhor")
            + " · "
            + conta(len(fora_da_curva), "fora da curva para cima",
                    "fora da curva para cima")),
        "anomalias_negativas": negativas,
        "anomalias_negativas_total": len(negativas),
        "fora_da_curva": fora_da_curva,
        "fora_da_curva_total": len(fora_da_curva),
        # ESTADO VAZIO É CONTEÚDO: quem não pôde ser comparado aparece
        # com o motivo, em vez de sumir da conta
        "sem_base_de_comparacao": sem_base,
        "sem_base_total": len(sem_base),
    }


def _difs(eu, pares):
    """O que separa esta loja das semelhantes, onde os dois lados existem."""
    out = []
    # DIFERENÇA DE UM PONTO NÃO É DIFERENÇA. A primeira versão publicava
    # "5% aqui contra 5% nas semelhantes" e "4 aqui contra 3" como se
    # fossem lições — é o mesmo ruído que a trava do comparador barra.
    for campo, rotulo, fmt, minimo in (
            ("busca_cidade", "aparece nas buscas da cidade", "{:.0f}", 2),
            ("busca_perto", "aparece nas buscas perto da loja", "{:.0f}", 2),
            ("pct_respondidas", "avaliações já respondidas", "{:.0f}%", 10),
            ("pct_com_nome", "avaliações que citam profissional pelo nome",
             "{:.0f}%", 10)):
        meus = eu.get(campo)
        deles = [q[campo] for q in pares if q.get(campo) is not None]
        if meus is None or not deles:
            continue
        ref = st.median(deles)
        if abs(ref - meus) < minimo:
            continue
        out.append({"o_que": rotulo, "aqui": meus,
                    "nas_semelhantes": round(ref, 1),
                    "texto": (f"{fmt.format(meus)} aqui contra "
                              f"{fmt.format(ref)} nas semelhantes")})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()
    d = monta()
    print(f"\n{'='*78}\n  QUEM ESTÁ FORA DA CURVA\n{'='*78}\n")
    print(f"  {d['manchete']}\n")
    for titulo, chave in (("DEVERIAM ESTAR MELHOR", "anomalias_negativas"),
                          ("FAZENDO ALGO QUE PRECISAMOS ENTENDER",
                           "fora_da_curva")):
        print(f"  ── {titulo}  ({len(d[chave])})")
        for x in d[chave]:
            print(f"     {x['rotulo']} · {x['unidade']}   "
                  f"({x['razao']}x os semelhantes)")
            print(f"       {x['leitura']}")
            for df in x["diferencas_visiveis"]:
                print(f"       · {df['o_que']}: {df['texto']}")
        print()
    if d["sem_base_total"]:
        print(f"  {conta(d['sem_base_total'], 'loja ficou de fora', 'lojas ficaram de fora')}"
              f" da comparação, com o motivo declarado\n")
    if a.salvar:
        (PORTAL/"anomalias.json").write_text(
            json.dumps(d, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8")
        print(f"  → dados/portal/anomalias.json")


if __name__ == "__main__":
    main()
