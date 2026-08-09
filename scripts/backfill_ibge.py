#!/usr/bin/env python3
"""
backfill_ibge.py — põe os números do IBGE nas praças que entraram antes do
coletor existir.

Quatro das sete praças da base — Feira, Londrina, Prudente e Mafra — não
tinham bloco `ibge` nenhum: nasceram antes do `descobrir_praca.py`. Cuiabá
tinha população e massa salarial, mas não as faixas etárias.

Isso passou despercebido enquanto ninguém precisava comparar praça com praça.
Na primeira vez que precisou — a gêmea da praça de oportunidade — o estrago
apareceu inteiro: **Juazeiro do Norte, com 305 mil habitantes, casou com
Mafra, que tem 89 mil**, porque Mafra só tinha dois dos seis eixos e
praça com menos eixo é mais fácil de casar. Amostra incompleta não erra o
número, erra o SINAL.

Não toca em `locais`, em `nota_geografia` nem em nada escrito à mão.

Uso:
    python3 scripts/backfill_ibge.py            # mostra o que falta
    python3 scripts/backfill_ibge.py --gravar
"""
import argparse, json, pathlib, sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
IDENT = RAIZ/"dados"/"identidade"
sys.path.insert(0, str(RAIZ/"coleta"))
import descobrir_praca as desc          # noqa: E402


def completo(bloco):
    """Um bloco só serve se tem população, massa salarial E faixas etárias.
    Faltando qualquer um, a praça entra torta na comparação."""
    return bool(bloco.get("populacao_estimada")
                and bloco.get("massa_salarial_mil_reais")
                and bloco.get("idades"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gravar", action="store_true")
    a = ap.parse_args()

    for arq in sorted(IDENT.glob("*.json")):
        d = json.loads(arq.read_text(encoding="utf-8"))
        cidades = d.get("cidades") or []
        atual = {b.get("municipio"): b for b in (d.get("ibge") or [])}
        faltam = [c for c in cidades
                  if not completo(atual.get(c.split("/")[0].strip(), {}))]
        if not faltam:
            print(f"  {arq.stem:10s} ok ({len(atual)} município(s))")
            continue
        print(f"  {arq.stem:10s} faltando: {', '.join(faltam)}")
        if not a.gravar:
            continue
        novos = []
        for c in cidades:
            nome = c.split("/")[0].strip()
            if completo(atual.get(nome, {})):
                novos.append(atual[nome]); continue
            m = desc.resolve(c)
            b = desc.numeros_da_cidade(m)
            novos.append(b)
            pop = (b.get("populacao_estimada") or {}).get("valor")
            idd = b.get("idades") or {}
            print(f"             {nome}: {pop} hab · alvo 30-45 = "
                  f"{idd.get('alvo_30_45')} · alvo 9-15 = {idd.get('alvo_9_15')}"
                  + (f" · ⚠ {b['nao_veio']}" if b.get("nao_veio") else ""))
        d["ibge"] = novos
        arq.write_text(json.dumps(d, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
        print(f"             → {arq.relative_to(RAIZ)} atualizado "
              f"({len(d.get('locais', []))} locais intactos)")


if __name__ == "__main__":
    main()
