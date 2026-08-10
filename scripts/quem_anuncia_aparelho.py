#!/usr/bin/env python3
"""
quem_anuncia_aparelho.py — quem está comprando mídia de APARELHO, por praça.

O buraco que este arquivo fecha: a rede coletou 735 anúncios em 13 praças
(Biblioteca do Meta + Centro de Transparência do Google) e o portal
mostrava disso um número só, escondido dentro da captação —
`anuncios_ativos: 0`. Quem anuncia, com que texto, há quantos dias e em
qual plataforma nunca teve tela. O franqueado não conseguia responder a
pergunta mais barata da praça dele: "quem está anunciando aparelho na
minha cidade agora?".

A régua do produto vale aqui igual: ODONTOLOGIA NÃO É ORTODONTIA. Um
anúncio de implante, clareamento ou lente de contato dental não disputa
o paciente de aparelho — e nem todo anúncio coletado é de dentista
(a varredura de Contagem trouxe advogado tributarista). Só entra quem
fala do produto no texto ou no nome: aparelho, ortodontia, bráquete,
alinhador, contenção, invisalign. Os descartados aparecem CONTADOS e com
o motivo — esconder o que ficou de fora é o que faz a diretoria achar
que medimos tudo.

Uso:
    python3 scripts/quem_anuncia_aparelho.py
    python3 scripts/quem_anuncia_aparelho.py --salvar   # → dados/portal/anuncios.json
"""
import argparse, json, pathlib, re, sys
from collections import defaultdict

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ/"scripts"))
from cruzamento import jsonl, identidades, conta

PORTAL = RAIZ/"dados"/"portal"

# o produto, no texto do anúncio. "sorriso" fica de fora de propósito:
# implante e lente de contato dental vendem sorriso e não vendem aparelho.
APARELHO = re.compile(r"aparelho|ortodont|ortodôntic|bráquete|braquete|"
                      r"alinhador|contenç|invisalign", re.I)
# `ortho` solto marca concorrente como nosso ("Clínica Ortho Mais" não é
# nossa) — a chave é `orthodontic`, sem espaço e sem acento.
NOSSO = re.compile(r"orthodontic", re.I)

PLATAFORMA = {"meta_ad_library": "Meta", "google_ads_transparency": "Google"}


def plataforma_de(r):
    f = (r.get("fonte") or "").lower()
    for k, v in PLATAFORMA.items():
        if k in f:
            return v
    return "Meta" if "facebook" in f or "apify" in f else "outra"


def monta():
    linhas = jsonl("anuncios")
    if not linhas:
        sys.exit("dados/serie/anuncios.jsonl vazio — rode "
                 "coleta/coletores/meta_ads.py e google_ads.py")
    ident = identidades(com_unidade=False)

    por_praca = defaultdict(list)
    for r in linhas:
        por_praca[r.get("praca_id")].append(r)

    saida = []
    for p, rs in sorted(por_praca.items()):
        if p not in ident:
            continue
        ativos = [r for r in rs if r.get("ativo")]
        do_produto = [r for r in ativos
                      if APARELHO.search((r.get("texto") or "") + " " +
                                         (r.get("anunciante") or ""))]
        fora = [r for r in ativos if r not in do_produto]

        agrupado = defaultdict(list)
        for r in do_produto:
            agrupado[r.get("anunciante") or "sem nome"].append(r)

        anunciantes = []
        for nome, itens in agrupado.items():
            dias = [r.get("dias_no_ar") for r in itens if r.get("dias_no_ar")]
            textos = [t for t in ((r.get("texto") or "").strip() for r in itens) if t]
            anunciantes.append({
                "nome": nome,
                "nosso": bool(NOSSO.search(nome)),
                "anuncios": len(itens),
                # duas páginas do Meta podem ter o MESMO nome — em Juazeiro
                # são duas chamadas "OrthoDontic". Contar nome por página
                # escondia uma delas.
                "paginas": sorted({r.get("page_id") for r in itens
                                   if r.get("page_id")}),
                "dias_no_ar_maior": max(dias) if dias else None,
                "plataformas": sorted({plataforma_de(r) for r in itens}),
                "desde": min((r.get("inicio_declarado") or
                              r.get("first_seen_snapshot") or "")
                             for r in itens) or None,
                "exemplo": (textos[0][:280] + "…") if textos and len(textos[0]) > 280
                           else (textos[0] if textos else None),
            })
        anunciantes.sort(key=lambda a: (not a["nosso"], -a["anuncios"]))
        nossos = [a for a in anunciantes if a["nosso"]]

        rotulo = ident[p].get("rotulo") or p
        if not anunciantes:
            manchete = (f"Ninguém anuncia aparelho em {rotulo} hoje — "
                        f"a praça está com a mídia vazia.")
        elif nossos:
            manchete = (f"{conta(len(anunciantes), 'anunciante')} "
                        f"{'disputa' if len(anunciantes) == 1 else 'disputam'} "
                        f"aparelho em {rotulo}, e a rede é "
                        f"{conta(len(nossos), 'deles', 'deles')}.")
        else:
            manchete = (f"{conta(len(anunciantes), 'anunciante')} "
                        f"{'compra' if len(anunciantes) == 1 else 'compram'} "
                        f"aparelho em {rotulo}, e "
                        f"{'nenhum' if len(anunciantes) > 1 else 'ele não'} "
                        f"é da rede.")

        # A rede anunciando onde a rede não está. Duas fontes independentes
        # dizem que não há unidade em Juazeiro do Norte, e duas páginas
        # chamadas OrthoDontic compram aparelho lá. Isso não vira frase de
        # certeza: fonte externa não distingue unidade nova fora da lista de
        # unidade vizinha comprando a praça. Vira bandeira, com as duas
        # leituras na tela e o nome das páginas para a rede conferir por dentro.
        temos_unidade = any(l.get("papel") == "proprio"
                            for l in ident[p].get("locais", []))
        bandeira = None
        if nossos and not temos_unidade:
            n_pag = len({pg for a in nossos for pg in a["paginas"]}) or len(nossos)
            bandeira = {
                "o_que_e": (f"{conta(n_pag, 'página', 'páginas')} com o "
                            f"nome OrthoDontic {'compra' if n_pag == 1 else 'compram'} "
                            f"aparelho em {rotulo}, e a lista oficial não tem "
                            f"unidade nesta cidade."),
                "paginas_ids": sorted({pg for a in nossos for pg in a["paginas"]}),
                "as_duas_leituras": ["unidade nova, ainda fora da lista oficial",
                                     "unidade vizinha comprando a praça"],
                "so_a_rede_responde": True,
                "paginas": [a["nome"] for a in nossos],
            }

        saida.append({
            "praca_id": p, "rotulo": rotulo,
            "manchete": manchete,
            "temos_unidade": temos_unidade,
            "bandeira": bandeira,
            "anuncios_ativos": len(do_produto),
            "anunciantes_total": len(anunciantes),
            "nossos_total": len(nossos),
            "somos_um_deles": bool(nossos),
            "anunciantes": anunciantes,
            "fora_do_produto": len(fora),
            "fora_do_produto_porque": ("anúncio ativo na cidade que não fala de "
                                       "aparelho, ortodontia, bráquete, alinhador "
                                       "nem contenção — outro produto, outro "
                                       "paciente"),
            "coletados_na_praca": len(rs),
        })

    saida.sort(key=lambda x: -x["anuncios_ativos"])
    return {
        "o_que_e": "Quem está comprando mídia de APARELHO em cada praça, hoje, "
                   "na Biblioteca de Anúncios do Meta e no Centro de "
                   "Transparência do Google.",
        "o_que_nao_e": "Não é quanto o concorrente gasta — nenhuma das duas "
                       "fontes publica valor. É quem está no ar, com que texto "
                       "e há quantos dias.",
        "a_regra": "Só entra anúncio que fala do produto. Implante, clareamento "
                   "e lente de contato dental não disputam o paciente de "
                   "aparelho, e ficam contados fora.",
        "anuncios_ativos": sum(x["anuncios_ativos"] for x in saida),
        "anunciantes_total": sum(x["anunciantes_total"] for x in saida),
        "pracas_sem_ninguem": [x["rotulo"] for x in saida
                               if not x["anunciantes_total"]],
        "pracas": saida,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()
    d = monta()
    print(f"\n{'=' * 80}\n  QUEM ANUNCIA APARELHO — por praça\n{'=' * 80}\n")
    for p in d["pracas"]:
        print(f"  {p['rotulo']:<26} {conta(p['anuncios_ativos'], 'anúncio'):>12} · "
              f"{conta(p['anunciantes_total'], 'anunciante')}"
              f"{'  ← a rede está no ar' if p['somos_um_deles'] else ''}")
        for an in p["anunciantes"][:3]:
            print(f"        {'NOSSO ' if an['nosso'] else '      '}"
                  f"{an['nome'][:44]:<44} "
                  f"{conta(an['anuncios'], 'anúncio'):>12} · "
                  f"{'/'.join(an['plataformas'])}")
        if p["fora_do_produto"]:
            print(f"        ({conta(p['fora_do_produto'], 'anúncio ativo', 'anúncios ativos')} "
                  f"fora do produto, contados fora)")
    print(f"\n  {d['anuncios_ativos']} anúncios de aparelho no ar · "
          f"{d['anunciantes_total']} anunciantes")
    if d["pracas_sem_ninguem"]:
        print(f"  mídia vazia em: {', '.join(d['pracas_sem_ninguem'])}")
    if a.salvar:
        PORTAL.mkdir(parents=True, exist_ok=True)
        (PORTAL/"anuncios.json").write_text(
            json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n  → dados/portal/anuncios.json ({len(d['pracas'])} praças)")


if __name__ == "__main__":
    main()
