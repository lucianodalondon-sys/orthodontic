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
import json, argparse, pathlib, sys, unicodedata
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import datetime as dt
from collections import defaultdict, Counter
from cruzamento import conta          # número e nome sempre concordando

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SERIE, CONT, IDENT, OUT = (RAIZ/"dados"/x for x in ("serie","conteudo","identidade","portal"))
# A lista de praças SAI da pasta de identidade, não do código. Escrever aqui
# foi o mesmo defeito dos coletores: praça nova entrava na base e nunca chegava
# ao portal, calada. Cuiabá, Palmas e Contagem ficaram três semanas de fora.
def _ident_todas():
    d = pathlib.Path(__file__).resolve().parent.parent/"dados"/"identidade"
    return {a.stem: json.loads(a.read_text(encoding="utf-8"))
            for a in sorted(d.glob("*.json"))}


_TODAS = _ident_todas()
# PRACAS = as praças da REDE, com unidade dentro. As de oportunidade têm
# identidade igual e passam pelos mesmos coletores, mas não entram no placar
# da rede — praça sem unidade não é unidade parada.
PRACAS = [k for k, v in _TODAS.items() if not v.get("sem_unidade")]
PRACAS_OPORTUNIDADE = [k for k, v in _TODAS.items() if v.get("sem_unidade")]


def jsonl(nome):
    p = SERIE/f"{nome}.jsonl"
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").split("\n") if l.strip()]


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
    _saz_med = carrega(OUT, "sazonalidade")     # o veredito da medição
    temas = jsonl("temas")
    descida = jsonl("descida_nacional")

    if not places:
        sys.exit("dados/serie/places.jsonl vazio — nada a publicar")

    corte = args.corte or max(r["snapshot_date"] for r in places)
    ident = {p: carrega(IDENT, p) for p in PRACAS}
    nome_local = {l["local_id"]: l for p in PRACAS for l in ident[p].get("locais", [])}

    # O QUE O RIVAL VENDE é leitura de CIDADE — três lojas de Cuiabá
    # disputam o mesmo leilão e leem a mesma guerra comercial. Carregado
    # aqui em cima porque a praça é montada antes da clínica.
    _of_por = {x["praca_id"]: x for x in carrega(OUT, "oferta").get("pracas", [])}
    ult_place = ultimo_por([r for r in places if r["snapshot_date"] <= corte],
                           lambda r: r["local_id"])
    # A ficha oficial guarda o endereço; a série de places, não. Sem isto a
    # apresentação da clínica abre sem dizer ONDE a loja fica.
    _fichas = jsonl("rede_fichas")
    _ficha_por_place = {}
    if _fichas:
        _u = max(r["snapshot_date"] for r in _fichas)
        for r in _fichas:
            if r["snapshot_date"] == _u and r.get("place_id"):
                _ficha_por_place[r["place_id"]] = r

    _MES = ["jan", "fev", "mar", "abr", "mai", "jun",
            "jul", "ago", "set", "out", "nov", "dez"]

    def _data(iso):
        """15/jul — a tela não fala ISO."""
        if not iso or len(str(iso)) < 10:
            return iso
        a, m, d = str(iso)[:10].split("-")
        return f"{int(d)}/{_MES[int(m)-1]}"
    ult_tema = ultimo_por([r for r in temas if r["snapshot_date"] <= corte],
                          lambda r: (r["praca_id"], r["tema"]))
    ult_funil = ultimo_por([r for r in funis if r["snapshot_date"] <= corte],
                           lambda r: r["local_id"])

    escritos = []

    # ---------- o índice das clínicas (as 374, não as 10) ----------
    # O PORTAL NÃO É DE DEZ LOJAS. Hoje dez têm estudo, mas a lista oficial
    # tem 374 em 304 cidades, e uma tela que lista dez em grade vira uma
    # parede inútil na centésima. O índice sai daqui pronto: agrupado por UF
    # e por cidade, com TODOS os contadores calculados — a tela nunca conta.
    # E as que não têm estudo aparecem, porque esconder o não medido é o que
    # faz a diretoria achar que medimos tudo.
    _lojas_medidas = {}
    for _p in PRACAS:
        for _l in ident[_p].get("locais", []):
            if _l.get("papel") == "proprio" and _l.get("place_id"):
                _lojas_medidas[_l["place_id"]] = _l["local_id"]
    _fl_ix = {x["local_id"]: x for x in carrega(OUT, "fila").get("fila", [])}

    _por_uf = defaultdict(lambda: defaultdict(list))
    _fichas_hoje = [r for r in _fichas
                    if _fichas and r["snapshot_date"] == max(
                        x["snapshot_date"] for x in _fichas)]
    for r in _fichas_hoje:
        uf = r.get("uf") or "—"
        lid = _lojas_medidas.get(r.get("place_id"))
        fl = _fl_ix.get(lid) or {}
        _por_uf[uf][r.get("cidade") or "—"].append({
            "unidade": r.get("unidade_na_lista") or r.get("nome"),
            "rotulo": f"{uf} · {r.get('cidade')}",
            "situacao": r.get("situacao_na_lista"),
            "nota": r.get("nota"), "avaliacoes": r.get("avaliacoes"),
            "confirmada": bool(r.get("confirmada")),
            "com_estudo": bool(lid),
            "local_id": lid,
            "arquivo": f"clinicas/{lid}" if lid else None,
            "faixa": fl.get("faixa"), "urgencia": fl.get("urgencia"),
            "tarefa": (fl.get("tarefa") or {}).get("estado") if fl else None,
        })

    # A LOJA QUE MEDIMOS E A LISTA OFICIAL NÃO CONFIRMOU. Das 374 linhas, 326
    # têm place_id; 48 a varredura não confirmou, e três lojas nossas caem aí
    # (duas de Cuiabá e Prudente). Elas JÁ ESTÃO entre as 374 — só não se sabe
    # em qual linha, porque a lista grava a cidade sem acento e não distingue
    # lojas da mesma cidade. Então NÃO se cria unidade nova (isso inflaria a
    # rede para 377) e NÃO se escolhe uma linha a dedo: a cidade passa a
    # carregar quais estudos são dela, com a ambiguidade escrita.
    _sem_acento = lambda t: "".join(
        c for c in unicodedata.normalize("NFD", str(t or ""))
        if unicodedata.category(c) != "Mn").lower().strip()
    _casadas = {x["local_id"] for uf in _por_uf for c in _por_uf[uf].values()
                for x in c if x.get("local_id")}
    _estudo_solto = defaultdict(list)
    for _p in PRACAS:
        for _l in ident[_p].get("locais", []):
            lid = _l.get("local_id")
            if (_l.get("papel") != "proprio" or lid in _casadas
                    or not (OUT/f"clinicas/{lid}.json").exists()):
                continue
            uf = (ident[_p].get("uf") or ["—"])[0]
            cid = str((ident[_p].get("cidades_rotulo")
                       or ident[_p].get("cidades") or ["—"])[0]).split(" · ")[-1]
            fl = _fl_ix.get(lid) or {}
            _estudo_solto[(uf, _sem_acento(cid))].append({
                "local_id": lid,
                "unidade": _l.get("unidade") or _l.get("nome"),
                "arquivo": f"clinicas/{lid}",
                "faixa": fl.get("faixa"),
                "tarefa": (fl.get("tarefa") or {}).get("estado") if fl else None,
            })

    _ufs = []
    for uf in sorted(_por_uf):
        cidades = []
        for cid in sorted(_por_uf[uf]):
            us = _por_uf[uf][cid]
            soltos = _estudo_solto.get((uf, _sem_acento(cid)), [])
            cidades.append({
                "cidade": cid, "rotulo": f"{uf} · {cid}",
                "unidades": us,
                "unidades_total": len(us),
                "com_estudo": sum(1 for x in us if x["com_estudo"]) + len(soltos),
                # estudos desta cidade que a lista oficial não confirmou linha
                "estudos_sem_linha_oficial": soltos,
                "porque_sem_linha": ("a lista oficial não confirmou a linha "
                                     "destas lojas, e como a cidade tem mais "
                                     "de uma não dá para dizer qual é qual"
                                     if soltos else None),
                # cidade com mais de uma loja é o caso que a média mentia:
                # a tela precisa saber para nunca fundir
                "mais_de_uma_loja": len(us) > 1,
                "frase": conta(len(us), "unidade") + " nesta cidade",
            })
        n = sum(c["unidades_total"] for c in cidades)
        e = sum(c["com_estudo"] for c in cidades)
        _ufs.append({
            "uf": uf, "cidades": cidades,
            "cidades_total": len(cidades),
            "unidades_total": n, "com_estudo": e, "sem_escuta": n - e,
            "frase": (conta(n, "unidade") + " em "
                      + conta(len(cidades), "cidade")
                      + (f" · {e} com estudo" if e else " · nenhuma escutada")),
        })
    _n_tot = sum(u["unidades_total"] for u in _ufs)
    _n_est = sum(u["com_estudo"] for u in _ufs)
    escritos.append(escreve("clinicas_indice", {
        "o_que_e": "Todas as unidades da lista oficial da rede, por estado e "
                   "cidade. As que já têm estudo abrem a página da clínica; "
                   "as outras aparecem para que o tamanho do que falta seja "
                   "visível.",
        "corte": corte,
        "unidades_total": _n_tot,
        "com_estudo": _n_est,
        "sem_escuta": _n_tot - _n_est,
        "ufs_total": len(_ufs),
        "cidades_total": sum(u["cidades_total"] for u in _ufs),
        "manchete": (f"{_n_est} de " + conta(_n_tot, "unidade")
                     + " com estudo — as outras "
                     + conta(_n_tot - _n_est, "ainda não foi escutada",
                             "ainda não foram escutadas")),
        "com_estudo_sem_linha_oficial": sum(
            1 for u in _ufs for c in u["cidades"] for x in c["unidades"]
            if x.get("sem_linha_oficial")),
        "cidades_com_mais_de_uma_loja": sum(
            1 for u in _ufs for c in u["cidades"] if c["mais_de_uma_loja"]),
        "ufs": _ufs,
    }))

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
            # OS PLANOS DA PRAÇA SÃO OS DAS LOJAS, no plural. O casco pedia
            # `planos/<praca_id>` — um plano por cidade — e isso 404 desde que
            # o plano passou a ser por `local_id`. Cuiabá tem três, e podem
            # ser três donos: a praça oferece os três, nomeados.
            "planos_das_lojas": [
                {"local_id": l["local_id"],
                 "unidade": l.get("unidade") or l.get("nome"),
                 "rotulo": ident[p].get("rotulo") or ident[p].get("nome"),
                 "arquivo": f"planos/{l['local_id']}"}
                for l in locais if l.get("papel") == "proprio"
                and (RAIZ/"dados"/"planos"/f"{l['local_id']}.json").exists()],
            "oferta": _of_por.get(p),
            "placar": placar, "funil": funil, "temas": temas_p,
            "sazonalidade": saz,
            # O PICO DA PRAÇA é buraco de coleta, e buraco calado é o pior
            # tipo. A série tem 4 pontos, todos de SC, vindos do estudo de
            # Mafra — e foi justamente ela que derrubou a tese nacional de
            # "dezembro e janeiro são pico" (lá é vale). Ou seja: não dá
            # para herdar a curva de uma região para as outras. Enquanto
            # não houver coleta por cidade, a praça diz isso na tela.
            "sazonalidade_estado": ({
                "tem": True,
                "regiao": saz[0].get("regiao"),
                "pontos": len(saz),
                "anos_da_serie": saz[0].get("serie_anos"),
            } if saz else {
                "tem": False,
                # Já NÃO é mais "ainda não medimos": medimos as 12 UFs no
                # Google Trends, 5 anos, e nenhuma passou. Isso é resultado,
                # não pendência — e some da lista de tarefas.
                "medimos": True,
                "por_que": ((_saz_med.get("manchete") or "").strip() + " " +
                            (_saz_med.get("por_que_nao_e_por_cidade") or "")
                            ).strip(),
                "as_duas_travas": _saz_med.get("as_duas_travas"),
                "veredito_por_uf": [
                    {"regiao": v["regiao"], "porque": v.get("porque"),
                     "semanas_com_busca": v.get("semanas_com_busca"),
                     "semanas": v.get("semanas"),
                     "pico_repete_em": v.get("pico_repete_em"),
                     "anos_medidos": v.get("anos_medidos")}
                    for v in (_saz_med.get("veredito") or [])
                    if v["regiao"] in (ident[p].get("uf") or [])],
                "o_que_preenche": ("nada que seja fonte externa: o Trends não "
                                   "publica índice para este termo nesta "
                                   "escala. Só dado interno da rede (agenda, "
                                   "contratos) diria quando a procura sobe — "
                                   "e isso é teto do produto"),
                "quem_responde": "só a rede, por dentro",
            }),
            # A 2ª coleta chegou: o movimento sai de o_que_mudou.json, gerado
            # por scripts/o_que_mudou.py a partir da série de places. O build
            # LÊ o payload em vez de esperar injeção externa — senão a ordem
            # dos scripts importa e um rebuild apagava o bloco calado.
            "o_que_mudou": (lambda m: (
                {"dias_medidos": m["dias_medidos"], "aviso": m["aviso"],
                 "nossas": m["nossas"], "quem_mais_ganhou": m["quem_mais_ganhou"],
                 "contador_caiu": m["contador_caiu"]} if m else None))(
                (carrega(OUT, "o_que_mudou").get("pracas") or {}).get(p)),
        })
        escritos.append(f"pracas/{p}")

    # ---------- radar do franqueado: onde captar ----------
    # A única tela que o FRANQUEADO abre para agir, não para se comparar. Sai
    # de dados/serie/captacao.jsonl, que já vem com a leitura pronta — o casco
    # não classifica porta nem decide o que é conserto de ficha.
    cap = jsonl("captacao")
    if cap:
        (OUT/"captacao").mkdir(parents=True, exist_ok=True)
        # A ÚLTIMA medição DE CADA PRAÇA, não as da última data do arquivo.
        # Filtrar pela data máxima global só reescrevia a praça medida naquele
        # dia (1 de 13); as outras 12 telas eram sobra de um build anterior —
        # apagar dados/portal/captacao/ fazia doze telas sumirem sem erro.
        # Cada arquivo carrega o próprio snapshot_date, que é o que a tela lê.
        for r in ultimo_por(cap, lambda c: c["praca_id"]).values():
            # os três grupos de frases vão com o tamanho contado ao lado
            r = dict(r, **{f"{g}_total": len(r.get(g) or [])
                           for g in ("fora", "sem_dono", "dentro")})
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
        # Só publica plano de praça que TEM unidade. As seis de oportunidade
        # geraram plano por engano e o texto falava com um franqueado que não
        # existe ("a SUA clínica aparece em 0 das 20 buscas", em Macapá, onde
        # a rede não tem unidade). O estudo daquelas cidades é outro arquivo,
        # em oportunidade/, e continua publicado. A trava fica aqui além de no
        # gerador porque o arquivo órfão pode sobreviver no disco.
        # O plano agora é POR LOJA (dados/planos/<local_id>.json): eram sete
        # planos para dez lojas, e as três de Cuiabá liam o mesmo texto como
        # se fossem o mesmo negócio. A trava também virou por loja: só
        # publica plano de local_id que é unidade PRÓPRIA de praça da rede.
        nossas = {l["local_id"] for pp in PRACAS
                  for l in ident[pp].get("locais", [])
                  if l.get("papel") == "proprio"}
        for arq in sorted(PLANOS.glob("*.json")):
            if arq.stem not in nossas:
                continue
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
            # A leitura autorada entra JUNTO com os números, como em toda
            # praça da rede. Sem isso a cidade do Radar abria com 20 campos
            # de número e nenhuma manchete — não era o mesmo estudo.
            for pid, est in estudos.items():
                texto = carrega(CONT/"oportunidade", pid)
                escreve(f"oportunidade/{pid}", {**est, **texto})
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

    # ---------- FRANQUEADORA: a sala de comando ----------
    # É a tela do login inicial da franqueadora, e ela não é um relatório: é o
    # painel de onde a rede inteira se enxerga e de onde se escolhe a
    # ferramenta. O Radar de Oportunidade é UMA das ferramentas, não a tela.
    #
    # Cada ferramenta abaixo só entra se tiver dado atrás. Ferramenta sem dado
    # entra com `disponivel: false` e o motivo — o casco mostra apagada, porque
    # esconder o que falta é o que faz a diretoria achar que mede tudo.
    unids = jsonl("unidades_rede")
    rede_corte = max((u["snapshot_date"] for u in unids), default=None)
    atuais = [u for u in unids if u["snapshot_date"] == rede_corte]
    por_uf = defaultdict(lambda: {"unidades": 0, "abertas": 0, "implantando": 0,
                                  "cidades": set(), "medidas": 0})
    for u in atuais:
        d = por_uf[u["uf"].upper()]
        d["unidades"] += 1
        d["abertas" if u["situacao"] == "aberta" else "implantando"] += 1
        d["cidades"].add(u["cidade"])
    ufs_medidas = {uf for p in PRACAS for uf in (ident[p].get("uf") or [])}
    for uf in ufs_medidas:
        if uf in por_uf:
            por_uf[uf]["medidas"] = sum(
                1 for p in PRACAS if uf in (ident[p].get("uf") or []))
    TODAS_UF = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
                "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
                "RS", "RO", "RR", "SC", "SP", "SE", "TO"]
    mapa = [{"uf": uf,
             "unidades": por_uf.get(uf, {}).get("unidades", 0),
             "abertas": por_uf.get(uf, {}).get("abertas", 0),
             "em_implantacao": por_uf.get(uf, {}).get("implantando", 0),
             "cidades": len(por_uf.get(uf, {}).get("cidades", ())),
             "pracas_medidas": por_uf.get(uf, {}).get("medidas", 0)}
            for uf in TODAS_UF]

    cruz = carrega(CONT, "rede_cruzamento") or {}
    if (OUT/"rede_cruzamento.json").exists():
        cruz = json.loads((OUT/"rede_cruzamento.json").read_text(encoding="utf-8"))

    # reputação de rede contra rede: o último registro de CADA marca, não o
    # último dia — as marcas foram coletadas em dias diferentes.
    marcas = {}
    for r in sorted(jsonl("reclamacoes_agregado"), key=lambda x: x["snapshot_date"]):
        marcas[r.get("empresa")] = r

    # Quem entra na comparação de marca. O Reclame Aqui é nacional e não tem
    # recorte por cidade — e é exatamente por isso que ele é da franqueadora:
    # a nota da marca é responsabilidade dela, não do franqueado. Mas a coleta
    # trouxe rede de implante junto, e quem quer aparelho não escolhe entre
    # OrthoDontic e uma rede de implante. A classificação mora em
    # dados/conteudo/redes_do_reclame_aqui.json para poder ser contestada sem
    # mexer em código.
    cfg = carrega(CONT, "redes_do_reclame_aqui")
    foco = {x["empresa"]: x for x in cfg.get("redes", [])}
    na_tela = set(cfg.get("focos_na_tela") or ["ortodontia", "odontologia_popular"])

    def linha_rep(r):
        c = foco.get(r.get("empresa"), {})
        return {"marca": r.get("nome"), "empresa": r.get("empresa"),
                "reclamacoes": r.get("reclamacoes_total"),
                "selo": r.get("selo_12m") or r.get("selo"), "nota": r.get("nota_12m"),
                "nossa": (r.get("empresa") == "orthodontic"),
                "foco": c.get("foco"), "nota_de_classificacao": c.get("nota"),
                "medido_em": r["snapshot_date"]}

    todas_rep = [linha_rep(r) for r in marcas.values()]
    reputacao = sorted([x for x in todas_rep if x["foco"] in na_tela],
                       key=lambda x: -(x["reclamacoes"] or 0))
    # As que ficaram de fora aparecem nomeadas, com o motivo. Cortar em
    # silêncio é como o "4 de 340" sobreviveu quatro semanas.
    fora_da_rep = sorted([x for x in todas_rep if x["foco"] not in na_tela],
                         key=lambda x: -(x["reclamacoes"] or 0))

    # a ficha do Google das unidades: o achado de categoria, agregado
    cat_ult = ultimo_por(jsonl("categoria"), lambda r: (r.get("praca_id"), r.get("place_id")))
    nossos_ids = {l.get("place_id") for p in PRACAS
                  for l in ident[p].get("locais", [])
                  if l.get("papel") == "proprio" and l.get("place_id")}
    fichas = [r for r in cat_ult.values() if r.get("place_id") in nossos_ids]
    por_tipo = Counter(r.get("tipo") for r in fichas)
    sem_site = sum(1 for r in fichas if not (r.get("site") or "").strip())

    # presença na busca, somada na rede
    caps = ultimo_por(jsonl("captacao"), lambda r: r.get("praca_id"))
    fam = defaultdict(lambda: {"dentro": 0, "fora": 0})
    for c in caps.values():
        for k, v in (c.get("por_familia") or {}).items():
            fam[k]["dentro"] += v.get("dentro", 0)
            fam[k]["fora"] += v.get("fora", 0)

    rad = json.loads((OUT/"radar.json").read_text(encoding="utf-8")) \
        if (OUT/"radar.json").exists() else {}

    fila = json.loads((OUT/"fila.json").read_text(encoding="utf-8")) \
        if (OUT/"fila.json").exists() else {}

    # --------------------------------------------------------------- cobertura
    #
    # "4 praças ouvidas de 340 unidades" ficou escrito à mão em
    # dados/conteudo/rede.json e nunca mais foi tocado. Nove praças entraram
    # depois e o número não mexeu — o portal abria dizendo 4 enquanto o bloco
    # ao lado, na MESMA tela, dizia 374 unidades. Quem lê acha que o produto
    # encolheu, e tem razão de achar: o número estava mentindo.
    #
    # Agora ele sai do dado. Ouvida = praça com avaliação lida, seja da rede ou
    # de oportunidade — em praça de oportunidade a gente ouve o mercado, que é
    # exatamente o que justifica abrir lá.
    from cruzamento import reviews_unicos as _revs
    # "13 de 374 praças ouvidas" misturava maçã com laranja DUAS vezes:
    # comparava PRAÇAS com UNIDADES na mesma fração, e o 13 incluía as seis
    # cidades de oportunidade — que são estudo de expansão, não rede. Cada
    # número agora é da sua própria espécie, e a fração só existe entre
    # unidades: 10 acompanhadas de 374.
    _unidades_acompanhadas = sum(
        1 for pp in PRACAS for l in ident[pp].get("locais", [])
        if l.get("papel") == "proprio")
    cobertura = {
        "unidades_total": len(atuais),
        "unidades_acompanhadas": _unidades_acompanhadas,
        "pracas_da_rede_estudadas": len(PRACAS),
        "cidades_de_oportunidade_estudadas": len(PRACAS_OPORTUNIDADE),
    }

    # ----------------------------------------------------------------- os cards
    #
    # O cliente pediu de volta o primeiro desenho: TUDO EM CARDS, linguagem
    # simples, fácil de entender. Cada card é UMA pergunta em português de
    # balcão, UM número grande e UMA frase — o detalhe mora na tela que o
    # card abre. Quatro grupos com nome de gente:
    #
    #   A REDE      as 374 unidades — marca, mapa, alertas, reputação
    #   AS 10 LOJAS as acompanhadas de perto — movimento, rivais, respostas
    #   EXPANSÃO    onde abrir a próxima
    #   ARQUIVO     de onde veio cada número (gaveta recolhida)
    #
    def _json(nome):
        arq = OUT/f"{nome}.json"
        return json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else {}

    def card(chave, titulo, pergunta, numero, frase, tela, grupo,
             disponivel=True, motivo=None):
        return {"chave": chave, "titulo": titulo, "pergunta": pergunta,
                "numero": numero, "frase": frase, "tela": tela,
                "grupo": grupo, "disponivel": disponivel,
                "indisponivel_porque": motivo}

    # A tira de números do INÍCIO, pronta: número + o nome que combina com
    # ele. O casco vinha juntando o número com um rótulo fixo e escrevia
    # "1 unidades em faixa vermelha" na primeira tela do portal.
    def tira(numero, singular, plural, tom):
        return {"numero": numero, "tom": tom,
                "rotulo": singular if numero == 1 else plural}

    mud = _json("o_que_mudou")
    quedas = sum(len(d.get("contador_caiu", []))
                 for d in mud.get("pracas", {}).values())
    rede_i = _json("rede_inteira")
    vermelhos = [a for a in rede_i.get("alertas", [])
                 if a.get("gravidade") == "vermelha"]
    caixa = _json("caixa_de_respostas")
    voz = _json("voz_da_cidade")

    # ---------- o mapa PINTADO POR PROBLEMA ----------
    # O mapa vinha só com a contagem de unidades, e mapa de contagem responde
    # "onde a rede é grande" — pergunta que ninguém faz na primeira tela. O
    # Painel de Controle abre com o mapa, e mapa de painel responde ONDE DÓI.
    # O tom sai pronto daqui; o casco só pinta o que recebe.
    uf_da_praca = {p: (ident[p].get("uf") or [None])[0] for p in PRACAS}
    risco_uf = defaultdict(lambda: {"vermelha": 0, "amarela": 0, "verde": 0,
                                    "acompanhadas": 0})
    for x in fila.get("fila", []):
        uf = uf_da_praca.get(x.get("praca_id"))
        if not uf:
            continue
        risco_uf[uf]["acompanhadas"] += 1
        risco_uf[uf][x.get("faixa", "verde")] = \
            risco_uf[uf].get(x.get("faixa", "verde"), 0) + 1
    graves_uf = Counter(a["uf"] for a in vermelhos if a.get("uf"))

    for m in mapa:
        r = risco_uf.get(m["uf"], {})
        graves = graves_uf.get(m["uf"], 0)
        m["acompanhadas"] = r.get("acompanhadas", 0)
        m["em_faixa_vermelha"] = r.get("vermelha", 0)
        m["em_faixa_amarela"] = r.get("amarela", 0)
        m["alertas_graves"] = graves
        if m["em_faixa_vermelha"] or graves:
            m["tom"] = "crit"
        elif m["em_faixa_amarela"]:
            m["tom"] = "warn"
        elif m["acompanhadas"]:
            m["tom"] = "ok"
        elif m["unidades"]:
            m["tom"] = "sem_escuta"
        else:
            m["tom"] = "sem_unidade"
        partes = []
        if m["em_faixa_vermelha"]:
            partes.append(f"{m['em_faixa_vermelha']} em faixa vermelha")
        if m["em_faixa_amarela"]:
            partes.append(f"{m['em_faixa_amarela']} em faixa amarela")
        if graves:
            partes.append(f"{conta(graves, 'alerta grave', 'alertas graves')} "
                          f"na ficha do Google")
        if not partes:
            partes.append(f"{conta(m['unidades'], 'unidade')} · "
                          f"{'ainda sem escuta' if m['unidades'] else 'sem unidade'}")
        m["motivo"] = " · ".join(partes)

    mapa_legenda = [
        {"tom": "crit", "o_que_e": "unidade em faixa vermelha ou alerta grave na ficha"},
        {"tom": "warn", "o_que_e": "unidade em faixa amarela"},
        {"tom": "ok", "o_que_e": "acompanhada, sem alerta aberto"},
        {"tom": "sem_escuta", "o_que_e": "tem unidade, ainda não é medida"},
        {"tom": "sem_unidade", "o_que_e": "a rede não está no estado"},
    ]
    # rivais do PRODUTO: só quem disputa aparelho (odontologia não é ortodontia)
    rivais_aparelho = sum(
        1 for p in PRACAS for l in ident[p].get("locais", [])
        if l.get("papel") != "proprio"
        and (l.get("produto") or {}).get("disputa_aparelho") == "sim")
    planos_prontos = (sorted(a.stem for a in (OUT/"planos").glob("*.json"))
                      if (OUT/"planos").exists() else [])

    cards = [
        # ------------------------------------------------------------ A REDE
        card("mapa", "A rede no Brasil", "Onde a OrthoDontic está hoje?",
             len(atuais),
             f"{sum(1 for u in atuais if u['situacao'] == 'aberta')} abertas e "
             f"{sum(1 for u in atuais if u['situacao'] != 'aberta')} em "
             f"implantação, em {len({u['cidade'] for u in atuais})} cidades. "
             f"{len([m for m in mapa if not m['unidades']])} estados ainda sem "
             f"unidade.",
             "mapa", "rede"),
        card("alertas", "Alertas nas fichas do Google",
             "Alguma unidade está mal na rua?",
             len(vermelhos),
             (f"{len(vermelhos)} alertas graves nas {rede_i.get('confirmadas', 0)} "
              f"fichas conferidas — o primeiro: "
              f"{vermelhos[0].get('por_que', '')}" if vermelhos else
              "nenhum alerta grave nas fichas conferidas"),
             "rede_inteira", "rede", bool(rede_i)),
        card("reputacao", "A marca no Reclame Aqui",
             "Como a OrthoDontic se compara com as outras redes?",
             next((x["nota"] for x in reputacao if x["nossa"]), None),
             (f"nota da OrthoDontic contra "
              f"{min((x['nota'] for x in reputacao if not x['nossa'] and x['nota']), default='?')} a "
              f"{max((x['nota'] for x in reputacao if not x['nossa'] and x['nota']), default='?')} "
              f"das outras {sum(1 for x in reputacao if not x['nossa'])} redes "
              f"comparadas — só ortodontia e odontologia popular entram."),
             "reputacao", "rede", bool(reputacao)),
        # -------------------------------------------------------- AS 10 LOJAS
        card("mudou", "O que mudou na semana",
             "O que aconteceu desde a última medição?",
             quedas,
             f"contadores de avaliação CAÍRAM — queda é avaliação apagada, "
             f"evento raro. {len(mud.get('pracas', {}))} praças medidas de novo; "
             f"o período ainda é curto e engorda a cada semana.",
             "mudou", "lojas", bool(mud)),
        card("fila", "Onde agir primeiro",
             "Qual loja precisa de ajuda neste mês?",
             fila.get("em_risco"),
             fila.get("manchete", ""),
             "fila", "lojas", bool(fila.get("fila"))),
        card("caixa", "Avaliações sem resposta",
             "Quantos pacientes reclamaram e ninguém respondeu?",
             caixa.get("total_abertas"),
             f"{caixa.get('com_texto', 0)} delas com o paciente explicando o "
             f"motivo, loja por loja. Responder é higiene da marca.",
             "caixa", "lojas", bool(caixa)),
        card("rival", "Os concorrentes de ortodontia",
             "Quem disputa o paciente de aparelho, e o que fazem melhor?",
             rivais_aparelho,
             "clínicas que vendem APARELHO nas praças acompanhadas. Clínica "
             "geral e implante não entram: é outro tratamento, outro paciente.",
             "rival", "lojas", (OUT/"rival.json").exists()),
        card("anuncios", "Quem anuncia aparelho na cidade",
             "Quem está comprando mídia de aparelho na praça, agora?",
             _json("anuncios").get("anuncios_ativos"),
             (lambda a: (f"anúncios de aparelho no ar, de "
                         f"{a.get('anunciantes_total')} anunciantes nas praças "
                         f"medidas" +
                         (f" — e ninguém anuncia em "
                          f"{', '.join(a['pracas_sem_ninguem'])}."
                          if a.get("pracas_sem_ninguem") else ".")))(
                 _json("anuncios")),
             "anuncios", "lojas", (OUT/"anuncios.json").exists(),
             "rode scripts/quem_anuncia_aparelho.py --salvar"),
        card("padroes", "O que faz uma loja crescer",
             "Por que umas lojas crescem e outras param?",
             len(_json("padroes").get("hipoteses_testadas", [])),
             "explicações confortáveis foram testadas e caíram. O que separa "
             "as lojas que crescem é manter viva a rotina de pedir avaliação "
             "no balcão — e isso é treinável.",
             "padroes", "lojas", (OUT/"padroes.json").exists()),
        card("timeline", "A vida de cada loja",
             "O que aconteceu em cada loja, em ordem?",
             sum(len(l.get("eventos", [])) for l in _json("timeline").get("lojas", [])),
             "eventos observáveis — avaliações, contadores, alertas e rivais "
             "de aparelho — numa linha do tempo por loja, com o estado da "
             "tarefa de cada uma.",
             "timeline", "lojas", (OUT/"timeline.json").exists()),
        card("constancia", "Quem mantém o ritmo",
             "Quais lojas seguem ganhando avaliações todo mês?",
             cruz.get("sustentam", 0),
             f"de {cruz.get('unidades', 0)} lojas acompanhadas mantêm o ritmo. "
             f"{cruz.get('paradas', 0)} pararam e "
             f"{cruz.get('campanha', 0)} só tiveram picos de campanha.",
             "constancia", "lojas", bool(cruz.get("unidades"))),
        # ----------------------------------------------------------- EXPANSÃO
        card("funil", "As melhores cidades do Brasil",
             "Onde vale estudar a próxima cidade?",
             len(_json("funil_nacional").get("candidatas", [])),
             (lambda fn: (f"candidatas rankeadas entre os 5.570 municípios "
                          f"(população-alvo × renda, IBGE)"
                          + (f" — a primeira é "
                             f"{fn['candidatas'][0]['rotulo']}."
                             if fn.get("candidatas") else ".")
                          + (f" E pela régua da própria rede, "
                             f"{fn['onde_cabem_mais'][0]['rotulo']} comporta "
                             f"mais {fn['onde_cabem_mais'][0]['folga']} "
                             f"unidades." if fn.get("onde_cabem_mais") else "")
                          ))(_json("funil_nacional")),
             "funil", "expansao", (OUT/"funil_nacional.json").exists()),
        card("radar", "Onde abrir a próxima franquia",
             "Quais cidades estão prontas para receber uma unidade?",
             len(rad.get("oportunidades", [])),
             f"cidades estudadas a fundo, todas sem OrthoDontic hoje — "
             f"{len(rad.get('ja_tem_unidade', []))} outras foram descartadas "
             f"por já ter unidade. Estudo de expansão: não entra em nenhuma "
             f"conta da rede.",
             "radar", "expansao", bool(rad.get("oportunidades"))),
        card("pracas", "As praças estudadas",
             "O que já sabemos de cada praça, em detalhe?",
             len(PRACAS),
             # "no mesmo padrão de SC · Mafra" saiu daqui: a régua interna
             # não é assunto de quem lê a tela. A frase diz o que a praça
             # tem, não contra quem foi comparada.
             "cidades onde a rede está e que já foram estudadas por inteiro "
             "— concorrência, canais, imprensa, busca e avaliações.",
             "pracas", "expansao", bool(PRACAS)),
        # ------------------------------------------------------------ ARQUIVO
        card("voz_da_cidade", "A voz da cidade",
             "O que a cidade comenta, antes de virar paciente?",
             sum(x.get("comentarios_lidos", 0) for x in voz.get("pracas", [])),
             f"comentários lidos nos canais locais de "
             f"{len(voz.get('pracas', []))} praças.",
             "voz_da_cidade", "arquivo", (OUT/"voz_da_cidade.json").exists()),
        card("busca", "A rede aparece na busca?",
             "Quando a cidade procura 'dentista', a OrthoDontic aparece?",
             fam.get("dentista", {}).get("dentro") if fam.get("dentista") else None,
             (f"aparições contra {fam['dentista']['fora']} ausências na busca "
              f"por 'dentista' — é essa palavra que traz o paciente de "
              f"aparelho." if fam.get("dentista") else "sem medição"),
             "busca", "arquivo", bool(fam)),
        card("fichas", "O cadastro das unidades",
             "As fichas do Google estão certas?",
             len(fichas),
             f"fichas conferidas · {sem_site} sem site na ficha.",
             "fichas", "arquivo", bool(fichas)),
        card("territorio", "Canais que ninguém ocupou",
             "Que canal falta em cada praça?",
             None, "canais mapeados por praça, com os que não existem.",
             "territorio", "arquivo", bool(cruz.get("territorio_vazio"))),
        card("achados", "O que já virou regra",
             "O que se repete em todas as praças — e o que caiu no teste?",
             None,
             "cada achado com o degrau dele: de sinal isolado a regra da "
             "rede, inclusive os derrubados.",
             "achados", "arquivo", (OUT/"achados.json").exists()),
        card("planos", "O plano de cada loja",
             "O que cada franqueado tem para fazer nesta semana?",
             len(planos_prontos),
             "planos escritos, um por loja — só para praça com unidade.",
             "planos", "arquivo", bool(planos_prontos)),
        # "4 regiões" era leitura errada do próprio arquivo: são 4 PONTOS de
        # uma região só (SC). Contar linha como se fosse região publicou como
        # fato uma coisa que o arquivo nunca disse.
        card("sazonalidade", "Quando a procura sobe",
             "Existe época certa para campanha?",
             None, "sem curva suficiente ainda.",
             "sazonalidade", "arquivo",
             len({r.get("regiao") for r in sazon}) > 1,
             ("só há curva de uma região ("
              + ", ".join(sorted({r.get("regiao") for r in sazon}))
              + f"), com {len(sazon)} pontos. Uma região não é calendário "
                f"da rede." if sazon else "nenhuma curva coletada")),
        card("evidencias", "De onde veio cada número",
             "Qual é a prova por trás de cada afirmação?",
             None, "as citações e fontes que sustentam os achados.",
             "evidencias", "arquivo", (OUT/"evidencias.json").exists()),
    ]

    sem_unidade = [m["uf"] for m in mapa if not m["unidades"]]
    escritos.append(escreve("franqueadora", {
        "corte": corte,
        "gerado_em": dt.datetime.now().isoformat(timespec="seconds"),
        "rede": {
            "unidades": len(atuais),
            "abertas": sum(1 for u in atuais if u["situacao"] == "aberta"),
            "em_implantacao": sum(1 for u in atuais if u["situacao"] != "aberta"),
            "cidades": len({u["cidade"] for u in atuais}),
            "ufs_com_unidade": sum(1 for m in mapa if m["unidades"]),
            "ufs_sem_unidade": sem_unidade,
            "ufs_sem_unidade_total": len(sem_unidade),
            "medido_em": rede_corte,
            "fonte": "orthodonticbrasil.com.br/encontre-uma-unidade",
        },
        "cobertura": {**carrega(CONT, "rede").get("cobertura", {}),
                      **cobertura,
                      "aviso": f"As leituras de rede valem para as "
                               f"{cobertura['unidades_acompanhadas']} unidades "
                               f"acompanhadas, em "
                               f"{cobertura['pracas_da_rede_estudadas']} praças — "
                               f"não para as {cobertura['unidades_total']}. As "
                               f"{cobertura['cidades_de_oportunidade_estudadas']} "
                               f"cidades de oportunidade são estudo de expansão e "
                               f"não entram em nenhuma conta da rede."},
        # A ABERTURA DO PORTAL SAI DAQUI, não do casco. Estava escrita à mão
        # dentro do portal.js ("Onde a rede está perdendo terreno") — texto
        # na tela que ninguém conseguia mudar pelo dado, e que abria o
        # produto pela derrota. O portal existe para a rede crescer; o que
        # está ruim tem tela própria, logo abaixo, e não precisa ser a
        # primeira frase. Os números da sublinha vêm da medição.
        "abertura": {
            "sobrelinha": "SALA DE CONTROLE · REDE NACIONAL",
            "titulo": "A inteligência que faz cada clínica crescer.",
            "sublinha": (
                conta(cobertura["unidades_acompanhadas"],
                      "unidade escutada de perto", "unidades escutadas de perto")
                + ", em " + conta(cobertura["pracas_da_rede_estudadas"],
                                  "cidade estudada por inteiro",
                                  "cidades estudadas por inteiro")
                + " — e, para cada uma, o que fazer nesta semana."),
            # o escopo continua declarado, mas como nota de pé, não como
            # manchete: quem chega precisa saber o que o portal faz antes de
            # saber o que ele ainda não cobre
            "escopo": (f"As leituras valem para estas "
                       f"{cobertura['unidades_acompanhadas']} unidades, não "
                       f"para as {cobertura['unidades_total']} da rede. As "
                       + conta(cobertura['cidades_de_oportunidade_estudadas'],
                               "cidade de oportunidade", "cidades de oportunidade")
                       + " são estudo de expansão e não entram em nenhuma "
                         "conta da rede."),
        },
        "mapa": mapa,
        "mapa_legenda": mapa_legenda,
        "tiras_do_inicio": [
            tira(fila.get("em_risco"), "unidade em faixa vermelha",
                 "unidades em faixa vermelha", "crit"),
            tira(fila.get("tarefas_vencidas"), "tarefa fora do prazo",
                 "tarefas fora do prazo", "warn"),
            tira(caixa.get("total_abertas"), "avaliação esperando resposta",
                 "avaliações esperando resposta", "marca"),
            tira(len(vermelhos), "alerta grave na ficha da rede",
                 "alertas graves nas fichas da rede", "bad"),
        ],
        # A porta de entrada. O casco desenha isto ANTES do menu, e o menu vira
        # o que sempre deveria ter sido: o que fazer depois de olhar a fila.
        "agora": ({"pergunta": fila.get("pergunta"),
                   "manchete": fila.get("manchete"),
                   "em_risco": fila.get("em_risco"),
                   "unidades": fila.get("unidades"),
                   "o_que_e_atencao": fila.get("o_que_e_atencao"),
                   "primeiras": [{k: x[k] for k in
                                  ("pos", "rotulo", "unidade_curta", "urgencia",
                                   "faixa", "quem_avanca", "acao")}
                                 for x in fila.get("fila", [])[:3]],
                   "tela": "fila"} if fila.get("fila") else None),
        "grupos": [
            # Nunca escrever "374" nem "10" aqui: os dois números mudam a cada
            # coleta, e um rótulo cravado à mão sobrevive à mudança mentindo.
            {"chave": "rede", "nome": "A rede",
             "explica": f"as {cobertura['unidades_total']} unidades: mapa, "
                        f"alertas e reputação da marca"},
            {"chave": "lojas",
             "nome": f"As {cobertura['unidades_acompanhadas']} lojas acompanhadas",
             "explica": "as unidades medidas de perto, loja por loja"},
            {"chave": "expansao", "nome": "Expansão",
             "explica": "onde abrir a próxima franquia"},
            {"chave": "arquivo", "nome": "Arquivo",
             "explica": "de onde veio cada número"},
        ],
        "cards": cards,
        "reputacao_das_redes": reputacao,
        "reputacao_fora_da_tela": {
            "redes": fora_da_rep,
            "por_que": cfg.get("_por_que_este_arquivo_existe"),
            "criterio": cfg.get("_criterio")},
        "fichas_da_rede": {"conferidas": len(fichas),
                           "por_categoria": dict(por_tipo),
                           "sem_site": sem_site},
        "presenca_na_busca": {k: dict(v) for k, v in fam.items()},
    }))

    # ---------- as páginas de clínica ----------
    #
    # O coração do portal (PROJETO §3): UMA página por unidade, composta
    # aqui no build juntando fila + timeline + caixa + rival + o que mudou
    # por local_id — o casco só desenha. A voz já sai com o rótulo de
    # balcão resolvido: chave interna nunca chega na tela.
    (OUT/"clinicas").mkdir(parents=True, exist_ok=True)
    _tl = carrega(OUT, "timeline")
    _cx = carrega(OUT, "caixa_de_respostas")
    _rv = carrega(OUT, "rival")
    _md = carrega(OUT, "o_que_mudou")
    _fl = carrega(OUT, "fila")
    _eixos = {e["chave"]: e["o_que_e"] for e in _rv.get("eixos", [])}
    _cx_por = {u.get("local_id"): u for u in _cx.get("unidades", [])}
    _rv_por = {p.get("local_id"): p for p in _rv.get("pracas", [])}
    _fl_por = {x["local_id"]: x for x in _fl.get("fila", [])}
    # A mídia é da CIDADE, não da loja: três lojas de Cuiabá disputam o
    # mesmo leilão. Vai na página de cada uma, declarada como leitura de
    # cidade — é análise de mercado, e mercado é por cidade.
    _an_por = {x["praca_id"]: x for x in carrega(OUT, "anuncios").get("pracas", [])}
    # A JORNADA É POR LOJA e responde "o problema é clínico ou é de balcão".
    _jor_por = {x["local_id"]: x
                for x in carrega(OUT, "jornada").get("lojas", [])}
    _pres_por = {x["local_id"]: x
                 for x in carrega(OUT, "presenca_por_loja").get("lojas", [])}
    _md_por = {}
    for _pd in _md.get("pracas", {}).values():
        for _ln in _pd.get("nossas", []):
            _md_por[_ln["local_id"]] = dict(_ln, dias=_pd.get("dias_medidos"),
                                            aviso=_pd.get("aviso"))
    n_cli = 0
    for l in _tl.get("lojas", []):
        lid = l["local_id"]
        cx = _cx_por.get(lid) or {}
        rv = _rv_por.get(lid) or {}
        fl = _fl_por.get(lid) or {}
        voz = ([{"o_que_e": _eixos.get(k, k), "pct": v}
                for k, v in (rv.get("nosso_perfil") or {}).items()]
               if rv.get("nosso_perfil") else None)
        # A CLÍNICA SE APRESENTA ANTES DE SE MEDIR. A tela abria com a nota
        # em cima do nome, como um boletim. Quem chega precisa saber PRIMEIRO
        # de que loja se trata: onde fica, desde quando escutamos, que lugar
        # ela ocupa na cidade e quantas lojas da rede dividem essa cidade.
        _pl = ult_place.get(lid) or {}
        _mud = _md_por.get(lid) or {}
        _irmas = [x for x in ident[l["praca_id"]].get("locais", [])
                  if x.get("papel") == "proprio" and x["local_id"] != lid] \
            if l.get("praca_id") in ident else []
        _hist = (_mud.get("historico") or {})
        _apresentacao = {
            "unidade": l.get("unidade"),
            "cidade": l.get("rotulo"),
            # o place_id mora na IDENTIDADE, não na série de places — foi a
            # identidade que virou a chave depois que local_id truncado fundiu
            # quatro pares de lojas
            "endereco": (_ficha_por_place.get(
                (nome_local.get(lid) or {}).get("place_id")) or {}
            ).get("endereco"),
            "desde": _data(_hist.get("desde")),
            "medicoes": _hist.get("medicoes"),
            "posicao_na_cidade": _pl.get("posicao_na_cidade"),
            "clinicas_na_cidade": _pl.get("clinicas_na_cidade"),
            "lojas_irmas": [{"local_id": x["local_id"],
                             "unidade": x.get("unidade") or x.get("nome")}
                            for x in _irmas],
            # a frase de abertura sai PRONTA daqui — o casco não redige
            "frase": None,
        }
        if _apresentacao["desde"]:
            _apresentacao["frase"] = (
                f"{l.get('unidade') or l.get('rotulo')} é escutada desde "
                f"{_data(_hist.get('desde'))}, em "
                + conta(_apresentacao["medicoes"] or 0, "medição", "medições")
                + (f", e divide {l.get('rotulo','a cidade').split(' · ')[-1]} "
                   + f"com mais {conta(len(_irmas), 'loja')} da rede"
                   if _irmas else "")
                + ".")
        escritos.append(escreve(f"clinicas/{lid}", {
            "local_id": lid, "praca_id": l.get("praca_id"),
            "apresentacao": _apresentacao,
            "rotulo": l.get("rotulo"), "unidade": l.get("unidade"),
            "cabecalho": l.get("cabecalho"),
            "faixa": fl.get("faixa"), "urgencia": fl.get("urgencia"),
            "tarefa": fl.get("tarefa"), "acao": fl.get("acao"),
            "gatilhos": fl.get("gatilhos") or [],
            "quem_avanca": fl.get("quem_avanca"),
            "o_que_mudou": _md_por.get(lid),
            "sem_resposta": {"abertas": cx.get("abertas"),
                             "com_texto": cx.get("com_texto"),
                             "itens": cx.get("itens") or [],
                             "itens_total": len(cx.get("itens") or [])},
            "voz_do_paciente": voz,
            "rival": {"comparados": rv.get("rivais_comparados") or [],
                      "vantagens_deles": rv.get("vantagens_deles") or [],
                      "fora": rv.get("rivais_fora") or [],
                      "fora_total": len(rv.get("rivais_fora") or []),
                      "sem_comparacao_porque": rv.get("sem_comparacao_porque")},
            # a presença na busca É DESTA LOJA, não a média da cidade
            "presenca_na_busca": _pres_por.get(lid),
            # em QUE MOMENTO da jornada esta loja dói — capítulo, não tela
            "jornada": _jor_por.get(lid),
            "oferta_da_cidade": (dict(_of_por[l["praca_id"]], e_da_cidade=True)
                                 if l.get("praca_id") in _of_por else None),
            "plano": (f"planos/{lid}" if (OUT/f"planos/{lid}.json").exists()
                      else None),
            "anuncios_da_cidade": (lambda a: a and {
                "e_da_cidade": True,
                "rotulo": a["rotulo"], "manchete": a["manchete"],
                "anuncios_ativos": a["anuncios_ativos"],
                "anunciantes_total": a["anunciantes_total"],
                "somos_um_deles": a["somos_um_deles"],
                "anunciantes": a["anunciantes"],
                "fora_do_produto": a["fora_do_produto"],
                "fora_do_produto_porque": a["fora_do_produto_porque"],
            })(_an_por.get(l.get("praca_id"))),
            "eventos": l.get("eventos") or [],
        }))
        n_cli += 1

    # ---------- manifest, POR ÚLTIMO ----------
    # Ele é o índice que o casco lê antes de qualquer outra coisa: diz quais
    # telas existem e onde estão. Escrever no começo era mentira — listava
    # quatro telas enquanto o build produzia trinta, e o casco nunca soube que
    # o radar, os planos e a captação existiam.
    def presentes(pasta):
        d = OUT/pasta
        return sorted(a.stem for a in d.glob("*.json")) if d.exists() else []

    # O casco não conta lista: quando um número da tela é "quantos itens tem
    # aqui", ele sai contado daqui, ao lado da lista. Foi assim que "estudos
    # nesta praça" virou len() na tela — e len() na tela é conta na tela.
    def _ficha_praca(p):
        tem = [k for k, v in (("praca", f"pracas/{p}"),
                              ("captacao", f"captacao/{p}"))
               if (OUT/f"{v}.json").exists()]
        # plano não é mais da praça: existe se alguma LOJA dela tem o seu
        if any((OUT/f"planos/{l['local_id']}.json").exists()
               for l in ident[p].get("locais", []) if l.get("papel") == "proprio"):
            tem.append("plano")
        return {"praca_id": p, "nome": ident[p].get("nome"),
                "rotulo": ident[p].get("rotulo") or ident[p].get("nome"),
                "uf": ident[p].get("uf", []),
                "cidades": (ident[p].get("cidades_rotulo")
                            or ident[p].get("cidades", [])),
                "tem": tem, "estudos": len(tem)}

    escreve("manifest", {
        "gerado_em": dt.datetime.now().isoformat(timespec="seconds"),
        "gerado_de": "dados/serie + dados/conteudo + dados/identidade",
        "corte": corte,
        "taxonomia_versao": next((r.get("taxonomia_versao") for r in temas
                                  if r.get("taxonomia_versao")), None),
        "cobertura": {**carrega(CONT, "rede").get("cobertura", {}), **cobertura},
        # o casco NÃO monta rótulo de cidade — recebe pronto, com a UF na frente
        "pracas": [_ficha_praca(p) for p in PRACAS],
        # o índice de verdade: o que existe, agora, nesta pasta
        "arquivos": {
            "rede": [x for x in ("fila", "timeline", "caixa_de_respostas", "padroes", "o_que_mudou", "rede_inteira", "rival", "anuncios", "presenca_por_loja", "voz_da_cidade", "rede", "rede_cruzamento", "achados",
                                 "corretor", "evidencias", "radar", "funil_nacional")
                     if (OUT/f"{x}.json").exists()],
            "clinicas": presentes("clinicas"),
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
