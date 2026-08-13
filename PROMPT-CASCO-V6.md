# Prompt para o Claude Design — casco v6

Este prompt substitui TODOS os anteriores (v2 a v5).

## 0 · A decisão mais importante: a identidade JÁ EXISTE

O cliente aprovou **o PRIMEIRO design**, o arquivo
**`referencia-aprovada/OrthoDontic Intelligence.dc.html`** — foi sobre
ele que ele disse "tô gostando do design". Tudo que veio depois foi
rejeitado, inclusive o `v2` (que está na pasta só para comparação) e
qualquer casco montado fora do Claude Design.

**NÃO redesenhe. NÃO invente identidade nova.** O trabalho é EVOLUIR
esse arquivo para a arquitetura e os dados novos descritos abaixo.

O que é a identidade aprovada, exatamente (está no arquivo, e a captura
`PRIMEIRO-DESIGN.png` mostra):

- **Plano navy** `#001433`, painéis `#001A5C`/`#02205F`, fio
  `rgba(255,255,255,.10)`, fio aceso ciano `rgba(0,185,255,.28)`.
- **Barra fixa no topo (64px, vidro fosco):** logo horizontal branco ·
  filete · `INTELLIGENCE` em mono espaçado · busca em pílula
  ("Buscar praça, sinal, achado…" + `⌘K`) · pílula de cobertura
  (`4 / 340 praças` com barra) · `corte 15/jul/2026` · seletor de
  perfil (Franqueadora) · troca de tema · avatar.
- **Menu na lateral esquerda**, não em abas: item ativo em pílula
  ciano com contador, praças listadas abaixo com bolinha de severidade.
- **Herói**: painel grande com sobrelinha em mono ciano
  (`SALA DE CONTROLE · REDE NACIONAL`), número-frase gigante em Gotham
  ("4 de 340 praças ouvidas."), sublinha em cinza-claro, legenda de
  bolinhas, e o globo/mapa em ciano translúcido à direita.
- **Tira de números**: cartões escuros com o número gigante colorido
  (vermelho `#FF5C5C` = crítico, ciano `#00B9FF`, cinza, verde
  `#3ED6B8`) e o rótulo em duas linhas embaixo.
- **Cartão de sinal**: barra de severidade na borda esquerda, selo
  `CRÍTICO`/`GRAVE`/`ATENÇÃO`, praça em mono, título forte, o texto do
  fato, uma **barra de medida** com o número em mono à esquerda, o bloco
  `O QUE FAZER` (rótulo em mono ciano) e o rodapé com a janela de tempo
  + `Ver evidência` em ciano.
- **Tipografia**: Gotham no texto; **IBM Plex Mono em TODO número,
  rótulo de sistema e data**. Cantos ~14–16px, animação de entrada
  discreta, `prefers-reduced-motion` respeitado.

Componentes novos (página da clínica, linha do tempo) se desenham com as
MESMAS peças: cartão escuro, selo, barra de medida, rótulo em mono,
`Ver evidência` em ciano.

## 1 · O que mudou desde a referência (a arquitetura nova)

O produto foi reorganizado (dois gols: performance das clínicas e vender
mais clínicas). A estrutura agora é:

```
PAINEL DE   o MAPA DO BRASIL bem na frente, pintado por PROBLEMA — e só
CONTROLE    embaixo dele os cartões de problema (fila.json). Clicar num
            cartão abre a PÁGINA DA CLÍNICA.
CLÍNICAS    uma página POR UNIDADE (clinicas/<local_id>.json) — o coração
            do portal e a futura visão do franqueado.
PRAÇAS      o mercado de cada cidade (pracas/<id>.json) — tese, placar,
            temas, citações, o que mudou na cidade.
O QUE A REDE ENSINA   padroes.json + rival.json→padrao_da_rede — o bom e
            o ruim que se repetem; decisão de rede.
RADAR DE CIDADES      radar.json (estudos prontos) + funil_nacional.json
            (top 50 do Brasil + onde cabem mais unidades).
A MARCA     rede_inteira.json (alertas das 374 fichas) + franqueadora.json
            → reputacao_das_redes (Reclame Aqui).
ARQUIVO     franqueadora.json → cards (grupo "arquivo") — de onde vem
            cada número; ferramenta apagada com o motivo.
```

As abas do topo da referência ("Rede · Radar · Praça · Plano") viram:
**Painel de Controle · Clínicas · Praças · O que a rede ensina · Radar de
cidades · A marca · Arquivo**.

### 1.1 · O Painel de Controle, na ordem exata

A primeira tela não abre com texto nem com número solto. Abre com o mapa.

1. **O MAPA DO BRASIL, grande, na frente de tudo** — não é enfeite de
   canto nem bloco no fim da página: é a primeira coisa que a diretoria
   vê. Pintado por PROBLEMA, não por tamanho. Cada estado em
   `franqueadora.json → mapa[]` traz `tom` pronto:

   | `tom` | o que é | como pintar |
   |---|---|---|
   | `crit` | unidade em faixa vermelha **ou** alerta grave na ficha | vermelho `#FF5C5C` |
   | `warn` | unidade em faixa amarela | amarelo `#F8D65D` |
   | `ok` | acompanhada, sem alerta aberto | verde `#3ED6B8` |
   | `sem_escuta` | tem unidade, ainda não é medida | ciano apagado |
   | `sem_unidade` | a rede não está no estado | só o contorno |

   `motivo` é a frase pronta do estado ("1 em faixa vermelha · 1 em faixa
   amarela") — use no hover e ao lado da sigla. `mapa_legenda[]` traz a
   legenda pronta, na ordem. Hoje: **BA, MS, MG, PR e SP em `crit`**;
   MT e SC em `warn`. Clicar num estado filtra os cartões debaixo.
2. **A tira de números** (`tiras_do_inicio`) logo abaixo do mapa.
3. **Os cartões de problema** (`fila.fila[]`), na ordem que vêm.
4. **A régua da rede e a cobertura** por último — contexto, não manchete.

## 2 · A página da clínica (o coração — payload novo)

`clinicas/<local_id>.json` já vem composto, um por unidade. Capítulos, na
ordem:

1. **cabeçalho** — rótulo (`UF · Cidade` + unidade), nota, avaliações,
   ritmo, posição na cidade, `faixa` (selo de cor) e `tarefa` (aberta /
   vencida, com `vence_em`).
1.5. **onde esta loja aparece na busca** — `presenca_na_busca`, campo
   novo e o mais duro do portal. Traz `frase_do_topo` pronta,
   `aparece_em` de `de`, `pct`, `melhor_posicao` e as
   `frases_onde_aparece[]`. Quando `invisivel` for true, a tela diz
   isso com peso: **a loja Dom Bosco não aparece em NENHUMA das 151
   buscas de Cuiabá**, e a loja ao lado aparece em 4. É POR LOJA, nunca
   a média da cidade — três lojas de Cuiabá podem ter donos diferentes.
   O botão "o meu plano" abre `plano` (`planos/<local_id>`).
2. **o que fazer agora** — `gatilhos[]` (com `fonte` em pé de linha),
   `quem_avanca` e `acao` (o quê · prazo · dono · custo) em destaque.
3. **o que mudou entre as coletas** — `o_que_mudou` traz DUAS janelas, e
   as duas aparecem:
   - o **delta curto** (`antes → agora`, `delta`, `dias`), que é o que
     mudou entre as duas últimas medições;
   - o **período inteiro** (`historico`: `desde`, `dias`, `medicoes`,
     `delta`, `ritmo_do_periodo`), que é desde a primeira medição.

   Isso importa: **Mafra, Londrina, Feira de Santana e Presidente
   Prudente são medidas desde 15/jul — 26 dias, 3 e 4 medições** — e a
   tela vinha dizendo "período de só 3 dias" justamente para elas, as
   quatro praças com mais histórico da rede. Escreva "medida desde
   15/jul · 26 dias · 3 medições" e mostre o movimento do período todo ao
   lado do da semana. O `aviso` só aparece onde o HISTÓRICO é curto.
   Se `o_que_mudou` for null: "ainda só uma medição — a comparação nasce
   na próxima coleta".
4. **a voz do paciente** — `voz_do_paciente[]` já com rótulo de balcão
   (`o_que_e` + `pct`), barras finas.
5. **avaliações esperando resposta** — `sem_resposta.itens[]` (nota,
   data, texto do paciente).
6. **quem anuncia aparelho na cidade** — `anuncios_da_cidade` (payload
   novo). `manchete` pronta, depois a lista de `anunciantes[]`: nome,
   quantos anúncios, plataforma (Meta · Google), há quantos dias no ar e
   um `exemplo` do texto. O nosso vem primeiro, marcado `nosso: true`.
   O bloco é **de CIDADE, não de loja** (`e_da_cidade: true`) — três
   lojas de Cuiabá disputam o mesmo leilão; diga isso na tela. Os
   descartados aparecem como `fora_do_produto` (número + motivo): 134
   anúncios de aparelho estavam no ar e o portal mostrava só um contador
   escondido dentro da captação.
6.5. **o anúncio que não é da praça** — `anuncio_de_outra_unidade[]`.
   Quando aparece, mostre em pé de linha com o motivo: a busca da
   Biblioteca casa por palavra, e "juazeiro do NORTE" trouxe a
   "Orthodontic Braço do NORTE", unidade de SC a 3 mil km. Some da
   contagem de "a rede está no ar aqui".
7. **o rival de aparelho** — `rival.vantagens_deles[]` OU
   `sem_comparacao_porque`; `rival.fora[]` numa lista recolhida "fora da
   comparação — outro produto", cada um com `por_que_fora`. Uma linha
   fixa: só quem vende aparelho entra na comparação.
8. **a linha do tempo** — `eventos[]` (data, `quem`: nossa · paciente ·
   fila · rival, texto pronto), linha vertical fina, cor por `quem`.

### 2.1 · O que é da LOJA e o que é da CIDADE

A aba **Praças** mostra 7 cidades e continua certa — tese, concorrência,
temas e portas são leitura de MERCADO, e mercado é por cidade. Mas o
estudo da unidade é outro, e é a aba **Clínicas**: são 10, não 7.

| por LOJA (`local_id`) | por CIDADE |
|---|---|
| presença na busca, plano, fila e tarefa | tese e DNA da praça |
| avaliações, nota, ritmo, respostas | temas das avaliações |
| rival medido contra ESTA unidade | quem anuncia aparelho |
| linha do tempo da loja | portas de busca, bairros, convênios |

Onde o bloco for de cidade dentro da página da clínica, ele vem com
`e_da_cidade: true` — escreva na tela ("leitura da cidade, vale para as
3 lojas de Cuiabá"). Nunca apresente número de cidade como se fosse da
loja: foi assim que um plano disse "a sua clínica aparece em N buscas"
para a única loja que não aparece em nenhuma.

## 3 · Mudanças de dado que as telas precisam refletir

- **Praça = UMA cidade.** `riomafra` não existe mais (é `mafra`); Cuiabá
  não soma mais Várzea Grande. Rótulos vêm prontos (`MT · Cuiabá`).
- **"Quando a procura sobe" não é ferramenta pendente: é pergunta
  RESPONDIDA COM NÃO.** `sazonalidade.json` guarda a medição de 12 UFs
  no Google Trends, 5 anos. Nenhuma passou. A tela não fica cinza com
  "em breve" — ela conta o resultado: por cidade o Trends devolve zero
  em todas as 124 cidades de SC e 186 do PR (Mafra e Londrina inclusas);
  por estado, onde há volume o pico muda de mês todo ano (o do Paraná
  foi ABR, JAN, JUN, MAR e JUL em cinco anos). Cada praça leva
  `sazonalidade_estado` com `medimos: true`, o veredito da própria UF e
  `quem_responde: "só a rede, por dentro"` — é teto de produto, e teto
  declarado é conteúdo.
- **A cidade do Radar abre igual à praça da rede.** Os seis estudos em
  `oportunidade/<id>.json` agora trazem `eyebrow`, `tese_titulo`, `tese`
  e `base` — os mesmos quatro campos com que uma praça abre. Desenhe o
  mesmo bloco de abertura nas duas telas: sobrelinha em mono, título
  grande, o parágrafo da tese, e a base em pé de linha. Antes elas
  abriam com vinte campos de número e nenhuma manchete, e a diferença
  saltava na tela.
- **Concorrente é só quem disputa aparelho.** Toda tela de confronto já
  recebe filtrado; os excluídos vêm nomeados com o motivo — a tela mostra.
- **fila.json ganhou `tarefa`** (status aberta/vencida, `vence_em`,
  `dias_aberta`) **e `tarefas_resolvidas[]`** — desenhar as resolvidas
  como lista de vitórias ("o dado externo fechou o loop").
- **cobertura.aviso** (franqueadora.json) sempre visível: as leituras
  valem para as 10 unidades acompanhadas, não para as 374.
- **funil_nacional.json** é novo: candidatas top 50 (rótulo pronto,
  população, alvos, renda relativa, score) + `onde_cabem_mais[]` +
  `metodo` aberto (a régua é o argumento).

## 4 · As regras que não caem nunca

- **O casco NUNCA calcula** — nenhuma soma, média, %, ordenação por
  valor, montagem de rótulo. Falta número? Conserto é no build.
- **`.length` na tela é conta na tela.** Todo "quantos itens tem aqui"
  já vem contado ao lado da lista. Use o campo, nunca conte o array:

  | em vez de contar | use |
  |---|---|
  | `manifest.pracas[].tem` | `.estudos` |
  | `franqueadora.rede.ufs_sem_unidade` | `.ufs_sem_unidade_total` |
  | `caixa.unidades` | `caixa.lojas_com_fila` |
  | `caixa.unidades[].itens` | `.itens_total` |
  | `padroes.hipoteses_testadas` | `.hipoteses_testadas_total` |
  | `funil_nacional.candidatas` | `.candidatas_total` |
  | `rede_inteira.alertas` | `.alertas_total` |
  | `rival.pracas[].rivais_fora` | `.rivais_fora_total` |
  | `clinicas/*.sem_resposta.itens` | `.itens_total` |
  | `clinicas/*.rival.fora` | `.fora_total` |
  | `captacao/*.fora` `.sem_dono` `.dentro` | `.fora_total` `.sem_dono_total` `.dentro_total` |

  E quando a lista for cortada para caber ("mostrar 8, esconder o
  resto"), o rótulo é **"ver todas as N"** com o total pronto — nunca
  `total − 8`, que é subtração na tela.
- **O casco não junta número com palavra.** A tira do Início vem pronta em
  `franqueadora.json → tiras_do_inicio`: cada item traz `numero`, `rotulo`
  (já no singular ou no plural que combina com o número) e `tom`
  (`crit` · `warn` · `marca` · `bad`). Desenhe os quatro na ordem em que
  vêm. Colar um rótulo fixo ao lado do número é o que escreveu
  **"1 unidades em faixa vermelha"** na primeira tela do portal.
- **Nenhum número no HTML.** `374`, `348`, `10 lojas`, `340` não se
  escrevem: todos mudam a cada coleta. Rótulo de menu e sobrelinha de
  tela saem de `franqueadora.json → grupos[]` e `cobertura`. Um `374`
  cravado sobrevive à coleta que o desmente — já aconteceu, ficou quatro
  semanas na tela ao lado de um bloco que dizia outro número.
- **Rótulo com a UF na frente**, recebido pronto.
- **Loja não se funde com loja** — Cuiabá são três páginas, Londrina duas.
- **Estado vazio é conteúdo** — ferramenta apagada mostra o porquê;
  `o_que_isso_nao_ve` aparece onde existir.
- **Nada de dado interno**, e toda tela de desempenho diz isso.
- **Linguagem de balcão** — palavra interna (casco, escada, ponta, andar)
  nunca aparece na tela.

## 5 · O CONSERTO DO ZIP QUE VOLTOU (leia antes de mexer)

O casco entregue está certo em quase tudo: os totais saem de campo pronto,
não há número escrito à mão no HTML, a loja invisível já aparece com peso,
e a tabela nova de sazonalidade já lê `pico_repete_em` e `porque`. Há **um
defeito**, e ele quebra 7 telas.

**`assets/portal.js`, linha 835.** A tela da praça oferece:

```js
'<button ... data-ir="planos/' + esc(d.praca_id) + '">O plano do franqueado</button>'
```

Isso pede `planos/<praça>.json` — **um plano por cidade**. Não existe mais.
O plano é por `local_id` desde que se descobriu que Cuiabá tem três lojas
que podem ter três donos, e que a média da cidade mentia para todos. Com o
payload de hoje, esse botão dá 404 nas sete praças: `planos/mafra.json`,
`planos/cuiaba.json`, `planos/londrina.json` e as outras quatro. Ele só
funcionava no zip porque o zip ainda carregava 14 planos velhos, de quando
o plano era por cidade — inclusive planos para as seis cidades do Radar,
que **não têm franqueado nenhum**.

O payload agora traz a lista certa. Cada `pracas/<id>.json` tem:

```json
"planos_das_lojas": [
  {"local_id": "ortho_cba_centro_norte", "unidade": "Centro Norte",
   "rotulo": "MT · Cuiabá", "arquivo": "planos/ortho_cba_centro_norte"}
]
```

Troque o botão único por **um botão por item da lista**, nomeando a
unidade: "O plano da unidade Centro Norte". Em Cuiabá saem três, em
Londrina dois, nas outras um. Se a lista vier vazia, não desenhe o bloco.

E apague do projeto os arquivos que o build não produz mais: os 14
`planos/<cidade>.json`, `pracas/riomafra.json` e `captacao/riomafra.json`
(`riomafra` é o nome local da região; a praça é `mafra`).

## 6 · A SEGUNDA RODADA DE AJUSTES (depois de ver o portal rodando)

### 6.1 · O portal é de 374 unidades, não de 10

Hoje dez lojas têm estudo. A rede tem **374 unidades em 304 cidades**, e 46
dessas cidades têm mais de uma loja. Uma grade de cartões que funciona com
dez vira uma parede inútil na centésima — e some com a informação de que
364 unidades ainda não foram escutadas.

Payload novo: **`clinicas_indice.json`**, com tudo contado no build.

```json
{"unidades_total": 374, "com_estudo": 10, "sem_escuta": 364,
 "cidades_total": 304, "cidades_com_mais_de_uma_loja": 46,
 "manchete": "10 de 374 unidades com estudo — as outras 364 ainda não foram escutadas",
 "ufs": [{"uf": "SP", "unidades_total": 78, "cidades_total": 65,
          "com_estudo": 0, "sem_escuta": 78,
          "frase": "78 unidades em 65 cidades · nenhuma escutada",
          "cidades": [{"rotulo": "SP · Bauru", "unidades_total": 2,
                       "mais_de_uma_loja": true, "unidades": [ ... ]}]}]}
```

A tela de **Clínicas** deixa de ser lista e vira **triagem**, nesta ordem:

1. **A manchete** (`manchete`) — o tamanho do que falta, em primeiro lugar.
2. **As que pedem ação agora** — as com `faixa`/`tarefa` na fila, poucas,
   em cartão grande. É isto que alguém abre o portal para ver.
3. **Busca e filtros** — por unidade, cidade ou UF; filtros por faixa,
   tarefa aberta/vencida, invisível na busca, com/sem estudo.
4. **O mapa de cobertura por UF** — sanfona fechada por padrão, uma linha
   por estado com a `frase` pronta ("78 unidades em 65 cidades · nenhuma
   escutada"). Abrir mostra as cidades; abrir a cidade mostra as unidades.
   Estado sem nenhuma escutada aparece apagado, não some.

Regras que não podem ser quebradas nesta tela:

- **Cidade com mais de uma loja nunca vira uma linha só.** `mais_de_uma_loja`
  vem pronto. Cuiabá tem três lojas e podem ser três donos; Londrina tem
  duas. A cidade agrupa, mas quem abre é a UNIDADE.
- Unidade sem estudo **aparece** — apagada, com "ainda não escutada", e sem
  link. Esconder faz a diretoria achar que medimos tudo.
- Alguns estudos vêm em `estudos_sem_linha_oficial`, no nível da cidade,
  com `porque_sem_linha` escrito: a lista oficial não confirmou a linha
  daquelas lojas. Mostre a frase; não invente a qual linha cada uma
  corresponde.

### 6.2 · Os nomes das seções

| era | fica |
|---|---|
| O que a rede ensina | **Benchmarks** |
| A marca | **Brand Watch** |

"O que a rede ensina" descreve o arquivo, não o que a pessoa ganha ao
clicar: ali está o que se repete entre as unidades, o bom e o ruim, para
comparar a sua com a rede. **Benchmarks** diz isso em uma palavra. (Se
preferir uma palavra de ação em vez de comparação, a alternativa é
*Playbook* — mas escolha uma e mantenha.)

"A marca" é vago: a seção monitora as 374 fichas do Google e a reputação no
Reclame Aqui. **Brand Watch** diz que é vigilância, e vigilância contínua.

O menu fica: **Painel de Controle · Clínicas · Praças · Benchmarks · Radar
de cidades · Brand Watch · Arquivo**.

### 6.3 · A frase das praças perdeu a régua interna

O cartão "As praças estudadas" dizia "...no mesmo padrão de SC · Mafra".
Mafra ser a régua é decisão interna nossa; para quem lê a tela isso não
quer dizer nada. Já corrigido no build — a frase agora é "cidades onde a
rede está e que já foram estudadas por inteiro — concorrência, canais,
imprensa, busca e avaliações". Nenhuma tela cita praça como parâmetro de
outra.

### 6.4 · A clínica se apresenta antes de se medir

Hoje a página abre com a nota, como boletim. Quem chega precisa saber de
que loja se trata. Campo novo em cada `clinicas/<local_id>.json`:

```json
"apresentacao": {
  "unidade": "OrthoDontic Cuiabá Dom Bosco (Centro Sul)",
  "cidade": "MT · Cuiabá",
  "endereco": "R. Barão de Melgaço, 3429 - Centro Norte, Cuiabá - MT",
  "desde": "8/ago", "medicoes": 2,
  "lojas_irmas": [{"local_id": "...", "unidade": "..."}],
  "frase": "OrthoDontic Cuiabá Dom Bosco (Centro Sul) é escutada desde 8/ago, em 2 medições, e divide Cuiabá com mais 2 lojas da rede."
}
```

A abertura passa a ser um **bloco de apresentação**: nome da unidade em
tamanho grande, cidade e endereço em linha discreta, a `frase` pronta como
sublinha, e as `lojas_irmas` como pastilhas clicáveis ("as outras lojas
desta cidade" — reforçando que são casos separados). A nota e o número de
avaliações descem para a tira de números logo abaixo. Em três das dez o
`endereco` vem null: escreva "endereço não confirmado na lista oficial",
não esconda a linha.

### 6.5 · A página da clínica está pobre visualmente

Tudo azul com letra branca, num plano só. O problema não é a paleta — é a
falta de hierarquia. Use as peças que a referência aprovada já tem, que
hoje aparecem só no Painel de Controle:

- **Três alturas de superfície**, não uma: o plano `#001433` ao fundo, o
  painel `#001A5C` para cada capítulo, e um cartão mais claro (ou com fio
  ciano aceso) para o que exige ação.
- **A cor tem significado e é escassa.** Vermelho `#FF5C5C` só em faixa
  crítica e loja invisível; ciano `#00B9FF` só no que é clicável e no
  rótulo de sistema; verde `#3ED6B8` só no que melhorou. O resto é cinza
  sobre navy. Se tudo é ciano, nada chama.
- **A tira de números** (mesma peça do painel) logo abaixo da apresentação:
  nota, avaliações, ritmo, posição na cidade — número gigante em mono,
  rótulo em duas linhas.
- **Capítulo é painel com cabeçalho**, não parágrafo solto. Cada um com
  sobrelinha em mono ciano (`PRESENÇA NA BUSCA`, `A VOZ DO PACIENTE`).
- **Respiro.** O que pesa hoje é densidade sem pausa: dobre o espaço entre
  capítulos e deixe a coluna de texto estreita (~70 caracteres).
- **A ação em destaque**, uma só, no alto: o cartão de "o que fazer agora"
  com a barra de severidade na borda esquerda, como o cartão de sinal da
  referência.

## 7 · A CONFERÊNCIA DA SEGUNDA VOLTA (o que passou e o que falta)

O casco foi rodado num navegador com o payload real, doze rotas, e o
resultado é bom: **zero 404 nos dados**, todas as telas com conteúdo, e
tudo que a seção 6 pediu está no ar — o índice das 374 com a manchete do
que falta, a triagem "as que pedem ação agora", a apresentação da clínica
antes da nota, as lojas irmãs em pastilha, os planos por loja, Benchmarks
e Brand Watch no menu. A frase que citava Mafra sumiu.

Faltam três coisas, todas pequenas.

**7.1 · A fonte dos números vem de fora.** `index.html` linha 9 carrega o
IBM Plex Mono do `fonts.googleapis.com`. O Gotham vai empacotado em
`assets/fonts/` — o mono, não. Como TODO número do portal é mono, uma rede
com bloqueio de CDN (ou o portal aberto sem internet, que é o caso de uma
apresentação em sala de reunião) derruba a identidade inteira dos números.
Empacote o IBM Plex Mono junto, como o Gotham.

**7.2 · Rota desconhecida abre tela vazia.** `#qualquercoisa` renderiza só
a moldura. Mande o que não casar para o Painel de Controle.

**7.3 · Os 16 arquivos velhos continuam no projeto.** `planos/<cidade>.json`
(14), `pracas/riomafra.json` e `captacao/riomafra.json`. O casco já não os
pede — mas quem publicar o projeto sem trocar a pasta `dados/portal` pelo
payload novo vai servir plano de cidade para franqueado. Apague.

**Uma coisa que está certa e não deve ser "consertada":** o contador de
resultado da busca usa `lista.length`. É a única contagem legítima no
casco, porque depende do que a pessoa digitou e o build não tem como
saber. A regra de que todo total sai pronto do build continua valendo
para tudo o mais.

### 7.4 · A abertura do portal vem do dado, e mudou

`portal.js` linha 265 tem o título escrito à mão:

```js
"<h1>Onde a rede está perdendo terreno.</h1>"
```

Duas coisas erradas. **Texto na tela dentro do casco** ninguém consegue
mudar pelo dado — foi preciso editar o JavaScript para trocar uma frase. E
o portal abria pela derrota: ele existe para a rede crescer, e o que está
ruim já tem tela própria logo abaixo, na tira de números e nos cartões de
problema. A primeira frase não precisa ser essa.

Agora vem pronto em `franqueadora.json → abertura`:

```json
{"sobrelinha": "SALA DE CONTROLE · REDE NACIONAL",
 "titulo": "A inteligência que faz cada clínica crescer.",
 "sublinha": "10 unidades escutadas de perto, em 7 cidades estudadas por inteiro — e, para cada uma, o que fazer nesta semana.",
 "escopo": "As leituras valem para estas 10 unidades, não para as 374 da rede. As 6 cidades de oportunidade são estudo de expansão e não entram em nenhuma conta da rede."}
```

Troque o `<h1>` fixo por `abertura.titulo`, use `sobrelinha` na linha em
mono ciano acima (como na referência aprovada) e `sublinha` logo abaixo do
título, em cinza-claro.

O `escopo` continua na tela, mas **como nota de pé do bloco**, discreta —
não como a manchete densa que abria o portal hoje. A honestidade sobre o
que ainda não medimos permanece; ela só deixa de ser a primeira coisa que
a diretoria lê.

## 8 · O ACABAMENTO (a identidade fica; o craft muda)

O cliente gosta da distribuição, da estrutura e da paleta. **Não redesenhe
nada disso.** O que falta é acabamento, e ele é medível — os números
abaixo saíram do `portal.css` entregue.

### 8.1 · A escala de tipo é um borrão

Hoje existem **14 tamanhos entre 9px e 15,5px**, de meio em meio pixel:
9 · 9,5 · 10 · 10,5 · 11 · 11,5 · 12 · 12,5 · 13 · 13,5 · 14 · 14,5 · 15 ·
15,5. Isso não é escala — é um contínuo. Nada parece mais importante que
nada, porque nada é visivelmente maior que nada. É a causa número um da
sensação de tela datada.

Troque por **seis degraus, sem meio pixel**, e use só esses:

| papel | tamanho | peso | entrelinha | espaçamento |
|---|---|---|---|---|
| rótulo de sistema (mono) | 11px | 500 | 1.2 | +0.08em |
| apoio / pé de linha | 13px | 400 | 1.5 | 0 |
| corpo | 15px | 400 | 1.6 | 0 |
| título de painel | 20px | 700 | 1.3 | −0.01em |
| número da tira (mono) | 34px | 500 | 1 | −0.02em |
| manchete | 44px | 900 | 1.05 | −0.03em |

A regra: **se dois textos têm papéis diferentes, a diferença de tamanho
entre eles é de pelo menos um degrau inteiro.** Nunca 13 ao lado de 13,5.

### 8.2 · Caixa demais, elevação de menos

O CSS tem **21 bordas `1px solid var(--hair)`** e **3 sombras**. Tudo é
retângulo contornado, e é isso que dá o ar de painel administrativo antigo.

- Tire a borda da maioria dos painéis. Separe por **espaço** e por **um
  degrau de fundo** (o plano `#001433`; o painel `#001A5C`; o cartão que
  pede ação um pouco mais claro ou com o fio ciano aceso).
- Guarde a borda para o que precisa de contorno semântico: cartão crítico,
  item selecionado, foco.
- Onde hoje há fio, use uma sombra baixa e larga
  (`0 1px 2px rgba(0,0,0,.30), 0 8px 24px rgba(0,0,0,.18)`). Sombra em
  fundo escuro tem de ser sutil; se aparecer, está forte demais.

### 8.3 · Três raios, não seis

Hoje há 3, 6, 7, 8, 10 e 999px. Fique com **três**: `6px` (pastilha,
selo, campo), `14px` (painel e cartão — o valor da referência aprovada) e
`999px` (só pílula e chip). Um raio por papel.

### 8.4 · Movimento (revisto — a versão anterior desta seção tinha erros)

Auditei o `portal.css` entregue contra o checklist de motion. **O que já
está certo:** não há `transition: all`, não há `ease-in` (que deixa a
interface lenta justamente no instante em que o olho está olhando), só se
anima cor/transform, e as transições de hover usam `.15s ease` — que é
exatamente a curva certa para mudança de cor. Não mexa nisso.

**O que falta:**

- **Zero `:active` no arquivo inteiro.** Nenhum botão responde ao clique.
  É a falha mais sentida e a mais barata de consertar: todo elemento
  clicável ganha `transform: scale(0.97)` em `:active`, com
  `transition: transform 160ms ease-out`. Escala abaixo de 0.95 exagera;
  acima de 0.98 não se percebe.
- **Zero `@media (hover: hover) and (pointer: fine)`.** No celular, tocar
  dispara o hover e o estado fica grudado. Todo `:hover` vai dentro dessa
  media query.
- **Zero animação de entrada.**

**A entrada de conteúdo,** ao trocar de tela:

```css
opacity: 0 → 1;  transform: translateY(8px) → none;
transition: opacity 220ms cubic-bezier(0.23, 1, 0.32, 1),
            transform 220ms cubic-bezier(0.23, 1, 0.32, 1);
```

Escalonada em **50ms** entre blocos, no máximo os seis primeiros. Use
**transição com `@starting-style`**, não `@keyframes`: keyframes reiniciam
do zero quando interrompidos, e aqui a pessoa troca de tela no meio da
animação o tempo todo. Nada de bounce. Nada de `scale(0)` — nada no mundo
real aparece do nada.

A curva `cubic-bezier(0.23, 1, 0.32, 1)` é um ease-out forte; as curvas
nativas do CSS são fracas demais para dar a sensação de intenção.

**Saída mais rápida que a entrada:** entra em 220ms, sai em 120ms. O
usuário decide devagar e o sistema responde rápido.

**O ⌘K NÃO ANIMA.** A busca é aberta por atalho de teclado, dezenas de
vezes por dia. Ação repetida por teclado nunca anima — qualquer transição
ali faz o portal parecer lento e desconectado do comando. Abre e fecha
seco. Vale para qualquer atalho que venha depois.

**Nada de contador subindo nos números.** Cogitei e está fora: quem abre o
portal todo dia veria a mesma animação todo dia, e o que é visto todo dia
tem de ser instantâneo. Animação decorativa só onde é rara.

**`prefers-reduced-motion` NÃO é desligar tudo** — esta parte da versão
anterior estava errada. Movimento reduzido significa manter o que ajuda a
entender (opacidade, cor) e remover o que se desloca:

```css
@media (prefers-reduced-motion: reduce) {
  /* mantém: opacity e color */
  /* remove: translateY, scale */
}
```

### 8.5 · Foco e teclado

Só há dois `focus-visible` no arquivo inteiro. Todo elemento clicável
precisa de anel visível: `outline: 2px solid var(--cyan); outline-offset:
2px`. O portal tem busca com `⌘K` — quem usa atalho navega por teclado.

### 8.6 · Respiro e ritmo

As telas empilham painéis de largura total, todos com o mesmo espaço entre
si. Dá monotonia.

- Espaço entre painéis: **40px**; dentro do painel: **20px**; entre rótulo
  e valor: **6px**. Três medidas, não dez.
- Largura máxima do texto corrido: **70 caracteres**. Hoje a frase de
  apresentação atravessa a tela inteira.
- Cabeçalho de seção **grudado no topo** (`position: sticky`) quando a
  lista for longa — vale para a triagem das 374.

### 8.7 · O que NÃO mudar

Paleta, logo, Gotham no texto, mono em todo número e rótulo de sistema, a
estrutura de menu lateral, a ordem das telas e a linguagem de balcão. O
pedido do cliente foi explícito: **gosta de como está distribuído e do
estilo — quer só mais moderno.** Modernidade aqui é acabamento, não
identidade nova.

### 8.8 · A auditoria, linha a linha

| antes | depois | por quê |
| --- | --- | --- |
| nenhum `:active` no arquivo | `transform: scale(0.97)` com `transition: transform 160ms ease-out` | botão precisa responder ao toque; é o que faz a interface parecer viva |
| `:hover` solto | dentro de `@media (hover: hover) and (pointer: fine)` | no celular o toque dispara hover e o estado fica preso |
| 14 tamanhos de fonte entre 9 e 15,5px | 6 degraus: 11 · 13 · 15 · 20 · 34 · 44 | meio pixel de diferença não é hierarquia, é ruído |
| 21 bordas de 1px, 3 sombras | espaço + um degrau de fundo; borda só no que é crítico ou selecionado | contorno em tudo é o que dá ar de painel administrativo antigo |
| 6 raios de canto | 3: `6px` · `14px` · `999px` | um raio por papel |
| sem animação de entrada | `opacity` + `translateY(8px)`, 220ms, `cubic-bezier(0.23, 1, 0.32, 1)`, escalonado 50ms | conteúdo que aparece seco parece quebrado |
| (se usar) `@keyframes` na entrada | transição com `@starting-style` | keyframes reiniciam do zero ao ser interrompidos; troca de tela interrompe o tempo todo |
| entrada e saída na mesma duração | entra 220ms, sai 120ms | o sistema responde mais rápido do que a pessoa decide |
| `transition: transform .15s ease` no que entra | `cubic-bezier(0.23, 1, 0.32, 1)` | as curvas nativas são fracas; `ease` fica só em cor e hover, onde está certo |
| ⌘K com transição | sem animação nenhuma | ação de teclado repetida dezenas de vezes por dia nunca anima |
| 2 `focus-visible` no arquivo | anel em todo elemento clicável | quem usa ⌘K navega por teclado |

**O que já está certo e não deve ser tocado:** não há `transition: all`,
não há `ease-in`, só se anima cor e transform (nada de `height`, `width`,
`padding` — essas passam por layout e paint e derrubam quadro), e o
`.15s ease` das mudanças de cor está na curva correta.

## 9 · OS CAPÍTULOS NOVOS (payload já pronto)

Nenhum destes vira item de menu. São **capítulos** — a regra continua:
sete áreas profundas, não vinte e cinco rasas.

### 9.1 · Na clínica

**`jornada`** — em que momento a unidade dói, nos onze estágios que o
paciente vive. Traz `manchete` pronta, `quem_resolve` e `e_clinico`
(booleano que responde "é problema de cadeira ou de balcão?"). Cada
estágio tem `frase` pronta, `pct_dor`, `amostra_curta` e — quando não há
nada — `medido: false` com `porque_vazio` escrito. Desenhe como uma
linha do tempo horizontal, com a dor em vermelho sobre cada estágio.
**As duas lojas de Londrina têm a mesma dor: contato.** Isso precisa
saltar da tela.

**`acoes`** — o ciclo de cada problema: `problema`, `acao_recomendada`,
`antes`, `depois`, `dias` e `veredito` (resolvido, melhorou,
sem_mudanca, piorou, cedo_demais, aberto). Hoje todos os 16 arcos estão
em `cedo_demais`, e o payload traz `aviso` explicando por quê — mostre o
aviso, não esconda a tabela vazia.

**`oferta_da_cidade`** — vem com `e_da_cidade: true`, escreva assim.

### 9.2 · Na praça

**`oferta`** — `tese` ("a disputa desta cidade é por escassez — 24 dos
45 anúncios de aparelho medidos falam disso") e `posicao_vaga` ("ninguém
está falando de sem entrada"). Os doze eixos vêm com `o_que_significa`,
que é a razão de negócio de cada um. A posição vaga merece destaque:
é ali que o franqueado tem chance sem brigar de frente.

**`imprensa`** — manchetes com data, veículo e link. Era um contador.

**`ritmo_de_publicacao`** — quem publica e há quantos dias parou.
Perfil `parado: true` aparece apagado.

### 9.3 · O carimbo de confiança, em todo lugar

Vários blocos agora trazem `confianca`:

```json
{"natureza": "fato|inferencia|hipotese|recomendacao",
 "confianca": "alta|media|baixa|sem_medicao",
 "medido": true, "amostra": 64, "medicoes": 1, "janela_dias": 26,
 "procedencia": "medido em 64 buscas testadas, 1 medição",
 "o_que_aumentaria": "repetir a varredura noutra data"}
```

**Desenhe cada natureza diferente.** Fato pode ser número grande e
sólido. Inferência precisa de marca visual que a separe do fato —
mesmo tamanho, cor mais fria, ou um rótulo em mono. Recomendação nunca
com cara de medição: ela é conselho, e conselho errado com aparência de
número medido é o que destrói a confiança no produto inteiro.

`procedencia` é frase pronta, para pé de bloco. `sem_medicao` significa
"não perguntamos" — diferente de zero, que significa "perguntamos e não
há". A tela precisa distinguir os dois.

## 10 · O ESTADO DA CONFERÊNCIA (medido no casco entregue)

Conferi o zip 3 campo a campo contra o payload. **Não refaça o que já
está pronto:**

| item | estado |
|---|---|
| 7.1 · IBM Plex Mono empacotado | ✅ feito, zero pedido externo |
| 7.3 · arquivos velhos apagados | ✅ feito, nenhum plano de cidade sobrando |
| 7.4 · `abertura` vinda do dado | ✅ feito |
| 8.1 · escala de tipo em 6 degraus | ✅ 11 · 13 · 15 · 20 · 34 · 44 |
| 8.3 · três raios | ✅ 6 · 14 · 999 |
| 8.4 · `:active`, hover gating, `@starting-style` | ✅ feito |
| 8.5 · foco visível | ✅ de 2 para 8 |
| `estudos_sem_linha_oficial` | ✅ lido |

**O que falta, em ordem de importância:**

1. **Os capítulos da seção 9** — `jornada`, `acoes`, `oferta`,
   `oferta_da_cidade`, `imprensa`, `ritmo_de_publicacao` e o carimbo
   `confianca`. Nenhum deles é lido hoje. É a maior parte do trabalho, e
   é onde está a inteligência nova.
2. **8.2 · as bordas** — continuam 23 contra 8 sombras. Era o único item
   do acabamento que não andou: painel ainda é caixa contornada.
3. **7.2 · rota desconhecida** — `#qualquercoisa` ainda abre a moldura
   vazia; mande para o Painel de Controle.
4. **As duas datas do índice**, campo novo: `clinicas_indice.json` agora
   traz `cadastro_lido_em` (a lista do site, lida todo dia) e
   `fichas_medidas_em` (a varredura do Google, que custa cota e roda de
   vez em quando). **Elas são diferentes de propósito.** Cada unidade
   traz `ficha_medida_em`; quando for null, nota e avaliações não foram
   medidas para aquela unidade — apague o campo, não escreva zero.
   Mostre as duas datas no cabeçalho da tela de Clínicas: foi a
   divergência entre elas que fez o portal dizer 374 numa tela e 373
   noutra.

## 11 · OS BLOCOS DE TERRITÓRIO E MOVIMENTO (payload já pronto)

Nenhum item de menu novo. Tudo entra como capítulo dentro do que existe.

### 11.1 · Na clínica — "Seu território"

`meu_territorio` traz, por unidade: `location` (lat/lng), `bairro`,
`clinica_mais_proxima`, `aparelho_mais_proximo`,
`unidade_da_rede_mais_proxima` e `raios` em 1, 2 e 5 km — cada raio com
`clinicas`, `de_aparelho` e `da_rede`.

**A hierarquia semântica é obrigatória aqui**, e é o exemplo mais claro
do carimbo de confiança:

| o que a tela diz | natureza | como desenhar |
|---|---|---|
| "a clínica mais próxima está a 0,07 km" | **fato** | número grande, sólido |
| "alta proximidade entre unidades da rede" | **inferência** | cor mais fria, rótulo em mono |
| "pode haver sobreposição de mercado" | **hipótese** | texto, sem número gigante |
| "estudar antes de abrir outra unidade aqui" | **recomendação** | cartão de ação, nunca com cara de medição |

Escreva **"alta proximidade entre unidades"**, nunca "canibalização". E
sempre que aparecer distância, o pé de bloco diz o que ela não é: linha
reta não é tempo de deslocamento.

Em Porto Alegre há quatro unidades a 130–250 metros umas das outras, e
uma a 12 km delas com uma única clínica no raio de 1 km. Essas duas
realidades na mesma cidade precisam parecer diferentes na tela.

### 11.2 · Na clínica — "O que mudou ao seu redor"

`movimentos.eventos[]`, com `titulo`, `fato`, `por_que_importa`,
`decisao`, `severidade` e `confianca`. Vem marcado `e_da_cidade: true`.
`movimentos.resumo.aviso_de_metodo` explica quantas clínicas entraram em
cada medição e quantas eram comparáveis — mostre essa frase, é ela que
impede o leitor de achar que sumiu clínica quando foi a varredura que
variou.

### 11.3 · Na clínica — "O que fazer"

`execucao.itens[]`. Cada item tem `e_marketing` (booleano) e um bloco
`execucao`. **Desenhe os dois de formas diferentes:**

- `e_marketing: false` → é da unidade. Mostre `porque_nao_e_marketing`,
  que explica por que campanha não resolve aquilo.
- `e_marketing: true` → é briefing. Tem `problema`, `objetivo`,
  `evidencias[]`, `nao_fazer[]`, `entregavel_sugerido`, `prazo`,
  `metrica_de_validacao` e `recoletar_em_dias`.

Não há orçamento e não há promessa de retorno. Se a tela inventar
qualquer um dos dois, o produto perde a credibilidade inteira.

### 11.4 · Na praça — "A cidade por dentro"

`bairros` (com `territorio[]` de cada unidade),
`movimentos_do_mercado`, `clinicas_com_coordenada` e
`raios_declarados_km`. Cidade com várias unidades **não pode** parecer um
mercado homogêneo: Porto Alegre tem 33 bairros medidos e a rede em
quatro, com quatro lojas num só.

### 11.5 · No painel — só o que mudou

`franqueadora.json → movimentos_prioritarios`. Só entram eventos de
severidade **alta ou crítica**; `total_no_periodo` diz quantos existem ao
todo, e `pracas_sem_delta` lista as que têm uma medição só. Essa última
lista importa: praça sem segunda medição **não é praça sem movimento**, é
praça sem base de comparação, e a tela precisa dizer isso.

---

## 12 · A BUSCA TEM DUAS ESCALAS, E A TELA PRECISA MOSTRAR AS DUAS

Este é o bloco mais importante desta rodada, porque ele **corrige uma
conclusão errada que o portal já estava exibindo**.

Até agora existia uma medida só: `presenca_na_busca` — "a clínica aparece
em N de M buscas da cidade". Para Mafra, isso responde. Para São Paulo, o
portal dizia **"aparece em 0 de 193 buscas"** para as quatro unidades da
capital, e qualquer pessoa lendo aquilo concluiria que as quatro estão
invisíveis e precisam da mesma coisa.

A medição nova refez a mesma pergunta a partir do **endereço de cada
clínica**, com viés circular de 3 km, e o resultado foi outro:

| unidade | na cidade | perto dela |
|---|---|---|
| OrthoDontic · São Miguel Paulista | 0 de 193 | **5 de 5, todas em 1º** |
| OrthoDontic · Tatuapé | 0 de 193 | 3 de 5 |
| OrthoDontic · Lapa | 0 de 193 | 1 de 5 |
| OrthoDontic · República | 0 de 193 | 1 de 5 |

Quatro lojas da mesma cidade, dois diagnósticos opostos. Uma não precisa
de nada; outra precisa de ficha revisada. A tela antiga mandava as quatro
fazerem a mesma coisa.

### 12.1 · O bloco novo na clínica — `perto_da_clinica`

Campos prontos: `de`, `aparece_em`, `em_primeiro`, `melhor_posicao`,
`invisivel_perto`, `raio_m`, `frase`, `buscas[]` (cada uma com `frase`,
`posicao`, `topo`, `topo_avaliacoes`, `topo_metros`),
`quem_aparece_na_frente[]` e `na_cidade` (`aparece_em`/`de` da leitura
antiga, para a comparação lado a lado).

Como desenhar:

- As duas leituras aparecem **juntas e rotuladas**, nunca fundidas num
  número só. Sugestão de rótulo de balcão: **"na cidade inteira"** e
  **"perto da clínica"**. Nunca "local" e "global" — ninguém no balcão
  fala assim.
- Quando `na_cidade.aparece_em == 0` e `aparece_em > 0`, a tela precisa
  dizer, com todas as letras, que a leitura de cidade **não vale nesta
  escala**. Essa é a informação, não um detalhe de rodapé.
- `buscas[]` é uma lista curta (5 itens). Mostre a frase, a posição
  (ou "fora") e quem apareceu em primeiro. `topo_metros` é a distância em
  metros entre o primeiro colocado e a porta da clínica — é o que torna a
  linha concreta.
- `quem_aparece_na_frente[]` é **posição, não roubo de paciente**. O texto
  não pode sugerir canibalização: isso não está medido.

### 12.2 · O que a tela NÃO pode dizer

- Que o raio de 3 km é a área de captação. Não é: distância no mapa não é
  tempo de deslocamento.
- Que a clínica "perdeu" para quem está na frente. Ela está atrás na
  ordem do mapa. Só isso.
- Que a medição é volume de busca. Continua sem volume.

### 12.3 · Cada unidade agora tem nome próprio

As quatro linhas idênticas "SP · São Paulo · OrthoDontic" acabaram. O
campo `unidade` chega desambiguado por bairro e, quando o bairro não
basta (Porto Alegre tem quatro unidades no Centro Histórico, Curitiba
quatro no Centro), por rua:

    OrthoDontic · Tatuapé
    OrthoDontic Centro Histórico · R. dos Andradas

O casco **não monta** esse nome — ele chega pronto, como todo rótulo.
Onde a tela hoje mostra `rotulo` sozinho e repete a cidade, use
`rotulo` + `unidade`.

### 12.4 · No Radar — `territorio`

Cada linha do Radar (`oportunidades[]`, `ja_tem_unidade[]`,
`nao_conferidas[]`) agora carrega `territorio`, com `bairros_medidos`,
`clinicas_mapeadas`, `bairro_do_topo`, `clinicas_no_topo`, `pct_no_topo`,
`frase` e `estudo` (link para a página da praça). Serve para diferenciar
duas cidades com o mesmo total de clínicas: numa elas estão espalhadas,
noutra empilhadas numa rua só.

O campo `e_concentracao_nao_demanda` existe para ser **exibido**, não
escondido: bairro cheio de clínica é onde as clínicas abrem, não
necessariamente onde o paciente mora.

### 12.5 · A ferramenta nova no painel — `perto`

**Não é item de menu.** O menu continua com sete seções. Isto é mais um
cartão dentro do PAINEL DE CONTROLE, grupo **lojas**, com a mesma anatomia
dos outros: pergunta, número, frase.

    pergunta  "A clínica aparece para quem está perto dela?"
    número    2        (lojas que não aparecem nem no próprio quarteirão)
    frase     "de 45 lojas medidas a partir do próprio endereço, essas não
               aparecem nem para quem está a 3 km. Outras 9 lojas pareciam
               invisíveis pela busca da cidade inteira e aparecem aqui:
               numa cidade grande ninguém disputa o nome do município."

A tela `perto` lê `dados/portal/perto_da_loja.json`. Ela é uma **lista de
lojas**, ordenada da pior para a melhor, e cada linha traz: rótulo da praça,
nome da unidade, `aparece_em`/`de`, `em_primeiro`, e a comparação
`na_cidade`. O cabeçalho da tela usa `o_que_e`, `por_que_existe` e
`o_que_nao_e`, que já vêm escritos no payload.

O número do cartão é o das lojas **realmente** invisíveis. Não use
`invisivel` da leitura de cidade para esse cartão: é o número que estava
errado e que esta tela existe para corrigir.
