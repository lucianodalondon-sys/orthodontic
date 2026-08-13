#!/usr/bin/env python3
"""
google_places.py — varredura da categoria numa praça, pela Places API (New).

Por que existe, se já temos o coletor da Apify:
  · a Apify cobra por lugar e é lenta; a Places API é barata e responde em
    segundos, então dá para varrer a categoria INTEIRA em vez de conferir
    uma lista escolhida a mão.
  · as quatro primeiras praças foram montadas com 4 a 6 concorrentes cada,
    escolhidos por quem estava olhando. Isso é amostra de conveniência: o
    concorrente que ninguém lembrou de incluir nunca aparece no placar.
  · Cuiabá foi varrida e deu 15 clínicas — e o segundo colocado da praça
    (REDEORTO) não estava em nenhuma lista feita à mão.

O que ele NÃO faz: avaliação com data. A Places API devolve no máximo 5
avaliações por lugar, o que não dá para calcular ritmo. Ritmo continua vindo
do coletor da Apify. Este aqui responde "quem existe", aquele responde
"quem está correndo".

Precisa de: Places API (New) habilitada no projeto e GOOGLE_API_KEY no
_pipeline/.env.

Uso:
    python3 coleta/coletores/google_places.py --praca cuiaba
    python3 coleta/coletores/google_places.py --todas
    python3 coleta/coletores/google_places.py --praca feira --dry-run
"""
import argparse, json, os, pathlib, re, subprocess, sys
import datetime as dt

RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent
IDENT = RAIZ/"dados"/"identidade"
SERIE = RAIZ/"dados"/"serie"
BRUTO = RAIZ/"dados"/"bruto"
API = "https://places.googleapis.com/v1/places:searchText"

# As buscas. Uma praça é varrida por vários ângulos porque o Google
# devolve conjuntos diferentes para termos diferentes — quem busca só
# "ortodontia" perde a clínica que se cadastrou como "clínica odontológica".
TERMOS = ["ortodontia", "aparelho ortodôntico", "clínica odontológica",
          "dentista", "ortodontista", "alinhador invisível"]

CAMPOS = ("places.id,places.displayName,places.rating,places.userRatingCount,"
          "places.formattedAddress,places.primaryTypeDisplayName,places.types,"
          "places.businessStatus,places.websiteUri,places.nationalPhoneNumber,"
          "places.location,nextPageToken")


def chave():
    k = os.environ.get("GOOGLE_API_KEY", "").strip()
    if not k:
        env = RAIZ/"_pipeline"/".env"
        if env.exists():
            for l in env.read_text(encoding="utf-8").split("\n"):
                l = l.strip().replace("\r", "")
                if l.startswith("GOOGLE_API_KEY="):
                    k = l.split("=", 1)[1].strip()
    if not k:
        sys.exit("GOOGLE_API_KEY ausente em _pipeline/.env")
    return k


def busca(texto, key, page=None):
    corpo = {"textQuery": texto, "languageCode": "pt-BR", "maxResultCount": 20}
    if page:
        corpo["pageToken"] = page
    r = subprocess.run(["curl", "-sS", "-m", "40", "-X", "POST", API,
                        "-H", "Content-Type: application/json",
                        "-H", f"X-Goog-Api-Key: {key}",
                        "-H", f"X-Goog-FieldMask: {CAMPOS}",
                        "-d", json.dumps(corpo, ensure_ascii=False)],
                       capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
    except Exception:
        return [], None, (r.stdout or r.stderr)[:140]
    if "error" in d:
        return [], None, d["error"].get("message", "")[:140]
    return d.get("places", []), d.get("nextPageToken"), None


def e_odonto(p):
    """Filtra o que a busca traz de sobra: farmácia, hospital geral, laboratório."""
    t = set(p.get("types") or [])
    nome = (p.get("displayName", {}).get("text") or "").lower()
    if t & {"dentist", "dental_clinic"}:
        return True
    return any(w in nome for w in ("odonto", "dental", "ortod", "dentist", "sorri"))


def sem_acento(s):
    import unicodedata
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def na_praca(p, cidades):
    """O Google casa nome parecido de outro estado: buscar 'Várzea Grande'
    trouxe uma unidade de 'Várzea Paulista/SP' para dentro de Cuiabá. Sem
    este filtro o placar da praça sai contaminado — e foi por pouco que
    isso não virou 'a rede tem quatro unidades em Cuiabá'.

    Casa pela ÚLTIMA palavra do nome da cidade mais a UF, porque o Google
    abrevia: 'Presidente Prudente' vira 'Pres. Prudente'. Exigir o nome
    inteiro zerou a praça de Prudente sem avisar.
    """
    end = sem_acento(p.get("formattedAddress"))
    for c in cidades:
        nome, uf = (c.split("/") + [""])[:2]
        chave = sem_acento(nome).split()[-1]          # prudente · grande · mafra
        uf = sem_acento(uf).strip()
        if chave in end and (not uf or re.search(rf"[-,]\s*{uf}\b", end)):
            return True
    return False


def varre(praca, key, dry=False):
    ident = json.loads((IDENT/f"{praca}.json").read_text(encoding="utf-8"))
    cidades = ident.get("cidades") or []
    achados, erros = {}, []
    for cidade in cidades:
        for termo in TERMOS:
            pagina, voltas = None, 0
            while voltas < 3:                      # 3 páginas = até 60 por termo
                lst, pagina, err = busca(f"{termo} {cidade}", key, pagina)
                if err:
                    erros.append(f"{termo} {cidade}: {err}"); break
                for p in lst:
                    if not e_odonto(p) or not na_praca(p, cidades):
                        continue
                    pid = p.get("id")
                    if pid and pid not in achados:
                        p["_cidade_busca"] = cidade
                        achados[pid] = p
                voltas += 1
                if not pagina:
                    break
    return ident, list(achados.values()), erros


def ancora(praca, achados, quantos=14):
    """Escreve as maiores clínicas na identidade da praça.

    Era o elo que faltava: a varredura enchia categoria.jsonl e a identidade
    continuava vazia, então o coletor de avaliação devolvia zero locais. Em
    Palmas isso foi feito por script solto — praça nova ficaria sem.

    A unidade da rede entra como 'proprio' e é reconhecida pelo nome. O resto
    entra como concorrente com o tipo em branco, porque tipar é humano.
    """
    import re, unicodedata
    arq = IDENT/f"{praca}.json"
    ident = json.loads(arq.read_text(encoding="utf-8"))
    ja = {l.get("place_id") for l in ident.get("locais", []) if l.get("place_id")}
    ordenados = sorted(achados, key=lambda p: -(p.get("userRatingCount") or 0))
    hoje = dt.date.today().isoformat()

    def bairro_do_endereco(e):
        """O bairro é o último trecho antes de ', Cidade - UF'."""
        partes = [x.strip() for x in str(e or "").split(",")]
        for i, x in enumerate(partes):
            if re.fullmatch(r".+ - [A-Z]{2}", x) and i > 0:
                b = partes[i-1].split(" - ")[-1].strip()
                return b if len(b) >= 3 and not re.fullmatch(r"[\d\s\-]+", b) else ""
        return ""

    def id_unico(nome, endereco, place_id, ident, praca):
        """UM ID POR LOJA, SEMPRE — e nunca o nome truncado.

        Toda unidade da rede se chama "OrthoDontic". Com o id saindo do
        nome, as 7 de Porto Alegre viraram `orthodontic` e a coleta de
        avaliações mediu UMA — 152 avaliações onde deviam ser sete lojas.
        É a mesma armadilha que já fundiu ODONTOMAX, Vamos Sorrir,
        DENTEBRAS e Odonto Minas, e o guarda de `cruzamento.identidades()`
        existe justamente para gritar quando ela volta.

        A ordem de desempate: nome, depois BAIRRO (que é o que distingue
        duas lojas da mesma marca na mesma cidade e é legível para quem
        lê a tela), e por último um pedaço do place_id, que é único por
        definição.
        """
        usados = {l.get("local_id") for l in ident.get("locais", [])}
        base = slug(nome) or f"local_{len(ident.get('locais', []))}"
        if base not in usados:
            return base
        b = slug(bairro_do_endereco(endereco))
        if b and f"{base}_{b}"[:40] not in usados:
            return f"{base}_{b}"[:40]
        return f"{base}_{slug(place_id)[-6:]}"[:40]

    def slug(s):
        s = unicodedata.normalize("NFKD", s or "")
        s = "".join(c for c in s if not unicodedata.combining(c)).lower()
        return re.sub(r"[^a-z0-9]+", "_", s).strip("_")[:26]

    # DUAS PROVAS, E O NOME EXATO BASTA.
    #
    # A regra antiga era: site igual ao nacional = nossa; site diferente =
    # NÃO É NOSSA. Ela nasceu certa — "You Align Orthodontics", em Contagem,
    # tinha entrado como unidade da rede. Mas produziu falso NEGATIVO em
    # Florianópolis: as três lojas de lá usam `orthodonticsc.com.br`, um
    # site regional da própria rede, e as três foram descartadas. A praça
    # ficou com zero unidades enquanto a lista oficial dizia três.
    #
    # O nome exato já resolve o falso positivo que motivou a regra:
    # `\borthodontic\b` NÃO casa com "Orthodontics" (o 's' encosta na
    # borda de palavra) nem com "Ortho Mais". Então o nome basta, e o
    # domínio nacional entra como prova adicional, não como veto.
    def e_da_rede(p):
        site = (p.get("websiteUri") or "").lower()
        if "orthodonticbrasil.com.br" in site:
            return True
        nome = (p.get("displayName", {}).get("text") or "").lower()
        return re.search(r"\borthodontic\b", nome) is not None

    nossos = [p for p in ordenados if e_da_rede(p)]
    outros = [p for p in ordenados if p not in nossos][:quantos]
    novos = 0
    for p in nossos + outros:
        pid = p.get("id")
        if not pid or pid in ja:
            continue
        nome = p.get("displayName", {}).get("text") or ""
        eh_nosso = p in nossos
        # a unidade sem place_id que o esqueleto criou recebe o dela
        vazio = next((l for l in ident["locais"]
                      if l.get("papel") == "proprio" and not l.get("place_id")), None)
        alvo = vazio if (eh_nosso and vazio) else None
        dados = {"place_id": pid, "nome": nome,
                 "location": ({"lat": (p.get("location") or {}).get("latitude"),
                               "lng": (p.get("location") or {}).get("longitude")}
                              if (p.get("location") or {}).get("latitude") is not None
                              else None),
                 "avaliacoes_google": p.get("userRatingCount"),
                 "nota_google": p.get("rating"),
                 "endereco": p.get("formattedAddress"),
                 "place_id_origem": f"varredura google places {hoje}"}
        if alvo:
            alvo.update(dados); alvo.pop("chave_pendente", None)
        else:
            ident["locais"].append({
                "local_id": id_unico(nome, p.get("formattedAddress"), pid,
                                     ident, praca),
                "papel": "proprio" if eh_nosso else "concorrente",
                **({"tipo": "franquia"} if eh_nosso else {"tipo_concorrente": "PREENCHER"}),
                **dados, "descoberto_em": hoje})
        ja.add(pid); novos += 1
    arq.write_text(json.dumps(ident, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return novos, sum(1 for l in ident["locais"] if l.get("papel") == "proprio")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--praca")
    ap.add_argument("--todas", action="store_true")
    ap.add_argument("--sem-ancorar", action="store_true",
                    help="só varre, não escreve na identidade")
    ap.add_argument("--dry-run", action="store_true", help="mostra e não grava")
    a = ap.parse_args()
    pracas = ([p.stem for p in sorted(IDENT.glob("*.json"))] if a.todas
              else [a.praca] if a.praca else None)
    if not pracas:
        sys.exit("use --praca <id> ou --todas")
    key = chave()
    hoje = dt.date.today().isoformat()

    for praca in pracas:
        ident, achados, erros = varre(praca, key, a.dry_run)
        conhecidos = {l.get("place_id") for l in ident["locais"] if l.get("place_id")}
        achados.sort(key=lambda p: -(p.get("userRatingCount") or 0))
        novos = [p for p in achados if p.get("id") not in conhecidos]

        rot = ident.get("rotulo") or ident.get("nome", praca)
        print(f"\n{'='*72}\n  {rot} · {len(achados)} clínicas · "
              f"{len(novos)} NÃO estavam na nossa lista\n{'='*72}")
        for p in achados[:26]:
            marca = "NOVO" if p.get("id") not in conhecidos else "    "
            fech = " [FECHADA]" if p.get("businessStatus") != "OPERATIONAL" else ""
            print(f"  {marca} {(p.get('userRatingCount') or 0):>5d} "
                  f"{str(p.get('rating') or '?'):>4s}  "
                  f"{(p.get('displayName', {}).get('text') or '')[:40]:40s}"
                  f"{(p.get('primaryTypeDisplayName', {}).get('text') or '')[:16]}{fech}")
        for e in erros[:4]:
            print(f"  ! {e}")

        if a.dry_run:
            continue
        d = BRUTO/praca/"google_places"/hoje
        d.mkdir(parents=True, exist_ok=True)
        (d/"varredura.json").write_text(json.dumps(achados, ensure_ascii=False), encoding="utf-8")
        with (SERIE/"categoria.jsonl").open("a", encoding="utf-8") as f:
            for p in achados:
                f.write(json.dumps({
                    "snapshot_date": hoje, "praca_id": praca, "place_id": p.get("id"),
                    "nome": p.get("displayName", {}).get("text"),
                    "nota": p.get("rating"), "avaliacoes": p.get("userRatingCount"),
                    "tipo": (p.get("primaryTypeDisplayName") or {}).get("text"),
                    "endereco": p.get("formattedAddress"), "site": p.get("websiteUri"),
                    "telefone": p.get("nationalPhoneNumber"),
                    "situacao": p.get("businessStatus"),
                    # A COORDENADA JÁ ERA PAGA E ERA JOGADA FORA. O
                    # FieldMask pede `places.location` desde sempre, o bruto
                    # guardava as 3.304, e categoria.jsonl gravava zero. Sem
                    # ela não há distância, não há vizinhança real, não há
                    # grade de busca — e a conta do Google já tinha sido paga.
                    "location": ({"lat": (p.get("location") or {}).get("latitude"),
                                  "lng": (p.get("location") or {}).get("longitude")}
                                 if (p.get("location") or {}).get("latitude") is not None
                                 else None),
                    "na_nossa_lista": p.get("id") in conhecidos,
                    "fonte": "google places api (new) searchText",
                    "filtro": "|".join(TERMOS), "first_seen_snapshot": hoje},
                    ensure_ascii=False)+"\n")
        print(f"  → categoria.jsonl +{len(achados)}")
        if not a.sem_ancorar:
            n, prop = ancora(praca, achados)
            print(f"  → identidade +{n} locais ({prop} da rede) — pronta para o coletor de avaliação")
    print()


if __name__ == "__main__":
    main()
