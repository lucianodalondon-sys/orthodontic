# O que a coleta não vê

> Regra do projeto: **o portal declara o próprio ponto cego em toda tela onde
> ele muda a leitura.** Um sistema que diz o que não sabe é mais confiável que
> um que finge ver tudo — e é o que impede a diretoria de tomar decisão errada
> com número certo.

---

## O ponto cego principal: mídia offline

Tudo que a coleta enxerga deixa **rastro público digital**: avaliação no Google,
anúncio na biblioteca do Meta, anúncio no Centro de Transparência do Google,
post, comentário, matéria de portal.

**Não deixa rastro, e portanto não medimos:**

| Canal | Por que importa aqui |
|---|---|
| **Rádio** | Em Mafra o estudo documenta 3 emissoras fortes, uma da paróquia, e que **um único balcão comercial vende 3 das 4 frequências**. Descrito como "a mídia da mãe e da avó". |
| **TV aberta** | O dossiê da rede registra que a **OdontoCompany usa TV aberta para volume**. |
| **Outdoor, panfleto, fachada** | Sem rastro nenhum. |
| **Patrocínio de comunidade** | A unidade de Mafra **patrocina os escoteiros** — está no estudo. Não sabemos valor, alcance, nem se há outros. |
| **Prêmio e circuito local** | Um concorrente de Mafra foi "eleito ortodontista destaque do ano" por circuito comercialmente acessível. |
| **Parceria com escola e convênio** | Relevante porque a decisora é a mãe e o público-alvo está na escola. |
| **Indicação / boca a boca** | Os quatro estudos apontam como **O canal de decisão**. Nenhuma fonte pública mede. |

---

## Onde isso muda o que já foi escrito

### O caso do Google Ads

Encontramos: três redes concorrentes compram busca no Brasil (OdontoCompany 35
anúncios, Odontoclinic 15, Sorrifácil 1) e a OrthoDontic aparece com **zero**
em quatro variantes de nome.

**O que dá para afirmar:** a OrthoDontic não está na busca paga.

**O que NÃO dá para afirmar:** que a OrthoDontic "não está em nenhuma mídia".
Ela pode estar no rádio de Mafra, num outdoor em Feira, patrocinando o time
da escola. Não sabemos.

### O caso do Moisés Suzart

Ele cresce **~39 avaliações por mês** em Feira, tem 1.298 no total, e **não
compra busca nem responde avaliação**. Nas nossas fontes, ele não faz nada que
explique o crescimento.

**Isso não é um paradoxo — é a medida do nosso ponto cego.** A causa do
crescimento dele está fora do que coletamos: rádio, TV local, indicação médica,
presença comunitária, ou simplesmente o processo de pedir review na cadeira, que
não deixa rastro.

### O caso da Lumière

Cresceu de ~28 para ~43 avaliações/mês e triplicou anúncios no Meta. **Correlação
temporal não é causa.** Ela pode ter entrado no rádio no mesmo mês.

---

## A regra de escrita que isso impõe

| Não escrever | Escrever |
|---|---|
| "a unidade está muda" | "a unidade está ausente **do digital rastreável**" |
| "a rede não escolheu nenhuma mídia" | "a rede não aparece em nenhuma das mídias **que conseguimos medir**" |
| "cresce porque anuncia" | "cresce; anuncia — a causa não está estabelecida" |
| "zero anúncios" | "zero anúncios **na biblioteca do Meta e no Centro de Transparência**" |

O alerta **"silêncio no pico"** passa a se chamar **"silêncio no digital
rastreável no pico"**. Custa quatro palavras e evita uma acusação injusta a um
franqueado que talvez esteja no rádio da cidade.

---

## Como o portal fecha esse buraco

Não fecha com coleta — fecha com **declaração**. É a única parte do sistema onde
o dado vem da unidade, não da máquina:

`dados/serie/midia_offline.jsonl` — um registro por praça × canal, com `status`
(`nao_medido` / `parcialmente_conhecido` / `declarado`), a evidência indireta
que temos, e **quem preenche** (unidade ou franqueadora).

Na ficha da praça isso aparece como um bloco fixo — **"o que não estamos
vendo aqui"** — ao lado do placar de mídia. Não é rodapé: é conteúdo.

E vira a pergunta nº 1 da visita do consultor, que custa nada e responde tudo:
**"o que vocês fazem de mídia que não está na internet?"**

---

## Os outros pontos cegos (já registrados nos estudos)

1. **Quem ouviu o preço e foi embora sem escrever nada.** Nenhuma fonte pública
   tem essa voz.
2. **Grupos fechados** de WhatsApp e Facebook, onde parte do boca a boca acontece.
3. **Share real de receita.** O placar compara reputação, não faturamento.
4. **Lembrança de marca.** Só a rede pode medir, e nunca divulgou.

---

_Este documento é parte do método, não uma ressalva. Toda praça nova entra com
o seu bloco de mídia offline em branco — e branco declarado vale mais que
suposição._
