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
- O visual, a paleta, a tipografia, o estilo dos cards.
- Todas as outras telas.
- A regra de sempre: **o casco não calcula.** Todo número, rótulo, plural e
  frase saem prontos do payload. A única contagem permitida na tela
  continua sendo o "mostrando as 30 primeiras de N que casam" da busca.
