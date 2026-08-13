#!/usr/bin/env python3
"""
execucao_necessaria.py — o que é OPERAÇÃO e o que é MARKETING.

A pergunta que este arquivo existe para responder é uma só, e é a mais
importante do produto para quem vai agir:

    ESTE PROBLEMA SE RESOLVE NO BALCÃO OU FORA DELE?

Porque mandar problema de balcão para agência é queimar dinheiro e
confiança ao mesmo tempo. Se o paciente reclama que ninguém atende o
telefone, nenhuma campanha conserta isso — pelo contrário, mais mídia
sobre um telefone que não atende só aumenta o número de pessoas irritadas.

A separação é dura e está escrita aqui, não no gosto de quem lê:

    OPERAÇÃO — recepção, telefone, WhatsApp, agendamento, cobrança,
               atendimento clínico, manutenção. Quem resolve é a
               unidade. Nunca vira briefing de agência.

    MARKETING — encontrabilidade, ficha do Google, presença na busca,
               mídia paga, conteúdo, criativo, ativação local. Aqui sim
               existe execução especializada, e o briefing é gerado.

O QUE ESTE SCRIPT NÃO FAZ

· Não inventa orçamento. Não sabe quanto custa, e fingir que sabe seria
  o tipo de número que destrói a credibilidade de tudo em volta.
· Não promete retorno. Não temos faturamento, lead nem conversão —
  prometer resultado com dado externo é chute com cara de projeção.
· Não diz que a execução aconteceu. O portal não fala com a unidade nem
  com a agência; ele registra a recomendação e depois mede de novo.
· Não gera briefing sem evidência. Sem número medido por trás, a
  recomendação não sai.

Uso:
    python3 scripts/execucao_necessaria.py
    python3 scripts/execucao_necessaria.py --salvar
"""
import argparse, json, pathlib, sys
import datetime as dt

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from cruzamento import identidades, conta, confianca

RAIZ = pathlib.Path(__file__).resolve().parent.parent
OUT = RAIZ/"dados"/"portal"
SAIDA = OUT/"execucao.json"

# Os momentos da jornada que são de BALCÃO. Se a dor pública da unidade
# cai num destes, a resposta é operação — e a agência não é chamada.
DE_OPERACAO = {
    "contato": "telefone e WhatsApp sem resposta",
    "agendamento": "marcar, remarcar e encaixar",
    "recepcao": "chegada, espera e acolhimento",
    "cobranca": "mensalidade, boleto e multa",
    "clinico": "o atendimento na cadeira",
    "manutencao": "as voltas de cada mês",
    "suporte": "quando algo quebra e ninguém resolve",
    "avaliacao": "a primeira consulta",
    "contencao": "alta e depois dela",
}
# E os que abrem espaço para execução especializada.
DE_MARKETING = {
    "descoberta": "como a pessoa chega até a clínica",
    "contratacao": "preço e oferta, quando é posicionamento e não balcão",
}


def carrega(nome):
    p = OUT/f"{nome}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()

    ident = identidades()
    pres = {x["local_id"]: x for x in carrega("presenca_por_loja").get("lojas", [])}
    # A ESCALA DA MEDIÇÃO DECIDE SE EXISTE PROBLEMA.
    #
    # "aparece em 0 de 193 buscas da cidade" gerava briefing de SEO local
    # para as quatro unidades de São Paulo. Uma delas é o PRIMEIRO
    # resultado nas cinco buscas feitas da porta dela. Mandar essa para a
    # agência é gastar dinheiro num problema que não existe — e é a mesma
    # família de erro que mandar problema de balcão para campanha.
    perto = {x["local_id"]: x for x in carrega("perto_da_loja").get("lojas", [])}
    jor = {x["local_id"]: x for x in carrega("jornada").get("lojas", [])}
    cx = {x.get("local_id"): x for x in carrega("caixa_de_respostas").get("unidades", [])}
    ba = {x["praca_id"]: x for x in carrega("bairros").get("pracas", [])}
    of = {x["praca_id"]: x for x in carrega("oferta").get("pracas", [])}
    fila = {x["local_id"]: x for x in carrega("fila").get("fila", [])}

    fora = []
    for pid, pr in ident.items():
        for l in pr.get("locais", []):
            if l.get("papel") != "proprio":
                continue
            lid = l["local_id"]
            unidade = l.get("unidade") or l.get("nome") or lid
            itens = []

            # ── 1 · a dor pública decide quem resolve ──────────────────
            j = jor.get(lid) or {}
            pior = next((e for e in (j.get("estagios") or [])
                         if e.get("quem_resolve") and j.get("quem_resolve")
                         and e["rotulo"].lower() in (j.get("manchete") or "").lower()),
                        None)
            estagio = (pior or {}).get("estagio")
            if estagio in DE_OPERACAO:
                itens.append({
                    "problema": j.get("manchete"),
                    "e_marketing": False,
                    "execucao": {
                        "necessaria": True, "tipo": "operacao",
                        "especialidade": "a própria unidade",
                        "porque_nao_e_marketing": (
                            f"a dor pública está em {DE_OPERACAO[estagio]}. "
                            "Campanha não conserta isso — mais mídia sobre um "
                            "gargalo de balcão só aumenta o número de pessoas "
                            "irritadas."),
                        "quem_resolve": (pior or {}).get("quem_resolve"),
                        "metrica_de_validacao": "as mesmas avaliações, "
                                                "reclassificadas na próxima coleta",
                        "recoletar_em_dias": 30,
                    },
                    "evidencias": [e["frase"] for e in (j.get("estagios") or [])
                                   if e.get("frase") and e.get("dor")][:3],
                    # A AMOSTRA ESTAVA NO TEXTO E FORA DO CARIMBO. O item
                    # dizia "14 de 17 avaliações são de 1 ou 2 estrelas" e o
                    # carimbo saía com "sem amostra declarada" — o número
                    # existia, só não estava onde a procedência o lê.
                    "confianca": confianca(
                        "recomendacao",
                        amostra=(pior or {}).get("avaliacoes"),
                        unidade_amostra=("avaliação neste momento da jornada",
                                         "avaliações neste momento da jornada"),
                        fonte="dados/portal/jornada.json",
                        a_favor=[j.get("manchete")] if j.get("manchete") else [],
                        o_que_aumentaria="a próxima medição da jornada"),
                })

            # ── 2 · invisível na busca é MARKETING, e tem briefing ─────
            pb = pres.get(lid) or {}
            pe = perto.get(lid) or {}
            # a loja se defende no próprio quarteirão? então o número da
            # cidade é escala, não gargalo, e não gera briefing
            defende_se = bool(pe.get("de")) and (
                (pe.get("aparece_em") or 0) / pe["de"] >= 0.4)
            if pb and pb.get("de") and not defende_se:
                ap_ = pb.get("aparece_em") or 0
                if pb.get("invisivel") or (pb["de"] and ap_ / pb["de"] < 0.08):
                    frases = (pb.get("frases_onde_aparece") or [])[:5]
                    itens.append({
                        "problema": pb.get("frase_do_topo"),
                        "e_marketing": True,
                        "execucao": {
                            "necessaria": True,
                            "tipo": "seo_local",
                            "especialidade": "marketing local e Google Business",
                            "problema": (
                                f"a unidade aparece em "
                                f"{conta(ap_, 'busca', 'buscas')} de "
                                f"{pb['de']} testadas na própria cidade"),
                            "objetivo": ("ser encontrada nas frases que a "
                                         "cidade digita para procurar aparelho"),
                            "evidencias": ([f"aparece em {ap_} de {pb['de']} buscas"]
                                           + [f"aparece em: {f}" for f in frases]),
                            "nao_fazer": [
                                "não comprar mídia antes de a ficha estar "
                                "correta — pagar para levar gente a um "
                                "cadastro errado é pior do que não pagar",
                                "não prometer posição: o Google não vende "
                                "ordem no mapa",
                            ],
                            "entregavel_sugerido": (
                                "ficha do Google revisada — categoria "
                                "primária, endereço, horário, fotos e "
                                "serviços — e as frases da cidade cobertas "
                                "na descrição e nas publicações"),
                            "prazo": "30 dias",
                            "metrica_de_validacao": (
                                "refazer EXATAMENTE as mesmas buscas desta "
                                "medição e comparar quantas passam a mostrar "
                                "a unidade"),
                            "recoletar_em_dias": 30,
                        },
                        "confianca": confianca(
                            "recomendacao",
                            amostra=pb.get("de"),
                            unidade_amostra=("busca testada", "buscas testadas"),
                            medicoes=1,
                            fonte="dados/portal/presenca_por_loja.json",
                            a_favor=[pb.get("frase_do_topo")],
                            contra=["uma medição só — a segunda dirá se é "
                                    "estrutural ou momento"],
                            o_que_aumentaria="repetir a varredura de buscas "
                                             "noutra data"),
                    })

            # ── 2b · e quando NÃO precisa, isso também se declara ──────
            #
            # Estado vazio é conteúdo. Se a leitura da cidade acusou e a
            # leitura de perto inocentou, esconder o caso faria a unidade
            # sumir da tela — e amanhã alguém abriria o número da cidade e
            # pediria a campanha de novo.
            if pb and pb.get("de") and defende_se and not (pb.get("aparece_em") or 0):
                itens.append({
                    "problema": (f"a leitura da cidade diz 0 de {pb['de']}, "
                                 f"e ela não vale nesta escala"),
                    "e_marketing": True,
                    "execucao": {
                        "necessaria": False,
                        "tipo": "seo_local",
                        "porque_nao": (
                            f"medida a partir do endereço da própria "
                            f"clínica, ela aparece em "
                            f"{conta(pe['aparece_em'], 'busca', 'buscas')} "
                            f"de {pe['de']}"
                            + (f", em {conta(pe['em_primeiro'], 'vez', 'vezes')} "
                               f"em 1º lugar" if pe.get("em_primeiro") else "")
                            + ". Ninguém disputa o nome do município inteiro "
                              "numa cidade deste tamanho: o paciente busca de "
                              "onde está."),
                        "metrica_de_validacao": "a mesma grade de buscas, "
                                                "a partir do mesmo endereço",
                        "recoletar_em_dias": 60,
                    },
                    "confianca": confianca(
                        "fato", amostra=pe.get("de"),
                        unidade_amostra=("busca testada", "buscas testadas"),
                        medicoes=1,
                        fonte="dados/serie/perto_da_loja.jsonl",
                        o_que_aumentaria="mais frases por loja na próxima grade"),
                })

            # ── 3 · avaliação negativa aberta é OPERAÇÃO ───────────────
            c = cx.get(lid) or {}
            if (c.get("abertas") or 0) >= 5:
                itens.append({
                    "problema": (conta(c["abertas"], "avaliação negativa aberta",
                                       "avaliações negativas abertas")
                                 + " sem resposta"),
                    "e_marketing": False,
                    "execucao": {
                        "necessaria": True, "tipo": "reputacao",
                        "especialidade": "a própria unidade",
                        "porque_nao_e_marketing": (
                            "responder paciente é trabalho de quem atende. "
                            "Agência escrevendo resposta em nome da clínica "
                            "é o caminho mais curto para uma resposta que o "
                            "paciente percebe como automática."),
                        "metrica_de_validacao": "quantas seguem sem resposta "
                                                "na próxima coleta",
                        "recoletar_em_dias": 15,
                    },
                    "confianca": confianca(
                        "recomendacao", amostra=c.get("abertas"),
                        unidade_amostra=("avaliação", "avaliações"),
                        fonte="dados/portal/caixa_de_respostas.json"),
                })

            if itens:
                fora.append({
                    "local_id": lid, "praca_id": pid,
                    "rotulo": pr.get("rotulo"), "unidade": unidade,
                    "itens": itens,
                    # só conta quem GERA trabalho: o caso declarado como
                    # "não precisa" aparece na tela e fica fora da conta
                    "de_marketing": sum(
                        1 for i in itens
                        if i["e_marketing"] and i["execucao"].get("necessaria")),
                    "de_operacao": sum(
                        1 for i in itens
                        if not i["e_marketing"] and i["execucao"].get("necessaria")),
                    "descartados": sum(
                        1 for i in itens if not i["execucao"].get("necessaria")),
                })

    mkt = sum(x["de_marketing"] for x in fora)
    ope = sum(x["de_operacao"] for x in fora)
    desc = sum(x["descartados"] for x in fora)
    # unidade que só recebeu declaração de "não precisa" não é unidade com
    # execução a recomendar — ela aparece na tela, e fora desta conta
    com_trabalho = [x for x in fora if x["de_marketing"] or x["de_operacao"]]
    print(f"  {conta(len(com_trabalho), 'unidade')} com execução a recomendar")
    print(f"    {ope} de OPERAÇÃO — ficam com a unidade")
    print(f"    {mkt} de MARKETING — geram briefing")
    print("    " + conta(desc, "caso medido e declarado como NÃO necessário",
                         "casos medidos e declarados como NÃO necessários"))
    for x in fora[:6]:
        print(f"\n  {x['rotulo']} · {x['unidade'][:34]}")
        for i in x["itens"]:
            marca = ("MKT" if i["e_marketing"] else "OPE") \
                if i["execucao"].get("necessaria") else "—"
            print(f"    [{marca:>3s}] {(i['problema'] or '')[:78]}")

    if not a.salvar:
        print("\n  (--salvar para gravar)")
        return
    SAIDA.write_text(json.dumps({
        "o_que_e": "O que precisa ser executado em cada unidade, separado "
                   "entre o que é da própria unidade e o que exige execução "
                   "especializada.",
        "a_regra": "problema de balcão nunca vira briefing de agência: "
                   "campanha não conserta telefone que não atende",
        "o_que_nao_e": "não há orçamento, não há promessa de retorno, e nada "
                       "aqui afirma que a execução aconteceu",
        "medido_em": dt.date.today().isoformat(),
        "unidades": fora,
        "de_marketing": mkt, "de_operacao": ope,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n  → {SAIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
