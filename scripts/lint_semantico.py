#!/usr/bin/env python3
"""
lint_semantico.py — a tela ainda diz coisa que o próprio projeto já negou?

`confere_tese.py` cobra NÚMERO: o "9,7 por mês" citado existe no disco?
Este cobra CONCEITO. São falhas diferentes e nenhuma pega a outra.

O caso que originou o script: a tese de Mafra dizia "no mês em que a
região mais procura aparelho" — e a medição de sazonalidade, feita
depois, concluiu que o Google Trends não sustenta curva nesta escala em
NENHUMA das 15 regiões. O número não estava errado; a frase inteira
descrevia um mundo que a medição seguinte derrubou.

Texto autorado apodrece em silêncio porque ninguém relê o que já está
publicado. Aqui cada regra tem: o que procurar, por que é proibido, e
onde está a prova de que é proibido.

O que ele NÃO faz: não reescreve, não julga estilo e não bloqueia o build.
Ele aponta, e a correção é de quem escreveu.

Uso:
    python3 scripts/lint_semantico.py
    python3 scripts/lint_semantico.py --exigir
"""
import argparse, json, pathlib, re, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from cruzamento import conta

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ONDE = [RAIZ/"dados"/"conteudo", RAIZ/"dados"/"portal"]

# (nome, regex, por que é proibido, onde está a prova)
REGRAS = [
    ("sazonalidade inventada",
     r"m[êe]s em que .{0,40}mais procura|pico de procura|alta temporada de "
     r"aparelho|m[êe]s de maior procura|sazonalidade favor[áa]vel",
     "o Trends foi medido em 15 regiões e nenhuma passou nas travas de "
     "volume e de repetição do pico; por cidade, zero em 124 de SC e 186 "
     "do PR",
     "dados/portal/sazonalidade.json"),

    ("dado interno como se fosse nosso",
     r"\b(nosso|nossa|do nosso) (CRM|funil de vendas|faturamento|contrato)|"
     r"interessados do m[êe]s|taxa de fechamento da rede|meta da rede",
     "o produto é feito inteiramente com informação externa, e essa regra "
     "é permanente — o que só a rede pode responder é TETO do produto, "
     "declarado como teto",
     "CLAUDE.md · legacy/dado_interno/"),

    ("canibalização afirmada",
     r"canibaliza|rouba(ndo)? paciente|tira paciente d[ao]|perde paciente "
     r"para a unidade",
     "proximidade é fato, sobreposição de mercado é hipótese e "
     "canibalização exigiria saber a origem real do paciente — que é dado "
     "interno e não temos",
     "dados/portal/bairros.json · o_que_nao_e"),

    ("raio virou área de captação",
     r"[áa]rea de capta[çc][ãa]o|raio de capta[çc][ãa]o|atende (um )?raio de|"
     r"quem est[áa] a \d+ ?km",
     "o raio é um viés dado ao Google, não uma barreira; distância em "
     "linha reta também não é tempo de deslocamento",
     "coleta/coletores/perto_da_loja.py"),

    ("concentração virou demanda",
     r"bairro com mais demanda|onde h[áa] mais demanda|demanda concentrada "
     r"em|maior demanda da cidade",
     "clínica em volta é OFERTA; demanda seria gente procurando, e isso "
     "não está medido",
     "dados/portal/bairros.json · o_que_nao_e"),

    ("execução dada como feita",
     r"a unidade (j[áa] )?(executou|implementou|aplicou)|campanha foi "
     r"(rodada|executada)|a a[çc][ãa]o foi (feita|executada)",
     "o portal não fala com a unidade nem com a agência: ele registra a "
     "recomendação e mede de novo depois — dizer que foi executado é "
     "afirmar o que não se sabe",
     "scripts/livro_de_acoes.py"),

    ("promessa de retorno",
     r"vai (aumentar|gerar|trazer) \d+|retorno estimado|\bROI\b|aumento de "
     r"\d+% (em|nas) (vendas|contratos|pacientes)",
     "não temos faturamento, lead nem conversão; prometer resultado com "
     "dado externo é chute com cara de projeção",
     "scripts/execucao_necessaria.py",),

    ("a muleta (s)",
     r"\w\(s\)\b",
     "número e nome concordam sempre — `cruzamento.conta()` existe para "
     "isso; o portal já escreveu '1 unidades em faixa vermelha'",
     "CLAUDE.md"),

    ("palavra interna na tela",
     r"\bcasco\b|\bescada\b|\ba ponta\b|\br[ée]gua interna\b|\bpayload\b|"
     r"\blocal_id\b|\bsnapshot\b",
     "a tela fala língua de balcão; palavra de dentro do projeto nunca "
     "aparece para quem lê",
     "CLAUDE.md · PROMPT-CASCO-V6.md"),
]

# campos que são texto para HUMANO. Chave técnica não conta como tela.
TEXTUAIS = re.compile(
    r"tese|manchete|frase|titulo|t$|d$|leitura|problema|porque|por_que|"
    r"o_que|motivo|fato|deducao|opiniao|aviso|ressalva|nota|eyebrow|"
    r"descricao|resumo|comando", re.I)


# Campos que existem para quem MEXE no projeto, não para quem lê a tela:
# o aviso do manifest é contrato do build, e a nota de método de um achado
# explica como o achado foi feito. Acusar palavra interna aí empurraria o
# texto a ficar pior sem ninguém ganhar nada.
DE_DENTRO = re.compile(r"manifest\.json|_nota|nota_de_metodo|contrato", re.I)


def textos(no, caminho=""):
    if isinstance(no, dict):
        for k, v in no.items():
            yield from textos(v, f"{caminho}.{k}")
    elif isinstance(no, list):
        for i, v in enumerate(no):
            yield from textos(v, f"{caminho}[{i}]")
    elif isinstance(no, str) and len(no) > 12:
        campo = caminho.split(".")[-1].split("[")[0]
        if TEXTUAIS.search(campo):
            yield caminho, no


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exigir", action="store_true")
    a = ap.parse_args()

    achados, arquivos = [], 0
    for base in ONDE:
        if not base.exists():
            continue
        for arq in sorted(base.rglob("*.json")):
            try:
                d = json.loads(arq.read_text(encoding="utf-8"))
            except Exception:
                continue
            arquivos += 1
            rel = str(arq.relative_to(RAIZ))
            if DE_DENTRO.search(rel):
                continue
            for caminho, txt in textos(d):
                for nome, rx, porque, prova in REGRAS:
                    m = re.search(rx, txt, re.I)
                    # A FRASE QUE NEGA A ARMADILHA NÃO É A ARMADILHA.
                    # "o raio não é área de captação" é exatamente a
                    # ressalva que queremos na tela; acusá-la faria o lint
                    # empurrar o texto para o lado errado.
                    # "o portal não sabe se a ação foi executada" é a
                    # ressalva certa, e a primeira versão desta janela
                    # acusava justamente ela.
                    if m and re.search(
                            r"\bn[ãa]o\s+(é|e|mede|significa|quer|sabe|"
                            r"prova|confirma|garante)\b|\bningu[ée]m\b",
                            txt[max(0, m.start()-56):m.start()+8], re.I):
                        continue
                    if m:
                        achados.append((nome, rel, caminho, m.group(0)[:44],
                                        txt[max(0, m.start()-40):m.start()+70],
                                        porque, prova))

    print(f"  {arquivos} arquivos de conteúdo e payload conferidos")
    if not achados:
        print("  nenhuma frase contradiz o que o projeto já mediu")
        return

    por_regra = {}
    for x in achados:
        por_regra.setdefault(x[0], []).append(x)
    print(f"\n  {conta(len(achados), 'frase a rever', 'frases a rever')}, "
          f"em {conta(len(por_regra), 'regra')}:\n")
    for nome, itens in sorted(por_regra.items(), key=lambda x: -len(x[1])):
        print(f"  ── {nome.upper()}  ({len(itens)})")
        print(f"     por quê: {itens[0][5]}")
        print(f"     prova:   {itens[0][6]}")
        vistos = set()
        for _, rel, caminho, achado, trecho, _, _ in itens:
            k = (rel, achado)
            if k in vistos:
                continue
            vistos.add(k)
            print(f"       {rel}")
            print(f"         …{re.sub(chr(10), ' ', trecho)}…")
            if len(vistos) >= 4:
                break
        print()
    if a.exigir:
        sys.exit(1)


if __name__ == "__main__":
    main()
