#!/usr/bin/env python3
"""
rede_inteira.py — a ficha pública das 374 unidades, não das 10 medidas.

Por que existe
--------------
Toda tela do portal fala de 10 unidades. A rede tem 374. Essa é a crítica mais
dura que o produto recebeu, e ela é justa: "uma fila que ignora 97,3% da rede
não prioriza a rede".

A varredura completa de uma praça — avaliação com texto, concorrência, portas,
canais — é cara e depende de Apify, que hoje está sem cota. Mas a CAMADA
BARATA não depende disso: nota, volume de avaliações, categoria declarada,
telefone, site e situação saem da API do Google Places, uma chamada por
unidade. Não dá a voz do paciente. Dá o placar da rede inteira.

Com isso, "3 de 10 sustentam" vira uma frase sobre a rede, e a auditoria de
ficha deixa de conferir 10 cadastros para conferir 374.

O que ele NÃO faz
-----------------
Não lê avaliação. Não classifica tema. Não mede ritmo — para ritmo é preciso a
data de cada avaliação, e isso é a varredura cara. Aqui é foto: como a unidade
aparece hoje para quem procura.

A armadilha, e ela é a de sempre
--------------------------------
Buscar "OrthoDontic <cidade>" no Google devolve QUALQUER clínica com nome
parecido, em qualquer cidade. Três travas:

  1. a busca leva cidade E estado, sempre
  2. o resultado só entra se o nome, sem espaço e sem acento, contiver
     "orthodontic" — "Clínica Ortho Mais" não é nossa
  3. o endereço devolvido precisa bater com a cidade procurada

Unidade que não passa nas três sai como `nao_confirmada`, com o motivo. É
melhor devolver 300 confirmadas e 74 em aberto do que 374 com lixo dentro.

Uso:
    python3 coleta/coletores/rede_inteira.py --piloto 10
    python3 coleta/coletores/rede_inteira.py --todas --salvar
"""
import argparse, json, os, pathlib, re, subprocess, sys, time, unicodedata
import datetime as dt

RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent
SERIE = RAIZ/"dados"/"serie"
BRUTO = RAIZ/"dados"/"bruto"/"_rede"

CAMPOS = ("places.id,places.displayName,places.formattedAddress,"
          "places.rating,places.userRatingCount,places.primaryTypeDisplayName,"
          "places.nationalPhoneNumber,places.websiteUri,places.businessStatus,"
          "places.googleMapsUri")


def chave():
    k = os.environ.get("GOOGLE_API_KEY", "").strip()
    if not k:
        env = RAIZ/"_pipeline"/".env"
        if env.exists():
            for l in env.read_text(encoding="utf-8").split("\n"):
                if l.strip().startswith("GOOGLE_API_KEY="):
                    k = l.split("=", 1)[1].strip()
    if not k:
        sys.exit("GOOGLE_API_KEY ausente")
    return k


def sa(s):
    return "".join(c for c in unicodedata.normalize("NFD", s or "")
                   if unicodedata.category(c) != "Mn").lower()


def nossa(nome):
    """'Clínica Ortho Mais' NÃO é nossa. 'OrthoDontic Centro' é.

    'ortho' solto casa com meia dúzia de concorrentes; a palavra inteira,
    sem espaço e sem acento, é o que identifica a marca."""
    return "orthodontic" in re.sub(r"[^a-z]", "", sa(nome))


def busca(texto, k):
    r = subprocess.run(
        ["curl", "-sS", "-m", "40", "https://places.googleapis.com/v1/places:searchText",
         "-H", f"X-Goog-Api-Key: {k}", "-H", f"X-Goog-FieldMask: {CAMPOS}",
         "-H", "Content-Type: application/json",
         "-d", json.dumps({"textQuery": texto, "languageCode": "pt-BR",
                           "regionCode": "BR", "maxResultCount": 5})],
        capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {}


def unidades():
    p = SERIE/"unidades_rede.jsonl"
    linhas = [json.loads(l) for l in p.read_text(encoding="utf-8").split("\n") if l.strip()]
    ult = max(x["snapshot_date"] for x in linhas)
    return [x for x in linhas if x["snapshot_date"] == ult]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--piloto", type=int, help="roda só N unidades, para conferir")
    ap.add_argument("--todas", action="store_true")
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()

    us = unidades()
    if a.piloto:
        # amostra espalhada, não as N primeiras: as primeiras são todas do
        # mesmo estado e não testam a variedade de nome e endereço.
        passo = max(len(us)//a.piloto, 1)
        us = us[::passo][:a.piloto]
    elif not a.todas:
        sys.exit("use --piloto N ou --todas")

    k = chave()
    hoje = dt.date.today().isoformat()
    fora, conf, nao = [], 0, 0
    print(f"\n  {len(us)} unidade(s) · corte {hoje}\n")

    for i, u in enumerate(us, 1):
        # O campo `cidade` da lista oficial já vem com a UF colada:
        # "Londrina/PR". Procurar essa string inteira dentro de um endereço
        # escrito "Londrina - PR" nunca casa, e a primeira rodada devolveu
        # 0 de 12 confirmadas — todas com o motivo errado, dizendo "fica em
        # outra cidade" sobre a cidade certa.
        cidade = (u.get("cidade") or "").split("/")[0].strip()
        uf = (u.get("uf") or "").upper()
        # Cidade com mais de uma unidade devolvia a MESMA ficha para todas —
        # Campinas e Londrina têm duas, e as duas linhas saíam idênticas. O
        # nome da unidade na lista oficial ("Londrina - Souza Naves") carrega
        # o bairro ou a rua, e é ele que desempata.
        nome_un = (u.get("unidade") or "")
        sufixo = ""
        if " - " in nome_un:
            sufixo = " " + nome_un.split(" - ", 1)[1].strip()
        elif sa(nome_un).replace(sa(cidade), "").strip():
            sufixo = " " + nome_un.strip()
        q = f"OrthoDontic{sufixo} {cidade} {uf}".replace("  ", " ")
        d = busca(q, k)
        achou = None
        motivo = "nenhum resultado do Google"
        for pl in (d.get("places") or []):
            nome = (pl.get("displayName") or {}).get("text") or ""
            end = pl.get("formattedAddress") or ""
            if not nossa(nome):
                motivo = f"o topo é '{nome[:40]}', que não é da marca"
                continue
            # compara sem acento e sem pontuação: "Ji-Parana" contra
            # "Ji-Paraná", "Guaiba" contra "Guaíba"
            import re as _re
            limpo = lambda t: _re.sub(r"[^a-z ]", " ", sa(t))
            if limpo(cidade) not in limpo(end):
                motivo = f"'{nome[:30]}' fica em outra cidade: {end[:50]}"
                continue
            achou = pl
            break

        linha = {"snapshot_date": hoje, "escopo": "rede_inteira",
                 "cidade": cidade, "uf": uf,
                 "unidade_na_lista": u.get("unidade"),
                 "situacao_na_lista": u.get("situacao"),
                 "consulta": q, "fonte": "google places · searchText"}
        if achou:
            conf += 1
            linha.update({
                "confirmada": True,
                "place_id": achou.get("id"),
                "nome": (achou.get("displayName") or {}).get("text"),
                "endereco": achou.get("formattedAddress"),
                "nota": achou.get("rating"),
                "avaliacoes": achou.get("userRatingCount"),
                "tipo": achou.get("primaryTypeDisplayName", {}).get("text")
                        if isinstance(achou.get("primaryTypeDisplayName"), dict)
                        else achou.get("primaryTypeDisplayName"),
                "telefone": achou.get("nationalPhoneNumber"),
                "site": achou.get("websiteUri"),
                "situacao_google": achou.get("businessStatus"),
                "mapa": achou.get("googleMapsUri"),
            })
            print(f"  {i:>3d}/{len(us)} ✓ {cidade[:22]:22s}/{uf} "
                  f"nota {str(achou.get('rating')):>3s} · "
                  f"{str(achou.get('userRatingCount')):>5s} aval · "
                  f"{linha['tipo']}")
        else:
            nao += 1
            linha.update({"confirmada": False, "nao_confirmada_porque": motivo})
            print(f"  {i:>3d}/{len(us)} ✗ {cidade[:22]:22s}/{uf} {motivo[:56]}")
        # duas unidades da mesma cidade não podem apontar para a mesma ficha
        if achou:
            gemeo = next((x for x in fora if x.get("place_id") == achou.get("id")), None)
            if gemeo:
                linha["confirmada"] = False
                linha["nao_confirmada_porque"] = (
                    f"a busca devolveu a MESMA ficha de '{gemeo.get('unidade_na_lista')}'"
                    f" — cidade com mais de uma unidade e nomes que não desempatam")
                linha.pop("place_id", None)
                conf -= 1
                nao += 1
                print(f"        ↑ desfeita: mesma ficha da unidade anterior")
        fora.append(linha)
        time.sleep(0.12)

    print(f"\n  {conf} confirmadas · {nao} não confirmadas "
          f"({100*conf//max(len(us),1)}%)")

    if a.salvar:
        p = SERIE/"rede_fichas.jsonl"
        antigas = []
        if p.exists():
            antigas = [json.loads(l) for l in p.read_text(encoding="utf-8").split("\n")
                       if l.strip() and json.loads(l).get("snapshot_date") != hoje]
        with p.open("w", encoding="utf-8") as f:
            for x in antigas + fora:
                f.write(json.dumps(x, ensure_ascii=False) + "\n")
        print(f"  → dados/serie/rede_fichas.jsonl ({len(antigas)+len(fora)} linhas)")
        BRUTO.mkdir(parents=True, exist_ok=True)
        (BRUTO/f"{hoje}.json").write_text(json.dumps(fora, ensure_ascii=False, indent=1),
                                          encoding="utf-8")


if __name__ == "__main__":
    main()
