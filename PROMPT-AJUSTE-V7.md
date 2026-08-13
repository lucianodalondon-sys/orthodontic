# Ajuste V7 — o portal precisa caber em 373 clínicas, não em 45

Este é um **ajuste** sobre o portal que você já entregou. Nada de refazer:
quatro telas mudam, o resto fica como está.

O problema é um só, e aparece em quatro lugares: **o portal desenha listas
que crescem junto com a rede.** Hoje são 45 clínicas medidas e a tela já
fica comprida. A rede tem **373 unidades** e as praças vão de 23 para
centenas. Uma lista que tem uma linha por loja não sobrevive a isso.

A regra nova, e ela vale para tudo:

> **Nenhuma lista da tela pode ter uma linha por unidade da rede.** Ou ela
> tem teto e um "ver todas as N" com o total pronto, ou ela é uma grade de
> cards com filtro. O total sempre vem pronto do payload — o casco continua
> proibido de contar.

---

## 1 · CLÍNICAS deixa de ser lista lateral e vira grade

**Como está:** uma coluna vertical na lateral com as 45 lojas, uma embaixo
da outra, em ordem de nada. Quem procura a própria loja rola até achar.

**Como fica:** o item CLÍNICAS do menu abre **uma tela só**, com uma grade
de cards. Sem lista lateral. Sem submenu.

**A ordem já vem pronta no payload — não reordene.** É ordem de ALERTA: a
loja que pega fogo primeiro, não a que começa com A.

### O payload

`dados/portal/clinicas_indice.json`

| campo | o que é |
|---|---|
| `cards` | **a grade, já ordenada.** 374 cards, cada um com `ordem` |
| `cards_total` | quantos são |
| `grupos` | os quatro estados, com `quantas` e `frase` prontos |
| `por_faixa` | vermelha / amarela / verde, com `quantas` |
| `frase_da_grade` | `"373 unidades na lista oficial · 43 com alerta aberto"` |
| `ordem` | a explicação da ordenação, escrita — mostre num "como isto está ordenado" |
| `ufs` | a árvore UF → cidade → unidade **continua existindo** (ver 1.4) |

### 1.1 · Cada card

```
┌──────────────────────────────────────────┐
│ ● vermelha                    #1         │   faixa + ordem
│ SC · Joinville                           │   rotulo
│ OrthoDontic · América                    │   unidade  (nome próprio!)
│                                          │
│ O contador de avaliações parou           │   alerta
│ 4,3 · 377 avaliações                     │   nota · avaliacoes
│                                          │
│ → Religar a rotina de pedido…            │   acao
└──────────────────────────────────────────┘
```

Campos do card: `rotulo`, `unidade`, `estado`, `faixa`, `urgencia`,
`alerta`, `alerta_fato`, `acao`, `nota`, `avaliacoes`, `endereco`,
`arquivo`, `ordem`.

**`unidade` é o nome próprio da loja**, não a marca. As 373 se chamam
"OrthoDontic"; o que distingue é o bairro (`· América`, `· Lapa`,
`· Cristo Redentor`). Nunca corte esse pedaço.

### 1.2 · Os quatro estados de card

Vêm em `grupos`, na ordem certa, com a contagem pronta:

| `estado` | quantas | como desenha |
|---|---|---|
| `com_estudo` | 45 | card cheio, **clicável** → `arquivo` |
| `ficha_medida` | 285 | apagado, com nota e nº de avaliações, **não clicável** |
| `so_na_lista` | 21 | apagado, só nome e endereço |
| `em_implantacao` | 23 | apagado, com selo "ainda não abriu" |

O apagado é conteúdo, não decoração: ele é o tamanho do que falta medir.
**Não esconda os 329 sem estudo** — é olhando para eles que a diretoria vê
que o portal está pronto e o que falta é medição.

### 1.3 · Filtros (chips no topo, contagem pronta)

    [ todas 374 ]  [ ● vermelha 12 ]  [ ● amarela 20 ]  [ ● verde 12 ]
    [ com estudo 45 ]  [ ficha medida 285 ]  [ só na lista 21 ]  [ em implantação 23 ]

Mais o filtro por UF, tirado de `ufs` (23 estados). Todos os números saem
de `grupos[].quantas` e `por_faixa[].quantas`. **Nenhum `.length`.**

### 1.4 · A árvore continua, como segunda visão

Um alternador **grade ↔ por estado**. A visão "por estado" é a árvore
`ufs` que você já desenha hoje (UF → cidade → unidades), e ela responde
outra pergunta: onde a rede está no mapa. A grade responde: onde ela dói.

### 1.5 · O card que não é unidade

Um card traz `sem_linha_oficial: true` (SP · República). Ele tem estudo e
não tem linha na lista oficial da rede. Desenhe o selo com o texto de
`porque_sem_linha`, e mostre `porque_um_card_a_mais` no rodapé da grade.
São 374 cards para 373 unidades, e o portal explica o porquê em vez de
esconder.

---

## 2 · "Alertas que sumiram" encolhe para uma linha

**Como está:** um bloco grande com oito linhas quase idênticas —
"RS · Caxias do Sul · Unidade nova que ainda não engatou · resolvido",
"PR · Curitiba · Unidade nova que ainda não engatou · resolvido"…

**Por que encolhe:** porque estava errado. Os 22 "resolvidos" não foram
resolvidos. Nove abriram e sumiram na mesma data; sete de "posição"
sumiram porque o ranking mudou de tamanho — Joinville · Aventureiro
"saltou" da metade de baixo para 1º de 15 em um dia; seis sumiram porque
a varredura leu mais avaliações e o contador cresceu sozinho. **Mudança de
método publicada como vitória.**

A régua nova: alerta só é resolvido quando esteve ativo num dia anterior,
a base de comparação é a mesma, e o número que o abriu se moveu na direção
certa.

**Como fica** — uma faixa fina dentro da fila, não um bloco:

    Alertas fechados com prova    0        22 sumiram sem prova de resultado ▾

Aberto, mostra `porque_descartadas` (motivo + quantas) e o texto de
`o_que_conta_como_resolvido`. Quando houver resolução de verdade, cada uma
vira uma linha com `leitura` — "subiu de 7º para 3º entre as mesmas 15
clínicas medidas".

Payload: `fila.json` → `frase_resolvidas`, `resolvidas_total`,
`resolucoes_descartadas`, `porque_descartadas[]`,
`o_que_conta_como_resolvido`, `tarefas_resolvidas[]`.

---

## 3 · "Onde a rede perde, em toda parte" para de listar loja por loja

**Como está:** oito eixos, e embaixo de cada um as 45 lojas, uma por
linha, com o rótulo repetido ("RS · Caxias do Sul · OrthoDontic" três
vezes seguidas, porque as três lojas se chamam igual).

**Como fica:** um eixo por linha, com barra. As lojas só aparecem quando
se abre o eixo, e mesmo aí só as **seis piores**.

    Tem profissional que o paciente chama pelo nome
    ████████████████░░░░░░░  32 lojas de 45 medidas · até 11,5×
    decisão de: unidade                              ver as 32 lojas ▾

Aberto:

    MT · Cuiabá · Centro Norte      11,5×   Dra Caroline Amorim
    MG · Contagem                    8,7×   Orthopride Contagem
    SP · São Paulo · Lapa            8,6×   DRB Odonto
    …

Payload: `rival.json` → `padrao_da_rede[]` com `o_que_e`, `frase`
(pronta: "32 lojas de 45 medidas"), `pior_razao`, `piores[]` (máx. 6),
`piores_total`, `frase_ver_todas`, `de_quem_e_a_decisao`.

Os rótulos já vêm sem a marca repetida. Não recomponha.

---

## 4 · "Praças sem base de comparação" ganha nome e motivo

O bloco aparecia com esse título seco e cinco cidades embaixo, e quem lê
entende "deu erro". Não deu: elas foram medidas pela primeira vez nesta
rodada, e movimento precisa de duas medições.

Use `titulo_sem_delta` ("Ainda não dá para comparar") no lugar do título
atual, e mostre `porque_algumas_nao_aparecem` **junto**, não escondido num
tooltip.

Payload: `franqueadora.json` → bloco de mudanças do mercado.

---

## O que NÃO muda

- Os sete itens do menu. Nenhum item novo.
- A identidade: azul-noite, o ciano da marca, a fonte, a grade.
  (O acabamento muda — está na Parte 2 —, a identidade não.)
- Todas as outras telas.
- A regra de sempre: **o casco não calcula.** Todo número, rótulo, plural e
  frase saem prontos do payload. A única contagem permitida na tela
  continua sendo o "mostrando as 30 primeiras de N que casam" da busca.

---

# Parte 2 — o cabeçalho, e a linguagem da apresentação

Esta parte veio de duas coisas: os cabeçalhos do portal estão pobres, e a
apresentação que o Claude Design fez para a diretoria (`Orthodontic
Intelligence`, 22 slides) está muito melhor. **O portal precisa falar a
mesma língua daquele deck.** Não é trocar a paleta: é adotar a arquitetura
de cabeçalho, a hierarquia de tipo e o hábito de explicar.

## 5 · O problema, dito sem rodeio

Hoje uma ferramenta abre assim:

    A REDE INTEIRA
    Alertas nas fichas do Google
    A ficha pública de cada unidade da rede, pela API do Google. Uma chamada por unidade.
    ┌ 374 ┐ ┌ 326 ┐ ┌ 4,8 ┐ ┌ 13 ┐
    Não é ritmo nem voz do paciente — para isso é a varredura completa, que hoje cobre 13 praças…

Quatro problemas em cinco linhas:

1. **"Alertas nas fichas do Google" é rótulo de sistema, não frase.** Não
   diz o que a ferramenta faz nem por que importa.
2. **"pela API do Google. Uma chamada por unidade"** é conversa de quem
   construiu, não de quem usa.
3. **O método está em cima**, em mono minúsculo, ocupando a largura
   inteira — a primeira coisa que a pessoa lê é metodologia.
4. **Nenhuma linha diz para quem aquilo serve** nem o que fazer depois.

O deck resolve os quatro em toda página. É isso que o portal precisa fazer.

## 6 · A anatomia do cabeçalho (igual à do deck)

```
  DA REDE INTEIRA                                   ORTHODONTIC INTELLIGENCE
  ──────────────────────────────────────────────────────────────────────────
  A vitrine da marca na rua:
  a ficha de cada unidade no Google
  Quando alguém procura uma unidade da OrthoDontic, o que ele encontra —
  e onde a marca está mal apresentada?

  PARA  franqueadora · consultor de campo
```

| faixa | conteúdo | tipo |
|---|---|---|
| sobrelinha esquerda | `cabecalho.sobrelinha` | mono 11px, +0.18em, ciano |
| sobrelinha direita | `ORTHODONTIC INTELLIGENCE` | mono 11px, +0.18em, 22% de opacidade |
| régua | hairline 1px a 10% | — |
| **título** | `cabecalho.titulo` | **44px / peso 900 / entrelinha 1.05 / −0.03em** |
| subtítulo | `cabecalho.pergunta` | 15px, cinza-claro, máx. 62ch |
| para quem | `cabecalho.para_quem` | chips mono 11px |

O título **quebra em duas linhas** quando é longo, como no deck — não
encolhe a fonte. Duas linhas de 44px valem mais que uma de 28px.

### 6.1 · O método desce para o rodapé

`cabecalho.metodo` e `cabecalho.o_que_nao_e` saem de cima e vão para o
**pé da tela**, depois do conteúdo, separados por uma hairline:

```
  ──────────────────────────────────────────────────────────────────────────
  COMO ISTO É MEDIDO   uma chamada por unidade à ficha pública do Google,
                       para todas as unidades da lista oficial.
  O QUE ISTO NÃO É     não é ritmo nem voz do paciente — aqui é retrato:
                       como a unidade aparece agora para quem procura.
```

Continua sempre visível. Não vira tooltip, não vira modal, não vira "?".
Esconder como se mede é o que faz o número virar palpite — mas ninguém
precisa ler método para entender manchete.

### 6.2 · O "como ler", quando existe

`cabecalho.como_ler` vira uma faixa discreta **entre o cabeçalho e o
conteúdo**, com barra ciano à esquerda — igual aos blocos de conclusão do
deck. É a instrução de uso, e é o que impede a leitura errada.

### 6.3 · O payload

Tudo isto já está pronto em **todos** os arquivos de tela:

```json
"cabecalho": {
  "sobrelinha": "DA REDE INTEIRA",
  "titulo": "A vitrine da marca na rua: a ficha de cada unidade no Google",
  "pergunta": "Quando alguém procura uma unidade da OrthoDontic, …",
  "para_quem": ["franqueadora", "consultor de campo"],
  "como_ler": "A ficha do Google é a fachada digital: …",
  "o_que_nao_e": "Não é ritmo nem voz do paciente — …",
  "metodo": "uma chamada por unidade à ficha pública do Google, …"
}
```

E há um índice central, **`dados/portal/cabecalhos.json`**, com as 23
ferramentas. Use-o na página da clínica, onde dez ferramentas convivem na
mesma tela: cada bloco leva o cabeçalho da ferramenta de onde ele veio, em
versão reduzida (sobrelinha + título + pergunta em uma linha).

**Nunca escreva título na mão.** Se um título parece errado, ele se
conserta em `scripts/cabecalhos.py`, não na tela.

## 7 · O que mais o deck faz melhor, e o portal deve copiar

### 7.1 · Números grandes como âncora, com legenda embaixo

O deck usa `374 / unidades`, `~291 mil / habitantes`, `19 / anúncios
ativos`. Número em mono, 34–56px, **legenda em 13px cinza embaixo, nunca
ao lado**. O portal já faz isso nas tiras — falta usar a **cor
semântica**.

### 7.2 · A cor significa alguma coisa

O deck tem quatro acentos e cada um quer dizer uma coisa. O portal está
todo azul, e por isso tudo parece ter o mesmo peso.

| cor | quando |
|---|---|
| **ciano** | medido, neutro, o padrão |
| **verde-água** | resultado bom, oportunidade, ação recomendada |
| **amarelo** | atenção, hipótese, "ainda não dá para afirmar" |
| **vermelho** | risco aberto, faixa vermelha, alerta ativo |

Isto casa com o carimbo de confiança que já vem no payload: **fato** →
ciano sólido; **inferência** → amarelo; **recomendação** → verde-água,
sempre em cartão de ação, nunca com cara de medição.

### 7.3 · Toda tela termina com uma conclusão

O deck fecha cada página com uma linha no rodapé: cinza → seta → **negrito
branco**.

    Hoje essas respostas estão espalhadas pela internet.  →  O portal organiza e interpreta.

O portal termina no último gráfico e deixa a pessoa sozinha com o número.
Toda ferramenta ganha essa linha final, tirada do payload: `manchete`,
`conclusao` ou `frase_da_grade`, conforme a tela.

### 7.4 · Cartão com fundo em degradê, não caixa com borda

No deck os cartões têm degradê sutil no azul e borda quase invisível; a
separação vem do **fundo**, não do contorno. O portal usa borda em tudo, e
é isso que dá ar de painel administrativo antigo. Um degrau de fundo, raio
14px, borda só no cartão selecionado ou crítico.

### 7.5 · Mono para metadado, sans para conteúdo

O deck é rigoroso: rótulo (`ANÚNCIOS ATIVOS`, `PRAZO`, `COMO SABEREMOS`) é
sempre mono maiúsculo espaçado; o conteúdo é sempre sans. O portal mistura
os dois e usa mono em texto corrido — foi assim que a linha de método
virou aquele borrão cinza embaixo do título.

### 7.6 · Antes → depois, quando houver os dois

Duas colunas, `ANTES` cinza e `DEPOIS` ciano, como nos slides 12 e 14. O
livro de ações (`acoes.json`) tem exatamente essa forma: métrica antes,
ação, métrica depois, veredito. Hoje ele desenha como lista.

## 8 · Um aviso sobre o deck

A apresentação diz **374 unidades**. A lista oficial da rede, lida no dia,
tem **373** — e o portal mostra 373 porque conta o que está no arquivo. Os
dois números não brigam: um é slide de agosto, o outro é a leitura de
hoje. Só não copie o 374 para dentro do portal: **na tela, número vem
sempre do payload.**
