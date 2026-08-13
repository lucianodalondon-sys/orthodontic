#!/usr/bin/env python3
"""
perto_da_loja.py — a loja aparece para quem busca PERTO DELA?

POR QUE ISTO EXISTE. `portas.py` mede a cidade inteira a partir de um ponto
só: manda a frase com o nome do município e vê quem o mapa devolve. Isso
responde bem em Mafra, e responde MAL em São Paulo — as quatro unidades da
capital aparecem em 0 de 193 buscas, e nenhuma conclusão útil sai disso.
Numa cidade de 12 milhões, ninguém disputa "dentista São Paulo": o paciente
busca de onde está, e o mapa responde de onde ele está.

A pergunta honesta para a loja de metrópole é outra:

    QUANDO ALGUÉM BUSCA APARELHO A POUCOS QUARTEIRÕES DA CLÍNICA,
    O GOOGLE MOSTRA A CLÍNICA?

Essa pergunta só ficou possível porque a coordenada de cada unidade já
estava paga e no disco (`backfill_coordenadas.py` recuperou 3.304 sem uma
chamada nova). O `locationBias` da busca de lugares aceita um círculo; o
centro é a própria loja.

O QUE ISTO NÃO É, E PRECISA ESTAR DITO

· NÃO é volume de busca. Continua sem dizer quantas pessoas digitam a
  frase — o autocompletar prova que a frase existe, não que ela é procurada.
· NÃO é a página de resultados nem o anúncio. É o MAPA.
· NÃO é área de captação. Um círculo de 3 km no papel não é 3 km de
  deslocamento real: rio, morro e avenida sem travessia mudam tudo.
  DISTÂNCIA GEOGRÁFICA NÃO É TEMPO DE DESLOCAMENTO.
· NÃO diz que o vizinho no topo rouba paciente. Aparecer antes é aparecer
  antes; canibalização é outra afirmação, e ela não está medida aqui.
· O viés é uma DICA para o Google, não uma ordem. Ele pode devolver
  resultado de fora do círculo, e devolve. Por isso a distância de cada
  resultado ao centro vai gravada — quando dá para calcular.

CUSTO. Cada consulta é uma chamada paga de Places Text Search (US$ 0,032 na
faixa usada pelo projeto). O script IMPRIME a conta antes e só gasta com
`--executar`. Sem a flag ele não chama a API nenhuma vez.

Uso:
    python3 coleta/coletores/perto_da_loja.py --praca sao_paulo
    python3 coleta/coletores/perto_da_loja.py --praca sao_paulo --executar --salvar
    python3 coleta/coletores/perto_da_loja.py --todas --frases 4 --raio 2000
"""
import argparse, json, math, os, pathlib, re, subprocess, sys, time, unicodedata
import datetime as dt

RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent
IDENT = RAIZ/"dados"/"identidade"
SERIE = RAIZ/"dados"/"serie"
BRUTO = RAIZ/"dados"/"bruto"
API = "https://places.googleapis.com/v1/places:searchText"
CAMPOS = ("places.id,places.displayName,places.userRatingCount,places.rating,"
          "places.formattedAddress,places.location")
CUSTO_POR_CONSULTA = 0.032
RAIO_PADRAO = 3000        # metros — bairro e vizinhos, não a cidade

# As frases valem por serem de APARELHO. "clínica odontológica" e
# "implante" trazem outra decisão, outro ticket, outro paciente — a régua
# do produto vale aqui igual: odontologia não é ortodontia.
#
# `dentista` fica DENTRO de propósito: é PORTA, não concorrente. Quem
# digita "dentista perto de mim" é exatamente quem marca a avaliação e sai
# com aparelho — e é a frase mais digitada das que temos.
DE_APARELHO = re.compile(
    r"aparelho|ortodont|braquete|bracket|alinhador|contencao|dentista", re.I)
# ... mas frase de manutenção/urgência não mede captação nova
FORA = re.compile(r"manutencao|quebrou|urgencia|24 ?horas|plantao", re.I)


def sem_acento(s):
    s = unicodedata.normalize("NFKD", str(s or ""))
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def chave():
    k = os.environ.get("GOOGLE_API_KEY", "").strip()
    if not k:
        env = RAIZ/"_pipeline"/".env"
        if env.exists():
            for l in env.read_text(encoding="utf-8").split("\n"):
                if l.strip().startswith("GOOGLE_API_KEY="):
                    k = l.split("=", 1)[1].strip().replace("\r", "")
    return k


def metros(a, b):
    """Haversine em metros. Serve para dizer a que distância do centro o
    Google devolveu cada resultado — e só para isso."""
    if not a or not b:
        return None
    R = 6371000.0
    p1, p2 = math.radians(a["lat"]), math.radians(b["lat"])
    dp = p2 - p1
    dl = math.radians(b["lng"] - a["lng"])
    h = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return round(2*R*math.asin(math.sqrt(h)))


def frases_da_praca(praca_id, quantas):
    """As frases que a PRÓPRIA cidade digita, da última medição dela.

    É sempre a última medição DESTA praça, nunca a última data do arquivo:
    cortar pela data global apaga quem não foi medido hoje — armadilha já
    paga em `onde_cada_loja_aparece`.
    """
    p = SERIE/"portas.jsonl"
    if not p.exists():
        return []
    linhas = [json.loads(l) for l in p.read_text(encoding="utf-8").split("\n")
              if l.strip()]
    minhas = [r for r in linhas if r.get("praca_id") == praca_id]
    if not minhas:
        return []
    corte = max(r["snapshot_date"] for r in minhas)
    vistas, fora = set(), []
    for r in minhas:
        if r["snapshot_date"] != corte:
            continue
        f = (r.get("frase") or "").strip()
        s = sem_acento(f)
        if not f or s in vistas:
            continue
        if not DE_APARELHO.search(s) or FORA.search(s):
            continue
        vistas.add(s)
        fora.append({"frase": f, "intencao": r.get("intencao")})
    # a ordem do arquivo já é a do autocompletar, que é a da própria cidade
    return fora[:quantas]


def busca(frase, centro, raio, key):
    corpo = {
        "textQuery": frase, "languageCode": "pt-BR", "maxResultCount": 10,
        # DICA, não ordem: o Google pode devolver de fora do círculo.
        "locationBias": {"circle": {
            "center": {"latitude": centro["lat"], "longitude": centro["lng"]},
            "radius": float(raio)}},
    }
    r = subprocess.run(["curl", "-sS", "-m", "40", "-X", "POST", API,
                        "-H", "Content-Type: application/json",
                        "-H", f"X-Goog-Api-Key: {key}",
                        "-H", f"X-Goog-FieldMask: {CAMPOS}",
                        "-d", json.dumps(corpo, ensure_ascii=False)],
                       capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
    except Exception:
        return None, "resposta ilegível"
    if "error" in d:
        return None, str(d["error"].get("message"))[:90]
    return d.get("places", []), None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--praca")
    ap.add_argument("--todas", action="store_true")
    ap.add_argument("--frases", type=int, default=5,
                    help="quantas frases por loja (padrão 5)")
    ap.add_argument("--raio", type=int, default=RAIO_PADRAO,
                    help="raio do viés, em metros (padrão 3000)")
    ap.add_argument("--executar", action="store_true",
                    help="sem isto, nenhuma chamada paga é feita")
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()

    alvos = []
    arqs = sorted(IDENT.glob("*.json")) if a.todas else [IDENT/f"{a.praca}.json"]
    for arq in arqs:
        if not arq.exists():
            print(f"  ⚠ {arq.name}: não existe")
            continue
        d = json.loads(arq.read_text(encoding="utf-8"))
        pid = d.get("praca_id") or arq.stem
        proprios = [l for l in d.get("locais", []) if l.get("papel") == "proprio"]
        if not proprios:
            continue        # praça de oportunidade não tem loja para medir
        frases = frases_da_praca(pid, a.frases)
        if not frases:
            print(f"  ⚠ {d.get('rotulo') or pid}: sem portas medidas — "
                  f"rode portas.py antes")
            continue
        for l in proprios:
            loc = l.get("location")
            if not loc:
                print(f"  ⚠ {l['local_id']}: sem coordenada — fica de fora")
                continue
            alvos.append({"praca_id": pid, "rotulo": d.get("rotulo"),
                          "local": l, "centro": loc, "frases": frases})

    consultas = sum(len(x["frases"]) for x in alvos)
    pracas = sorted({x["praca_id"] for x in alvos})
    print(f"\n  A CONTA, ANTES DE GASTAR")
    print(f"    praças .............. {len(pracas)}  ({', '.join(pracas)})")
    print(f"    lojas (pontos) ...... {len(alvos)}")
    print(f"    frases por loja ..... {a.frases}")
    print(f"    raio do viés ........ {a.raio} m")
    print(f"    consultas ........... {consultas}")
    print(f"    custo estimado ...... US$ {consultas*CUSTO_POR_CONSULTA:.2f}"
          f"  (US$ {CUSTO_POR_CONSULTA:.3f} por consulta)")
    if not a.executar:
        print("\n  (nenhuma chamada foi feita — --executar para gastar)\n")
        return
    key = chave()
    if not key:
        print("\n  ⚠ sem GOOGLE_API_KEY — nada foi medido\n")
        return

    hoje = dt.date.today().isoformat()
    linhas, brutos = [], {}
    for x in alvos:
        l, centro = x["local"], x["centro"]
        nome = l.get("unidade") or l.get("nome") or l["local_id"]
        print(f"\n  ── {x['rotulo']} · {nome[:38]}  ({centro['lat']:.4f}, "
              f"{centro['lng']:.4f})")
        for fr in x["frases"]:
            achados, erro = busca(fr["frase"], centro, a.raio, key)
            time.sleep(0.4)
            if achados is None:
                print(f"       ⚠  {fr['frase'][:44]:44s} {erro}")
                continue
            pos, quem = None, []
            for i, p in enumerate(achados[:10], 1):
                pl = p.get("location") or {}
                q = {"posicao": i,
                     "nome": (p.get("displayName") or {}).get("text"),
                     "place_id": p.get("id"),
                     "avaliacoes": p.get("userRatingCount"),
                     "nota": p.get("rating"),
                     "metros_do_centro": metros(
                         centro, {"lat": pl.get("latitude"),
                                  "lng": pl.get("longitude")}
                         if pl.get("latitude") is not None else None)}
                quem.append(q)
                if p.get("id") == l.get("place_id") and pos is None:
                    pos = i
            marca = f"{pos}º" if pos else "FORA"
            topo = (quem[0]["nome"] or "")[:32] if quem else "(vazio)"
            print(f"       {marca:>4s}  {fr['frase'][:44]:44s} topo: {topo}")
            linhas.append({
                "snapshot_date": hoje, "praca_id": x["praca_id"],
                "rotulo": x["rotulo"], "local_id": l["local_id"],
                "place_id": l.get("place_id"), "unidade": nome,
                "frase": fr["frase"], "intencao": fr.get("intencao"),
                "raio_m": a.raio, "centro": centro,
                "nossa_posicao": pos, "resultados": len(achados),
                "quem": quem[:5],
                "fonte": "google places textsearch com locationBias circular",
            })
            brutos.setdefault(x["praca_id"], []).append(
                {"frase": fr["frase"], "local_id": l["local_id"],
                 "places": achados})

    if not linhas:
        # zero silencioso é falha: se nada foi medido, o script diz que
        # falhou em vez de fingir que rodou
        print("\n  ✗ FALHA: nenhuma consulta respondeu\n")
        sys.exit(1)

    aparece = sum(1 for r in linhas if r["nossa_posicao"])
    print(f"\n  {aparece} de {len(linhas)} consultas mostram a própria loja "
          f"num raio de {a.raio} m")

    if not a.salvar:
        print("\n  (--salvar para gravar)\n")
        return
    SERIE.mkdir(parents=True, exist_ok=True)
    with (SERIE/"perto_da_loja.jsonl").open("a", encoding="utf-8") as f:
        for r in linhas:
            f.write(json.dumps(r, ensure_ascii=False)+"\n")
    for pid, itens in brutos.items():
        d = BRUTO/pid/"perto_da_loja"/hoje
        d.mkdir(parents=True, exist_ok=True)
        (d/"busca.json").write_text(
            json.dumps(itens, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  → dados/serie/perto_da_loja.jsonl +{len(linhas)}\n")

    print("  O QUE ISTO NÃO DIZ:")
    print("   · não é volume de busca, e o círculo não é área de captação")
    print("   · aparecer antes não é roubar paciente — canibalização não")
    print("     está medida aqui\n")


if __name__ == "__main__":
    main()
