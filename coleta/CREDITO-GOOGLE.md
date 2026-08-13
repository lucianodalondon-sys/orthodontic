# O crédito do Google — quanto temos, e quando acaba

> **Lido no console em 13/ago/2026.** Este arquivo não se atualiza sozinho:
> quem abrir o Billing de novo, atualize aqui e ponha a data.

## O estado

| | |
|---|---|
| tipo | **crédito de teste gratuito** (trial), não conta paga |
| total | R$ 1.745 |
| consumido | R$ 360 (1 a 13/ago/2026) |
| **restante** | **R$ 1.385** |
| **acaba em** | **7 de novembro de 2026** — 85 dias a partir de 13/ago |
| cobrança | R$ 0,00. O console mostra custo R$ 360 e economia R$ 360 |

**O teste acaba por PRAZO ou por CONSUMO, o que vier primeiro.** Não dá para
pausar nem estender. Quando acabar, o Google interrompe os recursos criados
durante o teste e **não cobra** — a menos que se faça upgrade para uma conta
de Cloud Billing paga.

Na prática, para este projeto: **quando acabar, é preciso trocar a chave**
em `_pipeline/.env` (`GOOGLE_API_KEY`) por uma de outro projeto com crédito,
ou fazer o upgrade. Sem uma das duas coisas, a ponta, as portas, a varredura
e a busca perto da loja param — e param TODAS de uma vez, porque usam a
mesma chave.

## O custo real, calibrado

R$ 360 dividido pelas chamadas que o disco registra no período:

| série | o que conta | chamadas |
|---|---|---|
| `places` | ponta — 1 por ficha | 1.194 |
| `portas` | só a parte "quem responde no mapa" | 660 |
| `perto_da_loja` | geo-grid — 1 por consulta | 225 |
| `categoria` | varredura — resultados ÷ 20 por chamada | ~180 |
| | **total** | **~2.259** |

    R$ 360 ÷ 2.259  ≈  R$ 0,159 por chamada
    R$ 1.385 restantes  ≈  ~8.700 chamadas

O `≈` é honesto: `categoria` grava RESULTADO, não chamada, e o Text Search
devolve até 20 por vez. A divisão por 20 é a melhor aproximação que o disco
permite. O número por chamada pode variar por SKU — Place Details e Text
Search não custam igual.

## Quanto dura, ao ritmo de hoje

O ciclo de 13/ago custou **883 chamadas ≈ R$ 140** — mas ele levou junto a
varredura completa e as portas, que não são semanais.

| ciclo | chamadas | custo | quantas vezes cabem |
|---|---|---|---|
| **semanal enxuto** (ponta + perto) | ~630 | ~R$ 100 | **~13 semanas** |
| semanal + portas | ~830 | ~R$ 132 | ~10 semanas |
| completo com varredura | ~883 | ~R$ 140 | ~9 semanas |

O prazo de 7/nov são ~12 semanas. Ou seja: **o ciclo enxuto atravessa o
prazo; o ciclo completo toda semana consome o crédito antes.** A varredura
completa é mensal por método (ela descobre; a watchlist acompanha) — e essa
decisão, tomada por causa da instabilidade de 53% em Cuiabá, também é o que
faz o crédito durar.

## O que fazer quando acabar

1. Criar novo projeto no Google Cloud com crédito de teste, gerar chave,
   trocar `GOOGLE_API_KEY` em `_pipeline/.env`. **Não commitar a chave** —
   `_pipeline/` é gitignored e tem de continuar sendo.
2. Ou fazer upgrade para Cloud Billing pago, e aí o custo por chamada passa
   a ser real e recorrente.
3. Em qualquer dos dois casos: rodar `python3 coleta/coletores/ponta.py`
   sem `--salvar` primeiro, para confirmar que a chave nova responde antes
   de gastar uma rodada inteira.
