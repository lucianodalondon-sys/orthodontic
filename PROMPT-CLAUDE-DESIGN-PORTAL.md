# PROMPT MESTRE — Claude Design
## Portal de Inteligência OrthoDontic · visão da FRANQUEADORA

> Cole tudo abaixo no Claude Design, junto com o design system da OrthoDontic
> (skill `orthodontic-design`).

---

Construa o **ORTHODONTIC INTELLIGENCE** — o portal de inteligência de rede da
maior rede de ortodontia do Brasil, ~340 unidades. Não é dashboard de BI. É um
**centro de operações**: a franqueadora abre e vê o que está acontecendo nas
cidades onde suas unidades operam.

**A tese, em uma frase:**
> A rede sabe o que 340 unidades registraram no sistema dela. Não sabe o que 340
> praças estão fazendo com a marca. Este portal é o segundo olho.

---

## 0 · ESCOPO DESTA ENTREGA — leia antes de tudo

**Construa APENAS a visão da FRANQUEADORA.** A diretoria, a CEO e o conselho
(holding de private equity).

As visões do **consultor de campo** e do **franqueado** virão depois. Não as
construa, não faça o seletor de perfil, não desenhe as telas delas.

Mas **projete como se elas fossem existir**, porque vão:
- nada na interface deve **ranquear franqueado nominalmente de forma humilhante**
— o dado é frio, a comparação é entre unidades, e a linguagem nunca acusa;
- todo número de unidade aparece **com a ação recomendada ao lado**, nunca
  sozinho. Essa é a regra que vai permitir o franqueado entrar depois sem que o
  produto seja lido como instrumento de cobrança.

---

## 1 · DESENHAR PARA 340, MOSTRAR 4 — a decisão mais importante

Hoje existem **4 praças com inteligência e 336 sem**. Uma tela desenhada para 4
quebra quando chegar a 340; uma desenhada para 340 funciona com 4.

### O que isso obriga

**Nada é uma lista fixa.** Toda coleção de unidades é uma **grade filtrável, com
busca e ordenação**, projetada para 340 linhas e exibindo 21. Se um componente
só faz sentido com 4 itens, ele está errado.

**A ficha da praça é ALCANÇADA, não navegada.** Ninguém vai rolar 340 fichas. Os
caminhos até ela são três: um alerta, uma busca, ou um filtro. O trilho
lateral tem **busca global (⌘K)** como elemento de primeira classe, não enfeite.

**Filtros sempre visíveis** — é assim que a diretoria pensa e é a
língua da casa:
`região` · `porte de cidade` · `safra` (ano de abertura) · `unidade madura` ·
`status de inteligência` (estudada / em coleta / não ouvida)

**Alertas são AGRUPADOS por tipo, não empilhados.** Com 340 unidades, "silêncio
no o que dá para ver na internet" vira 40 alertas iguais. O cartão diz **"12 unidades em
silêncio no pico regional"** e abre a lista. Nunca 12 cartões idênticos.

**Comparação é o verbo principal.** O número de uma unidade só significa alguma
coisa contra as unidades parecidas com ela. Toda métrica na ficha aparece com a referência ao
lado: *"0,7 review/mês — mediana das unidades parecidas: 4,1"*.

### O estado padrão é a ignorância — e isso é a história

**336 de 340 praças não têm dado nenhum.** Não esconda, não preencha com cinza
apagado envergonhado. É a narrativa de crescimento do produto e o argumento de
venda mais forte que existe.

Desenhe um **medidor de cobertura** persistente no topo:
`4 / 340 praças ouvidas` com barra de progresso, sempre visível.

E uma tela dedicada, **"A rede que ainda não ouvimos"**, com as 336 e um critério
de priorização — qual praça estudar em seguida e por quê (região não coberta,
porte não coberto, safra não coberta). Campo vazio declarado vale mais que
suposição.

---

## 2 · SISTEMA DE DESIGN

Invoque a skill **`orthodontic-design`**. Linke `styles.css`. Use os logos reais
de `assets/logos/` — **nunca redesenhe a marca**.

### Use como está
Gotham (300/400/500/700/900) · cyan `#00B9FF` + navy `#001E78` · botões pill ·
sombras com tinta navy · brilho cyan (`--shadow-cyan`) em CTA e estado ativo ·
anel de foco cyan 3px · motivo dos anéis concêntricos · vidro (`--glass-fill`).

### O mundo escuro já existe na marca — não invente outro
O sistema tem `--grad-navy` (`#16307F → #001E78 → #001A5C`) e
`--surface-inverse-deep`. **O portal mora ali.**

- Plano da página `#001433` · superfície de painel `--od-navy-800 #001A5C` ·
  painel elevado `#02205F`
- Fio `rgba(255,255,255,.10)` · destaque `rgba(0,185,255,.28)`
- Texto branco · `rgba(255,255,255,.72)` · `rgba(255,255,255,.48)`
- Logo: `logo-horizontal-white.png` e `symbol-white.png`

Não é "um dashboard escuro". É a OrthoDontic no fundo do próprio gradiente dela.

### Os três conflitos do sistema — resolva assim

O readme marca as cores de estado como *adições*, não como manual. Há licença.

**1. `--color-info` É o cyan da marca.** Se o cyan for marca, ação primária,
estado ativo **e** informação, tudo lê como informação.
→ **Cyan é só marca, ação e estado ativo. Não é status.** Elimine "info".

**2. `--color-danger #E23D6D` está em cima do `--od-magenta #E8408D`.** Alerta
crítico ficaria com cor de CTA de campanha.
→ **Magenta não entra no portal.** Crítico sobe para `#FF5C5C`.

**3. Os quatro estados foram escolhidos para fundo branco.** Sobre `#001A5C`
precisam de novo degrau.

| Nível | Hex | Origem |
|---|---|---|
| Bom | `#3ED6B8` | `--color-success` clareado |
| Atenção | `#F8D65D` | `--od-yellow` |
| Grave | `#F5A057` | `--od-orange` |
| Crítico | `#FF5C5C` | `--color-danger` reescalonado |

**Regra: cor de estado nunca é cor de marca, e vice-versa.**

### Registro
**Arredondamento:** pill nos botões (definidor da marca), mas painel de dado em
`--radius-md 16px`. `xl`/`2xl` em painel de operação fica com cara de brinquedo.

**Voz:** o "você" caloroso com chips de benefício é para **paciente**. Aqui é
conselho. Use o registro que o próprio readme define para documentação:
**formal, preciso, instrucional.** Sem emoji, sem estrela, sem bolha.

**Tipografia de dado:** Gotham para títulos e números-herói. Uma **monoespaçada**
para valores, datas de corte, N, filtros e IDs — é o mono que dá instrumento.

---

## 3 · DIREÇÃO VISUAL E ATMOSFERA

**Sala de controle — não ficção científica, não Power BI.**

A linguagem é de **peça de engenharia flutuando no escuro, emitindo luz, com
dados em linhas finas ao redor** — telemetria de alta performance.

- **O fundo nunca é chapado.** Gradiente radial amplo, navy mais claro no alto e
  ao centro, escurecendo para `#000B24` nas bordas. Por cima, **grão a 3-4%** —
  é o grão que tira o aspecto de "div preta".
- **O objeto-herói flutua e emite luz.** O mapa do Brasil em **wireframe/nuvem
  de pontos cyan translúcido**, com **poça de luz radial** embaixo (cyan a ~12%,
  muito difusa). Não é mapa preenchido: é modelo técnico aceso no escuro.
- **Linhas de dado atravessam o espaço.** Curvas de 1px em cyan a 30-50%,
  cruzando áreas vazias com pontos marcados e rótulos minúsculos. A curva de
  sazonalidade vive assim — solta, não presa em caixa de gráfico.
- **Tipografia com ar.** Rótulos em caixa alta, `--tracking-wider`, peso leve,
  corpo pequeno. Títulos em Gotham Black, grandes, caixa alta, à esquerda.
  **Contraste de escala é o efeito principal.**
- **Numeração de capítulo** no canto direito, peso leve.
- **Réguas verticais finas** de 1px `rgba(255,255,255,.14)` nas bordas.
- **Botão circular com arco** parcial — **em cyan, nunca em vermelho**.
- **O motivo dos anéis concêntricos** (`--rings-soft`) como marca d'água enorme
  atrás do mapa. É o elemento da marca que mais parece radar.

> **A disciplina do vermelho:** vermelho é **exclusivamente crítico** (`#FF5C5C`).
> Se aparecer em botão ou detalhe por estética, o portal perde a capacidade de
> alarmar.

### Onde a atmosfera vale — e onde cede
**Vale integral** na home, no topo da ficha e nas transições. **Cede densidade**
nos painéis de trabalho — a fila de alertas, a grade das unidades, o placar. Um
portal bonito e vazio não sobrevive à segunda reunião.

### Evitar
Tabela como componente padrão · magenta e cores de campanha · neon genérico ·
emoji como ícone · cartão branco com sombra suave · **fundo chapado sem gradiente
e sem grão** · HUD, hexágono, linha de varredura.

---

## 4 · NAVEGAÇÃO

Aplicativo de página única com transição suave.

**Barra superior fixa (vidro fosco):** logo · **busca global ⌘K** · pílula de
cobertura `4 / 340` com barra · data da última coleta.

**Trilho lateral escuro:**
`Sala de Controle` · `Praças` · `Rede não ouvida` · `O que Aprendemos` ·
`Corretor de Campanha` · `Método`

**Controles que precisam existir e funcionar:** botão primário/secundário/
fantasma · pílulas de filtro · botões de escolha · busca com resultado ao vivo ·
gaveta lateral · modal · abas · tooltip em gráfico · seletor de período ·
**ordenação e filtro em toda grade**.

---

## 5 · TELA 1 — SALA DE CONTROLE

**Herói:** o mapa do Brasil ocupando a primeira dobra, como modelo técnico
luminoso. 340 pontos: **4 acesos em cyan com halo**, **336 apagados** em
`rgba(255,255,255,.14)`. Acesas: **Londrina/PR · Presidente Prudente/SP · Feira
de Santana/BA · Mafra/SC**. Hover num ponto aceso abre cartão de vidro.

Ao redor, no vazio, uma curva de dado de 1px com o pico marcado:
`JUL · ÍNDICE 34`.

À esquerda, contraste extremo de escala:

> `INTELIGÊNCIA DE REDE` *(rótulo minúsculo, caixa alta, muito espaçado)*
>
> # 4 DE 340 PRAÇAS OUVIDAS
>
> Sabemos o que acontece dentro das clínicas. Estamos começando a saber o que
> acontece em volta delas.

**Faixa de números-herói** (contagem animada na entrada):

| Valor | Rótulo |
|---|---|
| **8** | sinais abertos |
| **336** | praças ainda não ouvidas |
| **23** | dias entre a 1ª e a 2ª coleta |
| **3** | conclusões do estudo corrigidas pela 2ª coleta |

**Fila de alertas — cartões grandes, AGRUPADOS por tipo.** Cada um: faixa de
severidade, o que aconteceu, **o que fazer**, botão `Ver evidência`. Com 340
unidades cada cartão vira grupo; com 4, o grupo tem 1 ou 2 itens.

Os oito sinais, com o texto exato:

**CRÍTICO · Riomafra — Concorrente invadiu a categoria**
A clínica de nove meses ao lado, que só vendia prótese e implante, começou a
anunciar aparelho em julho, no pico anual da região. Entre 15/jul e 07/ago ela
foi de ~10 para 37 anúncios ativos.
*Fazer:* subir 4 a 6 anúncios sempre-ativos com rosto e parcela clara.

**CRÍTICO · Riomafra — A vizinha acelerou e a unidade ficou parada**
Em 23 dias a Lumière fez +33 avaliações (~43/mês) e a OrthoDontic fez **zero**.
A distância era 42; agora é 75.
*Fazer:* religar a máquina de avaliações — a unidade já fez 47 em três meses de
2022, sabe fazer.

**CRÍTICO · Riomafra — Agendamento a 5,9% contra régua de 40%**
De cada 100 interessados, seis viram avaliação agendada. Comparecimento (49%),
fechamento (75%) e pagamento (99%) batem ou superam a régua.
*Fazer:* blindar a linha de frente — resposta em minutos, fluxo em vez de rajada.

**ATENÇÃO · Rede — Responde tudo, resolve menos**
No Reclame Aqui a rede tem **3.133 reclamações**, responde **98,6%** e está com
selo **GREAT**. Vai muito melhor que as gigantes: a OdontoCompany tem 23.283
reclamações, responde 67,7% e está como **NÃO RECOMENDADA**; a Sorridents tem
11.425 e responde 45%.
O buraco não é responder, é **resolver**: 86,4% resolvidas e **63,3%** que
voltariam a fazer negócio, contra 96,3% e 76,6% da Odontoclinic, que tem selo
RA1000. Três redes menores têm RA1000 e a OrthoDontic não.
*Fazer:* fechar a distância de resolução até o RA1000. Responder já está feito.

**GRAVE · Londrina — A matriz perde o maior volume da cidade em ~2 meses**
Odontoclinic +14/mês contra +4/mês da matriz. A distância caiu de 28 para 20
avaliações.
*Fazer:* ligar a máquina de avaliações na matriz — hoje ela responde 0% das
avaliações que recebe.

**GRAVE · Rede — A OrthoDontic é a única rede fora da busca paga**
No Centro de Transparência do Google: OdontoCompany 35 anúncios (10 da própria
franqueadora), Odontoclinic 15, Sorrifácil 1, **OrthoDontic 0** — em quatro
variantes de nome. Quanto tempo os anúncios dela ficam no ar: mediana de 104 dias no ar, um
criativo com 864 dias.
*Fazer:* decisão de franqueadora. Verificar a conta de Google Ads da rede antes
de concluir.

**GRAVE · Feira — O gigante corre, a unidade está estacionada**
Moisés Suzart +30 em 23 dias (~39/mês) contra ~2/mês da unidade.
*Fazer:* máquina de avaliações. A unidade já fez 17 num único mês em jul/2025.

**ATENÇÃO · Rede — Três de cinco unidades respondem 0% das avaliações**
Londrina matriz 0% · Prudente 0% · Feira 4% · Riomafra 52% · Londrina Centro 61%.
*Fazer:* rotina de resposta. Custa zero e a unidade executa sozinha.

---

## 6 · TELA 2 — FICHA DA PRAÇA

Alcançada por alerta, busca ou filtro. **Nunca por rolagem de lista.**

**Cabeçalho:** nome grande, cidade em mono, a tese em destaque, e à direita
quatro medidores redondos — nota, avaliações, reviews novos/mês, anúncios ativos —
**cada um com a mediana das unidades parecidas marcada no arco**.

Abaixo do cabeçalho, um **botões para trocar o período**: `15/jul` · `07/ago` ·
`comparar`.

### Riomafra — Mafra/SC · Rio Negro/PR
**Tese:** *"A melhor clínica da cidade é a mais calada."*

**Ponteiros:** nota **4,9** (meta 4,8) · avaliações **155** · novas/mês **0,7**
(meta 15) · anúncios **3** *(era 0 em 15/jul)* · agendamento **5,9%** (régua 40%)
Base: 452 vozes + 2ª coleta em 07/ago.

**O funil contra a régua** — a peça visual mais importante. Cinco estágios, os
que batem em verde, o quebrado em vermelho e maior:

| Estágio | Real | Régua |
|---|---|---|
| Interessados | 5.050 | — |
| Agendamentos | 298 · **5,9%** | **40%** |
| Comparecimentos | 147 · 49,3% | 50% |
| Fechados | 110 · 74,8% | 80% |
| Pagos | 109 · 99,1% | 90% |

Ao lado, em destaque: **"Quem chega, fecha. Quem chama, some."**
*Ressalva obrigatória em nota:* as contas não fecham — 109 pagos contra
~336 contratos/ano na mesma unidade. O multiplicador projetado não é publicado.

**Velocidade de reputação** — barras horizontais, a nossa em cor de marca:
Lumière **43/mês** · Edgard Góes **16** · Cuidado e Prevenção **4** ·
OdontoCompany Mafra **1** · **OrthoDontic Mafra 0**
*Legenda:* a unidade somou 10 avaliações em 14 meses; a vizinha fez 33 em 23 dias.

**O placar (07/ago)** com a variação desde 15/jul:
OdontoCompany Mafra 4,6 · 339 (+1, e a nota **caiu** de 4,7) ·
Instituto Lumière 5,0 · 230 (**+33**) · OdontoCompany Rio Negro 4,7 · 188 (0) ·
**OrthoDontic Mafra 4,9 · 155 (0)** · Cuidado e Prevenção 4,9 · 138 (+3) ·
Edgard Góes 5,0 · 115 (+12)

**A temporada:** colunas JUL **34** (pico) · AGO **23** · SET **22** · DEZ/JAN
**2,5-7,9** (vale).
*Legenda:* dez/jan é vale aqui — a tese nacional não vale no planalto, e foi esta
praça que a derrubou.

**A mídia da unidade** — os 3 anúncios que subiram desde 15/jul:
um sem texto, um *"Se liga nessa novidade que preparamos pra você! 🩵"*, e um
sobre manutenção de aparelho.
*Leitura:* **nenhum tem rosto, nenhum tem parcela** — o plano pedia os dois. E o
terceiro fala com quem **já é paciente**. Enquanto isso, 22 dos 27 anúncios da
Lumière são de **acolhimento**, o registro que o estudo recomendou para nós.

**O DNA local** — cartões, um marcado como proibição:
- **A língua:** o falar do planalto — "piá", chimarrão, inverno de verdade. E
  dizer **Riomafra**: a praça é uma colônia partida pela divisa, com ônibus
  urbano cruzando a ponte.
- **Temperamento:** colônia discreta. Desconfia de promessa grande; respeita
  trabalho, constância e palavra cumprida.
- **A alavanca:** prova antes de promessa. Parcela clara.
- **A joia enterrada:** o casal de ortodontistas que voltou pra casa em 2019. De
  2 para 9 especialistas. Sobrenome da colônia no mapa das duas cidades — e
  ausente do feed.
- **NUNCA DIZER:** hype, urgência de liquidação, "última chance". Nunca gíria gaúcha
  nem estética de Oktoberfest.

**Vozes reais** — carrossel, tipografia de destaque:
> "A melhor clínica e os melhores dentistas!!!" — seguidor
> "Ótimo atendimento, preço justo e lugar aconchegante." — paciente
> "falta de comunicação entre a equipe… fiquei 1 mês sem manutenção" — a única
> ferida, e é operacional

**O plano de 90 dias** — 7 ações com estado. Marque o que a 2ª coleta observou:
1. Blindar manutenção e retenção — 15 dias — *sem sinal*
2. Ligar a máquina de avaliações (≥15/mês) — 15 dias — **não executado** (0 em 23 dias)
3. Destravar o rosto — 30 dias — *sem sinal nos anúncios*
4. Reocupar a especialidade no feed — 30 dias — **rever: o feed já é 45% ortodontia**
5. Entrar na mídia paga JÁ — 7-14 dias — **executado, conteúdo fora do briefing**
6. Reivindicar as duas margens — 60 dias — *sem sinal*
7. Parcerias de comunidade — 90 dias — *sem sinal*

### ⚠ BLOCO OBRIGATÓRIO EM TODA FICHA — "O que não estamos vendo aqui"

Painel fixo, ao lado do placar de mídia. **Não é rodapé, é conteúdo.**

> **A coleta só enxerga o que fica público na internet.** Não vemos:
> **rádio** — em Riomafra são 3 emissoras fortes, uma da paróquia, e um único
> balcão vende 3 das 4 frequências · **TV aberta** · **outdoor, panfleto,
> fachada** · **patrocínio de comunidade** — a unidade patrocina os escoteiros ·
> **parceria com escola e convênio** · **indicação e boca a boca**, que os quatro
> estudos apontam como *o* canal de decisão.
>
> `Quem preenche: a unidade.` `Status: não medido.`

E o rodapé do bloco:
*"Moisés Suzart cresce ~39 avaliações/mês em Feira sem comprar busca e sem
responder avaliação. Nas nossas fontes ele não faz nada que explique o
crescimento. Isso não é paradoxo — é a medida do que não vemos."*

### As outras três praças (dados para as fichas)

**Londrina — Souza Naves, a MATRIZ.** *"A coroa que está escorregando."*
4,6 · **564** (+3 em 23 dias). Odontoclinic 4,9 · **544** (+11) — **a distância
caiu de 28 para 20; ultrapassa em ~2 meses.** Filial do Centro: 3,8 · 76, **sem
publicar desde março/2026**. Atendimento em 65% dos reviews. **A matriz responde
0% das avaliações; a filial do Centro responde 61%** — a de pior nota é a que
mais responde. Engajamento: **mediana de 1 curtida** por post, contra 15 da
Odontoclinic. Feed: **93% ortodontia**. Joia: é a matriz, tocada por quem fundou
a rede, na cidade onde a marca nasceu em 2002 — não aparece na comunicação.
Língua: orgulho de raiz e tradição, fé e família, consumo por indicação.
Alavanca: confiança + preço justo — barato levanta suspeita.
Citações: *"sempre me senti acolhido e hoje, ao fim do tratamento, me sinto muito
realizado. Consigo sorrir novamente"* · *"Dr. João nota 10, excelente doutor"* ·
*"Graças a Deus li os comentários!!!"* (mãe buscando dentista).
**Concorrente novo, nunca visto nos estudos: Classdent, 19 anúncios ativos.**

**Feira de Santana — o Centro.** *"Todos os caminhos levam à Feira. Menos o da
própria clínica."*
4,7 · **170** (–3 · limpeza do Google, não represália; entraram 2 em julho).
Ritmo: **~2/mês**. Moisés Suzart 4,9 · **1.298** (+30 · ~39/mês) — **e ele não
compra busca nem responde avaliação**. Atendimento em 65%. Responde 4%. Feed 57%
ortodontia, mediana 3 curtidas. Histórico: **17 avaliações em jul/2025**, pico
isolado. 616 mil hab., maior que 8 capitais.
Língua: baianês de sertão — "oxe", "meu rei", "massa", "arrochar".
Alavanca: **preço como ORGULHO** — "pagar menos e sair por cima é virtude".
**Joia: NENHUMA ainda** — a unidade é invisível fora do Google. *Mostre o campo
vazio como informação, não como falha.*
JAMAIS: axé litorâneo de vitrine.
Citações: *"Preço acessível e me trataram como gente. Amei."* · *"marca horário e
atende 2, 3, 4 horas depois"*.

**Presidente Prudente — a 1ª FRANQUIA da rede, 02/05/2005.** *"O tesouro guardado
na gaveta."* **A praça mais saudável.**
4,9 · **592** (+10 · ~13/mês, a melhor da rede) — **deve ultrapassar a NEXA (619)
em volume em ~2 meses.** Das 84 avaliações com texto: **83 de cinco estrelas, 1
de uma, zero no meio.** Atendimento em 58%. **Responde 0%.** Feed 71%
ortodontia, mediana 2 curtidas. A NEXA responde 100% e cresce 1,3/mês.
Língua: superlativo local. **A régua de tom a cidade entregou: "que tratem as
pessoas com dignidade e humanismo"** — o comentário mais curtido do corpus.
Alavanca: **CLAREZA, não preço.**
Joia: a primeira franquia de toda a rede, aberta por dois prudentinos.
Citações: *"Já passei por lá — e agora são meus filhos."* · *"explicam tudo
direito"* · *"me lembro do dia 02/05/2005, dia da inauguração!!"*.

---

## 7 · TELA 3 — A REDE QUE AINDA NÃO OUVIMOS

Tela dedicada às **336**. Grade filtrável projetada para 340 linhas.

Topo: `4 / 340` com barra, e o texto:
> **336 praças sem inteligência nenhuma.** Não sabemos quantas repetem o
> vazamento de Riomafra, quantas estão em silêncio no pico, quantas têm uma
> vizinha de nove meses ao lado.

**Critério de próxima praça** — cartões com o que falta cobrir:
`Norte: 0 praças` · `Centro-Oeste: 0` · `Capital: 0` · `Unidade recém-aberta: 0` ·
`Sudeste: 1` · `Sul: 2` · `Nordeste: 1`

*Legenda:* a amostra atual não cobre Norte, Centro-Oeste, capital nem unidade
nova. **É por isso que nenhum achado pode virar doutrina ainda.**

---

## 8 · TELA 4 — O QUE APRENDEMOS

Desenhe como **laboratório**, não como lista.

**A escada dos achados no topo**, esteira horizontal. Use exatamente estas
palavras — ninguém precisa de legenda para entender:

`SINAL ISOLADO (0)` → `SE REPETE (13)` → `VALE PARA A REDE (0)` →
`VIROU REGRA (0)` · fora da esteira: `❌ CAIU (2)`

Com a explicação de cada degrau em letra pequena embaixo:
*sinal isolado = vimos em 1 ou 2 praças · se repete = vimos em 3 ou mais ·
vale para a rede = vimos em praças bem diferentes entre si · virou regra = a
rede decidiu agir · caiu = uma praça mostrou o contrário*

*Legenda da tela:* nada aqui virou regra ainda. Só ouvimos 4 praças, e elas não
cobrem Norte, Centro-Oeste, capital nem unidade nova.

**Os treze achados que se repetem** — cada um com quantas praças confirmam:

1. **O paciente não avalia ortodontia — avalia como foi tratado.** 4/4 ·
   Riomafra 66% · Feira 65% · Londrina 65% · Prudente 58% *(847 avaliações com texto, as quatro medidas do mesmo jeito)*
2. **A ferida é sempre operação, nunca o produto.** 4/4 · e o Reclame Aqui
   confirma: 3.133 reclamações, 98,6% respondidas, selo GREAT
3. **A confiança é em gente com nome.** 4/4
4. **A porta de entrada é "quanto custa / cabe na parcela?", depois "dói?".** 4/4
5. **Julho é o pico da mãe-decisora.** 4/4
6. **O adulto 30+ é dinheiro na mesa e nenhuma praça fala com ele.** 4/4
7. **A clínica-escola é fraca onde a rede é forte.** 4/4
8. **A joia local existe, é incopiável — e está enterrada.** 3/4 *(Feira não tem)*
9. **A prova social está parada em todas.** 4/4
10. **A mãe é a decisora — e lê os reviews antes de escolher.** 4/4
11. **A ordem certa é blindar a operação antes de mídia nova.** 4/4
12. **A rede não responde.** 4/4 · 0% · 0% · 4% · 52%
13. **As unidades sabem fazer campanha de avaliação — e não sustentam.**
    Riomafra fez 47 em 3 meses de 2022; Feira fez 17 em jul/2025. Depois, quase
    nada.

**As duas derrubadas, em tratamento gráfico de "crença que caiu":**

> ❌ **"Dezembro e janeiro são pico nacional"**
> Caiu por causa de Riomafra. Série de 5 anos: julho 34, dez/jan 2,5-7,9. Confirmado
> pelo BI: 494 e 78 interessados contra 4.120 em julho/25.
> *Custou centavos de coleta e evitou verba nacional no mês errado.*

> ❌ **"Quanto menor a cidade, mais o paciente fala de atendimento"**
> Caiu quando medimos as quatro do mesmo jeito. A sequência 47·54·63·69
> comparava **coletas de tamanhos diferentes, não cidades diferentes**. Medindo
> igual, todas ficam entre 58% e 66% e a ordem por tamanho de cidade some.

E um cartão menor, de rodapé da tela:
> ❌ **"Quem responde avaliação é quem cresce"** — a gente levantou e derrubou no
> mesmo dia. **Não tem relação nenhuma:** Moisés Suzart cresce ~39/mês
> respondendo **0%**; a NEXA responde **100%** e cresce 1,3/mês.

**As variáveis — o que jamais pode ser nacionalizado.** Quatro colunas visuais,
uma por praça:

| | Londrina | Prudente | Feira | Riomafra |
|---|---|---|---|---|
| Alavanca de preço | confiança + preço justo | clareza | preço como orgulho | palavra cumprida |
| Posição | desafiante | **líder** | desafiante, 7x atrás | melhor nota, 4ª em volume |
| O inimigo | clínica geral | vácuo competitivo | doutor pessoa física | rede popular + startup |
| O que nunca dizer | urgência de liquidação | corporativês | axé litorâneo | gíria gaúcha, Oktoberfest |

---

## 9 · TELA 5 — CORRETOR DE CAMPANHA

**A tela que a franqueadora compra primeiro**, porque mede o trabalho dela.

Campo de texto grande com uma peça real dentro:
> 🚨 SEMANA DO APARELHO! Últimos dias com condição especial. Aparelho sem
> entrada — agende agora mesmo sua avaliação!

Botão primário: **`Analisar contra as praças ouvidas`**. Resultados entram em
sequência animada. *(Com 340 praças, o resultado seria agrupado por perfil de
praça, não 340 cartões — desenhe já pensando nisso.)*

**Londrina — ⚠️ RISCO.** Meio de funil: preço baixo levanta suspeita. A matriz
briga na autoridade, não no preço. → *"tratado por quem criou o padrão"*

**Prudente — 🟡 ADAPTAR.** A alavanca é clareza. A régua de tom que a cidade
entregou foi "dignidade e humanismo". → *"você entende tudo antes de decidir"*

**Feira — 🟢 FUNCIONA, COM CONDIÇÃO.** Preço é orgulho. Mas precisa falar como
Feira, e a unidade já está num coro de 59 anúncios quase idênticos. →
*"cabe no seu bolso, meu rei"*

**Riomafra — 🔴 CONFLITO.** "Últimos dias" aciona o radar antivigarista da
colônia. → *bloqueado: urgência de liquidação*

**Abaixo, "A campanha nacional chega à cadeira?"** — três barras longas e quase
vazias, número enorme ao lado:
- Publicações de unidade com o embaixador: **1 de 156**
- Criativos nacionais com o jingle: **1 de 34**
- Menções espontâneas ao embaixador: **0 de 2.834 vozes**

*Legenda:* oito anos de embaixador. O jingle está **subusado, não gasto**.

---

## 10 · A GAVETA DE EVIDÊNCIA

Todo número abre uma **gaveta lateral com vidro fosco**. É o que separa isto de
um dashboard: um dashboard afirma; um portal de inteligência mostra de onde
tirou e o que ainda não sabe.

Exemplo, o agendamento de Riomafra:
- **5,9%** em tipografia enorme
- *dos interessados viram avaliação agendada — a régua espera 40%*
- Selo **confiança: média**
- **A leitura:** o único estágio quebrado. Comparecimento bate a régua;
  fechamento e pagamento estão acima. A cadeira e o contrato funcionam — o vão
  está entre a primeira mensagem e a agenda.
- **O que pesa contra** (bloco em cor de atenção): as contas não fecham —
  109 pagos contra ~336 contratos/ano na mesma unidade. Enquanto não fechar, o
  multiplicador projetado não é publicado.
- Ficha técnica em mono: `N 5.050 · 298` · `corte jul/2026` ·
  `fonte dados/serie/funil.jsonl` · `filtro local_id=ortho_mafra`

---

## 11 · MOVIMENTO

Tokens do sistema: `--dur-fast 120ms` · `--dur 200ms` · `--dur-slow 360ms` ·
`--dur-slower 600ms`, com `--ease-out` nas entradas.

- **Entrada orquestrada:** o mapa acende, os quatro pontos acendem em sequência,
  os números contam, os cartões sobem escalonados.
- **Troca de tela:** deslize e fade curtos, nunca corte seco.
- **Hover:** brilho de borda cyan; barras clareiam; o ponto expande o halo.
- **Alertas críticos:** o halo respira **três vezes e para**. O sistema proíbe
  movimento decorativo infinito.
- **Gráficos:** desenham na entrada.
- `--ease-bounce` só em botão. Nunca em dado.
- Respeite `prefers-reduced-motion`.

---

## 12 · TRAVAS

1. **Não invente número.** Todo dado está aqui. Se faltar, mostre o estado
   vazio — as 336 praças sem dado e a joia inexistente de Feira são decisões de
   produto, não pendências.
2. **Não reescreva citação de paciente.** São verbatim.
3. **Nenhum número de unidade sem a ação ao lado.**
4. **Não ranqueie franqueado de forma humilhante.** O tom nunca acusa.
5. **Cor de estado nunca é cor de marca.**
6. **Toda afirmação de mídia diz onde foi medida.** Nunca "a unidade está muda" —
   sempre **"ausente do o que dá para ver na internet"**. Nunca "cresce porque anuncia" —
   sempre "cresce; anuncia".
7. **Se a tela virou tabela sem filtro, busca e ordenação, refaça.**
8. **Se um componente só funciona com 4 itens, refaça para 340.**

---

## 13 · O TESTE FINAL

A diretoria abre isto numa reunião de conselho e a primeira reação tem que ser
**"como a gente não tinha isso?"** — não "que dashboard bonito".

A diferença está em quatro coisas: o mapa com **336 cidades apagadas**; o funil
que mostra onde o dinheiro vaza; a gaveta que prova cada número **inclusive
dizendo onde ele não fecha**; e o bloco que declara, em toda ficha, **o que não
estamos vendo**.
