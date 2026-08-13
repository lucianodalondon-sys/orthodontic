#!/usr/bin/env python3
"""
dedup_serie.py — tira linha repetida quando o MESMO coletor rodou duas vezes.

POR QUE ISTO EXISTE. Duas execuções do mesmo coletor, na mesma praça e no
mesmo dia, gravam a mesma medição duas vezes. Aconteceu com Florianópolis:
dois processos de `canais.py` rodando em paralelo deixaram 18 linhas onde
existem 9 canais. Contador de canal, de anúncio e de porta passa a mentir
para cima, e a régua ("mínimo 8 canais") passa a ser cumprida por
duplicata.

O QUE ELE APAGA, E SÓ ISSO

    mesma praça + mesma data + mesma entidade  →  fica a primeira

Nada mais. Ele NÃO junta datas diferentes (isso é histórico, e histórico é
o produto), NÃO decide qual medição é melhor e NÃO toca em linha que tenha
qualquer campo de identidade diferente. Série continua append-only: o
arquivo é reescrito com as MESMAS linhas, menos as repetidas.

A chave de cada série está declarada abaixo, à mão, porque adivinhar chave
é como o projeto já perdeu 981 avaliações em dobro.

Uso:
    python3 scripts/dedup_serie.py
    python3 scripts/dedup_serie.py --salvar
"""
import argparse, json, pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SERIE = RAIZ/"dados"/"serie"

# série → campos que, junto com praca_id e snapshot_date, identificam a
# medição. Campo ausente entra como None e continua fazendo parte da chave.
CHAVES = {
    # `tipo` entra porque o coletor grava um lugar para cada papel da
    # cidade (prefeitura, imprensa, mãe…) e o que não achou fica com
    # handle e nome vazios: oito vagas não preenchidas não são oito
    # linhas repetidas.
    "canais": ("plataforma", "tipo", "handle", "nome"),
    # `chave` é o que o coletor de anúncio já usa para deduplicar; `ad_id`
    # é o id do próprio anúncio. A primeira versão deste arquivo procurou
    # `anuncio_id`, `id`, `pagina` e `texto` — nenhum existe — e a chave
    # virou (praça, data, None, None, None, None): 610 anúncios DIFERENTES
    # entraram como repetidos, 36 do mesmo anunciante de uma vez. Campo de
    # chave que não existe na série é falha, e o guarda abaixo grita.
    "anuncios": ("chave", "ad_id"),
    "portas": ("frase", "local_id"),
    "perto_da_loja": ("local_id", "frase", "raio_m"),
    "categoria": ("place_id",),
    "imprensa": ("link", "titulo"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()

    total = 0
    for nome, campos in CHAVES.items():
        p = SERIE/f"{nome}.jsonl"
        if not p.exists():
            continue
        linhas = [json.loads(l) for l in p.read_text(encoding="utf-8").split("\n")
                  if l.strip()]
        # CAMPO DE CHAVE QUE NÃO EXISTE FUNDE TUDO. Sem esta trava, a
        # chave inteira vira None e a série inteira do dia colapsa numa
        # linha só — foi o que quase aconteceu com 610 anúncios.
        cegos = [c for c in campos
                 if not any(c in r for r in linhas)]
        if len(cegos) == len(campos):
            print(f"  ✗ {nome}: nenhum campo de chave existe nesta série "
                  f"({', '.join(campos)}) — não mexo")
            continue
        vistos, fica, por_praca = set(), [], {}
        for r in linhas:
            k = (r.get("praca_id"), r.get("snapshot_date")) + tuple(
                json.dumps(r.get(c), ensure_ascii=False, sort_keys=True)
                for c in campos)
            if k in vistos:
                por_praca[r.get("praca_id")] = por_praca.get(r.get("praca_id"), 0)+1
                continue
            vistos.add(k)
            fica.append(r)
        fora = len(linhas) - len(fica)
        if not fora:
            print(f"  {nome:<16} {len(linhas)} linhas · nada repetido")
            continue
        total += fora
        print(f"  {nome:<16} {len(linhas)} linhas · {fora} repetidas — "
              + ", ".join(f"{k}: {v}" for k, v in sorted(por_praca.items())[:5]))
        if a.salvar:
            with p.open("w", encoding="utf-8") as f:
                for r in fica:
                    f.write(json.dumps(r, ensure_ascii=False)+"\n")

    if not total:
        print("\n  nenhuma duplicata — nada a fazer")
    elif a.salvar:
        print(f"\n  → {total} linhas repetidas removidas")
    else:
        print(f"\n  {total} linhas repetidas (--salvar para remover)")


if __name__ == "__main__":
    main()
