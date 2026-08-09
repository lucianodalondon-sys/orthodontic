#!/usr/bin/env python3
"""
build_portal.py — monta o payload que o casco lê.

    dados/serie/*.jsonl   (medido — o que a coleta produz, append-only)
  + dados/conteudo/*.json (autorado — o que os estudos concluíram)
  + dados/identidade/*.json (a tabela de amarração)
  → dados/portal/*.json  (pronto para renderizar; o casco não calcula nada)

Regra: o casco NUNCA calcula. Se um número aparece na tela, ele sai daqui.
Regra: todo número carrega procedência. Sem procedência, não entra.

Uso:  python3 scripts/build_portal.py [--corte AAAA-MM-DD]
"""
import json, argparse, pathlib, sys
from collections import defaultdict

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SERIE, CONT, IDENT, OUT = (RAIZ/"dados"/x for x in ("serie","conteudo","identidade","portal"))
# A lista de praças SAI da pasta de identidade, não do código. Escrever aqui
# foi o mesmo defeito dos coletores: praça nova entrava na base e nunca chegava
# ao portal, calada. Cuiabá, Palmas e Contagem ficaram três semanas de fora.
PRACAS = sorted(p.stem for p in (pathlib.Path(__file__).resolve().parent.parent
                                 / "dados" / "identidade").glob("*.json"))


def jsonl(nome):
    p = SERIE/f"{nome}.jsonl"
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def carrega(dir_, nome):
    p = dir_/f"{nome}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def escreve(nome, obj):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/f"{nome}.json").write_text(
        json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return nome


def ultimo_por(rows, chave):
    """Último snapshot de cada chave — a série é append-only, então o portal mostra a ponta."""
    fora = {}
    for r in sorted(rows, key=lambda r: r.get("snapshot_date", "")):
        fora[chave(r)] = r
    return fora


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corte", default=None, help="data de corte a publicar (padrão: a mais recente da série)")
    args = ap.parse_args()

    places = jsonl("places")
    funis = jsonl("funil")
    regua = (jsonl("regua") or [{}])[-1]
    sazon = jsonl("sazonalidade")
    temas = jsonl("temas")
    descida = jsonl("descida_nacional")

    if not places:
        sys.exit("dados/serie/places.jsonl vazio — nada a publicar")

    corte = args.corte or max(r["snapshot_date"] for r in places)
    ident = {p: carrega(IDENT, p) for p in PRACAS}
    nome_local = {l["local_id"]: l for p in PRACAS for l in ident[p].get("locais", [])}

    ult_place = ultimo_por([r for r in places if r["snapshot_date"] <= corte],
                           lambda r: r["local_id"])
    ult_tema = ultimo_por([r for r in temas if r["snapshot_date"] <= corte],
                          lambda r: (r["praca_id"], r["tema"]))
    ult_funil = ultimo_por([r for r in funis if r["snapshot_date"] <= corte],
                           lambda r: r["local_id"])

    escritos = []

    # ---------- manifest ----------
    escritos.append(escreve("manifest", {
        "gerado_de": "dados/serie + dados/conteudo + dados/identidade",
        "corte": corte,
        "taxonomia_versao": next((r.get("taxonomia_versao") for r in temas if r.get("taxonomia_versao")), None),
        "cobertura": carrega(CONT, "rede").get("cobertura", {}),
        # o casco NÃO monta rótulo de cidade — recebe pronto, com a UF na frente
        "pracas": [{"praca_id": p, "nome": ident[p].get("nome"),
                    "rotulo": ident[p].get("rotulo") or ident[p].get("nome"),
                    "uf": ident[p].get("uf", []),
                    "cidades": ident[p].get("cidades_rotulo") or ident[p].get("cidades", [])}
                   for p in PRACAS],
        "telas": ["rede", "achados", "corretor", "evidencias"] + [f"pracas/{p}" for p in PRACAS],
        "aviso": "O casco não calcula. Todo valor exibido sai deste diretório.",
    }))

    # ---------- rede ----------
    rede = carrega(CONT, "rede")
    linhas = []
    for p in PRACAS:
        proprios = [l for l in ident[p].get("locais", []) if l.get("papel") == "proprio"]
        principal = proprios[0] if proprios else None
        pl = ult_place.get(principal["local_id"]) if principal else {}
        tema = ult_tema.get((p, "atendimento"), {})
        linhas.append({
            "praca_id": p,
            "nome": ident[p].get("nome"),
            "rotulo": ident[p].get("rotulo") or ident[p].get("nome"),
            "uf": ident[p].get("uf", []),
            "cidades": ident[p].get("cidades_rotulo") or ident[p].get("cidades", []),
            "papel": carrega(CONT, p).get("papel"),
            "nota": pl.get("nota"),
            "avaliacoes": pl.get("avaliacoes_total"),
            "reviews_novos_mes": pl.get("reviews_novos_mes"),
            "anuncios_ativos": pl.get("anuncios_ativos"),
            "atendimento_pct": tema.get("pct"),
            "atendimento_n": tema.get("n"),
            "atendimento_base": tema.get("base"),
        })
    rede["praca_linhas"] = linhas
    rede["corte"] = corte
    escritos.append(escreve("rede", rede))

    # ---------- uma por praça ----------
    (OUT/"pracas").mkdir(parents=True, exist_ok=True)
    for p in PRACAS:
        c = carrega(CONT, p)
        locais = ident[p].get("locais", [])
        placar = []
        for l in locais:
            pl = ult_place.get(l["local_id"])
            if not pl:
                continue
            placar.append({
                "local_id": l["local_id"], "nome": l.get("nome"),
                "tipo": l.get("tipo_concorrente") or l.get("tipo"),
                "proprio": l.get("papel") == "proprio",
                "nota": pl.get("nota"), "avaliacoes": pl.get("avaliacoes_total"),
                "reviews_novos_mes": pl.get("reviews_novos_mes"),
                "anuncios_ativos": pl.get("anuncios_ativos"),
            })
        placar.sort(key=lambda r: -(r.get("avaliacoes") or 0))

        f = ult_funil.get(next((l["local_id"] for l in locais if l.get("papel") == "proprio"), None))
        funil = None
        if f:
            funil = {
                "estagios": [
                    {"l": "Interessados", "v": f["interessados"], "pct": None, "regua": None},
                    {"l": "Agendamentos", "v": f["agendamentos"], "pct": f["taxa_agendamento"], "regua": regua.get("agendamento")},
                    {"l": "Comparecimentos", "v": f["comparecimentos"], "pct": f["taxa_comparecimento"], "regua": regua.get("comparecimento")},
                    {"l": "Fechados", "v": f["fechados"], "pct": f["taxa_fechamento"], "regua": regua.get("fechamento")},
                    {"l": "Pagos", "v": f["pagos"], "pct": f["taxa_pagamento"], "regua": regua.get("pagamento")},
                ],
                "base_ativa": f.get("base_ativa"), "base_ativa_anterior": f.get("base_ativa_anterior"),
                "contratos_mes": f.get("contratos_mes_2026"), "contratos_mes_anterior": f.get("contratos_mes_2025"),
                "meta_rede": f.get("meta_rede_contratos_mes"), "ressalva": f.get("ressalva"),
            }

        temas_p = [{"tema": k[1], **v} for k, v in ult_tema.items() if k[0] == p]
        saz = [r for r in sazon if r.get("regiao") in ident[p].get("uf", [])]

        escreve(f"pracas/{p}", {
            "praca_id": p, "corte": corte,
            # o casco não monta rótulo: recebe pronto, com a UF na frente
            "rotulo": ident[p].get("rotulo") or ident[p].get("nome"),
            "uf": ident[p].get("uf", []),
            "cidades": ident[p].get("cidades_rotulo") or ident[p].get("cidades", []),
            "identidade": {k: v for k, v in ident[p].items() if k != "locais"},
            **{k: v for k, v in c.items() if k != "praca_id"},
            "placar": placar, "funil": funil, "temas": temas_p,
            "sazonalidade": saz,
            "o_que_mudou": None,  # nasce na 2ª coleta — estado vazio é decisão de produto
        })
        escritos.append(f"pracas/{p}")

    # ---------- achados, corretor, evidências ----------
    escritos.append(escreve("achados", carrega(CONT, "achados")))
    corr = carrega(CONT, "corretor")
    corr["descida"] = descida
    escritos.append(escreve("corretor", corr))
    escritos.append(escreve("evidencias", carrega(CONT, "evidencias")))

    print(f"corte {corte} · {len(escritos)} arquivos em dados/portal/")
    for e in escritos:
        print("  ", e)


if __name__ == "__main__":
    main()
