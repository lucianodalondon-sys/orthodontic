#!/usr/bin/env python3
"""
caixa_de_respostas.py — as avaliações negativas sem resposta, uma a uma.

A única leitura que a revisão externa classificou como "SIM" sem ressalva:
responder reclamação pública é objetivo, tem dono, tem prazo, e o dado traz
tudo — texto, nota, data, se foi respondida e quando. Não é score: é a lista
do que está aberto, da mais recente para a mais antiga.

Regra de escopo: SÓ unidades da rede. Praça de estudo não tem franqueado para
responder — entra aqui e vira o erro dos seis planos de novo.

O que o histórico completo mudou: a fila saltou de 75 para o número real.
Com amostra truncada, a maior parte das negativas antigas simplesmente não
estava no disco.

Uso:
    python3 scripts/caixa_de_respostas.py
    python3 scripts/caixa_de_respostas.py --salvar
"""
import argparse, json, pathlib, sys
from collections import defaultdict

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ/"scripts"))
from cruzamento import reviews_unicos, identidades

PORTAL = RAIZ/"dados"/"portal"


def monta():
    ident = identidades()          # SÓ rede — praça de estudo fica fora
    nossos = {}
    for p, d in ident.items():
        for l in d.get("locais", []):
            if l.get("papel") == "proprio":
                nossos[l["local_id"]] = {"praca_id": p, "rotulo": d.get("rotulo"),
                                         "unidade": l.get("nome")}

    caixa = defaultdict(list)
    respondidas = defaultdict(int)
    for r in reviews_unicos():
        lid = r.get("local_id")
        if lid not in nossos:
            continue
        if str(r.get("nota")) not in ("1", "2", "3"):
            continue
        if r.get("respondida"):
            respondidas[lid] += 1
            continue
        caixa[lid].append({
            "nota": r.get("nota"), "data": str(r.get("data") or "")[:10],
            "texto": (r.get("texto") or "").strip() or None,
            "tem_texto": bool((r.get("texto") or "").strip()),
        })

    unidades = []
    for lid, itens in caixa.items():
        itens.sort(key=lambda x: x["data"] or "", reverse=True)
        m = nossos[lid]
        unidades.append({
            **m, "local_id": lid,
            "abertas": len(itens),
            "com_texto": sum(1 for x in itens if x["tem_texto"]),
            "ja_respondidas": respondidas.get(lid, 0),
            "itens": itens,
        })
    unidades.sort(key=lambda x: -x["abertas"])

    total = sum(u["abertas"] for u in unidades)
    com_texto = sum(u["com_texto"] for u in unidades)
    return {
        "o_que_e": "Toda avaliação de 1 a 3 estrelas das unidades da rede que "
                   "está SEM resposta, da mais recente para a mais antiga.",
        "a_regra": "Responder não é o que faz a unidade sustentar — Cuiabá "
                   "sustenta há 26 meses respondendo 1%. Responder é higiene "
                   "de reputação: a mãe lê os comentários antes de escolher, "
                   "e a reclamação sem resposta é a versão dela dos fatos.",
        "prazo_sugerido": "48 horas para as com texto; as só-estrela podem "
                          "receber resposta padrão.",
        "dono": "franqueado; o consultor cobra na visita",
        "total_abertas": total,
        "com_texto": com_texto,
        "manchete": (f"{total} avaliações negativas sem resposta na rede medida — "
                     f"{com_texto} delas com o paciente explicando o motivo."),
        # a tela não conta lista: "lojas com fila" e o tamanho de cada fila
        # saem contados daqui
        "lojas_com_fila": len(unidades),
        "unidades": [dict(u, itens_total=len(u.get("itens") or []))
                     for u in unidades],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()
    d = monta()
    print(f"\n  {d['manchete']}\n")
    for u in d["unidades"]:
        print(f"  {u['abertas']:>3d} abertas ({u['com_texto']} com texto) · "
              f"{u['rotulo']} · {u['unidade']}")
        for x in u["itens"][:2]:
            if x["texto"]:
                print(f"        [{x['nota']}★ {x['data']}] “{x['texto'][:76]}”")
    if a.salvar:
        (PORTAL/"caixa_de_respostas.json").write_text(
            json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n  → dados/portal/caixa_de_respostas.json")


if __name__ == "__main__":
    main()
