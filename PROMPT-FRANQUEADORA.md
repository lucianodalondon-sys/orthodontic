# Prompt para o Claude Design — a SALA DE COMANDO da franqueadora

> Cole daqui para baixo. É só esta tela. Nenhuma outra.
>
> **Anexe junto os dois JSON:** `franqueadora.json` e `manifest.json`.
> Eles vão em `dados/portal/` dentro do projeto.

---

Construa **uma tela**: a sala de comando da franqueadora OrthoDontic — rede de
ortodontia com **374 unidades em 304 cidades do Brasil**.

É a tela do login inicial de quem trabalha na franqueadora. **É de onde a rede
inteira se enxerga, e de onde se escolhe a ferramenta.**

**Não é um relatório.** Relatório se lê uma vez e arquiva. Isto é um painel que
alguém abre toda segunda-feira.

---

## 0 · O QUE NÃO PODE FALTAR, E JÁ FALTOU

Uma versão anterior perdeu as três coisas que fazem esta tela existir. Se o que
você entregar não tiver as três, está errado:

1. **O MAPA.** A rede é geográfica — 374 unidades, 27 estados, 4 estados
   vazios. Sem o mapa, o diretor não vê a rede dele, vê uma planilha.
2. **A SALA DE COMANDO.** Uma tela de onde se comanda, não de onde se lê. O
   estado da rede no topo, as ferramentas ao lado, e cada uma a um clique.
3. **A CARA DE INTELIGÊNCIA.** Isto custa quase um milhão por ano. Precisa
   parecer sistema de inteligência de mercado, não apresentação de agência.

E uma quarta, que é a estrutural:

4. **AS FERRAMENTAS FICAM NA BARRA ESQUERDA, E SÃO TREZE.** O Radar de
   Oportunidade é **uma** delas. Uma versão anterior tratou o radar como se
   fosse o produto — não é.

---

## 1 · A MARCA — use a skill `orthodontic-design`, não invente

**Você já tem a skill `orthodontic-design`.** Carregue ela antes de escrever a
primeira linha. É a marca real, reconstruída do Manual de Marca oficial —
**ela manda.** Não invente paleta, não escolha outra fonte, não redesenhe o
logo.

Leia o `readme.md` da skill primeiro; ele traz o guia completo da marca. Se por
algum motivo a skill não estiver disponível, peça o zip
`OrthoDontic Design System` antes de começar — **não improvise a marca.**

| | |
|---|---|
| **Ciano `#00B9FF`** | a assinatura — CTA, links, o disco do símbolo, destaque |
| **Navy `#001E78`** | a âncora — títulos, superfícies escuras, fim do gradiente |
| **Gotham** | a tipográfica da marca: Black 900 para display em CAIXA ALTA e tracking apertado; Book/Light para texto; Bold 700 em CAIXA ALTA com tracking largo para rótulos |
| **Fundo** | `--od-mist #F3F7FC` na página, branco no cartão |
| **Sombra** | **sempre com tinta navy**, nunca cinza neutro |
| **Cantos** | pill (999px) em botão, 16px em cartão, 22px na bolha de vidro. **Canto reto é fora da marca.** |
| **Anéis concêntricos** | o motivo da marca — anéis brancos, sólidos e em contorno, sangrando de um campo ciano. É a assinatura visual, use no cabeçalho |
| **Ícones** | Lucide, traço médio, ponta arredondada |

Ligue o `styles.css` da skill e herde os tokens. Use `assets/logos/` como
está — os arquivos foram extraídos do PDF do manual, nunca redesenhados.

**Uma decisão que você precisa tomar com cuidado:** a marca é clara, alegre e
azul; uma sala de comando pede densidade e foco. **Não escureça tudo** — isso
mata a marca. O caminho é **navy profundo no cabeçalho e na barra esquerda**
(que é onde a marca fica forte e o motivo dos anéis aparece), e a **área de
trabalho clara** sobre `--od-mist`, densa e organizada. Ciano só onde importa:
o que exige ação e o que está selecionado.

### A voz da tela

A marca fala com o paciente em "você", calorosa. **Esta tela não fala com o
paciente** — fala com um diretor. O registro aqui é o do manual: direto,
instrucional, sem adjetivo de venda.

Mas a regra de linguagem do projeto vale inteira: **nada de jargão**.

| Não escreva | Escreva |
|---|---|
| velocity, baseline, share of voice | ritmo, ponto de partida, fatia da categoria |
| KPI, benchmark, churn | número, comparação, perda |
| dashboard, insights, overview | painel, achados, panorama |

---

## 2 · O DADO — a tela não calcula nada

Tudo vem de `dados/portal/franqueadora.json`, por `fetch` de caminho relativo.
**Nenhum dado dentro do HTML.** Se um número aparece na tela, ele veio pronto.
A tela pode ordenar e filtrar por campo existente, e formatar data. Só.

```
fetch('./dados/portal/manifest.json')       ← o índice, sempre primeiro
fetch('./dados/portal/franqueadora.json')   ← esta tela inteira
```

### O que vem em `franqueadora.json`

```json
{
  "rede": {
    "unidades": 374, "abertas": 348, "em_implantacao": 26,
    "cidades": 304, "ufs_com_unidade": 23,
    "ufs_sem_unidade": ["AC","AP","MA","RN"],
    "medido_em": "2026-08-09",
    "fonte": "orthodonticbrasil.com.br/encontre-uma-unidade"
  },
  "cobertura": { "pracas_medidas": 7, "total": 340, "aviso": "…" },
  "mapa": [ { "uf":"BA", "unidades":21, "abertas":20, "em_implantacao":1,
              "cidades":19, "pracas_medidas":1 }, … 27 estados … ],
  "ferramentas": [ { "chave","nome","o_que_responde","tela",
                     "disponivel","resumo","indisponivel_porque" } ],
  "reputacao_das_redes": [ { "marca","reclamacoes","selo","nota","nossa" } ],
  "fichas_da_rede": { "conferidas":10, "por_categoria":{…}, "sem_site":0 },
  "presenca_na_busca": { "dentista":{"dentro":13,"fora":99}, … }
}
```

**Ferramenta com `disponivel: false` aparece apagada, com o motivo escrito.**
Não some da barra. Esconder o que ainda não tem dado é o que faz a diretoria
achar que o sistema mede tudo.

---

## 3 · A ESTRUTURA DA TELA

Três zonas, e elas não se misturam.

```
┌──────────────┬───────────────────────────────────────────────────┐
│              │  CABEÇALHO navy + anéis concêntricos              │
│  BARRA       │  logo · rede em números · busca (/) · data        │
│  ESQUERDA    ├───────────────────────────────────────────────────┤
│  navy        │                                                   │
│              │   O MAPA — 27 estados, densidade por unidade      │
│  13          │   e os 4 vazios em destaque                       │
│  FERRAMENTAS │                                                   │
│  agrupadas   ├───────────────────────────────────────────────────┤
│              │   O QUE MUDOU — o que exige olhar hoje            │
│              ├───────────────────────────────────────────────────┤
│  cobertura   │   AS FERRAMENTAS — cartão por cartão, com o        │
│  no rodapé   │   número de cada uma                              │
└──────────────┴───────────────────────────────────────────────────┘
```

### 3.1 · A barra esquerda — as treze ferramentas

Navy profundo, fixa, com o logo em cima. Cada item: ícone Lucide + nome +
número pequeno à direita. O selecionado ganha faixa ciano à esquerda e fundo
levemente mais claro.

**Agrupadas em quatro blocos com rótulo em caixa alta e tracking largo** — a
barra tem treze itens e sem grupo vira lista:

**PANORAMA**
- Mapa da rede — *onde a rede está, estado por estado*
- As praças medidas — *a ficha completa de cada praça*

**CRESCER**
- **Radar de Oportunidade** — *onde vale abrir a próxima unidade*
- Território vazio — *que canal falta em cada praça, e ninguém ocupou*

**A REDE HOJE**
- Quem sustenta, quem parou — *quais unidades operam e quais só fizeram campanha*
- Presença na busca — *a rede aparece quando a cidade procura dentista?*
- Auditoria de ficha do Google — *o cadastro das unidades está certo?*
- Reputação: rede contra rede — *como a marca se compara com as concorrentes*
- Calendário da rede — *quando a procura sobe em cada região*

**OPERAÇÃO**
- Carteira do consultor — *quem visitar primeiro, e por quê*
- O plano de cada franqueado — *o que cada unidade faz nesta semana*
- A escada dos achados — *o que já vale para a rede e o que caiu*
- Biblioteca de evidências — *a citação por trás de cada afirmação*

No rodapé da barra, sempre visível: **`7 praças medidas de 340 unidades`**.
Discreto, mas nunca escondido — é a ressalva que qualifica a tela inteira.

### 3.2 · O cabeçalho — navy com os anéis

Faixa navy com o **motivo dos anéis concêntricos** sangrando à direita, logo
horizontal à esquerda, e a rede em quatro números grandes, em Gotham Black:

> **374** unidades · **348** abertas · **26** em implantação · **304** cidades

Ao lado, menor: `medido em 09/08/2026 · fonte: site da rede`.

Busca global abre com `/` e encontra praça, cidade, unidade e ferramenta.

### 3.3 · O MAPA — o coração da tela

Não é enfeite. É a primeira coisa que o diretor olha.

**Não temos coordenadas de unidade** — o dado é por estado. Então **não faça
mapa de pino**: faça o **mapa do Brasil por estado**, colorido pela densidade
de unidades, do `--od-sky` (poucas) ao `--od-navy` (muitas).

Desenhe os 27 estados em SVG inline, com as siglas. Não use biblioteca de
mapa nem imagem externa — a página tem de abrir em rede fechada.

**Os quatro estados sem nenhuma unidade — AC, AP, MA, RN — não podem ser só
"os mais claros".** Marque-os: contorno tracejado em ciano e o rótulo
`SEM UNIDADE`. **É o achado mais forte da tela**, e é a ponte natural para o
Radar de Oportunidade — três das seis praças que o radar recomenda estão
exatamente nesses estados.

Passar o mouse em um estado mostra: unidades, abertas, em implantação, cidades
e quantas praças ali já foram medidas. Clicar filtra a lista de praças.

Ao lado do mapa, uma coluna estreita com o ranking dos estados: SP 78, PR 57,
RS 52, SC 50, MG 37… — barra horizontal fina, número tabular.

### 3.4 · O QUE MUDOU — a faixa que exige olhar

Entre o mapa e as ferramentas, uma faixa horizontal com **três a cinco cartões
pequenos**, cada um com um número grande e uma frase curta. É o que muda
semana a semana:

> **5 unidades pararam** nos últimos 60 dias
> **99 ausências** contra 13 aparições na busca por "dentista"
> **9 de 10 unidades** cadastradas como "Clínica odontológica", não "Dentista"
> **4 estados** sem nenhuma unidade

Cada cartão leva para a ferramenta que explica. **Agrupe por causa, nunca por
unidade** — "5 unidades pararam" é uma linha, não cinco.

### 3.5 · As ferramentas em cartão

Abaixo, as treze em grade de cartões (branco, 16px, sombra navy). Cada um:
ícone, nome, a pergunta que ele responde em uma linha, e **o resumo com o
número que já vem pronto no JSON**.

Exemplos do que o JSON entrega, verbatim:

> **Radar de Oportunidade** — *onde vale abrir a próxima unidade*
> `6 praças livres estudadas · 2 descartadas por já ter unidade`

> **Quem sustenta, quem parou** — *quais unidades operam e quais só fizeram campanha*
> `3 de 10 sustentam · 5 pararam · 2 em campanha`

> **Reputação: rede contra rede** — *como a marca se compara com as concorrentes*
> `9 redes medidas no Reclame Aqui`

Duas ferramentas merecem um cartão maior, porque o dado delas é visual:

- **Reputação** — barra comparando as 9 redes por volume de reclamação, com a
  OrthoDontic destacada em ciano e o selo de cada uma. É a peça que a
  franqueadora usa **para fora**, contra a OdontoCompany.
- **Presença na busca** — três barras: `aparelho 6/6` cheia, `ortodontia 14/16`,
  `dentista 13/112` quase vazia. **O vazio é a mensagem.**

---

## 4 · O QUE ESTA TELA NÃO É

- **Não é a tela do franqueado.** O franqueado tem a dele, com o plano de ação.
  Aqui é quem comanda a rede.
- **Não é o Radar de Oportunidade.** O radar é uma das treze.
- **Não tem dado dentro.** Tudo por `fetch`.
- **Não calcula.** Se precisar de um número que não está no JSON, ele não
  aparece.

---

## 5 · AGUENTAR A REDE INTEIRA

Hoje 7 praças estão medidas; a rede tem 374 unidades em 304 cidades. A tela
precisa funcionar com as duas escalas.

- Nada de lista fixa no código — tudo vem do manifesto e do JSON.
- Busca global com `/`.
- O mapa não muda de tamanho com o número de praças.
- Carregue só o que a tela pedida precisa.

---

## 6 · COMO SEI QUE FICOU PRONTO

- [ ] tem **mapa do Brasil por estado**, em SVG inline, com os 4 estados vazios marcados
- [ ] tem **barra esquerda navy com as 13 ferramentas**, em 4 grupos
- [ ] o Radar de Oportunidade é **um item da barra**, não a tela
- [ ] usa **Gotham, ciano `#00B9FF` e navy `#001E78`** da skill `orthodontic-design`
- [ ] o **motivo dos anéis concêntricos** aparece no cabeçalho
- [ ] sombra com tinta navy, canto arredondado, botão pill
- [ ] `7 praças medidas de 340` visível sem precisar procurar
- [ ] **zero dado dentro do HTML** — tudo por `fetch` relativo
- [ ] buscar `{{`, `velocity` e `baseline` no arquivo dá **zero**
- [ ] ferramenta sem dado aparece **apagada com o motivo**, não some
- [ ] tema claro e escuro, os dois legíveis, cor definida em token no `:root`
- [ ] abre sem CDN — rede fechada
- [ ] busca abre com `/`

---

## 7 · OS ARQUIVOS

Vão anexados a este briefing, e no projeto ficam assim:

```
index.html
assets/…                          (css e js, sem CDN)
dados/portal/manifest.json        ← o índice, primeiro fetch
dados/portal/franqueadora.json    ← esta tela inteira
```

A estrutura de pasta importa: o casco busca por **caminho relativo**, então
`./dados/portal/…` precisa existir a partir do `index.html`.

Use os arquivos reais. Não invente exemplo — exemplo sempre sai mais
bem-comportado que o dado.
