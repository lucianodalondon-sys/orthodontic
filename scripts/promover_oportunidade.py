#!/usr/bin/env python3
"""
promover_oportunidade.py — a praça de oportunidade vira praça de verdade.

O erro que este arquivo conserta: eu tratei praça de oportunidade como um
produto separado, com um estudo próprio e mais raso — IBGE, concorrência e a
gêmea, três seções. O dossiê de Mafra tem dezoito.

O que faltou não é detalhe, é a metade que decide: **quem fala com a cidade,
com quantos seguidores; o que a cidade diz, com as palavras dela; qual a ferida
da praça; que canal não existe e portanto está vago; o que jamais dizer ali.**
Sem isso não há entrada de unidade nova — há uma planilha de população.

A correção é arquitetural, não cosmética: **praça de oportunidade é praça sem
unidade.** Mesmo `entrar.py`, mesmos coletores, mesmo dossiê. Só não tem
unidade própria dentro, e por isso as leituras que dependem de unidade a
ignoram.

Este script faz a ponte: pega o estudo já pago (a varredura de 90 a 130
clínicas, que custou dinheiro) e escreve a identidade da praça com os
concorrentes já ancorados por place_id — para o coletor de avaliação não
começar do zero.

Uso:
    python3 scripts/promover_oportunidade.py --todas
    python3 scripts/promover_oportunidade.py --praca macapa --forcar
"""
import argparse, json, pathlib, re, sys, unicodedata
import datetime as dt

RAIZ = pathlib.Path(__file__).resolve().parent.parent
IDENT = RAIZ/"dados"/"identidade"
ALVOS = RAIZ/"coleta"/"alvos"
OPORT = RAIZ/"dados"/"oportunidade"
SERIE = RAIZ/"dados"/"serie"
QUANTOS = 14      # quantos concorrentes ancorar — o mesmo da varredura de praça


def slug(s):
    s = unicodedata.normalize("NFKD", str(s or ""))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")[:26]


def varredura(praca_id):
    """A varredura já gravada, clínica por clínica. Não recoleta nada."""
    arq = SERIE/"categoria_oportunidade.jsonl"
    if not arq.exists():
        return []
    linhas = [json.loads(l) for l in arq.read_text(encoding="utf-8").splitlines()
              if l.strip()]
    minhas = [r for r in linhas if r.get("praca_id") == praca_id]
    if not minhas:
        return []
    corte = max(r["snapshot_date"] for r in minhas)
    vistos = {r["place_id"]: r for r in minhas if r["snapshot_date"] == corte}
    return sorted(vistos.values(), key=lambda r: -(r.get("avaliacoes") or 0))


def monta(est, hoje):
    praca_id = est["praca_id"]
    cidade = est["cidade"]
    nome, uf = [x.strip() for x in cidade.split("/")]
    cs = varredura(praca_id)

    ident = {
        "praca_id": praca_id,
        "nome": nome,
        "cidades": [cidade],
        "uf": [uf],
        "rotulo": est["rotulo"],
        "cidades_rotulo": [est["rotulo"]],
        "criada_em": hoje,
        # A marca que faz o resto do sistema saber que aqui NÃO tem unidade.
        # Sem ela, o placar da rede passaria a contar praça sem unidade como
        # unidade parada — e "5 pararam" viraria "11 pararam", mentindo.
        "tipo": "oportunidade",
        "sem_unidade": True,
        "conferencia_de_unidade": est.get("conferencia"),
        "ibge": [est.get("cidade_numeros")] if est.get("cidade_numeros") else [],
        "nota_geografia": "PREENCHER: por que esta cidade é uma praça só, e até "
                          "onde vai o raio real de onde viria o paciente.",
        "por_que_esta_praca": (est.get("gemea") or {}).get("frase")
                              or "praça livre encontrada pelo Radar de Oportunidade",
        "gemea": est.get("gemea"),
        "locais": [
            {"local_id": slug(r.get("nome")) or f"local_{i}",
             "papel": "concorrente",
             "nome": r.get("nome"),
             "tipo_concorrente": "PREENCHER",
             "place_id": r.get("place_id"),
             "avaliacoes_google": r.get("avaliacoes"),
             "nota_google": r.get("nota"),
             "endereco": r.get("endereco"),
             "site": r.get("site") or "",
             "place_id_origem": f"varredura do radar {r.get('snapshot_date')}"}
            for i, r in enumerate(cs[:QUANTOS])
        ],
    }
    return ident


def alvos_yaml(ident):
    """O esqueleto de alvos, com os nove tipos de canal por preencher.

    A etapa dos canais é HUMANA e é onde o estudo ganha ou perde: em Mafra
    foram oito canais e três lacunas — 'não existe página de humor, não existe
    mãe-influencer, não existe criador de vídeo local'. Quem chega primeiro
    nesses três fala sozinho. Nenhuma busca automática conclui isso."""
    TIPOS = [
        ("voz_da_cidade", "o perfil que a cidade inteira segue"),
        ("jornal_local", "o portal/jornal que pauta a conversa"),
        ("prefeitura", "a agenda pública"),
        ("mae", "a mãe-influencer — a decisora do aparelho"),
        ("humor", "a página de humor, que é a voz afetiva"),
        ("esporte_base", "a escolinha de 9-15 — o público exato, com os pais na arquibancada"),
        ("gastronomia", "o perfil-indicador de consumo"),
        ("radio", "a mídia da mãe e da avó"),
        ("classificados", "onde o povão compra e comenta"),
    ]
    L = [f"# ALVOS DE COLETA — {ident['praca_id']}  (PRAÇA DE OPORTUNIDADE)",
         f"# Esqueleto gerado em {ident['criada_em']}.",
         "# A etapa 2 (os canais da cidade) é HUMANA e é onde o estudo se decide.",
         "# Ver coleta/NOVA-PRACA.md\n",
         f"praca_id: {ident['praca_id']}",
         f"cidades: {json.dumps(ident['cidades'], ensure_ascii=False)}",
         "sem_unidade: true",
         "alvos:"]
    for l in ident["locais"][:8]:
        L += [f"  - name: {l['local_id']}_google", "    layer: concorrente",
              "    platform: google", f"    query: \"{l['nome']}\"",
              f"    place_id: {l['place_id']}", "    status: roda"]
    L.append("\n# ---- PREENCHER À MÃO: os canais da cidade ----")
    for tipo, oque in TIPOS:
        L += [f"  # - name: {tipo}_ig            # {oque}",
              "  #   layer: territorio", "  #   platform: instagram",
              "  #   handle: \"\"", "  #   status: pendente"]
    L.append("\n# E ANOTE OS QUE NÃO EXISTEM. Canal que falta é território vago —")
    L.append("# em Mafra faltavam três, e é o achado mais acionável do dossiê.")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--praca", action="append", default=[])
    ap.add_argument("--todas", action="store_true")
    ap.add_argument("--forcar", action="store_true",
                    help="reescreve a identidade mesmo se já existir")
    a = ap.parse_args()

    alvos = list(a.praca)
    if a.todas:
        alvos = sorted(p.stem for p in OPORT.glob("*.json"))
    if not alvos:
        sys.exit("use --praca <id> ou --todas")

    hoje = dt.date.today().isoformat()
    IDENT.mkdir(parents=True, exist_ok=True)
    ALVOS.mkdir(parents=True, exist_ok=True)

    for pid in alvos:
        arq_est = OPORT/f"{pid}.json"
        if not arq_est.exists():
            print(f"  {pid}: sem estudo em dados/oportunidade/"); continue
        est = json.loads(arq_est.read_text(encoding="utf-8"))
        destino = IDENT/f"{pid}.json"

        # A trava que salvou Palmas uma vez: identidade existente tem trabalho
        # humano dentro (o tipo de cada concorrente, os canais conferidos).
        if destino.exists() and not a.forcar:
            antigo = json.loads(destino.read_text(encoding="utf-8"))
            ancorados = [l for l in antigo.get("locais", []) if l.get("place_id")]
            print(f"  {pid}: já existe com {len(ancorados)} locais — "
                  f"não mexi (use --forcar se é isso mesmo)")
            continue

        ident = monta(est, hoje)
        if not ident["locais"]:
            print(f"  {pid}: a varredura não está em categoria_oportunidade.jsonl "
                  f"— rode estudar_oportunidade.py --salvar antes"); continue

        destino.write_text(json.dumps(ident, ensure_ascii=False, indent=2)+"\n",
                           encoding="utf-8")
        (ALVOS/f"{pid}.yaml").write_text(alvos_yaml(ident), encoding="utf-8")
        print(f"  {ident['rotulo']}: identidade criada · "
              f"{len(ident['locais'])} concorrentes ancorados · sem unidade")

    print("\n  Agora estas praças passam pelo MESMO processo das outras:")
    print("    python3 coleta/entrar.py --praca <id> --continuar")
    print("  E o que não é automático continua humano — os canais da cidade,")
    print("  o tipo de cada concorrente, a joia enterrada, as proibições de tom.\n")


if __name__ == "__main__":
    main()
