#!/usr/bin/env python3
"""
o_mapa_dos_bairros.py — a cidade grande não é uma praça só.

POR QUE ISTO EXISTE. Porto Alegre tem 9 unidades da rede; Curitiba, 8;
Cuiabá, 3. Ler a cidade inteira como um mercado único funde nove
franqueados possivelmente diferentes no mesmo número — o mesmo erro que
a média das três lojas de Cuiabá já cometeu, agora em escala maior. Numa
cidade de 1,4 milhão de habitantes a unidade não disputa "Porto Alegre":
ela disputa o bairro dela e os vizinhos.

E o dado para isso JÁ ESTAVA NO DISCO. A varredura da categoria guarda o
endereço de cada clínica, e 98% deles trazem o bairro. Não foi preciso
coletar nada — foi preciso ler o que já tinha sido coletado.

O QUE ESTE SCRIPT RESPONDE

· Em que bairro cada unidade nossa está.
· Quem são os VIZINHOS dela — os concorrentes do mesmo bairro, que é
  contra quem ela disputa de verdade, não a cidade toda.
· Onde a categoria se concentra na cidade, e se a rede está lá.
· Que bairro tem procura (muita clínica) e nenhuma unidade nossa — que é
  onde a próxima pode caber.

O QUE ELE NÃO FAZ

· Não mede distância nem tempo de deslocamento: não temos coordenada,
  temos texto de endereço. Bairro vizinho no papel pode estar longe.
· Não afirma que concentração de clínicas é concentração de demanda. É
  concentração de OFERTA, e são coisas diferentes — em geral andam
  juntas, mas isso é inferência, e vai declarada como tal.
· Não trata bairro sem endereço legível como bairro vazio.

Uso:
    python3 scripts/o_mapa_dos_bairros.py
    python3 scripts/o_mapa_dos_bairros.py --salvar
    python3 scripts/o_mapa_dos_bairros.py --praca porto_alegre
"""
import argparse, json, pathlib, re, sys, unicodedata
import datetime as dt
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from cruzamento import identidades, conta, confianca

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SERIE = RAIZ/"dados"/"serie"
SAIDA = RAIZ/"dados"/"portal"/"bairros.json"

MIN_PARA_BAIRRO = 3     # clínicas num bairro para ele virar linha na tela


def sa(t):
    return "".join(c for c in unicodedata.normalize("NFD", str(t or ""))
                   if unicodedata.category(c) != "Mn").lower().strip()


def bairro_de(endereco):
    """O bairro dentro do endereço brasileiro do Google.

    O formato é
        'R. Sergipe, 829 - 1º Andar - Centro, Londrina - PR, 86010-000'
    e o bairro é o ÚLTIMO trecho antes de ", Cidade - UF".

    A primeira versão pegava o primeiro " - " que casasse e devolvia
    "1º Andar - Centro" para a loja de Londrina e "Rua NE1" para a de
    Palmas. Pior: com o bairro errado, o script concluiu que a rede NÃO
    está no Centro de Londrina — e ela está. Complemento de endereço
    (andar, sala, quadra, lote) mora entre o número e o bairro, então o
    corte certo é sempre o de trás para a frente.
    """
    if not endereco:
        return None
    partes = [x.strip() for x in str(endereco).split(",")]
    # acha o trecho "Cidade - UF" e pega o que vem imediatamente antes
    alvo = None
    for i, x in enumerate(partes):
        if re.fullmatch(r".+ - [A-Z]{2}", x) and i > 0:
            alvo = partes[i-1]
            break
    if alvo is None:
        return None
    # dentro dele, o bairro é o pedaço depois do último " - "
    b = alvo.split(" - ")[-1].strip()
    if (re.fullmatch(r"[\d\-\s]+", b) or len(b) < 3
            or re.match(r"^\d+$", b)):
        return None
    return b


def linhas(nome):
    a = SERIE/f"{nome}.jsonl"
    if not a.exists():
        return []
    return [json.loads(l) for l in a.read_text(encoding="utf-8").split("\n")
            if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--praca")
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()

    ident = dict(identidades())
    for arq in sorted((RAIZ/"dados"/"identidade").glob("*.json")):
        ident.setdefault(arq.stem, json.loads(arq.read_text(encoding="utf-8")))

    # a ponta de cada clínica varrida
    ult = {}
    for r in sorted(linhas("categoria"), key=lambda r: r.get("snapshot_date", "")):
        ult[(r.get("praca_id"), r.get("place_id"))] = r

    # onde ESTÃO as nossas unidades (pelo place_id da identidade)
    nossos_place = {}
    for pid, pr in ident.items():
        for l in pr.get("locais", []):
            if l.get("papel") == "proprio" and l.get("place_id"):
                nossos_place[l["place_id"]] = (pid, l)

    por_praca = defaultdict(lambda: defaultdict(list))
    sem_bairro = defaultdict(int)
    for r in ult.values():
        p = r.get("praca_id")
        if a.praca and p != a.praca:
            continue
        b = bairro_de(r.get("endereco"))
        if not b:
            sem_bairro[p] += 1
            continue
        por_praca[p][b].append(r)

    fora = []
    for p, bairros in sorted(por_praca.items()):
        pr = ident.get(p) or {}
        lojas = [l for l in pr.get("locais", []) if l.get("papel") == "proprio"]
        # o bairro de cada unidade nossa
        onde_estamos = {}
        for l in lojas:
            for b, cs in bairros.items():
                if any(c.get("place_id") == l.get("place_id") for c in cs):
                    onde_estamos[l["local_id"]] = b
        nossos_bairros = set(onde_estamos.values())

        linhas_b = []
        for b, cs in bairros.items():
            aval = sum(c.get("avaliacoes") or 0 for c in cs)
            nossas_aqui = [lid for lid, bb in onde_estamos.items() if bb == b]
            # o rival mais forte do bairro, pelo volume de avaliação
            top = sorted(cs, key=lambda c: -(c.get("avaliacoes") or 0))
            top = [c for c in top if c.get("place_id") not in nossos_place][:3]
            linhas_b.append({
                "bairro": b,
                "clinicas": len(cs),
                "avaliacoes_somadas": aval,
                "temos_unidade": bool(nossas_aqui),
                "nossas": nossas_aqui,
                "vizinhos_fortes": [
                    {"nome": c.get("nome"), "nota": c.get("nota"),
                     "avaliacoes": c.get("avaliacoes")} for c in top],
                "pouca_amostra": len(cs) < MIN_PARA_BAIRRO,
                "frase": (conta(len(cs), "clínica varrida", "clínicas varridas")
                          + (f", e a unidade da rede está aqui"
                             if nossas_aqui else ", e a rede não está aqui")),
            })
        linhas_b.sort(key=lambda x: -x["clinicas"])

        # onde há oferta concentrada e a rede não está
        vazios = [x for x in linhas_b
                  if not x["temos_unidade"] and not x["pouca_amostra"]][:5]
        cobertos = [x for x in linhas_b if x["temos_unidade"]]

        fora.append({
            "praca_id": p,
            "rotulo": pr.get("rotulo") or pr.get("nome") or p,
            "bairros_medidos": len(linhas_b),
            "clinicas_medidas": sum(x["clinicas"] for x in linhas_b),
            "sem_bairro_no_endereco": sem_bairro.get(p, 0),
            "unidades_da_rede": len(lojas),
            "unidades_localizadas": len(onde_estamos),
            "onde_estamos": [
                {"local_id": lid, "bairro": b,
                 "unidade": next((l.get("unidade") or l.get("nome")
                                  for l in lojas if l["local_id"] == lid), lid)}
                for lid, b in sorted(onde_estamos.items())],
            "bairros": linhas_b[:25],
            "bairros_sem_a_rede": vazios,
            "manchete": (
                f"{conta(len(linhas_b), 'bairro medido', 'bairros medidos')}"
                f" · a rede está em {conta(len(cobertos), 'deles', 'deles')}"
                if linhas_b else None),
            "leitura": (
                (f"O bairro com mais clínicas é {linhas_b[0]['bairro']}, com "
                 + conta(linhas_b[0]["clinicas"], "clínica varrida",
                         "clínicas varridas")
                 + (", e a rede está lá." if linhas_b[0]["temos_unidade"]
                    else ", e a rede NÃO está lá."))
                if linhas_b else None),
            "confianca": confianca(
                "fato",
                amostra=sum(x["clinicas"] for x in linhas_b),
                unidade_amostra=("clínica varrida", "clínicas varridas"),
                medicoes=1,
                fonte="dados/serie/categoria.jsonl (endereço da varredura)",
                contra=([f"{sem_bairro.get(p, 0)} endereços sem bairro legível"]
                        if sem_bairro.get(p) else []),
                o_que_aumentaria="busca por coordenada, que diria em que parte "
                                 "da cidade a loja APARECE, e não só onde ela fica"),
        })

    fora.sort(key=lambda x: -x["unidades_da_rede"])
    for x in fora:
        print(f"\n  {x['rotulo']} · {x['manchete']}")
        if x["leitura"]:
            print(f"    {x['leitura']}")
        for o in x["onde_estamos"]:
            print(f"    · {o['unidade'][:34]:<36}{o['bairro']}")
        if x["bairros_sem_a_rede"]:
            v = x["bairros_sem_a_rede"][0]
            print(f"    sem a rede, com procura: {v['bairro']} "
                  f"({v['clinicas']} clínicas)")

    if not a.salvar:
        print("\n  (--salvar para gravar)")
        return
    SAIDA.write_text(json.dumps({
        "o_que_e": "A cidade por dentro: em que bairro cada unidade está, "
                   "contra quem ela disputa ali, e onde a categoria se "
                   "concentra sem a rede.",
        "o_que_nao_e": "Não é distância nem deslocamento — não temos "
                       "coordenada, temos texto de endereço. E concentração "
                       "de clínicas é oferta, não demanda medida.",
        "por_que_existe": "cidade com mais de uma unidade não pode ser lida "
                          "como um mercado só: Porto Alegre tem 9 unidades, "
                          "Curitiba 8, e elas podem ter donos diferentes",
        "medido_em": dt.date.today().isoformat(),
        "minimo_por_bairro": MIN_PARA_BAIRRO,
        "pracas": fora,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n  → {SAIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
