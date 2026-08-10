#!/usr/bin/env python3
"""
pontos_cegos.py — a ETAPA 10 gerada de fora, sem pedir nada para a rede.

Por que mudou
-------------
A etapa 10 nasceu como formulário: cada canal offline tinha `quem_preenche:
unidade`, esperando o franqueado responder "eu faço rádio? patrocino a
escolinha?". Isso pressupõe acesso ao franqueado.

**Este produto é 100% dado externo.** Não temos e não vamos ter CRM, contrato,
faturamento nem o franqueado ao telefone. Um campo que só o cliente pode
preencher não é lacuna a preencher: é lacuna PERMANENTE, e tem de estar
escrita como permanente.

Então a etapa inverte. Ela não pergunta o que a unidade faz; ela declara
**o que esta base é incapaz de ver**, e junta a evidência pública indireta
quando existe. Duas categorias, e a diferença importa:

  fechavel_de_fora   um sinal público existe e ainda não foi coletado
  so_com_dado_interno  nenhuma fonte pública responde isso, nunca

O segundo grupo é o teto honesto do produto. Ele aparece na tela, com nome,
porque esconder o que não medimos é o que faz a diretoria achar que medimos
tudo — e é a primeira coisa que um concorrente com CRM usaria contra nós.

O que ele acha de fora
----------------------
A clínica-escola que dá tratamento DE GRAÇA é o exemplo que justifica a
etapa. Em Londrina o COU/UEL e em Prudente a Unoeste anunciam odontologia
gratuita — para CRIANÇA, no caso de Prudente, que é exatamente o público que
a rede disputa. Isso não aparece em nenhum placar de avaliação, não compra
anúncio, e mesmo assim tira paciente. Está na imprensa local, de graça.

Uso:
    python3 scripts/pontos_cegos.py
    python3 scripts/pontos_cegos.py --salvar
"""
import argparse, datetime as dt, json, pathlib, re, sys, unicodedata
from collections import defaultdict

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ/"scripts"))
from cruzamento import jsonl, identidades

SERIE = RAIZ/"dados"/"serie"

# Os nove tipos de canal que a ETAPA 2 procura. Tipo sem nenhum handle na
# praça é território vazio — e território vazio é achado, não falha.
TIPOS = ["voz_da_cidade", "imprensa", "mae", "preco_achadinho", "humor",
         "jovem", "gastronomia", "prefeitura", "esporte_base"]


def sa(s):
    return "".join(c for c in unicodedata.normalize("NFD", s or "")
                   if unicodedata.category(c) != "Mn").lower()


# ---------------------------------------------------------- os pontos cegos
#
# Cada um diz: o que é, se dá para fechar de fora, e como se procura o indício
# público. Quando `busca` é None, não existe fonte pública nenhuma — é teto.
CEGOS = [
    # ODONTOLOGIA NÃO É ORTODONTIA. Universidade que faz limpeza, extração e
    # canal de graça não disputa paciente de aparelho — é outro tratamento,
    # outro ticket, outra decisão. Só entra aqui quando o texto diz APARELHO
    # ou ORTODONTIA. A primeira versão disto marcava "COU oferece atendimento
    # odontológico gratuito" como concorrente, e não é.
    ("clinica_escola_com_aparelho_gratis",
     "Universidade que oferece APARELHO/ortodontia de graça na cidade",
     True,
     r"(universidade|faculdade|unoeste|uel|univag|ufmt|centro universit|"
     r"clinica escola|clínica-escola|curso de odontolog)"
     r".{0,90}(aparelho|ortodont|braquete|bráquete|alinhador)|"
     r"(aparelho|ortodont|braquete|bráquete|alinhador).{0,90}"
     r"(gratuit|de graca|de graça|sem custo)"),

    ("programa_publico_de_aparelho",
     "Prefeitura ou governo instalando aparelho ortodôntico de graça",
     True,
     r"(prefeitura|munic|estado|governo|sus|siminina)"
     r".{0,90}(aparelho|ortodont|braquete|bráquete)"),

    # Rádio e TV não se acham no TÍTULO da matéria — acham-se no VEÍCULO que
    # a publicou. Pescar no título trazia "Homem morre durante tratamento de
    # canal", que só casava porque o veículo, Rádio Itatiaia, vinha grudado no
    # fim da linha. O nome da emissora é o dado; a manchete é ruído.
    ("radio_e_tv_local", "Rádio e TV aberta da praça", True, "VEICULO"),

    # "apoio" sozinho casava com "Secretaria da Mulher reforça apoio às
    # vítimas". Patrocínio esportivo precisa da palavra do esporte junto.
    ("patrocinio_de_base",
     "Patrocínio de time, escolinha ou evento da cidade",
     True,
     r"(patroc[íi]nio|patrocina).{0,60}(time|clube|escolinha|futsal|futebol|atleta)|"
     r"(escolinha|sub-?1[0-9]|categoria de base).{0,60}(patroc|apoi)"),

    ("outdoor_panfleto_fachada",
     "Outdoor, panfleto, busdoor e a própria fachada",
     False, None),

    ("indicacao_boca_a_boca",
     "A indicação de quem já tratou — apontada como O canal de decisão",
     False, None),

    ("convenio_com_escola_ou_empresa",
     "Convênio fechado com escola, sindicato ou empresa",
     False, None),

    ("preco_praticado_e_desconto_de_balcao",
     "O preço real cobrado e o desconto que se dá na mesa",
     False, None),
]


def monta():
    ident = identidades(com_unidade=False)
    imprensa = defaultdict(list)
    for i in jsonl("imprensa"):
        imprensa[i.get("praca_id")].append(i)
    canais = defaultdict(list)
    for c in jsonl("canais"):
        if c.get("handle") and not c.get("rejeitado"):
            canais[c.get("praca_id")].append(c)

    hoje = dt.date.today().isoformat()
    linhas = []
    for p, d in sorted(ident.items()):
        tem = {c.get("tipo") for c in canais[p]}
        vazios = [t for t in TIPOS if t not in tem]

        for chave, nome, de_fora, busca in CEGOS:
            provas = []
            if busca == "VEICULO":
                rx = re.compile(r"r[áa]dio|emissora|\btv\b|televis|fm\b|am\b", re.I)
                vistos = set()
                for i in imprensa[p]:
                    v = (i.get("veiculo") or "").strip()
                    if v and v not in vistos and rx.search(sa(v)):
                        vistos.add(v)
                        provas.append({"veiculo": v, "titulo": None,
                                       "fonte": "dados/serie/imprensa.jsonl"})
            elif busca:
                rx = re.compile(busca, re.I)
                for i in imprensa[p]:
                    t = sa(i.get("titulo") or "")
                    if rx.search(t):
                        provas.append({"titulo": i.get("titulo"),
                                       "veiculo": i.get("veiculo"),
                                       "fonte": "dados/serie/imprensa.jsonl"})
                    if len(provas) >= 3:
                        break
            linhas.append({
                "snapshot_date": hoje, "praca_id": p,
                "rotulo": d.get("rotulo"),
                "canal": chave, "o_que_e": nome,
                "fechavel_de_fora": de_fora,
                "so_com_dado_interno": not de_fora,
                "estado": ("indicio_publico_encontrado" if provas else
                           "sem_rastro_publico" if de_fora else
                           "nunca_medivel_de_fora"),
                "provas": provas,
                "fonte": "dados/serie/imprensa.jsonl" if provas else None,
            })

        if vazios:
            linhas.append({
                "snapshot_date": hoje, "praca_id": p, "rotulo": d.get("rotulo"),
                "canal": "territorio_vazio", "o_que_e":
                    "Tipos de canal sem nenhum perfil local encontrado",
                "fechavel_de_fora": True, "so_com_dado_interno": False,
                "estado": "sem_rastro_publico",
                "tipos_sem_canal": vazios,
                "aviso": "Não achar não é o mesmo que não existir. Isto é "
                         "o limite da busca, não um retrato da cidade.",
                "fonte": "dados/serie/canais.jsonl",
            })
    return linhas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()
    linhas = monta()

    por = defaultdict(list)
    for l in linhas:
        por[l["praca_id"]].append(l)

    print(f"\n{'='*78}\n  OS PONTOS CEGOS — o que esta base não vê\n{'='*78}")
    for p, v in sorted(por.items()):
        com = [x for x in v if x.get("provas")]
        print(f"\n  {v[0]['rotulo']}")
        for x in v:
            if x["canal"] == "territorio_vazio":
                print(f"    ◦ território vazio: {', '.join(x['tipos_sem_canal'])}")
                continue
            marca = ("●" if x.get("provas") else
                     "○" if x["fechavel_de_fora"] else "×")
            print(f"    {marca} {x['o_que_e']}")
            for pr in x.get("provas", [])[:4]:
                if pr.get("titulo"):
                    print(f"        “{pr['titulo'][:74]}”")
                else:
                    print(f"        {pr['veiculo']}")
    print(f"\n  ● indício público achado   ○ sem rastro, mas achável de fora"
          f"   × nunca medível sem dado interno\n")

    n_interno = len({x["canal"] for x in linhas if x["so_com_dado_interno"]})
    print(f"  {n_interno} pontos cegos são PERMANENTES neste produto: "
          f"nenhuma fonte pública responde.")

    if a.salvar:
        p = SERIE/"midia_offline.jsonl"
        antigas = [x for x in jsonl("midia_offline")
                   if x.get("snapshot_date") != linhas[0]["snapshot_date"]]
        with p.open("w", encoding="utf-8") as f:
            for x in antigas + linhas:
                f.write(json.dumps(x, ensure_ascii=False) + "\n")
        print(f"\n  → dados/serie/midia_offline.jsonl "
              f"({len(antigas)} anteriores + {len(linhas)} novas)")


if __name__ == "__main__":
    main()
