#!/usr/bin/env python3
"""
confere_tese.py — o número citado na tese existe no disco?

POR QUE ISTO EXISTE. A tese, o DNA e o plano são escritos à mão, e é isso
que os torna bons: eles dizem o que a praça É, não o que a tabela mostra.
O preço disso é que eles apodrecem em silêncio. A tese de Curitiba dizia
"82,9 contra 1,6 avaliações por mês — cinquenta vezes de diferença"; a
coleta seguinte leu as unidades até o fim e o mesmo par virou 9,7 contra
1,6. A frase continuou na tela, bonita e errada.

O que este script confere, e só isto:

    · "N,N avaliações por mês"  → bate com algum ritmo da praça?
    · "Nª de N"                 → bate com alguma posição da praça?
    · "N de N buscas"           → bate com alguma medição de presença?
    · "N clínicas num raio de N km" → bate com o território de alguma loja?

Ele NÃO julga o texto, NÃO reescreve nada e NÃO sabe se a frase é boa. Ele
faz uma pergunta só: **este número aparece em algum lugar do disco para
esta praça?** Número que não aparece é sinalizado para um humano olhar —
pode ser cita legítima de outra fonte, e nesse caso a resposta é conferir e
seguir, não apagar.

Uso:
    python3 scripts/confere_tese.py
    python3 scripts/confere_tese.py --praca curitiba
"""
import argparse, json, pathlib, re, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from cruzamento import coleta, conta

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CONT = RAIZ/"dados"/"conteudo"
OUT = RAIZ/"dados"/"portal"


def num(s):
    return float(str(s).replace(",", "."))


def texto_da_praca(d):
    """Todo o texto autorado da praça, num pedaço só."""
    partes = [d.get("tese") or "", d.get("tese_titulo") or ""]
    for x in d.get("dna") or []:
        partes.append(x.get("t", "") if isinstance(x, dict) else str(x))
    for x in d.get("plano") or []:
        if isinstance(x, dict):
            partes += [x.get("t", ""), x.get("d", "")]
        else:
            partes.append(str(x))
    return "\n".join(partes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--praca")
    a = ap.parse_args()

    _, linhas = coleta()
    por_praca = {}
    for x in linhas:
        por_praca.setdefault(x["praca"], []).append(x)

    def carrega(nome, chave="lojas"):
        p = OUT/f"{nome}.json"
        return json.loads(p.read_text(encoding="utf-8")).get(chave, []) \
            if p.exists() else []
    perto = carrega("perto_da_loja")
    pres = carrega("presenca_por_loja")
    # o item de território não carrega `praca_id` — a praça é a do bloco
    # que o contém, e ler o campo de dentro devolvia None para todos
    terr_por = {}
    for bl in carrega("bairros", "pracas"):
        terr_por[bl.get("praca_id")] = bl.get("territorio") or []
    # a jornada é fonte legítima de "N de N": ela conta avaliações de 1 ou 2
    # estrelas dentro das que falam de um momento
    # a loja da jornada não carrega `praca_id`; a praça vem do local_id
    de_quem = {x["local_id"]: x["praca"] for x in linhas}
    jor_por = {}
    for x in carrega("jornada"):
        jor_por.setdefault(de_quem.get(x.get("local_id")), []).append(x)

    arqs = [CONT/f"{a.praca}.json"] if a.praca else sorted(CONT.glob("*.json"))
    achados = 0
    for arq in arqs:
        if not arq.exists():
            print(f"  ⚠ {arq.name} não existe")
            continue
        d = json.loads(arq.read_text(encoding="utf-8"))
        pid = d.get("praca_id") or arq.stem
        us = por_praca.get(pid) or []
        if not us:
            continue
        txt = texto_da_praca(d)
        ritmos = {x["ritmo"] for x in us if x.get("ritmo") is not None}
        posicoes = {(x["posicao"], x["de"]) for x in us
                    if x.get("posicao") and x.get("de")}
        buscas = {(x["aparece_em"], x["de"]) for x in perto + pres
                  if x.get("praca_id") == pid and x.get("de")}
        # somas de praça também são citáveis ("as cinco aparecem em 23 de 25")
        for fonte in (perto, pres):
            xs = [x for x in fonte if x.get("praca_id") == pid and x.get("de")]
            if xs:
                buscas.add((sum(x["aparece_em"] for x in xs),
                            sum(x["de"] for x in xs)))
                buscas.add((sum(x.get("em_primeiro") or 0 for x in xs),
                            sum(x["de"] for x in xs)))
        # e a jornada, que é de onde saem "12 de 13 avaliações desse momento"
        for x in jor_por.get(pid, []):
            for e in x.get("estagios") or []:
                if e.get("dor") is not None and e.get("avaliacoes"):
                    buscas.add((e["dor"], e["avaliacoes"]))
        raios = set()
        for t in terr_por.get(pid, []):
            for k, v in (t.get("raios") or {}).items():
                raios.add((v.get("clinicas"), k))

        fora = []
        for m in re.finditer(r"(\d+[,.]?\d*)\s*avaliaç(?:ão|ões)\s*por\s*m[êe]s", txt):
            if num(m.group(1)) not in ritmos:
                fora.append(f"ritmo {m.group(1)}/mês não bate com nenhuma "
                            f"unidade da praça")
        for m in re.finditer(r"(\d+)ª?\s*de\s*(\d+)\b", txt):
            par = (int(m.group(1)), int(m.group(2)))
            if par not in posicoes and par not in buscas:
                fora.append(f"'{m.group(0)}' não bate com posição nem com "
                            f"medição de busca")
        for m in re.finditer(r"(\d+)\s*de\s*(\d+)\s*(?:frases|buscas)", txt):
            if (int(m.group(1)), int(m.group(2))) not in buscas:
                fora.append(f"'{m.group(0)}' não bate com nenhuma medição "
                            f"de busca")
        for m in re.finditer(r"(\d+)\s*clínicas?\s*num\s*raio\s*de\s*(\d+)\s*km", txt):
            if (int(m.group(1)), f"{m.group(2)}km") not in raios:
                fora.append(f"'{m.group(0)}' não bate com o território "
                            f"de nenhuma loja")

        if fora:
            achados += len(fora)
            print(f"\n  {d.get('rotulo') or pid}")
            for f in fora:
                print(f"    ⚠ {f}")

    if not achados:
        print("  todo número citado nas teses aparece no disco")
    else:
        print(f"\n  {conta(achados, 'número a conferir', 'números a conferir')}"
              f" — pode ser cita legítima de outra fonte; confira antes de mexer")


if __name__ == "__main__":
    main()
