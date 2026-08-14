#!/usr/bin/env python3
"""
pipeline_expansao.py — o Radar vira funil comercial.

A troca
-------
Hoje existem duas telas: o funil nacional (a régua barata sobre os 5.570
municípios) e o radar (as cidades estudadas a fundo). São dois pedaços da
mesma pergunta, e quem vende franquia precisa dos dois na mesma linha:

    5.570 municípios
      ↓  triagem demográfica e de porte
    50 candidatas
      ↓  conferência: a rede já está lá?
    N para investigar
      ↓  varredura da categoria + estudo escrito
    6 estudadas
      ↓  conferida em duas fontes, categoria fraca
    N recomendadas para avançar

Cada degrau mostra quantas passaram e QUANTAS CAÍRAM, com o motivo. O funil
existe para tornar o descarte visível — sem isso, "6 cidades estudadas"
parece pouco, quando na verdade é o que sobrou de 5.570.

O que ele NÃO faz
-----------------
Não projeta faturamento, não promete retorno e não diz "abra aqui". A
saída é "esta cidade merece o próximo passo, e o próximo passo é este".

Uso:
    python3 scripts/pipeline_expansao.py
    python3 scripts/pipeline_expansao.py --salvar
"""
import argparse, json, pathlib, sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ/"scripts"))
from cruzamento import conta, confianca
from insight import monta as monta_insight

PORTAL = RAIZ/"dados"/"portal"

MUNICIPIOS_BR = 5570


def carrega(nome):
    p = PORTAL/f"{nome}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def monta():
    fn = carrega("funil_nacional")
    rd = carrega("radar")
    if not fn.get("candidatas") or not rd.get("oportunidades"):
        print("  ✗ FALHA: funil_nacional.json ou radar.json vazio.\n"
              "  rode antes: python3 scripts/funil_nacional.py --salvar e "
              "python3 scripts/radar_oportunidade.py --salvar")
        sys.exit(1)

    candidatas = fn["candidatas"]
    estudadas = rd["oportunidades"]
    ocupadas = rd.get("ja_tem_unidade", [])
    nao_conferidas = rd.get("nao_conferidas", [])

    # recomendada = estudada, conferida nas DUAS fontes, e com leitura de
    # oportunidade. Cidade não conferida não entra em recomendação — é a
    # regra que existe desde que "a rede não está em Juazeiro" saiu errado.
    def conferida(c):
        e = (c.get("conferencia") or {}).get("estado")
        return e in (None, "livre", "conferida")

    recomendadas = [c for c in estudadas
                    if conferida(c)
                    and "OPORTUNIDADE" in str(c.get("leitura") or "").upper()]

    # de onde veio cada cidade estudada: da régua, ou por outro caminho
    _cand = {c["rotulo"] for c in candidatas}
    _est = {c["rotulo"] for c in estudadas + ocupadas}
    da_regua = _est & _cand
    fora_da_regua = _est - _cand

    degraus = [
        {"degrau": "municípios brasileiros", "quantos": MUNICIPIOS_BR,
         "o_que_e": "a base inteira do IBGE"},
        {"degrau": "candidatas pela régua demográfica",
         "quantos": len(candidatas),
         "o_que_e": "porte, público-alvo por faixa etária e renda relativa",
         "cairam": MUNICIPIOS_BR - len(candidatas),
         "porque_caem": "cidade pequena demais para sustentar uma unidade "
                        "de aparelho, pela própria régua da rede"},
        {"degrau": "estudadas a fundo", "quantos": len(estudadas) + len(ocupadas),
         "o_que_e": "varredura da categoria na cidade e estudo escrito",
         # O FUNIL NÃO É UMA FILA ÚNICA, E FINGIR QUE É SERIA MENTIRA.
         # Das cidades estudadas, só parte veio da régua demográfica; as
         # outras entraram por outro caminho (praça onde a rede já está,
         # ou pedido direto). Escrever "50 → 13" sugeriria que uma é
         # subconjunto da outra, e não é.
         "vieram_da_regua": len(da_regua),
         "vieram_por_outro_caminho": len(fora_da_regua),
         "quais_por_outro_caminho": sorted(fora_da_regua),
         "porque_dois_caminhos": ("a régua demográfica alimenta a fila de "
                                  "estudo, mas não é a única porta: praça "
                                  "onde a rede já está e pedido direto da "
                                  "diretoria também entram"),
         "ainda_nao_estudadas_da_regua": len(candidatas) - len(da_regua),
         "porque_caem": "as candidatas que ainda não foram estudadas "
                        "esperam a vez — o estudo custa cota de coleta e "
                        "roda por lote"},
        {"degrau": "com a praça livre", "quantos": len(estudadas),
         "o_que_e": "a rede não está na cidade, conferido em duas fontes",
         "cairam": len(ocupadas),
         "porque_caem": "a rede já tem unidade lá — a conferência na lista "
                        "oficial e na busca por nome derrubou"},
        {"degrau": "recomendadas para avançar", "quantos": len(recomendadas),
         "o_que_e": "cidade grande com categoria fraca, pronta para o "
                    "próximo passo",
         "cairam": len(estudadas) - len(recomendadas),
         "porque_caem": "a categoria local já está consolidada, ou a "
                        "conferência não fechou"},
    ]

    cidades = []
    for c in estudadas:
        e = (c.get("conferencia") or {}).get("estado")
        pronta = c in recomendadas
        cidades.append({
            "rotulo": c["rotulo"], "cidade": c.get("cidade"),
            "uf": c.get("uf"),
            "estado_no_funil": ("avançar" if pronta else
                                "estudada, sem recomendação"),
            "leitura": c.get("leitura"),
            "populacao": c.get("populacao"),
            "alvo_30_45": c.get("alvo_30_45"),
            "alvo_9_15": c.get("alvo_9_15"),
            "clinicas_fortes": c.get("clinicas_fortes"),
            "lider_avaliacoes": c.get("lider_avaliacoes"),
            "por_que": c.get("defesa") or [],
            "por_que_total": len(c.get("defesa") or []),
            "conferencia": c.get("conferencia"),
            # O RISCO É PARTE DO ARGUMENTO. Um candidato a franqueado que
            # sabe fazer conta desconfia de dossiê sem risco.
            "riscos": _riscos(c),
            "proximo_passo": ("avaliar as regiões dentro da cidade e montar "
                              "o dossiê de território"
                              if pronta else
                              "não avançar por enquanto: a leitura da "
                              "categoria não sustenta"),
            "insight": monta_insight(
                fonte="expansao", chave=c["rotulo"],
                titulo=c.get("leitura") or "Cidade estudada",
                onde=c["rotulo"],
                fato=(f"{c.get('populacao'):,} habitantes".replace(",", ".")
                      + f" · {conta(c.get('clinicas_fortes') or 0, 'clínica forte', 'clínicas fortes')}"
                      + f" · o líder local tem {c.get('lider_avaliacoes')} avaliações"),
                por_que_importa=("cidade grande com categoria fraca é onde "
                                 "uma unidade entra sem disputar espaço já "
                                 "construído"
                                 if pronta else
                                 "a categoria local já tem líder "
                                 "consolidado, e entrar ali é disputar "
                                 "espaço construído"),
                acao=("abrir o dossiê de território e avaliar as regiões "
                      "dentro da cidade antes de qualquer conversa comercial"
                      if pronta else
                      "manter no acervo e reavaliar na próxima varredura"),
                publico="expansao",
                gravidade="media" if pronta else "baixa",
                evidencias=[{"texto": t} for t in (c.get("defesa") or [])[:3]],
                nao_faca=("não apresentar isto como projeção de "
                          "faturamento: é leitura de mercado observável, "
                          "não previsão de resultado"),
                link=f"radar/{c.get('cidade')}",
                carimbo=confianca(
                    natureza="fato",
                    amostra=c.get("clinicas_amostradas"),
                    unidade_amostra=("clínica varrida", "clínicas varridas"),
                    fonte="IBGE + varredura da categoria",
                    a_favor=["a ausência da rede foi conferida em duas "
                             "fontes independentes"],
                    contra=["ponto comercial, aluguel e disponibilidade de "
                            "profissional não são medidos por fonte "
                            "pública"])),
        })
    cidades.sort(key=lambda x: (x["estado_no_funil"] != "avançar",
                                -(x["populacao"] or 0)))

    return {
        "o_que_e": "O caminho de uma cidade até virar conversa comercial: "
                   "dos 5.570 municípios até as que merecem o próximo "
                   "passo.",
        "por_que_importa": ("'6 cidades estudadas' parece pouco. Mostrado o "
                            "funil, é o que sobrou de 5.570 — e cada "
                            "descarte tem motivo escrito"),
        "o_que_nao_e": ("não é projeção de faturamento nem garantia de que "
                        "abrir ali funciona. A saída é 'esta cidade merece "
                        "o próximo passo', e o passo está dito"),
        "degraus": degraus,
        "degraus_total": len(degraus),
        "manchete": (conta(len(recomendadas), "cidade pronta para avançar",
                           "cidades prontas para avançar")
                     + f", de {len(estudadas) + len(ocupadas)} estudadas"),
        "cidades": cidades,
        "cidades_total": len(cidades),
        "recomendadas_total": len(recomendadas),
        "nao_conferidas": nao_conferidas,
        "nao_conferidas_total": len(nao_conferidas),
        "porque_nao_conferidas": ("cidade cuja ausência da rede não foi "
                                  "confirmada nas duas fontes não entra em "
                                  "recomendação — foi assim que 'a rede não "
                                  "está em Juazeiro' saiu errado"),
        "onde_cabem_mais": fn.get("onde_cabem_mais", [])[:6],
        "onde_cabem_mais_total": len(fn.get("onde_cabem_mais", [])),
        "o_que_e_onde_cabem_mais": ("cidades onde a rede JÁ está e a régua "
                                    "dela indica folga — expansão dentro "
                                    "de praça conhecida, que é o caminho "
                                    "mais barato"),
    }


def _riscos(c):
    """O que pesa contra, dito antes que o candidato pergunte."""
    r = []
    if (c.get("clinicas_fortes") or 0) >= 3:
        r.append("a cidade já tem mais de duas clínicas fortes — entrar "
                 "aqui é disputar espaço construído")
    if (c.get("lider_avaliacoes") or 0) >= 1500:
        r.append(f"o líder local tem {c['lider_avaliacoes']} avaliações; "
                 f"reputação acumulada não se alcança com mídia")
    if c.get("uf_sem_nenhuma_unidade"):
        r.append("o estado inteiro não tem unidade da rede: não há "
                 "vizinha para apoiar abertura, e a marca é desconhecida "
                 "na praça")
    r.append("ponto comercial, aluguel e disponibilidade de ortodontista "
             "não são medidos por nenhuma fonte pública — isto o portal "
             "não vê")
    return r


def imprime(d):
    print(f"\n{'='*78}\n  PIPELINE DE EXPANSÃO — {d['manchete']}\n{'='*78}\n")
    for g in d["degraus"]:
        print(f"  {g['quantos']:>6}  {g['degrau']}")
        if g.get("vieram_da_regua") is not None:
            print(f"          · {g['vieram_da_regua']} vieram da régua, "
                  f"{g['vieram_por_outro_caminho']} por outro caminho")
        if g.get("cairam"):
            print(f"          ↓ {g['cairam']} caíram: {g['porque_caem']}")
    print()
    for c in d["cidades"]:
        marca = "→" if c["estado_no_funil"] == "avançar" else " "
        print(f"  {marca} {c['rotulo']:<26}{c['leitura'][:44]}")
        print(f"      próximo passo: {c['proximo_passo'][:64]}")
        print(f"      riscos: {len(c['riscos'])} declarados")
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()
    d = monta()
    imprime(d)
    if a.salvar:
        (PORTAL/"pipeline_expansao.json").write_text(
            json.dumps(d, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8")
        print(f"  → dados/portal/pipeline_expansao.json")


if __name__ == "__main__":
    main()
