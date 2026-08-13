#!/usr/bin/env python3
"""
playbook_do_concorrente.py — o que os concorrentes que GANHAM fazem, lido
em toda a rede de uma vez.

A diferença para a tela do rival
--------------------------------
`o_que_o_rival_faz.py` responde "em que o líder da MINHA praça me ganha".
É a leitura da unidade. Esta aqui é a da franqueadora:

    juntando 23 praças, o que separa o concorrente que avança do que não
    avança — e o que a gente testou e NÃO separou nada?

A segunda metade da pergunta é a que dá crédito à primeira. Uma lista só
com o que funciona é palestra; uma lista que também mostra o que foi
testado e não explicou nada é medição.

Quem é "vencedor", em critério observável
-----------------------------------------
Nada de faturamento — não temos, e não vamos ter. Vencedor aqui é o
concorrente que:

    disputa APARELHO (carimbado na identidade, não adivinhado pelo nome),
    tem amostra de avaliação suficiente para definir padrão,
    sustenta movimento há pelo menos dez meses, e
    corre acima da mediana da própria praça.

O resto do grupo é o comparativo. As duas metades saem da mesma coleta, do
mesmo jeito, no mesmo dia.

O limite
--------
Frequência não é causa. Se 70% dos que avançam são elogiados por explicar
o tratamento e 40% dos outros também, a diferença é uma pista — não um
mecanismo. Nenhuma linha aqui autoriza dizer "faça isto e você cresce".

Uso:
    python3 scripts/playbook_do_concorrente.py
    python3 scripts/playbook_do_concorrente.py --salvar
"""
import argparse, json, pathlib, statistics as st, sys
from collections import defaultdict

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ/"scripts"))
from cruzamento import coleta, reviews_unicos, conta, confianca
# a régua da voz do paciente é a MESMA da tela do rival — dois regex
# diferentes para o mesmo eixo produziriam dois números para a mesma
# pergunta, e o portal já pagou por esse erro
from o_que_o_rival_faz import EIXOS, RX, sa, MIN_AVALIACOES

PORTAL = RAIZ/"dados"/"portal"

MESES_PARA_SUSTENTAR = 10    # movimento de um mês não é "avança"
# Diferença de frequência abaixo disto não separa nada. É ela que produz a
# lista "testamos e não explicou", que é metade do valor deste arquivo.
MIN_DIFERENCA_PP = 15        # pontos percentuais

# GRUPO DE DOIS NÃO É GRUPO. A primeira rodada separou 2 concorrentes que
# avançam de 10 que não, e publicou "aparece em 50% dos que avançam" — que
# são UM concorrente. Metade da amostra virando meio ponto percentual é a
# forma mais fácil de publicar ruído com cara de achado. Abaixo deste
# tamanho a comparação não sai: sai o funil, dizendo por que não sai.
MIN_GRUPO = 6


def carrega(nome):
    p = PORTAL/f"{nome}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def perfil(revs):
    com_texto = [r for r in revs if (r.get("texto") or "").strip()]
    if not com_texto:
        return None, 0
    return ({k: sum(1 for r in com_texto if rx.search(sa(r["texto"])))
             / len(com_texto) for k, rx in RX.items()},
            len(com_texto))


def monta():
    ident, linhas = coleta()
    revs = defaultdict(list)
    for r in reviews_unicos():
        revs[(r.get("praca_id"), r.get("local_id"))].append(r)

    # ------------------------------------------------- quem avança, quem não
    vencedores, resto = [], []
    for p, d in sorted(ident.items()):
        rivais = [x for x in linhas
                  if x["praca"] == p and x["papel"] != "proprio"
                  and x.get("aparelho") and x.get("ritmo") is not None
                  and x.get("ritmo_comparavel")]
        if len(rivais) < 2:
            continue
        mediana = st.median([x["ritmo"] for x in rivais])
        for x in rivais:
            pf, n = perfil(revs.get((p, x["local_id"]), []))
            if not pf or n < MIN_AVALIACOES:
                continue
            reg = {"praca_id": p, "rotulo": d.get("rotulo"),
                   "nome": x["nome"], "ritmo": x["ritmo"],
                   "meses": x.get("meses"), "nota": x.get("nota"),
                   "avaliacoes_lidas": n, "perfil": pf,
                   "mediana_da_praca": round(mediana, 1)}
            avanca = (x.get("meses", 0) >= MESES_PARA_SUSTENTAR
                      and x["ritmo"] > mediana)
            (vencedores if avanca else resto).append(reg)

    # o funil, sempre — mesmo (e principalmente) quando ele não dá base
    n_conc = sum(1 for x in linhas if x["papel"] != "proprio")
    n_apar = sum(1 for x in linhas if x["papel"] != "proprio" and x.get("aparelho"))
    n_comp = sum(1 for x in linhas if x["papel"] != "proprio" and x.get("aparelho")
                 and x.get("ritmo") is not None and x.get("ritmo_comparavel"))
    funil = [
        {"degrau": "concorrentes medidos", "quantos": n_conc},
        {"degrau": "disputam aparelho", "quantos": n_apar,
         "porque_caem": "odontologia não é ortodontia: clínica geral, "
                        "implante e universidade dividem a rua, não o "
                        "paciente de aparelho"},
        {"degrau": "com ritmo comparável", "quantos": n_comp,
         "porque_caem": "a leitura de avaliações foi truncada — as N mais "
                        "novas cobrem a vida inteira de uma loja pequena e "
                        "poucas semanas de uma grande"},
        {"degrau": "com avaliações de texto suficientes",
         "quantos": len(vencedores) + len(resto),
         "porque_caem": f"abaixo de {MIN_AVALIACOES} avaliações com texto a "
                        f"clínica não define padrão"},
    ]

    # ------------------------------------------- o que separa os dois grupos
    def freq(grupo, eixo, corte=0.05):
        """Em quantos daquele grupo o eixo aparece em mais de 5% das
        avaliações. Proporção, nunca soma — clínica grande teria mais de
        tudo só por ser grande."""
        return 100*sum(1 for g in grupo if g["perfil"][eixo] >= corte)/len(grupo)

    separa, nao_separa = [], []
    for k, (rotulo, _) in EIXOS.items():
        fv, fr = freq(vencedores, k), freq(resto, k)
        item = {
            "eixo": k, "o_que_e": rotulo,
            "nos_vencedores_pct": round(fv, 1),
            "no_resto_pct": round(fr, 1),
            "diferenca_pp": round(fv - fr, 1),
            "frase": (f"aparece em {fv:.0f}% dos que avançam e em "
                      f"{fr:.0f}% dos demais"),
            "carimbo": confianca(
                natureza="inferencia",
                amostra=len(vencedores) + len(resto),
                unidade_amostra=("clínica concorrente",
                                 "clínicas concorrentes"),
                a_favor=["os dois grupos saem da mesma coleta, no mesmo "
                         "dia, com a mesma régua de texto"],
                contra=["frequência não é causa: isto diz o que anda "
                        "junto, nunca o que produz o quê"],
                o_que_aumentaria="acompanhar os mesmos concorrentes ao "
                                 "longo do tempo, e ver se quem muda o "
                                 "eixo muda o ritmo depois"),
        }
        (separa if abs(fv - fr) >= MIN_DIFERENCA_PP
         else nao_separa).append(item)
    separa.sort(key=lambda x: -x["diferenca_pp"])
    nao_separa.sort(key=lambda x: -abs(x["diferenca_pp"]))
    base_suficiente = (len(vencedores) >= MIN_GRUPO
                       and len(resto) >= MIN_GRUPO)
    if not base_suficiente:
        separa, nao_separa = [], []

    # ------------------------------------------------ o que o mercado ANUNCIA
    of = carrega("oferta")
    por_eixo = defaultdict(lambda: {"pracas": 0, "anuncios": 0, "onde": []})
    vagas = defaultdict(int)
    for pr in of.get("pracas", []):
        for e in pr.get("eixos", []):
            if not e.get("anuncios"):
                continue
            reg = por_eixo[e["eixo"]]
            reg["rotulo"] = e.get("rotulo")
            reg["o_que_significa"] = e.get("o_que_significa")
            reg["pracas"] += 1
            reg["anuncios"] += e["anuncios"]
            reg["onde"].append({"rotulo": pr.get("rotulo"), "pct": e.get("pct")})
        pv = (pr.get("posicao_vaga") or "")
        if pv:
            vagas[pv] += 1
    n_pracas_com_anuncio = sum(1 for pr in of.get("pracas", [])
                               if pr.get("anuncios_de_aparelho"))
    oferta = []
    for k, v in por_eixo.items():
        v["onde"].sort(key=lambda x: -(x["pct"] or 0))
        oferta.append({
            "eixo": k, "o_que_e": v.get("rotulo"),
            "o_que_significa": v.get("o_que_significa"),
            "pracas": v["pracas"], "anuncios": v["anuncios"],
            "frase": (conta(v["pracas"], "praça", "praças") + " de "
                      + conta(n_pracas_com_anuncio, "medida", "medidas")),
            "onde_mais_pesa": v["onde"][:5],
            "onde_mais_pesa_total": len(v["onde"]),
        })
    oferta.sort(key=lambda x: (-x["pracas"], -x["anuncios"]))

    top = separa[0] if separa else None
    return {
        "o_que_e": "O que separa o concorrente que avança do que não "
                   "avança, somando todas as praças medidas — e o que o "
                   "mercado inteiro está anunciando.",
        "por_que_importa": ("a tela do rival serve o franqueado, uma praça "
                            "por vez. Esta serve a decisão nacional: o que "
                            "vale virar padrão de rede e o que não vale"),
        "o_que_nao_e": ("não é causa e não é receita. Frequência que anda "
                        "junto com ritmo é pista; chamar de mecanismo "
                        "seria inventar"),
        "quem_e_vencedor": {
            "regra": (f"disputa aparelho, tem pelo menos "
                      f"{MIN_AVALIACOES} avaliações com texto lidas, "
                      f"sustenta movimento há {MESES_PARA_SUSTENTAR} meses "
                      f"ou mais e corre acima da mediana da própria praça"),
            "porque_assim": ("faturamento não entra: o portal é feito "
                             "inteiramente de informação externa"),
            "vencedores": len(vencedores), "resto": len(resto),
        },
        "corte_de_diferenca_pp": MIN_DIFERENCA_PP,
        "minimo_por_grupo": MIN_GRUPO,
        "base_suficiente": base_suficiente,
        "porque_sem_comparacao": (None if base_suficiente else
            f"são {len(vencedores)} concorrentes que avançam contra "
            f"{len(resto)} que não. Com grupo menor que {MIN_GRUPO}, cada "
            f"clínica vira dezenas de pontos percentuais e o resultado é "
            f"ruído com cara de achado — a comparação não é publicada."),
        "o_que_aumentaria_a_base": (
            "classificar por produto os concorrentes que a varredura já "
            "mediu e ainda não estão na identidade, e ler as avaliações "
            "por inteiro nos que disputam aparelho"),
        "funil_ate_a_comparacao": funil,
        "manchete": (
            (f"{top['o_que_e'].lower()} é o que mais separa quem avança: "
             f"{top['frase']}") if top else
            (f"ainda não dá para comparar quem avança com quem não avança: "
             f"{len(vencedores)} contra {len(resto)}")),
        "o_que_os_vencedores_fazem": separa,
        "o_que_os_vencedores_fazem_total": len(separa),
        # A METADE QUE DÁ CRÉDITO À OUTRA. Eixo testado que não separou
        # nada fica na tela: é o contrário de escolher a dedo o que
        # confirma a tese.
        "testamos_e_nao_explicou": nao_separa,
        "testamos_e_nao_explicou_total": len(nao_separa),
        "o_que_o_mercado_anuncia": oferta,
        "o_que_o_mercado_anuncia_total": len(oferta),
        "pracas_com_anuncio": n_pracas_com_anuncio,
        "posicoes_vagas": [{"posicao": k, "pracas": v}
                           for k, v in sorted(vagas.items(),
                                              key=lambda x: -x[1])][:6],
    }


def imprime(d):
    if d.get("erro"):
        print(f"  ✗ {d['erro']}")
        return
    print(f"\n{'='*78}\n  O PLAYBOOK DO CONCORRENTE\n{'='*78}\n")
    q = d["quem_e_vencedor"]
    print(f"  {q['vencedores']} concorrentes avançam · {q['resto']} não\n")
    print(f"  {d['manchete']}\n")
    if not d["base_suficiente"]:
        print(f"  ⚠ {d['porque_sem_comparacao']}\n")
        print("  ── O FUNIL ATÉ A COMPARAÇÃO")
        for f in d["funil_ate_a_comparacao"]:
            print(f"     {f['quantos']:>5}  {f['degrau']}")
    print("  ── O QUE APARECE MAIS NOS QUE AVANÇAM")
    for x in d["o_que_os_vencedores_fazem"]:
        print(f"     {x['diferenca_pp']:>+6.0f} pp  {x['o_que_e'][:44]:<46}"
              f"{x['nos_vencedores_pct']:.0f}% × {x['no_resto_pct']:.0f}%")
    print("\n  ── TESTAMOS E NÃO EXPLICOU NADA")
    for x in d["testamos_e_nao_explicou"]:
        print(f"     {x['diferenca_pp']:>+6.0f} pp  {x['o_que_e'][:44]:<46}"
              f"{x['nos_vencedores_pct']:.0f}% × {x['no_resto_pct']:.0f}%")
    print("\n  ── O QUE O MERCADO ANUNCIA")
    for x in d["o_que_o_mercado_anuncia"][:8]:
        print(f"     {x['frase']:<22}{x['o_que_e'][:36]:<38}"
              f"{x['anuncios']} anúncios")
    if d["posicoes_vagas"]:
        print("\n  ── POSIÇÃO VAGA, REPETIDA EM VÁRIAS PRAÇAS")
        for x in d["posicoes_vagas"][:3]:
            print(f"     {x['pracas']}x  {x['posicao'][:66]}")
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()
    d = monta()
    imprime(d)
    if a.salvar and not d.get("erro"):
        (PORTAL/"playbook.json").write_text(
            json.dumps(d, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8")
        print(f"  → dados/portal/playbook.json")


if __name__ == "__main__":
    main()
