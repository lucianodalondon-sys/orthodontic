#!/usr/bin/env python3
"""
rede_aprende.py — o que a rede DESCOBRIU, e com quanta força.

Por que esta camada existe
--------------------------
O portal responde muito bem "o que eu sei sobre esta clínica?". A pergunta
que faz uma franqueadora pagar por inteligência é outra:

    depois de observar dezenas de clínicas, milhares de pacientes e
    centenas de concorrentes, o que a OrthoDontic sabe hoje que não sabia
    antes — e o que deve fazer com isso?

Contagem operacional não responde isso. "13 unidades vermelhas" é
operação; "em 5 de 5 mercados comparáveis o rival vencedor é lembrado pelo
nome dos profissionais de 2,1x a 5x mais que nós" é conhecimento
proprietário — ninguém que raspe o Google amanhã tem isso, porque isso não
está no Google: está no cruzamento de 23 praças medidas do mesmo jeito.

O que este arquivo faz
----------------------
Lê os achados autorados e retestados e os organiza em QUATRO NÍVEIS DE
FORÇA, calculados do próprio placar — nunca escritos à mão:

    CONFIRMADO       passou em praticamente toda praça com amostra, e a
                     base é grande o bastante para não ser coincidência
    GANHANDO FORÇA   passa na maioria, com exceção NOMEADA
    EM TESTE         base pequena, ou não testável com o que temos hoje
    DERRUBADO        o dado contradisse, e isso fica na tela

O nível derrubado é o que dá crédito aos outros três. Uma lista onde nada
cai é curadoria, não medição.

O defeito que ele conserta
--------------------------
O resumo do arquivo dizia `constante: 0` enquanto vinte e oito achados
abaixo diziam `estado: "constante"`, e a mesma afirmação aparecia SETE
vezes com bases diferentes. Aqui o resumo é CONTADO dos itens, e afirmação
repetida não existe — `reteste.py` passou a substituir em vez de empilhar.

Uso:
    python3 scripts/rede_aprende.py
    python3 scripts/rede_aprende.py --salvar
"""
import argparse, json, pathlib, re, sys
from collections import Counter

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ/"scripts"))
from cruzamento import conta, confianca

CONT = RAIZ/"dados"/"conteudo"
PORTAL = RAIZ/"dados"/"portal"

# A régua dos níveis. Está aqui, escrita, porque nível de confiança que
# ninguém consegue conferir é opinião com cara de método.
BASE_MINIMA_CONFIRMADO = 8      # praças que votaram
TAXA_CONFIRMADO = 0.95          # quase toda praça com amostra
BASE_MINIMA_PADRAO = 5
TAXA_PADRAO = 0.75

NIVEIS = {
    "confirmado": {
        "titulo": "Confirmado na rede",
        "o_que_e": "passou em praticamente toda praça que teve amostra "
                   "para votar, e a base é grande o bastante para não ser "
                   "coincidência de amostra",
        "peso": 0},
    "ganhando_forca": {
        "titulo": "Padrão ganhando força",
        "o_que_e": "passa na maioria das praças, e a praça que contraria "
                   "está nomeada — padrão sem exceção soa a curadoria",
        "peso": 1},
    "em_teste": {
        "titulo": "Hipótese em teste",
        "o_que_e": "ou a base ainda é pequena, ou a afirmação não é "
                   "testável com o que medimos hoje. Fica na tela com o "
                   "motivo, porque saber o que NÃO tem lastro também é "
                   "informação",
        "peso": 2},
    "derrubado": {
        "titulo": "Derrubado pelo dado",
        "o_que_e": "a medição contradisse a explicação. É o nível que dá "
                   "crédito aos outros três",
        "peso": 3},
}

# O QUE O ACHADO SIGNIFICA E O QUE FAZER COM ELE.
#
# Texto autorado, e carimbado como RECOMENDAÇÃO — nunca como medição. O
# placar em cima é medido; a decisão embaixo é opinião informada, e as
# duas não podem parecer a mesma coisa.
DECISAO = {
    "A confiança é em gente com nome, não em marca": dict(
        significa="A marca institucional pode estar forte, e ainda assim a "
                  "confiança local estar sendo construída em PESSOAS. Onde "
                  "o paciente cita um profissional pelo nome, ele está "
                  "recomendando alguém, não uma placa.",
        decisao="Testar protagonismo dos ortodontistas em cinco unidades — "
                "nome e rosto na ficha do Google, na resposta às "
                "avaliações e no conteúdo local — e remedir em 60 dias.",
        dono="franqueadora"),
    "Perdemos para o rival no MESMO eixo em todas as praças: gente com nome":
        dict(
        significa="Perder no mesmo eixo em cinco estados não é problema de "
                  "unidade: unidade nenhuma escolhe isso sozinha. É "
                  "decisão de rede.",
        decisao="Levar a comparação impressa para a visita das cinco "
                "praças e combinar a resposta com o franqueado. O "
                "concorrente e a proporção dele já estão medidos.",
        dono="franqueadora"),
    "A porta de entrada é 'dentista', não 'aparelho'": dict(
        significa="O paciente que vira caso de aparelho quase nunca digita "
                  "'aparelho'. Ele digita 'dentista', marca uma avaliação "
                  "e sai com aparelho. Comprar só a palavra do produto é "
                  "disputar a menor das duas portas.",
        decisao="Revisar as frases de captação de cada praça: a lista de "
                "portas medidas da cidade está na tela da praça.",
        dono="franqueadora"),
    "O adulto 30+ é dinheiro na mesa e nenhuma praça fala com ele": dict(
        significa="Nas cidades analisadas a população adulta de 30 a 45 "
                  "anos é bem maior que a de 9 a 15 — e a comunicação da "
                  "categoria inteira fala com a segunda.",
        decisao="Testar uma frente de comunicação para adulto em duas "
                "praças, e medir pela mesma régua: portas de busca e "
                "ritmo de avaliação.",
        dono="franqueadora"),
    "O paciente não avalia ortodontia — avalia como foi tratado": dict(
        significa="Problema recorrente de recepção, contato e agendamento "
                  "deixa de ser caso isolado de franqueado quando aparece "
                  "em toda praça medida: vira pauta de rede.",
        decisao="Tratar os momentos que mais doem como programa de rede, "
                "não como visita. A tela da jornada mostra qual momento "
                "dói em cada loja.",
        dono="franqueadora"),
    "A ferida é sempre operação — nunca o produto": dict(
        significa="Ninguém reclama do aparelho. Reclama-se de como foi "
                  "atendido — e isso é consertável sem verba de mídia.",
        decisao="Blindar a operação antes de aumentar aquisição nas "
                "unidades em faixa vermelha.",
        dono="consultor de campo"),
}


def placar(n):
    """'23/23' → (23, 23). '—' e texto solto → (None, None)."""
    m = re.match(r"^\s*(\d+)\s*/\s*(\d+)\s*$", str(n or ""))
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)


def nivel(a):
    """O nível sai do placar, nunca do rótulo antigo."""
    if a.get("estado") == "derrubada":
        return "derrubado", "a medição contradisse a explicação"
    passou, base = placar(a.get("n"))
    if base is None:
        return "em_teste", (a.get("por_que_nao")
                            or "não é testável com o que medimos hoje")
    taxa = passou/base if base else 0
    if base >= BASE_MINIMA_CONFIRMADO and taxa >= TAXA_CONFIRMADO:
        return "confirmado", (f"passou em {passou} das "
                              f"{conta(base, 'praça que votou', 'praças que votaram')}")
    if base >= BASE_MINIMA_PADRAO and taxa >= TAXA_PADRAO:
        return "ganhando_forca", (f"passou em {passou} de {base} — "
                                  + (conta(len(a.get('excecoes') or []),
                                           "exceção nomeada", "exceções nomeadas")
                                     if a.get("excecoes")
                                     else "sem exceção nomeada"))
    return "em_teste", (f"passou em {passou} de {base}: base pequena ou "
                        f"taxa baixa demais para chamar de padrão")


def monta():
    d = json.loads((CONT/"achados.json").read_text(encoding="utf-8"))
    brutos = d.get("achados", [])

    # AFIRMAÇÃO REPETIDA NÃO EXISTE. Se voltar a existir, este guarda
    # grita — foi assim que 17 afirmações viraram 39 linhas na tela.
    vezes = Counter(x.get("t") for x in brutos)
    repetidas = [t for t, n in vezes.items() if n > 1]
    if repetidas:
        print("  ✗ FALHA: afirmação repetida nos achados — a camada que "
              "sintetiza está duplicando:")
        for t in repetidas:
            print(f"      {vezes[t]}x  {t}")
        print("\n  conserto: python3 scripts/reteste.py --salvar")
        sys.exit(1)

    itens = []
    for a in brutos:
        niv, porque = nivel(a)
        passou, base = placar(a.get("n"))
        chave = a.get("t")
        dec = DECISAO.get(chave)
        itens.append({
            "titulo": chave,
            "nivel": niv,
            "placar": a.get("n"),
            "passou": passou, "base": base,
            "porque_neste_nivel": porque,
            "leitura": a.get("leitura"),
            "como_se_mede": a.get("como_se_mede"),
            "evidencias": [{"onde": e[0], "valor": e[1]}
                           for e in (a.get("ev") or []) if len(e) == 2][:6],
            "evidencias_total": len(a.get("ev") or []),
            "excecoes": a.get("excecoes") or [],
            "sem_amostra": a.get("sem_amostra") or [],
            "derrubada_por": a.get("derrubada_por"),
            # a decisão é OPINIÃO, e vai carimbada como tal
            "o_que_significa": (dec or {}).get("significa"),
            "decisao_sugerida": (dec or {}).get("decisao"),
            "dono_da_decisao": (dec or {}).get("dono"),
            "carimbo_da_decisao": (
                confianca(natureza="recomendacao",
                          a_favor=["o placar em cima é medido"],
                          contra=["o que fazer com ele é opinião "
                                  "informada, e o portal não sabe se foi "
                                  "executado"],
                          o_que_aumentaria="remedir a mesma métrica depois "
                                           "do prazo, como no livro de ações")
                if dec else None),
            "carimbo": confianca(
                natureza=("fato" if niv in ("confirmado", "derrubado")
                          else "inferencia" if niv == "ganhando_forca"
                          else "hipotese"),
                amostra=base, unidade_amostra=("praça", "praças"),
                medicoes=2 if niv == "confirmado" else 1,
                a_favor=[porque],
                contra=[f"{len(a.get('excecoes') or [])} praça(s) contrariam"]
                       if a.get("excecoes") else [],
                medido=base is not None,
                o_que_aumentaria=("medir mais praças do mesmo jeito"
                                  if base else
                                  "criar a medição que testa esta "
                                  "afirmação")),
        })

    itens.sort(key=lambda x: (NIVEIS[x["nivel"]]["peso"], -(x["base"] or 0)))
    por_nivel = Counter(x["nivel"] for x in itens)

    forte = [x for x in itens if x["nivel"] == "confirmado"]
    manchete = (
        conta(len(forte), "padrão confirmado", "padrões confirmados")
        + " na rede, "
        + conta(por_nivel.get("derrubado", 0),
                "explicação derrubada pelo dado",
                "explicações derrubadas pelo dado")
        if forte else
        "nenhum padrão confirmado ainda — a base ainda é curta")

    return {
        "o_que_e": "O que a OrthoDontic descobriu observando as praças "
                   "medidas — e com quanta força cada descoberta se "
                   "sustenta.",
        "por_que_importa": ("qualquer um coleta o Google. Isto é o "
                            "cruzamento de 23 praças medidas do mesmo "
                            "jeito, e é o que não se copia raspando "
                            "fonte pública"),
        "o_que_nao_e": ("não é causa. Nenhuma linha aqui prova que fazer X "
                        "produz Y: são padrões observados, e um deles já "
                        "caiu quando a base cresceu"),
        "como_o_nivel_e_calculado": {
            "confirmado": f"base ≥ {BASE_MINIMA_CONFIRMADO} praças e "
                          f"{int(TAXA_CONFIRMADO*100)}% delas passando",
            "ganhando_forca": f"base ≥ {BASE_MINIMA_PADRAO} praças e "
                              f"{int(TAXA_PADRAO*100)}% passando",
            "em_teste": "base menor que isso, ou não testável com o que "
                        "medimos hoje",
            "derrubado": "a medição contradisse",
            "quem_calcula": "o placar do reteste, nunca um rótulo escrito "
                            "à mão",
        },
        "manchete": manchete,
        "niveis": [dict(NIVEIS[k], chave=k, quantos=por_nivel.get(k, 0),
                        frase=conta(por_nivel.get(k, 0), "descoberta",
                                    "descobertas"))
                   for k in ("confirmado", "ganhando_forca", "em_teste",
                             "derrubado")],
        "descobertas_total": len(itens),
        "descobertas": itens,
        "nota_do_reteste": d.get("nota_teto"),
    }


def imprime(d):
    print(f"\n{'='*78}\n  O QUE A REDE ESTÁ NOS ENSINANDO\n{'='*78}\n")
    print(f"  {d['manchete']}\n")
    for n in d["niveis"]:
        if not n["quantos"]:
            continue
        print(f"  ── {n['titulo'].upper()}  ({n['quantos']})")
        for x in d["descobertas"]:
            if x["nivel"] != n["chave"]:
                continue
            print(f"     {str(x['placar'] or '—')[:9]:<10}{x['titulo'][:62]}")
            print(f"                {x['porque_neste_nivel'][:62]}")
            if x["decisao_sugerida"]:
                print(f"                → {x['decisao_sugerida'][:60]}")
        print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()
    d = monta()
    imprime(d)
    if a.salvar:
        (PORTAL/"rede_aprende.json").write_text(
            json.dumps(d, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8")
        print(f"  → dados/portal/rede_aprende.json "
              f"({d['descobertas_total']} descobertas)")


if __name__ == "__main__":
    main()
