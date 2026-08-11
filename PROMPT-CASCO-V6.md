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
