#!/usr/bin/env python3
"""
o_que_o_rival_faz.py — o que o concorrente que GANHA faz, na voz do paciente dele.

A ideia, e por que ela é a melhor deste projeto
-----------------------------------------------
Das 35.538 avaliações lidas, só 2.190 são nossas. **33.348 são da
concorrência** — já pagas, já no disco, e nunca lidas como "o que eles fazem
que dá certo". Todo o resto do portal olha para dentro: nosso ritmo, nossa
nota, nossa ficha. Este arquivo olha para o vencedor da rua e pergunta o que
o paciente DELE elogia que o nosso não elogia.

É a única leitura aqui que produz instrução em vez de diagnóstico. "Sua
unidade está em 3º" não diz o que fazer na segunda-feira. "O líder da sua
praça é elogiado por explicar o tratamento em 2,4 vezes mais avaliações que
você" diz.

Como se compara sem trapacear
-----------------------------
Compara-se por PROPORÇÃO, nunca por volume: uma clínica com 3.837 avaliações
teria mais menções de tudo. E compara-se dentro da MESMA praça — o líder de
Cuiabá contra a nossa de Cuiabá, nunca contra a nossa de Mafra.

Duas travas que vêm das regras do projeto:

  ODONTOLOGIA NÃO É ORTODONTIA. Centro médico e rede de implante não disputam
  paciente de aparelho. A Vitae Center, "1ª" de Contagem, é um CENTRO MÉDICO
  com 3.837 avaliações de consulta médica — ela sai da comparação.

  Amostra mínima. Concorrente com 40 avaliações não define padrão de praça, e
  porcentagem em cima de amostra pequena é o jeito mais fácil de publicar
  ruído com cara de achado.

Uso:
    python3 scripts/o_que_o_rival_faz.py
    python3 scripts/o_que_o_rival_faz.py --praca cuiaba
    python3 scripts/o_que_o_rival_faz.py --salvar
"""
import argparse, json, pathlib, re, sys, unicodedata
from collections import defaultdict, Counter

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ/"scripts"))
from cruzamento import jsonl, reviews_unicos, identidades, coleta, conta

PORTAL = RAIZ/"dados"/"portal"

MIN_AVALIACOES = 60      # abaixo disso a clínica não define padrão
MIN_DIFERENCA = 1.4      # razão mínima para chamar de vantagem, não de ruído
TETO_NA_REDE = 6         # quantas lojas a leitura de REDE lista por eixo

# Categorias do Google que NÃO disputam paciente de aparelho.
FORA = re.compile(r"centro m[ée]dico|m[ée]dico|hospital|laborat[óo]rio|"
                  r"est[ée]tica|harmoniza|implante", re.I)


def sa(s):
    return "".join(c for c in unicodedata.normalize("NFD", s or "")
                   if unicodedata.category(c) != "Mn").lower()


# O que se procura no texto do paciente. Cada eixo é uma coisa que a clínica
# FAZ — não um elogio genérico. "Ótimo atendimento" não ensina nada; "explicou
# tudo antes" ensina.
EIXOS = {
    "explica_o_tratamento": (
        "Explica o que vai fazer, antes de fazer",
        r"explic|esclarec|tirou (todas as )?(minha|as) d[úu]vida|detalh|"
        r"mostrou o que|me orientou|orienta[çc][ãa]o"),
    "hora_marcada_e_hora": (
        "Atende na hora marcada",
        r"pontual|no hor[áa]rio|sem espera|r[áa]pido|n[ãa]o esperei|"
        r"fui atendid. na hora"),
    "preco_claro": (
        "Diz o preço de forma clara, e cabe no bolso",
        r"pre[çc]o justo|valor justo|acess[íi]vel|cabe no bolso|"
        r"sem surpresa|or[çc]amento claro|barato|em conta"),
    "acolhimento_do_medo": (
        "Cuida de quem tem medo de dentista",
        r"medo|receio|p[âa]nico|trauma|ansiedade|me acalm|paci[êe]ncia"),
    "resolve_no_mesmo_dia": (
        "Resolve no mesmo dia",
        r"mesmo dia|no ato|na hora|imediat|encaix"),
    "trata_crianca": (
        "Sabe atender criança",
        r"crian[çc]a|filh|meu filho|minha filha|pequen|infantil|adolescent"),
    "pos_venda": (
        "Continua presente depois que vendeu",
        r"retorno|acompanh|manuten[çc][ãa]o|p[óo]s|voltei|sempre que preciso"),
    "gente_com_nome": (
        "Tem profissional que o paciente chama pelo nome",
        r"\bdr[a]?\.?\s+[a-z]|doutor|doutora|a\s+[A-Z][a-z]+\s+(me|foi|explic)"),
}
RX = {k: re.compile(v[1], re.I) for k, v in EIXOS.items()}


def rotulo_da_loja(x):
    """'RS · Caxias do Sul · Kayser'. Sem a marca, que é igual em todas."""
    nome = (x.get("unidade") or "").replace("OrthoDontic", "").strip(" ·-–—")
    cidade = (x.get("rotulo") or "").split("·")[-1].strip()
    if nome.lower() == cidade.lower():
        nome = ""
    elif nome.lower().startswith(cidade.lower() + " "):
        nome = nome[len(cidade):].strip(" ·-–—")
    return x["rotulo"] + (f" · {nome}" if nome else "")


def perfil(revs):
    """A proporção de avaliações que menciona cada eixo. Proporção, não soma —
    senão a clínica maior 'ganha' em tudo só por ser maior."""
    com_texto = [r for r in revs if (r.get("texto") or "").strip()]
    if not com_texto:
        return None, 0
    out = {}
    for k, rx in RX.items():
        out[k] = sum(1 for r in com_texto if rx.search(sa(r["texto"])))/len(com_texto)
    return out, len(com_texto)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--praca")
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()

    ident, linhas = coleta()
    cat = {}
    for c in jsonl("categoria"):
        cat[c.get("place_id")] = c

    revs = defaultdict(list)
    for r in reviews_unicos():
        revs[(r.get("praca_id"), r.get("local_id"))].append(r)

    saida = []
    for p in sorted(ident):
        if a.praca and p != a.praca:
            continue
        d = ident[p]
        locais = {l["local_id"]: l for l in d.get("locais", [])}
        nossas = [x for x in linhas if x["praca"] == p and x["papel"] == "proprio"]
        if not nossas:
            continue

        # UMA LINHA POR UNIDADE, nunca a praça somada. Cuiabá tem três lojas
        # e Londrina duas, e nem sempre é o mesmo dono — a média das três
        # não diz nada para nenhum dos três franqueados. A comparação certa
        # é a loja DELE contra o rival da cidade dele.
        proprias = [(lid, l) for lid, l in locais.items()
                    if l.get("papel") == "proprio"]

        # os rivais que valem comparação
        rivais = []
        for x in sorted([y for y in linhas if y["praca"] == p
                         and y["papel"] != "proprio" and y["ritmo"]],
                        key=lambda y: -y["ritmo"]):
            l = locais.get(x["local_id"], {})
            # O veredito de produto vem carimbado na identidade por
            # produto_do_concorrente.py (nome + voz do cliente). É mais forte
            # que o regex de nome/categoria que morava aqui: clínica geral e
            # implante dividem a rua, não o paciente de aparelho.
            prod = l.get("produto") or {}
            if prod.get("disputa_aparelho") != "sim":
                porque = prod.get("porque") or "sem veredito de produto"
                if not any(r.get("fora") and r["nome"] == x["nome"] for r in rivais):
                    rivais.append({"nome": x["nome"], "fora": True,
                                   "por_que_fora": porque})
                continue
            rv = revs.get((p, x["local_id"]), [])
            pf, n = perfil(rv)
            if not pf or n < MIN_AVALIACOES:
                continue
            rivais.append({"nome": x["nome"], "ritmo": x["ritmo"], "nota": x["nota"],
                           "posicao": x["posicao"], "avaliacoes_lidas": n,
                           "perfil": pf, "fora": False})
            if len([r for r in rivais if not r["fora"]]) >= 3:
                break

        dentro = [r for r in rivais if not r["fora"]]
        if not dentro:
            # Estado vazio é conteúdo: praça sem rival de aparelho comparável
            # não some da tela — ela diz isso, que é leitura por si só.
            for lid, l in proprias:
                saida.append({"praca_id": p, "rotulo": d.get("rotulo"),
                              "local_id": lid, "unidade": l.get("unidade") or l.get("nome"),
                              "sem_comparacao_porque":
                                  "nenhum rival de APARELHO com amostra "
                                  "suficiente na praça — as clínicas medidas "
                                  "aqui são de outro produto",
                              "rivais_fora": [r for r in rivais if r["fora"]],
                              "rivais_fora_total":
                                  sum(1 for r in rivais if r["fora"]),
                              "vantagens_deles": []})
            continue

        for lid, l in proprias:
            meu, meu_n = perfil(revs.get((p, lid), []))
            if not meu or meu_n < MIN_AVALIACOES:
                if meu_n:
                    saida.append({"praca_id": p, "rotulo": d.get("rotulo"),
                                  "local_id": lid, "unidade": l.get("unidade") or l.get("nome"),
                                  "sem_comparacao_porque":
                                      f"só {meu_n} avaliações com texto — abaixo "
                                      f"do mínimo de {MIN_AVALIACOES}",
                                  "rivais_fora": [r for r in rivais if r["fora"]],
                                  "rivais_fora_total":
                                      sum(1 for r in rivais if r["fora"]),
                                  "vantagens_deles": []})
                continue
            vantagens = []
            for k, (nome, _) in EIXOS.items():
                melhor = max(dentro, key=lambda r: r["perfil"][k])
                if meu[k] <= 0:
                    continue
                razao = melhor["perfil"][k]/meu[k]
                if razao >= MIN_DIFERENCA:
                    vantagens.append({
                        "eixo": k, "o_que_e": nome, "quem": melhor["nome"],
                        "eles": round(100*melhor["perfil"][k], 1),
                        "nos": round(100*meu[k], 1), "razao": round(razao, 1)})
            vantagens.sort(key=lambda x: -x["razao"])
            saida.append({"praca_id": p, "rotulo": d.get("rotulo"),
                          "local_id": lid, "unidade": l.get("unidade") or l.get("nome"),
                          "nossas_avaliacoes_lidas": meu_n,
                          "rivais_comparados": [r["nome"] for r in dentro],
                          "rivais_fora": [r for r in rivais if r["fora"]],
                          "rivais_fora_total":
                              sum(1 for r in rivais if r["fora"]),
                          "vantagens_deles": vantagens,
                          "nosso_perfil": {k: round(100*v, 1) for k, v in meu.items()}})

    print(f"\n{'='*80}\n  O QUE O RIVAL FAZ QUE DÁ CERTO — na voz do paciente dele"
          f"\n{'='*80}")
    for s in saida:
        etiq = s["rotulo"] + (" · " + s["unidade"] if s.get("unidade") else "")
        if s.get("sem_comparacao_porque"):
            print(f"\n  {etiq}  — sem comparação: {s['sem_comparacao_porque']}")
            continue
        print(f"\n  {etiq}   ({s['nossas_avaliacoes_lidas']} avaliações nossas "
              f"contra {', '.join(s['rivais_comparados'][:3])})")
        for f in s["rivais_fora"]:
            print(f"     ⊘ fora da comparação: {f['nome'][:44]} — {f['por_que_fora']}")
        if not s["vantagens_deles"]:
            print("     nenhuma vantagem acima do corte — a praça está equilibrada")
        for v in s["vantagens_deles"][:5]:
            print(f"     → {v['o_que_e']}")
            print(f"        {v['quem'][:44]}: {v['eles']}% contra {v['nos']}% nossos "
                  f"({v['razao']}x)")

    # ------------------------------------------------------ a leitura de REDE
    #
    # Perder num eixo numa praça é problema daquela unidade. Perder no MESMO
    # eixo em cinco praças de cinco estados é decisão de franqueadora: vira
    # treinamento, roteiro de atendimento, protocolo — não visita.
    rede = []
    for k, (nome, _) in EIXOS.items():
        # todas as linhas aqui são nossas, e todas se chamam OrthoDontic:
        # repetir a marca 373 vezes na mesma coluna é ruído. Fica o que
        # distingue a loja — e, quando a praça tem uma só, fica o rótulo.
        onde = [(rotulo_da_loja(x), v)
                for x in saida for v in x.get("vantagens_deles", [])
                if v["eixo"] == k]
        if not onde:
            continue
        nossos = [x["nosso_perfil"][k] for x in saida if x.get("nosso_perfil")]
        # UMA LINHA POR LOJA NÃO SOBREVIVE À REDE. São 45 lojas hoje e 373
        # quando a medição alcançar a rede inteira: oito eixos × 373 linhas
        # é uma tela que ninguém rola. O que decide é o TAMANHO do buraco e
        # onde ele é pior — então a lista publicada é a das piores, com o
        # total pronto ao lado. O resto não some: está em `pracas` de cada
        # praça, na tela da unidade, que é onde o franqueado abre.
        piores = sorted(onde, key=lambda rv: -rv[1]["razao"])[:TETO_NA_REDE]
        rede.append({
            "eixo": k, "o_que_e": nome,
            "perde_em": len(onde), "de": len(saida),
            "frase": (conta(len(onde), "loja", "lojas") + " de "
                      + conta(len(saida), "medida", "medidas")),
            "pior_razao": max(v["razao"] for _, v in onde),
            "nosso_pior": min(nossos), "nosso_melhor": max(nossos),
            "piores": [{"rotulo": r, "razao": v["razao"], "quem": v["quem"]}
                       for r, v in piores],
            "piores_total": len(onde),
            "frase_ver_todas": (f"ver as {len(onde)} lojas"
                                if len(onde) > len(piores) else None),
            "de_quem_e_a_decisao": ("franqueadora" if len(onde) >= len(saida)-1
                                    else "unidade"),
        })
    rede.sort(key=lambda x: (-x["perde_em"], -x["pior_razao"]))

    print(f"\n{'='*80}\n  O PADRÃO DA REDE — onde perdemos em QUANTAS praças"
          f"\n{'='*80}\n")
    for r in rede:
        dono = ("← DECISÃO DE FRANQUEADORA" if r["de_quem_e_a_decisao"] == "franqueadora"
                else "")
        print(f"  {r['perde_em']}/{r['de']}  {r['o_que_e']:44s} até {r['pior_razao']}x  {dono}")
        print(f"        nós vamos de {r['nosso_pior']}% a {r['nosso_melhor']}% entre as praças")

    if a.salvar:
        PORTAL.mkdir(parents=True, exist_ok=True)
        (PORTAL/"rival.json").write_text(json.dumps({
            "o_que_e": "O que o concorrente que ganha faz, lido nas avaliações "
                       "dos pacientes DELE. Comparação por proporção, dentro da "
                       "mesma praça.",
            "o_que_nao_e": "Não é o que ele fatura nem o que ele gasta. É o que "
                           "o paciente dele escolheu escrever.",
            "corte_amostra": MIN_AVALIACOES, "corte_diferenca": MIN_DIFERENCA,
            "eixos": [{"chave": k, "o_que_e": v[0]} for k, v in EIXOS.items()],
            "padrao_da_rede": rede,
            "pracas": saida,
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n  → dados/portal/rival.json ({len(saida)} praças)")


if __name__ == "__main__":
    main()
