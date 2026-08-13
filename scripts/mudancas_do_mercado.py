#!/usr/bin/env python3
"""
mudancas_do_mercado.py — o que se MOVEU em volta da unidade.

POR QUE ELE EXISTE, E POR QUE NÃO É O `o_que_mudou.py`.

`o_que_mudou` responde "o que mudou na MINHA loja": contador de
avaliações, nota, ritmo — métrica por `local_id`. Esta pergunta continua
sendo dele.

Este script responde outra: "o que mudou NO MERCADO em volta dela" —
concorrente que apareceu, rival que acelerou, anunciante que entrou ou
saiu, oferta que mudou de eixo. A entidade aqui quase nunca é nossa, a
unidade de saída é EVENTO e não métrica, e a praça é o recorte. Enfiar as
duas no mesmo script faria um arquivo com duas perguntas e nenhuma clara.

A REGRA QUE MAIS IMPORTA AQUI

**Falta de coleta não é evento.** Uma clínica que não apareceu na
varredura de hoje não fechou: ela não foi verificada. Um anúncio que não
foi consultado não saiu do ar. Por isso todo par comparado tem de ser de
duas medições EQUIVALENTES — mesma praça, mesma fonte, duas datas em que
aquela praça foi realmente medida.

E a última medição é sempre POR PRAÇA, nunca a última data do arquivo:
cortar pela data global apaga quem não foi medido hoje.

SEM MEDIÇÃO ANTERIOR, O EVENTO É "linha de base criada" — não "não
mudou". As duas coisas são diferentes e a tela precisa distinguir.

Uso:
    python3 scripts/mudancas_do_mercado.py
    python3 scripts/mudancas_do_mercado.py --salvar
    python3 scripts/mudancas_do_mercado.py --praca porto_alegre
"""
import argparse, json, pathlib, sys
import datetime as dt
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from cruzamento import identidades, conta, confianca

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SERIE = RAIZ/"dados"/"serie"
SAIDA = RAIZ/"dados"/"portal"/"mudancas_do_mercado.json"

# Quanto uma métrica precisa andar para virar evento. Abaixo disso é ruído
# de medição, e ruído publicado como movimento destrói a confiança na tela.
SALTO_AVALIACOES = 15      # avaliações ganhas entre duas medições
QUEDA_AVALIACOES = -5      # perder avaliação é raro e sempre relevante
SALTO_NOTA = 0.2
MIN_BASE = 20              # avaliações da entidade para o salto significar algo


def linhas(nome):
    a = SERIE/f"{nome}.jsonl"
    if not a.exists():
        return []
    return [json.loads(l) for l in a.read_text(encoding="utf-8").split("\n")
            if l.strip()]


def datas_da_praca(rows, praca):
    """As datas em que ESTA praça foi realmente medida, em ordem."""
    return sorted({r["snapshot_date"] for r in rows
                   if r.get("praca_id") == praca and r.get("snapshot_date")})


def evento(praca, rotulo, tipo, natureza, severidade, titulo, fato,
           porque, decisao, fonte, evidencia=None, conf=None,
           entidade=None, local_id=None):
    return {
        "evento_id": f"{praca}|{tipo}|{entidade or '-'}",
        "data": dt.date.today().isoformat(),
        "praca_id": praca, "rotulo": rotulo,
        "local_id": local_id, "entidade_id": entidade,
        "tipo": tipo, "natureza": natureza, "severidade": severidade,
        "titulo": titulo, "fato": fato,
        "por_que_importa": porque, "decisao": decisao,
        "fonte": fonte, "evidencia": evidencia or {},
        "confianca": conf,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--praca")
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()

    ident = dict(identidades())
    for arq in sorted((RAIZ/"dados"/"identidade").glob("*.json")):
        ident.setdefault(arq.stem, json.loads(arq.read_text(encoding="utf-8")))

    cat = linhas("categoria")
    ads = linhas("anuncios")
    nossos_place, disputam = set(), set()
    for pid, pr in ident.items():
        for l in pr.get("locais", []):
            if l.get("papel") == "proprio" and l.get("place_id"):
                nossos_place.add(l["place_id"])
            if (l.get("produto") or {}).get("disputa_aparelho") and l.get("place_id"):
                disputam.add(l["place_id"])

    pracas = sorted({r.get("praca_id") for r in cat if r.get("praca_id")})
    if a.praca:
        pracas = [a.praca]

    fora, resumo = [], []
    for p in pracas:
        rot = (ident.get(p) or {}).get("rotulo") or p
        eventos = []

        # ─────────── categoria: quem apareceu, quem acelerou ───────────
        ds = datas_da_praca(cat, p)
        if len(ds) < 2:
            resumo.append({
                "praca_id": p, "rotulo": rot, "eventos": 0,
                "estado": "linha_de_base",
                "porque": (f"esta praça tem {conta(len(ds), 'medição', 'medições')}"
                           " da categoria — movimento só existe com duas "
                           "observações comparáveis"),
            })
            continue
        antes_d, agora_d = ds[-2], ds[-1]
        antes = {r["place_id"]: r for r in cat
                 if r.get("praca_id") == p and r["snapshot_date"] == antes_d}
        agora = {r["place_id"]: r for r in cat
                 if r.get("praca_id") == p and r["snapshot_date"] == agora_d}

        # AMOSTRA E UNIDADE TÊM DE FALAR DA MESMA COISA.
        #
        # Este carimbo recebia o número de AVALIAÇÕES da clínica e o rotulava
        # como "clínicas medidas": o evento do Vitae Center saía com "medido
        # em 3863 clínicas medidas" — 3.863 é a base de avaliações daquela
        # ficha, e a praça inteira tem 27 clínicas. Metadado errado é pior
        # que metadado ausente, porque ele parece rigor.
        _dias = (dt.date.fromisoformat(agora_d)
                 - dt.date.fromisoformat(antes_d)).days
        _fonte = f"dados/serie/categoria.jsonl ({antes_d} → {agora_d})"

        def base_conf(avaliacoes=None):
            """Evento de UMA clínica: a amostra é a base de avaliações dela.

            Sem número de avaliações (evento da praça inteira), a amostra é
            quantas clínicas entraram nas duas medições.
            """
            if avaliacoes is None:
                return confianca(
                    "fato", amostra=len(agora),
                    unidade_amostra=("clínica medida", "clínicas medidas"),
                    medicoes=len(ds), janela_dias=_dias, fonte=_fonte)
            return confianca(
                "fato", amostra=avaliacoes,
                unidade_amostra=("avaliação nesta clínica",
                                 "avaliações nesta clínica"),
                medicoes=len(ds), janela_dias=_dias, fonte=_fonte,
                a_favor=[f"{len(agora)} clínicas medidas nas duas rodadas"])

        # ─────────── A VARREDURA NÃO É ESTÁVEL, E ISSO FOI MEDIDO ───────────
        #
        # Em Cuiabá a varredura devolveu 243 clínicas em 8/ago e 145 em
        # 13/ago, com 130 em comum — 53% de estabilidade. A Places API não
        # devolve o mesmo conjunto duas vezes: o raio, a ordem e o corte
        # mudam a cada chamada.
        #
        # Logo, "apareceu" e "sumiu" NÃO SÃO MENSURÁVEIS com este coletor.
        # Publicá-los daria 113 falsos "concorrente novo/sumiu" numa praça
        # só — ruído da nossa própria medição vendido como movimento do
        # mercado. O que É mensurável é o delta de quem está nas DUAS
        # medições: esse par é comparável, e é só sobre ele que há evento.
        #
        # A instabilidade não some da tela: vira número declarado.
        nos_dois = set(antes) & set(agora)
        estabilidade = round(100 * len(nos_dois) / max(len(antes), len(agora), 1))

        for pid in sorted(nos_dois):
            r, v = agora[pid], antes[pid]
            nome = r.get("nome") or pid
            if pid in nossos_place:
                continue
            a0 = v.get("avaliacoes") or 0
            a1 = r.get("avaliacoes") or 0
            d = a1 - a0
            if a1 >= MIN_BASE and d >= SALTO_AVALIACOES:
                eventos.append(evento(
                    p, rot, "concorrente_acelerou", "fato",
                    "alta" if pid in disputam else "media",
                    f"{nome} acelerou",
                    f"ganhou {conta(d, 'avaliação', 'avaliações')} entre "
                    f"{antes_d} e {agora_d} — de {a0} para {a1}",
                    ("rival de aparelho ganhando atenção no mesmo mercado"
                     if pid in disputam else
                     "clínica odontológica ganhando atenção; nem toda "
                     "disputa aparelho"),
                    "ver o que ele está publicando e anunciando",
                    "dados/serie/categoria.jsonl",
                    {"place_id": pid, "antes": a0, "agora": a1},
                    base_conf(a1), entidade=pid))
            elif a1 >= MIN_BASE and d <= QUEDA_AVALIACOES:
                eventos.append(evento(
                    p, rot, "concorrente_perdeu_avaliacoes", "fato", "baixa",
                    f"{nome} perdeu avaliações",
                    f"caiu de {a0} para {a1} entre {antes_d} e {agora_d}",
                    "queda de contador costuma ser remoção pelo Google, não "
                    "perda de paciente",
                    "observar na próxima medição antes de concluir",
                    "dados/serie/categoria.jsonl",
                    {"place_id": pid, "antes": a0, "agora": a1},
                    base_conf(a1), entidade=pid))
            n0, n1 = v.get("nota"), r.get("nota")
            try:
                if n0 and n1 and abs(float(n1) - float(n0)) >= SALTO_NOTA \
                        and a1 >= MIN_BASE:
                    eventos.append(evento(
                        p, rot, "concorrente_mudou_nota", "fato", "baixa",
                        f"{nome} mudou de nota",
                        f"de {n0} para {n1} entre {antes_d} e {agora_d}",
                        "mudança de nota com base grande costuma vir de "
                        "muitas avaliações novas de uma vez",
                        "olhar junto com o salto de contador",
                        "dados/serie/categoria.jsonl",
                        {"place_id": pid, "antes": n0, "agora": n1},
                        base_conf(a1), entidade=pid))
            except (TypeError, ValueError):
                pass

        # ─────────── anúncios: quem entrou e quem saiu do ar ───────────
        dsa = datas_da_praca(ads, p)
        if len(dsa) >= 2:
            aa, ab = dsa[-2], dsa[-1]
            ant = {r["ad_id"]: r for r in ads
                   if r.get("praca_id") == p and r["snapshot_date"] == aa}
            ago = {r["ad_id"]: r for r in ads
                   if r.get("praca_id") == p and r["snapshot_date"] == ab}
            novos_anunciantes = ({r.get("anunciante") for r in ago.values()}
                                 - {r.get("anunciante") for r in ant.values()})
            for anunciante in sorted(x for x in novos_anunciantes if x):
                quantos = sum(1 for r in ago.values()
                              if r.get("anunciante") == anunciante)
                eventos.append(evento(
                    p, rot, "anunciante_novo", "fato", "media",
                    f"Anunciante novo: {anunciante}",
                    f"{conta(quantos, 'anúncio', 'anúncios')} no ar em {ab}, "
                    f"e nenhum na medição de {aa}",
                    "entrou no leilão da cidade — muda a pressão de mídia",
                    "ler a oferta dele antes de responder",
                    "dados/serie/anuncios.jsonl",
                    {"anunciante": anunciante, "anuncios": quantos},
                    confianca("fato", amostra=len(ago),
                              unidade_amostra=("anúncio medido",
                                               "anúncios medidos"),
                              medicoes=len(dsa),
                              fonte=f"dados/serie/anuncios.jsonl ({aa} → {ab})",
                              contra=["a Biblioteca não publica verba: "
                                      "quantidade de anúncio não é "
                                      "investimento"]),
                    entidade=anunciante))
        elif dsa:
            eventos.append(evento(
                p, rot, "linha_de_base_anuncios", "fato", "baixa",
                "Linha de base de anúncios criada",
                f"primeira medição de anúncios desta praça, em {dsa[-1]}",
                "movimento de campanha só existe a partir da segunda medição",
                "recoletar na próxima rodada para abrir o delta",
                "dados/serie/anuncios.jsonl", {},
                # linha de base tem amostra: é quantos anúncios estavam no
                # ar quando a praça foi consultada pela primeira vez
                confianca("fato", amostra=sum(1 for r in ads
                                        if r.get("praca_id") == p
                                        and r.get("ativo")),
                          unidade_amostra=("anúncio no ar", "anúncios no ar"),
                          medido=True, medicoes=1,
                          fonte="dados/serie/anuncios.jsonl")))

        ordem = {"critica": 0, "alta": 1, "media": 2, "baixa": 3}
        eventos.sort(key=lambda e: (ordem.get(e["severidade"], 9), e["titulo"]))
        fora.extend(eventos)
        resumo.append({
            "praca_id": p, "rotulo": rot, "eventos": len(eventos),
            "estado": "medido",
            "janela": f"{antes_d} → {agora_d}",
            "medicoes_da_praca": len(ds),
            "clinicas_antes": len(antes), "clinicas_agora": len(agora),
            "comparaveis": len(nos_dois),
            "estabilidade_pct": estabilidade,
            "aviso_de_metodo": (
                f"a varredura devolveu {len(antes)} clínicas em {antes_d} e "
                f"{len(agora)} em {agora_d}, com {len(nos_dois)} em comum "
                f"({estabilidade}%). Só as em comum viram evento: aparecer e "
                f"sumir, aqui, é variação da própria varredura, não "
                f"movimento do mercado."),
        })

    por_tipo = defaultdict(int)
    for e in fora:
        por_tipo[e["tipo"]] += 1

    print(f"  {conta(len(fora), 'evento')} em "
          f"{conta(len([r for r in resumo if r['estado'] == 'medido']), 'praça')}")
    for t, q in sorted(por_tipo.items(), key=lambda x: -x[1]):
        print(f"    {t:<32}{q}")
    base = [r for r in resumo if r["estado"] == "linha_de_base"]
    if base:
        print(f"\n  {conta(len(base), 'praça', 'praças')} com uma medição só — "
              f"linha de base criada, sem movimento a declarar")

    if not a.salvar:
        print("\n  (--salvar para gravar)")
        return
    SAIDA.write_text(json.dumps({
        "o_que_e": "O que se moveu no mercado em volta das unidades, entre "
                   "duas medições comparáveis da mesma praça.",
        "o_que_nao_e": "Não é o delta da nossa loja (isso é o_que_mudou.py). "
                       "E falta de coleta nunca vira evento: clínica que não "
                       "apareceu não fechou, anúncio não consultado não saiu "
                       "do ar.",
        "medido_em": dt.date.today().isoformat(),
        "limiares": {"salto_avaliacoes": SALTO_AVALIACOES,
                     "queda_avaliacoes": QUEDA_AVALIACOES,
                     "salto_nota": SALTO_NOTA,
                     "base_minima": MIN_BASE},
        "eventos_total": len(fora),
        "por_tipo": dict(por_tipo),
        "por_praca": resumo,
        "eventos": fora,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n  → {SAIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
