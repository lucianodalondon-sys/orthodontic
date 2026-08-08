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

## O RITMO DOS LÍDERES NOVOS — coletado

Coletamos avaliação com data das 20 clínicas líderes que faltavam. O resultado
é pior que o placar de volume:

| Praça | Líder em ritmo | Faz | A unidade faz | Distância |
|---|---|---:|---:|---:|
| **Londrina** | Clínica Dentista do Povo | **158,6/mês** | 4,0 | **40×** |
| **Prudente** | Bongiovanni | **68,8/mês** | 13,2 | 5× |
| **Cuiabá** | ★ OrthoDontic Centro Norte | **45,6/mês** | — | lidera |
| **Riomafra** | Instituto Lumière | **43,6/mês** | 0,0 | ∞ |
| **Feira** | Central do Sorriso | **40,1/mês** | 0,0 | ∞ |

Onde a unidade está, pelo contador do Google:

- **Riomafra: 11ª de 11.** Última.
- **Feira: 8ª de 9.**
- **Londrina: matriz 6ª de 10; Centro 8ª.**
- **Prudente: 4ª de 11** — era a "mais saudável" e está 5× atrás.
- **Cuiabá: 1ª de 15** — a única que lidera.

---

## UMA CORREÇÃO DO NOSSO PRÓPRIO INSTRUMENTO

Ritmo pode ser medido de dois jeitos, e eles discordam:

1. **Pelo contador do Google** entre duas coletas. Observação direta.
2. **Pelo intervalo da amostra** — quantas avaliações vieram e em quantos dias.

Eles só concordam quando a clínica é rápida de verdade (Lumière: 43,6 contra
46,8; gigante de Feira: 39,7 contra 41,9). Nas lentas divergem muito: na matriz
de Londrina a amostra dizia **51,7/mês** e o contador subiu **3 em 23 dias**.

**O contador ficou como fonte oficial**, e o `inteligencia.py` marca `~estimado`
quando só existe uma coleta. Cuiabá tem uma coleta só — os 45,6 são estimativa,
e a segunda coleta em setembro confirma ou derruba.

---

## E UMA CORREÇÃO MAIOR: A AMOSTRA ERRADA INVERTE O SINAL

Com a lista antiga de concorrentes, "responder avaliação faz crescer" dava
**negativo em quatro das cinco praças** — e a gente escreveu que responder era
sintoma de clínica parada, contrariando a recomendação dos próprios estudos.

Com a varredura completa, o sinal **inverteu**:

| Praça | Lista feita a mão | Amostra completa |
|---|---:|---:|
| Feira | −0,27 | **+0,54** |
| Londrina | −0,62 | **+0,49** |
| Riomafra | +0,23 | **+0,39** |
| Prudente | −0,29 | **+0,36** |
| Cuiabá | −0,19 | −0,19 |

**A recomendação original estava certa. O nosso "não" é que estava errado.**

E fica a lição que vale para tudo o que este projeto vai produzir: **amostra de
conveniência não erra pouco, erra de sinal.** O mesmo cálculo, na mesma cidade,
deu +0,49 e −0,62 conforme quem estava na lista.

---

## RAJADA NÃO É RITMO — a distinção que faltava

Medimos mais 60 clínicas do segundo escalão (5.818 avaliações) e apareceu um
padrão que um número de velocidade sozinho esconde.

**Centro Odontológico COP Tomba**, em Feira: **95 avaliações em maio de 2026**,
depois 4 em junho e 1 em julho. A média mensal parece saudável. A clínica está
parada desde junho.

**COP - Centro Odontológico do Povo**, também em Feira: **100 avaliações em
5 dias** (3 a 8 de agosto). Campanha rodando agora, enquanto escrevemos.

**Odontologia Prado**, em Cuiabá: 23 · 60 · 17 nos últimos três meses. Isso não
é rajada, é máquina ligada.

O `inteligencia.py` agora marca **⚡ RAJADA** quando um único mês concentra 60%
ou mais das avaliações, e marca **amostra curta** quando o intervalo é menor que
21 dias — porque 100 avaliações em 5 dias não vira taxa mensal, vira "está em
campanha e não sabemos o ritmo".

**Onde isso muda o placar:**

| Praça | Clínicas em rajada entre as maiores |
|---|---|
| Feira | 5 — inclusive Odonto Marco (76% num mês) e Ortocentro (87%) |
| Londrina | 2 — Central Norte (60%) e Odontoclinic (68%) |
| Cuiabá | 3 — inclusive a própria OrthoDontic Dom Bosco (69%) |
| Prudente | 1 |

**E vale para a rede também:** a OrthoDontic Dom Bosco, de Cuiabá, tem 69% das
avaliações num mês só. Riomafra fez 47 em três meses de 2022 e parou. Feira fez
17 em julho de 2025 e parou. **As unidades sabem fazer campanha de avaliação.
Elas não sabem sustentar.** Essa é uma frase diferente de "elas não sabem
fazer", e leva a um plano diferente.

---

## UMA CORREÇÃO NO ACHADO PRINCIPAL

Escrevemos que a OrthoDontic Centro Norte era a primeira unidade da amostra a
**liderar** a própria cidade. **Ela é a segunda.**

A varredura do segundo escalão encontrou a **Odontologia Prado**, com 499
avaliações e ~60,8/mês contra os 45,6 da unidade. Não estava em nenhuma lista
porque tem menos avaliações acumuladas — e volume acumulado não é ritmo.

O que continua de pé, e é o que importa: **três unidades da mesma marca na
mesma cidade fazendo 45,6 · 3,7 · 0,7.** A comparação que controla mercado,
preço e marca não depende de quem está em primeiro.

---

## O QUE AINDA NÃO DÁ PARA DIZER

**Reclame Aqui continua em 3 de 432 reclamações.** Não é crédito — testamos com
conta nova e zerada, e o actor devolve 3 mesmo pedindo 40. É limite da
ferramenta, não do dinheiro. Sem isso não dá para comparar a rede com as
concorrentes, que é o que daria sentido ao número 432.

**As 727 clínicas restantes seguem sem ritmo.** Medimos as 20 maiores. As outras
podem esconder alguém subindo rápido de base pequena — que é como o líder de
hoje começou.

---

_Nenhuma conclusão anterior foi apagada. As correções ficam ao lado do que foi
dito antes, porque é assim que se vê se o método está melhorando._
