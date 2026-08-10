#!/usr/bin/env python3
"""
tokens.py — a rotação de tokens do Apify, num lugar só.

Por que existe
--------------
Cada coletor lia `APIFY_TOKEN=` e usava aquele token até o fim. Quando ele
estourava a cota, a coleta morria no meio com

    {'error': {'type': 'platform-feature-disabled',
               'message': 'Monthly usage hard limit exceeded'}}

e o operador só descobria olhando o log. Aconteceu com Parauapebas, que parou
na metade dos canais, e antes disso com cinco cidades numa rodada inteira que
saiu como "ok · +0 registros" — o zero silencioso que este projeto trata como
falha.

Pior: o `.env` tinha dezoito tokens e dezesseis estavam MORTOS
(`user-or-token-not-found`). Ninguém sabia, porque nada testava.

O que este arquivo faz
----------------------
Lê todos os `APIFY_TOKEN*` do ambiente e do `.env`, pergunta ao Apify quanto
cada um ainda tem, e devolve na ordem do mais folgado para o mais apertado. O
coletor chama `proximo()` quando o atual estoura, em vez de morrer.

As contas são de plano FREE, US$ 5/mês cada. Dez contas são US$ 50 — dá para
uma rodada completa, não para desperdício. Por isso o `resumo()` imprime o que
sobrou no fim de cada coleta: cota é um recurso que acaba calado.
"""
import json, os, pathlib, subprocess

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ENV = RAIZ/"_pipeline"/".env"


def _todos():
    fora = []
    for k, v in os.environ.items():
        if k.startswith("APIFY_TOKEN") and v.strip().startswith("apify_api_"):
            fora.append((k, v.strip()))
    if ENV.exists():
        for l in ENV.read_text(encoding="utf-8").split("\n"):
            l = l.strip().replace("\r", "")
            if l.startswith("APIFY_TOKEN") and "=" in l:
                k, v = l.split("=", 1)
                v = v.strip()
                if v.startswith("apify_api_") and not any(t == v for _, t in fora):
                    fora.append((k.strip(), v))
    return fora


def cota(t, tempo=25):
    """Quanto ainda cabe neste token. None quando o token não existe mais."""
    r = subprocess.run(["curl", "-sS", "-m", str(tempo),
                        f"https://api.apify.com/v2/users/me/limits?token={t}"],
                       capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
    except Exception:
        return None
    if "error" in d:
        return None
    dd = d.get("data", {})
    u = (dd.get("current") or {}).get("monthlyUsageUsd")
    m = (dd.get("limits") or {}).get("maxMonthlyUsageUsd")
    if u is None or not m:
        return None
    return round(m - u, 2)


def vivos(minimo=0.20, quieto=False):
    """Os tokens com cota, do mais folgado para o mais apertado.

    `minimo` existe porque token com US$ 0,05 livre entra numa coleta e morre
    na segunda chamada — gasta tempo e não entrega nada."""
    fora = []
    for nome, t in _todos():
        c = cota(t)
        if c is None:
            if not quieto:
                print(f"  {nome:20s} morto")
            continue
        if c < minimo:
            if not quieto:
                print(f"  {nome:20s} US$ {c:.2f} — abaixo do mínimo")
            continue
        if not quieto:
            print(f"  {nome:20s} US$ {c:.2f} livres")
        fora.append({"nome": nome, "token": t, "livre": c})
    fora.sort(key=lambda x: -x["livre"])
    return fora


def resumo():
    v = vivos(quieto=True)
    total = sum(x["livre"] for x in v)
    return f"{len(v)} token(s) com cota · US$ {total:.2f} livres no total"


if __name__ == "__main__":
    v = vivos()
    print(f"\n  {resumo()}\n")
