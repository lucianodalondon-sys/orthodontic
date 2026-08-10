#!/usr/bin/env python3
"""
produto_do_concorrente.py — quem disputa APARELHO e quem só divide a rua.

A regra que este arquivo aplica é a que está no CLAUDE.md e o cliente já
corrigiu duas vezes: ODONTOLOGIA NÃO É ORTODONTIA. Clínica geral que faz
limpeza e canal não disputa paciente de aparelho; rede de implante idem.
Concorrente do produto é só quem tem EVIDÊNCIA de aparelho.

As duas fontes de evidência (as únicas amarráveis por local):
  1. o NOME — "Ortodontia", "Orto", "Invisalign", "Alinhador" no letreiro
     é autodeclaração de produto;
  2. a VOZ DO CLIENTE — % das avaliações com texto que falam de aparelho,
     ortodontia, bráquete, alinhador ou contenção.

O veredito, por local:
  sim            nome declara aparelho, OU ≥5 menções e ≥5% das avaliações
  nao            ≥40 avaliações com texto e ≤2,5% falam de aparelho —
                 a voz do cliente diz que o negócio ali é outro
  sem_evidencia  amostra pequena demais para afirmar qualquer coisa

Só o "sim" entra nas ferramentas de confronto (rival, fila, quem avança).
O "nao" e o "sem_evidencia" continuam MEDIDOS (a série é append-only e a
evidência pode chegar), mas fora de qualquer conta de concorrência.

Uso:
    python3 scripts/produto_do_concorrente.py            # mostra
    python3 scripts/produto_do_concorrente.py --salvar   # carimba identidade
"""
import argparse, json, pathlib, re, sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ/"scripts"))
from cruzamento import reviews_unicos, identidades

IDENT = RAIZ/"dados"/"identidade"

# "orto" pega Ortodontia/Ortocenter/RedeOrto; "ortopedia" fica de fora.
NOME_APARELHO = re.compile(r"ort(?!oped)h?o|aparelho|alinhador|invisalign", re.I)
NOME_IMPLANTE = re.compile(r"implant", re.I)
TXT_APARELHO = re.compile(
    r"aparelho|ortodon|br[aá]quete|alinhador|contenç|invisalign", re.I)
TXT_IMPLANTE = re.compile(r"implante|protocolo|pr[oó]tese", re.I)


def classifica():
    ident = identidades(com_unidade=False)
    voz = {}
    for r in reviews_unicos():
        t = (r.get("texto") or "").strip()
        if not t:
            continue
        k = (r["praca_id"], r["local_id"])
        d = voz.setdefault(k, {"n": 0, "ap": 0, "im": 0})
        d["n"] += 1
        if TXT_APARELHO.search(t):
            d["ap"] += 1
        if TXT_IMPLANTE.search(t):
            d["im"] += 1

    fora = {}
    for p, dd in sorted(ident.items()):
        for l in dd.get("locais", []):
            if l.get("papel") == "proprio":
                continue
            nome = l.get("nome") or ""
            v = voz.get((p, l["local_id"]), {"n": 0, "ap": 0, "im": 0})
            taxa = v["ap"]/v["n"] if v["n"] else 0.0
            no_nome = bool(NOME_APARELHO.search(nome))
            impl_nome = bool(NOME_IMPLANTE.search(nome))

            if no_nome:
                ver, motivo = "sim", "o nome declara aparelho/ortodontia"
            elif v["ap"] >= 5 and taxa >= 0.05:
                ver, motivo = "sim", (f"{v['ap']} de {v['n']} avaliações "
                                      f"falam de aparelho ({taxa:.0%})")
            elif v["n"] >= 40 and taxa <= 0.025:
                dono = ("implante" if (impl_nome or v["im"] > v["ap"]*3)
                        else "odontologia geral")
                ver = "nao"
                motivo = (f"a voz do cliente é de {dono}: só {v['ap']} de "
                          f"{v['n']} avaliações citam aparelho")
            elif v["n"] < 40:
                ver = "sem_evidencia"
                motivo = (f"amostra pequena ({v['n']} avaliações com texto) — "
                          f"não dá para afirmar o produto")
            else:
                ver = "sem_evidencia"
                motivo = (f"zona cinzenta: {v['ap']} de {v['n']} avaliações "
                          f"citam aparelho ({taxa:.0%}) — faz aparelho, mas "
                          f"não é o negócio principal")

            fora.setdefault(p, []).append({
                "local_id": l["local_id"], "nome": nome,
                "disputa_aparelho": ver, "porque": motivo,
                "avaliacoes_com_texto": v["n"],
                "menciona_aparelho": v["ap"], "menciona_implante": v["im"],
            })
    return fora


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()
    fora = classifica()

    tot = {"sim": 0, "nao": 0, "sem_evidencia": 0}
    print(f"\n{'='*78}\n  QUEM DISPUTA APARELHO — {sum(len(v) for v in fora.values())} "
          f"concorrentes nas 13 praças\n{'='*78}")
    for p, ls in sorted(fora.items()):
        print(f"\n  {p}")
        for x in sorted(ls, key=lambda x: x["disputa_aparelho"]):
            tot[x["disputa_aparelho"]] += 1
            tag = {"sim": "APARELHO", "nao": "  fora  ",
                   "sem_evidencia": "   ?    "}[x["disputa_aparelho"]]
            print(f"    [{tag}] {x['nome'][:44]:44s} {x['porque']}")
    print(f"\n  → {tot['sim']} disputam aparelho · {tot['nao']} fora "
          f"(outro produto) · {tot['sem_evidencia']} sem evidência")

    if a.salvar:
        n = 0
        for p, ls in fora.items():
            arq = IDENT/f"{p}.json"
            d = json.loads(arq.read_text(encoding="utf-8"))
            por_id = {x["local_id"]: x for x in ls}
            for l in d.get("locais", []):
                x = por_id.get(l["local_id"])
                if x and l.get("papel") != "proprio":
                    l["produto"] = {
                        "disputa_aparelho": x["disputa_aparelho"],
                        "porque": x["porque"],
                        "menciona_aparelho": x["menciona_aparelho"],
                        "avaliacoes_com_texto": x["avaliacoes_com_texto"],
                    }
                    n += 1
            arq.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n",
                           encoding="utf-8")
        print(f"  → produto carimbado em {n} concorrentes "
              f"(dados/identidade/*.json)")


if __name__ == "__main__":
    main()
