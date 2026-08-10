#!/usr/bin/env python3
"""
a_voz_da_cidade.py — o que a cidade fala nos comentários, que não é avaliação.

A diferença que justifica o arquivo
------------------------------------
Quem avalia uma clínica JÁ FOI paciente. Quem comenta no perfil de humor, no
de achadinho, no da prefeitura, é a cidade falando antes de escolher qualquer
coisa. São conversas diferentes, e misturá-las estragaria as duas:

  a avaliação diz  →  como fui tratado
  o comentário diz →  o que a cidade acha caro, de quem ela desconfia,
                      como ela fala, o que a faz rir

Por isso os comentários NÃO entram em reviews.jsonl nem na classificação de
temas de atendimento. Eles têm série própria (comentarios.jsonl) e leitura
própria: vocabulário, preço como assunto, desconfiança, e menção espontânea a
dentista ou aparelho — que é ouro quando aparece, porque ninguém perguntou.

Uso:
    python3 scripts/a_voz_da_cidade.py
    python3 scripts/a_voz_da_cidade.py --praca contagem
    python3 scripts/a_voz_da_cidade.py --salvar
"""
import argparse, json, pathlib, re, sys, unicodedata
from collections import Counter, defaultdict

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ/"scripts"))
from cruzamento import jsonl

PORTAL = RAIZ/"dados"/"portal"

MIN_COMENTARIOS = 80    # abaixo disso é anedota, não leitura de cidade


def sa(s):
    return "".join(c for c in unicodedata.normalize("NFD", s or "")
                   if unicodedata.category(c) != "Mn").lower()


# O que se escuta na conversa da cidade. Sinais, não temas de clínica —
# o classificador de avaliações continua sendo o de reviews.
SINAIS = {
    "fala_de_preco": (
        "Preço como assunto da conversa",
        r"caro|barat|pre[çc]o|desconto|promo[çc]|parcel|valor|paguei|"
        r"sal[áa]rio|dinheiro|custa"),
    "desconfianca": (
        "Desconfiança — golpe, propaganda enganosa, 'não caiam'",
        r"golpe|enganos|enganad|mentira|n[ãa]o caia|cuidado|furada|"
        r"propaganda|fake|vigarist"),
    "dentista_espontaneo": (
        "Dentista ou aparelho citado SEM ninguém perguntar",
        r"dentista|aparelho|ortodont|dente|sorriso|braquete|br[áa]quete"),
    "indicacao_pedida": (
        "Alguém pedindo indicação — 'conhecem algum...?'",
        r"algu[ée]m (conhece|indica|sabe)|indica[çc][ãa]o|onde (tem|acho|encontro)|"
        r"me indiquem|qual o melhor"),
    "humor_local": (
        "A cidade rindo de si mesma — o tom que funciona lá",
        r"kkk|rsrs|haha|😂|🤣|morri|chorando de rir"),
}
RX = {k: re.compile(v[1], re.I) for k, v in SINAIS.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--praca")
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()

    C = jsonl("comentarios")
    if not C:
        sys.exit("dados/serie/comentarios.jsonl vazio — rode "
                 "coleta/coletores/comentarios.py primeiro")

    por = defaultdict(list)
    for c in C:
        por[c.get("praca_id")].append(c)

    saida = []
    for p, cs in sorted(por.items()):
        if a.praca and p != a.praca:
            continue
        com_texto = [c for c in cs if (c.get("texto") or "").strip()]
        ok = len(com_texto) >= MIN_COMENTARIOS

        cont = {}
        exemplos = {}
        for k, rx in RX.items():
            hits = [c for c in com_texto if rx.search(sa(c["texto"]))]
            cont[k] = len(hits)
            # o exemplo mais curtido é o que a cidade validou
            top = sorted(hits, key=lambda c: -(c.get("curtidas") or 0))[:3]
            exemplos[k] = [{"texto": c["texto"][:180],
                            "curtidas": c.get("curtidas"),
                            "no_canal": c.get("handle_do_post"),
                            "tipo_canal": c.get("tipo_canal")} for c in top]

        saida.append({
            "praca_id": p,
            "comentarios_lidos": len(com_texto),
            "base_suficiente": ok,
            "aviso": None if ok else (f"só {len(com_texto)} comentários — abaixo "
                                      f"de {MIN_COMENTARIOS} é anedota, não leitura"),
            "sinais": [{"chave": k, "o_que_e": SINAIS[k][0], "n": cont[k],
                        "pct": round(100*cont[k]/max(len(com_texto), 1), 1),
                        "exemplos": exemplos[k]}
                       for k in SINAIS],
        })

    print(f"\n{'='*76}\n  A VOZ DA CIDADE — {sum(x['comentarios_lidos'] for x in saida)} "
          f"comentários lidos\n{'='*76}")
    for s in saida:
        marca = "" if s["base_suficiente"] else "  ⚠ base fina"
        print(f"\n  {s['praca_id']}  ·  {s['comentarios_lidos']} comentários{marca}")
        for x in s["sinais"]:
            if not x["n"]:
                continue
            print(f"    {x['pct']:>5.1f}%  {x['o_que_e']}")
            for e in x["exemplos"][:1]:
                print(f"            “{e['texto'][:88]}”")

    if a.salvar:
        PORTAL.mkdir(parents=True, exist_ok=True)
        (PORTAL/"voz_da_cidade.json").write_text(json.dumps({
            "o_que_e": "O que a cidade fala nos comentários dos canais locais — "
                       "antes de ser paciente de alguém.",
            "diferenca": "Avaliação é quem já foi tratado. Comentário é a cidade "
                         "conversando: o que acha caro, de quem desconfia, como "
                         "ri. As duas séries não se misturam.",
            "sem_identidade": "Nenhum nome, @ ou foto de quem comentou é guardado.",
            "pracas": saida,
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n  → dados/portal/voz_da_cidade.json")


if __name__ == "__main__":
    main()
