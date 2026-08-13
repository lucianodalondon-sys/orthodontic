#!/usr/bin/env python3
"""
cruzamento.py — a leitura da REDE, que é o que a franqueadora compra.

O inteligencia.py lê uma praça. Este lê todas juntas, e responde uma pergunta
diferente: **o que vale para a rede e o que vale só para uma cidade?**

É a diferença entre consultoria e sistema. Um estudo diz "sua unidade de
Mafra está parada". Um sistema diz "trinta e sete unidades pararam este mês,
e as sete que não pararam fazem a mesma coisa".

Seis leituras:

  1. O PLACAR DA REDE — todas as unidades, ordenadas, com a posição de cada uma
     dentro da própria praça. Estar em 1º numa cidade fraca não é o mesmo que
     estar em 3º numa cidade brigada.

  2. QUEM PAROU, QUEM LIGOU — o alerta que só existe olhando junto. A matriz de
     Londrina fez a maior campanha da cidade e desligou, e ninguém percebeu
     porque ninguém comparava com ela mesma.

  3. O QUE SE REPETE — cada padrão com o número de praças em que aparece, e o
     degrau na escada. Um padrão visto em 3 regiões diferentes vale mais que um
     visto em 3 cidades vizinhas.

  4. O TERRITÓRIO VAZIO DA REDE — o canal que falta em muitas praças ao mesmo
     tempo é decisão de franqueadora, não de unidade.

  5. AS UNIDADES PARECIDAS — comparar unidade com a rede inteira é injusto.
     Compara-se com quem tem porte e praça parecidos.

  6. O QUE PESA CONTRA — a praça que contraria cada padrão, sempre nomeada.

Uso:
    python3 scripts/cruzamento.py
    python3 scripts/cruzamento.py --salvar     # grava em dados/portal/rede.json
"""
import argparse, json, math, pathlib, re, statistics as st
from collections import defaultdict, Counter

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SERIE = RAIZ/"dados"/"serie"
IDENT = RAIZ/"dados"/"identidade"


def jsonl(nome):
    p = SERIE/f"{nome}.jsonl"
    return [json.loads(l) for l in p.read_text(encoding="utf-8").split("\n") if l.strip()] \
        if p.exists() else []


def id_da_avaliacao(chave):
    """O identificador que o Google dá à avaliação, seja qual for o coletor.

    Em 07/08 um coletor gravou `local_id|<id>`; em 08/08 outro gravou
    `google:<place_id>:<id>`. As chaves nunca casaram, então a deduplicação
    por chave não pegou nada e cinco clínicas ficaram com as MESMAS avaliações
    gravadas duas vezes — 981 linhas, 2,7% da base, concentradas justamente em
    Souza Naves e Mafra, que abrem e fecham o placar. O `<id>` é o último
    pedaço nos dois formatos, e é ele que identifica a avaliação de verdade."""
    return re.split(r"[|:]", chave or "")[-1] or None


def reviews_unicos():
    """As avaliações sem a contagem em dobro. Todo cálculo de ritmo passa aqui.

    Mantém a linha mais recente de cada avaliação — a do coletor novo, que traz
    data em formato ISO limpo — e preserva o primeiro snapshot em que ela
    apareceu, senão a série perde o histórico de quando a avaliação entrou."""
    vistos = {}
    for r in jsonl("reviews"):
        rid = id_da_avaliacao(r.get("chave"))
        k = (r.get("local_id"), rid) if rid else (r.get("chave"), id(r))
        ant = vistos.get(k)
        if ant is None:
            vistos[k] = r
        else:
            novo = r if r.get("snapshot_date", "") >= ant.get("snapshot_date", "") else ant
            velho = ant if novo is r else r
            novo = dict(novo)
            novo["first_seen_snapshot"] = min(
                x for x in (novo.get("first_seen_snapshot"), velho.get("first_seen_snapshot"),
                            novo.get("snapshot_date"), velho.get("snapshot_date")) if x)
            vistos[k] = novo
    return list(vistos.values())


def identidades(com_unidade=True):
    """As praças da REDE. Praça de oportunidade (sem unidade) fica de fora.

    Sem esta trava, as seis praças que o Radar encontrou entrariam no placar
    como unidades sem movimento — e o "3 de 10 sustentam, 5 pararam" viraria
    "3 de 16, 11 pararam". Seria mentira em cima do número que a franqueadora
    mais olha."""
    todas = {p.stem: json.loads(p.read_text(encoding="utf-8"))
             for p in sorted(IDENT.glob("*.json"))}
    # local_id repetido dentro da praça funde loja com loja — foi assim que
    # duas ODONTOMAX de Contagem viraram uma só e a série misturou os
    # contadores. Corromper calado é pior que parar: falha alto.
    # E O GUARDA OLHA O PROJETO INTEIRO, não uma praça de cada vez.
    # Checar só dentro da praça deixou passar `orthodontic` em São Paulo,
    # Rio, Caxias e Uberlândia ao mesmo tempo: quatro lojas, um id. A série
    # é chaveada por local_id globalmente, então a colisão entre cidades
    # funde exatamente como a colisão dentro da cidade.
    de_quem = {}
    entre_pracas = {}
    for k, v in todas.items():
        for l in v.get("locais", []):
            lid = l.get("local_id")
            if lid in de_quem and de_quem[lid] != k:
                entre_pracas.setdefault(lid, {de_quem[lid]}).add(k)
            de_quem[lid] = k
    if entre_pracas:
        raise ValueError(
            "local_id repetido ENTRE praças: "
            + "; ".join(f"{i} em {sorted(ps)}" for i, ps in
                        sorted(entre_pracas.items())[:6])
            + " — a série é chaveada por local_id no projeto inteiro, "
              "duas lojas não dividem identidade")

    for k, v in todas.items():
        ids = [l["local_id"] for l in v.get("locais", [])]
        rep = {i for i in ids if ids.count(i) > 1}
        if rep:
            raise ValueError(f"local_id duplicado em {k}: {sorted(rep)} — "
                             f"duas lojas não dividem identidade")
    if not com_unidade:
        return todas
    return {k: v for k, v in todas.items() if not v.get("sem_unidade")}


def disputa_aparelho(local):
    """Se este local disputa o NOSSO produto — aparelho.

    A regra que o cliente já corrigiu duas vezes: ODONTOLOGIA NÃO É
    ORTODONTIA. Clínica geral e rede de implante dividem a rua, não o
    paciente de aparelho. O veredito vem carimbado na identidade por
    `produto_do_concorrente.py` (nome + voz do cliente); toda ferramenta
    de CONFRONTO (rival, fila, quem avança) filtra por aqui. Quem não
    disputa continua medido, mas fora de qualquer conta de concorrência."""
    if local.get("papel") == "proprio":
        return True
    return (local.get("produto") or {}).get("disputa_aparelho") == "sim"


def ritmo_e_meses(datas, hoje=None):
    """Mesma conta do inteligencia.py, para os números baterem entre as telas."""
    import datetime as dt
    if len(datas) < 5:
        return None, 0
    ds = sorted(datas)
    dias = max((dt.date.fromisoformat(ds[-1]) - dt.date.fromisoformat(ds[0])).days, 1)
    ritmo = round(len(ds)/(dias/30.4), 1)
    hoje = hoje or dt.date.today()
    c = Counter(d[:7] for d in ds)
    tipico = st.median(list(c.values())) or 1
    seguidos, ano, mes = 0, hoje.year, hoje.month - 1
    if mes == 0:
        ano, mes = ano-1, 12
    for _ in range(36):
        if c.get(f"{ano:04d}-{mes:02d}", 0) < max(2, tipico*0.3):
            break
        seguidos += 1
        mes -= 1
        if mes == 0:
            ano, mes = ano-1, 12
    return ritmo, seguidos


def coleta():
    ident = identidades()
    revs = defaultdict(list)
    for r in reviews_unicos():
        if r.get("data"):
            revs[(r.get("praca_id"), r.get("local_id"))].append(str(r["data"])[:10])
    places = {}
    for p in jsonl("places"):
        k = (p.get("praca_id"), p.get("local_id"))
        if k not in places or p["snapshot_date"] >= places[k]["snapshot_date"]:
            places[k] = p

    linhas = []
    for praca, d in ident.items():
        for l in d.get("locais", []):
            k = (praca, l["local_id"])
            ds = revs.get(k, [])
            ritmo, meses = ritmo_e_meses(ds)
            pl = places.get(k, {})
            # AMOSTRA TRUNCADA NÃO ENTRA NO MESMO RANKING.
            #
            # O coletor profundo puxa as N mais NOVAS. Numa loja pequena,
            # essas N cobrem a vida inteira dela; numa loja grande, cobrem
            # poucas semanas. O ritmo sai das duas do mesmo jeito e os dois
            # números não são a mesma coisa:
            #
            #   Curitiba · XV de Novembro   120 avaliações em    44 dias → 82,9/mês
            #   Curitiba · Edifício Odin    120 avaliações em 2.324 dias →  1,6/mês
            #
            # Postos lado a lado dão "cinquenta vezes de diferença", e isso
            # é artefato da coleta, não da operação. Pior: Florianópolis ·
            # Ingleses tinha 120 avaliações em 14 dias e publicava
            # 260,6/mês — numa loja com 267 avaliações no total.
            #
            # Enquanto a loja não for lida até o fim, o ritmo dela é um
            # ritmo RECENTE, fica declarado como tal e sai da classificação.
            total_google = (pl.get("avaliacoes", pl.get("avaliacoes_total"))
                            or l.get("avaliacoes_google") or 0)
            truncada = bool(total_google and len(ds)
                            and len(ds) / total_google < 0.75
                            and total_google - len(ds) > 50)
            janela = 0
            if len(ds) >= 2:
                import datetime as _dt
                _o = sorted(ds)
                janela = (_dt.date.fromisoformat(_o[-1])
                          - _dt.date.fromisoformat(_o[0])).days
            linhas.append({
                "praca": praca, "rotulo": d.get("rotulo") or d.get("nome"),
                "uf": (d.get("uf") or [None])[0],
                # O NOME QUE VAI PARA A TELA É `unidade`, e `nome` é o
                # cadastro cru. Toda unidade da rede se chama OrthoDontic:
                # sem esta linha, as quatro de São Paulo voltam a aparecer
                # como quatro linhas idênticas em toda leitura que passa
                # por aqui. Concorrente não tem `unidade` e cai no `nome`.
                "local_id": l["local_id"],
                "nome": l.get("unidade") or l.get("nome"),
                "papel": l.get("papel"),
                "aparelho": disputa_aparelho(l),
                "total": pl.get("avaliacoes", pl.get("avaliacoes_total")) or l.get("avaliacoes_google"),
                "nota": pl.get("nota") or l.get("nota_google"),
                "ritmo": ritmo, "meses": meses,
                "amostra_lida": len(ds),
                "amostra_dias": janela,
                "amostra_truncada": truncada,
                "ritmo_comparavel": bool(ritmo is not None and not truncada),
                "porque_fora_do_ranking": (
                    f"lemos {len(ds)} das {total_google} avaliações desta "
                    f"clínica, e as mais novas: o ritmo aqui é o dos últimos "
                    f"{janela} dias, não o do histórico. Comparar com quem foi "
                    f"lido por inteiro compararia janelas diferentes."
                    if truncada else None),
            })
    # posição de cada um dentro da própria praça — SÓ ENTRE OS COMPARÁVEIS
    #
    # A CHAVE EXISTE SEMPRE, mesmo quando a posição não. Deixar `posicao` e
    # `de` ausentes para quem ficou fora do ranking derrubou `fila.py` e
    # `o_que_o_rival_faz.py` com KeyError: quem lê não tem como saber que a
    # chave às vezes some. `None` diz "não tem posição, e isso é sabido";
    # chave ausente diz "ninguém pensou nisso".
    for x in linhas:
        x.setdefault("posicao", None)
        x.setdefault("de", None)
    for praca in ident:
        todas_da_praca = [x for x in linhas if x["praca"] == praca]
        na_praca = sorted([x for x in todas_da_praca if x["ritmo_comparavel"]],
                          key=lambda x: -x["ritmo"])
        # "1ª DE 3" PRECISA DIZER DE QUE 3 SE TRATA.
        #
        # Quando quase toda a praça está lida pela metade, o grupo
        # comparável encolhe — Caxias tem 1 de 17, o Rio tem 0 de 15 — e
        # "1ª de 3" numa cidade onde medimos 17 clínicas lê-se como cidade
        # pequena. O número da praça inteira anda junto, e a frase sai
        # pronta daqui: o casco não redige.
        for x in todas_da_praca:
            x["medidas_na_praca"] = len(todas_da_praca)
            x["comparaveis_na_praca"] = len(na_praca)
        for i, x in enumerate(na_praca, 1):
            x["posicao"] = i
            x["de"] = len(na_praca)
            x["frase_da_posicao"] = (
                f"{i}ª em ritmo entre as "
                + conta(len(na_praca), "clínica lida por inteiro",
                        "clínicas lidas por inteiro")
                + (f", de {len(todas_da_praca)} medidas nesta praça"
                   if len(na_praca) < len(todas_da_praca) else ""))
    for x in linhas:
        x.setdefault("frase_da_posicao", None)
    return ident, linhas


def conta(n, singular, plural=None):
    """'1 avaliação', '2 avaliações' — o número junto com o nome certo.

    O portal é lido por diretoria e franqueado, e "ganhou 1 avaliações em
    2 dia(s)" é a frase que faz o leitor desconfiar de todo o resto. O
    `(s)` era a muleta: some. Quem escreve rótulo é quem tem o número na
    mão, e isso é aqui — a tela recebe a frase pronta e certa.
    """
    return f"{n} {singular if abs(n) == 1 else (plural or singular + 's')}"


# ---------------------------------------------------------------- CONFIANÇA
#
# TRÊS COISAS QUE NÃO PODEM PARECER A MESMA NA TELA.
#
# O portal já escreveu, no mesmo tamanho e na mesma cor: "a unidade não
# recebe avaliação há 26 dias" (medido), "a rotina de pedir avaliação
# parou" (deduzido) e "retome o pedido ao fim do atendimento" (sugerido).
# A primeira é verificável, a segunda é uma explicação entre várias
# possíveis, e a terceira é opinião. Publicar as três iguais é o jeito
# mais rápido de perder a credibilidade do produto inteiro — e a rede não
# tem como nos corrigir, porque nenhum dado interno entra aqui.
#
# `confianca()` carimba qualquer leitura com o que a sustenta. A tela
# desenha cada natureza de um jeito; o build nunca deixa passar nada sem
# carimbo.
NATUREZAS = ("fato", "inferencia", "hipotese", "recomendacao")


def confianca(natureza, *, amostra=None, unidade_amostra=("avaliação",
                                                          "avaliações"),
              janela_dias=None, medicoes=None,
              fonte=None, a_favor=None, contra=None, o_que_aumentaria=None,
              medido=True):
    """O carimbo de credibilidade de uma leitura.

    `medido=False` é diferente de amostra zero: um é "não perguntamos",
    o outro é "perguntamos e não há". A tela precisa dizer qual dos dois.

    O grau sai da própria evidência, não do gosto de quem escreve:

        alta    fato medido, com amostra e mais de uma medição
        média   fato com amostra curta, ou inferência bem sustentada
        baixa   hipótese, ou qualquer coisa com uma medição só
    """
    if natureza not in NATUREZAS:
        raise ValueError(f"natureza desconhecida: {natureza!r} "
                         f"— use uma de {NATUREZAS}")
    if not medido:
        grau = "sem_medicao"
    elif natureza == "fato":
        grau = ("alta" if (amostra or 0) >= 30 and (medicoes or 0) >= 2
                else "media" if (amostra or 0) >= 8
                else "baixa")
    elif natureza == "inferencia":
        grau = ("media" if (amostra or 0) >= 30 and (medicoes or 0) >= 2
                else "baixa")
    else:                       # hipótese e recomendação nunca são altas
        grau = "baixa"
    return {
        "natureza": natureza,
        "confianca": grau,
        "medido": bool(medido),
        "amostra": amostra,
        "janela_dias": janela_dias,
        "medicoes": medicoes,
        "fonte": fonte,
        "a_favor": a_favor or [],
        "contra": contra or [],
        "o_que_aumentaria": o_que_aumentaria,
        # a frase de rodapé sai pronta: o casco não redige procedência
        "procedencia": (
            "não medido" if not medido else
            # a unidade da amostra vem de fora: 176 BUSCAS não são 176
            # avaliações, e a procedência escrita errada mina justamente a
            # confiança que este carimbo existe para sustentar
            ("medido em " + conta(amostra, unidade_amostra[0],
                                  unidade_amostra[1])
             if amostra else "sem amostra declarada")
            + (f", {conta(medicoes, 'medição', 'medições')}" if medicoes else "")
            + (f", {conta(janela_dias, 'dia')} de janela" if janela_dias else "")),
    }


def selo(m):
    if m is None:
        return "?"
    if m >= 10:
        return "OPERAÇÃO"
    if m >= 3:
        return "campanha"
    return "parada"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()
    ident, linhas = coleta()
    nossas = [x for x in linhas if x["papel"] == "proprio" and x["ritmo"] is not None]
    todas = [x for x in linhas if x["ritmo"] is not None]

    print(f"\n{'='*78}\n  A REDE — {len(ident)} praças · {len(nossas)} unidades medidas · "
          f"{len(todas)} clínicas\n{'='*78}")

    # ---------------------------------------------------------------- 1
    print("\n## 1 · O PLACAR DA REDE")
    print("  Posição é dentro da PRÓPRIA praça. 1º numa cidade fraca não é o")
    print("  mesmo que 3º numa cidade brigada — por isso as duas colunas.\n")
    print(f"  {'ritmo':>6s} {'meses':>6s} {'posição':>9s} {'total':>6s}  praça · unidade")
    for x in sorted(nossas, key=lambda x: -x["ritmo"]):
        pos = f"{x['posicao']}º de {x['de']}"
        # praça com mais de uma unidade precisa do nome, senão vira duas linhas iguais
        nome = (x["nome"] or "").replace("OrthoDontic", "").strip(" -–—")
        etiq = f"{x['rotulo']}" + (f" · {nome}" if nome else "")
        print(f"  {x['ritmo']:>6.1f} {x['meses']:>6d} {pos:>9s} {str(x['total']):>6s}  "
              f"{etiq[:40]:40s} {selo(x['meses'])}")

    # ---------------------------------------------------------------- 2
    print("\n## 2 · QUEM SUSTENTA E QUEM NÃO")
    op = [x for x in nossas if x["meses"] >= 10]
    camp = [x for x in nossas if 3 <= x["meses"] < 10]
    par = [x for x in nossas if x["meses"] < 3]
    print(f"  OPERAÇÃO (10+ meses seguidos): {len(op)} de {len(nossas)}")
    def etiqueta(x):
        n = (x["nome"] or "").replace("OrthoDontic", "").strip(" -–—")
        return (f"{x['rotulo']}" + (f" · {n}" if n else ""))[:38]
    for x in op:
        print(f"    {etiqueta(x):38s} {x['ritmo']:>5.1f}/mês · {x['meses']} meses")
    if camp:
        print(f"  campanha (3 a 9 meses): {len(camp)}")
        for x in camp:
            print(f"    {etiqueta(x):38s} {x['ritmo']:>5.1f}/mês · {x['meses']} meses")
    if par:
        print(f"  ⚫ PARADA (menos de 3 meses): {len(par)}")
        for x in par:
            print(f"    {etiqueta(x):38s} {x['ritmo']:>5.1f}/mês · {x['posicao']}º de {x['de']}")
    # e o mercado? — só quem disputa APARELHO; clínica geral e implante
    # dividem a rua, não o paciente (regra: odontologia não é ortodontia)
    conc = [x for x in todas if x["papel"] != "proprio" and x.get("aparelho")]
    op_c = sum(1 for x in conc if x["meses"] >= 10)
    print(f"\n  Nos rivais de aparelho: {op_c} de {len(conc)} sustentam "
          f"({100*op_c//max(len(conc),1)}%)")
    print(f"  Na rede:         {len(op)} de {len(nossas)} sustentam "
          f"({100*len(op)//max(len(nossas),1)}%)")
    if len(nossas) and len(conc):
        if 100*len(op)/len(nossas) > 100*op_c/len(conc):
            print("  → A rede sustenta MAIS que o mercado. É o ativo dela.")

    # ---------------------------------------------------------------- 3
    print("\n## 3 · O TERRITÓRIO VAZIO DA REDE")
    print("  Canal que falta em muitas praças ao mesmo tempo é decisão de")
    print("  franqueadora, não de unidade.\n")
    C = jsonl("canais")
    tipos = defaultdict(lambda: {"tem": set(), "falta": set()})
    for c in C:
        t = c.get("tipo")
        if not t:
            continue
        if c.get("handle"):
            tipos[t]["tem"].add(c["praca_id"])
        elif c.get("status") == "nao_encontrado":
            tipos[t]["falta"].add(c["praca_id"])
    for t, v in sorted(tipos.items(), key=lambda x: -len(x[1]["falta"])):
        if not v["falta"]:
            continue
        marca = "  ←— " + ("É ELA QUEM DECIDE O APARELHO" if t == "mae" else
                           "9-15 COM OS PAIS JUNTO" if t == "esporte_base" else "")
        print(f"  {t:18s} falta em {len(v['falta'])} praças: "
              f"{', '.join(sorted(v['falta']))[:44]}{marca.rstrip()}")

    # ---------------------------------------------------------------- 4
    print("\n## 4 · AS UNIDADES PARECIDAS")
    print("  Comparar unidade com a rede inteira é injusto. Compara-se com quem")
    print("  tem porte de praça parecido.\n")
    def porte(x):
        d = ident[x["praca"]]
        pop = 0
        for n in d.get("ibge", []):
            try:
                pop += int((n.get("populacao_estimada") or {}).get("valor") or 0)
            except Exception:
                pass
        return ("acima de 500 mil" if pop >= 500_000 else
                "200 a 500 mil" if pop >= 200_000 else "até 200 mil")
    grupos = defaultdict(list)
    for x in nossas:
        grupos[porte(x)].append(x)
    for g, xs in sorted(grupos.items()):
        med = st.median([x["ritmo"] for x in xs])
        print(f"  {g:18s} {len(xs)} unidades · mediana {med:.1f}/mês")
        for x in sorted(xs, key=lambda x: -x["ritmo"]):
            n = (x["nome"] or "").replace("OrthoDontic", "").strip(" -–—")
            et = (f"{x['rotulo']}" + (f" · {n}" if n else ""))[:36]
            sinal = "acima" if x["ritmo"] > med else ("abaixo" if x["ritmo"] < med else "na mediana")
            print(f"      {et:36s} {x['ritmo']:>5.1f}  {sinal}")

    # ---------------------------------------------------------------- 5
    print("\n## 5 · O QUE PESA CONTRA")
    contra = []
    if op:
        piores = [x for x in op if x["posicao"] > x["de"]/2]
        for x in piores:
            contra.append(f"{x['rotulo']} sustenta há {x['meses']} meses e mesmo assim é "
                          f"{x['posicao']}º de {x['de']} — constância não basta")
    for x in nossas:
        if x["meses"] < 3 and (x["total"] or 0) > 300:
            contra.append(f"{x['rotulo']} tem {x['total']} avaliações acumuladas e parou — "
                          "o problema não é falta de base")
    fortes = [x for x in conc if x["meses"] >= 10 and x["ritmo"] > (st.median([y['ritmo'] for y in nossas]) if nossas else 0)]
    if fortes:
        contra.append(f"{len(fortes)} rivais de aparelho sustentam E correm mais que a mediana da rede")
    for c in (contra or ["(nada encontrado — o que é motivo de desconfiança, não de comemoração)"]):
        print(f"  · {c}")

    # ---------------------------------------------------------------- 6
    print("\n## 6 · O QUE ISSO NÃO VÊ")
    off = jsonl("midia_offline")
    com = {o["praca_id"] for o in off}
    sem = set(ident) - com
    if sem:
        print(f"  ⚠ {len(sem)} praças sem canal offline declarado: {', '.join(sorted(sem))}")
    tot_rede = len(jsonl("unidades_rede")) or len(nossas)
    print(f"  A rede tem {tot_rede} unidades e esta leitura vê {len(nossas)}. "
          f"Tudo aqui é {100*len(nossas)//tot_rede}% da rede.")
    print("  Nenhum número aqui vem de dado interno.\n")

    if a.salvar:
        dst = RAIZ/"dados"/"portal"
        dst.mkdir(parents=True, exist_ok=True)
        (dst/"rede_cruzamento.json").write_text(json.dumps({
            "gerado_em": __import__("datetime").date.today().isoformat(),
            "pracas": len(ident), "unidades": len(nossas), "clinicas": len(todas),
            "placar": sorted(nossas, key=lambda x: -x["ritmo"]),
            "sustentam": len(op), "campanha": len(camp), "paradas": len(par),
            "territorio_vazio": {t: sorted(v["falta"]) for t, v in tipos.items() if v["falta"]},
            "pesa_contra": contra,
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  → dados/portal/rede_cruzamento.json\n")


if __name__ == "__main__":
    main()
