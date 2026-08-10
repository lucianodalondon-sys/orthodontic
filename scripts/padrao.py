#!/usr/bin/env python3
"""
padrao.py — O PADRÃO DA PRAÇA, verificado por máquina.

Por que este arquivo existe
---------------------------
O processo estava escrito em coleta/NOVA-PRACA.md, com quinze etapas bem
detalhadas. E mesmo assim, toda vez que aparecia cidade nova, a pergunta
"o que falta aqui?" era respondida de memória — errado, e diferente a cada
vez. Documento descreve; não cobra.

Este arquivo cobra. Ele define cada etapa como uma PERGUNTA COM RESPOSTA NO
DISCO e roda essa pergunta contra todas as praças. Mafra é a régua: é a praça
que foi até o fim e que gerou o relatório que a diretoria usou para decidir.
Se uma praça não tem o que Mafra tem, ela não está pronta, e aqui aparece
qual etapa falta e qual comando preenche.

Sem isto, "todas as cidades no formato de Mafra" é uma intenção. Com isto,
é uma tabela que fecha ou não fecha.

Uso:
    python3 scripts/padrao.py                 # a tabela de todas as praças
    python3 scripts/padrao.py --praca mafra   # o detalhe de uma
    python3 scripts/padrao.py --faltas        # só o que falta, com o comando
    python3 scripts/padrao.py --salvar        # grava dados/portal/padrao.json
    python3 scripts/padrao.py --exigir        # sai com erro se alguma incompleta
"""
import argparse, json, pathlib, sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ/"scripts"))
from cruzamento import jsonl, reviews_unicos, conta

IDENT = RAIZ/"dados"/"identidade"
CONT = RAIZ/"dados"/"conteudo"
PORTAL = RAIZ/"dados"/"portal"


# ---------------------------------------------------------------- os mínimos
#
# Cada número aqui saiu do que Mafra tem. Não são metas inventadas: são o
# tamanho que provou dar leitura. Mudar um número aqui muda o que a rede
# considera "praça pronta" — então mude com o mesmo cuidado de mudar preço.
#
MIN_CANAIS = 8          # abaixo disso a cidade não foi mapeada, foi espiada
# 800 era o número aspiracional do documento, e Mafra — a régua — fez 1.046.
# Escrevi 800 contando POSTS, e post não é voz: voz é gente falando. A conta
# certa é avaliação com texto + post + comentário. Com a conta errada as treze
# praças reprovavam, inclusive a régua, que é o sinal clássico de critério
# quebrado e não de trabalho mal feito.
MIN_VOZES = 1000        # o que Mafra entregou, arredondado para baixo
MIN_CLINICAS = 80       # varredura rasa faz a cidade parecer fraca sem ser
MIN_REVIEWS = 800       # abaixo disso o tema não separa sinal de ruído
MIN_IMPRENSA = 20
# 40 era número redondo, e número redondo não é critério. As três cidades de
# porte parecido no Norte/Nordeste ficam juntas em 39, 44 e 44 — cortar em 40
# reprovava uma das três irmãs por UMA frase. O piso vai para 35, e o fato de
# Marabá ter o menor vocabulário de busca das treze praças (13,4 frases por
# 100 mil habitantes) fica como leitura da cidade, não como etapa reprovada.
MIN_PORTAS = 35
MIN_DNA = 5
MIN_CITACOES = 4
MIN_PLANO = 5


def carrega(d, p):
    a = d/f"{p}.json"
    return json.loads(a.read_text(encoding="utf-8")) if a.exists() else {}


class Base:
    """Tudo lido uma vez só. Treze praças × quinze etapas relendo os mesmos
    JSONL levaria minutos; assim leva segundos e ninguém deixa de rodar."""

    def __init__(self):
        self.ident = {p.stem: json.loads(p.read_text(encoding="utf-8"))
                      for p in sorted(IDENT.glob("*.json"))}
        self.serie = {}
        for n in ("canais", "posts", "categoria", "places", "anuncios", "imprensa",
                  "portas", "captacao", "midia_offline", "temas", "oportunidade",
                  "categoria_oportunidade"):
            por = {}
            for x in jsonl(n):
                por.setdefault(x.get("praca_id"), []).append(x)
            self.serie[n] = por
        self.reviews = {}
        for r in reviews_unicos():
            self.reviews.setdefault(r.get("praca_id"), []).append(r)
        self.cont = {p.stem: json.loads(p.read_text(encoding="utf-8"))
                     for p in CONT.glob("*.json")}

    def n(self, serie, p):
        return len(self.serie.get(serie, {}).get(p, []))


# ------------------------------------------------------------------- etapas
#
# (numero, nome, quem, so_para, checagem, comando_que_preenche)
#
# `checagem` devolve (ok, frase). A frase aparece na tabela e é o que se lê
# quando a etapa falha — por isso ela carrega o número, nunca só "faltando".
#
# `so_para`: "rede" = praça com unidade; "oportunidade" = praça sem unidade;
# None = as duas. Cobrar de uma praça de oportunidade o plano do franqueado
# foi exatamente o erro que gerou seis planos para franqueado inexistente.

def _e0(b, p):
    d = b.ident[p]
    faltam = [k for k in ("praca_id", "rotulo", "uf", "cidades") if not d.get(k)]
    if faltam:
        return False, f"identidade sem {', '.join(faltam)}"
    if not d.get("rotulo", "").split(" · ")[0] in (d.get("uf") or []):
        return False, f"rótulo '{d['rotulo']}' não começa pela UF da praça"
    return True, f"{d['rotulo']} · {len(d.get('locais') or [])} locais"


def _e0b(b, p):
    """Onde a rede ESTÁ, a prova é a própria unidade. Onde ela NÃO está, a
    prova precisa de duas fontes independentes concordando — porque recomendar
    abertura onde já existe unidade quebra a confiança na ferramenta inteira."""
    d = b.ident[p]
    if not d.get("sem_unidade"):
        nossos = [l for l in d.get("locais", []) if l.get("papel") == "proprio"]
        com_id = [l for l in nossos if l.get("place_id")]
        return (bool(com_id),
                f"{conta(len(nossos), 'unidade própria', 'unidades próprias')}, "
                f"{len(com_id)} com ficha "
                f"do Google identificada")
    c = d.get("conferencia_de_unidade") or d.get("conferencia") or {}
    if not c:
        return False, "praça sem unidade e sem conferência de duas fontes"
    fontes = [k for k in c if k not in ("_nota", "conclusao", "veredito")]
    return (len(fontes) >= 2,
            f"{len(fontes)} fontes independentes concordam que a rede não está lá")


def _e1(b, p):
    ib = b.ident[p].get("ibge") or []
    com_pop = [x for x in ib if (x.get("populacao_estimada") or {}).get("valor")]
    return bool(com_pop), (f"{conta(len(com_pop), 'município')} com população "
                           f"do IBGE")


def _e2(b, p):
    ch = b.serie["canais"].get(p, [])
    # `rejeitado` marca homônimo conferido na bio: Rio Branco Atlético Clube
    # do ES, Prefeitura de Rio Branco do SUL, o restaurante em Mafra/Portugal,
    # o professor Guilherme Prudente. Contar isso é inflar a etapa justamente
    # onde a praça parecia melhor.
    achados = [c for c in ch if c.get("handle") and not c.get("rejeitado")]
    return (len(achados) >= MIN_CANAIS,
            f"{len(achados)} canais com handle (mínimo {MIN_CANAIS})")


def vozes(b, p):
    """Uma voz é alguém falando em público sobre a cidade ou sobre a clínica.

    Avaliação SEM texto não conta: estrela sozinha não diz nada e infla o
    número. Comentário conta, e é onde mora a conversa real — em Contagem são
    19.794 comentários contra 725 posts."""
    r = sum(1 for x in b.reviews.get(p, []) if (x.get("texto") or "").strip())
    ps = b.serie["posts"].get(p, [])
    return r + len(ps) + sum(int(x.get("comentarios") or 0) for x in ps), r, len(ps)


def _e3(b, p):
    v, r, ps = vozes(b, p)
    return v >= MIN_VOZES, (f"{v} vozes (mínimo {MIN_VOZES}) — "
                            f"{r} avaliações com texto, {ps} posts")


def _e5(b, p):
    n = b.n("categoria", p) or b.n("categoria_oportunidade", p)
    return n >= MIN_CLINICAS, f"{n} clínicas varridas (mínimo {MIN_CLINICAS})"


def _e6(b, p):
    n = len(b.reviews.get(p, []))
    return n >= MIN_REVIEWS, f"{n} avaliações lidas (mínimo {MIN_REVIEWS})"


def _e7(b, p):
    nossos = {l["local_id"] for l in b.ident[p].get("locais", [])
              if l.get("papel") == "proprio"}
    meus = [r for r in b.reviews.get(p, []) if r.get("local_id") in nossos]
    an = b.n("anuncios", p)
    return bool(meus), f"{len(meus)} avaliações da unidade · {an} anúncios da praça"


def _e9(b, p):
    n = b.n("imprensa", p)
    return n >= MIN_IMPRENSA, f"{n} matérias de imprensa (mínimo {MIN_IMPRENSA})"


def _e10(b, p):
    n = b.n("midia_offline", p)
    return n > 0, f"{n} canais offline declarados (rádio, outdoor, escola…)"


def _e11(b, p):
    c = b.cont.get(p, {})
    falta = []
    if not c.get("tese"):
        falta.append("tese")
    if len(c.get("dna") or []) < MIN_DNA:
        falta.append(f"dna ({len(c.get('dna') or [])}/{MIN_DNA})")
    if len(c.get("citacoes") or []) < MIN_CITACOES:
        falta.append(f"citações ({len(c.get('citacoes') or [])}/{MIN_CITACOES})")
    if len(c.get("plano") or []) < MIN_PLANO:
        falta.append(f"plano ({len(c.get('plano') or [])}/{MIN_PLANO})")
    return (not falta), ("completa" if not falta else "falta " + ", ".join(falta))


def _e13(b, p):
    t = b.serie["temas"].get(p, [])
    return bool(t), f"{len({x.get('tema') for x in t})} temas classificados"


def _e14(b, p):
    n = b.n("portas", p)
    cap = b.n("captacao", p)
    return (n >= MIN_PORTAS and cap > 0,
            f"{n} portas de busca · {conta(cap, 'leitura')} de captação")


def _e15(b, p):
    a = (PORTAL/"oportunidade"/f"{p}.json")
    if not a.exists():
        return False, "sem estudo de oportunidade publicado"
    d = json.loads(a.read_text(encoding="utf-8"))
    g = d.get("gemea") or {}
    return bool(g.get("praca_id")), f"gêmea: {g.get('rotulo') or '—'}"


def _e16(b, p):
    a = (RAIZ/"dados"/"planos"/f"{p}.json")
    return a.exists(), "plano do franqueado escrito" if a.exists() else "sem plano"


ETAPAS = [
    (0,  "A praça definida",          "humano", None,          _e0,
     "editar dados/identidade/<praça>.json — rótulo com UF na frente"),
    (0.5, "A rede está lá?",          "auto",   None,          _e0b,
     "python3 scripts/radar_oportunidade.py --cidade '<Cidade/UF>' --salvar"),
    (1,  "A cidade em números",       "auto",   None,          _e1,
     "python3 scripts/backfill_ibge.py --praca <praça>"),
    (2,  "Quem fala com a cidade",    "auto+humano", None,     _e2,
     "python3 coleta/coletores/canais.py --praca <praça>  (handle null = achar na mão)"),
    (3,  "Escutar a cidade",          "auto",   None,          _e3,
     "python3 coleta/coletores/instagram.py --praca <praça>"),
    (5,  "Varrer a categoria",        "auto",   None,          _e5,
     "python3 coleta/coletores/google_places.py --praca <praça> --varrer"),
    (6,  "Ritmo e meses seguidos",    "auto",   None,          _e6,
     "python3 coleta/coletores/google_reviews.py --praca <praça>"),
    (7,  "A unidade por dentro",      "auto",   "rede",        _e7,
     "python3 coleta/coletores/meta_ads.py --praca <praça>"),
    (9,  "A joia enterrada",          "auto+humano", None,     _e9,
     "python3 coleta/coletores/imprensa_rss.py --praca <praça>"),
    (10, "O que não vamos ver",       "humano", "rede",        _e10,
     "declarar canais offline em dados/serie/midia_offline.jsonl"),
    (11, "A inteligência",            "humano", "rede",        _e11,
     "escrever tese, dna, citações e plano em dados/conteudo/<praça>.json"),
    (13, "Cruzar com as outras",      "auto",   None,          _e13,
     "python3 scripts/classificar.py"),
    (14, "As portas da cidade",       "auto",   None,          _e14,
     "python3 coleta/coletores/portas.py --praca <praça> && "
     "python3 scripts/oportunidades_franqueado.py --praca <praça> --salvar"),
    (15, "O estudo de oportunidade",  "auto",   "oportunidade", _e15,
     "python3 scripts/estudar_oportunidade.py --praca <praça> --salvar"),
    (16, "O plano do franqueado",     "auto",   "rede",        _e16,
     "python3 scripts/plano_do_franqueado.py --praca <praça> --salvar"),
]


def vale_para(etapa, praca_e_de_oportunidade):
    so = etapa[3]
    if so is None:
        return True
    return (so == "oportunidade") == bool(praca_e_de_oportunidade)


def audita(b):
    fora = {}
    for p, d in b.ident.items():
        opo = bool(d.get("sem_unidade"))
        linhas = []
        for num, nome, quem, _so, chk, cmd in ETAPAS:
            if not vale_para((num, nome, quem, _so, chk, cmd), opo):
                continue
            try:
                ok, frase = chk(b, p)
            except Exception as e:
                ok, frase = False, f"erro ao checar: {e}"
            linhas.append({"etapa": num, "nome": nome, "quem": quem, "ok": ok,
                           "estado": frase,
                           "comando": None if ok else cmd.replace("<praça>", p)})
        feitas = sum(1 for l in linhas if l["ok"])
        fora[p] = {"praca_id": p, "rotulo": d.get("rotulo"),
                   "tipo": "oportunidade" if opo else "rede",
                   "feitas": feitas, "de": len(linhas),
                   "completa": feitas == len(linhas), "etapas": linhas}
    return fora


def imprime(res, so_faltas=False, uma=None):
    ordem = sorted(res.values(), key=lambda x: (x["tipo"], -x["feitas"]))
    if uma:
        r = res.get(uma)
        if not r:
            sys.exit(f"praça '{uma}' não existe. as que existem: {', '.join(sorted(res))}")
        print(f"\n{'='*76}\n  {r['rotulo']} — {r['feitas']} de {r['de']} etapas "
              f"({r['tipo']})\n{'='*76}\n")
        for l in r["etapas"]:
            print(f"  {'✓' if l['ok'] else '✗'} {str(l['etapa']):>4s} · {l['nome']:26s} {l['estado']}")
            if l["comando"]:
                print(f"        └─ {l['comando']}")
        print()
        return

    print(f"\n{'='*94}\n  O PADRÃO DA PRAÇA — Mafra é a régua\n{'='*94}\n")
    nums = [e[0] for e in ETAPAS]
    print(f"  {'praça':22s} " + " ".join(f"{str(n):>4s}" for n in nums) + "   completa")
    for r in ordem:
        por = {l["etapa"]: l for l in r["etapas"]}
        cel = []
        for n in nums:
            l = por.get(n)
            cel.append("   ·" if l is None else ("   ✓" if l["ok"] else "   ✗"))
        marca = "SIM" if r["completa"] else f"{r['feitas']}/{r['de']}"
        print(f"  {(r['rotulo'] or r['praca_id'])[:22]:22s} " + " ".join(cel) + f"   {marca}")
    print("\n  ✓ feita   ✗ falta   · não se aplica a este tipo de praça\n")
    for n, nome, quem, so, _c, _cmd in ETAPAS:
        alvo = "" if so is None else f"  (só {so})"
        print(f"   {str(n):>4s} · {nome:28s} {quem}{alvo}")

    if so_faltas or True:
        print(f"\n{'='*94}\n  O QUE FALTA, E O COMANDO QUE PREENCHE\n{'='*94}")
        for r in ordem:
            f = [l for l in r["etapas"] if not l["ok"]]
            if not f:
                continue
            print(f"\n  {r['rotulo']}  ({len(f)} etapa(s))")
            for l in f:
                print(f"    ✗ {str(l['etapa']):>4s} · {l['nome']}: {l['estado']}")
                print(f"         {l['comando']}")
        print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--praca")
    ap.add_argument("--faltas", action="store_true")
    ap.add_argument("--salvar", action="store_true")
    ap.add_argument("--exigir", action="store_true",
                    help="sai com erro se alguma praça estiver incompleta")
    a = ap.parse_args()

    b = Base()
    res = audita(b)
    imprime(res, so_faltas=a.faltas, uma=a.praca)

    if a.salvar:
        PORTAL.mkdir(parents=True, exist_ok=True)
        (PORTAL/"padrao.json").write_text(json.dumps({
            "gerado_em": max((x.get("snapshot_date", "")
                              for xs in b.serie.values() for v in xs.values() for x in v),
                             default=""),
            "regua": "mafra",
            "etapas": [{"etapa": n, "nome": nm, "quem": q, "so_para": so}
                       for n, nm, q, so, _c, _cmd in ETAPAS],
            "pracas": list(res.values()),
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  → dados/portal/padrao.json")

    if a.exigir and any(not r["completa"] for r in res.values()):
        incompletas = [r["praca_id"] for r in res.values() if not r["completa"]]
        sys.exit(f"\n  ✗ {len(incompletas)} praça(s) fora do padrão: "
                 f"{', '.join(incompletas)}\n")


if __name__ == "__main__":
    main()
