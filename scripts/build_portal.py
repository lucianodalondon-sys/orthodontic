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
import datetime as dt
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

    # ---------- radar do franqueado: onde captar ----------
    # A única tela que o FRANQUEADO abre para agir, não para se comparar. Sai
    # de dados/serie/captacao.jsonl, que já vem com a leitura pronta — o casco
    # não classifica porta nem decide o que é conserto de ficha.
    cap = jsonl("captacao")
    if cap:
        (OUT/"captacao").mkdir(parents=True, exist_ok=True)
        corte_cap = max(r["snapshot_date"] for r in cap)
        for r in ultimo_por([c for c in cap if c["snapshot_date"] == corte_cap],
                            lambda c: c["praca_id"]).values():
            escreve(f"captacao/{r['praca_id']}", r)
            escritos.append(f"captacao/{r['praca_id']}")

    # ---------- o plano do franqueado ----------
    # A mesma medição da captação, escrita para quem vai fazer: um número no
    # topo, cinco tarefas, grátis primeiro, cada uma com "como saber que
    # funcionou". O casco não reescreve nada — o texto já vem pronto, porque
    # é ele que decide se o franqueado age ou arquiva.
    PLANOS = RAIZ/"dados"/"planos"
    if PLANOS.exists():
        (OUT/"planos").mkdir(parents=True, exist_ok=True)
        for arq in sorted(PLANOS.glob("*.json")):
            escreve(f"planos/{arq.stem}", json.loads(arq.read_text(encoding="utf-8")))
            escritos.append(f"planos/{arq.stem}")

    # ---------- radar de oportunidade ----------
    # A única tela que fala com o time de EXPANSÃO, não com o de marketing.
    # Entra no portal com a defesa escrita, não com nota: a decisão de abrir
    # unidade é cara e ninguém assina por causa de um número de 0 a 100.
    # Cidade que o radar não conseguiu conferir contra a lista oficial de
    # unidades NÃO entra — sugerir praça onde já existe clínica é o erro que
    # quebraria a confiança na ferramenta inteira.
    op = jsonl("oportunidade")
    if op:
        corte_op = max(r["snapshot_date"] for r in op)
        atual = ultimo_por([r for r in op if r["snapshot_date"] == corte_op],
                           lambda r: r.get("cidade"))
        cidades_radar, ocupadas, nao_conferidas = [], [], []
        for r in atual.values():
            if r.get("erro"):
                continue
            pres = r.get("presenca") or {}
            linha = {k: r.get(k) for k in (
                "rotulo", "cidade", "uf", "populacao", "alvo_9_15", "alvo_30_45",
                "clinicas_amostradas", "clinicas_fortes", "lider_avaliacoes",
                "avaliacoes_somadas", "hab_por_clinica_forte",
                "uf_sem_nenhuma_unidade", "leitura", "maiores", "defesa")}
            linha["conferencia"] = {
                "conferida": pres.get("conferida"),
                "livre": pres.get("livre"),
                "motivo": pres.get("motivo"),
                "unidades_da_rede": r.get("unidades_da_rede"),
                "nomes_da_rede": r.get("nomes_da_rede"),
                "fontes": ["lista oficial orthodonticbrasil.com.br",
                           "busca por nome no Google Places"],
            }
            if not pres.get("conferida"):
                nao_conferidas.append(linha)
            elif not pres.get("livre"):
                ocupadas.append(linha)
            elif str(r.get("leitura", "")).startswith("OPORTUNIDADE"):
                cidades_radar.append(linha)
        cidades_radar.sort(key=lambda r: -(r.get("alvo_30_45") or 0))

        # O estudo completo da praça de oportunidade — cidade, concorrência e a
        # praça gêmea onde a rede já opera. É o que responde a segunda pergunta
        # do time de expansão: "essa cidade dá quanto?". Sem a gêmea, o radar
        # diz onde e não diz quanto.
        EST = RAIZ/"dados"/"oportunidade"
        estudos = {}
        if EST.exists():
            for arq in sorted(EST.glob("*.json")):
                estudos[arq.stem] = json.loads(arq.read_text(encoding="utf-8"))
        if estudos:
            (OUT/"oportunidade").mkdir(parents=True, exist_ok=True)
            for pid, est in estudos.items():
                escreve(f"oportunidade/{pid}", est)
                escritos.append(f"oportunidade/{pid}")
            for linha in cidades_radar:
                pid = next((k for k, v in estudos.items()
                            if v.get("cidade") == linha.get("cidade")), None)
                est = estudos.get(pid)
                if not est:
                    linha["estudo"] = None
                    continue
                g = est.get("gemea") or {}
                linha["estudo"] = f"oportunidade/{pid}"
                linha["gemea"] = {
                    "rotulo": g.get("rotulo"), "praca_id": g.get("praca_id"),
                    "distancia": g.get("distancia"), "frase": g.get("frase"),
                    "unidades_de_la": g.get("unidades_de_la"),
                    "onde_difere": g.get("onde_difere"),
                }
                linha["concorrencia"] = {
                    k: est["concorrencia"].get(k) for k in
                    ("varridas", "fortes", "medias", "fracas", "concentracao_top5",
                     "de_rede_nacional", "sem_site_pct",
                     "enderecos_com_ficha_dobrada", "nota_mediana")}

        unids = jsonl("unidades_rede")
        rede_corte = max((u["snapshot_date"] for u in unids), default=None)
        atuais = [u for u in unids if u["snapshot_date"] == rede_corte]
        ufs_com = {u["uf"].upper() for u in atuais}
        TODAS_UF = {"AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
                    "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
                    "RS", "RO", "RR", "SC", "SP", "SE", "TO"}
        escritos.append(escreve("radar", {
            "corte": corte_op,
            "oportunidades": cidades_radar,
            "ja_tem_unidade": ocupadas,
            "nao_conferidas": nao_conferidas,
            "rede_hoje": {
                "corte": rede_corte,
                "unidades": len(atuais),
                "abertas": sum(1 for u in atuais if u["situacao"] == "aberta"),
                "em_implantacao": sum(1 for u in atuais if u["situacao"] != "aberta"),
                "cidades": len({u["cidade"] for u in atuais}),
                "ufs_sem_nenhuma_unidade": sorted(TODAS_UF - ufs_com),
                "fonte": "orthodonticbrasil.com.br/encontre-uma-unidade",
            },
            "ressalvas": [
                "População residente, não a diurna — a literatura de território "
                "diz que a diurna prevê melhor, e o IBGE não a publica de graça.",
                "A praça é o município inteiro, não o raio de deslocamento real.",
                "Mede a categoria pública do Google: volume e nota, não "
                "faturamento nem ticket.",
                "'Praça livre' é a lista oficial da rede mais a busca por nome "
                "no Google. Uma unidade aberta ontem e ainda não publicada no "
                "site é o furo que resta.",
            ],
        }))

    # ---------- achados, corretor, evidências ----------
    escritos.append(escreve("achados", carrega(CONT, "achados")))
    corr = carrega(CONT, "corretor")
    corr["descida"] = descida
    escritos.append(escreve("corretor", corr))
    escritos.append(escreve("evidencias", carrega(CONT, "evidencias")))

    # ---------- manifest, POR ÚLTIMO ----------
    # Ele é o índice que o casco lê antes de qualquer outra coisa: diz quais
    # telas existem e onde estão. Escrever no começo era mentira — listava
    # quatro telas enquanto o build produzia trinta, e o casco nunca soube que
    # o radar, os planos e a captação existiam.
    def presentes(pasta):
        d = OUT/pasta
        return sorted(a.stem for a in d.glob("*.json")) if d.exists() else []

    escreve("manifest", {
        "gerado_em": dt.datetime.now().isoformat(timespec="seconds"),
        "gerado_de": "dados/serie + dados/conteudo + dados/identidade",
        "corte": corte,
        "taxonomia_versao": next((r.get("taxonomia_versao") for r in temas
                                  if r.get("taxonomia_versao")), None),
        "cobertura": carrega(CONT, "rede").get("cobertura", {}),
        # o casco NÃO monta rótulo de cidade — recebe pronto, com a UF na frente
        "pracas": [{"praca_id": p, "nome": ident[p].get("nome"),
                    "rotulo": ident[p].get("rotulo") or ident[p].get("nome"),
                    "uf": ident[p].get("uf", []),
                    "cidades": ident[p].get("cidades_rotulo") or ident[p].get("cidades", []),
                    "tem": [k for k, v in (("praca", f"pracas/{p}"),
                                           ("captacao", f"captacao/{p}"),
                                           ("plano", f"planos/{p}"))
                            if (OUT/f"{v}.json").exists()]}
                   for p in PRACAS],
        # o índice de verdade: o que existe, agora, nesta pasta
        "arquivos": {
            "rede": [x for x in ("rede", "rede_cruzamento", "achados", "corretor",
                                 "evidencias", "radar")
                     if (OUT/f"{x}.json").exists()],
            "pracas": presentes("pracas"),
            "captacao": presentes("captacao"),
            "planos": presentes("planos"),
            "oportunidade": presentes("oportunidade"),
        },
        "telas": sorted(escritos),
        "aviso": "O casco não calcula. Todo valor exibido sai deste diretório.",
    })
    escritos.append("manifest")

    print(f"corte {corte} · {len(escritos)} arquivos em dados/portal/")
    for e in escritos:
        print("  ", e)


if __name__ == "__main__":
    main()
