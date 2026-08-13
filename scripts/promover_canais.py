#!/usr/bin/env python3
"""
promover_canais.py — leva para a série os canais que a pesquisa humana já achou.

O buraco que este arquivo tapa
------------------------------
A ETAPA 2 ("quem fala com a cidade") reprovava em 8 das 13 praças. A conclusão
óbvia era que faltava coletar. Estava errada: **os handles já estavam no
repositório** — em `coleta/alvos/*.yaml`, nos dossiês de pesquisa e no
levantamento manual dos canais. Trabalho humano feito meses atrás que nunca
foi transportado para `dados/serie/canais.jsonl`.

O coletor automático, enquanto isso, gravava `handle: null,
status: nao_encontrado` por cima de uma resposta que estava a dois diretórios
de distância.

O segundo buraco: HOMÔNIMO
--------------------------
Os handles que a busca automática ACHOU são, em boa parte, de outra cidade ou
de uma pessoa com aquele sobrenome. Conferidos um a um:

    riobrancoes           Rio Branco Atlético Clube, do ES, desde 1913
    riobrancoecamericana  Rio Branco Esporte Clube, de Americana/SP
    prefsriobrancodosul   Prefeitura de Rio Branco do SUL, no PR
    superriobranco        supermercado num BAIRRO chamado Rio Branco
    caiquemafra           uma pessoa: Caíque Mafra
    casadosabormafra      restaurante em Mafra, PORTUGAL
    _prudente             Guilherme Prudente, professor de educação física
    imperatrizdasmagias   página espírita
    imperatriz_natal      uma vendedora, Janny Braga
    prefsantanaba         Prefeitura de Santana/BA, outro município

Rio Branco/AC contava CINCO canais e nenhum era da cidade. A contagem da
ETAPA 2 estava inflada exatamente onde parecia melhor.

Nada é apagado: a linha rejeitada continua na série com `rejeitado: true` e o
motivo escrito. Série é append-only, e um dia alguém vai perguntar por que
`riobrancoes` saiu.

Uso:
    python3 scripts/promover_canais.py            # mostra o que faria
    python3 scripts/promover_canais.py --salvar
"""
import argparse, datetime as dt, json, pathlib, re, sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SERIE = RAIZ/"dados"/"serie"
ALVOS = RAIZ/"coleta"/"alvos"


# --------------------------------------------------- o que sai, e por que sai
#
# Cada linha aqui foi conferida na bio do próprio perfil. O motivo é o que
# aparece na série — sem ele isto vira lista de exclusão sem defesa.
REJEITAR = {
    ("rio_branco", "riobrancoes"): "Rio Branco Atlético Clube, do Espírito Santo",
    ("rio_branco", "riobrancoecamericana"): "Rio Branco Esporte Clube, de Americana/SP",
    ("rio_branco", "prefsriobrancodosul"): "Prefeitura de Rio Branco do Sul, no Paraná",
    ("rio_branco", "superriobranco"): "supermercado num bairro chamado Rio Branco",
    ("rio_branco", "fundacaoriobranco"): "sem vínculo comprovado com Rio Branco/AC",
    ("mafra", "caiquemafra"): "uma pessoa: Caíque Mafra. Sobrenome, não cidade",
    ("mafra", "casadosabormafra"): "restaurante em Mafra, Portugal",
    ("mafra", "bocamafrapremium"): "marca comercial, sem vínculo com a praça",
    ("prudente", "_prudente"): "Guilherme Prudente, pessoa. Sobrenome, não cidade",
    ("imperatriz", "imperatrizdasmagias"): "página espírita; 'Imperatriz' não é a cidade",
    ("imperatriz", "imperatriz_natal"): "loja de uma vendedora; não é canal da cidade",
    ("feira", "prefsantanaba"): "Prefeitura de Santana/BA, outro município",
    ("feira", "santacasafsa"): "hospital local — é da cidade, mas não é voz_da_cidade",
    # homônimos que a busca na web trouxe e NÃO entraram
    ("juazeiro_do_norte", "prefeituradejuazeiro"): "é Juazeiro/BA, não Juazeiro do Norte/CE",
    ("maraba", "prefeituramarabapaulista"): "é Marabá Paulista, em São Paulo",
    ("rio_branco", "prefeiturariobrancomt"): "é Rio Branco do Mato Grosso",
    ("juazeiro_do_norte", "achadinhosde.promo"): "conta nacional de promoção, não da cidade",
}

# ------------------------------------------------- o que entra, e de onde vem
#
# Só confiança ALTA: o endereço está escrito literalmente num arquivo, com o
# tipo de canal declarado por quem pesquisou. Os de confiança média e baixa
# ficaram de fora de propósito — anunciante odontológico não é canal de preço
# da cidade, e handle inferido por padrão de nome entra na base como fato.
PROMOVER = [
    # praça, tipo, plataforma, handle, fonte
    ("prudente", "voz_da_cidade", "instagram", "livepresidenteprudente", "pesquisas/_dossies/DOSSIE-02-presidente-prudente.md"),
    ("prudente", "gastronomia",   "instagram", "gastronomiaprudente",    "pesquisas/_dossies/DOSSIE-02-presidente-prudente.md"),
    ("prudente", "mae",           "instagram", "espacomaecoruja",        "pesquisas/_dossies/DOSSIE-02-presidente-prudente.md"),
    ("prudente", "preco_achadinho", "instagram", "precobaixoprudente",   "pesquisas/_dossies/DOSSIE-02-presidente-prudente.md"),
    ("prudente", "imprensa",      "instagram", "oimparcialsp",           "pesquisas/_dossies/DOSSIE-02-presidente-prudente.md"),
    ("prudente", "jovem",         "instagram", "nyloungeprudente",       "pesquisas/_dossies/DOSSIE-02-presidente-prudente.md"),
    ("prudente", "humor",         "tiktok",    "olucascavalcanti",       "pesquisas/_dossies/DOSSIE-02-presidente-prudente.md"),
    ("prudente", "esporte_base",  "instagram", "ad.prudente.futsal",     "coleta/OS-CANAIS-DAS-CINCO-PRACAS.md"),

    ("mafra", "imprensa",      "instagram", "riomaframixoficial",   "pesquisas/_dossies/DOSSIE-04-mafra.md"),
    ("mafra", "imprensa",      "instagram", "diarioderiomafra",     "pesquisas/_dossies/DOSSIE-04-mafra.md"),
    ("mafra", "imprensa",      "instagram", "clickriomafra",        "pesquisas/_dossies/DOSSIE-04-mafra.md"),
    ("mafra", "voz_da_cidade", "instagram", "dicasriomafra",        "pesquisas/_dossies/DOSSIE-04-mafra.md"),
    ("mafra", "gastronomia",   "instagram", "restaurante.vitorino", "pesquisas/_dossies/DOSSIE-04-mafra.md"),
    ("mafra", "esporte_base",  "instagram", "mafra_futsal_oficial", "pesquisas/_dossies/DOSSIE-04-mafra.md"),
    ("mafra", "mae",           "instagram", "maternidadecatarinakuss", "pesquisas/_dossies/DOSSIE-04-mafra.md"),
    ("mafra", "preco_achadinho", "instagram", "crescieperdi_mafra",  "coleta/OS-CANAIS-DAS-CINCO-PRACAS.md"),

    ("feira", "imprensa",        "instagram", "acordacidade",     "coleta/alvos/feira.yaml"),
    ("feira", "preco_achadinho", "instagram", "feiraguayfs.oficial", "coleta/alvos/feira.yaml"),
    ("feira", "preco_achadinho", "instagram", "atacadaosaoroque", "coleta/OS-CANAIS-DAS-CINCO-PRACAS.md"),
    ("feira", "humor",           "instagram", "humorfeirense",    "coleta/alvos/feira.yaml"),
    ("feira", "jovem",           "instagram", "jqvfeiradesantana", "dados/bruto/feira/canais/2026-08-08/busca.json"),
    ("feira", "gastronomia",     "instagram", "iasminconfeitaria", "dados/bruto/feira/canais/2026-08-08/busca.json"),
    ("feira", "esporte_base",    "instagram", "zero75esportes",   "coleta/OS-CANAIS-DAS-CINCO-PRACAS.md"),

    ("rio_branco", "imprensa",        "instagram", "acre68.noticias",              "dados/bruto/rio_branco/canais/2026-08-09/busca.json"),
    ("rio_branco", "jovem",           "instagram", "unip.riobranco",               "dados/bruto/rio_branco/canais/2026-08-09/busca.json"),
    ("rio_branco", "preco_achadinho", "instagram", "shinerayriobranco",            "dados/bruto/rio_branco/canais/2026-08-09/busca.json"),
    ("rio_branco", "gastronomia",     "instagram", "caseirinhosmaeefilhooficial",  "dados/bruto/rio_branco/canais/2026-08-09/busca.json"),

    ("imperatriz", "voz_da_cidade", "instagram", "imperatrizeregiao", "dados/bruto/imperatriz/canais/2026-08-09/busca.json"),
    ("imperatriz", "voz_da_cidade", "instagram", "aciimperatriz",     "dados/bruto/imperatriz/canais/2026-08-09/busca.json"),
    ("imperatriz", "jovem",         "instagram", "unigrandeitz",      "dados/bruto/imperatriz/canais/2026-08-09/busca.json"),

    ("maraba", "prefeitura", "web", "maraba.pa.gov.br", "dados/serie/imprensa.jsonl"),
    ("parauapebas", "prefeitura", "web", "parauapebas.pa.gov.br", "dados/serie/imprensa.jsonl"),
    ("parauapebas", "imprensa",   "web", "zedudu.com.br",         "dados/serie/imprensa.jsonl"),
]

# ------------------------------------------- achados em busca na web, ago/2026
#
# A busca automática do Instagram devolveu lista VAZIA nestas praças, e o
# garimpo no disco esgotou o que havia. Estes vieram de busca na web, um a um,
# com o número de seguidores conferido na própria página do perfil.
#
# A busca trouxe a armadilha de homônimo de novo, e três vezes:
#   @prefeituradejuazeiro      é Juazeiro/BA, não Juazeiro do NORTE/CE
#   @prefeituramarabapaulista  é Marabá Paulista/SP
#   @prefeiturariobrancomt     é Rio Branco do MATO GROSSO
# Nenhum entrou. O certo de cada praça está abaixo.
#
# E um caso diferente, que também ficou de fora: @achadinhosde.promo tem 511 mil
# seguidores e apareceu na busca de Juazeiro, mas é conta NACIONAL de promoção.
# Seguidor grande não faz canal ser local.
DA_WEB = [
    # CE · Juazeiro do Norte
    ("juazeiro_do_norte", "prefeitura",    "instagram", "prefjuazeirodonorte", 93000),
    ("juazeiro_do_norte", "voz_da_cidade", "instagram", "juazeirodonorte.ce", 315000),
    ("juazeiro_do_norte", "voz_da_cidade", "instagram", "juazeiroemfotos", 338000),
    ("juazeiro_do_norte", "imprensa",      "instagram", "jornaldocariri", 19000),
    ("juazeiro_do_norte", "humor",         "instagram", "juazeiromemes", None),
    ("juazeiro_do_norte", "gastronomia",   "instagram", "poraoburger", 165000),
    ("juazeiro_do_norte", "gastronomia",   "instagram", "monsieur.creme", 34000),
    ("juazeiro_do_norte", "gastronomia",   "instagram", "pointdacomidacaseiraoficiall", 32000),

    # PA · Marabá
    ("maraba", "prefeitura",    "instagram", "prefeituramaraba", 139000),
    ("maraba", "voz_da_cidade", "instagram", "notificamaraba", 146000),
    ("maraba", "voz_da_cidade", "instagram", "marabaurgente", 94000),
    ("maraba", "voz_da_cidade", "instagram", "bodimdemaraba", 115000),
    ("maraba", "imprensa",      "instagram", "tvcorreiomaraba", 29000),
    # página de torcedor do Águia, não veículo de imprensa
    ("maraba", "esporte_base",  "instagram", "aguia_de_mab_inf", 5843),

    # PA · Parauapebas
    ("parauapebas", "voz_da_cidade", "instagram", "parauapebas", 227000),
    ("parauapebas", "imprensa",      "instagram", "pebasnoticias1", 100000),
    ("parauapebas", "imprensa",      "instagram", "noticiasdeparauapebas", 75000),
    ("parauapebas", "prefeitura",    "instagram", "camaradeparauapebas", 16000),
    ("parauapebas", "gastronomia",   "instagram", "containers.pbs", 5722),
    ("parauapebas", "jovem",         "instagram", "uepa.parauapebas", 6830),

    # SC · Florianópolis — busca na web, ago/2026
    #
    # A busca automática do coletor rodou TRÊS vezes nesta praça e convergiu em
    # cinco canais. Não foi falta de cota: a terceira execução rodou com US$ 44
    # livres e trouxe os mesmos. A capital tem imprensa e humor fortes que a
    # busca por NOME não acha, porque nenhum deles tem "florianopolis" no
    # handle — @agorafloripa, @tudixfloripa, @informe_floripa.
    #
    # Cada bio foi lida antes de entrar:
    #   agorafloripa.com.br  "as últimas notícias da Grande Florianópolis"
    #   informe_floripa      "jornal online — Grande Florianópolis"
    #   tudixfloripa         "Humor, informação e peixe frito · Grande Floripa"
    #   guiagourmetfloripa   "Guia da melhor #gastronomia de Florianópolis e região"
    #   basedofigueira       perfil oficial das categorias de base do Figueirense
    #   racadabase           categorias de base do Avaí F.C.
    #
    # Figueirense e Avaí são os dois clubes DA CIDADE — é o mesmo teste que
    # reprovou @riobrancoes (Espírito Santo) e @caiquemafra (uma pessoa).
    ("florianopolis", "imprensa",     "instagram", "agorafloripa.com.br", 200000),
    ("florianopolis", "imprensa",     "instagram", "informe_floripa", 59000),
    ("florianopolis", "humor",        "instagram", "tudixfloripa", 134000),
    ("florianopolis", "gastronomia",  "instagram", "guiagourmetfloripa", 23000),
    ("florianopolis", "esporte_base", "instagram", "basedofigueira", 7989),
    ("florianopolis", "esporte_base", "instagram", "racadabase", 38000),

    # PA · Marabá (segunda rodada)
    ("maraba", "jovem",         "instagram", "unamamaraba", 21000),
    # @aguiademarabafc é o handle do X, não do Instagram. Eu tinha escrito o
    # do X vindo de um artigo da Wikipédia — handle não conferido é handle
    # inventado, e inventado entra na base como fato.
    ("maraba", "esporte_base",  "instagram", "aguiademaraba", 150000),

    # MA · Imperatriz
    ("imperatriz", "prefeitura",    "instagram", "prefeituradeimperatriz", 149000),
    ("imperatriz", "voz_da_cidade", "instagram", "imperatrizonline", 379000),
    ("imperatriz", "imprensa",      "instagram", "imperatriznoticias", 59000),
    ("imperatriz", "imprensa",      "instagram", "jornalimperatriz", 16000),
    ("imperatriz", "esporte_base",  "instagram", "escolaoficialgremio_itz", None),

    # AC · Rio Branco
    ("rio_branco", "prefeitura",    "instagram", "prefriobranco", 62000),
    ("rio_branco", "imprensa",      "instagram", "alertacidadeac", 129000),
    ("rio_branco", "imprensa",      "instagram", "acreemnoticia", 27000),
    ("rio_branco", "voz_da_cidade", "instagram", "alertariobranco", None),
    ("rio_branco", "imprensa",      "instagram", "cidadeacnews", 4620),
]


def do_yaml(praca):
    """Os alvos guardam handle, tipo, seguidores e nota — tudo que a série quer.

    Lido com regex de propósito: o repositório não tem PyYAML garantido e o
    formato aqui é plano. Se um dia virar YAML complexo, isto quebra alto em
    vez de importar errado calado."""
    a = ALVOS/f"{praca}.yaml"
    if not a.exists():
        return []
    fora, atual = [], {}
    for l in a.read_text(encoding="utf-8").split("\n"):
        m = re.match(r"\s*-?\s*(tipo|platform|handle|seguidores|nota|status):\s*(.*)$", l)
        if not m:
            continue
        k, v = m.group(1), m.group(2).strip().strip('"').strip("'")
        if k == "tipo" and atual.get("tipo"):
            if atual.get("handle"):
                fora.append(atual)
            atual = {}
        atual[k] = v
    if atual.get("handle"):
        fora.append(atual)
    return [x for x in fora if x.get("handle") and x.get("handle") != "null"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()

    p = SERIE/"canais.jsonl"
    linhas = [json.loads(l) for l in p.read_text(encoding="utf-8").split("\n") if l.strip()]
    hoje = dt.date.today().isoformat()
    ja = {(x.get("praca_id"), x.get("handle")) for x in linhas if x.get("handle")}

    # 1 · marcar os homônimos
    rejeitados = 0
    for x in linhas:
        k = (x.get("praca_id"), x.get("handle"))
        if k in REJEITAR and not x.get("rejeitado"):
            x["rejeitado"] = True
            x["rejeitado_porque"] = REJEITAR[k]
            x["rejeitado_em"] = hoje
            rejeitados += 1
            print(f"  ✗ {x['praca_id']:14s} @{x['handle']:28s} {REJEITAR[k]}")

    # 2 · promover os que a pesquisa humana já tinha
    novos = []
    def junta(praca, tipo, plat, handle, fonte, nome=None, seg=None, nota=None):
        if (praca, handle) in ja:
            return
        ja.add((praca, handle))
        novos.append({"snapshot_date": hoje, "praca_id": praca, "plataforma": plat,
                      "tipo": tipo, "handle": handle, "nome": nome,
                      "seguidores": int(seg) if str(seg or "").isdigit() else None,
                      "bio": None, "verificado": None,
                      "fonte": fonte, "promovido_em": hoje,
                      "first_seen_snapshot": hoje})

    for praca, tipo, plat, handle, fonte in PROMOVER:
        junta(praca, tipo, plat, handle, fonte)

    for praca, tipo, plat, handle, seg in DA_WEB:
        junta(praca, tipo, plat, handle, "busca na web · ago/2026", seg=seg)

    # Percorre a pasta de IDENTIDADE, não as praças que já têm linha em
    # canais.jsonl. Cuiabá tem zero linhas — era a pior praça da ETAPA 2 — e
    # por isso mesmo nunca entraria num laço que parte do que já existe.
    for praca in sorted(x.stem for x in (RAIZ/"dados"/"identidade").glob("*.json")):
        for c in do_yaml(praca):
            junta(praca, c.get("tipo"), c.get("platform") or "instagram",
                  c["handle"], f"coleta/alvos/{praca}.yaml",
                  seg=c.get("seguidores"), nota=c.get("nota"))

    from collections import Counter
    print(f"\n  {rejeitados} homônimo(s) marcado(s) · {len(novos)} canal(is) promovido(s)")
    for praca, n in sorted(Counter(x["praca_id"] for x in novos).items()):
        print(f"    {praca:20s} +{n}")

    if a.salvar:
        with p.open("w", encoding="utf-8") as f:
            for x in linhas + novos:
                f.write(json.dumps(x, ensure_ascii=False) + "\n")
        print(f"\n  → dados/serie/canais.jsonl  ({len(linhas)+len(novos)} linhas)")
    else:
        print("\n  (nada gravado — rode com --salvar)")


if __name__ == "__main__":
    main()
