# O que a rede aprendeu — as 13 praças no mesmo formato

Este é o documento para a diretoria. Não descreve ferramenta: descreve o que
o dado disse quando as treze praças passaram pelo mesmo processo.

---

## 1 · O padrão fechou

Sete praças com unidade. Todas com o estudo completo de Mafra — a praça que
foi até o fim e cujo relatório a diretoria usou para decidir. Não é opinião:
`python3 scripts/padrao.py` roda quinze etapas contra cada praça e diz quais
fecharam.

| praça | etapas |
|---|---|
| MG · Contagem · MT · Cuiabá · BA · Feira · PR · Londrina · SC · Mafra · TO · Palmas · SP · Presidente Prudente | **14 de 14** |

Mais seis cidades de oportunidade, onde a rede **não** está, com o mesmo
processo aplicado. AP · Macapá também fechou.

---

## 2 · O que vale para a rede inteira

Cada afirmação abaixo foi testada contra as treze praças, não contra quatro.
Onde uma praça contraria, ela aparece nomeada — **padrão sem exceção soa a
curadoria.**

### CONSTANTE — vale em todas

| achado | n |
|---|---|
| O paciente não avalia ortodontia — avalia como foi tratado | **13/13** |
| A confiança é em gente com nome, não em marca | **13/13** |
| A porta de entrada é `dentista`, não `aparelho` | **13/13** |
| O adulto de 30 a 45 é dinheiro na mesa, e nenhuma praça fala com ele | **13/13** |
| A recomendação é o motor, e ela é espontânea | **13/13** |
| **Perdemos para o rival no mesmo eixo em todas as praças: gente com nome** | **5/5** |

### SE REPETE — vale onde há amostra

**A ferida é sempre operação, nunca o produto** — 6/6. Nas 839 avaliações de
1 a 3 estrelas, quem reclama fala de atendimento, agenda, comunicação e
contrato. Não de aparelho.

### CANDIDATA — com exceção nomeada

**A mãe é a decisora** — 9/13. Cai em Cuiabá, Feira, Marabá e Parauapebas,
onde menos de 3% das avaliações mencionam filho ou família.

**A unidade mais lenta fica abaixo da mediana da cidade** — 4/7. Contagem,
Palmas e Prudente correm *acima* da mediana da própria praça. O título
anterior dizia "a prova social está parada em TODAS", e isso foi derrubado
pelo reteste.

### NÃO TESTÁVEL — e está escrito por quê

Seis afirmações não se testam com o que temos, e ficam marcadas: julho como
pico (a sazonalidade tem 4 pontos, todos de SC), a clínica-escola, a joia
local, a embalagem dos anúncios, a ordem de blindar antes de anunciar, e os
formatos de conteúdo. **Declarar o que é leitura humana vale mais que inflar
a escada.**

---

## 3 · O achado que vira decisão de rede

Das 35.538 avaliações lidas, **só 2.190 são nossas. 33.348 são da
concorrência** — já pagas, no disco, e nunca lidas como *"o que eles fazem
que dá certo"*.

Lendo o paciente do rival, dentro da mesma praça e por proporção:

| perdemos em | praças | pior caso |
|---|---|---|
| **Profissional que o paciente chama pelo nome** | **5 de 5** | ODONTO ART, Contagem: 29,7% contra 6,0% nossos — **5,0x** |
| Sabe atender criança | 4 de 5 | Turminha da Dra Bia, Prudente: 53,9% contra 3,1% — **17,3x** |
| Atende na hora marcada | 4 de 5 | Inovar, Palmas: 18,7% contra 1,8% — **10,6x** |
| Explica o que vai fazer, antes de fazer | 3 de 5 | ODONTO ART, Contagem: 5,5% contra 0,3% — **19,2x** |
| Cuida de quem tem medo de dentista | 3 de 5 | Dentista do Povo, Londrina: 6,0% contra 1,1% — 5,2x |

**O 5 de 5 fecha um circuito.** O achado constante já dizia que a confiança
é em gente com nome. Este diz onde isso custa: o rival é citado pelo nome
mais do que nós em **todas** as praças comparadas.

Perder no mesmo eixo em cinco estados não é problema de unidade. É
treinamento, roteiro de recepção e ficha do Google — decisão de
franqueadora, e o conserto não tem custo de mídia.

---

## 4 · O que cada praça tem de próprio

| praça | a tese |
|---|---|
| **MG · Contagem** | A maior base da rede, e a ferida é o **contrato** — não o aparelho. 33 avaliações negativas sem resposta, a maior fila da rede. |
| **TO · Palmas** | **Nota 5,0 e invisível no leilão.** Uma reclamação em 114. E 22 anúncios no ar na cidade, nenhum da rede. |
| **MT · Cuiabá** | **A mesma marca é a 2ª e a última da mesma cidade.** 46,4/mês contra 0,7/mês. Mesmo material, mesma tabela — o que sobra é operação. |
| **SC · Mafra** | A melhor clínica da cidade é a mais calada. Donos ortodontistas nascidos ali, ausentes do próprio feed. |
| **PR · Londrina** | A matriz ocupa o 2º e o último lugar do placar da própria cidade. |
| **BA · Feira** | O líder cresce ~39 avaliações/mês **sem comprar busca**. |
| **SP · Prudente** | A primeira franquia da rede, e a concorrente que atende criança é elogiada por isso 17 vezes mais. |

---

## 5 · O teto, declarado

O portal é feito **inteiramente com informação externa**. Não há CRM,
contrato, faturamento nem lead. Quatro pontos cegos são **permanentes**, e
aparecem na tela com nome:

- outdoor, panfleto, busdoor e a fachada
- a indicação de quem já tratou — apontada como *o* canal de decisão
- convênio fechado com escola, sindicato ou empresa
- o preço realmente praticado e o desconto que se dá na mesa

E um limite de escala que não se esconde: a rede tem **374 unidades**; esta
leitura mede **10**. Tudo aqui vale para as 13 praças ouvidas, não para as
374 unidades.

Em Cuiabá há ainda um concorrente que nenhum placar mostra: **a prefeitura
instala aparelho ortodôntico de graça** pelo programa Siminina Sorridente.
É o mesmo produto, gratuito, e estava fora de qualquer conta.
