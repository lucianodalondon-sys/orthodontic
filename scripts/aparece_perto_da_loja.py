#!/usr/bin/env python3
"""
aparece_perto_da_loja.py — lê a busca com viés de local, POR LOJA.

O PROBLEMA QUE ISTO CONSERTA. `onde_cada_loja_aparece.py` mede a cidade
inteira a partir de um ponto só e devolve, para as quatro unidades de São
Paulo, "aparece em 0 de 193 buscas". A frase é verdadeira e a conclusão que
ela sugere — "as lojas da capital são invisíveis" — é falsa. Ninguém em São
Paulo disputa "dentista São Paulo"; o paciente busca de onde está.

Medindo com o viés no endereço de cada loja (`coleta/coletores/perto_da_loja.py`),
a mesma São Paulo devolveu 10 de 20: uma unidade em 1º lugar nas cinco
frases, outra fora em quatro. São diagnósticos opostos para lojas da mesma
cidade — e é a diferença entre mandar quatro franqueados fazer a mesma
coisa e mandar um só.

AS DUAS LEITURAS CONVIVEM, E DIZEM COISAS DIFERENTES

    cidade  → a loja disputa a cidade toda?  (vale em Mafra, mente em SP)
    perto   → a loja aparece para o vizinho? (vale em toda parte)

Nenhuma das duas substitui a outra, e a tela mostra as duas com o nome do
que cada uma mede.

O QUE ISTO NÃO DIZ

· Não é volume: continua sem saber quanta gente digita a frase.
· O raio NÃO é área de captação — distância no mapa não é deslocamento.
· Ficar atrás de um vizinho não é perder paciente para ele. Posição é
  posição; canibalização não está medida.

Uso:
    python3 scripts/aparece_perto_da_loja.py
    python3 scripts/aparece_perto_da_loja.py --salvar
"""
import argparse, json, pathlib, sys
import datetime as dt
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from cruzamento import identidades, conta, confianca

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SERIE = RAIZ/"dados"/"serie"/"perto_da_loja.jsonl"
SAIDA = RAIZ/"dados"/"portal"/"perto_da_loja.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()

    if not SERIE.exists():
        print("  nenhuma medição com viés de local ainda — "
              "coleta/coletores/perto_da_loja.py")
        return
    linhas = [json.loads(l) for l in SERIE.read_text(encoding="utf-8").split("\n")
              if l.strip()]
    if not linhas:
        print("  ✗ FALHA: arquivo existe e está vazio")
        sys.exit(1)

    # É SEMPRE A ÚLTIMA MEDIÇÃO DE CADA PRAÇA, nunca a última data do
    # arquivo: cortar pela data global apagaria toda praça não medida hoje.
    corte = {}
    for r in linhas:
        p = r.get("praca_id")
        corte[p] = max(corte.get(p, ""), r.get("snapshot_date") or "")
    atuais = [r for r in linhas if r["snapshot_date"] == corte.get(r["praca_id"])]

    # O NOME VEM DA IDENTIDADE DE HOJE, não da linha gravada na coleta.
    # A série guarda o nome do dia em que mediu — e no dia em que São Paulo
    # foi medida as quatro unidades ainda se chamavam "OrthoDontic". Ler o
    # nome do histórico devolveria as quatro linhas idênticas de volta.
    ident = identidades()
    nome_de = {l["local_id"]: (l.get("unidade") or l.get("nome"))
               for pr in ident.values() for l in pr.get("locais", [])}
    por_loja = defaultdict(list)
    for r in atuais:
        por_loja[r["local_id"]].append(r)

    lojas = []
    for lid, rs in por_loja.items():
        rs.sort(key=lambda r: r["frase"])
        de = len(rs)
        aparece = [r for r in rs if r.get("nossa_posicao")]
        primeiro = [r for r in aparece if r["nossa_posicao"] == 1]
        pos = [r["nossa_posicao"] for r in aparece]
        raio = rs[0].get("raio_m")
        km = raio/1000 if raio else None
        # quem aparece na frente da gente, e quantas vezes — sem chamar
        # isso de roubo de paciente, que é afirmação que não temos
        antes = defaultdict(int)
        for r in rs:
            p = r.get("nossa_posicao") or 99
            for q in r.get("quem") or []:
                if q["posicao"] < p and q.get("place_id") != r.get("place_id"):
                    antes[q.get("nome") or "?"] += 1
        vizinhos = [{"nome": k, "vezes_na_frente": v}
                    for k, v in sorted(antes.items(), key=lambda x: -x[1])[:5]]

        # A FRASE NÃO PODE PROMETER MAIS DO QUE A MEDIÇÃO ENTREGA.
        #
        # Ela dizia "nem para quem está a 3 km dela". Não foi isso que
        # medimos: fizemos CINCO buscas com o centro no endereço da clínica
        # e um viés de 3 km. Não testamos os consumidores dentro do raio, e
        # o próprio `locationBias` é uma preferência, não uma barreira — o
        # Google devolve resultado de fora do círculo e devolve. Dizer "nem
        # para quem está a 3 km" transforma cinco consultas em cobertura
        # geográfica, que é exatamente o tipo de salto que este projeto
        # existe para não dar.
        if not aparece:
            frase = (f"não apareceu no mapa em nenhuma das "
                     f"{conta(de, 'busca testada', 'buscas testadas')} feitas "
                     f"a partir do próprio endereço")
        elif len(primeiro) == de:
            frase = (f"a clínica é o primeiro resultado nas "
                     f"{conta(de, 'busca testada', 'buscas testadas')} feitas "
                     f"a partir do próprio endereço")
        else:
            frase = (f"aparece em {len(aparece)} de {de} buscas "
                     f"feitas a partir do próprio endereço, "
                     + (f"em {conta(len(primeiro), 'vez', 'vezes')} em 1º lugar"
                        if primeiro else
                        f"melhor posição: {min(pos)}º"))

        lojas.append({
            "local_id": lid,
            "praca_id": rs[0].get("praca_id"),
            "rotulo": rs[0].get("rotulo"),
            "unidade": nome_de.get(lid) or rs[0].get("unidade"),
            "medido_em": rs[0].get("snapshot_date"),
            "raio_m": raio,
            "de": de,
            "aparece_em": len(aparece),
            "em_primeiro": len(primeiro),
            "melhor_posicao": min(pos) if pos else None,
            "invisivel_perto": not aparece,
            "frase": frase,
            "buscas": [{"frase": r["frase"], "intencao": r.get("intencao"),
                        "posicao": r.get("nossa_posicao"),
                        "topo": ((r.get("quem") or [{}])[0] or {}).get("nome"),
                        "topo_avaliacoes": ((r.get("quem") or [{}])[0] or {}).get("avaliacoes"),
                        "topo_metros": ((r.get("quem") or [{}])[0] or {}).get("metros_do_centro")}
                       for r in rs],
            "quem_aparece_na_frente": vizinhos,
            "confianca": confianca(
                "fato", amostra=de,
                unidade_amostra=("busca testada", "buscas testadas"),
                medicoes=1,
                janela_dias=0,
                fonte="dados/serie/perto_da_loja.jsonl",
                o_que_aumentaria="repetir a mesma grade noutra data, ou "
                                 "aumentar o número de frases por loja"),
        })

    lojas.sort(key=lambda x: (x["aparece_em"]/max(x["de"], 1), x["em_primeiro"]))

    # A COMPARAÇÃO COM A LEITURA DE CIDADE É O ACHADO, não um detalhe.
    cidade = {}
    p = RAIZ/"dados"/"portal"/"presenca_por_loja.json"
    if p.exists():
        cidade = {x["local_id"]: x
                  for x in json.loads(p.read_text(encoding="utf-8")).get("lojas", [])}
    viradas = []
    for x in lojas:
        c = cidade.get(x["local_id"])
        if not c or not c.get("de"):
            continue
        x["na_cidade"] = {"aparece_em": c.get("aparece_em"), "de": c.get("de")}
        if not c.get("aparece_em") and x["aparece_em"]:
            viradas.append(x)

    print(f"  {conta(len(lojas), 'loja medida', 'lojas medidas')} com viés no "
          f"próprio endereço, em "
          f"{conta(len({x['praca_id'] for x in lojas}), 'praça')}")
    print(f"    {sum(1 for x in lojas if x['invisivel_perto'])} não aparecem "
          f"nem perto de si mesmas")
    print(f"    {sum(x['em_primeiro'] for x in lojas)} buscas com a loja em 1º")
    if viradas:
        print(f"\n  {conta(len(viradas), 'loja')} que a leitura de cidade "
              f"chamava de invisível e aparece perto de si:")
        for x in viradas[:8]:
            print(f"    {x['rotulo']} · {(x['unidade'] or '')[:26]:26s} "
                  f"cidade {x['na_cidade']['aparece_em']}/{x['na_cidade']['de']} "
                  f"→ perto {x['aparece_em']}/{x['de']}")
    for x in lojas[:6]:
        print(f"\n  {x['rotulo']} · {(x['unidade'] or '')[:30]}")
        print(f"    {x['frase']}")

    if not a.salvar:
        print("\n  (--salvar para gravar)")
        return
    SAIDA.write_text(json.dumps({
        "o_que_e": "Se a clínica aparece no mapa do Google para quem busca "
                   "a poucos quarteirões dela — a busca é feita a partir do "
                   "endereço da própria clínica, não do centro da cidade.",
        "por_que_existe": "a leitura de cidade responde bem em cidade pequena "
                          "e mente em metrópole: as quatro unidades de São "
                          "Paulo apareciam em 0 de 193 buscas da capital e "
                          "aparecem em 10 de 20 quando a busca sai da porta "
                          "de cada uma",
        "o_que_nao_e": "são cinco buscas por loja, não a cobertura de um "
                       "raio: o viés de local é uma preferência que damos ao "
                       "Google, não uma barreira geográfica. Não é volume de "
                       "busca; o raio não é área de captação, "
                       "porque distância no mapa não é tempo de deslocamento; "
                       "e ficar atrás de um vizinho não é perder paciente "
                       "para ele",
        "medido_em": max(corte.values()),
        "corte_por_praca": corte,
        "lojas": lojas,
        "lojas_total": len(lojas),
        "invisiveis_perto": sum(1 for x in lojas if x["invisivel_perto"]),
        "viradas_pela_leitura_de_perto": [x["local_id"] for x in viradas],
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n  → {SAIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
