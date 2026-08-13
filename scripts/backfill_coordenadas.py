#!/usr/bin/env python3
"""
backfill_coordenadas.py — recupera do BRUTO a coordenada que já foi paga.

O QUE ACONTECEU. O `FieldMask` da varredura pede `places.location` desde a
primeira coleta. O arquivo bruto guardou as 3.304 respostas inteiras, com
latitude e longitude em todas. E `categoria.jsonl` gravava **zero** — o
campo era descartado na hora de escrever a série.

Ou seja: a coordenada de toda clínica varrida do país já estava paga e no
disco. Sem ela não existe distância, não existe vizinhança de verdade
(bairro é texto, não geografia) e não existe grade de busca. Este script
recupera tudo sem uma única chamada nova de API.

REGRAS QUE ELE SEGUE

· Nunca inventa coordenada. Só copia o que está no bruto.
· Não cria `local_id` novo nem mexe em `place_id` — a chave é o
  `place_id`, e ele já existe dos dois lados.
· Onde o bruto não tiver, a linha fica com `location: null` e entra na
  contagem de "sem coordenada", que é declarada.
· Não apaga histórico: reescreve as MESMAS linhas acrescentando o campo,
  sem mudar `snapshot_date` nem remover nada.

Uso:
    python3 scripts/backfill_coordenadas.py            # só mede
    python3 scripts/backfill_coordenadas.py --salvar
"""
import argparse, json, pathlib, sys
from collections import defaultdict

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SERIE = RAIZ/"dados"/"serie"
BRUTO = RAIZ/"dados"/"bruto"
IDENT = RAIZ/"dados"/"identidade"


def do_bruto():
    """place_id → {lat, lng}, lido de todos os brutos de varredura.

    Quando o mesmo lugar aparece em coletas diferentes, vale a mais nova —
    a clínica pode ter corrigido o pino no mapa.
    """
    fora, quando = {}, {}
    for f in sorted(BRUTO.rglob("*/google_places/*/varredura.json")):
        data = f.parent.name
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  ⚠ {f}: {type(e).__name__}")
            continue
        itens = d if isinstance(d, list) else (d.get("places") or d.get("achados") or [])
        for p in itens:
            if not isinstance(p, dict):
                continue
            pid = p.get("id") or p.get("place_id")
            loc = p.get("location") or {}
            lat, lng = loc.get("latitude"), loc.get("longitude")
            if pid and lat is not None and lng is not None:
                if pid not in quando or data >= quando[pid]:
                    fora[pid] = {"lat": lat, "lng": lng}
                    quando[pid] = data
    return fora


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()

    coord = do_bruto()
    print(f"  {len(coord)} coordenadas recuperadas do bruto, "
          f"sem nenhuma chamada de API")

    # ---------- categoria.jsonl ----------
    arq = SERIE/"categoria.jsonl"
    linhas = [json.loads(l) for l in arq.read_text(encoding="utf-8").split("\n")
              if l.strip()]
    achou, faltou = 0, defaultdict(int)
    for r in linhas:
        if r.get("location"):
            achou += 1
            continue
        c = coord.get(r.get("place_id"))
        if c:
            r["location"] = c
            achou += 1
        else:
            r["location"] = None
            faltou[r.get("praca_id")] += 1
    print(f"  categoria.jsonl: {achou} de {len(linhas)} linhas com coordenada")
    if faltou:
        print(f"  sem coordenada em: " +
              ", ".join(f"{k} ({v})" for k, v in sorted(faltou.items())[:6]))

    # ---------- identidades ----------
    tocadas, locais_ok, locais_sem = 0, 0, 0
    mudanca = {}
    for f in sorted(IDENT.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        mudou = False
        for l in d.get("locais", []):
            if l.get("location"):
                locais_ok += 1
                continue
            c = coord.get(l.get("place_id"))
            if c:
                l["location"] = c
                locais_ok += 1
                mudou = True
            else:
                locais_sem += 1
        if mudou:
            tocadas += 1
            mudanca[f] = d
    print(f"  identidades: {locais_ok} locais com coordenada, "
          f"{locais_sem} sem — em {tocadas} arquivos")

    if not a.salvar:
        print("\n  (--salvar para gravar)")
        return
    with arq.open("w", encoding="utf-8") as fh:
        for r in linhas:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    for f, d in mudanca.items():
        f.write_text(json.dumps(d, ensure_ascii=False, indent=2)+"\n",
                     encoding="utf-8")
    print(f"\n  → categoria.jsonl e {tocadas} identidades atualizadas")


if __name__ == "__main__":
    main()
