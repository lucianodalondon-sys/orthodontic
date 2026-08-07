#!/usr/bin/env python3
"""
injetar_casco.py — cola o payload de dados dentro do casco vindo do Claude Design.

O artefato publicado roda sob CSP estrita: NENHUMA requisição externa passa.
Sem fetch, sem XHR, sem CDN. Então o dado não pode ser buscado em tempo de
execução — ele é embutido no momento da publicação.

    dados/portal/*.json  +  casco (HTML do Claude Design)
    → portal/index.html  (pronto para publicar)

O casco lê assim, e nunca de outro jeito:

    const DADOS = JSON.parse(
      document.getElementById("dados-portal").textContent
    );

Uso:
    python3 scripts/injetar_casco.py casco-bruto.html
    python3 scripts/injetar_casco.py casco-bruto.html -o portal/index.html
"""
import json, argparse, pathlib, re, sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PORTAL = RAIZ/"dados"/"portal"
MARCADOR = re.compile(
    r'<script[^>]*id=["\']dados-portal["\'][^>]*>.*?</script>', re.S | re.I)


def coleta_payload():
    if not PORTAL.exists():
        sys.exit("dados/portal/ não existe — rode scripts/build_portal.py antes")
    payload = {}
    for p in sorted(PORTAL.glob("*.json")):
        payload[p.stem] = json.loads(p.read_text(encoding="utf-8"))
    pracas = {}
    for p in sorted((PORTAL/"pracas").glob("*.json")):
        pracas[p.stem] = json.loads(p.read_text(encoding="utf-8"))
    if pracas:
        payload["pracas"] = pracas
    return payload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("casco", help="HTML vindo do Claude Design")
    ap.add_argument("-o", "--saida", default="portal/index.html")
    args = ap.parse_args()

    html = pathlib.Path(args.casco).read_text(encoding="utf-8")
    payload = coleta_payload()

    # </script> dentro de JSON quebraria o bloco; escapa a barra.
    bruto = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    bloco = f'<script id="dados-portal" type="application/json">{bruto}</script>'

    if MARCADOR.search(html):
        html, n = MARCADOR.subn(bloco, html, count=1)
        onde = "substituiu o bloco existente"
    elif "</head>" in html:
        html = html.replace("</head>", bloco + "\n</head>", 1)
        onde = "injetou antes de </head>"
    elif "<body" in html:
        i = html.index(">", html.index("<body")) + 1
        html = html[:i] + "\n" + bloco + html[i:]
        onde = "injetou no início do <body>"
    else:
        html = bloco + "\n" + html
        onde = "injetou no topo do arquivo"

    saida = pathlib.Path(args.saida)
    if not saida.is_absolute():
        saida = RAIZ/saida
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(html, encoding="utf-8")

    corte = payload.get("manifest", {}).get("corte", "?")
    try:
        mostra = saida.relative_to(RAIZ)
    except ValueError:
        mostra = saida
    print(f"{mostra} · corte {corte} · {onde}")
    print(f"payload: {len(bruto)/1024:.0f} KB · telas: {', '.join(k for k in payload if k != 'pracas')}"
          + (f" · praças: {', '.join(payload.get('pracas', {}))}" if payload.get("pracas") else ""))

    if "dados-portal" not in html:
        sys.exit("ERRO: o bloco não ficou no HTML")
    faltando = [k for k in ("rede", "achados", "corretor", "evidencias") if k not in payload]
    if faltando:
        print("AVISO: faltam telas no payload:", ", ".join(faltando))


if __name__ == "__main__":
    main()
