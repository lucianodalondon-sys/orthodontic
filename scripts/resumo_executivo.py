#!/usr/bin/env python3
"""
resumo_executivo.py — a home deixa de ser um catálogo de ferramentas.

O erro que ele conserta
-----------------------
O Painel de Controle oferecia mapa, alertas, reputação, o que mudou, fila,
busca perto da clínica, avaliações sem resposta, rival, anúncios, padrões,
timeline, constância, funil, radar, praças, voz da cidade, busca, fichas,
território, achados e planos. Vinte e três portas — e várias delas são
visões diferentes da MESMA matéria-prima. O resultado é que a home e a
página da clínica pareciam a mesma coisa, e que a diretoria abria o portal
sem saber o que fazer com ele.

A página da CLÍNICA responde "o que está acontecendo com esta unidade?".

A home tem de responder outra pergunta, completamente diferente:

    o que está acontecendo na REDE que eu não perceberia olhando loja por
    loja?

"13 unidades vermelhas" e "399 avaliações esperando resposta" não
respondem isso: são contagens operacionais. "Em 5 de 5 mercados
comparáveis o rival vencedor é lembrado pelo nome dos profissionais de
2,1x a 5x mais que nós" responde.

O que a home passa a ser
------------------------
Cinco perguntas, e nada mais:

    1. o que a rede aprendeu?          → rede_aprende.py
    2. onde intervir esta semana?      → agenda_do_consultor.py
    3. o que o concorrente mexeu?      → mudancas_do_mercado.py
    4. o que dá para testar?           → playbook + padrão ganhando força
    5. onde crescer?                   → radar_oportunidade.py

Cada item é um INSIGHT no contrato de `insight.py`: fato, por que importa,
quem age, o que fazer e o texto pronto para encaminhar. Nenhuma ferramenta
é repetida na home — ela cruza todas.

Uso:
    python3 scripts/resumo_executivo.py
    python3 scripts/resumo_executivo.py --salvar
"""
import argparse, json, pathlib, sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ/"scripts"))
from cruzamento import conta
from insight import monta as monta_insight, resumo as resumo_insights

PORTAL = RAIZ/"dados"/"portal"

# Quantos cabem em cada bloco. A home inteira tem de caber numa tela: mais
# de doze cartões e ela volta a ser catálogo.
TETO = {"descobertas": 3, "unidades": 5, "movimentos": 2,
        "testar": 3, "cidades": 2}


def carrega(nome):
    p = PORTAL/f"{nome}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _descobertas():
    """O que a rede aprendeu — só o que tem decisão pendurada."""
    d = carrega("rede_aprende")
    out = []
    for x in d.get("descobertas", []):
        if x["nivel"] != "confirmado" or not x.get("decisao_sugerida"):
            continue
        out.append(monta_insight(
            fonte="aprendizado", chave=x["titulo"],
            titulo=x["titulo"],
            onde="rede inteira",
            fato=(f"{x['placar']} praças medidas. "
                  + (x.get("leitura") or x["porque_neste_nivel"])),
            por_que_importa=x["o_que_significa"],
            acao=x["decisao_sugerida"],
            publico=("diretoria" if x["dono_da_decisao"] == "franqueadora"
                     else "consultor"),
            gravidade="alta",
            evidencias=[{"texto": f"{e['onde']}: {e['valor']}"}
                        for e in x.get("evidencias", [])],
            carimbo=x.get("carimbo"),
            link="rede_aprende",
            medido_em=None))
    return out[:TETO["descobertas"]]


def _unidades():
    """Onde intervir — a agenda já vem pronta e ordenada."""
    d = carrega("agenda")
    return [x["insight"] for x in d.get("esta_semana", [])][:TETO["unidades"]]


def _movimentos():
    """O que o concorrente mexeu. Só o que é comparável e muda decisão."""
    d = carrega("mudancas_do_mercado")
    out = []
    for e in d.get("eventos", []):
        if e.get("severidade") not in ("critica", "alta"):
            continue
        # linha de base não é movimento: é a primeira medição da praça
        if str(e.get("tipo", "")).startswith("linha_de_base"):
            continue
        out.append(monta_insight(
            fonte="mercado", chave=e.get("evento_id") or e.get("titulo"),
            titulo=e.get("titulo"),
            onde=e.get("rotulo"),
            fato=e.get("fato") or e.get("titulo"),
            por_que_importa=(e.get("por_que_importa")
                             or "movimento de concorrente na praça onde a "
                                "rede tem unidade"),
            acao=(e.get("o_que_fazer")
                  or "levar o movimento para a próxima conversa com a "
                     "unidade, antes de responder com verba"),
            publico="consultor",
            gravidade="alta" if e.get("severidade") == "critica" else "media",
            medido_em=e.get("data"),
            link=f"pracas/{e.get('praca_id')}"))
    return out[:TETO["movimentos"]]


def _testar():
    """O que dá para testar: posição vaga repetida e padrão ganhando força."""
    out = []
    pb = carrega("playbook")
    for v in pb.get("posicoes_vagas", [])[:2]:
        if v["pracas"] < 3:
            continue
        out.append(monta_insight(
            fonte="playbook", chave=v["posicao"],
            titulo="Posição vaga no discurso do mercado",
            onde=conta(v["pracas"], "praça", "praças"),
            fato=(f"{v['posicao']} Isso se repete em "
                  f"{conta(v['pracas'], 'praça medida', 'praças medidas')}."),
            por_que_importa=("posição que ninguém ocupa é a mais barata de "
                             "ocupar: não há leilão em cima dela"),
            acao=("testar esta mensagem em duas praças e remedir as "
                  "mesmas frases de busca depois"),
            publico="marketing", gravidade="media",
            link="playbook"))
    ap = carrega("rede_aprende")
    for x in ap.get("descobertas", []):
        if x["nivel"] != "ganhando_forca" or not x.get("decisao_sugerida"):
            continue
        out.append(monta_insight(
            fonte="aprendizado", chave=x["titulo"],
            titulo=x["titulo"], onde="rede inteira",
            fato=f"{x['placar']} — {x['porque_neste_nivel']}",
            por_que_importa=(x.get("o_que_significa")
                             or "padrão que ainda não é regra, mas já "
                                "aparece na maioria das praças medidas"),
            acao=x["decisao_sugerida"],
            publico="marketing", gravidade="media",
            evidencias=[{"texto": f"{e['onde']}: {e['valor']}"}
                        for e in x.get("evidencias", [])],
            carimbo=x.get("carimbo"), link="rede_aprende"))
    return out[:TETO["testar"]]


def _cidades():
    """Onde crescer — só cidade conferida nas duas fontes."""
    d = carrega("radar")
    out = []
    for c in d.get("oportunidades", []):
        conf = c.get("conferencia") or {}
        if conf.get("estado") not in (None, "livre", "conferida"):
            continue
        out.append(monta_insight(
            fonte="radar", chave=c["rotulo"],
            titulo=c.get("leitura") or "Cidade para estudar",
            onde=c["rotulo"],
            fato=(f"{c['populacao']:,} habitantes".replace(",", ".")
                  + f" · {conta(c.get('clinicas_fortes') or 0, 'clínica forte', 'clínicas fortes')}"
                  + f" · líder local com {c.get('lider_avaliacoes')} avaliações"),
            por_que_importa=("cidade grande com categoria fraca é onde uma "
                             "unidade nova entra sem disputar espaço já "
                             "construído"),
            acao=("abrir o dossiê de território e avaliar as regiões "
                  "dentro da cidade antes de qualquer conversa comercial"),
            publico="expansao", gravidade="media",
            evidencias=[{"texto": t} for t in (c.get("defesa") or [])[:3]],
            link=f"radar/{c.get('cidade')}"))
    return out[:TETO["cidades"]]


def monta():
    blocos = [
        {"chave": "descobertas",
         "titulo": "O que a rede aprendeu",
         "pergunta": "o que sabemos hoje que não sabíamos antes?",
         "abre": "rede_aprende", "itens": _descobertas()},
        {"chave": "unidades",
         "titulo": "Onde intervir esta semana",
         "pergunta": "qual unidade não pode esperar?",
         "abre": "agenda", "itens": _unidades()},
        {"chave": "movimentos",
         "titulo": "O que o concorrente mexeu",
         "pergunta": "o que mudou na rua desde a última medição?",
         "abre": "mudancas_do_mercado", "itens": _movimentos()},
        {"chave": "testar",
         "titulo": "O que dá para testar",
         "pergunta": "onde há espaço que ninguém está ocupando?",
         "abre": "playbook", "itens": _testar()},
        {"chave": "cidades",
         "titulo": "Onde crescer",
         "pergunta": "que cidade merece estudo antes das outras?",
         "abre": "radar", "itens": _cidades()},
    ]
    for b in blocos:
        b["quantos"] = len(b["itens"])
        b["frase"] = conta(len(b["itens"]), "coisa para decidir",
                           "coisas para decidir")
        # ESTADO VAZIO É CONTEÚDO: bloco sem item diz por quê, e não some
        b["vazio_porque"] = (None if b["itens"] else
                             VAZIO.get(b["chave"]))
    todos = [i for b in blocos for i in b["itens"]]
    return {
        "o_que_e": "O que a OrthoDontic precisa saber esta semana — o "
                   "cruzamento das ferramentas, não o índice delas.",
        "por_que_importa": ("a página da clínica responde o que acontece "
                            "com uma unidade. Esta responde o que acontece "
                            "na REDE que ninguém veria olhando loja por "
                            "loja"),
        "o_que_nao_e": ("não é atalho para as ferramentas. Nada aqui se "
                        "repete lá dentro: cada cartão é um cruzamento"),
        "a_regra": ("toda ferramenta do portal termina respondendo cinco "
                    "coisas: o que aconteceu, por que importa, quem "
                    "precisa agir, o que fazer e como encaminhar"),
        "manchete": (conta(len(todos), "coisa que a OrthoDontic precisa "
                           "saber esta semana",
                           "coisas que a OrthoDontic precisa saber esta "
                           "semana")),
        "blocos": blocos,
        "blocos_total": len(blocos),
        "itens_total": len(todos),
        "resumo": resumo_insights(todos),
        "teto_por_bloco": TETO,
    }


VAZIO = {
    "descobertas": "nenhuma descoberta confirmada mudou de estado desde a "
                   "última rodada",
    "unidades": "nenhuma unidade com ação aberta nesta rodada",
    "movimentos": "nenhum movimento comparável de concorrente nesta "
                  "rodada — praça com uma medição só tem linha de base, "
                  "que é diferente de 'não mudou'",
    "testar": "nenhuma posição vaga se repetiu em praças suficientes",
    "cidades": "nenhuma cidade conferida nas duas fontes está pronta para "
               "avançar",
}


def imprime(d):
    print(f"\n{'='*78}\n  INTELIGÊNCIA DA REDE — {d['manchete']}\n{'='*78}")
    for b in d["blocos"]:
        print(f"\n  ── {b['titulo'].upper()}  ({b['quantos']})")
        print(f"     {b['pergunta']}")
        if not b["itens"]:
            print(f"     (vazio: {b['vazio_porque']})")
        for i in b["itens"]:
            print(f"\n     {i['onde']}")
            print(f"     {i['titulo'][:70]}")
            print(f"       fato    {i['fato'][:88]}")
            print(f"       importa {(i['por_que_importa'] or '')[:88]}")
            print(f"       ação    {i['acao'][:88]}")
            print(f"       para    {i['quem_age_rotulo']}")
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()
    d = monta()
    imprime(d)
    if a.salvar:
        (PORTAL/"inteligencia_da_rede.json").write_text(
            json.dumps(d, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8")
        print(f"  → dados/portal/inteligencia_da_rede.json "
              f"({d['itens_total']} cartões)")


if __name__ == "__main__":
    main()
