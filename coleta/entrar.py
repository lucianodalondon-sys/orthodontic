#!/usr/bin/env python3
"""
entrar.py — um comando para entrar numa cidade nova.

Até agora, entrar numa praça eram seis comandos na ordem certa, e a ordem
importa: sem a varredura não há place_id, sem place_id o coletor de avaliação
devolve zero, sem canal não há o que escutar. Errar a ordem não dá erro —
dá praça pela metade, silenciosamente.

    python3 coleta/entrar.py --cidade "Ribeirão Preto/SP"
    python3 coleta/entrar.py --cidade "Mafra/SC" --mais "Rio Negro/PR" --id riomafra
    python3 coleta/entrar.py --praca palmas --continuar    # retoma de onde parou
    python3 coleta/entrar.py --cidade "Bauru/SP" --simular # mostra o plano, não gasta

Ele é retomável de propósito. A conta da Apify acaba no meio, a rede cai, o
container reinicia — e nada disso pode obrigar a refazer o que já foi pago.
Cada etapa checa se já tem dado na série antes de rodar.

O QUE ELE NÃO FAZ, e continua sendo humano:
  · conferir os canais que a busca achou (em Palmas, 31% era lixo)
  · dizer que tipo de concorrente é cada um
  · achar a joia enterrada
  · perguntar à unidade o que ela faz de mídia fora da internet

Ele imprime essa lista no fim. É onde o método ganha ou perde.
"""
import argparse, json, pathlib, subprocess, sys, time
import datetime as dt

RAIZ = pathlib.Path(__file__).resolve().parent.parent
IDENT = RAIZ/"dados"/"identidade"
SERIE = RAIZ/"dados"/"serie"

# A ordem é a do coleta/NOVA-PRACA.md e não pode ser trocada.
ETAPAS = [
 ("descobrir", "a cidade em números e os veículos de imprensa",
  ["python3", "coleta/descobrir_praca.py"], None, 0.00),
 ("varrer", "a categoria inteira — quem existe na praça",
  ["python3", "coleta/coletores/google_places.py", "--praca", "{p}"], "categoria", 0.05),
 ("avaliar", "avaliações com data — de onde sai o ritmo",
  ["python3", "coleta/coletores/google_reviews.py", "--praca", "{p}", "--max-reviews", "150"],
  "reviews", 0.60),
 ("canais", "quem fala com a cidade, e quais canais NÃO existem",
  ["python3", "coleta/coletores/canais.py", "--praca", "{p}"], "canais", 0.20),
 ("escutar", "o que a cidade diz — as palavras dela",
  ["python3", "coleta/coletores/escutar_cidade.py", "--praca", "{p}", "--posts", "80"],
  "posts", 0.35),
 ("anuncios", "quem anuncia na praça e com que texto",
  ["python3", "coleta/coletores/meta_ads.py", "--praca", "{p}"], "anuncios", 0.40),
 ("imprensa", "a notícia local e a pista da joia enterrada",
  ["python3", "coleta/coletores/imprensa_rss.py", "--praca", "{p}"], "imprensa", 0.00),
 ("portas", "as frases que a cidade digita, e onde a unidade some",
  ["python3", "coleta/coletores/portas.py", "--praca", "{p}", "--quantas", "20",
   "--salvar"], "portas", 0.64),
 ("separar", "as vozes por assunto",
  ["python3", "scripts/classificar.py"], None, 0.00),
 ("ler", "o placar, as hipóteses e o que pesa contra",
  ["python3", "scripts/inteligencia.py", "--praca", "{p}"], None, 0.00),
 ("captar", "as oportunidades de captação do franqueado",
  ["python3", "scripts/oportunidades_franqueado.py", "--praca", "{p}", "--salvar"],
  None, 0.00),
 ("plano", "o mesmo, escrito para o franqueado fazer",
  ["python3", "scripts/plano_do_franqueado.py", "--praca", "{p}", "--salvar", "--md"],
  None, 0.00),
]

A_MAO = [
 "conferir os canais que a busca achou — em Palmas 31% era de outra cidade ou outro assunto",
 "dizer que TIPO de concorrente é cada um: rede popular, doutor com nome próprio, clínica-escola…",
 "achar a joia enterrada — o ativo local que ninguém copia (a imprensa costuma ter a pista)",
 "perguntar à unidade: \"o que vocês fazem de mídia que não está na internet?\"",
 "o calendário: férias escolares do estado + as festas da cidade",
]


def jsonl(nome):
    p = SERIE/f"{nome}.jsonl"
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def ja_tem(arquivo, praca):
    if not arquivo:
        return 0
    return sum(1 for r in jsonl(arquivo) if r.get("praca_id") == praca)


def roda(cmd, minutos=25):
    try:
        r = subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True, timeout=minutos*60)
        return r.returncode == 0, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return False, f"passou de {minutos} minutos"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cidade", help='ex: "Ribeirão Preto/SP"')
    ap.add_argument("--mais", action="append", default=[], help="outra cidade da mesma praça")
    ap.add_argument("--praca", help="praça já existente, para continuar")
    ap.add_argument("--id", help="praca_id (padrão: derivado do nome)")
    ap.add_argument("--continuar", action="store_true", help="pula o que já tem dado")
    ap.add_argument("--simular", action="store_true", help="mostra o plano e não gasta")
    a = ap.parse_args()

    if not a.cidade and not a.praca:
        sys.exit("use --cidade \"Nome/UF\" para praça nova, ou --praca <id> para continuar")

    praca = a.praca or a.id or None
    if a.cidade and not praca:
        import re, unicodedata
        n = unicodedata.normalize("NFKD", a.cidade.split("/")[0])
        praca = re.sub(r"[^a-z0-9]+", "_",
                       "".join(c for c in n if not unicodedata.combining(c)).lower()).strip("_")

    print(f"\n{'='*74}\n  ENTRANDO NA PRAÇA · {praca}"
          + (f"  ({a.cidade}{' + ' + ' + '.join(a.mais) if a.mais else ''})" if a.cidade else "")
          + f"\n{'='*74}")

    custo = sum(c for _, _, _, _, c in ETAPAS)
    print(f"\n  {len(ETAPAS)} etapas · custo estimado US$ {custo:.2f} · ~40 min de máquina")
    if a.simular:
        for i, (nome, oque, cmd, arq, c) in enumerate(ETAPAS, 1):
            tem = ja_tem(arq, praca)
            marca = f"já tem {tem}" if tem else "vai rodar"
            print(f"  {i}. {nome:10s} US$ {c:.2f}  {oque[:48]:48s} [{marca}]")
        print("\n  (simulação — nada foi gasto)\n")
        return

    inicio = time.time()
    feitas, puladas, falhas = [], [], []
    for i, (nome, oque, cmd, arq, c) in enumerate(ETAPAS, 1):
        tem = ja_tem(arq, praca)
        if a.continuar and tem:
            print(f"\n  {i}/{len(ETAPAS)} {nome} — pulado, já tem {tem} registros")
            puladas.append(nome)
            continue

        linha = [x.replace("{p}", praca) for x in cmd]
        if nome == "descobrir":
            if (IDENT/f"{praca}.json").exists() and a.continuar:
                print(f"\n  {i}/{len(ETAPAS)} descobrir — pulado, identidade existe")
                puladas.append(nome); continue
            if not a.cidade:
                print(f"\n  {i}/{len(ETAPAS)} descobrir — pulado, sem --cidade")
                puladas.append(nome); continue
            linha += ["--cidade", a.cidade, "--id", praca, "--sem-clinicas"]
            for m in a.mais:
                linha += ["--mais", m]

        print(f"\n  {i}/{len(ETAPAS)} {nome} — {oque}")
        ok, saida = roda(linha)
        if ok:
            depois = ja_tem(arq, praca)
            print(f"      ok" + (f" · +{depois-tem} registros" if arq else ""))
            feitas.append(nome)
        else:
            print(f"      FALHOU: {saida.strip().splitlines()[-1][:120] if saida.strip() else '?'}")
            falhas.append(nome)
            if "not-enough-usage" in saida or "402" in saida:
                print("\n  A conta da Apify acabou. Troque APIFY_TOKEN em _pipeline/.env e rode:")
                print(f"    python3 coleta/entrar.py --praca {praca} --continuar\n")
                return

    mins = (time.time()-inicio)/60
    print(f"\n{'='*74}\n  {len(feitas)} etapas rodaram, {len(puladas)} puladas, "
          f"{len(falhas)} falharam · {mins:.0f} min")
    if falhas:
        print(f"  falharam: {', '.join(falhas)} — rode de novo com --continuar")

    print(f"\n  AGORA É COM VOCÊ — sem isto a praça não está pronta:")
    for j, item in enumerate(A_MAO, 1):
        print(f"    {j}. {item}")
    print(f"\n  E quando terminar: python3 scripts/inteligencia.py --praca {praca}\n")


if __name__ == "__main__":
    main()
