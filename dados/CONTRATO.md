# O contrato entre a coleta e o casco

O casco (a interface) **não calcula nada**. Se um número aparece na tela, ele
saiu de `dados/portal/`. Esse é o contrato inteiro.

```
  coleta                 análise                 publicação
  ──────                 ───────                 ──────────
  dados/serie/*.jsonl ─┐
  dados/conteudo/*.json ├─► build_portal.py ─► dados/portal/*.json ─┐
  dados/identidade/*.json ┘                                          ├─► injetar_casco.py ─► portal/index.html
                                          casco do Claude Design ────┘
```

---

## As três origens, e por que ficam separadas

| Diretório | O que é | Quem produz |
|---|---|---|
| `serie/` | **medido** — o que a coleta observou, com data | o pipeline |
| `conteudo/` | **autorado** — o que os estudos concluíram | o analista |
| `identidade/` | **a tabela de amarração** — o que é a mesma coisa em fontes diferentes | mantida à mão |

Misturar medido com autorado silenciosamente seria desonesto num produto que
vende evidência. Um número de `serie/` é verificável; uma tese de `conteudo/`
é uma leitura. O portal mostra os dois, mas eles nunca se confundem na origem.

---

## `serie/` — append-only, nunca sobrescreve

Toda linha carrega `snapshot_date`. Nada é apagado. Se a coleta de agosto
contradiz a de julho, as duas ficam — a contradição é dado.

O `build_portal.py` publica **a ponta da série** (o snapshot mais recente até
a data de corte). O histórico inteiro fica para o bloco "O que mudou" e para os
gráficos de série.

| Arquivo | Uma linha por |
|---|---|
| `places.jsonl` | local × snapshot — nota, volume, reviews novos/mês, anúncios ativos |
| `funil.jsonl` | unidade × período — o funil do Conecta |
| `regua.jsonl` | a régua da rede vigente (40/50/80/90) |
| `temas.jsonl` | praça × tema × snapshot — com `n`, `base` e `taxonomia_versao` |
| `sazonalidade.jsonl` | região × mês — índice de busca |
| `descida_nacional.jsonl` | palco × snapshot — a medição do embaixador |

**Dois campos fazem a série funcionar:**
`first_seen_snapshot` (a primeira coleta em que apareceu — é daí que sai a
velocity, de graça) e `last_seen_snapshot` (a última — em anúncio, a diferença
entre os dois é *dias no ar*; em review, detecta review apagado).

---

## As três colunas de volume que não podem se confundir

Os estudos misturam, e num banco isso vira erro sistemático.

| Campo | O que é |
|---|---|
| `avaliacoes_total` | quantas avaliações a clínica tem no Google |
| `reviews_coletados` | quantas a coleta puxou |
| `reviews_com_texto` | quantas têm texto — **a base de toda estatística de tema** |

Toda estatística de tema declara qual delas é o denominador, no campo `base`.

---

## Taxonomia versionada

Todo registro classificado carrega `taxonomia_versao`. Se o léxico mudar, sobe
a versão e **reprocessa o histórico inteiro** — nunca comparar número de v1.0
com número de v1.1.

O painel exibe os três juntos: valor, `n` e versão.

---

## Procedência

Todo valor exibido tem que ser reconstruível a partir de: `fonte` (o arquivo),
`filtro` (a consulta), `n`, `snapshot_date` e `taxonomia_versao`. Se não for,
não entra.

É o que a gaveta de evidência mostra — inclusive a **contra-evidência**, quando
existe. Ver `conteudo/evidencias.json`.

---

## Como o casco consome

O artefato publicado roda sob CSP estrita: **nenhuma requisição externa passa.**
Sem fetch, sem XHR, sem CDN. Então o dado é embutido na publicação, não buscado
em execução.

O casco lê assim, e de nenhum outro jeito:

```js
const DADOS = JSON.parse(
  document.getElementById("dados-portal").textContent
);
```

E dentro dele:

```
DADOS.manifest              corte, cobertura, taxonomia, índice de telas
DADOS.rede                  sinais + linhas das praças
DADOS.pracas.mafra       ficha completa de uma praça
DADOS.achados               constantes, variáveis, a derrubada
DADOS.corretor              vereditos por praça + a descida nacional
DADOS.evidencias            o conteúdo da gaveta, por chave
```

**Nenhum componente carrega valor literal.** Se um número está escrito dentro
de um componente, está errado — ele tem que vir de `DADOS`.

---

## O ciclo

```bash
# 1. a coleta roda e acrescenta em dados/serie/*.jsonl   (pipeline, no outro repo)
# 2. monta o payload
python3 scripts/build_portal.py

# 3. injeta no casco e gera o publicável
python3 scripts/injetar_casco.py casco-bruto.html

# 4. commit  →  a série ganha mais um ponto, versionada pelo git
```

O git **é** a série append-only: data, autoria e histórico de graça. Por isso a
gaveta de evidência pode um dia linkar a linha exata no commit exato, em vez de
só afirmar a fonte.
