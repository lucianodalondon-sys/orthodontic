# Prompt para o Claude Design — casco v3

Cole isto inteiro. Ele substitui o PROMPT-CASCO-V2.

---

## O que mudou desde a versão que você entregou

O design está aprovado. **Não redesenhe nada.** Tipografia, paleta, anéis
concêntricos, sombras, pílulas, o mapa, a barra lateral — tudo fica.

O problema é de **organização**, não de estilo: treze ferramentas lado a lado
viraram um armário. Quem abre não sabe por onde começar, e a ferramenta que
muda uma decisão fica do lado da que só se consulta.

O payload mudou para resolver isso. Três coisas novas em
`dados/portal/franqueadora.json`, e um arquivo novo.

---

## 1 · A porta de entrada: `franqueadora.json → agora`

Este bloco é **a primeira coisa da tela**, acima do mapa e acima do menu.
Se ele for `null`, some com a seção inteira — não invente estado vazio.

```json
"agora": {
  "pergunta": "Em quais unidades a OrthoDontic está perdendo atenção local, para qual concorrente, e onde intervir primeiro neste mês?",
  "manchete": "4 de 10 unidades medidas estão em faixa vermelha. A primeira é PR · Londrina.",
  "em_risco": 4,
  "unidades": 10,
  "o_que_e_atencao": "participação observável em busca, avaliações, publicidade e atividade digital. Não é faturamento — nenhum número desta tela vem de dado interno da rede.",
  "primeiras": [ /* as 3 primeiras linhas da fila, resumidas */ ],
  "tela": "fila"
}
```

Como desenhar:

- `pergunta` em cima, pequena, como olho — é ela que justifica o portal existir.
- `manchete` grande. É o único número que a diretoria precisa ler em pé.
- `o_que_e_atencao` logo abaixo, discreto mas **sempre visível**. Não é
  rodapé, não é tooltip. Se sumir, o portal vira promessa de faturamento.
- `primeiras` como três cartões, e um CTA em pílula levando para `tela: "fila"`.

---

## 2 · O menu em três andares: `franqueadora.json → andares` + `ferramentas`

Cada ferramenta agora tem `andar`. Agrupe por `andares` (que vem na ordem
certa e traz `nome` e `explica`), e renderize as ferramentas de cada andar.

```
AGORA      onde intervir primeiro neste mês          → 1 ferramenta
DECIDIR    as quatro que mudam uma decisão           → 4 ferramentas
CONSULTAR  de onde veio cada número                  → 8 ferramentas
```

Peso visual proporcional: **AGORA** domina, **DECIDIR** é o corpo do menu,
**CONSULTAR** é uma gaveta — menor, mais discreta, pode nascer recolhida.

`disponivel: false` continua igual à v2: item apagado, **com o
`indisponivel_porque` visível**. Esconder o que falta é o que faz a diretoria
achar que o portal mede tudo.

---

## 3 · A tela nova: `dados/portal/fila.json`

Uma tela, uma lista, ordenada. É a tela mais importante do portal inteiro.

```json
{
  "pergunta": "...", "o_que_e_atencao": "...",
  "manchete": "...", "unidades": 10, "em_risco": 4,
  "criterio": [ {"chave","titulo","peso"} ],
  "faixas":   [ {"de": 60, "nome": "vermelha"}, ... ],
  "fila": [ {
      "pos": 1, "urgencia": 90, "faixa": "vermelha",
      "rotulo": "PR · Londrina", "unidade_curta": "Centro",
      "ritmo": 0.8, "meses": 2, "nota": 3.8, "avaliacoes": 76,
      "posicao": 23, "de": 24,
      "quem_avanca": {"nome": "Vittallon Odontologia", "ritmo": 35.6, "meses": 11, "nota": 4.9, "posicao": 1},
      "gatilhos": [ {"chave","titulo","fato","peso","fonte"} ],
      "acao": {"o_que","prazo","dono","custo","por_causa_de"},
      "ciclo": {"alertado_em","acao_confirmada","confirmada_em","resultado","medido_em"}
  } ],
  "o_que_isso_nao_ve": [ "...", "...", "..." ]
}
```

Como desenhar cada linha, na ordem:

1. **`pos` e `faixa`.** A faixa é cor (vermelha / amarela / verde) — use a
   paleta que você já definiu, não invente vermelho e verde de semáforo.
   `urgencia` é um número de 0 a 100 e aparece pequeno, ao lado.
2. **`rotulo`** e, **só se `unidade_curta` não for `null`**, ` · ` +
   `unidade_curta`. Quando é `null`, a praça tem uma unidade só e repetir o
   rótulo ao lado dele mesmo é ruído. **O casco nunca monta rótulo** — a UF já
   vem na frente, pronta.
3. **`quem_avanca`** ao lado, como confronto: o nome do concorrente, o ritmo
   dele contra o nosso. Se for `null`, não desenhe o bloco.
4. **`gatilhos`** — a lista de evidências, cada uma com `titulo` (curto) e
   `fato` (a frase com o número). O `fonte` é o arquivo de onde saiu: mostre
   em hover ou num pé de linha discreto. Ele é o que faz alguém acreditar.
5. **`acao`** — em destaque, no fim da linha: `o_que`, e abaixo
   `prazo · dono · custo`. Um alerta sem dono é boletim, e boletim ninguém
   executa.
6. **`ciclo`** — o bloco que fecha a linha. **Hoje ele está todo `null`, e é
   assim que tem de aparecer.** Desenhe três degraus:

   ```
   alertado em 09/08  →  ação confirmada: —  →  resultado: —
   ```

   Com uma legenda fixa: *"o ciclo começa na próxima coleta"*. Esse estado
   vazio é decisão de produto, não bug. É a promessa visível de que no mês que
   vem esta tela responde "o que recuperamos?" — e é o que separa este portal
   de um relatório.

No fim da tela, **`o_que_isso_nao_ve`** como bloco fechado e legível, não como
letra miúda. Ele diz que a fila mede 10 de 374 unidades e que não enxerga
contrato nem receita. Não amenize.

**`criterio`** vira um "como esta fila é montada", recolhido por padrão. Quem
duvida da ordem abre e vê os pesos.

---

## 4 · A ferramenta que saiu

**"Carteira do consultor" não existe mais no menu.** Ela prometia *"quem
visitar primeiro, e por quê"* e entregava quatro pareceres sobre uma peça de
anúncio. Quem cumpre essa promessa agora é a fila. Se você tiver a rota
`#/consultor` no casco, remova-a.

`corretor.json` continua no repositório e continua sendo lido pela tela de
praça — só não é mais ferramenta de primeiro nível.

---

## 5 · As regras da v2 que continuam valendo

- **O casco NUNCA calcula.** Nenhuma soma, média, porcentagem, ordenação por
  valor ou montagem de rótulo. Todo número que aparece na tela sai pronto do
  JSON. Se faltou um número, o conserto é no `build_portal.py`, não no casco.
- **`manifest.json` é o índice.** Leia ele primeiro; ele diz quais telas
  existem. `fila` já está na lista `arquivos.rede`.
- **Rótulo com UF na frente:** `MG · Contagem`. Nunca `Contagem/MG`.
- **Estado vazio é conteúdo.** Ferramenta apagada mostra o porquê; ciclo vazio
  mostra que está vazio; `o_que_isso_nao_ve` aparece em toda tela que tem.
- **Nada de dado interno.** Nenhum número deste portal vem do CRM da rede, e
  toda tela que fala de desempenho precisa dizer isso.

---

## 6 · O que NÃO fazer

- Não redesenhe o mapa, a barra lateral, a tipografia ou a paleta.
- Não transforme a fila em tabela densa. Cada linha é um caso com narrativa:
  quem está caindo, contra quem, por qual evidência, o que fazer.
- Não esconda `o_que_e_atencao` nem `o_que_isso_nao_ve` atrás de ícone.
- Não preencha o `ciclo` com placeholder simpático ("aguardando execução ✨").
  Escreva o travessão e a legenda, e pronto.
- Não some com as oito ferramentas de CONSULTAR. Elas ficam — recolhidas,
  não deletadas.

---

# ADENDO v3.1 — a tela do rival, e o que mudou no payload

Três coisas novas desde o v3. O design continua aprovado; nada de redesenhar.

## A · Ferramenta nova no andar DECIDIR: `dados/portal/rival.json`

**"O que o rival faz que dá certo"** — a leitura das 33.348 avaliações de
concorrente. É a única tela do portal que dá instrução em vez de diagnóstico.

Duas camadas, e a ordem importa:

**1 · `padrao_da_rede`** — desenhe primeiro. É a leitura da franqueadora:

```json
{ "o_que_e": "Tem profissional que o paciente chama pelo nome",
  "perde_em": 5, "de": 5, "pior_razao": 5.0,
  "nosso_pior": 6.0, "nosso_melhor": 10.9,
  "de_quem_e_a_decisao": "franqueadora",
  "pracas": [{"rotulo": "MG · Contagem", "razao": 5.0, "quem": "ODONTO ART…"}] }
```

Quando `de_quem_e_a_decisao` for `"franqueadora"`, marque a linha. É o que
separa "visita do consultor" de "treinamento de rede" — e é a frase que a
diretoria compra.

**2 · `pracas[]`** — o detalhe por cidade, com `vantagens_deles` ordenadas
por `razao`. Cada linha diz: o que o rival faz, quem é ele, a proporção
dele contra a nossa, e quantas vezes.

**Obrigatório na tela:** `rivais_fora` — quem foi tirado da comparação e
**por quê**. A Vitae Center é "1ª de Contagem" e é um centro médico; se ela
não aparecer explicada, alguém vai perguntar por que sumiu. Cada exclusão
traz o motivo escrito, e ele diz se cortou pela categoria ou pelo nome.

E o rodapé fixo: *"não é o que ele fatura nem o que ele gasta; é o que o
paciente dele escolheu escrever"*.

## B · A escada dos achados mudou de forma

`achados.json` agora carrega, por achado:

- `como_se_mede` — a frase que explica o método. **Desenhe visível**, não em
  tooltip: é ela que sustenta o número numa reunião.
- `excecoes[]` — as praças que contrariam, nomeadas. **Nunca esconda.** Um
  padrão sem exceção soa a curadoria; com a exceção nomeada, aguenta pergunta.
- `sem_amostra[]` — praças que não votaram, e por isso o denominador é menor.
- `estado: "nao_testavel"` + `por_que_nao` — seis achados são leitura humana
  e estão declarados. Desenhe-os apagados, com o motivo, no fim da escada.

Os degraus agora são: `constante` · `vale_para_a_rede` · `se_repete` ·
`candidata` · `derrubada` · `nao_testavel`.

## C · O padrão da praça: `dados/portal/padrao.json`

Quinze etapas × treze praças, com `ok`, `estado` e o comando que preenche
cada buraco. Serve de tela de bastidor — quem duvida de uma praça abre e vê
o que foi feito nela. Não precisa ir para o menu principal; um link no rodapé
da ficha de praça basta.

## D · Números que mudaram e estão em tela

| | |
|---|---|
| cobertura | **13 praças ouvidas · 374 unidades** (era "4 de 340", escrito à mão) |
| planos de franqueado | **7** — só praça com unidade |
| reputação | **7 redes** de ortodontia e odontologia popular; implante fora, nomeado |
| praças com estudo completo | **7 de 7** da rede |

---

# ADENDO v3.2 — as ferramentas que nasceram depois, e um formato que mudou

O design segue aprovado. Cinco telas novas, um formato alterado, e o menu
agora tem TRÊS entradas no andar AGORA. Tudo já está em `dados/`.

## A · O andar AGORA agora tem três entradas, nesta ordem

```
O que mudou            → dados/portal/o_que_mudou.json
A caixa de respostas   → dados/portal/caixa_de_respostas.json
A fila de intervenção  → dados/portal/fila.json  (inalterada)
```

## B · Tela nova: "O que mudou" — `o_que_mudou.json`

A resposta à pergunta que abre a semana. Por praça:

- `dias_medidos` e `aviso` — quando o período é curto, o aviso vem escrito
  ("o delta ainda diz pouco…"). **Desenhe o aviso visível.** Ele morre
  sozinho quando o ciclo engorda; não o esconda para a tela parecer melhor.
- `nossas[]` — cada loja nossa com `antes → agora (delta)`. Use ▲ ▼ ·.
- `quem_mais_ganhou[]` — rivais em movimento. O caso-exemplo real: Dentel,
  Londrina, 5 → 22 em 3 dias. É a linha que vende a assinatura.
- `contador_caiu[]` — **destaque**: contador que cai é avaliação removida,
  evento raro e auditável.

Cada ficha de praça (`pracas/*.json`) também traz agora o bloco
`o_que_mudou` preenchido — a mesma estrutura, local.

## C · Tela nova: "A caixa de respostas" — `caixa_de_respostas.json`

Lista de trabalho, POR LOJA: `manchete`, e `unidades[]` com `abertas`,
`com_texto`, `ja_respondidas` e `itens[]` (nota, data, texto). Ordene como
vem. Desenhe `a_regra` visível: responder é higiene de reputação, não motor
de ritmo — a tela não pode prometer o que o dado desmentiu.

## D · Tela nova: "Os padrões da rede" — `padroes.json`

A tela mais importante do andar DECIDIR. Ordem de leitura:

1. `hipoteses_testadas[]` — quatro cartões com veredito `NAO SEPARA` e a
   `prova`. O valor da tela é o que CAIU; desenhe os vereditos grandes.
2. `conclusao` — `t`, `leitura`, `consequencia` e `controle` (Cuiabá, as
   três lojas). É a única conclusão, e é por eliminação — o texto diz isso.
3. `lojas[]` — a tabela por loja (meses_seguidos, selo, pct_5_estrelas…).
4. `o_que_isso_nao_ve` — fechado e legível, como sempre.

## E · Tela nova: "A rede inteira" — `rede_inteira.json`

As 374. `alertas[]` ordenados por gravidade, cada um com `por_que` e
`de_quem_e` (franqueadora | unidade) — **marque visualmente os de
franqueadora**: Patrocínio fechada no Google é o primeiro. Depois
`por_uf[]`, e `nao_confirmadas_lista[]` com o motivo de cada uma — as 48
que ficaram fora aparecem nomeadas.

## F · Tela nova: "A voz da cidade" — `voz_da_cidade.json`

1.380 comentários dos canais locais, por praça. É CONSULTAR: contexto de
briefing, não decisão.

## G · FORMATO MUDOU: o rival agora é POR LOJA — `rival.json`

`pracas[]` virou lista de LOJAS: cada item tem `local_id`, `unidade`, e ou
`vantagens_deles[]` ou `sem_comparacao_porque` (string). **Quando vier
`sem_comparacao_porque`, desenhe a linha apagada com o motivo** — quatro
lojas ficam fora por amostra pequena e isso aparece, não some. O rótulo é
`rotulo · unidade`; o casco nunca monta, recebe pronto. `padrao_da_rede`
segue igual, mas `pracas[]` de cada eixo agora nomeia a LOJA.

## H · A escada mudou os degraus — `achados.json`

Degraus agora: `constante` · `vale_para_a_rede` · `se_repete` · `candidata`
· `derrubada` · `nao_testavel`. Cada achado pode trazer `como_se_mede`
(desenhe visível), `excecoes[]` (nomeadas, nunca escondidas) e
`sem_amostra[]`.
