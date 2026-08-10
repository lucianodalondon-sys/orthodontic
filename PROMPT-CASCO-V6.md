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
INÍCIO      os ALERTAS DAS CLÍNICAS na frente (fila.json) + o mapa do
            Brasil + a régua da rede (374 · 348 · 26 · 304). Clicar num
            alerta abre a PÁGINA DA CLÍNICA.
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
**Início · Clínicas · Praças · O que a rede ensina · Radar de cidades ·
A marca · Arquivo**.

## 2 · A página da clínica (o coração — payload novo)

`clinicas/<local_id>.json` já vem composto, um por unidade. Capítulos, na
ordem:

1. **cabeçalho** — rótulo (`UF · Cidade` + unidade), nota, avaliações,
   ritmo, posição na cidade, `faixa` (selo de cor) e `tarefa` (aberta /
   vencida, com `vence_em`).
2. **o que fazer agora** — `gatilhos[]` (com `fonte` em pé de linha),
   `quem_avanca` e `acao` (o quê · prazo · dono · custo) em destaque.
3. **o que mudou entre as coletas** — `o_que_mudou` (antes → agora,
   delta, nota, `aviso` visível quando o período é curto). Se null:
   "ainda só uma medição — a comparação nasce na próxima coleta".
4. **a voz do paciente** — `voz_do_paciente[]` já com rótulo de balcão
   (`o_que_e` + `pct`), barras finas.
5. **avaliações esperando resposta** — `sem_resposta.itens[]` (nota,
   data, texto do paciente).
6. **o rival de aparelho** — `rival.vantagens_deles[]` OU
   `sem_comparacao_porque`; `rival.fora[]` numa lista recolhida "fora da
   comparação — outro produto", cada um com `por_que_fora`. Uma linha
   fixa: só quem vende aparelho entra na comparação.
7. **a linha do tempo** — `eventos[]` (data, `quem`: nossa · paciente ·
   fila · rival, texto pronto), linha vertical fina, cor por `quem`.

## 3 · Mudanças de dado que as telas precisam refletir

- **Praça = UMA cidade.** `riomafra` não existe mais (é `mafra`); Cuiabá
  não soma mais Várzea Grande. Rótulos vêm prontos (`MT · Cuiabá`).
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
- **Rótulo com a UF na frente**, recebido pronto.
- **Loja não se funde com loja** — Cuiabá são três páginas, Londrina duas.
- **Estado vazio é conteúdo** — ferramenta apagada mostra o porquê;
  `o_que_isso_nao_ve` aparece onde existir.
- **Nada de dado interno**, e toda tela de desempenho diz isso.
- **Linguagem de balcão** — palavra interna (casco, escada, ponta, andar)
  nunca aparece na tela.
