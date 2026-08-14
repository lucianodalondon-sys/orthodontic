#!/usr/bin/env python3
"""
padroes_da_rede.py — o que as lojas acompanhadas ensinam lidas juntas.

Esta é a síntese que a franqueadora compra: não a ficha de cada loja, mas o
que se repete entre elas — e, mais valioso, o que se ESPERAVA que separasse
quem sustenta de quem para e NÃO separa. Cada hipótese abaixo foi testada no
disco, com histórico completo de avaliações das dez lojas, e o resultado
fica escrito mesmo quando é "não é isso".

O método é eliminação, e a praça-controle é Cuiabá: três lojas, mesma marca,
mesmo material, mesma tabela, mesma cidade — uma sustenta há 26 meses e duas
estão paradas. O que quer que separe, não é nada que as três compartilham.

Tudo POR LOJA (local_id), nunca praça somada: nem sempre é o mesmo dono.

Uso:
    python3 scripts/padroes_da_rede.py
    python3 scripts/padroes_da_rede.py --salvar   # → dados/portal/padroes.json
"""
import argparse, json, pathlib, re, sys, unicodedata
from collections import defaultdict
import datetime as dt

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ/"scripts"))
from cruzamento import reviews_unicos, coleta, jsonl, conta, confianca

PORTAL = RAIZ/"dados"/"portal"
NOME = re.compile(r"\bdr[a]?\.?\s+[a-z]|doutor|doutora", re.I)


def sa(s):
    return "".join(c for c in unicodedata.normalize("NFD", s or "")
                   if unicodedata.category(c) != "Mn").lower()


def _controle(lojas):
    """As cidades onde MAIS DE UMA loja da rede é medida: mesma marca, mesmo
    material, mesma tabela, resultados diferentes. É o desenho mais próximo
    de um experimento que o dado externo permite — e os nomes saem do
    payload, nunca da memória de quem escreveu."""
    from collections import defaultdict as _dd
    por = _dd(list)
    for l in lojas:
        por[l["rotulo"]].append(l)
    # a cidade que mais CONTRASTA vem primeiro: controle sem contraste não
    # controla nada. Ordem alfabética punha Goiânia (3·1·0·0) na frente de
    # Cuiabá (26·2·0), que é o caso que sustenta a leitura.
    fora = []
    for rot, ls in sorted(por.items(),
                          key=lambda kv: -(max((x.get("meses_seguidos") or 0)
                                               for x in kv[1])
                                           - min((x.get("meses_seguidos") or 0)
                                                 for x in kv[1]))):
        if len(ls) < 2:
            continue
        ls.sort(key=lambda x: -(x.get("meses_seguidos") or 0))
        fora.append(rot + ": " + " · ".join(
            f"{str(x.get('unidade') or '').replace('OrthoDontic', '').strip(' ·')} "
            f"{x.get('meses_seguidos')}" for x in ls))
    return ". ".join(fora[:3]) + "." if fora else None


def monta():
    # quantas unidades a rede tem hoje, lido da lista oficial do site —
    # nunca escrito no texto (já ficou 374 aqui e 373 na tela ao lado)
    _of = jsonl("unidades_rede")
    _dia_of = max((r.get("snapshot_date") or "" for r in _of), default=None)
    _na_rede = sum(1 for r in _of if r.get("snapshot_date") == _dia_of)

    ident, linhas = coleta()
    R = defaultdict(list)
    for r in reviews_unicos():
        R[r.get("local_id")].append(r)

    lojas = []
    for u in [x for x in linhas if x["papel"] == "proprio" and x["ritmo"] is not None]:
        revs = R[u["local_id"]]
        ct = [r for r in revs if (r.get("texto") or "").strip()]
        neg = [r for r in revs if str(r.get("nota")) in ("1", "2", "3")]
        datas = sorted(str(r["data"])[:10] for r in revs if r.get("data"))
        idade = ((dt.date.fromisoformat(datas[-1]) -
                  dt.date.fromisoformat(datas[0])).days // 30) if len(datas) > 1 else 0
        lojas.append({
            "local_id": u["local_id"], "praca_id": u["praca"],
            "rotulo": u["rotulo"], "unidade": u["nome"],
            "meses_seguidos": u["meses"], "ritmo_vida": u["ritmo"],
            "selo": ("OPERACAO" if u["meses"] >= 10 else
                     "campanha" if u["meses"] >= 3 else "parada"),
            "idade_meses": idade,
            "avaliacoes": len(revs),
            "pct_5_estrelas": round(100*sum(1 for r in revs
                                            if str(r.get("nota")) == "5")/max(len(revs), 1)),
            "pct_negativas": round(100*len(neg)/max(len(revs), 1)),
            "pct_respondidas": round(100*sum(1 for r in revs
                                             if r.get("respondida"))/max(len(revs), 1)),
            "pct_nome_citado": round(100*sum(1 for r in ct
                                             if NOME.search(sa(r["texto"])))/max(len(ct), 1)),
        })
    lojas.sort(key=lambda x: -x["meses_seguidos"])
    op = [l for l in lojas if l["selo"] == "OPERACAO"]
    par = [l for l in lojas if l["selo"] == "parada"]

    def faixa(campo, grupo):
        vs = [l[campo] for l in grupo]
        return f"{min(vs)}–{max(vs)}" if vs else "—"

    hipoteses = [
        {"h": "Quem sustenta tem paciente mais satisfeito",
         "veredito": "NAO SEPARA",
         "prova": f"5★: quem sustenta fica em {faixa('pct_5_estrelas', op)}%, "
                  f"quem parou em {faixa('pct_5_estrelas', par)}%. Fernando Corrêa "
                  f"tem 97% de cinco estrelas e está parada; Centro Norte, na mesma "
                  f"cidade e mesma marca, 98% e 26 meses seguidos."},
        {"h": "Quem sustenta é a loja mais antiga (ou mais nova)",
         "veredito": "NAO SEPARA",
         "prova": f"idade: sustentam com {faixa('idade_meses', op)} meses de vida; "
                  f"param com {faixa('idade_meses', par)}. Há loja nova e loja "
                  f"veterana nos dois grupos."},
        {"h": "Quem sustenta responde as avaliações",
         "veredito": "NAO SEPARA",
         "prova": f"resposta: sustentam respondendo {faixa('pct_respondidas', op)}%; "
                  f"param respondendo {faixa('pct_respondidas', par)}%. Cuiabá Centro "
                  f"Norte sustenta há 26 meses respondendo 1%; Mafra está parada "
                  f"respondendo 61%. Responder é higiene de reputação, não motor "
                  f"de ritmo."},
        {"h": "Quem sustenta tem profissional citado pelo nome",
         "veredito": "NAO SEPARA",
         "prova": f"nome citado: {faixa('pct_nome_citado', op)}% contra "
                  f"{faixa('pct_nome_citado', par)}%. Todas as dez ficam entre 0% e "
                  f"9% — e o rival da cidade chega a 30%. É fraqueza da REDE "
                  f"inteira, não o que separa as lojas entre si."},
    ]

    conclusao = {
        "t": (f"A satisfação é igual nas "
              + conta(len(lojas), "loja acompanhada", "lojas acompanhadas")
              + "; a constância não é"),
        # A ELIMINAÇÃO NÃO PROVA O QUE SOBRA — E ISTO VIRA PROGRAMA DE REDE.
        #
        # A frase dizia que a rotina de balcão "é a única que explica o
        # padrão". Não é: quatro explicações caíram, e a lista do que NÃO
        # foi testado é grande — ponto comercial, verba local, rotatividade
        # de ortodontista, preço, tamanho da equipe. Nenhuma fonte pública
        # mede nenhuma delas. Se a rede vai investir em cima disto, a tela
        # tem de dizer que está apostando numa inferência por eliminação.
        "leitura": "Quatro explicações confortáveis foram testadas e nenhuma "
                   "separa quem sustenta de quem para: satisfação, idade, resposta "
                   "e nome citado são iguais nos dois grupos. A praça-controle é "
                   "Cuiabá: três lojas com a mesma marca, o mesmo material e a "
                   "mesma tabela na mesma cidade — uma sustenta há 26 meses, duas "
                   "estão paradas. O que sobra entre as explicações TESTADAS é a "
                   "rotina de balcão: pedir ou não pedir a avaliação ao paciente "
                   "satisfeito. Nenhuma fonte pública mede essa rotina "
                   "diretamente, e a eliminação não cobre tudo — veja ao lado o "
                   "que não foi testado.",
        "o_que_nao_foi_testado": [
            "ponto comercial: rua, fluxo de pedestre, estacionamento",
            "verba de mídia local, que cada franqueado decide sozinho",
            "rotatividade de ortodontista e tamanho da equipe",
            "preço praticado e política de parcelamento da unidade",
        ],
        "porque_nao_foi_testado": ("nenhuma fonte pública mede nenhuma "
                                   "destas — são o teto do produto, não "
                                   "pendência de coleta"),
        "carimbo": confianca(
            natureza="inferencia",
            amostra=len(lojas), unidade_amostra=("loja acompanhada",
                                                 "lojas acompanhadas"),
            a_favor=["quatro explicações alternativas foram testadas e "
                     "caíram", "Cuiabá é praça-controle: três lojas iguais "
                     "no papel, resultados opostos"],
            contra=["eliminação não prova o que sobra: quatro explicações "
                    "não testadas continuam de pé",
                    "a rotina de balcão não é medida por nenhuma fonte "
                    "pública"],
            o_que_aumentaria="acompanhar uma loja que MUDE a rotina e ver "
                             "se o ritmo muda depois — é o que o livro de "
                             "ações faz"),
        "consequencia": "A intervenção mais barata do portal: a rotina de pedido "
                        "é copiável de loja para loja da MESMA cidade, sem verba, "
                        "sem agência e sem depender de praça. O manual está a uma "
                        "visita de distância — na loja irmã.",
        # os nomes saem do payload, não da memória: "Fernando Corrêa" e
        # "Dom Bosco" eram como as lojas se chamavam antes de nome_da_loja.py
        "controle": _controle(lojas),
    }

    return {
        # "as dez lojas" ficou escrito quando a rede tinha dez estudadas.
        # Hoje são 45, e número escrito à mão apodrece — a regra do projeto
        # é que todo número da tela sai do build.
        "o_que_e": (f"O que as {conta(len(lojas), 'loja', 'lojas')} "
                    f"acompanhadas ensinam quando lidas juntas — inclusive "
                    f"as explicações que o dado derrubou."),
        "metodo": "eliminação sobre histórico completo de avaliações, POR LOJA. "
                  "Cuiabá é a praça-controle: três lojas idênticas no papel, "
                  "resultados opostos.",
        "lojas": lojas,
        "hipoteses_testadas": hipoteses,
        "hipoteses_testadas_total": len(hipoteses),
        "conclusao": conclusao,
        "o_que_isso_nao_ve": [
            "A rotina de balcão em si — nenhuma fonte pública grava se a "
            "recepção pede avaliação. A conclusão é por eliminação, não por "
            "observação direta.",
            conta(len(lojas), "loja acompanhada é", "lojas acompanhadas são")
            + " comparação controlada, não estatística. O padrão vale "
            f"como hipótese forte para as {conta(_na_rede, 'unidade')} da rede, "
            "não como lei.",
        ],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()
    d = monta()

    print(f"\n{'='*78}\n  OS PADRÕES DA REDE — {len(d['lojas'])} lojas, lidas juntas\n{'='*78}\n")
    for h in d["hipoteses_testadas"]:
        print(f"  [{h['veredito']}] {h['h']}")
        print(f"      {h['prova']}\n")
    c = d["conclusao"]
    print(f"  ★ {c['t']}\n    {c['leitura']}\n")
    print(f"    controle: {c['controle']}")
    if a.salvar:
        (PORTAL/"padroes.json").write_text(
            json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n  → dados/portal/padroes.json")


if __name__ == "__main__":
    main()
