#!/usr/bin/env python3
"""
o_que_a_cidade_publica.py — a imprensa e o ritmo de quem publica.

O buraco que este script fecha: 644 matérias de imprensa e 3.376 posts de
Instagram estavam coletados, e o portal mostrava **um contador**. "44
matérias" não é inteligência — é prova de que a coleta rodou. A manchete
que interessa nunca chegava à tela, e o ritmo de publicação do
concorrente — que diz quem está acordado e quem parou — nunca foi lido.

DUAS LEITURAS, e elas não se misturam:

IMPRENSA — o que o veículo local publicou. Serve à praça: obra, feira,
escola, economia da cidade. É contexto de mercado, não desempenho de
loja.

RITMO DE PUBLICAÇÃO — quantos posts cada perfil pôs no ar e quando foi o
último. Serve ao confronto: perfil que publicou ontem está vivo; perfil
parado há seis meses não disputa atenção, por mais seguidores que tenha.

O QUE ESTE SCRIPT NÃO FAZ

· Não lê sentimento de matéria nem de post. O que ele diz é o que está
  escrito no título e a data.
· Não chama engajamento de resultado. Curtida é curtida.
· Não compara perfis de tamanhos diferentes como se fossem iguais: o
  ritmo sai por perfil, com a data da última publicação ao lado.

Uso:
    python3 scripts/o_que_a_cidade_publica.py
    python3 scripts/o_que_a_cidade_publica.py --salvar
"""
import argparse, json, pathlib, sys
import datetime as dt
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from cruzamento import identidades, conta

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SERIE = RAIZ/"dados"/"serie"
SAIDA = RAIZ/"dados"/"portal"/"o_que_a_cidade_publica.json"

MAX_MANCHETES = 12
PARADO_DIAS = 60        # sem publicar há mais que isso = perfil parado


def linhas(nome):
    a = SERIE/f"{nome}.jsonl"
    if not a.exists():
        return []
    return [json.loads(l) for l in a.read_text(encoding="utf-8").split("\n")
            if l.strip()]


# O RSS NÃO FALA ISO. As 644 matérias vêm como "Fri, 11 Oct 2024 07:00:00
# GMT" — formato RFC 822. Ler só os dez primeiros caracteres devolvia None
# em todas, e a tela dizia "0 matérias nos últimos 30 dias" para as treze
# cidades, no dia seguinte à coleta.
_MES = {m: i+1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun",
     "jul", "aug", "sep", "oct", "nov", "dec"])}


def data_de(bruto):
    """A data, venha ela em ISO ou em RFC 822. None quando não dá."""
    t = str(bruto or "").strip()
    if not t:
        return None
    try:
        return dt.date.fromisoformat(t[:10])
    except ValueError:
        pass
    partes = t.replace(",", " ").split()
    for i, x in enumerate(partes):
        if x[:3].lower() in _MES and i >= 1:
            try:
                return dt.date(int(partes[i+1]), _MES[x[:3].lower()],
                               int(partes[i-1]))
            except (ValueError, IndexError):
                return None
    return None


def dias_desde(bruto, hoje):
    d = data_de(bruto)
    return (hoje - d).days if d else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()
    hoje = dt.date.today()

    ident = dict(identidades())
    for arq in sorted((RAIZ/"dados"/"identidade").glob("*.json")):
        ident.setdefault(arq.stem, json.loads(arq.read_text(encoding="utf-8")))

    # ---------- imprensa ----------
    # a mesma matéria reaparece a cada coleta: a chave é o link
    por_link = {}
    for r in sorted(linhas("imprensa"), key=lambda r: r.get("snapshot_date", "")):
        por_link[(r.get("praca_id"), r.get("link"))] = r
    imprensa = defaultdict(list)
    for r in por_link.values():
        imprensa[r.get("praca_id")].append(r)

    # ---------- ritmo de publicação ----------
    por_post = {}
    for r in sorted(linhas("posts"), key=lambda r: r.get("snapshot_date", "")):
        por_post[(r.get("praca_id"), r.get("post_id"))] = r
    ritmo = defaultdict(lambda: defaultdict(list))
    for r in por_post.values():
        if r.get("handle"):
            ritmo[r.get("praca_id")][r["handle"]].append(r)

    pracas = []
    for praca in sorted(set(imprensa) | set(ritmo)):
        eu = ident.get(praca) or {}
        # -- imprensa
        ms = sorted(imprensa.get(praca, []),
                    key=lambda r: (data_de(r.get("publicado"))
                                   or dt.date(1970, 1, 1)), reverse=True)
        materias = [{
            "titulo": r.get("titulo"),
            "veiculo": r.get("veiculo"),
            "link": r.get("link"),
            "publicado": (data_de(r.get("publicado")).isoformat()
                          if data_de(r.get("publicado")) else None),
            "dias": dias_desde(r.get("publicado"), hoje),
        } for r in ms[:MAX_MANCHETES]]
        # CONTAR DENTRO DA LISTA CORTADA É CONTAR ERRADO. A primeira versão
        # contava os recentes entre as 12 que vão para a tela, e todas as
        # treze cidades diziam exatamente "12 matérias nos últimos 30 dias".
        # O total sai de TODAS as matérias; o corte é só de exibição.
        recentes = [r for r in ms
                    if (dias_desde(r.get("publicado"), hoje) or 999) <= 30]

        # -- ritmo, por perfil
        perfis = []
        for handle, ps in ritmo.get(praca, {}).items():
            datas = sorted([str(p.get("data") or "")[:10] for p in ps if p.get("data")],
                           reverse=True)
            ultimo = datas[0] if datas else None
            d = dias_desde(ultimo, hoje) if ultimo else None
            perfis.append({
                "handle": handle,
                "posts_medidos": len(ps),
                "ultimo_post": ultimo,
                "dias_sem_publicar": d,
                "parado": (d is not None and d > PARADO_DIAS),
                "curtidas_medianas": (
                    sorted([p.get("curtidas") or 0 for p in ps])[len(ps)//2]
                    if ps else None),
                "frase": (
                    f"{conta(len(ps), 'post medido', 'posts medidos')}"
                    + (f", último há {conta(d, 'dia')}" if d is not None
                       else ", sem data no último")),
            })
        perfis.sort(key=lambda x: (x["dias_sem_publicar"] is None,
                                   x["dias_sem_publicar"]))
        vivos = [p for p in perfis if not p["parado"]
                 and p["dias_sem_publicar"] is not None]
        parados = [p for p in perfis if p["parado"]]

        pracas.append({
            "praca_id": praca,
            "rotulo": eu.get("rotulo") or eu.get("nome") or praca,
            "imprensa": {
                "medido": bool(ms),
                "total": len(imprensa.get(praca, [])),
                "mostrando": len(materias),
                "recentes_30d": len(recentes),
                "manchete": (
                    f"{conta(len(recentes), 'matéria', 'matérias')} sobre a "
                    f"cidade nos últimos 30 dias, de "
                    f"{conta(len(imprensa.get(praca, [])), 'já lida', 'já lidas')}"
                    if ms else None),
                "porque_vazio": (None if ms else
                                 "nenhuma matéria coletada para esta cidade — "
                                 "ausência de medição, não ausência de imprensa"),
                "materias": materias,
            },
            "ritmo": {
                "medido": bool(perfis),
                "perfis": len(perfis),
                "vivos": len(vivos),
                "parados": len(parados),
                "manchete": (
                    f"{conta(len(vivos), 'perfil publicando', 'perfis publicando')}"
                    f" nos últimos {PARADO_DIAS} dias, "
                    f"{conta(len(parados), 'parado')}"
                    if perfis else None),
                "porque_vazio": (None if perfis else
                                 "nenhum perfil medido nesta cidade"),
                "lista": perfis[:15],
            },
        })

    for p in pracas:
        print(f"\n  {p['rotulo']}")
        print(f"    imprensa: {p['imprensa']['manchete'] or p['imprensa']['porque_vazio']}")
        print(f"    ritmo:    {p['ritmo']['manchete'] or p['ritmo']['porque_vazio']}")

    if not a.salvar:
        print("\n  (--salvar para gravar)")
        return
    SAIDA.write_text(json.dumps({
        "o_que_e": "O que a imprensa local publicou sobre a cidade, e quem "
                   "está publicando — com que ritmo — nas redes.",
        "o_que_nao_e": "Não é leitura de sentimento nem medida de audiência. "
                       "É o que está escrito e a data.",
        "medido_em": hoje.isoformat(),
        "parado_apos_dias": PARADO_DIAS,
        "pracas": pracas,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n  → {SAIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
