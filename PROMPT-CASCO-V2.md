# Prompt para o Claude Design — o casco do portal OrthoDontic

> Cole daqui para baixo. É o briefing inteiro.

---

Construa o **casco** de um portal de inteligência de mercado para uma rede de
franquias de ortodontia com 374 unidades no Brasil.

**Casco quer dizer: o portal não tem dado nenhum dentro dele.** Ele busca os
arquivos JSON, lê e desenha. Só isso. Esta é a regra que manda em todas as
outras, e ela existe porque a coleta roda toda semana e o portal não pode
precisar ser reescrito a cada rodada.

---

## 1 · A REGRA QUE MANDA EM TODAS

### O casco NUNCA calcula

Se um número aparece na tela, ele veio pronto de um arquivo JSON. O casco não
soma, não divide, não faz média, não classifica, não decide cor por faixa, não
monta frase.

**Por quê:** todo número deste projeto carrega procedência e ressalva. Um
percentual calculado na tela perde as duas, e uma tela que calcula diverge do
relatório impresso na semana seguinte. Já aconteceu: uma versão anterior
calculava "ritmo por mês" no navegador e mostrava `-4,0` para uma clínica cujo
contador de avaliações tinha **caído** — o dado correto era "o contador caiu 3,
avaliação removida", e essa frase já vinha pronta no JSON.

O que o casco PODE fazer: ordenar uma lista por um campo que já existe,
filtrar por um campo que já existe, e formatar data.

### Os dados vêm de fora, por fetch

```
fetch('./dados/portal/manifest.json')   ← sempre o primeiro
```

Todos os caminhos são **relativos à página**. Nada de URL absoluta, nada de
domínio escrito no código, nada de token. Os JSON viajam junto com o HTML no
mesmo deploy.

**Não embuta dados no HTML.** Nem em `<script id="dados">`, nem em variável, nem
como exemplo. Se precisar de algo para desenvolver, busque os arquivos de
verdade — eles estão no repositório em `dados/portal/`.

### Estado vazio é obrigatório, não opcional

Toda tela precisa funcionar quando o arquivo dela não existe ou vem vazio. A
mensagem é específica: *"esta praça ainda não tem plano de captação"*, não
"erro". Praça nova entra na base sem todos os coletores rodados, e isso é
normal, não falha.

---

## 2 · O CONTRATO DE DADOS

### O índice: `dados/portal/manifest.json`

É o primeiro fetch e é ele que diz o que existe. **Não presuma que uma tela
existe — pergunte ao manifesto.**

```json
{
  "gerado_em": "2026-08-09T02:29:11",
  "corte": "2026-08-08",
  "cobertura": { "ouvidas": 4, "total": 340 },
  "pracas": [
    { "praca_id": "contagem",
      "nome": "Contagem",
      "rotulo": "MG · Contagem",
      "uf": ["MG"],
      "cidades": ["MG · Contagem"],
      "tem": ["praca", "captacao", "plano"] }
  ],
  "arquivos": {
    "rede":         ["rede", "rede_cruzamento", "achados", "corretor", "evidencias", "radar"],
    "pracas":       ["contagem", "cuiaba", "feira", "londrina", "palmas", "prudente", "riomafra"],
    "captacao":     ["contagem", "…"],
    "planos":       ["contagem", "…"],
    "oportunidade": ["imperatriz", "juazeiro_do_norte", "macapa", "maraba", "parauapebas", "rio_branco"]
  },
  "telas": ["achados", "captacao/londrina", "…"]
}
```

O campo `tem` de cada praça diz quais telas ela já tem. O menu se monta a
partir dele — praça sem plano não mostra aba de plano vazia.

### Os arquivos, e o que cada um é

| Arquivo | É a tela de | Público |
|---|---|---|
| `rede.json` | o mapa das praças, uma linha por praça | franqueadora |
| `rede_cruzamento.json` | o que vale para a REDE e o que vale para uma cidade só | franqueadora |
| `achados.json` | a escada dos achados, com o que subiu e o que caiu | franqueadora |
| `radar.json` | **Radar de Oportunidade** — onde abrir unidade nova | expansão |
| `oportunidade/<cidade>.json` | o estudo completo de uma praça de oportunidade | expansão |
| `pracas/<praca>.json` | a ficha da praça: placar, ritmo, temas, sazonalidade | consultor + franqueado |
| `captacao/<praca>.json` | a leitura analítica de onde captar | agência / consultor |
| `planos/<praca>.json` | **o plano do franqueado** — a mesma coisa, para executar | **franqueado** |
| `corretor.json` | a visão do consultor de campo | consultor |
| `evidencias.json` | as citações e provas por trás dos achados | todos |

**Não invente campo.** Se um dado que você acha que a tela precisa não está no
JSON, a tela não mostra — e não calcula um substituto.

---

## 3 · AS TELAS

Quatro públicos, e eles não querem a mesma coisa. Não faça uma tela só com
abas: faça quatro entradas, e deixe claro em qual delas a pessoa está.

### 3.1 · REDE — a franqueadora

De `rede.json` + `rede_cruzamento.json` + `achados.json`.

O topo é a cobertura declarada: *"4 praças medidas de 340 unidades"*. **Ela vai
no topo, não no rodapé** — é uma amostra, e esconder isso é o que faria a
diretoria confiar demais.

Depois, a tabela das praças (`praca_linhas`), com o rótulo **já pronto** no
campo `rotulo`.

E a leitura de rede, de `rede_cruzamento.json`, que é o que a franqueadora
compra — os números já vêm somados:

```json
{ "pracas": 7, "unidades": 10, "clinicas": 144,
  "sustentam": 3, "campanha": 2, "paradas": 5,
  "placar": [ … uma linha por unidade, com posição na praça … ],
  "territorio_vazio": { … por tipo de canal … },
  "pesa_contra": [ … o contraexemplo, sempre … ] }
```

A manchete: **3 de 10 unidades sustentam; 5 pararam.** E `pesa_contra` vai
junto, na mesma tela — achado sem contraexemplo procurado não é achado.

`achados.json` traz a escada: 14 achados distribuídos em 5 estados (de SINAL
ISOLADO a VIROU REGRA, e ❌ CAIU). **Mostre os que caíram também** — é o que
prova que a escada é honesta.

### 3.2 · RADAR DE OPORTUNIDADE — expansão

De `radar.json` e `oportunidade/<cidade>.json`. É a única tela que aparece como
**receita** da franqueadora, não como custo.

Três blocos, nesta ordem:

**A rede hoje** (`rede_hoje`) — 374 unidades, 348 abertas, 26 **em implantação**,
304 cidades. E em destaque `ufs_sem_nenhuma_unidade`: **AC, AP, MA e RN não têm
uma única unidade.** É o número que abre a conversa.

**As oportunidades** (`oportunidades`, já em ordem) — um cartão por cidade, com
`rotulo` no formato `UF · Cidade`, população, os dois alvos etários, clínicas
fortes, líder local e habitantes por clínica forte.

Dentro do cartão, **a defesa** (`defesa`) — uma lista de parágrafos **já
escritos**, com marcação `**negrito**` de markdown. Renderize o negrito e
**não reescreva o texto**. É a defesa que o time leva para a reunião.

E **a gêmea** (`gemea`), que é o que fecha o cartão:

> *"AP · Macapá tem o perfil de TO · Palmas. Lá a unidade OrthoDontic tem 304
> avaliações, nota 5,0 e faz 14,0 avaliações por mês há 11 meses seguidos."*

Mostre `gemea.frase` em destaque, `gemea.unidades_de_la` (o que a unidade faz
lá) e **`gemea.onde_difere`, que não pode ser escondido** — é onde os eixos não
batem, e é a parte honesta do cartão. Mostre também `faixa_das_parecidas`: as
três praças parecidas entregam de 0,0 a 14,0 avaliações por mês, e a diferença
entre as pontas **não é a cidade, é a operação**.

**O terceiro bloco não pode ser escondido:** `ja_tem_unidade` e
`nao_conferidas`. São as cidades que saíram do radar, com o motivo escrito.
Santarém e Petrolina entraram como controle e saíram sozinhas — é isso que
mostra que a checagem funciona. Cidade em `nao_conferidas` aparece apagada, com
*"não deu para conferir contra a lista oficial"*, nunca como recomendação.

As `ressalvas` ficam **no topo da tela, não no rodapé**.

### 3.3 · PRAÇA — o consultor e o franqueado

De `pracas/<praca>.json`.

**Abre com o histograma de 12 meses**, não com o funil. O histograma é a leitura
que decide: mostra se a clínica opera ou fez campanha e parou.

Ao lado de **todo** número de ritmo vem o selo de constância:

| | |
|---|---|
| 🟢 **OPERAÇÃO** | 10 meses ou mais seguidos |
| 🟡 **CAMPANHA** | 3 a 9 meses |
| 🔴 **RAJADA** | um mês concentra 60% ou mais |
| ⚫ **PAROU** | sem movimento nos últimos 60 dias |

De 130 clínicas medidas, **só quatro sustentam**. É a informação mais rara que o
portal tem.

Quando o campo trouxer `~estimado`, mostre o til e um balão: *"medido pelo
intervalo da amostra; a próxima coleta confirma pelo contador do Google."*

### 3.4 · O PLANO DO FRANQUEADO — a tela que existe para AGIR

De `planos/<praca>.json`. **Esta é a tela mais importante do portal**, porque é
a única em que alguém faz alguma coisa depois de ler.

O público é um dentista com quarenta pacientes na agenda e quinze minutos entre
um e outro. Se ele não entender na primeira leitura, não faz.

**Um número no topo, e só um.** `placar`: `{ "aparece_em": 5, "de": 20, "pct": 25 }`

> A sua clínica aparece em **5 das 20 buscas** que testamos na sua cidade.

Desenhe isso como **20 quadrados, 5 preenchidos**. O vazio é a mensagem — não
precisa ler nada para entender. Repita o mesmo desenho, pequeno, dentro da
primeira tarefa, comparando as duas famílias de busca lado a lado (aparelho
`5 de 7` cheio, dentista `0 de 13` vazio).

Depois, **no máximo cinco tarefas** (`tarefas`, já em ordem de prioridade — do
grátis para o pago). Cada uma tem:

| Campo | Vira |
|---|---|
| `titulo` | o título da tarefa |
| `custo`, `tempo`, `quem` | três etiquetas em mono, e `R$ 0` ganha destaque |
| `o_que_esta_acontecendo` | lista de parágrafos; itens que começam com `·` são lista |
| `o_que_fazer` | passos numerados, em bloco destacado |
| `nao_faca` | um aviso em cor de alerta — **quando existe, é obrigatório** |
| `como_saber` | rodapé da tarefa: o que vai ser medido de novo em 30 dias |

A numeração das tarefas **carrega informação**: é ordem de prioridade e de
custo. Deixe o número visível e grande.

⚠ **Nunca escreva dica de "coloque palavra-chave no nome da clínica".** É contra
as diretrizes do Google e derruba o perfil. O JSON já traz esse aviso no campo
`nao_faca` — respeite-o.

No fim, `ressalvas` — o que a medição não enxerga. **Antes da assinatura, não
depois.**

### 3.5 · ONDE CAPTAR — a versão analítica

De `captacao/<praca>.json`. É a mesma medição do plano, sem tradução: para a
agência e o consultor. `por_familia`, `fora`, `sem_dono`, `bairros`,
`convenios`, `vocabulario_da_praca`, `servicos_citados`.

Um detalhe que não pode sumir: `anunciantes_descartados` — anunciantes que a
busca trouxe e que **não são da praça**. Mostrar que foram descartados é o que
faz confiar nos que ficaram.

---

## 4 · O QUE PRECISA AGUENTAR 340 UNIDADES

Hoje são 7 praças na base. O portal vai para **374 unidades em 304 cidades**.
Se a tela só funciona com sete, ela não serve.

- **Nada de lista fixa no código.** As praças vêm do manifesto, sempre.
- **Busca global**, com `/` para abrir. Acha praça, unidade, concorrente,
  cidade do radar e achado. Com 340 unidades, rolar não é navegação.
- **A tabela da rede precisa de filtro e ordenação** por UF, por selo de
  constância, por posição na praça.
- **O alerta agrupa por causa, não por unidade.** "Sete unidades pararam nos
  últimos 60 dias" é uma linha, não sete.
- **Carregue sob demanda.** O casco busca o manifesto e a tela pedida; não
  carrega as 340 fichas de uma vez.
- **Cache com o `gerado_em` do manifesto** como chave, para a rodada nova
  invalidar sozinha.

---

## 5 · A LÍNGUA DA TELA

### A UF vem ANTES do nome da cidade, sempre

**`MG · Contagem`**, nunca `Contagem/MG`. Vale em toda tela, no menu, na busca e
na exportação.

| Praça | Como aparece |
|---|---|
| Contagem | `MG · Contagem` |
| Riomafra | `SC · Mafra + PR · Rio Negro` |
| Cuiabá | `MT · Cuiabá + MT · Várzea Grande` |

**O casco não monta esse texto.** Ele vem pronto no campo `rotulo`. Se você
estiver concatenando cidade e UF em algum lugar, está errado.

Com a UF na frente, a cidade errada salta aos olhos antes de virar decisão, e
numa lista de 340 o olho agrupa por estado sem coluna extra.

### Palavra difícil não entra

O leitor é dentista ou diretor, não analista.

| Não escreva | Escreva |
|---|---|
| velocity, baseline, share of voice | ritmo, ponto de partida, fatia da categoria |
| porta, intenção, SEO local | busca, o seu perfil do Google, o seu site |
| KPI, benchmark, funil de aquisição | número, comparação, caminho do paciente |
| churn, lead, awareness | perda, interessado, quem conhece a marca |

Se um termo técnico for inevitável, ele aparece **uma vez, explicado**, e depois
some.

### Todo número carrega de onde veio

Ao lado de cada bloco, a procedência em texto pequeno: a fonte e a data. Sem
isso o número vira opinião.

---

## 6 · O QUE NÃO PODE ACONTECER

Lista de erros que já aconteceram em versões anteriores deste portal:

1. **Placeholder aparecendo como texto na tela.** Uma versão entregou 393
   `{{ }}` renderizados literalmente. Buscar `{{` no arquivo final tem de dar
   **zero**.
2. **Lista de praças escrita no código.** Deixou Cuiabá, Palmas e Contagem
   três semanas fora do portal, caladas.
3. **Dado embutido no HTML.** Na rodada seguinte o portal mostra o dado velho e
   ninguém percebe.
4. **Número calculado na tela.** Diverge do relatório e perde a ressalva.
5. **Rótulo de cidade montado no casco.** Sai `Contagem/MG` em metade das telas.
6. **Ressalva no rodapé.** Ressalva que muda a leitura vai antes do número, não
   depois.
7. **Esconder o que saiu.** As cidades que o radar descartou provam que o radar
   funciona. Some com elas e o produto vira propaganda.

---

## 7 · O VISUAL

**Não é relatório. É portal de inteligência** — e essa diferença é o que faz a
diretoria tratar como sistema e não como apresentação.

- Denso, mas respirável. Muita informação por tela, hierarquia clara.
- **Tipografia com três registros**, porque o conteúdo tem três: uma sem-serifa
  forte para instrução e títulos, uma serifada para o texto que se lê de
  verdade, e uma monoespaçada para todo número, etiqueta e medida.
- **Cor semântica separada da cor de marca.** Verde/amarelo/vermelho/cinza são
  dos selos de constância. O acento da marca é outra coisa e não disputa com
  eles.
- **Tema claro e escuro**, os dois pensados. Defina a paleta em tokens no
  `:root`; redefina os mesmos tokens em `@media (prefers-color-scheme: dark)` e
  em `[data-theme="dark"]`. Nenhuma cor pode existir só dentro de um bloco de
  tema.
- Tabela larga rola dentro do próprio container, nunca no corpo da página.
- `font-variant-numeric: tabular-nums` em toda coluna de número.
- Foco de teclado visível. `prefers-reduced-motion` respeitado.

Evite o visual que todo painel gerado por IA tem hoje: creme com serifada e
acento terracota, preto com um verde-limão, gradiente roxo-azul, card com
barrinha colorida na lateral, emoji como marcador de seção. Faça uma escolha
que combine com o assunto — odontologia, medição, campo.

---

## 8 · COMO ENTREGAR

Um projeto estático, sem build obrigatório, que roda abrindo o `index.html` com
os JSON ao lado:

```
index.html
assets/…                 (css e js, sem CDN)
dados/portal/            (os JSON, exatamente como estão no repositório)
```

Sem dependência de CDN — o portal precisa abrir numa rede fechada.

### Como sei que ficou pronto

- [ ] buscar `{{` no projeto dá **zero**
- [ ] buscar `velocity` e `baseline` dá **zero**
- [ ] **nenhum dado dentro do HTML ou do JS** — tudo vem de `fetch`
- [ ] a lista de praças sai do `manifest.json`, não do código
- [ ] toda cidade aparece como `UF · Cidade`, e o casco **não** monta esse texto
- [ ] apagar um JSON não quebra o portal — ele mostra "sem dado ainda"
- [ ] as ressalvas aparecem **antes** dos números que elas qualificam
- [ ] a tela do Radar mostra as cidades que **saíram**, com o motivo
- [ ] a tela do Plano tem **um** número no topo e no máximo cinco tarefas
- [ ] o `nao_faca` de cada tarefa aparece com destaque de alerta
- [ ] todo ritmo tem selo de constância do lado
- [ ] a busca abre com `/` e encontra praça, unidade, concorrente e cidade
- [ ] funciona com 340 unidades no manifesto, não só com 7
- [ ] tema claro e escuro, os dois legíveis

---

## 9 · OS DADOS DE VERDADE

Estão no repositório, em `dados/portal/`. **São 34 arquivos, 664 KB.** Use os
arquivos reais para desenvolver — não invente exemplo, porque o exemplo sempre
sai mais bem-comportado que o dado.

Comece por `dados/portal/manifest.json`, que indexa todo o resto.

---

## 10 · UMA NOTA SOBRE ONDE ISSO VAI FICAR HOSPEDADO

O repositório é **privado** e precisa continuar sendo: ele contém a análise de
concorrência do cliente, avaliação por avaliação.

Isso significa que o portal **não pode ser servido direto do GitHub Pages de um
repositório público**. Os JSON viajam junto com o deploy, e o deploy vai para um
lugar com controle de acesso — os 340 logins do projeto.

Para o desenvolvimento do casco isso não muda nada: os caminhos são relativos e
funcionam igual em qualquer hospedagem. Só não escreva domínio no código.
