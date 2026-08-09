#!/usr/bin/env python3
"""
unidades_da_rede.py — a lista oficial das unidades, direto do site da rede.

Existe por causa de um erro que estava prestes a acontecer: o Radar de
Oportunidade decidia se a rede já estava numa cidade olhando o campo
`websiteUri` da ficha do Google. Se a unidade não tem site na ficha, ou tem
o site do franqueado em vez do da rede, o radar diz "cidade livre" para uma
cidade que já tem clínica — e a franqueadora recebe uma recomendação de abrir
onde já tem. É o pior erro possível neste produto.

A fonte certa é a própria rede. O site publica o buscador de unidades e a
lista vem inteira de uma chamada só:

    POST /wp-json/orthodontic/v1/unities-list-load   → HTML com todos os cards
    GET  /wp-json/wp/v2/clinicas                     → confere a contagem

Cada card traz três linhas: nome da unidade, Cidade/UF, endereço. Um pedaço
delas está marcado **"Unidade em Implantação"** — cidade vendida, unidade
ainda não aberta. Para o radar essas contam igual: a praça não está livre.

Uso:
    python3 coleta/coletores/unidades_da_rede.py            # baixa e salva
    python3 coleta/coletores/unidades_da_rede.py --tem "Macapá/AP"
"""
import argparse, json, pathlib, re, subprocess, sys, time, unicodedata
import datetime as dt
import html as _html

RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent
SERIE = RAIZ/"dados"/"serie"
BASE = "https://www.orthodonticbrasil.com.br"
LISTA = f"{BASE}/wp-json/orthodontic/v1/unities-list-load"
CONTA = f"{BASE}/wp-json/wp/v2/clinicas?per_page=1"
ARQ = SERIE/"unidades_rede.jsonl"


def sem_acento(s):
    s = unicodedata.normalize("NFD", str(s))
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower().strip()


def baixar(tent=3):
    for i in range(tent):
        r = subprocess.run(["curl", "-sSL", "-m", "90", "-X", "POST", LISTA,
                            "-H", "User-Agent: Mozilla/5.0",
                            "-H", "Content-Type: application/json", "-d", "{}"],
                           capture_output=True, text=True)
        if r.stdout.strip():
            try:
                d = json.loads(r.stdout)
                if isinstance(d, str):
                    d = json.loads(d)
                if d.get("unidades"):
                    return d["unidades"]
            except Exception:
                pass
        time.sleep(2*(i+1))
    return None


def esperado():
    """Quantas o WordPress diz que existem. Serve de conferência da varredura."""
    r = subprocess.run(["curl", "-sSLi", "-m", "40", CONTA,
                        "-H", "User-Agent: Mozilla/5.0"], capture_output=True, text=True)
    m = re.search(r"(?im)^x-wp-total:\s*(\d+)", r.stdout or "")
    return int(m.group(1)) if m else None


def limpa_cidade(nome):
    """Oito cards escrevem o endereço inteiro na linha da cidade.

    "R:Tiradentes, 111 - salNeo 2 - Serra/ES" precisa virar "Serra/ES", senão
    a cidade nunca casa com a busca e o radar diria que Serra está livre. A
    regra: quebra em pedaços e fica com o último que não tem número — endereço
    tem número, nome de cidade não. "Pelotas 2" (a segunda unidade de Pelotas)
    cai no caso de sobra e perde o sufixo."""
    if not re.search(r"[,\d]", nome):
        return nome.strip()
    pedacos = [p.strip() for p in re.split(r"[.,]|\s-\s", nome) if p.strip()]
    limpos = [p for p in pedacos if not re.search(r"\d", p)]
    if limpos:
        return limpos[-1]
    return re.sub(r"\s*\d+\s*$", "", pedacos[-1]).strip() or nome.strip()


def separar(bruto):
    """Cada card termina em 'Agendar na unidade'. Antes disso vêm três linhas."""
    texto = _html.unescape(re.sub(r"<[^>]+>", "\n", bruto))
    linhas = [re.sub(r"\s+", " ", l).strip() for l in texto.split("\n")]
    linhas = [l for l in linhas if l]
    fora, buf = [], []
    for l in linhas:
        if l == "Agendar na unidade":
            fora.append(buf[-3:]); buf = []
        else:
            buf.append(l)
    unidades = []
    for c in fora:
        if len(c) < 2:
            continue
        cid = next((x for x in reversed(c) if re.match(r"^[^/]+/[A-Z]{2}$", x)), None)
        if not cid:
            continue
        nome, uf = [x.strip() for x in cid.split("/")]
        nome = limpa_cidade(nome)
        cid = f"{nome}/{uf}"
        implantando = any("implanta" in sem_acento(x) for x in c)
        end = ""
        if not implantando and len(c) == 3 and c[2] != cid:
            end = c[2]
        unidades.append({"unidade": c[0], "cidade": cid, "rotulo": f"{uf} · {nome}",
                         "uf": uf, "endereco": end,
                         "situacao": "em implantação" if implantando else "aberta"})
    # Porto Alegre tem DUAS unidades em implantação, e as duas se chamam
    # "Unidade em Implantação" sem endereço — cards idênticos. Sem contar a
    # ocorrência, a trava de duplicata do arquivo engoliria a segunda e a rede
    # perderia uma unidade na série.
    contagem = {}
    for u in unidades:
        k = (u["cidade"], u["unidade"], u["endereco"])
        contagem[k] = contagem.get(k, 0) + 1
        u["ocorrencia"] = contagem[k]
    return unidades


def carregar():
    """Lê o último snapshot salvo. Se não houver, baixa."""
    if ARQ.exists():
        linhas = [json.loads(l) for l in ARQ.read_text(encoding="utf-8").splitlines() if l.strip()]
        if linhas:
            ultimo = max(l["snapshot_date"] for l in linhas)
            return [l for l in linhas if l["snapshot_date"] == ultimo], ultimo
    bruto = baixar()
    if not bruto:
        return [], None
    us = separar(bruto)
    salvar(us)
    return us, dt.date.today().isoformat()


def tem_unidade(cidade, unidades=None):
    """A pergunta do radar: existe unidade nesta cidade?

    Casa por nome sem acento + UF, porque a lista da rede escreve 'Ilheus' e
    'Sertaozinho' sem acento e o IBGE escreve com."""
    if unidades is None:
        unidades, _ = carregar()
    nome, uf = (str(cidade).split("/") + [""])[:2]
    alvo, uf = sem_acento(nome), uf.strip().upper()
    return [u for u in unidades
            if sem_acento(u["cidade"].split("/")[0]) == alvo and u["uf"].upper() == uf]


def _chave(u):
    return (u.get("snapshot_date"), u.get("cidade"), u.get("unidade"),
            u.get("endereco"), u.get("ocorrencia", 1))


def salvar(unidades):
    """Append-only, mas sem repetir a mesma unidade no mesmo dia.

    A lista inteira vem de uma chamada só — rodar duas vezes no mesmo dia não
    é dado novo, é o mesmo dado de novo. Sem esta trava, três execuções viravam
    'a rede publica 12 unidades em Cuiabá' e o alerta de conferência acusava
    uma praça saudável. O arquivo continua sendo série: dia diferente, linha
    nova, nada apagado."""
    hoje = dt.date.today().isoformat()
    SERIE.mkdir(parents=True, exist_ok=True)
    ja = set()
    if ARQ.exists():
        for l in ARQ.read_text(encoding="utf-8").splitlines():
            if l.strip():
                ja.add(_chave(json.loads(l)))
    novos = 0
    with ARQ.open("a", encoding="utf-8") as f:
        for u in unidades:
            linha = {"snapshot_date": hoje, **u,
                     "fonte": "orthodonticbrasil.com.br/encontre-uma-unidade"}
            if _chave(linha) in ja:
                continue
            ja.add(_chave(linha))
            f.write(json.dumps(linha, ensure_ascii=False)+"\n")
            novos += 1
    return novos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tem", action="append", default=[],
                    help='confere uma cidade: --tem "Macapá/AP"')
    ap.add_argument("--nao-salvar", action="store_true")
    a = ap.parse_args()

    bruto = baixar()
    if not bruto:
        sys.exit("não consegui baixar a lista de unidades da rede — não vou "
                 "responder 'cidade livre' sem ter olhado a lista.")
    us = separar(bruto)
    esp = esperado()
    abertas = [u for u in us if u["situacao"] == "aberta"]
    cidades = {u["cidade"] for u in us}
    print(f"\n  {len(us)} unidades · {len(abertas)} abertas · "
          f"{len(us)-len(abertas)} em implantação · {len(cidades)} cidades")
    if esp is not None:
        marca = "ok" if esp == len(us) else "⚠ a lista mudou de formato"
        print(f"  o site diz {esp} — a varredura leu {len(us)} · {marca}")

    for c in a.tem:
        achadas = tem_unidade(c, us)
        if achadas:
            for u in achadas:
                print(f"  {u['rotulo']}: JÁ TEM — {u['unidade']} ({u['situacao']})")
        else:
            print(f"  {c}: nenhuma unidade na lista oficial")

    if not a.nao_salvar:
        salvar(us)
        print(f"  → dados/serie/unidades_rede.jsonl +{len(us)}\n")


if __name__ == "__main__":
    main()
