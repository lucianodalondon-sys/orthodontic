#!/usr/bin/env python3
"""
a_rede_inteira.py — a rede inteira, não só as unidades medidas.

Por que existe
--------------
A crítica mais dura que o produto recebeu foi justa: "uma fila que ignora
97,3% da rede não prioriza a rede". Toda tela falava de 10 unidades.

A varredura completa cobre só parte das praças — é ela que dá voz do
paciente, concorrência e portas de busca. Mas a ficha pública de TODAS saiu
por uma
chamada por unidade na API do Google, e ela responde o que a franqueadora
pergunta primeiro: **onde a marca está mal na rua, agora.**

O que ele acha e ninguém achava
--------------------------------
  · a unidade que o Google marca como FECHADA PERMANENTEMENTE enquanto a
    lista oficial da rede diz que está aberta — isso é risco de marca, e só
    a franqueadora resolve
  · a unidade com nota abaixo de 4,0, nomeada
  · a unidade aberta sem NENHUMA avaliação: existe no papel e não existe
    para quem procura
  · a ficha cadastrada na categoria errada

O que ele NÃO faz, e está escrito na tela
------------------------------------------
Não mede ritmo. Ritmo exige a data de cada avaliação, e isso é a varredura
cara. Aqui é retrato: como a unidade aparece hoje. Nota alta com 9 avaliações
não é o mesmo que nota alta com 686 — por isso o volume anda junto da nota
em toda linha.

Uso:
    python3 scripts/a_rede_inteira.py
    python3 scripts/a_rede_inteira.py --salvar
"""
import argparse, json, pathlib, statistics as st, sys
from collections import Counter, defaultdict

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ/"scripts"))
from cruzamento import jsonl, conta, confianca
from insight import monta as monta_insight

# O QUE FAZER COM CADA ALERTA. Sem isto a tela é um painel de sistema:
# quatro números grandes e nenhuma instrução.
CONSERTO = {
    "fechada_no_google": dict(
        titulo="A ficha está marcada como fechada no Google",
        acao="pedir a reativação da ficha no Google Meu Negócio — a "
             "unidade está aberta na lista oficial da rede",
        importa="ficha fechada some do mapa: quem procura não encontra, e "
                "quem encontra acha que a clínica não existe mais",
        custo="sem custo de mídia", prazo=7,
        nao_faca="não criar ficha nova por cima: duplicar perde as "
                 "avaliações já acumuladas"),
    "sem_nenhuma_avaliacao": dict(
        titulo="Unidade aberta e sem nenhuma avaliação",
        acao="rodar o pacote de abertura — ficha completa e as primeiras "
             "avaliações pedidas no fim do atendimento",
        importa="existe no papel e não existe para quem procura: sem "
                "avaliação a ficha não aparece na busca do bairro",
        custo="sem custo de mídia", prazo=60),
    "nota_baixa": dict(
        titulo="Nota abaixo do que a rede pratica",
        acao="ler as avaliações negativas com a equipe e responder todas, "
             "começando pelas com texto",
        importa="a nota é a primeira coisa que o paciente vê, antes do "
                "endereço e antes do preço",
        custo="sem custo de mídia", prazo=14,
        nao_faca="não pedir para apagar avaliação: responder muda o que o "
                 "próximo lê, apagar não"),
    "categoria_divergente": dict(
        titulo="Categoria da ficha diferente do resto da rede",
        acao="trocar a categoria principal da ficha para a que o resto da "
             "rede usa",
        importa="a categoria decide em que busca a ficha entra: errada, a "
                "unidade some das buscas que trazem paciente de aparelho",
        custo="sem custo de mídia", prazo=7),
}

PORTAL = RAIZ/"dados"/"portal"

NOTA_RUIM = 4.0        # abaixo disso a ficha pública trabalha contra a marca
POUCA_VOZ = 20         # com menos que isto, a nota não sustenta leitura


def monta():
    F = jsonl("rede_fichas")
    if not F:
        sys.exit("dados/serie/rede_fichas.jsonl vazio — rode "
                 "coleta/coletores/rede_inteira.py --todas --salvar")
    corte = max(x["snapshot_date"] for x in F)
    F = [x for x in F if x["snapshot_date"] == corte]
    ok = [x for x in F if x.get("confirmada")]
    nao = [x for x in F if not x.get("confirmada")]

    notas = [x["nota"] for x in ok if x.get("nota")]
    avs = [x.get("avaliacoes") or 0 for x in ok]

    def linha(x, por_que):
        return {"cidade": x["cidade"], "uf": x["uf"],
                "unidade": x.get("unidade_na_lista"),
                "nome_no_google": x.get("nome"),
                "nota": x.get("nota"), "avaliacoes": x.get("avaliacoes"),
                "endereco": x.get("endereco"), "mapa": x.get("mapa"),
                "situacao_na_lista": x.get("situacao_na_lista"),
                "situacao_google": x.get("situacao_google"),
                "por_que": por_que}

    # ---------------------------------------------------------- os alertas
    alertas = []

    fechadas = [x for x in ok if x.get("situacao_google") != "OPERATIONAL"]
    for x in fechadas:
        alertas.append({**linha(x, "o Google marca esta ficha como FECHADA "
                                   "PERMANENTEMENTE, e a lista oficial da rede "
                                   "diz que a unidade está aberta"),
                        "gravidade": "vermelha", "chave": "fechada_no_google",
                        "de_quem_e": "franqueadora"})

    sem_voz = [x for x in ok if not x.get("avaliacoes")
               and x.get("situacao_na_lista") == "aberta"]
    for x in sem_voz:
        alertas.append({**linha(x, "unidade aberta sem NENHUMA avaliação: "
                                   "existe no papel e não existe para quem procura"),
                        "gravidade": "vermelha", "chave": "sem_nenhuma_avaliacao",
                        "de_quem_e": "franqueadora"})

    ruins = sorted([x for x in ok if x.get("nota") and x["nota"] < NOTA_RUIM],
                   key=lambda x: x["nota"])
    for x in ruins:
        base = ("e com base fina, o que ainda dá conserto rápido"
                if (x.get("avaliacoes") or 0) < POUCA_VOZ
                else f"sobre {x['avaliacoes']} avaliações, o que já é reputação firmada")
        alertas.append({**linha(x, f"nota {x['nota']} na ficha pública, {base}"),
                        "gravidade": "vermelha" if x["nota"] < 3.5 else "amarela",
                        "chave": "nota_baixa", "de_quem_e": "unidade"})

    tipos = Counter(x.get("tipo") for x in ok)
    fora_de_categoria = [x for x in ok if x.get("tipo") != tipos.most_common(1)[0][0]]
    for x in fora_de_categoria:
        alertas.append({**linha(x, f"ficha cadastrada como '{x.get('tipo')}' enquanto "
                                   f"{tipos.most_common(1)[0][1]} unidades da rede usam "
                                   f"'{tipos.most_common(1)[0][0]}'"),
                        "gravidade": "amarela", "chave": "categoria_divergente",
                        "de_quem_e": "unidade"})

    ordem = {"vermelha": 0, "amarela": 1}
    alertas.sort(key=lambda x: (ordem.get(x["gravidade"], 9), x.get("nota") or 9))

    # ALERTA SEM AÇÃO É BOLETIM. Cada um destes é conserto de vitrine, e
    # quase todos são de graça — mas ninguém conserta o que não diz o que
    # fazer nem para quem mandar.
    for x in alertas:
        c = CONSERTO[x["chave"]]
        x["o_que_fazer"] = c["acao"]
        x["custo"] = c["custo"]
        x["prazo_dias"] = c["prazo"]
        x["insight"] = monta_insight(
            fonte="ficha", chave=f"{x['uf']}|{x['cidade']}|{x['chave']}",
            titulo=c["titulo"],
            onde=f"{x['uf']} · {x['cidade']}"
                 + (f" · {x['unidade']}" if x.get("unidade") else ""),
            fato=x["por_que"],
            por_que_importa=c["importa"],
            acao=c["acao"],
            # "franqueadora" é o dono do problema; o público que recebe é
            # a diretoria — os dois vocabulários existem e não se misturam
            publico=("diretoria" if x["de_quem_e"] == "franqueadora"
                     else "franqueado"),
            gravidade="alta" if x["gravidade"] == "vermelha" else "media",
            nao_faca=c.get("nao_faca"),
            revisar_em=c["prazo"],
            evidencias=([{"o_que": "ficha no mapa", "texto": x["mapa"]}]
                        if x.get("mapa") else []),
            link=x.get("mapa"),
            carimbo=confianca(
                natureza="fato",
                amostra=x.get("avaliacoes"),
                unidade_amostra=("avaliação", "avaliações"),
                fonte="ficha pública do Google",
                a_favor=["é o que qualquer paciente vê ao procurar a "
                         "unidade"],
                contra=["a ficha é retrato do dia da coleta; se alguém "
                        "corrigiu ontem, o portal só vê na próxima"]))

    # QUANTAS PRAÇAS A VARREDURA COMPLETA COBRE — contado, não escrito.
    # Estava "13 praças" no texto enquanto a identidade já tinha 17.
    _of = jsonl("unidades_rede")
    _dia_of = max((r.get("snapshot_date") or "" for r in _of), default=None)
    _na_lista_oficial = sum(1 for r in _of if r.get("snapshot_date") == _dia_of)

    _pracas_varridas = {r.get("praca_id") for r in jsonl("categoria")
                        if r.get("praca_id")}
    _n_varridas = conta(len(_pracas_varridas), "praça", "praças")

    por_uf = defaultdict(lambda: {"unidades": 0, "notas": []})
    for x in ok:
        d = por_uf[x["uf"]]
        d["unidades"] += 1
        if x.get("nota"):
            d["notas"].append(x["nota"])

    return {
        "corte": corte,
        "o_que_e": "A ficha pública de cada unidade da rede, pela API do Google. "
                   "Uma chamada por unidade.",
        "o_que_nao_e": "Não é ritmo nem voz do paciente — para isso é a varredura "
                       f"completa, que hoje cobre {_n_varridas}. Aqui é retrato: como a "
                       "unidade aparece agora para quem procura.",
        # O TAMANHO DA REDE SAI DA LISTA OFICIAL, NÃO DA VARREDURA.
        # Aqui dizia 374 — o número de FICHAS lidas — enquanto a lista
        # oficial do site tem 373 e as outras duas telas diziam 373. A
        # varredura de fichas repete linha (Guaíba e Vitória da Conquista
        # aparecem duas vezes), então contar ficha não conta unidade.
        "na_lista_oficial": _na_lista_oficial,
        "fichas_lidas": len(F),
        "porque_duas_contagens": (
            "a lista oficial do site é o cadastro; a varredura de fichas é o "
            "enriquecimento, e ela pode repetir ou faltar linha. Quando os "
            "dois números divergem, o cadastro manda."),
        "confirmadas": len(ok),
        "nao_confirmadas": len(nao),
        "por_que_nao_confirma": "a busca só aceita ficha cujo NOME contenha "
                                "'orthodontic' e cujo ENDEREÇO seja da cidade "
                                "procurada. Devolver menos e certo é melhor que "
                                "devolver tudo com lixo dentro.",
        "nota_mediana": round(st.median(notas), 1) if notas else None,
        "nota_pior": min(notas) if notas else None,
        "avaliacoes_somadas": sum(avs),
        "avaliacoes_medianas": int(st.median(avs)) if avs else None,
        "abaixo_de_4": len(ruins),
        "alertas": alertas,
        "alertas_total": len(alertas),
        "por_uf": sorted([{"uf": k, "unidades": v["unidades"],
                           "nota_mediana": round(st.median(v["notas"]), 1)
                                           if v["notas"] else None}
                          for k, v in por_uf.items()],
                         key=lambda x: -x["unidades"]),
        "nao_confirmadas_lista": [{"cidade": x["cidade"], "uf": x["uf"],
                                   "por_que": x.get("nao_confirmada_porque")}
                                  for x in nao],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()
    d = monta()

    print(f"\n{'='*78}\n  A REDE INTEIRA — {d['confirmadas']} de "
          f"{d['na_lista_oficial']} fichas conferidas\n{'='*78}\n")
    print(f"  nota mediana {d['nota_mediana']} · pior {d['nota_pior']} · "
          f"{d['avaliacoes_somadas']:,} avaliações somadas".replace(",", "."))
    print(f"  {d['abaixo_de_4']} unidades com nota abaixo de 4,0\n")

    verm = [x for x in d["alertas"] if x["gravidade"] == "vermelha"]
    print(f"  {len(verm)} ALERTA(S) VERMELHO(S)\n")
    for x in verm:
        print(f"   ● {x['cidade']}/{x['uf']:2s} · {x.get('unidade') or ''}")
        print(f"     {x['por_que']}")
        print(f"     nota {x.get('nota')} · {x.get('avaliacoes')} aval · "
              f"resolve: {x['de_quem_e']}\n")

    print(f"  amarelos: {len([x for x in d['alertas'] if x['gravidade']=='amarela'])}")
    print(f"\n  {d['nao_confirmadas']} não confirmadas — {d['por_que_nao_confirma'][:70]}…")

    if a.salvar:
        PORTAL.mkdir(parents=True, exist_ok=True)
        (PORTAL/"rede_inteira.json").write_text(
            json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n  → dados/portal/rede_inteira.json")


if __name__ == "__main__":
    main()
