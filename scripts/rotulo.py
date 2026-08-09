"""Rótulo de praça — a UF vem SEMPRE antes do nome da cidade.

Existe Palmas no TO e no PR; existe Palmas de Monte Alto na BA. A coleta já
entrou contaminada por causa disso. Com a UF na frente, o erro salta aos olhos
antes de virar dado — e numa lista de 340 unidades a leitura agrupa por estado
sem precisar de coluna extra.

    "Contagem/MG"  ->  "MG · Contagem"
"""


def rotulo_cidade(cidade):
    nome, uf = (str(cidade).split("/") + [""])[:2]
    nome, uf = nome.strip(), uf.strip().upper()
    return f"{uf} · {nome}" if uf else nome


def rotulo_praca(ident):
    """Aceita o dict da identidade ou uma lista de cidades."""
    if isinstance(ident, dict):
        if ident.get("rotulo"):
            return ident["rotulo"]
        cidades = ident.get("cidades") or []
    else:
        cidades = list(ident or [])
    return " + ".join(rotulo_cidade(c) for c in cidades)
