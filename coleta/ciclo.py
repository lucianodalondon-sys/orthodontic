#!/usr/bin/env python3
"""
ciclo.py — o relógio da coleta.

Sabe o que roda em que frequência, quando cada coisa rodou pela última vez, e
o que está vencido. Roda só o que venceu — coletar de novo o que não venceu é
gastar crédito para gravar a mesma linha.

    python3 coleta/ciclo.py                 # o que está vencido
    python3 coleta/ciclo.py --rodar         # roda o vencido
    python3 coleta/ciclo.py --rodar --so google_reviews
    python3 coleta/ciclo.py --rodar --forcar
    python3 coleta/ciclo.py --plano         # o calendário inteiro, com pendências

Estado em dados/serie/_ciclo.json. Log em dados/serie/_ciclo.log.
"""
import argparse, json, pathlib, subprocess, sys
import datetime as dt

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ESTADO = RAIZ/"dados"/"serie"/"_ciclo.json"
LOG = RAIZ/"dados"/"serie"/"_ciclo.log"
PRACAS = ["mafra", "londrina", "feira", "prudente"]
DIAS = {"semanal": 7, "quinzenal": 14, "mensal": 30, "trimestral": 90, "anual": 365}

# ---------------------------------------------------------------- catálogo
# status: pronto (roda) · construir · precisa_acesso
COLETORES = {
 "google_reviews": dict(freq="semanal", status="pronto", por_praca=True,
   cmd=["python3", "coleta/coletores/google_reviews.py", "--praca", "{praca}", "--max-reviews", "80"],
   custo="~US$0,04/praça", da="nota, volume, velocity, taxa de resposta, distribuição"),
 "meta_ads": dict(freq="semanal", status="pronto", por_praca=True,
   cmd=["python3", "coleta/coletores/meta_ads.py", "--praca", "{praca}"],
   custo="~US$0,10/praça", da="quem anuncia, com que texto, há quantos dias"),
 "imprensa_rss": dict(freq="semanal", status="pronto", por_praca=False,
   cmd=["python3", "coleta/coletores/imprensa_rss.py"],
   custo="grátis", da="a joia enterrada, o que a cidade noticia"),

 "google_places": dict(freq="mensal", status="pronto", por_praca=True,
   cmd=["python3", "coleta/coletores/google_places.py", "--praca", "{praca}"],
   custo="~US$0,05/praça", da="a categoria INTEIRA — 747 clínicas onde a lista a mão tinha 36"),

 "canais": dict(freq="mensal", status="pronto", por_praca=True,
   cmd=["python3", "coleta/coletores/canais.py", "--praca", "{praca}"],
   custo="~US$0,20/praça", da="os 9 canais da cidade — e os que NÃO existem, que é território vazio"),

 # --- a construir, na ordem de valor (ver coleta/FONTES.md) ---
 "reclame_aqui": dict(freq="mensal", status="pronto", por_praca=False,
   cmd=["python3", "coleta/coletores/reclame_aqui.py", "--empresa", "orthodontic", "--n", "20"],
   custo="~US$1/marca", da="reclamação, resposta, resolução e selo — da marca e das concorrentes"),
 "google_ads": dict(freq="semanal", status="pronto", por_praca=True,
   cmd=["python3", "coleta/coletores/google_ads.py", "--praca", "{praca}"],
   custo="~US$0,20/praça", da="quem compra a BUSCA, e há quantos dias o anúncio está no ar"),
 "whatsapp_teste": dict(freq="mensal", status="pronto", por_praca=True, manual=True,
   cmd=["python3", "coleta/coletores/whatsapp_teste.py", "--praca", "{praca}", "--preparar"],
   custo="manual",
   da="tempo até a 1ª resposta — a ferida nº1 das 4 praças, sem medição"),
 "doctoralia":     dict(freq="mensal", status="construir", custo="baixo",
   da="avaliação por PROFISSIONAL nomeado — mede a constante nº3"),
 "grupos_facebook":dict(freq="mensal", status="construir", custo="baixo",
   da="a DECISÃO acontecendo: 'alguém indica ortodontista?'"),
 "mapa_diff":      dict(freq="mensal", status="construir", custo="baixo",
   da="clínica nova no raio desde a última coleta"),
 "cnpj_novo":      dict(freq="mensal", status="construir", custo="grátis",
   da="o concorrente ANTES de ele abrir"),
 "vagas":          dict(freq="mensal", status="construir", custo="baixo",
   da="expansão do concorrente · rotatividade da nossa recepção"),
 "google_qa":      dict(freq="mensal", status="construir", custo="baixo",
   da="a dúvida ANTES de decidir"),
 "youtube":        dict(freq="trimestral", status="construir", custo="grátis (chave já funciona)",
   da="comentários em vídeo local"),
 "instagram": dict(freq="mensal", status="pronto", por_praca=True,
   cmd=["python3", "coleta/coletores/instagram.py", "--praca", "{praca}"],
   custo="~US$0,40/praça",
   da="a voz da cidade — o pipeline legado fazia, falta portar"),
 "serp":           dict(freq="mensal", status="construir", custo="baixo",
   da="quem aparece quando o paciente procura"),
 "cro_registro":   dict(freq="trimestral", status="construir", custo="grátis",
   da="quantos ortodontistas na cidade, em qual clínica"),
 "glassdoor":      dict(freq="trimestral", status="construir", custo="baixo",
   da="a voz do funcionário da linha de frente"),

 # --- dependem da rede ---
 "gbp_insights":   dict(freq="mensal", status="precisa_acesso", custo="grátis",
   da="buscas, cliques e LIGAÇÕES por unidade — topo de funil sem o Conecta"),
 "conecta_funil":  dict(freq="mensal", status="precisa_acesso", custo="grátis",
   da="funil, base ativa e safra"),
}


def carrega():
    return json.loads(ESTADO.read_text(encoding="utf-8")) if ESTADO.exists() else {}


def salva(e):
    ESTADO.parent.mkdir(parents=True, exist_ok=True)
    ESTADO.write_text(json.dumps(e, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def venceu(ultimo, freq, hoje):
    if not ultimo:
        return True, "nunca rodou"
    d = (hoje - dt.date.fromisoformat(ultimo)).days
    lim = DIAS[freq]
    return d >= lim, f"há {d}d (limite {lim}d)"


def registra(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{dt.datetime.now().isoformat(timespec='seconds')}\t{msg}\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rodar", action="store_true")
    ap.add_argument("--forcar", action="store_true")
    ap.add_argument("--so", help="só um coletor")
    ap.add_argument("--praca", help="só uma praça")
    ap.add_argument("--plano", action="store_true", help="mostra o calendário inteiro")
    args = ap.parse_args()

    hoje = dt.date.today()
    est = carrega()

    if args.plano:
        for st, rot in [("pronto", "RODANDO"), ("construir", "A CONSTRUIR"), ("precisa_acesso", "DEPENDE DA REDE")]:
            print(f"\n=== {rot} ===")
            for k, c in COLETORES.items():
                if c["status"] != st:
                    continue
                print(f"  {k:18s} {c['freq']:11s} {c['custo']:26s} {c['da']}")
        pr = sum(1 for c in COLETORES.values() if c["status"] == "pronto")
        print(f"\n{pr} de {len(COLETORES)} coletores prontos.")
        return

    pend = []
    for k, c in COLETORES.items():
        if args.so and k != args.so:
            continue
        if c["status"] != "pronto":
            continue
        alvos = PRACAS if c.get("por_praca") else ["*"]
        if args.praca and c.get("por_praca"):
            alvos = [args.praca]
        for p in alvos:
            chave = f"{k}|{p}"
            v, porque = venceu(est.get(chave), c["freq"], hoje)
            if v or args.forcar:
                pend.append((k, c, p, porque))

    if not pend:
        print("nada vencido. Tudo em dia.")
        for k, c in COLETORES.items():
            if c["status"] != "pronto":
                continue
            for p in (PRACAS if c.get("por_praca") else ["*"]):
                u = est.get(f"{k}|{p}")
                if u:
                    print(f"  {k:18s} {p:10s} última {u}")
        return

    print(f"{len(pend)} tarefa(s) vencida(s):")
    for k, c, p, porque in pend:
        print(f"  {k:18s} {p:10s} {c['freq']:11s} {porque}  · {c['custo']}")

    if not args.rodar:
        print("\nrode com --rodar para executar")
        return

    for k, c, p, _ in pend:
        cmd = [x.replace("{praca}", p) for x in c["cmd"]]
        print(f"\n--- {k} · {p} ---", flush=True)
        r = subprocess.run(cmd, cwd=RAIZ)
        if r.returncode == 0:
            est[f"{k}|{p}"] = hoje.isoformat()
            registra(f"OK\t{k}\t{p}")
        else:
            registra(f"FALHOU({r.returncode})\t{k}\t{p}")
            print(f"  [FALHOU] código {r.returncode} — estado NÃO atualizado")
    salva(est)

    print("\n--- reconstruindo o payload do portal ---")
    subprocess.run(["python3", "scripts/build_portal.py"], cwd=RAIZ)


if __name__ == "__main__":
    main()
