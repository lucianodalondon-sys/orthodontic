#!/usr/bin/env python3
"""
canais.py — quem fala com a cidade. Os nove tipos de canal da etapa 2.

Por que existe: esta era a única etapa do coleta/NOVA-PRACA.md que rodava em
script descartável. Ela produziu o achado mais forte sobre território — o canal
da mãe, que decide o aparelho, existe em 1 de 5 praças — e mesmo assim não se
repetia sozinha. Praça nova entrava sem ele.

A armadilha, e ela é grande: a busca do Instagram casa por pedaço de palavra e
devolve o mundo inteiro. Procurar "feira de santana maes" trouxe perfis da
Indonésia; "prudente" trouxe a prefeitura do Rio e o presidente de El Salvador.
Sem o filtro de cidade, metade do levantamento é lixo — e lixo com número
grande parece dado bom.

Por isso o perfil só entra se ele PRÓPRIO se identifica com a cidade, no @, no
nome ou na bio. E o que não aparece é anotado como não_encontrado, porque
canal que falta é território vazio: quem chegar primeiro fala sozinho.

Uso:
    python3 coleta/coletores/canais.py --praca cuiaba
    python3 coleta/coletores/canais.py --todas
    python3 coleta/coletores/canais.py --praca cuiaba --dry-run
"""
import argparse, json, os, pathlib, re, subprocess, sys, time, unicodedata
import datetime as dt

RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent
IDENT = RAIZ/"dados"/"identidade"
SERIE = RAIZ/"dados"/"serie"
BRUTO = RAIZ/"dados"/"bruto"
ACTOR = "apify~instagram-scraper"
API = "https://api.apify.com/v2"

# Os nove tipos, e o que cada um responde. A ordem não é decorativa: o nº 3 e o
# nº 9 são os que decidem, e são os mais esquecidos.
TIPOS = [
 ("voz_da_cidade",   "",                    "como a cidade fala"),
 ("imprensa",        "noticias",            "a notícia e a joia enterrada"),
 ("mae",             "maes",                "É ELA QUEM DECIDE O APARELHO"),
 ("preco_achadinho", "ofertas",             "como a cidade fala de dinheiro"),
 ("humor",           "humor",               "o que viraliza, a língua solta"),
 ("jovem",           "universitario",       "o público de 15-25"),
 ("gastronomia",     "onde comer",          "onde a indicação converte"),
 ("prefeitura",      "prefeitura",          "onde o cidadão reclama e celebra"),
 ("esporte_base",    "futsal escolinha",    "O PÚBLICO DE 9-15 COM OS PAIS JUNTO"),
]
PISO_SEGUIDORES = 2000        # abaixo disso não é canal, é perfil


def sa(s):
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def token():
    t = os.environ.get("APIFY_TOKEN", "").strip()
    if not t:
        env = RAIZ/"_pipeline"/".env"
        if env.exists():
            for l in env.read_text(encoding="utf-8").splitlines():
                l = l.strip().replace("\r", "")
                if l.startswith("APIFY_TOKEN="):
                    t = l.split("=", 1)[1].strip()
    if not t:
        sys.exit("APIFY_TOKEN ausente")
    return t


def curl(u, *a, tent=4):
    """Rede com soluço: resposta vazia não é resposta."""
    for i in range(tent):
        r = subprocess.run(["curl", "-sS", "-m", "120", *a, u], capture_output=True, text=True)
        if r.stdout.strip():
            try:
                return json.loads(r.stdout)
            except Exception:
                return None
        time.sleep(4*(i+1))
    return None


def marcas(cidades):
    """As palavras que provam que o perfil é da praça."""
    m = set()
    for c in cidades:
        nome = sa(c.split("/")[0])
        m.add(nome)
        m.add(nome.replace(" ", ""))
        partes = nome.split()
        if len(partes) > 1:                       # 'feira de santana' -> 'santana'
            m.add(partes[-1])
    return m


# O que um canal de cada tipo PRECISA dizer de si. Sem isso a busca casa por
# pedaço de palavra e entrega qualquer coisa: em Palmas, "maes" casou dentro
# de "maestra" e trouxe uma pizzaria como canal da mãe.
EXIGE = {
 "mae":             ["mae", "maes", "mamae", "materni", "gestante", "gravid", "filho", "familia"],
 "humor":           ["humor", "meme", "comed", "risada", "piada", "engracad"],
 "esporte_base":    ["futsal", "futebol", "esport", "escolinha", "atleta", "sub-", "sub ", "volei"],
 "prefeitura":      ["prefeitura", "oficial", "municip"],
 "imprensa":        ["noticia", "jornal", "informa", "portal", "reporta"],
 "preco_achadinho": ["oferta", "promo", "desconto", "barato", "achadinho", "vitrine", "cupom"],
 "jovem":           ["universi", "faculdade", "estudante", "campus", "festa", "calour"],
 "gastronomia":     ["restaurante", "delivery", "sabor", "comida", "gastronom", "almoc", "pizza"],
}
# Se a bio cita OUTRA cidade ou outro país, não é da praça — foi assim que a
# prefeitura de "Palmas de Monte Alto", da Bahia, entrou como Palmas/TO.
CONFLITO = ["monte alto", "portugal", "italia", "espanha", "argentina", "brasilia df"]
UFS = ["ac", "al", "am", "ap", "ba", "ce", "df", "es", "go", "ma", "mg", "ms", "mt",
       "pa", "pb", "pe", "pi", "pr", "rj", "rn", "ro", "rr", "rs", "sc", "se", "sp", "to"]
# Nome de cidade se repete pelo Brasil: existe Palmas no TO e no PR, e a
# prefeitura de Palmas/PR entrou como se fosse a nossa. A UF desempata.
UF_NO_HANDLE = None


def uf_conflita(blob, uf):
    """O handle ou a bio apontam para OUTRO estado?

    @prefeituradepalmas_pr entrou como Palmas/TO. Existe Palmas no Tocantins e
    no Paraná, e sem checar a UF os dois viram a mesma cidade.
    """
    if not uf:
        return False
    uf = uf.lower()
    for outra in UFS:
        if outra == uf:
            continue
        if re.search(rf"[_\-. ]{outra}\b", blob) or f"-{outra}" in blob or f"/{outra}" in blob:
            return True
    return False


def da_cidade(perfil, marcas_praca, tipo=None, uf=None):
    """O perfil é MESMO da praça, e é MESMO deste tipo?

    Duas checagens, e as duas vieram de erro real em Palmas:
      · 31% dos canais achados eram de outro lugar ou de outro assunto
      · a maior 'voz da cidade' era uma italiana de cosméticos de sobrenome
        Palmas, com 1,8 milhão de seguidores — número grande parece dado bom
    """
    nome = sa(perfil.get("username") or "")
    bio = sa(" ".join([perfil.get("fullName") or "", perfil.get("biography") or ""]))
    blob = nome + " " + bio
    if not any(m in blob for m in marcas_praca if len(m) > 4):
        return False
    if any(c in bio for c in CONFLITO):
        return False
    if uf_conflita(blob, uf):
        return False
    exigidas = EXIGE.get(tipo or "")
    if exigidas and not any(w in blob for w in exigidas):
        return False
    return True


def busca(termo, tok):
    corpo = {"search": termo, "searchType": "user", "searchLimit": 20,
             "resultsType": "details", "resultsLimit": 1}
    d = curl(f"{API}/acts/{ACTOR}/run-sync-get-dataset-items?token={tok}&timeout=300&memory=2048",
             "-X", "POST", "-H", "Content-Type: application/json",
             "-d", json.dumps(corpo, ensure_ascii=False))
    return d if isinstance(d, list) else []


def roda(praca, tok, dry=False):
    ident = json.loads((IDENT/f"{praca}.json").read_text(encoding="utf-8"))
    cidades = ident.get("cidades") or []
    mk = marcas(cidades)
    principal = cidades[0].split("/")[0] if cidades else praca
    uf = (cidades[0].split("/") + [""])[1] if cidades else ""
    hoje = dt.date.today().isoformat()

    rot = ident.get("rotulo") or ident.get("nome", praca)
    print(f"\n{'='*72}\n  CANAIS · {rot}\n{'='*72}")
    achados, vazios, bruto = {}, [], []
    for tipo, sufixo, oque in TIPOS:
        termo = f"{principal} {sufixo}".strip()
        if dry:
            print(f"  [dry] {tipo:16s} busca '{termo}'")
            continue
        res = busca(termo, tok)
        bruto += [{**r, "_tipo": tipo, "_termo": termo} for r in res]
        cand = [r for r in res if r.get("username") and da_cidade(r, mk, tipo, uf)
                and (r.get("followersCount") or 0) >= PISO_SEGUIDORES]
        cand.sort(key=lambda x: -(x.get("followersCount") or 0))
        if not cand:
            vazios.append(tipo)
            print(f"  {tipo:16s} NÃO ENCONTRADO  ← território vazio, ver abaixo")
            continue
        for c in cand[:2]:
            u = c["username"]
            if u not in achados or achados[u]["tipo"] == "voz_da_cidade":
                achados[u] = {"tipo": tipo, "perfil": c}
        top = cand[0]
        print(f"  {tipo:16s} @{top['username'][:26]:26s} {top.get('followersCount'):>8} · {oque}")

    if dry:
        return
    if vazios:
        print(f"\n  OS QUE NÃO EXISTEM ({len(vazios)}): {', '.join(vazios)}")
        print("  Isso não é falha da busca — é território vazio. Quem chegar")
        print("  primeiro fala sozinho. E se 'mae' está na lista, é a maior")
        print("  brecha possível: é ela quem decide o aparelho.")
        print("  ⚠ ANTES DE CONCLUIR: uma busca por nome não é a única forma de")
        print("    achar uma influenciadora. Confirme à mão.")

    d = BRUTO/praca/"canais"/hoje
    d.mkdir(parents=True, exist_ok=True)
    (d/"busca.json").write_text(json.dumps(bruto, ensure_ascii=False), encoding="utf-8")
    with (SERIE/"canais.jsonl").open("a", encoding="utf-8") as f:
        for u, a in achados.items():
            p = a["perfil"]
            f.write(json.dumps({
                "snapshot_date": hoje, "praca_id": praca, "plataforma": "instagram",
                "tipo": a["tipo"], "handle": u, "nome": p.get("fullName"),
                "seguidores": p.get("followersCount"), "posts": p.get("postsCount"),
                "bio": (p.get("biography") or "")[:300], "verificado": p.get("verified"),
                "fonte": f"apify {ACTOR}", "filtro": "searchType=user + filtro de cidade",
                "first_seen_snapshot": hoje}, ensure_ascii=False)+"\n")
        for tipo in vazios:
            f.write(json.dumps({
                "snapshot_date": hoje, "praca_id": praca, "plataforma": "instagram",
                "tipo": tipo, "handle": None, "status": "nao_encontrado",
                "nota": "a busca não achou; precisa de conferência humana antes de virar conclusão",
                "fonte": f"apify {ACTOR}", "first_seen_snapshot": hoje}, ensure_ascii=False)+"\n")
    print(f"\n  canais.jsonl +{len(achados)} canais e +{len(vazios)} vazios declarados")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--praca")
    ap.add_argument("--todas", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    pracas = ([p.stem for p in sorted(IDENT.glob("*.json"))] if a.todas
              else [a.praca] if a.praca else None)
    if not pracas:
        sys.exit("use --praca <id> ou --todas")
    tok = "" if a.dry_run else token()
    for p in pracas:
        roda(p, tok, a.dry_run)
    print()


if __name__ == "__main__":
    main()
