# Prompt para o Claude Design — casco v5

Este prompt substitui TODOS os anteriores (v2, v3, v4 e adendos). O v4 pediu
um design de "sala de comando" com mapa protagonista e três andares — **o
cliente não gostou: ficou confuso, não dava para entender nada**. A direção
agora é a do PRIMEIRO desenho, o que o cliente gostou:

> **Tudo em cards. Fácil de entender. Linguagem simples.**
> Quem abre precisa entender cada card em 5 segundos, sem manual.

Os dados estão em `dados/` neste projeto, e o Design System da OrthoDontic
também (`tokens/`, `assets/`, `guidelines/`).

---

## 1 · A regra-mãe: clareza antes de estilo

- **A home é uma grade de cards.** Nada de "andares", nada de hero-mapa,
  nada de menu conceitual. Cards em grade, agrupados por 4 títulos simples.
- **Cada card é: uma pergunta + um número grande + uma frase.** Tudo vem
  pronto de `franqueadora.json → cards[]`: `pergunta`, `numero`, `frase`,
  `titulo`, `tela`, `grupo`. O casco NÃO inventa texto nem número.
- **Linguagem de balcão.** As palavras internas do projeto — casco, escada,
  ponta, andar, praça-régua — NUNCA aparecem na tela. Se um título soar
  "inteligente", troque pelo que uma pessoa da franqueadora falaria.
- **Card apagado é conteúdo.** `disponivel: false` → card visível, opaco,
  com `indisponivel_porque` legível. Esconder o que falta é proibido.

## 2 · Os 4 grupos (de `franqueadora.json → grupos`)

```
A REDE                    mapa · alertas nas fichas · Reclame Aqui
AS 10 LOJAS ACOMPANHADAS  o que mudou · onde agir · avaliações sem resposta ·
                          concorrentes de ortodontia · o que faz crescer ·
                          quem mantém o ritmo
EXPANSÃO                  onde abrir a próxima · as praças estudadas
ARQUIVO                   (gaveta recolhida) voz da cidade · busca · cadastro ·
                          canais · regras · planos · evidências
```

A REDE e AS 10 LOJAS dominam a página. EXPANSÃO vem depois. ARQUIVO nasce
recolhido — um clique abre a gaveta.

Acima da grade, um cabeçalho curto: logo, "OrthoDontic · Inteligência de
mercado", a linha de cobertura (de `cobertura.aviso` — sempre visível) e a
data do corte. Só isso.

## 3 · O visual — o DS da OrthoDontic, leve

- Fundo claro (`--od-cream`/branco), cards brancos com **borda hairline
  1px** (`--od-line`) e canto suave. Sombra só `--shadow-xs` no hover.
- Número grande do card em **Gotham Light 48–64px, `--od-navy`**; quando o
  número é alerta (alertas graves, contadores caídos, sem resposta), o
  número vai em `--od-cyan`. `numero: null` → o card vive só de frase.
- Título do card em bold curto; pergunta em cinza `--od-gray`; frase em
  corpo normal. Nada de parágrafo em bold, nada de caixa alta longa.
- Os anéis concêntricos do brand entram discretos no cabeçalho. Semáforo
  (vermelha/amarela/verde) como dot fino + texto, nunca bloco colorido.
- Moderno aqui significa: grade limpa, muito ar, hairlines, transição de
  150ms no hover. NÃO significa: gradiente em card, glassmorphism, ícone
  3D, animação chamativa.

## 4 · As telas que os cards abrem

Cada card leva à sua tela (campo `tela`). As mais importantes:

- **mapa** — o mapa do Brasil (geometria de `assets/brasil-ufs.js`, traço
  fino) com densidade em ciano translúcido, dados de `franqueadora.json →
  mapa`. Estado sem unidade fica só contorno. Aqui dentro, não na home.
- **fila** (`fila.json`) — a lista de lojas por urgência. Cada linha:
  faixa (dot), rótulo pronto (`rotulo` + `unidade_curta` se não-nulo),
  gatilhos com fonte, ação com prazo·dono·custo. O `ciclo` nasce nulo:
  desenhe travessões com "começa na próxima coleta".
- **rival** (`rival.json`) — POR LOJA. Cada loja: OU `vantagens_deles[]`
  OU `sem_comparacao_porque` (linha apagada com o motivo). Os
  `rivais_fora[]` aparecem numa lista discreta "fora da comparação — outro
  produto", cada um com `por_que_fora`. **Só quem vende aparelho entra na
  comparação; a tela diz isso em uma linha.**
- **mudou** (`o_que_mudou.json`) — por praça: `dias_medidos` + `aviso`
  visível quando existir, `nossas[]` com antes → agora (▲ ▼ ·),
  `quem_mais_ganhou[]` (já filtrado: só rivais de aparelho) e
  `contador_caiu[]` em destaque.
- **caixa** (`caixa_de_respostas.json`) — lista de trabalho por loja:
  nota, data, texto da avaliação sem resposta. `a_regra` visível.
- **padroes** (`padroes.json`) — os 4 cartões de hipótese com o veredito
  "NÃO SEPARA" grande, depois `conclusao`, depois a tabela `lojas[]`.
- **rede_inteira** (`rede_inteira.json`) — `alertas[]` por gravidade com
  `por_que` e `de_quem_e`; `por_uf[]` casa com o mapa.
- **radar** (`radar.json` + `oportunidade/*.json`) — as cidades de
  expansão. Sempre com a frase: estudo de oportunidade, fora das contas
  da rede.

As demais telas (`voz_da_cidade`, `busca`, `fichas`, `territorio`,
`achados`, `planos`, `evidencias`, `pracas/*.json`) seguem o mesmo padrão:
título simples, o payload na ordem em que vem, estados vazios declarados.

## 5 · As regras que não caem nunca

- **O casco NUNCA calcula.** Nenhuma soma, média, %, ordenação por valor,
  montagem de rótulo. Falta número? O conserto é no build, não aqui.
- **Rótulo com a UF na frente** (`MG · Contagem`), recebido pronto.
- **Loja não se funde com loja.** Onde o payload traz `local_id`, a tela
  mostra por loja — Cuiabá são três lojas, Londrina duas.
- **Concorrente é só quem disputa aparelho.** As telas de confronto já
  recebem filtrado; quem ficou de fora aparece nomeado com o motivo.
- **Estado vazio é conteúdo.** Card apagado mostra o porquê; ciclo vazio
  mostra travessões; `o_que_isso_nao_ve` aparece onde existir.
- **Nada de dado interno**, e toda tela de desempenho diz isso.
