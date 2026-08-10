#!/usr/bin/env python3
"""
ibge_nacional.py — os números do IBGE para TODOS os municípios do Brasil.

É a régua populacional que faltava antes do Radar: hoje o portal estuda 6
cidades a fundo e não diz nada sobre as outras ~5.560. Este coletor puxa,
numa chamada por variável (`N6[all]`), o que o `descobrir_praca.py` já
puxava cidade a cidade:

  · população estimada (agregado 6579)
  · massa salarial (agregado 5938 — vira renda relativa no funil)
  · Censo 2022 por faixa etária (agregado 9514), só as seis faixas que
    formam os dois alvos: 9-15 (quem usa o aparelho) e 30-45 (quem paga
    e é o alvo maior)

Mesmas contas das praças, para os números baterem entre as telas.

Uso:
    python3 coleta/coletores/ibge_nacional.py            # mostra sem gravar
    python3 coleta/coletores/ibge_nacional.py --salvar   # → dados/serie/ibge_municipios.jsonl
"""
import argparse, json, pathlib, subprocess, sys, time
import datetime as dt

RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent
SERIE = RAIZ/"dados"/"serie"
IBGE = "https://servicodados.ibge.gov.br"

# códigos do agregado 9514 (Censo 2022, classificação 287 = idade)
FAIXAS = {"93084": "5a9", "93085": "10a14", "93086": "15a19",
          "93089": "30a34", "93090": "35a39", "93091": "40a44"}


def curl(url, timeout=180, tentativas=3):
    erro = None
    for t in range(tentativas):
        if t:
            time.sleep(2*t)
        r = subprocess.run(["curl", "-sS", "-m", str(timeout), "--retry", "2",
                            "-H", "User-Agent: Mozilla/5.0", url],
                           capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout
        erro = (r.stderr or "sem resposta")[:120]
    raise RuntimeError(f"curl falhou: {erro}")


def serie_nacional(agregado, variavel, periodo="-1"):
    """Uma variável para todos os municípios. Retorna {ibge_id: (valor, ano)}."""
    d = json.loads(curl(f"{IBGE}/api/v3/agregados/{agregado}/periodos/{periodo}"
                        f"/variaveis/{variavel}?localidades=N6%5Ball%5D"))
    fora = {}
    for s in d[0]["resultados"][0]["series"]:
        ano, val = list(s["serie"].items())[-1]
        if val in (None, "", "-", "...", "X"):
            continue
        loc = s["localidade"]
        fora[int(loc["id"])] = (int(float(val)), ano, loc["nome"])
    return fora


def faixa_nacional(cod):
    """Uma faixa etária do Censo para todos os municípios."""
    d = json.loads(curl(f"{IBGE}/api/v3/agregados/9514/periodos/2022/variaveis/93"
                        f"?localidades=N6%5Ball%5D&classificacao=287%5B{cod}%5D"))
    fora = {}
    for s in d[0]["resultados"][0]["series"]:
        val = list(s["serie"].values())[-1]
        if val in (None, "", "-", "...", "X"):
            continue
        fora[int(s["localidade"]["id"])] = int(float(val))
    return fora


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()
    hoje = dt.date.today().isoformat()

    print("  municípios (nome/UF)…")
    munis = {int(m["municipio-id"]): m for m in json.loads(
        curl(f"{IBGE}/api/v1/localidades/municipios?view=nivelado"))}
    print(f"    {len(munis)}")

    print("  população estimada (6579)…")
    pop = serie_nacional(6579, 9324)
    print(f"    {len(pop)}")
    print("  massa salarial (5938)…")
    massa = serie_nacional(5938, 37)
    print(f"    {len(massa)}")

    idades = {}
    for cod, nome in FAIXAS.items():
        print(f"  censo 2022 · faixa {nome}…")
        idades[nome] = faixa_nacional(cod)
        print(f"    {len(idades[nome])}")

    linhas = []
    for mid, m in sorted(munis.items()):
        p = pop.get(mid)
        if not p:
            continue
        f = {n: idades[n].get(mid) for n in FAIXAS.values()}
        tem_idade = all(v is not None for v in f.values())
        jovem = (round(f["5a9"]*0.2 + f["10a14"] + f["15a19"]*0.2)
                 if tem_idade else None)
        adulto = (f["30a34"] + f["35a39"] + f["40a44"]) if tem_idade else None
        ms = massa.get(mid)
        linhas.append({
            "snapshot_date": hoje, "ibge_id": mid,
            "municipio": m["municipio-nome"], "uf": m["UF-sigla"],
            "populacao": p[0], "populacao_ano": p[1],
            "massa_salarial_mil_reais": ms[0] if ms else None,
            "alvo_9_15": jovem, "alvo_30_45": adulto,
            "fonte": "ibge agregados 6579/5938/9514",
        })

    sem_idade = sum(1 for x in linhas if x["alvo_9_15"] is None)
    sem_massa = sum(1 for x in linhas if x["massa_salarial_mil_reais"] is None)
    print(f"\n  {len(linhas)} municípios · {sem_idade} sem faixa etária · "
          f"{sem_massa} sem massa salarial")
    if not linhas:
        sys.exit("  ✗ nada coletado — zero silencioso é falha")

    if a.salvar:
        # uma foto por rodada; o arquivo é série, o funil lê a mais recente
        with (SERIE/"ibge_municipios.jsonl").open("a", encoding="utf-8") as f:
            for x in linhas:
                f.write(json.dumps(x, ensure_ascii=False) + "\n")
        print(f"  → dados/serie/ibge_municipios.jsonl (+{len(linhas)})")


if __name__ == "__main__":
    main()
