# Ajuste V7 — o portal precisa caber em 373 clínicas, não em 45

> ## Como devolver o portal — vale para todas as rodadas
>
> No zip de volta vai **só o casco**: `index.html`, `assets/` e nada mais.
>
> **Não inclua a pasta `uploads/`.** Ela é o histórico de arquivos que
> subiram para o projeto — na última entrega eram 73 MB, com imagens
> antigas e até outro projeto dentro, num portal que tem 650 KB. O zip
> passou de 40 MB e não coube no chat.
>
> **Não devolva `dados/portal/`.** O payload sai do nosso build e vai
> sempre no zip de ida; devolver a cópia só cria uma versão para
> divergir da outra.
>
> O que precisamos de volta é exatamente isto:
>
>     portal-casco/
>       index.html
>       assets/  (portal.js, portal.css, fontes, logos)
>
> Foi assim que veio o portal 6, e funcionou: 684 KB.


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

---

# Parte 3 — o portal deixa de ter 23 ferramentas e passa a ter 6 capacidades

Esta parte é a maior das três, e ela **reduz** o portal em vez de aumentar.
Nenhuma tela é apagada: o que muda é o que ganha protagonismo e o que passa
a viver dentro de outra coisa.

## 9 · A regra que vale para o portal inteiro

> **Toda ferramenta termina respondendo cinco coisas:**
> **O que aconteceu? → Por que importa? → Quem precisa agir? → O que
> fazer? → Como encaminho isso?**
>
> Se não chega até a quinta, não é ferramenta: é dado, evidência ou
> detalhe de outra — e o lugar dela é dentro dessa outra, não no menu.

Isso agora existe no payload como um objeto só, e **todo cartão importante
tem exatamente estes campos**:

```json
{
  "insight_id": "agenda-3f2a91c4",
  "titulo": "Religar a rotina de pedido de avaliação",
  "onde": "SC · Joinville · América",
  "fato": "O contador de avaliações parou: 2 meses seguidos…",
  "por_que_importa": "esta unidade está na faixa vermelha…",
  "quem_age": "franqueado",
  "quem_age_rotulo": "Franqueado da unidade",
  "acao": "Religar a rotina de pedido de avaliação no fim do atendimento",
  "o_que_perguntar": "mudou alguma coisa na rotina…?",
  "nao_faca": "não contratar mídia para corrigir isto…",
  "revisar_em_dias": 14,
  "gravidade": "alta",
  "evidencias": [ {"o_que": "...", "texto": "..."} ],
  "carimbo": { … natureza, confiança, amostra, procedência … },
  "link": "clinicas/ortho_joi_america",
  "encaminhamento": { … }
}
```

### 9.1 · O cartão, desenhado

```
┌────────────────────────────────────────────────────────────┐
│ ● alta            SC · Joinville · América                 │
│ Religar a rotina de pedido de avaliação                    │
│                                                            │
│ FATO           O contador de avaliações parou: 2 meses…    │  ← ciano
│ POR QUE IMPORTA  está na faixa vermelha da fila…           │  ← cinza
│ AÇÃO           Religar a rotina no fim do atendimento      │  ← verde-água
│ NÃO FAÇA       não contratar mídia para corrigir isto      │  ← vermelho fraco
│ PARA           Franqueado da unidade         revisar em 14d│
│                                                            │
│ [ ver clínica ]                          [ ENCAMINHAR ▾ ]  │
└────────────────────────────────────────────────────────────┘
```

Os rótulos `FATO`, `POR QUE IMPORTA`, `AÇÃO`, `PARA` são mono maiúsculo
espaçado (a linguagem da apresentação). A cor não é decoração: **fato é
medido, ação é recomendação**, e o carimbo do payload diz qual é qual.

### 9.2 · O botão ENCAMINHAR

Existe em todo cartão de insight. Ao clicar, abre:

    Encaminhar para
    ○ Franqueadora · diretoria      ○ Marketing e agência
    ○ Consultor de campo            ○ Operações
    ○ Franqueado da unidade         ○ Expansão e comercial
    ─────────────────────────────────────────────────────
    [ copiar ]   [ WhatsApp ]   [ e-mail ]   [ copiar link ]

**O texto já vem pronto no payload.** O destinatário sugerido vem em
`encaminhamento.recomendado`, pré-selecionado, e a mensagem dele está
inteira em `encaminhamento.texto_pronto` — copie e pronto.

Se a pessoa trocar de destinatário, junte duas metades que também já vêm
escritas: `para[].abertura` do escolhido + linha em branco +
`encaminhamento.corpo`. É concatenação de texto autorado, não conta na
tela — está declarado assim de propósito, porque guardar a mensagem
inteira seis vezes fazia 62% do payload da home ser cópia da mesma frase.

Não gere texto na tela e não chame API nenhuma.

O mesmo insight muda de abertura conforme o destinatário: *"Padrão
observado na rede:"* para a diretoria, *"Para a próxima visita:"* para o
consultor, *"Ponto de atenção na presença pública da sua unidade:"* para o
franqueado. O corpo é o mesmo fato, a mesma evidência e a mesma ação.

**O que ele NÃO é:** o portal não guarda para quem foi mandado, quem leu
nem quem executou. Encaminhar é copiar um texto. Não desenhe estado de
"enviado", "lido" ou "concluído" — isso seria inventar dado interno, que é
justamente o que este produto não tem e não vai ter.

---

## 10 · As seis capacidades

O menu continua com sete itens. O que muda é o que cada um é.

| # | capacidade | payload | onde vive |
|---|---|---|---|
| 1 | **Inteligência da rede** (a home) | `inteligencia_da_rede.json` | PAINEL |
| 2 | **Agenda do consultor** | `agenda.json` | dentro do PAINEL |
| 3 | **O que a rede ensina** | `rede_aprende.json` | seção própria |
| 4 | **Gêmeos e anomalias** | `gemeos.json` · `anomalias.json` | CLÍNICAS |
| 5 | **Playbook competitivo** | `playbook.json` | seção própria |
| 6 | **Radar de expansão** | `radar.json` · `funil_nacional.json` | RADAR |

### 10.1 · A home vira INTELIGÊNCIA DA REDE

O título **PAINEL DE CONTROLE** sai. Entra:

    INTELIGÊNCIA DA REDE
    O que a OrthoDontic precisa saber esta semana

E abaixo, **cinco blocos e no máximo doze cartões** — o payload já vem
cortado nesse teto:

    3  O QUE A REDE APRENDEU        o que sabemos hoje que não sabíamos antes?
    5  ONDE INTERVIR ESTA SEMANA    qual unidade não pode esperar?
    1  O QUE O CONCORRENTE MEXEU    o que mudou na rua desde a última medição?
    3  O QUE DÁ PARA TESTAR         onde há espaço que ninguém está ocupando?
    2  ONDE CRESCER                 que cidade merece estudo antes das outras?

`blocos[].quantos` e `blocos[].pergunta` vêm prontos. Bloco vazio **não
some**: ele mostra `vazio_porque`.

**Nenhum cartão da home repete uma ferramenta.** Cada um é um cruzamento —
por isso a home e a página da clínica deixam de parecer a mesma coisa.

### 10.2 · Agenda do consultor

`agenda.json` → `esta_semana` (máx. 6), com `frase_ver_todas` pronta.

Cada linha tem: `o_que_vimos`, `o_que_conversar`, `leve[]` (as evidências
medidas para levar na visita), `nao_faca`, `revisar_em_dias`, e o
`insight` completo com encaminhamento. Desenhe na ordem em que a conversa
acontece — é uma pauta, não um ranking.

### 10.3 · O que a rede ensina

`rede_aprende.json` → `niveis[]` e `descobertas[]`. Quatro faixas, nesta
ordem, com a cor semântica:

    🟢 CONFIRMADO NA REDE        (6)   ciano/verde
    🟡 PADRÃO GANHANDO FORÇA     (2)   amarelo
    ⚪ HIPÓTESE EM TESTE         (7)   cinza
    🔴 DERRUBADO PELO DADO       (2)   vermelho

O nível **derrubado** é o que dá crédito aos outros três — desenhe-o com o
mesmo peso, não escondido no fim. Cada descoberta traz `placar` ("23/23"),
`porque_neste_nivel`, `evidencias[]`, e as confirmadas trazem
`o_que_significa` + `decisao_sugerida` + `carimbo_da_decisao`.

**A decisão é recomendação, o placar é fato.** Nunca desenhe os dois com a
mesma cor.

### 10.4 · Gêmeos e anomalias, dentro de CLÍNICAS

Na página da clínica, um bloco novo:

    MAIS PARECIDA COM ESTA
    SP · Sorocaba · Jardim Faculdade      distância 0,09 · 4 de 4 eixos
    cidades de 661 mil e 762 mil habitantes · 22 e 17 clínicas medidas

    O QUE AS SEPARA
    avaliações por mês         2,8 aqui contra 1,0 lá
    buscas perto da loja       4 de 5 aqui contra 2 de 5 lá
    avaliações já respondidas  29% aqui contra 85% lá

E na rede, `anomalias.json` com duas listas: `anomalias_negativas`
("deveria estar melhor") e `fora_da_curva` ("está fazendo algo que
precisamos entender"). A segunda é a mais valiosa — é boa prática
escondida na rede.

### 10.5 · Playbook competitivo

`playbook.json`. **Duas metades, e a segunda é obrigatória:**
`o_que_os_vencedores_fazem` e **`testamos_e_nao_explicou`**. Uma lista só
com o que funciona é palestra; uma que mostra o que foi testado e não
separou nada é medição.

Quando não há base (`base_suficiente: false`), a tela mostra o **funil**
`funil_ate_a_comparacao` e o texto de `porque_sem_comparacao` — 271
concorrentes medidos → 46 disputam aparelho → 16 com ritmo comparável →
12 com texto suficiente. Isso é conteúdo, não erro.

A parte que sempre tem base é `o_que_o_mercado_anuncia` (avaliação grátis
em 21 de 23 praças, alinhador em 20) e `posicoes_vagas`.

---

## 11 · O que sai do protagonismo

Nada é apagado. Estas telas passam a viver **dentro** de outra:

| tela | passa a viver em |
|---|---|
| busca perto da clínica | Encontrabilidade, na página da clínica |
| timeline | página da clínica |
| voz da cidade | página da praça |
| busca da cidade | praça + clínica |
| fichas das unidades | problemas → Alertas; ficha completa → clínica |
| canais e território | praça |
| rival | Playbook competitivo |
| anúncios | Playbook competitivo |
| achados | O que a rede ensina |
| funil nacional | primeira fase do Radar |
| sazonalidade | sai da navegação — foi medida e não sustentou uso |
| evidências | drawer "ver evidências" dentro de qualquer insight |

E o **ARQUIVO** fica discreto: método, fontes, séries e estados vazios
continuam existindo — é o que dá confiança —, mas o executivo não abre o
portal para isso. Dentro de cada ferramenta, `ⓘ ver método` e `ver
evidências` bastam.

---

## 12 · O que NÃO fazer nesta rodada

- **Não** crie item novo no menu. Continuam sendo sete.
- **Não** gere texto de encaminhamento na tela: ele vem pronto.
- **Não** desenhe estado de envio, leitura ou execução.
- **Não** invente orçamento, retorno financeiro ou prazo que não esteja no
  payload.
- **Não** conte nada na tela. Todo número, plural e frase vêm prontos.

---

# Parte 4 — a conferência do build (portal 6) e o que falta ligar

Rodei o portal que você entregou num navegador, contra o payload de hoje.
**Nenhum erro de console, nenhum 404, nada quebrado.** O que segue é
fiação que falta, não conserto de visual.

## O que já está certo — não mexa

- A home é **Inteligência da rede**: cinco blocos, 14 cartões, com a
  pergunta de cada bloco e o estado vazio explicado.
- O cabeçalho está em 14 telas cheias e em 15 blocos reduzidos, com
  `como ler` entre o cabeçalho e o conteúdo e o **método no rodapé**.
- CLÍNICAS é a grade ordenada por alerta, com os quatro estados e os
  filtros contados do payload.
- ENCAMINHAR está implementado exatamente como pedido: `abertura + corpo`,
  com `texto_pronto` de reserva. Não mude isso.
- **Zero `.length` impresso na tela e zero `.sort()`.** A única conta que
  sobrou é largura de barra e geometria de mapa, que é desenho, não número
  publicado. Está certo.

## 12 · O que falta ligar

### 12.1 · `pipeline_expansao.json` não está sendo lido

Payload novo. Ele funde o funil nacional e o radar numa tela só, que é o
que o time comercial usa:

```
  5.570  municípios brasileiros
     50  candidatas pela régua demográfica
         ↓ 5.520 caíram: cidade pequena demais para sustentar uma unidade
     13  estudadas a fundo
         · 5 vieram da régua, 8 por outro caminho
      6  com a praça livre
         ↓ 7 caíram: a rede já tem unidade lá
      6  recomendadas para avançar
```

Campos: `degraus[]` (com `quantos`, `cairam`, `porque_caem`), `cidades[]`
(com `por_que[]`, **`riscos[]`**, `proximo_passo`, `insight`),
`onde_cabem_mais[]`.

O bloco `vieram_da_regua` / `vieram_por_outro_caminho` **tem de aparecer**:
o funil não é fila única, e escrever "50 → 13" sugeriria subconjunto.

Os **riscos** também não são opcionais. Um candidato a franqueado que sabe
fazer conta desconfia de dossiê sem risco.

A rota `radar` passa a abrir esta tela; `funil` vira âncora dentro dela.

### 12.2 · A agenda do consultor merece rota própria

Hoje `#agenda` abre a tela da fila. O bloco dentro da home está perfeito —
mas a agenda é uma das seis capacidades e tem cabeçalho próprio no
payload (`cabecalhos.json → agenda`). Faça `#agenda` abrir `agenda.json`
em tela cheia: `esta_semana[]` com `frase_ver_todas`, e o mesmo
`linhaAgenda` que você já escreveu.

### 12.3 · Seis telas ainda sem cabeçalho

`cabecalhoTela()` cobre 14. Faltam, e todas já têm texto pronto em
`cabecalhos.json`:

    agenda · funil_nacional · sazonalidade · voz_da_cidade · pipeline_expansao

(`franqueadora` é a home antiga e pode ficar sem — a home agora é
`inteligencia_da_rede`.)

### 12.4 · A caixa de respostas mudou de forma

A tela ainda abre com **399** e a lista crua. O payload agora prioriza:

| campo | o que é |
|---|---|
| `manchete` | "20 unidades precisam responder agora — 399 abertas…" |
| `precisam_agora_total` | quantas estão em vermelho |
| `janela_que_pesa_dias` | 180 |
| `unidades[].frase` | "14 críticas sem resposta nos últimos 180 dias · 36 abertas no total" |
| `unidades[].criticas_recentes` | o número que ordena |
| `unidades[].gravidade` | alta · media · baixa |
| `unidades[].assuntos[]` | do que reclamam: `{assunto, quantas, frase}` |
| `unidades[].insight` | com ENCAMINHAR pronto |

Desenhe como fila de trabalho:

```
  🔴 MG · Contagem · OrthoDontic
     14 críticas sem resposta nos últimos 180 dias · 36 abertas no total
     agendamento (6) · atendimento clínico (3) · contato (2)
     [ ver as 36 ]                                  [ ENCAMINHAR ▾ ]
```

O 399 continua na tela, como acervo, embaixo — não como manchete. Ninguém
responde 399.

**Por que mudou:** a ordenação anterior era "há quantos dias a mais antiga
espera", e ela pôs na frente uma reclamação de **4.172 dias** e pintou as
40 unidades de vermelho. Não separava nada.

### 12.5 · Os alertas de ficha ganharam ação

`rede_inteira.json → alertas[]` agora traz `o_que_fazer`, `custo`,
`prazo_dias` e `insight`. Cada alerta vira cartão com ação e ENCAMINHAR,
não só diagnóstico. E quase todos são "sem custo de mídia" — isso merece
aparecer.

### 12.6 · `gravidade_rotulo`

Era defeito nosso: a tela escrevia `media`, sem acento, porque recebia a
chave de código. Agora todo insight traz `gravidade_rotulo` ("alta
prioridade", "média prioridade"). Use ele nos rótulos e nas tiras —
`gravidade` continua servindo para a cor.

---

# Parte 5 — o que a auditoria mudou no payload

Nove auditorias independentes percorreram o produto como franqueadora,
consultor, marketing, expansão e franqueado. Oito defeitos foram
confirmados contra o disco e consertados **do nosso lado**. Nada aqui pede
tela nova — mas cinco coisas mudaram de forma no payload, e a tela precisa
acompanhar.

## 13.1 · `gravidade_rotulo` nas tiras

As tiras da home ainda escrevem `alta`, `media`, `baixa` — a chave de
código, sem acento. Todo insight agora traz `gravidade_rotulo` ("alta
prioridade", "média prioridade"), e `resumo.por_gravidade[]` traz `rotulo`.
Use o rótulo no texto; `gravidade` continua servindo para a cor. Nos
cartões você já faz certo.

## 13.2 · A grade de clínicas ganhou a procedência do número

Os três cards de Cuiabá mostravam **nota 5 e 1.222 avaliações**, os três —
a varredura devolveu a mesma ficha para as três linhas oficiais. Agora cada
card traz:

    "nota": 4.9, "avaliacoes": 78,
    "numero_de": "medição desta loja",        // ou "ficha do Google"
    "sem_numero_porque": null                  // ou o motivo, escrito

Desenhe `numero_de` como nota de rodapé do card, discreta. E quando
`avaliacoes` for `null`, mostre `sem_numero_porque` no lugar do número —
47 cards estão nessa situação, e o motivo é conteúdo: *"mais de uma unidade
desta cidade tem o mesmo nome na lista oficial, e a ficha do Google não
distingue qual é qual"*.

## 13.3 · O confronto com o rival agora diz de quem é a decisão, e por quê

`rival.json → padrao_da_rede[]` ganhou `porque_esse_dono`:

    Tem profissional que o paciente chama pelo nome
    ████████████████░░░░░  32 de 45 lojas · até 11,5×
    DECISÃO DE FRANQUEADORA
    aparece em 32 de 45 lojas medidas (71%); o corte para virar
    decisão de rede é 60%

Três eixos passam a ser decisão de franqueadora; cinco continuam da
unidade. O corte publicado ao lado do veredito é obrigatório — antes o
limiar exigia perder em 44 de 45 lojas e nunca disparava.

## 13.4 · A home encolheu, e é isso que se quer

De 14 para 12 cartões, e **nenhum deles repete a agenda**. Os cinco que
eram os cinco primeiros itens da agenda viraram um só, de rede:

    O contador de avaliações parou — em toda a rede medida
    24 unidades medidas têm este como o problema que mais pesa, em 12 estados

No lugar liberado entraram as **anomalias** (`anomalias.json`), que são
cruzamento de verdade e não existiam na home: duas unidades que deveriam
estar melhor do que estão, e uma que está fazendo algo que ninguém foi
perguntar o quê.

**Zero cartões sem carimbo.** As duas cidades de expansão voltaram a levar
o carimbo e o `nao_faca` ("não apresentar isto como projeção de
faturamento") que se perdiam na cópia — e é justamente esse texto que
circula quando alguém encaminha.

## 13.5 · A conclusão dos padrões deixou de ser fato

`padroes.json → conclusao` agora tem `carimbo` (inferência, confiança
baixa) e **`o_que_nao_foi_testado[]`**. A tela precisa mostrar os dois: a
frase diz que quatro explicações caíram e que o que sobra é a rotina de
balcão, mas ponto comercial, verba local, rotatividade de ortodontista e
preço nunca foram testados — e nenhuma fonte pública os mede.

Se a rede vai virar isso em programa nacional, a tela tem de dizer que está
apostando numa inferência por eliminação. O card da home foi reescrito no
mesmo espírito.
