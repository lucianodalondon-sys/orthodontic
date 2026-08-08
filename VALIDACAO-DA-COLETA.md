# O que está validado na coleta, e o que não está

**Auditoria de 08/08/2026.** A pergunta foi direta — *"temos todo o processo de
coleta validado?"* — e a resposta honesta é **não, mas hoje ficou muito mais
perto.**

---

## O QUE ESTAVA QUEBRADO E FOI CONSERTADO HOJE

### O coletor não conseguia coletar a praça mais rica

`python3 coleta/coletores/google_reviews.py --praca cuiaba` devolvia
**0 locais.** Toda a coleta de Cuiabá — a praça do achado principal — foi feita
com script descartável, fora do processo. Se alguém tentasse repetir amanhã,
não conseguiria.

A causa era estrutural: a lista de clínicas ficava **escrita dentro do código**,
praça por praça, num dicionário `QUERIES`. Não escala para 340 e deixava praça
de fora **sem avisar**.

**Consertado:** o coletor agora lê `dados/identidade/<praca>.json` e busca por
`place_id` quando existe. Resultado:

| Praça | Locais | Por place_id |
|---|---:|---:|
| Cuiabá | 29 | 29 |
| Prudente | 25 | 24 |
| Londrina | 24 | 23 |
| Feira | 21 | 20 |
| Riomafra | 15 | 15 |
| **Total** | **114** | **111** |

Antes eram 21 escritos a mão. E buscar por `place_id` não é só mais cômodo: é
**exato**. Buscar por nome já casou "OrthoDontic Prudente" com a Bongiovanni,
que é a concorrente nº 1 da praça.

### O catálogo do ciclo mentia

Dizia "3 de 19 coletores prontos" quando 7 rodam. `google_places`,
`reclame_aqui`, `google_ads` e `instagram` estavam marcados como "a construir"
e já funcionavam. **Corrigido: 7 de 20.**

### O coletor de reclamação usava um actor quebrado

Devolvia sempre 3 reclamações de 3.133 — e com essas 3 a gente escreveu
"a marca não responde", que foi parar no prompt do portal como alerta CRÍTICO.
Trocado por `webdata_labs~reclameaqui-scraper`, que traz a ficha completa.

---

## O QUE RODA HOJE, DE PONTA A PONTA

| Coletor | Frequência | Custo | Validado em |
|---|---|---|---|
| `google_places` | mensal | ~US$0,05/praça | 5 praças, 747 clínicas |
| `google_reviews` | semanal | ~US$0,04/praça | 5 praças, 20.961 avaliações |
| `meta_ads` | semanal | ~US$0,10/praça | 5 praças, 324 anúncios |
| `google_ads` | semanal | ~US$0,20/praça | rede nacional |
| `instagram` | mensal | ~US$0,40/praça | 5 praças, 350 posts, 135 canais |
| `imprensa_rss` | semanal | grátis | 4 praças, 202 matérias |
| `reclame_aqui` | mensal | ~US$1/marca | 7 redes, 140 reclamações |

**Custo de uma volta completa: ~US$ 1 por praça.**

---

## O QUE AINDA NÃO ESTÁ VALIDADO

### Coisas que fizemos hoje e não viraram coletor

Três análises que produziram os achados mais fortes rodaram em script
descartável e **não se repetem sozinhas**:

- **a coleta funda** (400 a 600 avaliações) que revelou rajada contra ritmo e
  mostrou que a matriz de Londrina fez 180 avaliações em maio
- **a busca de canais da cidade** (os 9 tipos), que achou o vazio do canal da mãe
- **a varredura do 2º escalão**, que achou a Odontologia Prado

Enquanto forem script solto, **a próxima praça não terá isso.**

### Onze coletores nunca escritos

O mais caro deles é o **teste de WhatsApp** — tempo até a primeira resposta.
Os cinco estudos apontam isso como a ferida nº 1, e é a única das treze
constantes que **nenhuma fonte pública mede**. Continua sem medição.

Depois vêm: Doctoralia (avaliação por profissional), grupos de Facebook (a
decisão acontecendo), CNPJ novo (o concorrente antes de abrir), vagas
(rotatividade da recepção), Google Q&A, SERP, CRO, Glassdoor, YouTube,
mapa-diff.

### Quatro locais sem âncora

De 114, quatro seguem sem `place_id` confirmado e ficam de fora dos placares.
São casos que o casamento automático recusou de propósito — melhor ficar
pendente que ficar errado.

### O que depende da rede

`gbp_insights` (buscas, cliques e ligações por unidade) e `conecta_funil`.
Sem dado interno, seguem parados — e o portal foi desenhado para funcionar
sem eles.

---

## A LIÇÃO QUE MAIS SE REPETIU HOJE

Quatro vezes, no mesmo dia, o mesmo erro mudou a conclusão de **sinal**:

| O que a amostra pequena dizia | O que a amostra completa diz |
|---|---|
| a unidade é 2ª da praça | é 7ª, 20ª, 5ª — a lista a mão perdia o líder |
| responder avaliação **não** faz crescer | faz, positivo em 4 de 5 praças |
| a matriz de Londrina está estagnada | fez a maior campanha da cidade e desligou |
| a marca não responde reclamação | responde 98,6%, melhor que as gigantes |

**Amostra de conveniência não erra pouco. Erra de sinal.**

Por isso a validação da coleta não é burocracia neste projeto: é o que separa
uma recomendação certa de uma recomendação invertida — e as duas chegam à
diretoria com a mesma cara de confiança.

---

## O QUE FAZER A SEGUIR, EM ORDEM

1. **Portar a coleta funda para coletor.** É a que produz o histograma mensal,
   que é a métrica que separa operação de campanha. Sem ela, a próxima praça
   volta a medir errado.
2. **Escrever o teste de WhatsApp.** É a ferida nº 1 e ninguém mede.
3. **Fechar os 4 locais pendentes**, à mão, olhando o endereço.
4. **Rodar o ciclo inteiro numa praça, do zero**, sem script auxiliar — é o
   único teste que prova que o processo está de pé.

---

_A coleta de hoje: 20.961 avaliações, 747 clínicas, 350 posts, 135 canais,
324 anúncios, 140 reclamações e 202 matérias, em 5 praças. Custo ~US$ 12._
