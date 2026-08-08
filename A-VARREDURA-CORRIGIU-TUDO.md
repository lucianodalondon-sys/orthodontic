# A varredura corrigiu as cinco praças

**08/08/2026** · Varredura completa da categoria pela Places API do Google:
**747 clínicas** nas cinco praças. Trabalhávamos com **36**.

> O erro não era de conta. Era de lista. Todo placar que a gente montou saiu de
> uma lista de concorrentes escolhida a mão — e **quem não entrou na lista nunca
> apareceu no placar.**

---

## O QUE MUDOU EM CADA PRAÇA

### Riomafra — a concorrente do estudo não é a líder

| | Estudo dizia | Varredura mostra |
|---|---|---|
| Líder da praça | Instituto Lumière (230) | **Susin Odontologia (441)** |
| Posição da unidade | 2ª | **7ª de 87** |

Nunca vimos: **Susin Odontologia 441** · Clínica Viver Bem 246 · Uniduni 159.
Três clínicas acima ou perto da Lumière, e a maior tem quase o dobro dela.

**Isto pesa mais que as outras correções:** é o estudo que a Paula disse ter
ajudado a montar o plano de ação da unidade.

### Feira de Santana — não era um gigante, são cinco

| | Estudo dizia | Varredura mostra |
|---|---|---|
| O gigante | Moisés Suzart (1.298) | Moisés Suzart (1.298) — confirmado |
| Posição da unidade | 2ª | **20ª de 144** |

Nunca vimos: Odonto Marco **1.268** · Instituto Ortocentro **1.000** · Central
do Sorriso **960** · Vamos Sorrir **826** · You Odontologia **663**.

A leitura "a unidade contra o gigante" estava errada. São seis clínicas acima
de 600 avaliações, e a unidade tem 170.

### Londrina — quatro já passaram a matriz, não uma

| | Estudo dizia | Varredura mostra |
|---|---|---|
| A ameaça | Odontoclinic ultrapassa em ~2 meses | **Quatro já ultrapassaram** |
| Posição da matriz | 1ª, sendo alcançada | **5ª de 151** |

Nunca vimos: Vittallon **1.073** · Dentista do Povo **946** · Central Norte
**732** · Odontologia Peixoto **570** — todas acima da matriz (566).

A previsão "perde a liderança em 2 meses" estava errada porque **a liderança já
tinha sido perdida** — para clínicas que não estavam na lista.

### Presidente Prudente — a líder não era a NEXA

| | Estudo dizia | Varredura mostra |
|---|---|---|
| Líder | NEXA Odonto (619) | **Bongiovanni (1.071)** |
| Posição da unidade | 2ª, prestes a assumir | **3ª de 121** |

A frase "passa a NEXA em ~2 meses" continua verdadeira, mas assumir a liderança
não. Bongiovanni tem quase o dobro.

### Cuiabá — confirmada

Foi a única praça já montada por varredura. Três OrthoDontic: **3ª, 45ª e 51ª de
243**. Nada mudou.

---

## O PADRÃO

| Praça | Concorrentes na lista | Clínicas reais | Posição do estudo | Posição real |
|---|---:|---:|---:|---:|
| Riomafra | 5 | 87 | 2ª | **7ª** |
| Feira | 3 | 144 | 2ª | **20ª** |
| Londrina | 3 | 151 | 1ª | **5ª** |
| Prudente | 5 | 121 | 2ª | **3ª** |
| Cuiabá | 14 | 243 | 3ª | 3ª |

**Em quatro das cinco praças a unidade estava pior do que dissemos.** E o erro
tem sempre a mesma direção — a lista feita a mão inclui o concorrente óbvio (a
rede rival, a franquia conhecida) e perde o consultório grande sem marca
nacional, que é justamente quem lidera.

Cuiabá é a única que não mudou. E é a única que nasceu de varredura.

---

## O QUE MAIS A VARREDURA ACHOU

**Feira tem ficha duplicada no Google.** Duas fichas no mesmo endereço (R. Mal.
Deodoro, 208, 1º andar): a real com 170 avaliações e nota 4,7, e uma fantasma
chamada "Aparelho Dental - Orthodontic Feira de Santana" **sem nota e sem
avaliação**. Ficha duplicada divide a reputação e confunde a busca. Custa nada
para resolver e é a primeira coisa a fazer nessa unidade.

**Londrina Centro tem nota 3,8** — a pior de todas as unidades OrthoDontic que
já medimos, com 76 avaliações.

**As quatro praças antigas estavam sem `place_id`.** O contrato do projeto diz
que a identidade é ancorada no `place_id` do Google, e nas quatro primeiras ele
estava nulo. Agora 17 dos 21 locais estão ancorados por endereço; 4 seguem
pendentes de conferência humana.

---

## COMO ISSO ENTRA NA CONVERSA COM A ORTHODONTIC

Não escondendo. **É o argumento.**

Um estudo feito a mão vê o que quem o fez lembrou de olhar. Uma varredura vê
tudo o que existe. A rede tem 340 unidades — ninguém vai montar 340 listas de
concorrentes a mão, e se montar, vai errar do mesmo jeito e na mesma direção.

É exatamente para isso que serve um sistema em vez de um estudo.

E o custo de descobrir isso foi **uma varredura de alguns minutos**, contra
semanas de estudo por praça.

---

## O QUE AINDA NÃO DÁ PARA DIZER

A varredura traz **quem existe e qual o volume**. Não traz **ritmo** — a API do
Google devolve no máximo 5 avaliações por clínica, e ritmo precisa de avaliação
com data.

Então dos 747 novos nomes, sabemos o tamanho, **não sabemos quem está
correndo**. Susin pode ter 441 avaliações acumuladas em dez anos e estar parada,
ou ter feito 300 no último ano. **Isso muda tudo e ainda não sabemos.**

Para saber, é preciso coletar avaliação com data dos novos líderes de cada
praça — o que depende de crédito na Apify, hoje esgotado.

---

_Nenhuma conclusão anterior foi apagada. As correções ficam ao lado do que foi
dito antes, porque é assim que se vê se o método está melhorando._
