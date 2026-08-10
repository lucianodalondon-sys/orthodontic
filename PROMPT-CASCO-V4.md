# Prompt para o Claude Design — casco v4

Este prompt substitui TODOS os anteriores (v2, v3 e adendos). O casco atual
não é o que o cliente quer — **redesenhe a partir desta direção**. Os dados
estão em `dados/` neste projeto, e o Design System da OrthoDontic também
(`tokens/`, `assets/`, `guidelines/`).

---

## 1 · A direção visual — moderna, de linhas finas

O que o cliente pediu, na ordem em que pediu: **design moderno · o mapa do
Brasil na entrada · o Design System da OrthoDontic usado de verdade · linhas
finas.**

### A regra-mãe: hierarquia por tamanho e espaço, nunca por peso

- **Traço fino em tudo.** Bordas e divisores de `1px` (`--od-line`,
  hairline). O mapa do Brasil em stroke fino. Ícones em outline `1.5px`.
  Nada de bloco chapado pesado, nada de borda grossa, nada de card
  "inflado".
- **Gotham nos pesos leves.** Números grandes em Gotham Light/Book em corpo
  GRANDE (48–96px) — o impacto vem do tamanho e do espaço ao redor, não do
  bold. Bold só em rótulos curtos e CTAs. Nunca um parágrafo em bold.
- **Ar.** Espaçamento generoso entre seções (use a escala de `spacing.css`
  nos degraus altos). Uma tela de inteligência moderna respira; densidade é
  o inimigo — o dado denso vive em gavetas que se abrem, não na primeira
  dobra.
- **Sombra quase nenhuma.** Prefira hairline border a sombra. Quando
  precisar de elevação, só `--shadow-xs`/`--shadow-sm` (navy-tinted, do
  DS). O glow ciano é EXCLUSIVO de CTA primário e estado ativo.

### A paleta, do DS (`tokens/colors.css`)

- Fundo claro: `--od-cream`/branco com lavagens `--od-sky` e `--od-cyan-050`.
- Texto: `--od-navy`. Cinza `--od-gray` só para apoio.
- **`--od-cyan` é a cor do DADO VIVO** — o número que importa, o estado no
  mapa, a linha ativa, o CTA. Se tudo for ciano, nada é.
- O cabeçalho pode mergulhar no `--grad-navy` (hero escuro, texto claro) —
  é a "sala de comando" — com o resto da página claro. Contraste de mundos:
  comando escuro em cima, leitura clara embaixo.
- Semáforo da fila (vermelha/amarela/verde): derive dos tokens de status do
  DS, dessaturado e fino (dot + hairline, não bloco colorido).
- Os **anéis concêntricos** do brand-motif entram como assinatura discreta
  no cabeçalho (traço fino, baixa opacidade), nunca como decoração barulhenta.

### O mapa do Brasil é a entrada

A primeira dobra da tela da franqueadora é **o mapa**, grande, protagonista:

- Geometria real dos 27 estados (`assets/brasil-ufs.js` do casco anterior
  pode ser reaproveitado), desenhada em **traço fino navy** sobre fundo
  claro (ou traço claro sobre o hero navy — escolha uma e seja consistente).
- Preenchimento por densidade de unidades em **escala de ciano translúcido**
  (`--od-cyan` em alfas) — dados de `franqueadora.json → mapa`. Estado sem
  unidade fica só o contorno: o vazio É a informação (AC, AP, MA, RN).
- Hover/clique por estado: unidades, abertas, em implantação, praças
  medidas — tudo já vem pronto no payload.
- Ao lado ou sobreposto ao mapa, o bloco `agora`: a pergunta pequena como
  olho, a `manchete` em Gotham Light gigante, e `o_que_e_atencao` sempre
  visível. O mapa e a manchete juntos SÃO a sala de comando.

### O que "moderno" significa aqui (e o que não significa)

Sim: grid limpo, tipografia grande e leve, hairlines, microtransições
discretas (150–200ms), scroll suave entre andares, dark-hero + corpo claro.
Não: glassmorphism, gradiente em todo card, ícone 3D, emoji como ícone,
sombra colorida espalhada, animação que chama atenção para si.

---

## 2 · A arquitetura — três andares, e a ordem importa

Leia `manifest.json` primeiro; `franqueadora.json → andares` + `ferramentas`
(campo `andar`) montam o menu. Peso visual: AGORA domina, DECIDIR é o corpo,
CONSULTAR é gaveta recolhida.

```
AGORA      O que mudou · A caixa de respostas · A fila de intervenção
DECIDIR    Os padrões da rede · A rede inteira · O rival · Radar de
           Oportunidade · Quem sustenta · Reputação · Território vazio
CONSULTAR  A voz da cidade · Mapa · Presença na busca · Auditoria de ficha ·
           A escada · As praças · Os planos · Calendário (apagado) · Evidências
```

`disponivel: false` → item apagado COM o `indisponivel_porque` visível.

---

## 3 · As telas, uma a uma (payloads em `dados/`)

### O que mudou — `o_que_mudou.json`
Por praça: `dias_medidos` + `aviso` (quando o período é curto, o aviso vem
escrito — **desenhe visível**; ele morre sozinho quando o ciclo engorda).
`nossas[]` com `antes → agora (delta)` (▲ ▼ ·), `quem_mais_ganhou[]` (o
caso-exemplo real: Dentel, Londrina, 5 → 22 em 3 dias) e `contador_caiu[]`
em destaque — contador que cai é avaliação removida, evento raro.

### A caixa de respostas — `caixa_de_respostas.json`
Lista de trabalho POR LOJA: `unidades[]` com `abertas`, `com_texto`,
`itens[]` (nota, data, texto). `a_regra` visível: responder é higiene de
reputação, não motor de ritmo.

### A fila de intervenção — `fila.json`
Cada linha: `pos` + `faixa` (cor fina, não bloco), `rotulo` (+ ` · ` +
`unidade_curta` SÓ se não for null), `quem_avanca` como confronto,
`gatilhos[]` com `fonte` em pé de linha, `acao` com prazo·dono·custo, e o
`ciclo` com três degraus — hoje todo null, desenhado com travessões e a
legenda "o ciclo começa na próxima coleta". `o_que_isso_nao_ve` fechado e
legível no fim.

### Os padrões da rede — `padroes.json`
A tela mais importante de DECIDIR. Ordem: 1) `hipoteses_testadas[]` — quatro
cartões com o veredito **NÃO SEPARA** grande; o valor da tela é o que caiu.
2) `conclusao` (t, leitura, consequencia, controle — Cuiabá, três lojas).
3) `lojas[]` como tabela fina. 4) `o_que_isso_nao_ve`.

### A rede inteira — `rede_inteira.json`
As 374. `alertas[]` por gravidade, cada um com `por_que` e `de_quem_e`
(franqueadora | unidade) — **marque os de franqueadora**; Patrocínio fechada
no Google é o primeiro. `por_uf[]` casa com o mapa da entrada.
`nao_confirmadas_lista[]` nomeadas com motivo.

### O rival — `rival.json` (POR LOJA)
`pracas[]` é lista de LOJAS: `local_id`, `unidade`, e OU `vantagens_deles[]`
OU `sem_comparacao_porque` — quando vier, desenhe a linha apagada com o
motivo. `padrao_da_rede` em cima: eixos com `perde_em/de` e
`de_quem_e_a_decisao` marcado quando "franqueadora".

### A escada — `achados.json`
Degraus: `constante` · `vale_para_a_rede` · `se_repete` · `candidata` ·
`derrubada` · `nao_testavel`. Cada achado pode trazer `como_se_mede`
(visível), `excecoes[]` (nomeadas, nunca escondidas), `sem_amostra[]`.

### As demais
Radar (`radar.json` + `oportunidade/*.json`), Quem sustenta
(`rede_cruzamento.json`), Reputação (`franqueadora.json →
reputacao_das_redes` + `reputacao_fora_da_tela` com os excluídos nomeados),
Voz da cidade (`voz_da_cidade.json`), praças (`pracas/*.json`, que agora
trazem `o_que_mudou` local), planos (`planos/*.json`), evidências.

---

## 4 · As regras que não caem nunca

- **O casco NUNCA calcula.** Nenhuma soma, média, %, ordenação por valor ou
  montagem de rótulo. Falta número? Conserto é no build, não no casco.
- **Rótulo com UF na frente** (`MG · Contagem`), recebido pronto.
- **Estado vazio é conteúdo**: ferramenta apagada mostra o porquê; ciclo
  vazio mostra os travessões; `o_que_isso_nao_ve` aparece onde existir.
- **Nada de dado interno**, e toda tela de desempenho diz isso.
- **Loja não se funde com loja** — onde o payload traz `local_id`, a tela
  mostra por loja.
