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
| Mafra | 15 | 15 |
| Palmas | 14 | 14 |
| **Total** | **128** | **128** |

Antes eram 21 escritos a mão. E buscar por `place_id` não é só mais cômodo: é
**exato**. Buscar por nome já casou "OrthoDontic Prudente" com a Bongiovanni,
que é a concorrente nº 1 da praça.

### O catálogo do ciclo mentia

Dizia "3 de 19 coletores prontos" quando 7 rodam. `google_places`,
`reclame_aqui`, `google_ads` e `instagram` estavam marcados como "a construir"
e já funcionavam. Com `canais` e `whatsapp_teste` escritos hoje: **9 de 21.**

### O coletor de reclamação usava um actor quebrado

Devolvia sempre 3 reclamações de 3.133 — e com essas 3 a gente escreveu
"a marca não responde", que foi parar no prompt do portal como alerta CRÍTICO.
Trocado por `webdata_labs~reclameaqui-scraper`, que traz a ficha completa.

---

## O QUE RODA HOJE, DE PONTA A PONTA

| Coletor | Frequência | Custo | Validado em |
|---|---|---|---|
| `google_places` | mensal | ~US$0,05/praça | 6 praças, 884 clínicas |
| `google_reviews` | semanal | ~US$0,04/praça | 6 praças, 23.025 avaliações |
| `canais` | mensal | ~US$0,20/praça | 6 praças, 148 canais |
| `meta_ads` | semanal | ~US$0,10/praça | 5 praças, 324 anúncios |
| `google_ads` | semanal | ~US$0,20/praça | rede nacional |
| `instagram` | mensal | ~US$0,40/praça | 5 praças, 350 posts |
| `imprensa_rss` | semanal | grátis | 5 praças, 202 matérias |
| `reclame_aqui` | mensal | ~US$1/marca | 7 redes, 140 reclamações |
| `whatsapp_teste` | mensal | manual | **escrito, nunca usado de verdade** |

**Custo de uma volta completa: ~US$ 1 por praça.**

---

## O QUE AINDA NÃO ESTÁ VALIDADO

### O teste de WhatsApp existe, mas nunca foi usado de verdade

`whatsapp_teste.py` está escrito e testado ponta a ponta — com dados
fictícios, que foram apagados. **A ferida nº 1 dos cinco estudos continua sem
um único número real**, porque a etapa que falta é humana: alguém precisa
mandar a mensagem e anotar a hora.

É a coisa mais barata e mais valiosa da lista inteira.

### Dez coletores nunca escritos

Doctoralia (avaliação por profissional), grupos de Facebook (a decisão
acontecendo), CNPJ novo (o concorrente antes de abrir), vagas (rotatividade da
recepção), Google Q&A, SERP, CRO, Glassdoor, YouTube, mapa-diff.

### Um local com âncora incerta

De 128, um só: a clínica-escola da UEFS, em Feira, tem duas fichas disputando
e ficou marcada como `chave_incerta`. Ambas são minúsculas e não mudam placar
nenhum — mas fica declarado em vez de silenciosamente resolvido.

### O ritmo de Palmas e de Cuiabá é estimativa

As duas têm uma coleta só. O `~estimado` sai quando a segunda coleta chegar e
o contador do Google puder ser comparado. Setembro.

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

## A PROVA: PALMAS/TO, DO ZERO, SÓ COM OS COLETORES

O único teste que vale é entrar numa praça nova sem nenhum script auxiliar.
Palmas foi escolhida por preencher o buraco do **Norte**, que não tinha praça
nenhuma.

| Passo | Comando | Resultado |
|---|---|---|
| Descobrir | `descobrir_praca.py --cidade "Palmas/TO"` | IBGE, imprensa, esqueleto |
| Varrer | `google_places.py --praca palmas` | **137 clínicas** |
| Avaliar | `google_reviews.py --praca palmas` | **2.064 avaliações**, 14 clínicas numa corrida só |
| Escutar | `canais.py --praca palmas` | **13 canais**, humor declarado inexistente |
| Separar | `classificar.py` | 16.157 avaliações classificadas na base |
| Ler | `inteligencia.py --praca palmas` | placar, hipóteses e contraexemplos |

**Nenhum script descartável.** Custo ~US$ 1,50, cerca de 40 minutos.

### E Palmas já ensinou algo que nenhuma outra praça tinha ensinado

| Clínica | Ritmo | Meses seguidos | Responde |
|---|---:|---:|---:|
| DenteClin | 33,8 | 5 | 51% |
| Centro Integrado | 31,7 | 5 | 52% |
| **★ OrthoDontic** | **14,0** | **11** | **0%** |

A unidade é **3ª em ritmo mas 1ª em constância**. As duas que estão na frente
são campanha de cinco meses; a unidade sustenta há onze.

É a segunda vez que uma OrthoDontic aparece como a operação mais estável da
praça — a primeira foi Cuiabá. **Começa a virar padrão: a rede não é a mais
rápida, é a mais constante.** Com duas praças isso ainda é sinal isolado, mas é
o tipo de coisa que muda o argumento de "vocês estão perdendo" para "vocês
duram mais que os outros — falta acelerar".

---

## O QUE FAZER A SEGUIR, EM ORDEM

1. ✅ ~~Portar a coleta funda~~ — `google_reviews.py --max-reviews 600` já faz,
   e o `inteligencia.py` monta o histograma mensal.
2. ✅ ~~Escrever o teste de WhatsApp~~ — `whatsapp_teste.py`, testado.
3. ✅ ~~Fechar os locais pendentes~~ — zero pendentes; um ficou marcado como
   incerto de propósito.
4. ✅ ~~Rodar o ciclo do zero~~ — Palmas, acima.
5. **Rodar o teste de WhatsApp de verdade.** O coletor existe e nunca foi
   usado com uma mensagem real. É a ferida nº 1 e continua sem um número.
6. **Segunda coleta de Palmas em setembro**, para o ritmo sair do `~estimado`
   e virar contador.
7. Os dez coletores que faltam, na ordem do `coleta/FONTES.md`.

---

_A coleta de hoje: 23.025 avaliações, 884 clínicas, 350 posts, 148 canais,
324 anúncios, 140 reclamações e 202 matérias, em **6 praças**. Custo ~US$ 14._
