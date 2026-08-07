# PROMPT MESTRE — Claude Design
## Portal de Inteligência OrthoDontic

> Cole tudo abaixo no Claude Design, junto com o design system da OrthoDontic.

---

Construa o **ORTHODONTIC INTELLIGENCE** — o portal de inteligência de rede da
maior rede de ortodontia do Brasil (~340 unidades). Não é um dashboard de BI.
É um **centro de operações**: a franqueadora abre isto e vê o que está
acontecendo nas cidades onde suas unidades operam, em tempo quase real.

**Quem abre:** a CEO, a diretoria e o conselho (holding de private equity), os
consultores de campo, e os franqueados — cada um vendo o seu nível.

**A tese do produto, em uma frase:**
> A rede sabe o que 340 unidades registraram no sistema dela. Não sabe o que
> 340 cidades estão fazendo com a marca. Este portal é o segundo olho.

---

## 1 · SISTEMA DE DESIGN

Invoque a skill **`orthodontic-design`**. Linke `styles.css` (traz todos os
tokens e a Gotham). Use os arquivos reais de logo em `assets/logos/` — **nunca
redesenhe a marca**.

### Use exatamente como está

Gotham (300 Light · 400 Book · 500 Medium · 700 Bold · 900 Black) ·
cyan `#00B9FF` + navy `#001E78` · botões pill · sombras com tinta navy, nunca
cinza neutro · brilho cyan (`--shadow-cyan`) nos CTAs primários e no estado
ativo · anel de foco cyan de 3px · o motivo dos anéis concêntricos ·
superfícies de vidro (`--glass-fill`, `--glass-blur`).

### O mundo escuro já existe dentro da marca — não invente outro

O sistema já tem o gradiente `--grad-navy` (`#16307F → #001E78 → #001A5C`) e os
tokens `--surface-inverse` e `--surface-inverse-deep`. **O portal mora ali.**
Não construa uma paleta escura nova: estenda a ponta navy do gradiente da marca.

- **Plano da página:** `#001433` — um degrau abaixo de `--od-navy-800 #001A5C`
- **Superfície de painel:** `--od-navy-800 #001A5C`, com o painel elevado em
  `#02205F`
- **Fio de borda:** `rgba(255,255,255,.10)`; borda de destaque `rgba(0,185,255,.28)`
- **Texto:** branco · `rgba(255,255,255,.72)` · `rgba(255,255,255,.48)`
- **Logo:** `logo-horizontal-white.png` e `symbol-white.png` — existem
  exatamente para isto

O resultado não é "um dashboard escuro". É a OrthoDontic no fundo do próprio
gradiente dela.

### Os três conflitos do sistema — e como resolver

O sistema foi desenhado para campanha de paciente em fundo claro. Três coisas
quebram num produto de operação, e o próprio readme marca as cores de estado
como *adições*, não como manual — então há licença para ajustar.

**1. `--color-info` É o cyan da marca.** Neste produto o cyan é a cor da marca,
do botão primário e do estado ativo. Se também for "informação", tudo na tela
lê como informação.
→ **O cyan fica reservado para marca, ação primária e estado ativo. Não é
status.** Elimine o nível "info" do conjunto.

**2. `--color-danger #E23D6D` está praticamente em cima do `--od-magenta
#E8408D`.** Um alerta crítico ficaria com a mesma cor de um CTA de campanha.
→ **O magenta não aparece no portal.** Ele pertence ao mundo de campanha. E o
crítico sobe para um vermelho que soa alarme sobre navy.

**3. Os quatro estados foram escolhidos para fundo branco.** Sobre `#001A5C`
eles precisam de novo degrau para segurar contraste.

**O conjunto de estado do portal, sobre navy:**

| Nível | Hex | Origem |
|---|---|---|
| Bom | `#3ED6B8` | `--color-success #2FB39B` clareado para o fundo escuro |
| Atenção | `#F8D65D` | `--od-yellow`, funciona como aviso e não colide com nada |
| Grave | `#F5A057` | `--od-orange`, secundária da marca, intacta |
| Crítico | `#FF5C5C` | `--color-danger` reescalonado — longe do magenta, alarme sobre navy |

**Regra:** cor de estado nunca é cor de marca, e cor de marca nunca é estado.

### Duas adaptações de registro

**Arredondamento.** A marca arredonda tudo. Mantenha **pill nos botões** — é
definidor da marca. Mas painéis de dado usam `--radius-md 16px`, nunca `xl` ou
`2xl`: arredondamento generoso em painel de operação fica com cara de brinquedo.

**Voz.** A voz de "você", calorosa, com chips de benefício e reações em emoji, é
para **paciente**. Este portal é interno, para um conselho. Use o registro que o
próprio readme define para documentação: **formal, preciso, instrucional.** Sem
emoji, sem estrela de avaliação, sem bolha de benefício.

**Tipografia de dado.** Gotham para títulos e números-herói. Some uma
**monoespaçada** para valores, datas de corte, N, filtros e IDs — é o mono que
dá cara de instrumento. Sem ele, vira relatório.

---

## 2 · DIREÇÃO VISUAL

**A referência é sala de controle — não ficção científica, não Power BI.**
Profundo, calmo, e quando algo precisa de atenção, aquilo se destaca sozinho.

### O que fazer

- **Profundidade real.** Painéis flutuam sobre o plano navy com fio de 1px,
  sombra navy difusa (`--shadow-lg`) e um gradiente interno quase imperceptível.
  Vidro fosco na barra superior e nas gavetas — a marca já tem esse material.
- **Números-herói gigantes** em Gotham Black (`--fw-black`), até `--text-7xl`,
  com contagem animada na entrada. O `5,9%` do agendamento tem que doer na tela.
- **O motivo dos anéis concêntricos** (`--rings-soft`) como marca d'água enorme
  atrás do mapa. É o elemento da marca que mais parece radar — use isso.
- **O mapa é o herói da home.** Brasil em navy profundo, 340 pontos. Quatro
  acesos em cyan com halo; 336 apagados em `rgba(255,255,255,.14)`. Conta a
  história inteira do produto sem uma palavra.
- **Sparkline em tudo que tem série**, ao lado do número.
- **Medidores radiais e trilhas de medição** no lugar de mais tabelas.

### O que evitar

- **Tabela como componente padrão.** Se a tela virou grade de linhas e colunas,
  está errada. Tabela só onde comparação item a item é o conteúdo — e mesmo lá,
  com barra embutida, marca de estado e linhas grandes e clicáveis.
- Magenta e as demais cores de campanha. Neon genérico de dashboard. Emoji como
  ícone. Cartão branco com sombra suave.
- Densidade de planilha. **Respiro é sinal de confiança.** Menos elementos,
  maiores.
- Ficção científica literal: HUD, hexágono, linha de varredura, fonte angular.

---

## 3 · ESTRUTURA E NAVEGAÇÃO

Aplicativo de página única, quatro áreas, transição suave entre elas.

**Barra superior fixa (vidro fosco):** logo · busca global (`⌘K`) · pílula de
cobertura `4 / 340 praças` com barra de progresso · data do corte · seletor de
perfil (Franqueadora / Consultor / Franqueado) · avatar.

**Trilho lateral esquerdo, escuro, ícones + rótulo:**
`Sala de Controle` · `Praças` (expande nas 4) · `O que Aprendemos` ·
`Corretor de Campanha` · `Método e Cobertura`

**Controles reais que precisam existir e funcionar visualmente:** botão primário
e secundário, botão fantasma, pílulas de filtro selecionáveis, controle
segmentado (períodos), busca com resultados ao vivo, alternador de tema,
gaveta lateral, modal, abas, tooltip no gráfico, menu suspenso, seletor de
período.

---

## 4 · TELA 1 — SALA DE CONTROLE

**Herói:** mapa do Brasil ocupando a maior parte da primeira dobra. Fundo
escuro, 340 pontos discretos, quatro acesos com halo pulsante nas cidades:
**Londrina/PR · Presidente Prudente/SP · Feira de Santana/BA · Mafra/SC**.
Passar o mouse num ponto aceso abre um cartão flutuante com nota, avaliações e
sinais abertos.

Sobreposto ao mapa, canto superior esquerdo, texto grande:

> **4 de 340 praças ouvidas.**
> Sabemos o que acontece dentro das clínicas. Estamos começando a saber o que
> acontece em volta delas.

**Faixa de números-herói** logo abaixo (contagem animada):

| Valor | Rótulo |
|---|---|
| **7** | sinais abertos |
| **4** | praças com inteligência ativa |
| **336** | praças ainda não ouvidas |
| **1** | crença da rede derrubada por dado |

**Fila de sinais** — cartões grandes, não linhas de tabela. Cada cartão: faixa
de severidade colorida, cidade, título, o que aconteceu, **o que fazer**, e um
botão `Ver evidência`. Os três críticos pulsam.

Os sete sinais, com o texto exato:

**CRÍTICO · Riomafra — Concorrente invadiu a categoria**
A clínica de nove meses ao lado, que só vendia prótese e implante, começou a
anunciar aparelho em julho, no pico anual da região.
*Fazer:* subir 4 a 6 anúncios sempre-ativos com rosto e parcela clara. 7 a 14 dias.

**CRÍTICO · Riomafra — Silêncio no pico**
Zero anúncios ativos, e zero no histórico da biblioteca, enquanto a busca da
região está no índice 34 — o topo da série de cinco anos.
*Fazer:* programar as duas ondas de férias. Margem PR até 27/07, margem SC de
23/07 a 02/08. O criativo troca de margem no dia 23.

**CRÍTICO · Riomafra — Agendamento a 5,9% contra régua de 40%**
De cada 100 interessados, seis viram avaliação agendada. Comparecimento,
fechamento e pagamento batem ou superam a régua.
*Fazer:* blindar a linha de frente — resposta em minutos, e trocar rajada de
campanha por fluxo constante.

**GRAVE · Londrina — Gap de marca dentro da mesma cidade**
A matriz tem 4,6 e a filial do Centro tem 3,5. Para o paciente, as duas são
OrthoDontic.
*Fazer:* tratar como passivo de marca da franqueadora, não como problema de uma
unidade.

**GRAVE · Feira de Santana — A unidade grita dentro do coro**
17 anúncios ativos num mar de 59 anúncios de 16 anunciantes com texto quase
idêntico. Quem lidera a cidade se recusa a gritar.
*Fazer:* trocar urgência por rosto, acolhimento e preço dito como orgulho do
batalhador.

**ATENÇÃO · Riomafra — Velocidade de reputação travada**
0,7 review novo por mês. A vizinha faz cerca de 28, pedindo a cada paciente na
primeira visita.
*Fazer:* ligar a máquina de avaliações, priorizando review de tratamento
concluído — o que a vizinha de nove meses não consegue ter.

**ATENÇÃO · Presidente Prudente — Claim sem validação**
"A mais bem avaliada de Prudente" é sustentável pelos números (4,9 · 582), mas o
estudo marca o claim como pendente.
*Fazer:* validar a redação exata antes de publicar.

---

## 5 · TELA 2 — FICHA DA PRAÇA

Abre em **Riomafra**. Seletor no topo troca entre as quatro.

**Cabeçalho cinematográfico:** nome da praça grande, cidade em mono abaixo, a
tese em destaque, e à direita quatro medidores radiais: nota, avaliações,
reviews novos/mês, anúncios ativos. Cada um com o alvo marcado no arco.

### Riomafra — Mafra/SC · Rio Negro/PR
**A tese:** *"A melhor clínica da cidade é a mais calada."*
Melhor reputação entre as grandes da praça, quase nenhuma ferida, e o ativo mais
raro numa cidade de colônia: donos ortodontistas nascidos ali, com sobrenome da
terra. E está em silêncio, no mês em que a região mais procura aparelho.

**Ponteiros:** nota **4,9** (meta 4,8) · avaliações **155** · novas/mês **0,7**
(meta 15) · anúncios ativos **0** (meta 4 a 6) · agendamento **5,9%** (régua 40%)
Base: 452 vozes, corte 15/jul/2026, taxonomia v1.1.

**O funil contra a régua** — a peça visual mais importante do portal. Cinco
estágios em funil, cada um com o valor real e a régua da rede marcada. Os que
batem a régua em verde, o que falha em vermelho e maior que os outros.

| Estágio | Real | Régua |
|---|---|---|
| Interessados | 5.050 | — |
| Agendamentos | 298 · **5,9%** | **40%** |
| Comparecimentos | 147 · 49,3% | 50% |
| Fechados | 110 · 74,8% | 80% |
| Pagos | 109 · 99,1% | 90% |

Frase em destaque ao lado: **"Quem chega, fecha. Quem chama, some."**
Três dos quatro estágios batem ou superam a régua. O único quebrado é o
primeiro — e é o mais barato de consertar.

**Velocidade de reputação** — barras horizontais, a nossa em cor de marca e as
outras em neutro:
Instituto Lumière **28/mês** (melhor mês: 72 em mar/26) · OdontoCompany Mafra
**13/mês** (33 em mai/26) · Cuidado e Prevenção **9/mês** · **OrthoDontic Mafra
0,7/mês** (melhor mês: 4).
Legenda: *a unidade somou 10 avaliações em 14 meses; a vizinha fez 72 num único mês.*

**O placar da praça:**
OdontoCompany Mafra 4,7 · 338 · rede popular
Instituto Lumière 5,0 · 197 · tráfego pago, 9 meses de vida, capital 28x maior
OdontoCompany Rio Negro 4,7 · 188
**OrthoDontic Mafra 4,9 · 155 · a única especializada em ortodontia**
Cuidado e Prevenção 4,9 · 135 · 20 anos, dona do infantil
Edgard Góes 5,0 · 103 · consultório da margem paranaense

**A temporada:** colunas com JUL **34** (o pico, destacado) · AGO **23** ·
SET **22** · DEZ/JAN **2,5 a 7,9** (o vale).
Legenda: *dezembro e janeiro são vale aqui. A tese nacional de "férias de fim de
ano" não vale no planalto — e foi esta praça que a derrubou.*

**O DNA local** — cartões, um deles marcado como proibição:
- **A língua:** o falar do planalto, "piá", chimarrão, inverno de verdade. E
  dizer **Riomafra** — a praça é uma colônia partida ao meio pela divisa, com
  ônibus urbano cruzando a ponte.
- **Temperamento:** colônia discreta e comunitária. Desconfia de promessa
  grande; respeita trabalho, constância e palavra cumprida.
- **A alavanca:** prova antes de promessa. Parcela clara que cabe no orçamento.
- **A joia enterrada:** o casal de ortodontistas que voltou pra casa em 2019. De
  2 para 9 especialistas. Sobrenome da colônia no mapa das duas cidades — e
  ausente do feed.
- **JAMAIS:** hype, urgência de liquidação, "última chance" — o radar
  antivigarista da colônia queima a marca. Nunca gíria gaúcha nem estética de
  Oktoberfest.

**Vozes reais** — carrossel de citações grandes, tipografia de destaque:
> "A melhor clínica e os melhores dentistas!!!" — seguidor da unidade
> "Ótimo atendimento, preço justo e lugar aconchegante." — paciente
> "Clínica limpa e cheirosa, ambiente super agradável e profissionais mto atenciosos." — paciente
> "falta de comunicação entre a equipe… fiquei 1 mês sem manutenção" — a única ferida, e é operacional

**O plano de 90 dias** — sete ações como cartões arrastáveis, com estado, prazo
e esforço→impacto. A ação 05 marcada como URGENTE:
1. Blindar manutenção e retenção — 15 dias — baixo→ALTO
2. Ligar a máquina de avaliações (meta ≥15/mês) — 15 dias
3. Destravar o rosto: a história do casal no feed e na fachada — 30 dias
4. Reocupar a especialidade: 80% do feed em ortodontia — 30 dias
5. **Entrar na mídia paga JÁ** — 7 a 14 dias — URGENTE
6. Reivindicar as duas margens: geotargeting Rio Negro — 60 dias
7. Parcerias de comunidade: futsal 9-15, maternidade, festa de setembro — 90 dias

**O bloco final: "O que mudou"** — deliberadamente **vazio**, com estado de
espera desenhado com capricho:
> **Aguardando a segunda coleta.**
> Este bloco nasce no próximo ciclo. É ele que transforma o estudo em sensor.
> `Próxima coleta: pendente`

### As outras três praças (dados para as fichas)

**Londrina/PR — Souza Naves, A MATRIZ.** Tese: *"A coroa que está escorregando."*
Nota 4,6 · 561 avaliações (o maior volume da cidade) · atendimento em 54% dos
reviews (237 de 438 com texto) · base 1.400+ vozes.
Placar: Odontoclinic 4,9 · 533 (clínica geral, a líder) · **OrthoDontic Souza
Naves 4,6 · 561** · especialista 4,6 · 116 · Dentel 4,2 · Sorrifácil e
OdontoCompany 3,9 · **OrthoDontic Centro 3,5** (a mesma marca no último lugar).
Língua: orgulho de raiz e tradição, "meu pai abriu esse restaurante em 1967",
"Ahhh, Londrina!". Fé e família. Consumo por indicação.
Alavanca: confiança + preço justo — preço baixo levanta suspeita.
Joia: é a matriz, tocada por quem fundou a rede, na cidade onde a maior rede de
ortodontia do Brasil nasceu em 2002, com cinco amigos da UEL. Não aparece em
lugar nenhum da comunicação — nem placa tem.
Citações: *"sempre me senti acolhido e hoje, ao fim do tratamento, me sinto
muito realizado. Consigo sorrir novamente"* · *"Dr. João nota 10, excelente
doutor"* · *"Graças a Deus li os comentários!!!"* (mãe buscando dentista).

**Feira de Santana/BA — Centro.** Tese: *"Todos os caminhos levam à Feira.
Menos o da própria clínica."*
Nota 4,7 · 173 avaliações · 17 anúncios ativos · atendimento em 63% dos reviews
· base 800+ vozes e 59 anúncios da categoria mapeados.
Placar: clínica do doutor local **4,9 · 1.268** (o gigante, pessoa física) ·
**OrthoDontic Feira 4,7 · 173** · OdontoCompany 4,4 · 56 (a 400 m) ·
faculdade 4,4 · 9.
Língua: baianês com pé no sertão — "oxe", "meu rei", "minha rainha", "massa",
"arrochar". 616 mil habitantes, maior que oito capitais, a Princesa do Sertão.
Alavanca: preço como ORGULHO — "pagar menos e sair por cima é virtude".
Joia: **nenhuma ainda** — a unidade é invisível fora do Google, cerca de 3 mil
seguidores, nenhuma menção na imprensa local. Aqui a estratégia é construir
pertencimento, não desenterrar patrimônio. *(Mostre esse campo vazio como
informação, não como falha.)*
JAMAIS: axé litorâneo de vitrine — soa a quem confundiu Feira com Salvador.
Citações: *"Preço acessível e me trataram como gente. Amei."* · *"marca horário
e atende 2, 3, 4 horas depois"*.

**Presidente Prudente/SP — a 1ª FRANQUIA da rede, 02/05/2005.**
Tese: *"O tesouro que está guardado na gaveta."*
Nota **4,9 · 582** — líder em nota e volume · 7 anúncios ativos, a única
comprando mídia de ortodontia na cidade · atendimento em 47% dos reviews · base
1.400+ vozes, 930 comentários de 12 perfis locais.
Das 84 avaliações com texto: **83 de cinco estrelas, 1 de uma estrela, zero no
meio.**
Placar: **OrthoDontic PP 4,9 · 582** · Dentoclinic 5,0 · 77 · Todos Sorrindo
4,9 · 34 · NEXA 4,7 · 618 (clínica geral) · Croorto 4,7 · 52 · Sorrifácil 4,6 · 31.
Língua: superlativo local — "o melhor da cidade". A régua de tom foi a cidade
que entregou: **"que tratem as pessoas com dignidade e humanismo"**, o
comentário mais curtido do corpus.
Alavanca: CLAREZA, não preço.
Joia: foi a primeira franquia de toda a rede, aberta por dois prudentinos.
Citações: *"Já passei por lá — e agora são meus filhos."* · *"explicam tudo
direito"* · *"me lembro do dia 02/05/2005, dia da inauguração!! Deus continue
abençoando."*

---

## 6 · TELA 3 — O QUE APRENDEMOS

A tela mais estratégica. Desenhe-a como **um laboratório**, não como lista.

**Máquina de estados no topo**, como esteira horizontal com os achados fluindo
entre os estágios:
`HIPÓTESE (0)` → `CANDIDATA (13)` → `CONSTANTE (0)` → `DOUTRINA (0)` ·
e fora da esteira, `❌ DERRUBADA (1)`

Legenda: *um achado só vira regra da rede quando praças diversas confirmam.
Quatro praças parecidas não fazem constante. A amostra atual não cobre Norte,
Centro-Oeste, capital nem unidade recém-aberta — por isso o teto honesto hoje é
candidata.*

**Os 13 achados candidatos**, cada um como cartão com o placar de confirmação
(4/4, 3/4) e as evidências por praça:

1. **O paciente não avalia ortodontia — avalia como foi tratado.** 4/4 ·
   Prudente 47% · Londrina 54% · Feira 63% · Riomafra 69% *(mostre a série
   subindo — o índice cresce conforme a cidade encolhe)*
2. **A ferida é sempre operação, nunca o produto.** 4/4 · pós-venda · agenda ·
   espera de 2 a 4 horas · manutenção
3. **A confiança é em gente com nome, não em marca.** 4/4
4. **A porta de entrada é sempre "quanto custa / cabe na parcela?", seguida de
   "dói?".** 4/4
5. **Julho é o pico da mãe-decisora.** 4/4 · Riomafra índice 34, 4.120 leads em jul/25
6. **O adulto 30+ é dinheiro na mesa e nenhuma praça fala com ele.** 4/4 ·
   Riomafra tem 21.000 adultos de 30-45 contra 7.700 jovens de 9-15
7. **A clínica-escola é fraca exatamente onde a rede é forte.** 4/4
8. **A joia local existe, é incopiável — e está enterrada.** 3/4 *(Feira não tem)*
9. **A embalagem é a mesma nas quatro: feed institucional + anúncio de urgência.** 4/4
10. **A prova social está parada em todas.** 4/4
11. **A mãe é a decisora — e lê os reviews antes de escolher.** 4/4
12. **A ordem certa é blindar a operação antes de qualquer mídia nova.** 4/4
13. **Os mesmos quatro formatos fixos de conteúdo emergem nas quatro.** 4/4

**A derrubada, em destaque especial** — cartão maior, tratamento gráfico de
"crença que caiu":
> ❌ **"Dezembro e janeiro são pico nacional"**
> Derrubada por Riomafra. Série de 5 anos: julho índice 34, dez/jan entre 2,5 e
> 7,9. Confirmado pelo dado interno: 494 e 78 interessados contra 4.120 em
> julho/25.
> *Custou centavos de coleta e evitou verba nacional programada para o mês
> errado em parte do país.*

**As variáveis — o que jamais pode ser nacionalizado.** Comparação lado a lado
das quatro praças, mas **não como tabela**: como quatro colunas visuais, uma por
praça, cada uma com sua cor de acento:

| | Londrina | Prudente | Feira | Riomafra |
|---|---|---|---|---|
| Alavanca de preço | confiança + preço justo — barato levanta suspeita | clareza, não preço | preço como orgulho do batalhador | palavra cumprida |
| Posição no placar | desafiante | líder — joga defesa | desafiante, 7x atrás | melhor nota, 4ª em volume |
| O inimigo | clínica geral bem avaliada | vácuo competitivo | doutor pessoa física | rede popular + startup de tráfego |
| Mídia própria | urgência genérica | 7 ativos, leilão dominado | 17 ativos no coro | zero |
| Léxico proibido | urgência de liquidação | corporativês | axé litorâneo | gíria gaúcha, Oktoberfest |

---

## 7 · TELA 4 — CORRETOR DE CAMPANHA

**A tela que a franqueadora compra primeiro**, porque mede o trabalho dela.

Campo grande de texto no topo, com uma peça real já dentro:
> 🚨 SEMANA DO APARELHO! Últimos dias com condição especial. Aparelho sem
> entrada — agende agora mesmo sua avaliação!

Botão primário grande: **`Analisar contra as 4 praças`**. Ao clicar, os quatro
resultados entram em sequência animada.

**Os quatro vereditos:**

**Londrina — ⚠️ RISCO**
Público de meio de funil: preço baixo levanta suspeita, não desejo. A matriz não
briga de igual para igual no preço — briga na autoridade.
*Sugestão:* "tratado por quem criou o padrão".

**Presidente Prudente — 🟡 ADAPTAR**
A alavanca aqui é clareza, não desconto. O que sustenta o 4,9 é "explicam tudo,
não tive nenhuma dúvida", e a régua de tom que a cidade entregou foi "dignidade
e humanismo".
*Sugestão:* "você entende tudo antes de decidir".

**Feira de Santana — 🟢 FUNCIONA, COM CONDIÇÃO**
Preço é orgulho aqui. Mas a peça precisa falar como Feira, e hoje está dentro de
um coro de 59 anúncios quase idênticos.
*Sugestão:* "cabe no seu bolso, meu rei".

**Riomafra — 🔴 CONFLITO**
"Últimos dias" e "agora mesmo" acionam o radar antivigarista da colônia. A praça
respeita palavra cumprida e desconfia de promessa grande.
*Bloqueado:* urgência de liquidação.

**Abaixo, o painel "A campanha nacional chega à cadeira?"** — três barras longas
e quase vazias, com o número enorme ao lado:
- Publicações de unidade que carregam o embaixador: **1 de 156**
- Criativos nacionais com o jingle: **1 de 34**
- Menções espontâneas ao embaixador: **0 de 2.834 vozes**

Legenda: *oito anos de embaixador. O jingle está subusado, não gasto.*

---

## 8 · A GAVETA DE EVIDÊNCIA

Todo número no portal tem um botão discreto que abre uma **gaveta lateral com
vidro fosco**. É o que separa isto de um dashboard: um dashboard afirma, um
portal de inteligência mostra de onde tirou e o que ainda não sabe.

Conteúdo da gaveta, no exemplo do agendamento de Riomafra:
- **5,9%** em tipografia enorme
- *dos interessados viram avaliação agendada — a régua da rede espera 40%*
- Selo de **confiança: média**
- **A leitura:** o único estágio quebrado do funil. Comparecimento bate a régua,
  fechamento e pagamento estão acima dela. A cadeira e o contrato funcionam — o
  vão está entre a primeira mensagem e a agenda.
- **Contra-evidência** (bloco destacado em cor de atenção): o denominador não
  reconcilia — 109 pagos no funil contra cerca de 336 contratos/ano na mesma
  unidade. Enquanto a reconciliação não fechar, o multiplicador projetado não é
  publicado.
- Ficha técnica em mono: `N 5.050 interessados · 298 agendamentos` ·
  `corte jul/2026` · `fonte funil.jsonl (Conecta)` · `filtro unidade=ortho_mafra`

---

## 9 · MOVIMENTO

Use os tokens de movimento do sistema: `--dur-fast 120ms` · `--dur 200ms` ·
`--dur-slow 360ms` · `--dur-slower 600ms`, com `--ease-out` nas entradas.

- **Entrada orquestrada:** o mapa acende primeiro, os quatro pontos acendem em
  sequência, os números contam até o valor, os cartões de sinal sobem
  escalonados.
- **Troca de tela:** deslize e fade curtos, nunca corte seco.
- **Hover:** painéis ganham brilho de borda cyan; barras clareiam; o ponto no
  mapa expande o halo.
- **Alertas críticos:** o halo respira **três vezes na entrada e para**. O
  sistema proíbe movimento decorativo infinito — depois disso o estado é
  carregado pela cor e pela faixa de severidade, não pela animação.
- **Gráficos:** desenham na entrada — barras crescem, funil preenche de cima
  para baixo.
- `--ease-bounce` só em botão. Nunca em dado.
- Respeite `prefers-reduced-motion`.

---

## 10 · TRAVAS

1. **Não invente número.** Todo dado está neste documento. Se faltar, mostre o
   estado vazio — o bloco "O que mudou" vazio é uma decisão de produto, não uma
   pendência.
2. **Não reescreva citação de paciente.** São verbatim. A imperfeição é a prova.
3. **Não ranqueie franqueado nominalmente** na visão de rede.
4. **Toda recomendação carrega evidência.** Nenhuma afirmação solta.
5. **Cor de estado nunca é cor de marca.**
6. **Se a tela virou tabela, refaça.**

---

## 11 · O TESTE FINAL

A diretoria abre isto numa reunião de conselho e a primeira reação tem que ser
**"como a gente não tinha isso?"** — não "que dashboard bonito".

A diferença está em três coisas: o mapa que mostra 336 cidades apagadas, o funil
que mostra onde o dinheiro vaza, e a gaveta que prova cada número — inclusive
dizendo onde ele ainda não fecha.
