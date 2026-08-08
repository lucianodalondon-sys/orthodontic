# Entrando numa praça nova

> O que era artesanal em quatro cidades vira processo. Sete etapas, na ordem —
> e a ordem importa: **primeiro a cidade, depois a clínica.** Quem começa pela
> clínica só enxerga o que a clínica já sabe.

**Tempo:** ~2 dias de trabalho, sendo ~4 horas de gente e o resto de coleta.
**Custo de coleta:** ~US$ 2 por praça.

---

## ETAPA 0 · Definir a praça (30 min, humano)

**A praça não é o município. É o raio real de onde vem o paciente.**

Riomafra ensinou isso do jeito difícil: Mafra/SC e Rio Negro/PR são **uma
cidade partida pela divisa dos estados** — mesmo DDD, ônibus urbano cruzando a
ponte, a mídia local inteira se chama "Riomafra". Tratar como duas cidades era o
erro do forasteiro.

Perguntas para fechar a praça:
- Tem cidade grudada do outro lado de rio, divisa ou rodovia?
- O ônibus urbano sai do município?
- A mídia local cobre as duas?
- O paciente atravessa para se tratar?

E o oposto também vale: **Londrina tem uma Zona Norte de 108 mil habitantes sem
unidade dentro.** Uma cidade pode ser praças diferentes.

**Saída:** `praca_id`, lista de cidades, e uma linha explicando por quê.

---

## ETAPA 1 · A cidade em números (automático)

```bash
python3 coleta/descobrir_praca.py --cidade "Campo Grande/MS"
python3 coleta/descobrir_praca.py --cidade "Mafra/SC" --mais "Rio Negro/PR" --id riomafra
python3 coleta/descobrir_praca.py --cidade "Campo Grande/MS" --sem-clinicas   # custo zero
```

Traz do IBGE, de graça: população (censo e estimativa), massa salarial e renda.
Depois grava o esqueleto de `dados/identidade/<praca>.json` e
`coleta/alvos/<praca>.yaml`.

Duas proteções que ele tem, e valem saber:

- **Ele se recusa a sobrescrever uma praça que já existe.** Aqueles arquivos
  guardam trabalho humano — os canais da cidade, o tipo de cada concorrente.
  Se precisar mesmo refazer, `--sobrescrever`.
- **Número que não vem, ele avisa.** Rede da máquina cai no IBGE de vez em
  quando; o script tenta três vezes e, se ainda assim não vier, escreve
  `⚠ não veio` em vez de deixar em branco. Número que some calado é pior que
  número errado — vira conclusão errada sobre a cidade.

**Falta buscar à mão** (10 min): quantos jovens de 9-15 e adultos de 30-45 —
é o tamanho real do alvo. Em Riomafra são ~7.700 contra ~21.000, e foi esse
número que mostrou que **o alvo maior é o menos falado**.

---

## ETAPA 2 · Quem fala com a cidade (1h30, humano — a etapa que não dá para pular)

Aqui está o miolo do método. São **nove tipos de canal**, e cada um responde
uma pergunta diferente. Procure de 8 a 14 perfis no total.

| # | Tipo de canal | O que ele entrega | Como achar |
|---|---|---|---|
| 1 | **A voz da cidade** — o maior perfil local | como a cidade fala, o que a move | busque `<cidade>` no Instagram e pegue o de maior seguidor |
| 2 | **A imprensa local** | a notícia, e a joia enterrada | Google News da cidade mostra os veículos |
| 3 | **A mãe** | **é ela quem decide o aparelho** | busque `maternidade <cidade>`, `mães de <cidade>` |
| 4 | **O preço / achadinho** | como a cidade fala de dinheiro | `ofertas <cidade>`, `promoções`, supermercado |
| 5 | **O humor local** | o que viraliza, a língua solta | `humor <cidade>`, `memes <cidade>` |
| 6 | **O jovem** | o público de 15-25 | perfis de festa, faculdade, evento |
| 7 | **A gastronomia / consumo** | onde a indicação converte | `onde comer <cidade>` |
| 8 | **A prefeitura** | onde o cidadão reclama e celebra | perfil oficial |
| 9 | **O esporte de base** | **o público de 9-15 COM os pais junto** | escolinha de futsal, futebol, vôlei |

### Duas regras que vieram dos quatro estudos

**O canal que NÃO existe é informação.** Em Riomafra não existe página de humor,
não existe mãe-influencer e não existe criador de vídeo local. Isso não é falha
da busca — é território vazio. **Quem chegar primeiro fala sozinho.** Anote os
que faltam.

**O nº 9 é o mais subestimado.** A escolinha de futsal junta exatamente o público
de 9 a 15 anos **com os pais na arquibancada** — decisor e paciente no mesmo
lugar, toda semana. Nenhuma outra mídia entrega isso.

**Saída:** `coleta/alvos/<praca>.yaml` com os perfis, cada um com o tipo.

---

## ETAPA 3 · Escutar a cidade (automático, ~US$ 0,50)

```bash
python3 coleta/coletores/instagram.py --praca <praca>
python3 coleta/coletores/imprensa_rss.py --praca <praca>
```

Meta: **800 a 1.400 vozes**. Foi o que as quatro praças renderam.

Depois: `python3 scripts/classificar.py` separa por assunto.

**O que sai daqui:** como a cidade fala (as palavras dela), o que ela premia, o
que ela detesta, e **o que nunca dizer** — o "axé litorâneo" que soaria falso em
Feira, a "gíria gaúcha" que queimaria em Riomafra.

---

## ETAPA 4 · O placar da categoria (automático, ~US$ 0,30)

O `descobrir_praca.py` já busca as clínicas de ortodontia da cidade e devolve
nota, volume e `place_id` de cada uma. Depois:

```bash
python3 coleta/coletores/google_reviews.py --praca <praca>
```

**O que olhar no placar, nesta ordem:**

1. **Quem lidera em VOLUME**, não em nota. Nota alta com volume baixo é o padrão
   da rede — e é o problema, não a virtude.
2. **O ritmo**: quantas avaliações novas por mês cada uma faz. É o dado mais
   revelador que existe. Em Riomafra a unidade fazia 0,7 e a vizinha 43.
3. **Que tipo de concorrente é cada um.** Muda tudo o que vem depois:
   rede popular · clínica geral bem avaliada · **doutor com nome próprio** ·
   clínica-escola · startup de tráfego pago · especialista de nicho.
4. **A clínica-escola.** Ela quase nunca faz aparelho de adolescente e adulto —
   é a brecha que apareceu nas quatro praças.

---

## ETAPA 5 · A clínica por dentro (automático, ~US$ 0,60)

```bash
python3 coleta/coletores/meta_ads.py --praca <praca>
python3 coleta/coletores/google_ads.py --praca <praca>
python3 coleta/coletores/instagram.py --praca <praca>
```

**As cinco perguntas que isso responde:**

1. **A unidade anuncia?** Em que plataforma, com que texto, há quantos dias.
   Ausência é resposta — e ausência **no pico da temporada** é alerta.
2. **O feed fala de aparelho?** Conta os posts. Não confie em olhar o perfil —
   foi assim que a gente errou em Riomafra.
3. **A unidade responde avaliação?** Três de cinco unidades respondem 0%.
4. **Tem rosto?** Quantos posts mostram gente. É o que mais separa quem cresce.
5. **Quanto engaja?** Mediana de curtidas. A matriz de Londrina tem **1**.

---

## ETAPA 6 · A joia enterrada (1h, humano + documental)

**O ativo local que ninguém pode copiar — e que quase sempre está escondido.**

Nas quatro praças: Londrina **é a matriz** da rede; Prudente foi a **primeira
franquia**; Riomafra tem **o casal de ortodontistas que voltou pra casa**. Feira
**não tem nenhuma** — e isso também é informação, muda a estratégia de
"desenterrar" para "construir".

Onde procurar:
- **imprensa local** (o coletor de RSS já traz) — foi de lá que saiu o casal de Riomafra
- **registro público de empresa** — ano de abertura, sócios, capital
- **o site e o "sobre" da unidade**
- **conversa com o franqueado** — a etapa mais barata e a mais pulada

E procure também a joia **do concorrente**: em Feira, o líder começou dentro de
uma grande franquia e depois personalizou tudo no próprio nome. Isso explica o
placar inteiro.

---

## ETAPA 7 · O que não vamos ver (30 min, declarado)

**Obrigatório.** A coleta só enxerga o que fica público na internet. Antes de
concluir qualquer coisa, registre o que ficou de fora:

rádio · TV local · outdoor e panfleto · patrocínio de time e evento · parceria
com escola e convênio · **indicação boca a boca**, que os quatro estudos apontam
como *o* canal de decisão.

**A pergunta que resolve, e é uma só:**
> **"O que vocês fazem de mídia que não está na internet?"**

Sem isso, a gente escreve "a unidade está muda" sobre uma clínica que pode estar
no rádio da cidade toda semana. Em Riomafra o rádio é canal forte — três
emissoras, uma da paróquia — e a unidade patrocina os escoteiros.

**Saída:** `dados/serie/midia_offline.jsonl` preenchido para a praça.

---

## ETAPA 8 · A INTELIGÊNCIA (automático — e nunca opcional)

```bash
python3 scripts/inteligencia.py --praca <praca>
```

**Coleta sem inteligência é dado parado.** Esta etapa não é um extra que se
faz quando sobra tempo: nenhuma praça vira dossiê sem passar por aqui.

O que o script obriga a olhar:

1. **O ritmo certo.** Se a amostra bateu no teto da coleta, a conta ingênua
   (total ÷ 12) mente para baixo. Em Cuiabá o número ingênuo dizia 12,5/mês
   para cinco clínicas ao mesmo tempo — o real era 45,6. **Teria feito a gente
   escrever que a unidade empata com os líderes quando ela lidera.** O script
   marca `⚠ amostra no teto` sozinho.

2. **Mais de uma unidade da rede na mesma praça.** Quando existe, é a
   comparação mais valiosa que o projeto tem: mercado, preço, marca e
   concorrência ficam controlados de graça. O que sobra é a unidade.

3. **As hipóteses vivas, recalculadas.** Toda praça nova pode matar um padrão
   antigo. Isso é resultado, não problema.

4. **O que pesa contra.** O script procura o contraexemplo de cada achado.
   Achado sem contraexemplo procurado não é achado, é torcida.

5. **Se a praça tem canais offline declarados.** Se não tem, ele avisa — porque
   sem isso "a unidade está parada" pode ser mentira sobre uma clínica que está
   no rádio da cidade toda semana.

---

## O QUE CUIABÁ ACRESCENTOU AO MÉTODO

A quinta praça mudou cinco coisas. Todas viraram item de checklist:

**Procure outras unidades da própria rede na praça.** Cuiabá tem três, e elas
fazem 45,6 · 3,7 · 0,7 por mês. Sessenta e cinco vezes, mesma marca, mesma
cidade. Nenhuma outra evidência chega perto disso — e a busca custa nada.

**O código da unidade no site da rede diz a ordem de abertura.**
`orthodonticbrasil.com.br/clinicas/...-478/` → unidade 478. Em Cuiabá a mais
antiga (151) é a que menos cresce. Serve para testar safra sem pedir dado
interno.

**Procure o concorrente que não cobra.** A prefeitura de Cuiabá instala
aparelho de graça pelo programa Siminina. Nenhuma das quatro praças anteriores
tinha concorrente público. Busque `<cidade> aparelho ortodôntico gratuito
prefeitura` e `programa municipal saúde bucal <cidade>`.

**Procure rede franqueada concorrente na biblioteca de anúncios.** A REDEORTO
apareceu com 37 anúncios em 16 cidades — uma rede inteira anunciando unidade
por unidade. Isso é assunto de franqueadora, não de unidade, e só aparece
quando se olha o anunciante e não a praça.

**Canal que não aparece na busca não é canal que não existe.** Em Cuiabá a
busca não achou perfil de mãe. Numa cidade de um milhão isso seria a maior
brecha já vista — mas uma busca rasa não prova território vazio. **Marque como
`nao_encontrado` e mande verificar à mão antes de virar conclusão.**

---

## O CHECKLIST DE ENTREGA

Uma praça só está pronta quando tem:

- [ ] a praça definida, com a justificativa do raio
- [ ] população, renda e o tamanho do alvo (9-15 e 30-45)
- [ ] 8 a 14 canais da cidade mapeados, com o tipo de cada um
- [ ] **os canais que NÃO existem, anotados**
- [ ] 800+ vozes coletadas e separadas por assunto
- [ ] como a cidade fala + **o que nunca dizer**
- [ ] o placar completo, com ritmo e tipo de cada concorrente
- [ ] a clínica-escola verificada
- [ ] a unidade por dentro: anúncios, feed, resposta, rosto, engajamento
- [ ] a joia enterrada — ou a declaração de que não tem
- [ ] o calendário: férias escolares do estado + festas da cidade
- [ ] **outras unidades da rede na mesma praça, comparadas entre si**
- [ ] o concorrente que não cobra (programa público, clínica-escola)
- [ ] rede franqueada concorrente na biblioteca de anúncios
- [ ] **o que não estamos vendo, declarado**
- [ ] **`scripts/inteligencia.py` rodado — sem isso não vira dossiê**
- [ ] ponto de partida congelado com data, para a próxima coleta comparar

---

## COMO ESCOLHER A PRÓXIMA CIDADE

Não é por tamanho nem por quem gritou mais alto. É por **o que falta na
amostra** — cada praça nova precisa ensinar algo que as outras não ensinam.

Hoje temos 4 de 340, e a amostra tem buracos grandes:

| Falta | Situação |
|---|---|
| **Norte** | nenhuma praça |
| **Centro-Oeste** | nenhuma praça |
| **Capital** | nenhuma — as quatro são interior |
| **Unidade recém-aberta** | nenhuma — a mais nova tem 7 anos |
| Sudeste | 1 (Prudente) |
| Sul | 2 (Londrina, Riomafra) |
| Nordeste | 1 (Feira) |

**A próxima praça ideal:** capital ou região metropolitana, no Norte ou
Centro-Oeste, com unidade de safra recente. Uma praça assim sozinha vale mais
que três parecidas com as que já temos — porque é ela que vai dizer se os treze
padrões valem para a rede ou só para o interior do Sul e Sudeste.
