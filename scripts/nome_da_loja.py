#!/usr/bin/env python3
"""
nome_da_loja.py — dá nome próprio a cada unidade, para a tela e para quem lê.

O PROBLEMA. Toda unidade da rede se chama "OrthoDontic". Isso já fundiu
`local_id` uma vez (as sete de Porto Alegre viraram uma) e o guarda de
`cruzamento.identidades()` resolveu a parte de dentro. Sobrou a parte de
fora: na TELA, as quatro unidades de São Paulo aparecem como quatro linhas
idênticas — "SP · São Paulo · OrthoDontic" quatro vezes — e o franqueado da
Lapa não tem como saber qual é a dele. Uma leitura recém-medida mostrou
lojas da mesma cidade com resultados opostos (uma em 1º nas cinco buscas,
outra fora em quatro); com o mesmo nome nas quatro, o achado não chega a
ninguém.

A REGRA. O bairro é o que distingue duas lojas da mesma marca na mesma
cidade, e é a palavra que o franqueado usa para falar da própria clínica.
Então:

    nome único na praça  →  fica como está ("OrthoDontic")
    nome repetido        →  "OrthoDontic · Lapa"
    bairro ilegível      →  "OrthoDontic · R. Doze de Outubro"  (a rua)
    nem isso             →  "OrthoDontic (2)"  — declarado, não inventado

O bairro sai do ENDEREÇO que já está na identidade. Não há coleta nova, não
há chamada de API e não se inventa localização: quando o endereço não diz,
o campo fica vazio e a desambiguação cai para a rua e depois para a ordem.

O que este script NÃO faz: não mexe em `local_id` (renomear id migra série
inteira e isso tem script próprio), não toca em concorrente, e não altera
nada que já tenha `unidade` preenchida por fonte externa — Florianópolis
veio do Google já como "OrthoDontic Centro" e continua assim.

Uso:
    python3 scripts/nome_da_loja.py
    python3 scripts/nome_da_loja.py --salvar
"""
import argparse, json, pathlib, re
from collections import Counter

RAIZ = pathlib.Path(__file__).resolve().parent.parent
IDENT = RAIZ/"dados"/"identidade"
MARCA = "OrthoDontic"      # sem espaço e sem acento; `ortho` solto pega rival


def bairro_do_endereco(e):
    """O bairro é o último trecho antes de ', Cidade - UF'.

    Cortar de trás para frente é o que importa: lendo de frente, o
    complemento ("1º Andar - Centro") virava bairro e a rede aparecia fora
    do Centro de Londrina, onde ela está.
    """
    partes = [x.strip() for x in str(e or "").split(",")]
    for i, x in enumerate(partes):
        if re.fullmatch(r".+ - [A-Z]{2}", x) and i > 0:
            b = partes[i-1].split(" - ")[-1].strip()
            return b if len(b) >= 3 and not re.fullmatch(r"[\d\s\-]+", b) else ""
    return ""


def rua_do_endereco(e):
    r = str(e or "").split(",")[0].strip()
    return r if len(r) >= 5 else ""


def rua_e_numero(e):
    partes = [x.strip() for x in str(e or "").split(",")]
    r = rua_do_endereco(e)
    if not r:
        return ""
    num = re.match(r"\d+", partes[1]) if len(partes) > 1 else None
    return f"{r}, {num.group()}" if num else r


def sem_acento(s):
    import unicodedata
    s = unicodedata.normalize("NFKD", str(s or ""))
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def resto_do_nome(l):
    """O que sobra do nome cadastrado depois de tirar a marca.

    Londrina é o caso: as duas unidades chegaram sem endereço e com o
    nome fazendo todo o trabalho — "OrthoDontic Souza Naves" e
    "OrthoDontic Centro". Jogar isso fora em nome da padronização
    transformaria as duas em "OrthoDontic (1)" e "OrthoDontic (2)", que é
    pior do que o problema que estamos consertando.
    """
    n = (l.get("nome") or "").strip()
    s = re.sub(r"(?i)^orthodontic\b[\s\-–·]*", "", n).strip(" -–·")
    # nome longo é palavra-chave empilhada no cadastro, não nome de loja
    return s if 0 < len(s) <= 28 else ""


def desambigua(grupo):
    """A ESCADA PARA DE SUBIR NO DEGRAU QUE JÁ SEPARA — e não antes.

    Bairro resolve São Paulo, onde as quatro unidades estão em quatro
    bairros. Não resolve Porto Alegre, onde QUATRO estão no Centro
    Histórico, nem Curitiba, onde quatro estão no Centro. Parar no bairro
    ali produziria quatro linhas idênticas de novo — o mesmo problema com
    mais texto.

    Então cada degrau é testado contra o grupo inteiro, e só vale se
    separar TODOS. O último degrau é a ordem, que sempre separa e é
    declarada como o que é: um número, não um endereço.
    """
    def rotulo(l, quem):
        s = quem(l)
        return f"{MARCA} · {s}" if s else MARCA

    # E CADA LOJA SOBE SÓ O QUE PRECISA. Em Caxias, três unidades: duas no
    # Centro e uma no Kayser. Exigir que o degrau separasse as três de uma
    # vez empurrava a do Kayser para "Av. Bom Pastor" — endereço no lugar
    # do bairro que já a identificava. Quem o bairro resolve, para no
    # bairro; só as empatadas sobem.
    final, pendentes, tomados = [None]*len(grupo), list(range(len(grupo))), set()
    for quem in (lambda l: l.get("bairro") or "",
                 resto_do_nome,
                 lambda l: rua_do_endereco(l.get("endereco")),
                 lambda l: rua_e_numero(l.get("endereco"))):
        nomes = [rotulo(l, quem) for l in grupo]
        vezes = Counter(nomes[i] for i in pendentes)
        resta = []
        for i in pendentes:
            if vezes[nomes[i]] == 1 and nomes[i] not in tomados:
                final[i] = nomes[i]
                tomados.add(nomes[i])
            else:
                resta.append(i)
        pendentes = resta
        if not pendentes:
            return final
    # nenhum degrau separou: numera, e o número aparece porque é honesto
    for n, i in enumerate(pendentes, 1):
        final[i] = f"{MARCA} ({n})"
    return final


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()

    mudou_arq, linhas = {}, []
    for arq in sorted(IDENT.glob("*.json")):
        d = json.loads(arq.read_text(encoding="utf-8"))
        proprios = [l for l in d.get("locais", []) if l.get("papel") == "proprio"]
        if not proprios:
            continue
        mudou = False
        # o bairro entra na identidade sempre — ele é dado da loja, e serve
        # a outras leituras além do nome
        for l in proprios:
            b = bairro_do_endereco(l.get("endereco"))
            if b and l.get("bairro") != b:
                l["bairro"] = b
                mudou = True
        # A MARCA É O NOME; O RESTO É TEXTO DE FICHA DO GOOGLE.
        #
        # Uma unidade de Porto Alegre chega chamada "OrthoDontic - Clínica
        # Odontológica Centro Porto Alegre - Tratamento de Canal -
        # Periodontia - Restauração Dental - Prótese - Clareamento e
        # Limpeza Dental - Aparelho Ortodôntico Metálico e Estético -
        # Emergência - Extração do Siso - Faceta de Porcelana". Isso é
        # palavra-chave que alguém empilhou no cadastro, não nome de loja,
        # e na tela vira uma linha ilegível. Toda unidade da rede se chama
        # OrthoDontic, e a tela já mostra a cidade ao lado: a base é a
        # marca, e o que distingue vem do endereço — dado, não cadastro.
        #
        # Praça de uma loja só fica com a marca limpa. Praça de várias
        # passa pela escada.
        antes = {l["local_id"]: (l.get("unidade") or l.get("nome") or "").strip()
                 for l in proprios}
        novos = ({proprios[0]["local_id"]: MARCA} if len(proprios) == 1
                 else dict(zip((l["local_id"] for l in proprios),
                               desambigua(proprios))))
        for l in proprios:
            novo = novos[l["local_id"]]
            if l.get("unidade") != novo:
                l["unidade"] = novo
                mudou = True
            if antes[l["local_id"]] != novo:
                linhas.append((d.get("rotulo"), l["local_id"],
                               antes[l["local_id"]], novo))
        # DUAS TELAS IGUAIS NA MESMA CIDADE É FALHA — em cidades
        # diferentes, não: a tela mostra "SC · Joinville" ao lado de
        # "OrthoDontic · Centro", e Sorocaba tem o seu próprio Centro.
        rep = [k for k, v in Counter(novos.values()).items() if v > 1]
        if rep:
            print(f"  ⚠ {d.get('rotulo')}: ainda repetido — {rep}")
        if mudou:
            mudou_arq[arq] = d

    if not linhas and not mudou_arq:
        print("  nenhuma loja com nome repetido na própria praça — nada a fazer")
        return
    print(f"  {len(linhas)} unidades ganham nome próprio, "
          f"em {len(mudou_arq)} praças:")
    for rot, lid, base, novo in linhas:
        print(f"    {rot:<22}{lid[:30]:<32}{base:<14} → {novo}")

    if not a.salvar:
        print("\n  (--salvar para gravar)")
        return
    for arq, d in mudou_arq.items():
        arq.write_text(json.dumps(d, ensure_ascii=False, indent=2)+"\n",
                       encoding="utf-8")
    print(f"\n  → {len(mudou_arq)} identidades atualizadas")


if __name__ == "__main__":
    main()
