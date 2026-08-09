#!/usr/bin/env python3
"""
inteligencia.py — a leitura que vem DEPOIS da coleta, sempre.

Regra do projeto: coleta sem inteligência é dado parado. Toda praça coletada
roda isto antes de virar dossiê. Não é opcional e não é etapa avulsa.

O que ele faz, e por que cada coisa:

  1. RITMO CERTO — avaliações novas por mês. Vem de DUAS fontes, e a ordem
     importa:
       · o contador do Google entre duas coletas — observação direta, é a que
         vale. Precisa de duas coletas com 14+ dias de intervalo.
       · o intervalo da amostra — estimativa, usada só quando não há duas
         coletas. Marcada com ~estimado na tela.
     As duas só concordam quando a clínica é rápida de verdade. Na matriz de
     Londrina a amostra dizia 51,7/mês e o contador subiu 3 em 23 dias. Quando
     divergem, o script mostra o contador e avisa o que a amostra dizia.

  2. O PLACAR — quem lidera em volume e em ritmo, e onde a unidade cai.

  3. AS UNIDADES DA MESMA MARCA — quando há mais de uma na praça, é a
     comparação mais valiosa que existe: mercado, preço e marca ficam
     controlados, e o que sobra é a unidade.

  4. AS HIPÓTESES VIVAS — recalcula as correlações que o projeto já levantou,
     com os dados novos. Uma praça nova pode matar um padrão antigo, e isso
     é resultado, não problema.

  5. A ASSINATURA DA AVALIAÇÃO — tamanho e emoji. Avaliação curta em massa é
     sinal de campanha ("pediu na cadeira"). Sinal, não prova.

  6. O QUE PESA CONTRA — todo achado sai com o contraexemplo do lado. Achado
     sem contraexemplo procurado não é achado, é torcida.

Uso:
    python3 scripts/inteligencia.py --praca cuiaba
    python3 scripts/inteligencia.py --todas
"""
import argparse, json, math, pathlib, re, statistics as st, sys, unicodedata
from collections import defaultdict, Counter

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SERIE = RAIZ/"dados"/"serie"
IDENT = RAIZ/"dados"/"identidade"
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
NOMES = re.compile(r'\b(?:dr|dra|doutor|doutora)\.?\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+)')


def jsonl(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []


def correl(xs, ys):
    if len(xs) < 3:
        return None
    mx, my = st.mean(xs), st.mean(ys)
    den = math.sqrt(sum((a-mx)**2 for a in xs) * sum((b-my)**2 for b in ys))
    return (sum((a-mx)*(b-my) for a, b in zip(xs, ys))/den) if den else None


def forca(r):
    """Traduz o r para português. Ninguém na diretoria lê coeficiente."""
    if r is None:
        return "não dá para dizer — poucos casos"
    a = abs(r)
    if a < 0.2:  return "não separa nada"
    if a < 0.4:  return "quase não separa"
    if a < 0.6:  return "separa um pouco"
    if a < 0.8:  return "separa bem"
    return "separa muito"


def carrega(praca):
    ident = json.loads((IDENT/f"{praca}.json").read_text(encoding="utf-8"))
    locais = {l["local_id"]: l for l in ident["locais"]}
    places = [p for p in jsonl(SERIE/"places.jsonl") if p.get("praca_id") == praca]
    ult, hist = {}, defaultdict(dict)
    for p in places:                       # a coleta mais recente de cada local
        k = p["local_id"]
        if k not in ult or p["snapshot_date"] >= ult[k]["snapshot_date"]:
            ult[k] = p
        v = p.get("avaliacoes", p.get("avaliacoes_total"))
        if v is not None:
            hist[k][p["snapshot_date"]] = v
    revs = defaultdict(list)
    for r in jsonl(SERIE/"reviews.jsonl"):
        if r.get("praca_id") == praca:
            revs[r["local_id"]].append(r)
    return ident, locais, ult, revs, hist


def ritmo_por_delta(hist):
    """O ritmo confiável: quanto o contador do Google subiu entre duas coletas.

    É observação direta, sem interpretar data de avaliação. Vale mais que a
    conta pelo intervalo da amostra, que só bate com este quando a clínica é
    rápida de verdade — na matriz de Londrina a conta por data dizia 51,7/mês
    e o contador subiu 3 em 23 dias. Uma das duas está errada, e a que não
    depende de parsing é a que fica.
    """
    ds = sorted(hist)
    if len(ds) < 2:
        return None, None
    import datetime as dt
    d0, d1 = ds[0], ds[-1]
    dias = (dt.date.fromisoformat(d1) - dt.date.fromisoformat(d0)).days
    if dias < 14:                       # janela curta demais: ruído vira sinal
        return None, None
    return round((hist[d1]-hist[d0])/(dias/30.4), 1), dias


def meses_sustentados(ds, hoje=None):
    """Quantos meses seguidos a clínica manteve movimento até hoje.

    É a métrica que separa operação de campanha, e ela só apareceu quando a
    gente foi fundo: quase toda clínica que parecia rápida em Cuiabá, Feira e
    Prudente é campanha de poucos meses. A Odontologia Prado fazia 1 avaliação
    por mês até março e explodiu — pelo intervalo curto ela "ganhava" da
    OrthoDontic; em doze meses faz 23,8 contra 43,8.

    Velocidade responde "quanto"; isto responde "há quanto tempo" — e é o
    segundo que diz se dá para copiar.
    """
    import datetime as dt
    from collections import Counter
    if not ds:
        return 0
    hoje = hoje or dt.date.today()
    c = Counter(d[:7] for d in ds)
    if not c:
        return 0
    tipico = st.median([v for v in c.values()]) or 1
    seguidos, ano, mes = 0, hoje.year, hoje.month
    mes -= 1                                   # o mês corrente está incompleto
    if mes == 0:
        ano, mes = ano-1, 12
    for _ in range(36):
        if c.get(f"{ano:04d}-{mes:02d}", 0) < max(2, tipico*0.3):
            break
        seguidos += 1
        mes -= 1
        if mes == 0:
            ano, mes = ano-1, 12
    return seguidos


def perfil_mensal(ds):
    """Rajada ou ritmo? Um número de velocidade sozinho não distingue.

    O COP Tomba, em Feira, fez 95 avaliações em maio e 5 nos dois meses
    seguintes. A média mensal dele parece saudável; a clínica está parada
    desde junho. Já a Odontologia Prado, em Cuiabá, faz 23 · 60 · 17 —
    isso é máquina ligada.

    Devolve quantos meses tiveram movimento, e o quanto o maior mês pesa
    sobre o total. Um mês concentrando mais de 60% é rajada.
    """
    from collections import Counter
    if len(ds) < 8:
        return None
    c = Counter(d[:7] for d in ds)
    meses = sorted(c)
    pico = max(c.values())
    concentracao = pico/len(ds)
    ativos = sum(1 for m in meses if c[m] >= max(2, pico*0.15))
    return {"meses": len(meses), "meses_ativos": ativos,
            "concentracao_pico": round(concentracao, 2),
            "rajada": concentracao >= 0.6 and len(meses) > 1,
            "ultimo_mes": meses[-1], "pico_mes": max(c, key=c.get)}


def metricas(lid, loc, pl, rs, hist=None):
    # As coletas antigas gravavam 'avaliacoes_total' e data com hora junto.
    # O esquema mudou; a leitura tem que aceitar os dois, senão a praça
    # antiga some do relatório sem avisar.
    ds = sorted(str(r["data"])[:10] for r in rs if r.get("data"))
    txt = [r["texto"] for r in rs if r.get("tem_texto") and r.get("texto")]
    m = {"local_id": lid, "nome": loc.get("nome"), "papel": loc.get("papel"),
         "total": pl.get("avaliacoes", pl.get("avaliacoes_total")), "nota": pl.get("nota"),
         "amostra": len(ds), "textos": len(txt),
         "censurada": pl.get("amostra_censurada")}
    if len(ds) > 1:
        import datetime as dt
        d0 = dt.date.fromisoformat(ds[0]); d1 = dt.date.fromisoformat(ds[-1])
        dias = max((d1-d0).days, 1)
        m["ritmo_data"] = round(len(ds)/(dias/30.4), 1)   # estimativa pela amostra
        # Amostra de poucos dias não vira taxa mensal. O COP de Feira devolveu
        # 100 avaliações em 5 dias e a conta deu 608/mês, número que nenhuma
        # clínica sustenta. Sabemos que está numa campanha; não sabemos o ritmo.
        m["amostra_curta"] = dias < 21
        m["ritmo_ingenuo"] = round(len(ds)/12, 1)         # o que enganaria
        m["ritmo"] = m["ritmo_data"]; m["ritmo_fonte"] = "amostra"
        m["primeira"], m["ultima"], m["dias"] = ds[0], ds[-1], dias
    d_ritmo, d_dias = ritmo_por_delta(hist or {})
    if d_ritmo is not None:                # o contador do Google manda
        m["ritmo"] = max(d_ritmo, 0.0); m["ritmo_fonte"] = f"contador ({d_dias}d)"
        m["ritmo_delta"] = d_ritmo
    m["perfil"] = perfil_mensal(ds)
    m["meses_sustentados"] = meses_sustentados(ds)
    m["responde_pct"] = round(100*sum(1 for r in rs if r.get("respondida"))/max(len(rs), 1))
    if txt:
        m["mediana_car"] = round(st.median(len(t) for t in txt))
        m["curtas_pct"] = round(100*sum(1 for t in txt if len(t) <= 40)/len(txt))
        m["emoji_pct"] = round(100*sum(1 for t in txt if EMOJI.search(t))/len(txt))
        m["cita_nome_pct"] = round(100*sum(1 for t in txt if NOMES.search(t))/len(txt))
    return m


def roda(praca):
    ident, locais, ult, revs, hist = carrega(praca)
    M = [metricas(k, locais[k], ult[k], revs.get(k, []), hist.get(k))
         for k in ult if k in locais]
    M = [m for m in M if m.get("ritmo") is not None]
    M.sort(key=lambda x: -x["ritmo"])
    if not M:
        print(f"  {praca}: sem avaliação com data — nada a ler."); return None

    # a UF vem antes do nome: existe Palmas no TO e no PR
    rot = ident.get("rotulo") or ident.get("nome", praca)
    print(f"\n{'='*74}\n  INTELIGÊNCIA — {rot}  ({len(M)} clínicas)\n{'='*74}")

    print("\n## 1 · O PLACAR PELO RITMO")
    print("  'meses' = meses seguidos com movimento. Ritmo diz quanto; meses diz")
    print("  se é operação ou campanha. Campanha não se copia.")
    print("  O '+' quer dizer piso: a amostra encheu antes de alcançar o passado.")
    print(f"  {'ritmo':>6s} {'meses':>6s} {'total':>6s} {'nota':>5s} {'resp':>5s}  clínica")
    for m in M:
        marca = "★" if m["papel"] == "proprio" else " "
        fonte = m.get("ritmo_fonte", "amostra")
        alerta = "" if fonte.startswith("contador") else "  ~estimado"
        if m.get("amostra_curta") and not fonte.startswith("contador"):
            alerta = f"  ⚠ amostra de {m.get('dias')}d — em campanha, ritmo desconhecido"
        if m.get("ritmo_delta") is not None and m.get("ritmo_data") is not None \
           and m["ritmo_data"] > max(m["ritmo_delta"], 0.5)*3:
            alerta = "  ⚠ amostra dizia " + f"{m['ritmo_data']:.0f}"
        pf = m.get("perfil") or {}
        if pf.get("rajada"):
            alerta = f"  ⚡ RAJADA ({pf['concentracao_pico']:.0%} num mês só, pico {pf['pico_mes']})"
        ms = m.get("meses_sustentados", 0)
        # Quando a amostra bateu no teto, ela não alcança o passado inteiro:
        # a clínica rápida "perde" meses só porque enche a cota mais cedo.
        # Por isso o número vira um piso, marcado com +.
        msx = f"{ms}+" if m.get("censurada") and ms else str(ms)
        print(f"  {m['ritmo']:>6.1f} {msx:>6s} {str(m['total']):>6s} {str(m['nota']):>5s} "
              f"{m['responde_pct']:>4d}% {marca} {(m['nome'] or '')[:32]}{alerta}")

    prop = [m for m in M if m["papel"] == "proprio"]
    if prop:
        lider = M[0]
        print(f"\n  A unidade líder da praça faz {lider['ritmo']:.1f}/mês.")
        for m in prop:
            pos = M.index(m)+1
            print(f"  {m['nome'][:40]:40s} {m['ritmo']:>5.1f}/mês · {pos}º de {len(M)}")

    if len(prop) > 1:
        print("\n## 2 · MESMA MARCA, MESMA CIDADE — a comparação que controla tudo")
        prop.sort(key=lambda x: -x["ritmo"])
        alto, baixo = prop[0], prop[-1]
        raz = alto["ritmo"]/baixo["ritmo"] if baixo["ritmo"] else float("inf")
        for m in prop:
            print(f"  {m['ritmo']:>6.1f}/mês · {str(m['total']):>5s} avaliações · nota {m['nota']} · "
                  f"responde {m['responde_pct']}%  {m['nome'][:34]}")
        print(f"\n  {raz:.0f}× de diferença dentro da mesma marca e da mesma cidade.")
        print("  Mercado, preço, marca e concorrência estão controlados.")
        print("  O que sobra é a unidade — e o que uma faz, outra copia.")

    print("\n## 3 · AS HIPÓTESES, TESTADAS DE NOVO")
    testes = [("responder avaliação faz crescer", "responde_pct"),
              ("nota alta acompanha ritmo", "nota"),
              ("avaliação curta acompanha ritmo", "curtas_pct")]
    for rotulo, campo in testes:
        pares = [(m["ritmo"], float(m[campo])) for m in M if m.get(campo) is not None]
        r = correl([a for a, _ in pares], [b for _, b in pares])
        print(f"  {rotulo:36s} r = {r:+.2f}  → {forca(r)}" if r is not None
              else f"  {rotulo:36s} sem dados suficientes")

    print("\n## 4 · O QUE PESA CONTRA")
    contra = []
    curtas = [m for m in M if m.get("curtas_pct") is not None]
    for m in sorted(curtas, key=lambda x: -x["curtas_pct"])[:3]:
        if m["ritmo"] < 10:
            contra.append(f"{m['nome'][:30]} tem {m['curtas_pct']}% de avaliação curta e ritmo {m['ritmo']:.1f} — "
                          "curta não produz ritmo sozinha")
    for m in M[:3]:
        if m["responde_pct"] == 0:
            contra.append(f"{m['nome'][:30]} lidera em ritmo respondendo 0% das avaliações")
    for m in M:
        if m["responde_pct"] >= 80 and m["ritmo"] < 10:
            contra.append(f"{m['nome'][:30]} responde {m['responde_pct']}% e faz só {m['ritmo']:.1f}/mês")
    for c in (contra or ["(nada encontrado — o que é motivo de desconfiança, não de comemoração)"]):
        print(f"  · {c}")

    # A âncora é o place_id. Se dois local_id apontam para o mesmo lugar, a
    # clínica aparece duas vezes no placar e as contas saem erradas sem avisar.
    vistos = {}
    for m in M:
        pid = (ult.get(m["local_id"]) or {}).get("place_id")
        if pid:
            vistos.setdefault(pid, []).append(m["local_id"])
    dobrados = {k: v for k, v in vistos.items() if len(v) > 1}
    if dobrados:
        print("\n  ⚠ MESMO LUGAR EM DOIS REGISTROS — o placar está contando duplicado:")
        for pid, lids in dobrados.items():
            print(f"    {pid} → {', '.join(lids)}")

    # A varredura pode perder uma unidade da própria rede — foi assim que
    # Feira ficou com uma ficha fantasma solta e Contagem quase ganhou uma
    # unidade que não era nossa. A lista oficial do site é a conferência.
    try:
        sys.path.insert(0, str(RAIZ/"coleta"/"coletores"))
        import unidades_da_rede as _rede
        oficiais, quando = _rede.carregar()
        cidades = (json.loads((RAIZ/"dados"/"identidade"/f"{praca}.json")
                              .read_text(encoding="utf-8")).get("cidades") or [])
        esperadas = [u for c in cidades for u in _rede.tem_unidade(c, oficiais)]
        nossos = [m for m in M if m["papel"] == "proprio"]
        if oficiais and len(esperadas) != len(nossos):
            print(f"\n  ⚠ A REDE PUBLICA {len(esperadas)} UNIDADE(S) NESTA PRAÇA "
                  f"e o placar tem {len(nossos)} (lista de {quando}):")
            for u in esperadas:
                print(f"    {u['unidade']} — {u['endereco'] or u['situacao']}")
    except Exception as e:
        print(f"\n  ⚠ não consegui conferir com a lista oficial de unidades: {e}")

    # Contador que CAI é avaliação removida — pelo Google ou por alguém. Não é
    # ritmo negativo e não pode virar "-4,0/mês" numa tabela. A unidade de Feira
    # foi de 173 para 170 em 23 dias e ninguém tinha percebido.
    for lid, h in (hist or {}).items():
        ds = sorted(h)
        if len(ds) > 1 and h[ds[-1]] < h[ds[0]]:
            import datetime as _dt
            dias = (_dt.date.fromisoformat(ds[-1]) - _dt.date.fromisoformat(ds[0])).days
            print(f"\n  ⚠ O CONTADOR CAIU em {locais.get(lid, {}).get('nome', lid)}: "
                  f"{h[ds[0]]} → {h[ds[-1]]} em {dias} dias.")
            print("    Avaliação removida, ficha mexida ou fusão de fichas. Não é "
                  "ritmo negativo — é fato para conferir na ficha.")

    print("\n## 5 · O QUE ISSO NÃO VÊ")
    off = [o for o in jsonl(SERIE/"midia_offline.jsonl") if o.get("praca_id") == praca]
    if off:
        nm = [o["canal"] for o in off if o["status"] == "nao_medido"]
        print(f"  {len(off)} canais declarados, {len(nm)} não medidos: {', '.join(nm[:6])}")
    else:
        print("  ⚠ NENHUM canal offline declarado para esta praça.")
        print("    Sem isso, 'a unidade está parada' pode ser falso — ela pode estar no rádio.")
    print("  A pergunta que resolve: \"o que vocês fazem de mídia que não está na internet?\"")
    return M


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--praca")
    ap.add_argument("--todas", action="store_true")
    a = ap.parse_args()
    pracas = ([p.stem for p in sorted(IDENT.glob("*.json"))] if a.todas
              else [a.praca] if a.praca else None)
    if not pracas:
        raise SystemExit("use --praca <id> ou --todas")
    for p in pracas:
        roda(p)
    print()


if __name__ == "__main__":
    main()
