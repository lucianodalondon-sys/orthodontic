# Piloto Orthodontic · Camada 1 — DADOS E COLETA
### 4 praças · Londrina (Souza Naves) · Presidente Prudente · Feira de Santana · Mafra/Mafra

> Esta é a primeira das três camadas. Aqui não há tela, não há IA e não há
> insight. Só a pergunta: **o que entra, com que chave, com que frequência, e
> como sabemos que é verdade.**

---

## 0 · A MUDANÇA QUE DEFINE TUDO

O pipeline de hoje foi feito para **estudo**: roda uma vez, produz um corpus,
gera um documento. O portal precisa de **série**.

A diferença cabe numa linha:

> **Hoje a coleta sobrescreve. A partir de agora ela só acrescenta.**

Toda coleta ganha um `snapshot_date` e nada é apagado. Isso sozinho destrava
metade das métricas que os estudos calcularam à mão — velocity de review,
sobrevivência de criativo, movimento de placar — porque elas passam a ser
subproduto do histórico, não trabalho de análise.

**Regra dura:** nenhum arquivo de coleta é reescrito. Se a coleta de agosto
contradiz a de julho, as duas ficam. A contradição é dado.

---

## 1 · AS CHAVES (é aqui que projetos assim morrem)

Antes de coletar qualquer coisa, é preciso saber **o que é a mesma coisa** em
fontes diferentes. Uma clínica aparece no Google, no Instagram, na biblioteca de
anúncios, na Receita e no Reclame Aqui — com nome diferente em cada uma.

### A hierarquia de chaves

| Chave | O que identifica | Origem | Estável? |
|---|---|---|---|
| `praca_id` | a praça (raio real de captação) | atribuída por nós | sim |
| `local_id` | **uma clínica no mundo real** | atribuída por nós | sim |
| `place_id` | a ficha no Google | Google Places | sim — **é a âncora** |
| `cnpj` | a empresa | Receita / Junta | sim |
| `ig_handle` | o perfil no Instagram | — | **não** (muda) |
| `fb_page_id` | a página no Facebook | — | sim |
| `ad_page_id` | o anunciante na Ad Library | Meta | sim |
| `ra_id` | a empresa no Reclame Aqui | — | sim |

**O `place_id` do Google é a âncora.** Todo o resto pendura nele. É o único
identificador que a categoria inteira tem, que não muda, e que o paciente
efetivamente usa para decidir.

### A tabela de amarração

Um arquivo por praça, mantido à mão, revisado a cada coleta:

```yaml
# identidade/mafra.yaml
praca_id: mafra
cidades: [Mafra/SC, Rio Negro/PR]
locais:
  - local_id: ortho_mafra
    papel: proprio
    nome_publico: "OrthoDontic Mafra"
    place_id: "ChIJ..."
    cnpj: "..."
    ig_handle: "orthodontic.mafra"
    ad_page_id: "..."
    ra_id: null
    abertura: 2019-xx
    tipo: franquia
  - local_id: lumiere
    papel: concorrente
    tipo_concorrente: startup_trafego   # rede | clinica_geral | doutor_pf | escola | startup_trafego | especialista
    place_id: "ChIJ..."
    cnpj: "..."          # capital 28x — veio da Junta
    abertura: 2025-10
```

**Por que à mão:** resolução de identidade automática erra, e errar aqui
corrompe toda a série. São ~8 locais por praça, 4 praças. É meia hora de
trabalho, uma vez.

### Riscos de chave já conhecidos

- **Mafra tem homônima em Portugal.** O alerta já está no `targets_mafra.yaml`:
  *"clínica dentária"/beclinique = PT. Filtrar tudo por SC/Brasil.* Isso vira
  validação automática: todo resultado sem `place_id` da tabela é descartado e
  logado, nunca aceito por semelhança de nome.
- **A mesma marca com duas fichas na mesma cidade** (Souza Naves 4,6 × Centro
  3,5, Londrina). São dois `local_id` distintos, ambos `papel: proprio`. Nunca
  agregar sem separar.
- **Mafra é uma praça em dois estados.** `praca_id` ≠ município. A praça é o
  raio de captação, e é ela que agrega.

---

## 2 · AS FONTES

### Bloco A — o que já roda (só precisa virar série)

| Fonte | O que dá | Frequência | Custo/praça/mês | Depende de |
|---|---|---|---|---|
| **Google reviews** (próprios + concorrentes) | nota, volume, texto, data, resposta da clínica | **semanal** | ~US$ 0,30 | nada |
| **Google Places** | nota agregada, volume total, horários, atributos, fotos | semanal | ~US$ 0,05 | nada |
| **Instagram** (próprio, concorrentes, páginas locais) | posts, legendas, comentários, curtidas, seguidores | mensal | ~US$ 0,40 | nada |
| **Facebook** | posts, engajamento | mensal | ~US$ 0,10 | nada |
| **Meta Ad Library** | anúncios ativos, criativo, data de início | **semanal** | ~US$ 0,10 | nada |
| **SERP** | posição na busca por termo | mensal | ~US$ 0,10 | nada |
| **Google Trends** | série de busca por região | mensal | grátis | nada |
| **Junta / Receita** | CNPJ, capital, sócios, abertura | mensal | baixo | nada |

**Total do bloco A: ~US$ 1,20 por praça/mês. Quatro praças: ~US$ 5/mês.**
O dado não é o custo deste projeto.

### Bloco B — os sensores novos de OPERAÇÃO

Este bloco existe porque os quatro estudos concluíram a mesma coisa — **a ferida
é operação** — e nada do bloco A mede operação.

| Sensor | O que dá | Frequência | Como |
|---|---|---|---|
| **Google Business Profile — Insights** | buscas, visualizações, cliques, **ligações**, pedidos de rota, por unidade | mensal | **acesso de parceiro às 4 fichas** |
| **Tempo de 1ª resposta no WhatsApp** | minutos até a primeira resposta, por unidade **e por concorrente** | quinzenal | roteiro padronizado, horários variados |
| **Popular times** | movimento por hora e dia | mensal | Places |
| **Resposta a review** | % respondidos, tempo médio de resposta | semanal | derivado da coleta de reviews |
| **Reclame Aqui completo** | histórico por CNPJ, índice de resposta, tempo, resolução | mensal | plano pago |

**O GBP é o pedido mais importante do piloto inteiro.** As fichas já são da
rede — não passa por TI, não passa por jurídico, é um convite de parceiro por
ficha. E entrega **ligações por mês por unidade**, que é topo de funil real,
sem depender do Conecta.

### Bloco C — o alerta antecipado

| Sensor | O que dá | Frequência |
|---|---|---|
| **Diff do mapa** | clínicas novas no raio da unidade | mensal |
| **CNPJ novo na cidade** | concorrente registrado **antes de abrir** | mensal |
| **Vagas de emprego** | concorrente contratando ortodontista = expansão; unidade repetindo vaga de recepcionista = rotatividade na linha de frente | mensal |
| **Registro do CRO** | quantos ortodontistas na cidade, em qual clínica | trimestral |
| **Imprensa local (RSS)** | menções à unidade, à marca, aos concorrentes | semanal |

*A joia de Mafra — o casal que voltou pra casa — saiu de matéria em jornal
local. Não foi sorte: foi busca documental. Vira rotina.*

### Bloco D — o dado de dentro (não depende de nós)

| Fonte | O que dá | Como pedir |
|---|---|---|
| **Conecta — funil** | interessados → agendados → comparecidos → fechados → pagos | **CSV mensal das 4** |
| **Conecta — base e safra** | base ativa, contratos pagos/mês, safra de pagamento | mesmo CSV |

Mafra já entregou isso uma vez, via print de tela. **Pedir das quatro, em
CSV, é a menor escada possível** — e o precedente já existe.

---

## 3 · O CALENDÁRIO DE COLETA

```
SEMANAL   (segunda de manhã)
  · reviews próprios e concorrentes  → velocity, nota, resposta
  · Meta Ad Library                  → anúncio novo, anúncio que caiu
  · Places (nota e volume agregado)
  · imprensa local

QUINZENAL
  · teste de WhatsApp (própria + concorrentes)

MENSAL    (dia 1)
  · Instagram e Facebook
  · SERP
  · Google Trends
  · GBP Insights                     → ligações, cliques, buscas
  · diff do mapa + CNPJ novo + vagas
  · Reclame Aqui
  · CSV do Conecta

TRIMESTRAL
  · CRO
  · revisão da tabela de identidade
```

**Por que reviews e anúncios são semanais:** são os dois únicos sinais que se
movem rápido o suficiente para virar alerta. Concorrente que começa a anunciar
no pico da temporada — o que aconteceu em Mafra em julho — precisa ser
detectado em dias, não em meses.

---

## 4 · COMO O DADO É GUARDADO

### Layout

```
dados/
  identidade/
    londrina.yaml  prudente.yaml  feira.yaml  mafra.yaml
  bruto/
    <praca_id>/<fonte>/<snapshot_date>/...        # imutável, nunca reescrito
  serie/
    reviews.jsonl        # uma linha por review, com first_seen
    places.jsonl         # uma linha por local por snapshot
    anuncios.jsonl       # uma linha por anúncio por snapshot
    gbp_insights.jsonl   # uma linha por local por mês
    whatsapp.jsonl       # uma linha por teste
    funil.jsonl          # uma linha por unidade por mês (Conecta)
    concorrentes.jsonl   # aparecimentos e desaparecimentos
  classificado/
    reviews_classificados.jsonl   # com taxonomia_versao
  metricas/
    <praca_id>/<snapshot_date>.json               # o painel calculado
```

### Os dois campos que fazem a série funcionar

**`first_seen_snapshot`** — a data da primeira coleta em que aquele review
apareceu. Com isso, **velocity sai de graça**: quantos reviews novos por mês,
por clínica, sem depender de a plataforma informar nada. Foi o dado mais forte
do estudo de Mafra (0,7/mês contra 72 num mês) e foi calculado à mão. Agora
é subproduto.

**`last_seen_snapshot`** — a última coleta em que apareceu. Para anúncios,
`last_seen − first_seen` = **dias no ar**, que é o melhor proxy grátis de
performance que existe. *"Quem paga o mesmo anúncio por 2 meses está tendo
retorno"* — o estudo de Mafra usou isso, agora vira coluna.

Para reviews, `last_seen` também detecta **review apagado** — que é sinal.

---

## 5 · CLASSIFICAÇÃO E O CONTROLE DE VERSÃO DA TAXONOMIA

O `lexico_orthodontic.yaml` classifica cada review em temas (atendimento,
aparelho_tratamento, familia_filhos, preço, espera, contrato…). É de onde saem
os 54% · 47% · 63% · 69%.

**Problema real, já detectado na auditoria dos dossiês:** o léxico foi estendido
depois de Mafra (v1.1, "variantes femininas e nominais" no tema atendimento) e
ficou ambíguo se os percentuais das praças anteriores foram apurados com v1.0 ou
v1.1. Se o léxico muda e a série não guarda com qual versão cada número foi
calculado, **o histórico se reescreve sozinho** e nenhuma comparação entre
praças é confiável.

### As três regras

1. **Todo registro classificado carrega `taxonomia_versao`.**
2. **Mudou o léxico? Sobe a versão e reprocessa o histórico inteiro** — nunca
   comparar número de v1.0 com número de v1.1.
3. **O painel exibe a versão.** "Atendimento 69% *(N=224 · corte 15/jul/2026 ·
   taxonomia v1.1)*" — os três juntos, sempre.

---

## 6 · A REGRA DE PROCEDÊNCIA

A auditoria dos dossiês achou 58 erros, e quase nenhum era de número: eram de
**procedência** — frase atribuída ao capítulo errado, rótulo inventado, duas
citações fundidas em uma.

Num documento isso é chato. Num banco de dados que alimenta IA, é veneno: a IA
vai citar a fonte errada com confiança total.

**Regra:** todo valor no banco carrega de onde veio.

```json
{
  "metrica": "atendimento_pct",
  "valor": 0.69,
  "n": 224,
  "praca_id": "mafra",
  "snapshot_date": "2026-07-15",
  "taxonomia_versao": "1.1",
  "fonte": "reviews_classificados.jsonl",
  "filtro": "praca=mafra AND tem_texto=true",
  "calculado_em": "2026-07-15T17:03:58Z"
}
```

Se não dá para reconstruir o número a partir desses campos, o número não entra.

---

## 7 · A ARMADILHA QUE JÁ EXISTE NOS ESTUDOS

O placar de Prudente declara base de **454 avaliações**, mas a soma das
avaliações do próprio placar dá **1.394**.

Não é erro. São **duas coisas diferentes** que os documentos misturam:

| Campo | O que é |
|---|---|
| `avaliacoes_total` | quantas avaliações a clínica tem no Google |
| `reviews_coletados` | quantos a coleta puxou |
| `reviews_com_texto` | quantos têm texto — **a base de toda estatística de tema** |

No PDF isso passa. No banco, vira erro sistemático: "47% falam de atendimento"
calculado sobre uma base que não é a dela.

**São três colunas, com três nomes, e a estatística de tema sempre declara qual
delas é o denominador.**

---

## 8 · O QUE MUDA NO PIPELINE ATUAL

O que existe hoje (`targets_*.yaml` → `collect_*.py` → `build_corpus.py` →
`corpus.jsonl` + `classificado.jsonl` + `stats.json`) **continua valendo**. As
mudanças são cinco:

1. `snapshot_date` obrigatório em toda saída; `bruto/` vira imutável.
2. `local_id` em todo registro, resolvido pela tabela de identidade — não por
   nome.
3. `build_corpus.py` passa a **acrescentar** em `serie/`, com `first_seen` e
   `last_seen`, em vez de reescrever.
4. `taxonomia_versao` em todo registro classificado.
5. Um passo novo, `build_metricas.py`, que calcula o painel a partir da série —
   e não da coleta da vez.

Os `targets_*.yaml` das quatro praças **já existem e já rodaram**. O piloto não
começa do zero; começa da segunda coleta.

---

## 9 · AS PRÓXIMAS DUAS SEMANAS

| # | O quê | Por quê |
|---|---|---|
| 1 | **Recoletar Mafra agora** | o baseline congelou em 15/jul; um mês depois é a primeira medição de movimento do projeto inteiro |
| 2 | Montar as 4 tabelas de identidade | sem isso nada amarra |
| 3 | Rodar as outras 3 praças com os targets que já existem | dá o segundo ponto da série nas quatro |
| 4 | **Pedir acesso de parceiro às 4 fichas do Google** | o pedido de maior retorno e menor custo político do projeto |
| 5 | Rodar o 1º teste de WhatsApp nas 4 + concorrentes | o número que ninguém tem |
| 6 | Pedir o CSV do Conecta das 4 | precedente já existe (Mafra) |
| 7 | Congelar `taxonomia v1.1` e reprocessar as 4 | para os 54/47/63/69 ficarem comparáveis de verdade |

**O item 1 é o mais urgente e o mais barato.** Custa cerca de um dólar e é a
única coisa neste documento que responde à pergunta que vende o piloto: *o
número se mexeu?*

---

_Camada 1 de 3. A seguir: **inteligência** (o que se calcula e o que a IA lê em
cima disto) e **casco** (as telas)._
