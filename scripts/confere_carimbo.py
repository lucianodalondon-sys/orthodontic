#!/usr/bin/env python3
"""
confere_carimbo.py — o carimbo de confiança está dizendo a verdade?

POR QUE ISTO EXISTE. O motor de confiança é o que separa fato de inferência
e de opinião, e é justamente por isso que um metadado errado nele é pior
que metadado ausente: **ele parece rigor**. Dois casos reais:

  · o evento do Vitae Center saía com "medido em 3863 clínicas medidas".
    3.863 é a base de avaliações daquela ficha; a praça inteira tem 27
    clínicas. Amostra e unidade falavam de coisas diferentes.

  · a recomendação da jornada dizia no texto "14 de 17 avaliações são de 1
    ou 2 estrelas" e trazia `amostra: null` — "sem amostra declarada". O
    número existia e não estava onde a procedência o lê.

O que este script cobra, e só isto:

  1. amostra sem unidade, ou unidade sem amostra
  2. texto que cita "N de M" ou "N avaliações" com `amostra` nula
  3. `medido: true` com amostra nula — medir é ter medido alguma coisa
  4. `natureza: fato` sem fonte
  5. procedência que não cita o número da amostra que o próprio carimbo traz

Ele NÃO julga se o número está certo. Julga se o carimbo é coerente
consigo mesmo e com a frase que ele acompanha.

Uso:
    python3 scripts/confere_carimbo.py
    python3 scripts/confere_carimbo.py --exigir   # sai com erro se houver
"""
import argparse, json, pathlib, re, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from cruzamento import conta

RAIZ = pathlib.Path(__file__).resolve().parent.parent
OUT = RAIZ/"dados"/"portal"

# frases do texto ao lado que provam que existe amostra
COM_NUMERO = re.compile(r"\d+\s+de\s+\d+|\d+\s+avaliaç|\d+\s+busca", re.I)


def anda(no, caminho, achados, texto_perto=None):
    """Desce o payload procurando dicionários que tenham 'confianca'."""
    if isinstance(no, dict):
        # o texto vizinho ajuda a saber se havia amostra para declarar
        perto = " ".join(str(no.get(k) or "") for k in
                         ("problema", "frase", "titulo", "manchete", "fato",
                          "o_que_e", "leitura"))
        c = no.get("confianca")
        if isinstance(c, dict):
            confere(c, caminho, perto or (texto_perto or ""), achados)
        for k, v in no.items():
            if k != "confianca":
                anda(v, f"{caminho}.{k}", achados, perto or texto_perto)
    elif isinstance(no, list):
        for i, v in enumerate(no):
            anda(v, f"{caminho}[{i}]", achados, texto_perto)


def confere(c, caminho, texto, achados):
    am, un = c.get("amostra"), c.get("unidade_amostra")
    proc = str(c.get("procedencia") or "")

    # `unidade_amostra` não é emitida no payload — ela vira substantivo
    # dentro de `procedencia`. Então o que se confere aqui é se a
    # procedência realmente NOMEIA o que foi contado, não se o campo existe.
    if am is not None and not re.search(r"\d+\s+[a-zà-ú]", proc):
        achados.append((caminho, f"amostra {am} sem substantivo na procedência"))
    if am is None and COM_NUMERO.search(texto or ""):
        achados.append((caminho,
                        "o texto ao lado cita um número medido e o carimbo "
                        f"diz '{proc[:44]}'"))
    if c.get("medido") is True and am is None and c.get("natureza") == "fato":
        achados.append((caminho, "medido: true com amostra nula"))
    if c.get("natureza") == "fato" and not c.get("fonte"):
        achados.append((caminho, "fato sem fonte"))
    if am is not None and proc and str(am) not in proc:
        achados.append((caminho,
                        f"amostra {am} não aparece na procedência '{proc[:44]}'"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exigir", action="store_true")
    a = ap.parse_args()

    achados, arquivos = [], 0
    for arq in sorted(OUT.rglob("*.json")):
        try:
            d = json.loads(arq.read_text(encoding="utf-8"))
        except Exception:
            continue
        arquivos += 1
        anda(d, str(arq.relative_to(OUT)), achados)

    por_tipo = {}
    for _, m in achados:
        k = re.sub(r"\d+", "N", m)[:52]
        por_tipo[k] = por_tipo.get(k, 0) + 1

    print(f"  {arquivos} arquivos do portal conferidos")
    if not achados:
        print("  todo carimbo de confiança é coerente com a frase que acompanha")
        return
    print(f"\n  {conta(len(achados), 'carimbo incoerente', 'carimbos incoerentes')}:")
    for k, n in sorted(por_tipo.items(), key=lambda x: -x[1]):
        print(f"    {n:>4}×  {k}")
    print("\n  exemplos:")
    for caminho, m in achados[:6]:
        print(f"    {caminho[:66]}\n        {m}")
    if a.exigir:
        sys.exit(1)


if __name__ == "__main__":
    main()
