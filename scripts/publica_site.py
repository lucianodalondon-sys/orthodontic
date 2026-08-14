#!/usr/bin/env python3
"""
publica_site.py — junta o casco e o payload numa pasta que a Vercel serve.

Por que existe
--------------
O portal tem duas metades que nascem em lugares diferentes e nunca se
misturam no repositório:

  casco/          o que o Claude Design entrega — HTML, CSS, JS, fontes
  dados/portal/   o que `build_portal.py` monta — todo número da tela

Este script copia as duas para `site/`, que é o que a Vercel publica. Ele
não desenha nem calcula nada: se falta número, o conserto é no build; se
falta tela, o conserto é no Design.

`site/` é descartável e fica fora do git — quem manda são as duas origens.

O que ele COBRA antes de publicar
---------------------------------
Publicar é a única etapa que o cliente vê. Então aqui se confere o que
custaria caro descobrir depois:

  · o casco existe e tem `index.html`
  · o payload existe e tem `manifest.json`
  · a tela de login existe (sem ela o middleware manda todo mundo para uma
    porta que não abre)
  · todo arquivo que o casco pede por nome está no payload

A última é a que pega o erro de verdade: casco novo pedindo um payload que
o build ainda não escreve sai como tela em branco no navegador do cliente,
sem erro nenhum no terminal.

Uso:
    python3 scripts/publica_site.py
    python3 scripts/publica_site.py --limpar     # apaga site/ antes
"""
import argparse
import pathlib
import re
import shutil
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CASCO = RAIZ/"casco"
PAYLOAD = RAIZ/"dados"/"portal"
ENTRADA = RAIZ/"entrada"
SITE = RAIZ/"site"


def falha(msg, conserto=""):
    print(f"\n  ✗ FALHA: {msg}")
    if conserto:
        print(f"  conserto: {conserto}")
    sys.exit(1)


def payloads_que_o_casco_pede():
    """Os nomes que o JS do casco busca — para conferir se todos existem.

    O casco chama `carregar("nome")` e monta `dados/portal/nome.json`. Aqui
    se procura essa chamada. Nome montado em tempo de execução (a página de
    uma clínica, que é `clinicas/<local_id>`) não aparece e nem deveria: o
    que se confere é o payload FIXO, que é o que quebra a tela inteira.
    """
    js = sorted(CASCO.glob("assets/*.js"))
    if not js:
        return set()
    texto = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in js)
    return {m for m in re.findall(r'carregar\(\s*"([a-z_]+)"\s*\)', texto)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limpar", action="store_true")
    a = ap.parse_args()

    if not (CASCO/"index.html").exists():
        falha("não há casco/index.html",
              "descompacte o zip que voltou do Claude Design em casco/")
    if not (PAYLOAD/"manifest.json").exists():
        falha("não há dados/portal/manifest.json",
              "python3 scripts/build_portal.py")
    if not (ENTRADA/"login.html").exists():
        falha("não há entrada/login.html — o middleware manda todo mundo "
              "para /entrar, e sem esta página a porta não abre")

    faltando = sorted(p for p in payloads_que_o_casco_pede()
                      if not (PAYLOAD/f"{p}.json").exists())
    if faltando:
        falha(f"o casco pede {len(faltando)} payload(s) que o build não "
              f"escreveu: {', '.join(faltando)}",
              "python3 scripts/build_portal.py (e confira se o script que "
              "monta essa tela rodou antes)")

    if a.limpar and SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir(exist_ok=True)

    # o casco primeiro, inteiro
    for item in CASCO.iterdir():
        destino = SITE/item.name
        if item.is_dir():
            shutil.copytree(item, destino, dirs_exist_ok=True)
        else:
            shutil.copy2(item, destino)

    # o payload, no caminho relativo que o casco busca
    alvo = SITE/"dados"/"portal"
    if alvo.exists():
        shutil.rmtree(alvo)
    shutil.copytree(PAYLOAD, alvo)

    # a tela de login, como /entrar
    shutil.copy2(ENTRADA/"login.html", SITE/"entrar.html")

    arqs = [p for p in SITE.rglob("*") if p.is_file()]
    mb = sum(p.stat().st_size for p in arqs)/1_048_576
    telas = len(list((alvo).glob("*.json")))
    print(f"\n  site/ montado — {len(arqs)} arquivos · {mb:.1f} MB")
    print(f"  casco: {len(list(SITE.glob('assets/*')))} peças em assets/")
    print(f"  payload: {telas} telas + subpastas")
    print(f"  login: site/entrar.html\n")
    # este texto aparece no LOG DE BUILD da Vercel, que é onde alguém olha
    # quando o portal responde 503 — então ele nomeia as variáveis certas
    print("  a porta precisa destas variáveis na Vercel (ver DEPLOY.md):")
    print("     SEGREDO_DA_SESSAO    string longa e aleatória, só do servidor")
    print("     EMAILS_AUTORIZADOS   quem pode entrar, separado por vírgula")
    print("     RESEND_API_KEY       provedor que envia o código por e-mail")
    print("  sem elas o middleware devolve 503 e não deixa passar — de propósito.\n")


if __name__ == "__main__":
    main()
