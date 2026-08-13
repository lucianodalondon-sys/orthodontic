#!/usr/bin/env python3
"""
insight.py — o contrato que toda ferramenta do portal tem de cumprir.

A regra
-------
Toda ferramenta precisa terminar respondendo cinco coisas:

    O QUE ACONTECEU  →  POR QUE IMPORTA  →  QUEM PRECISA AGIR  →
    O QUE FAZER      →  COMO ENCAMINHO ISSO

Se não chega até a quinta, não é ferramenta: é dado, evidência ou detalhe
de outra ferramenta — e o lugar disso é dentro dela, não no menu.

Este arquivo é a peça única que monta esse objeto. Nenhum motor escreve o
próprio formato: todos chamam `monta()` daqui. É o que impede o portal de
voltar a ter vinte e três telas com vinte e três jeitos de dizer a mesma
coisa.

O ENCAMINHAMENTO
----------------
A quinta resposta é a que transforma o portal em ferramenta de trabalho. O
texto sai PRONTO do build, um por destinatário, porque a mesma descoberta
se conta de cinco jeitos:

    diretoria    o padrão, o tamanho dele, e a decisão que ele pede
    consultor    o que levar na visita e o que perguntar
    franqueado   o ponto de atenção na presença pública da unidade dele
    marketing    a oportunidade de execução, com o sinal que a sustenta
    expansão     por que a cidade avançou, e qual o próximo passo

E o que ele NÃO é: nada disso vira CRM. O portal não guarda para quem foi
mandado, quem leu nem quem executou — não temos essa informação e não
vamos ter. Encaminhar aqui é copiar um texto pronto. O único jeito de
saber se algo aconteceu continua sendo REMEDIR, que é o que o livro de
ações faz.

O que este arquivo se recusa a fazer
------------------------------------
  · inventar orçamento, retorno ou prazo que não esteja medido;
  · dizer que uma ação foi executada;
  · escrever recomendação com cara de medição — a ação vem carimbada
    como recomendação, sempre, ao lado do fato que vem carimbado como
    fato.

Uso (dentro de um motor):
    from insight import monta, PUBLICOS
    ins = monta(fonte="anomalias", chave=lid, titulo=..., fato=...,
                por_que_importa=..., acao=..., publico="consultor", ...)
"""
import hashlib
import re

# Quem pode receber. A lista é fechada de propósito: destinatário livre
# vira campo de texto, e campo de texto vira lugar onde alguém escreve
# nome de pessoa — que é dado interno.
PUBLICOS = {
    "diretoria":  "Franqueadora · diretoria",
    "consultor":  "Consultor de campo",
    "franqueado": "Franqueado da unidade",
    "marketing":  "Marketing e agência",
    "operacoes":  "Operações",
    "expansao":   "Expansão e comercial",
}

# Como cada um quer ouvir a mesma coisa. É a abertura do texto pronto —
# o corpo é o mesmo fato, a mesma evidência e a mesma ação.
ABERTURA = {
    "diretoria":  "Padrão observado na rede:",
    "consultor":  "Para a próxima visita:",
    "franqueado": "Ponto de atenção na presença pública da sua unidade:",
    "marketing":  "Oportunidade de execução, com o sinal que a sustenta:",
    "operacoes":  "Ponto recorrente de operação:",
    "expansao":   "Movimento no radar de expansão:",
}

GRAVIDADE = ("alta", "media", "baixa")


def _id(fonte, chave):
    """Identificador estável: a mesma descoberta na semana que vem tem o
    mesmo id, para dar para acompanhar sem guardar nada de dentro."""
    crua = f"{fonte}|{chave}"
    return f"{fonte}-" + hashlib.sha1(crua.encode("utf-8")).hexdigest()[:8]


def _limpa(s):
    return re.sub(r"\s+", " ", (s or "").strip())


def monta(*, fonte, chave, titulo, fato, por_que_importa, acao,
          publico, gravidade="media", evidencias=None, carimbo=None,
          onde=None, link=None, nao_faca=None, revisar_em=None,
          medido_em=None, o_que_perguntar=None):
    """O objeto que toda tela do portal desenha do mesmo jeito.

    fonte/chave  de que motor veio e sobre o quê — formam o `insight_id`
    fato         O QUE ACONTECEU, medido, com número
    por_que_importa  por que isso muda alguma decisão
    publico      QUEM PRECISA AGIR — uma chave de PUBLICOS
    acao         O QUE FAZER, e é RECOMENDAÇÃO, nunca medição
    """
    if publico not in PUBLICOS:
        raise ValueError(f"público desconhecido: {publico!r} — use um de "
                         f"{sorted(PUBLICOS)}")
    if gravidade not in GRAVIDADE:
        raise ValueError(f"gravidade desconhecida: {gravidade!r}")
    # AÇÃO SEM FATO É OPINIÃO SOLTA, E FATO SEM AÇÃO É BOLETIM. O contrato
    # existe justamente para não deixar passar nenhum dos dois.
    if not _limpa(fato):
        raise ValueError(f"insight sem fato: {fonte}/{chave}")
    if not _limpa(acao):
        raise ValueError(f"insight sem ação: {fonte}/{chave}")

    ev = list(evidencias or [])
    corpo = _corpo(onde, fato, por_que_importa, acao, ev, nao_faca,
                   revisar_em, link)
    return {
        "insight_id": _id(fonte, chave),
        "fonte": fonte,
        "titulo": _limpa(titulo),
        "onde": onde,
        # as cinco respostas, nesta ordem, sempre
        "fato": _limpa(fato),
        "por_que_importa": _limpa(por_que_importa),
        "quem_age": publico,
        "quem_age_rotulo": PUBLICOS[publico],
        "acao": _limpa(acao),
        "o_que_perguntar": _limpa(o_que_perguntar) or None,
        "nao_faca": _limpa(nao_faca) or None,
        "revisar_em_dias": revisar_em,
        "gravidade": gravidade,
        "evidencias": ev,
        "evidencias_total": len(ev),
        "medido_em": medido_em,
        "link": link,
        "carimbo": carimbo,
        # O TEXTO NÃO SE GUARDA SEIS VEZES.
        #
        # A primeira versão gravava a mensagem inteira uma vez por
        # destinatário. Como o corpo é o MESMO — muda só a linha de
        # abertura —, 62% do payload da home e 53% do da agenda eram
        # cópias da mesma frase. Agora vai o corpo uma vez, as seis
        # aberturas, e o texto pronto do destinatário recomendado.
        #
        # Juntar `abertura + corpo` na tela não é o casco calculando: as
        # duas metades são texto autorado e vêm prontas. Está declarado
        # aqui para ninguém "consertar" isso montando frase na tela.
        "encaminhamento": {
            "para": [{"chave": k, "rotulo": v, "abertura": ABERTURA[k]}
                     for k, v in PUBLICOS.items()],
            "recomendado": publico,
            "corpo": corpo,
            "texto_pronto": _limpa(ABERTURA[publico]) + "\n\n" + corpo,
            "como_montar": ("abertura do destinatário escolhido + linha em "
                            "branco + `corpo`. O texto do destinatário "
                            "recomendado já vem pronto em `texto_pronto`"),
            "como_usar": ("copiar e colar. O portal não guarda para quem "
                          "foi mandado nem se alguém executou — quem "
                          "responde isso é a próxima medição"),
        },
    }


def _corpo(onde, fato, importa, acao, ev, nao_faca, revisar, link):
    """O texto pronto, igual para todos os destinatários."""
    l = []
    if onde:
        l.append(f"*{onde}*")
    l.append(_limpa(fato))
    if _limpa(importa):
        l.append(f"Por que importa: {_limpa(importa)}")
    for e in ev[:3]:
        t = e.get("texto") if isinstance(e, dict) else str(e)
        if t:
            l.append(f"· {_limpa(t)}")
    l.append(f"Recomendação: {_limpa(acao)}")
    if _limpa(nao_faca):
        l.append(f"O que NÃO fazer: {_limpa(nao_faca)}")
    if revisar:
        l.append(f"Nova medição sugerida: {revisar} dias.")
    if link:
        l.append(f"Análise completa: {link}")
    l.append("— OrthoDontic Intelligence · leitura de fontes públicas, "
             "sem dado interno da rede")
    return "\n".join(l)


def resumo(insights):
    """O bloco de contagem que a home usa. Contado, nunca escrito."""
    from collections import Counter
    por_pub = Counter(i["quem_age"] for i in insights)
    por_grav = Counter(i["gravidade"] for i in insights)
    return {
        "total": len(insights),
        "por_publico": [{"chave": k, "rotulo": PUBLICOS[k],
                         "quantos": por_pub.get(k, 0)} for k in PUBLICOS],
        "por_gravidade": [{"gravidade": g, "quantos": por_grav.get(g, 0)}
                          for g in GRAVIDADE],
    }


if __name__ == "__main__":
    # o arquivo é biblioteca; rodar sozinho só mostra o contrato
    print(__doc__)
    print("  públicos:", ", ".join(f"{k} ({v})" for k, v in PUBLICOS.items()))
