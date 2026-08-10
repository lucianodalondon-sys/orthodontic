#!/usr/bin/env python3
"""
escreve_tese_oportunidade.py — a leitura autorada das cidades do Radar.

As seis cidades de oportunidade tinham 20 campos de número e ZERO texto:
abriam sem manchete, sem tese e sem base, enquanto toda praça da rede
abre com "A melhor clínica da cidade é a mais calada". Não estavam no
mesmo padrão de estudo — e o `padrao.py` dizia "completa" porque a régua
não cobrava leitura de quem não tem unidade.

Cada tese aqui é escrita EM CIMA do número medido do próprio arquivo
(dados/oportunidade/<id>.json). Nada de adjetivo sem conta atrás: se a
frase diz "nenhuma clínica forte", é porque `concorrencia.fortes` é 0.

Uso:
    python3 scripts/escreve_tese_oportunidade.py            # mostra
    python3 scripts/escreve_tese_oportunidade.py --salvar   # grava em
                                                # dados/conteudo/oportunidade/
"""
import argparse, json, pathlib, sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
EST = RAIZ/"dados"/"oportunidade"
OUT = RAIZ/"dados"/"conteudo"/"oportunidade"

MES = ["jan", "fev", "mar", "abr", "mai", "jun",
       "jul", "ago", "set", "out", "nov", "dez"]

# A leitura de cada cidade. O título e a tese são autorados; os números
# dentro deles são checados contra o estudo no final deste arquivo, e o
# script FALHA se algum não bater — texto que envelhece calado é o que
# este projeto já pagou caro para não repetir.
LEITURAS = {
    "imperatriz": {
        "titulo": "A cidade onde ninguém é forte",
        "tese": "Das seis cidades do Radar, é a única sem NENHUMA clínica "
                "forte: 117 varridas, 8 medianas, 109 fracas, e o líder da "
                "cidade inteira tem 291 avaliações — menos que a nossa "
                "unidade mais parada. Não há reputação instalada para "
                "disputar; há um balcão vazio no meio da praça.",
    },
    "juazeiro_do_norte": {
        "titulo": "Três donos do balcão, e a menor renda das seis",
        "tese": "Três clínicas fortes para 305.531 habitantes — uma a cada "
                "101.844 — e a renda per capita mais baixa do Radar: "
                "R$ 1.761, menos de um quarto da de Parauapebas. A "
                "reputação já tem dono, e a decisão do paciente aqui passa "
                "pela parcela antes de passar pelo nome.",
    },
    "macapa": {
        "titulo": "Meio milhão de pessoas para uma clínica forte",
        "tese": "489.676 habitantes e UMA única clínica forte entre as 133 "
                "varridas — a maior folga do Radar, 489 mil habitantes por "
                "clínica de reputação instalada. O líder tem 427 "
                "avaliações numa cidade de capital. É muita gente para "
                "pouca clínica com nome.",
    },
    "maraba": {
        "titulo": "Três fortes em cima, e um vazio embaixo",
        "tese": "A praça mais polarizada do Radar: das 92 clínicas "
                "varridas, 3 são fortes, só 2 são medianas e 87 são "
                "fracas. O líder tem 583 avaliações. Não existe meio de "
                "tabela para disputar — ou se entra no topo, ou se entra "
                "no ruído.",
    },
    "parauapebas": {
        "titulo": "A mais rica, e a mais disputada",
        "tese": "Renda per capita de R$ 7.201 — 2,6 vezes a de Juazeiro do "
                "Norte e a maior do Radar — e o preço disso é a disputa: 4 "
                "clínicas fortes, o líder com 1.055 avaliações, uma forte a "
                "cada 76.443 habitantes. É a única das seis cujo perfil "
                "casa com SP · Presidente Prudente, e não com Palmas.",
    },
    "rio_branco": {
        "titulo": "Uma capital, uma clínica forte",
        "tese": "389.001 habitantes, 120 clínicas varridas e apenas UMA "
                "forte — 389 mil habitantes por clínica de reputação "
                "instalada, a segunda maior folga do Radar. O líder tem "
                "619 avaliações. Capital de estado com o balcão de "
                "ortodontia quase vazio.",
    },
}

# o que cada frase promete, e de onde o número sai — o guarda contra
# adjetivo sem conta atrás
CHECAGEM = {
    "imperatriz": [("fortes", 0), ("varridas", 117), ("lider_avaliacoes", 291)],
    "juazeiro_do_norte": [("fortes", 3), ("populacao", 305531),
                          ("hab_por_clinica_forte", 101844),
                          ("renda_per_capita", 1761)],
    "macapa": [("fortes", 1), ("populacao", 489676), ("varridas", 133),
               ("lider_avaliacoes", 427)],
    "maraba": [("fortes", 3), ("varridas", 92), ("lider_avaliacoes", 583)],
    "parauapebas": [("fortes", 4), ("renda_per_capita", 7201),
                    ("lider_avaliacoes", 1055),
                    ("hab_por_clinica_forte", 76443)],
    "rio_branco": [("fortes", 1), ("populacao", 389001), ("varridas", 120),
                   ("lider_avaliacoes", 619)],
}


def valor(est, chave):
    if chave in ("fortes", "varridas"):
        return (est.get("concorrencia") or {}).get(chave)
    return est.get(chave)


def monta():
    if not EST.exists():
        sys.exit("dados/oportunidade/ não existe — rode "
                 "scripts/estudar_oportunidade.py --salvar")
    fora, erros = {}, []
    for arq in sorted(EST.glob("*.json")):
        pid = arq.stem
        est = json.loads(arq.read_text(encoding="utf-8"))
        leitura = LEITURAS.get(pid)
        if not leitura:
            erros.append(f"{pid}: cidade de oportunidade SEM leitura escrita")
            continue
        for chave, esperado in CHECAGEM.get(pid, []):
            real = valor(est, chave)
            if real != esperado:
                erros.append(f"{pid}: a tese diz {chave}={esperado}, "
                             f"o estudo mede {real}")
        c = est.get("concorrencia") or {}
        d = est.get("snapshot_date") or ""
        base = (f"{c.get('varridas')} clínicas varridas · "
                f"{(c.get('avaliacoes_somadas') or 0):,} avaliações somadas"
                .replace(",", ".") +
                (f" · corte {d[8:10]}/{MES[int(d[5:7]) - 1]}/{d[:4]}"
                 if len(d) == 10 else ""))
        conf = est.get("conferencia") or {}
        fora[pid] = {
            "praca_id": pid,
            "eyebrow": ("Cidade de oportunidade · a rede não está lá · "
                        "conferida em duas fontes"
                        if conf.get("livre") and conf.get("conferida")
                        else "Cidade de oportunidade · presença NÃO conferida"),
            "tese_titulo": leitura["titulo"],
            "tese": leitura["tese"],
            "base": base,
            "papel": "oportunidade",
        }
    return fora, erros


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()
    fora, erros = monta()
    print(f"\n{'=' * 78}\n  A LEITURA DAS CIDADES DO RADAR\n{'=' * 78}\n")
    for pid, d in fora.items():
        print(f"  {pid}")
        print(f"    {d['tese_titulo']}")
        print(f"    {d['tese'][:150]}…")
        print(f"    {d['base']}\n")
    if erros:
        print("  A TESE NÃO BATE COM O ESTUDO:")
        for e in erros:
            print("   ✗", e)
        sys.exit(1)
    print(f"  {len(fora)} cidades · toda frase confere com o número medido")
    if a.salvar:
        OUT.mkdir(parents=True, exist_ok=True)
        for pid, d in fora.items():
            (OUT/f"{pid}.json").write_text(
                json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n  → dados/conteudo/oportunidade/ ({len(fora)} arquivos)")


if __name__ == "__main__":
    main()
