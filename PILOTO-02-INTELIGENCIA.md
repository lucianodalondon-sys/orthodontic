# Piloto Orthodontic · Camada 2 — INTELIGÊNCIA
### O que se calcula, o que a IA lê, e onde ela é proibida

> Camada 2 de 3. Entra depois de [dados e coleta](PILOTO-01-DADOS-E-COLETA.md),
> antes do casco. Aqui ainda não há tela.

---

## 0 · A LINHA QUE DIVIDE TUDO

> **Estatística detecta. IA explica. Humano decide.**

Todo número deste projeto é calculado por conta, não por modelo. A IA nunca
produz um valor — ela lê valores já calculados e escreve o porquê, sempre com a
evidência pendurada.

A razão é prática: um número que saiu de LLM não se reproduz, não se audita e
não sobrevive a uma pergunta de conselho. Um número que saiu de `COUNT(*)`
sobrevive.

**Consequência:** se uma pergunta pode ser respondida por consulta, ela **não**
passa por IA. IA custa dinheiro, varia entre execuções e erra com confiança.

---

## 1 · O QUE SE CALCULA (determinístico, sem IA)

Tudo abaixo sai da série da camada 1. Nenhum item precisa de modelo.

### Reputação

| Métrica | Como | Por que importa |
|---|---|---|
| **Velocity** — reviews novos/mês por local | `COUNT` por `first_seen_snapshot` | foi o dado mais forte do projeto: 0,7/mês contra 72 num mês |
| **Velocity normalizada por idade** | velocity ÷ meses de operação | Prudente fez 582 em 20 anos; a vizinha de Riomafra fez 197 em 9 meses. Comparar volume bruto engana |
| **Gap de volume vs líder da praça** | `volume_lider ÷ volume_proprio` | 3,4x em Riomafra, 7x em Feira |
| **Meses para ultrapassar o líder** | gap ÷ (velocity própria − velocity líder) | transforma o gap em prazo. Se der negativo, o gap está **crescendo** — e isso é o alerta |
| **% respondidos e tempo de resposta** | da coleta semanal | o líder de Rio Negro vence respondendo cada avaliação |
| **Distribuição de estrelas** | histograma | Prudente: 83×5★, 1×1★, zero no meio — consistência é sinal |
| **% que cita profissional pelo nome** | léxico | 9% na clínica infantil de Riomafra, o dobro da unidade |
| **% por tema** | léxico + `taxonomia_versao` | os 54 · 47 · 63 · 69 |

### Presença e mídia

| Métrica | Como |
|---|---|
| **Anúncios ativos** por anunciante | contagem no snapshot |
| **Dias no ar** por criativo | `last_seen − first_seen` |
| **Share de voz da praça** | anúncios próprios ÷ total da praça |
| **Registro do criativo** | classificação por regra: urgência-desconto · preço-claro · acolhimento · rosto · institucional |
| **Silêncio no pico** | anúncios ativos = 0 **E** índice sazonal do mês no quartil superior |
| **Posição na busca** por termo, e o delta | SERP mensal |

### Operação

| Métrica | Como |
|---|---|
| **Ligações, cliques, buscas** por unidade/mês | GBP Insights |
| **Taxa ligação → agenda** | ligações (GBP) × agendamentos (Conecta) — **o topo de funil sem depender só do Conecta** |
| **Tempo de 1ª resposta no WhatsApp** (mediana e p90) | teste quinzenal |
| **Desvio da régua** por estágio | funil ÷ (40 · 50 · 80 · 90) |
| **Concentração de lead** (rajada × fluxo) | desvio-padrão de interessados/dia |

Essa última merece nota: o estudo de Riomafra achou que os interessados chegam
em **rajadas** e que na rajada o agendamento desaba. Se isso se confirmar nas
outras três, deixa de ser característica local e vira **defeito de desenho de
campanha da rede** — um dos achados mais caros que o piloto pode produzir.

---

## 2 · DETECÇÃO DE ANOMALIA — ESTATÍSTICA, NÃO IA

Com 4 praças e poucos meses de série, modelo preditivo é fantasia. O que
funciona é regra com limiar, calibrada nos números que os estudos já
produziram.

| Alerta | Regra | Origem do limiar |
|---|---|---|
| 🔴 **Concorrente invadiu a categoria** | anunciante que nunca falou de aparelho publica criativo com termo de ortodontia | a Lumière entrou em ortodontia em julho, no pico |
| 🔴 **Silêncio no pico** | anúncios = 0 **E** mês no quartil superior de busca | Riomafra: 0 contra 10 e 7, em julho |
| 🔴 **Review negativo sem resposta** | ≤3★ e sem resposta em 48h | a mãe lê os comentários antes de escolher |
| 🟠 **Velocity travada** | < 2 reviews/mês por 2 meses seguidos | 0,7/mês é o caso patológico documentado |
| 🟠 **Gap crescendo** | meses-para-ultrapassar piora 2 meses seguidos | — |
| 🟠 **Nota caindo** | queda ≥ 0,1 em 2 meses | meta declarada dos planos: nota ≥ 4,8 |
| 🟠 **WhatsApp lento** | mediana > 30 min em horário comercial | a ferida nº 1 das quatro praças |
| 🟡 **Clínica nova no raio** | CNPJ novo ou local novo no diff do mapa | a Lumière apareceu a 70 m |
| 🟡 **Vaga repetida de recepção** | 2ª publicação em 6 meses | rotatividade na linha de frente = onde o funil quebra |
| 🔴 **Agendamento fora da régua** | < 20% (metade da régua) | Riomafra: 6% contra 40% |

**Cada alerta nasce com três coisas ou não nasce:** o que aconteceu, a evidência
clicável, e o que fazer. Alerta sem ação vira ruído, e ruído vira portal que
ninguém abre.

---

## 3 · A IA — O QUE É REAL, O QUE É APOSTA, O QUE É PROIBIDO

### Real hoje — já executado neste projeto

Não é promessa. Cada item abaixo já rodou nesta base:

| Tarefa | Prova |
|---|---|
| **Classificar review por tema em escala** | os 54 · 47 · 63 · 69 saíram disso, com léxico + LLM |
| **Ler o playbook de um concorrente** a partir dos posts públicos dele | os 4 movimentos do gigante de Feira; a receita da Lumière |
| **Sintetizar corpus em diagnóstico** | os quatro estudos |
| **Auditar documento contra a fonte** | a auditoria adversarial dos dossiês achou 58 erros de procedência |
| **Escrever na língua de uma praça, com as proibições** | o kit de execução de Riomafra |
| **Extrair pauta do autocomplete** | *"é normal ficar 7 anos de aparelho?"* |

Essa lista é o argumento de venda mais honesto do projeto: **não estamos
propondo IA, estamos industrializando IA que já produziu os quatro estudos.**

### Aposta — declarada como tal, e desligada até haver amostra

| Tarefa | Por que ainda não | Quando liga |
|---|---|---|
| **Prever churn de safra** | precisa de safras de várias unidades | 20+ unidades com Conecta |
| **Escolher a próxima praça a estudar** | com 4, a amostragem se faz à mão | 15+ praças |
| **Transcrever e analisar conversa de orçamento** | é o sensor de maior valor **e** o maior risco jurídico | só com desenho de consentimento fechado |
| **Correlacionar ação → resultado** | precisa de intervenções registradas | a partir do 3º review de 90 dias |

### Proibido — trava de produto, não recomendação

1. **A IA nunca produz um número.** Só lê números calculados.
2. **Nenhuma recomendação sem evidência pendurada.** Se não há evidência, a
   saída é *"não sei"* — e "não sei" é uma resposta válida do sistema.
3. **Nunca reescrever citação de paciente.** A imperfeição é a prova.
4. **Nunca gerar depoimento**, nem exemplo "ilustrativo" de paciente.
5. **Nunca emitir claim público sem marca de validação.** *"A mais bem avaliada
   da cidade"* sai com `validar antes de publicar` grudado — o próprio estudo de
   Prudente exige isso.
6. **Nunca prometer resultado clínico.** Antes/depois só com responsável técnico
   + CRO + consentimento.
7. **Nunca ranquear franqueado nominalmente** na visão de rede.
8. **Nunca tratar a Oral Sin como concorrente** — é marca-irmã.
9. **Nunca escrever que o franqueado errou.** O problema se nomeia como sistêmico.

---

## 4 · O CONTRATO DE EVIDÊNCIA

Toda saída de IA carrega uma lista de evidências, e cada evidência é um ponteiro
verificável na série — não uma paráfrase.

```json
{
  "afirmacao": "O gargalo está entre o interesse e a agenda, não no fechamento.",
  "confianca": "alta",
  "evidencias": [
    {"tipo":"funil","praca":"riomafra","campo":"agendamento_pct","valor":0.059,
     "n":5050,"snapshot":"2026-07-15","fonte":"funil.jsonl"},
    {"tipo":"regua","campo":"agendamento_meta","valor":0.40},
    {"tipo":"funil","campo":"fechamento_pct","valor":0.748,"comparado_a":0.80}
  ],
  "contra_evidencias": [
    {"nota":"os 109 pagos não reconciliam com ~336 contratos/ano — denominador em aberto"}
  ]
}
```

**O campo `contra_evidencias` não é enfeite.** É o que separa análise de
propaganda, e é o que faz o documento sobreviver a uma mesa cética. O projeto
inteiro já usa isso: o capítulo 2 do projeto do portal ataca o próprio 3,4x
antes do conselho atacar.

**Confiança tem regra, não é adjetivo:**

| Nível | Critério |
|---|---|
| **alta** | ≥3 evidências independentes, mesma direção, sem contra-evidência aberta |
| **média** | 2 evidências, ou contra-evidência conhecida e declarada |
| **baixa** | 1 evidência, ou série menor que 3 pontos |
| **não sei** | não há evidência — e o sistema diz isso |

---

## 5 · A MÁQUINA DE ESTADOS DOS ACHADOS

O que se descobre numa praça não vale para 340. O portal precisa de um lugar
onde isso fica explícito — e essa é a tela mais estratégica do produto.

```
HIPÓTESE          1-2 praças
   ↓
CANDIDATA         3+ praças, mesma direção
   ↓
CONSTANTE         praças diversas em região, porte e idade de unidade
   ↓
DOUTRINA          a rede decidiu agir com base nisso
   
❌ DERRUBADA      uma praça contradiz — e fica registrado qual
```

**Onde as 13 constantes estão hoje, com honestidade:** todas em **CANDIDATA**.
Quatro praças confirmam, mas são quatro praças de uma amostra que não cobre
Norte, Centro-Oeste, capital, nem unidade recém-aberta. Nenhuma é doutrina.

**E já existe uma derrubada** — a mais valiosa do projeto:

> *"Dez/jan é pico nacional"* → ❌ **DERRUBADA** por Riomafra.
> Série de 5 anos: julho índice 34, dez/jan 2,5–7,9. Confirmado pelo BI: 4.120
> interessados em julho/25 contra 494 e 78.

Isso custou centavos de coleta e evitou verba nacional programada para o mês
errado em parte do país. **É o melhor argumento de ROI que o piloto tem**, e é
argumento de método, não de tecnologia.

**Regra:** toda promoção de estado exige praças **diversas**, não só numerosas.
Quatro praças parecidas não fazem constante.

---

## 6 · OS DOIS LINTERS (aqui a IA vira produto, não enfeite)

### Linter A — o corretor de campanha nacional

A franqueadora sobe uma campanha. O sistema roda contra o DNA de cada praça e
devolve o risco, praça a praça.

Entrada: peça nacional. Saída, por praça:

| Praça | Veredito | Por quê |
|---|---|---|
| Londrina | ⚠️ risco | preço baixo levanta **suspeita**; a alavanca é confiança + preço justo |
| Prudente | 🟡 adaptar | a alavanca é **clareza**, não desconto |
| Feira | 🟢 funciona | preço é **orgulho** — mas tem que falar como Feira |
| Riomafra | 🔴 conflito | "última chance" queima no radar antivigarista da colônia |

**Isto é real hoje.** As proibições de tom estão documentadas praça a praça nos
quatro estudos. É consulta a uma tabela + geração — não previsão.

E é a tela que a franqueadora compra primeiro, porque **mede o trabalho dela**,
não o do franqueado. Custo político zero.

### Linter B — o corretor de peça local

Antes de qualquer peça sair, passa por seis checagens:

1. Usa léxico proibido da praça? *(axé litorâneo em Feira, gíria gaúcha em
   Riomafra)*
2. Promete resultado clínico? *(compliance CFO)*
3. Tem antes/depois sem CRO e consentimento?
4. Expõe número interno em peça pública?
5. Culpa ou expõe o franqueado?
6. Tem claim não validado?

Saída: aprovado · aprovado com ressalva · bloqueado, com a linha e a regra.

---

## 7 · O REGISTRO DO QUE FUNCIONA (o fosso)

É a única coisa aqui que ninguém copia. Método, telas e IA outra consultoria
refaz em um ano. **Isto só se acumula vivendo.**

Cada intervenção vira registro:

```json
{
  "unidade": "ortho_mafra",
  "acao": "ligar a máquina de avaliações",
  "iniciada": "2026-08-01",
  "baseline": {"velocity": 0.7, "nota": 4.9, "snapshot": "2026-07-15"},
  "aos_90_dias": {"velocity": null, "nota": null},
  "contexto": {"porte_praca":"pequena","idade_unidade":7,"posicao":"lider_nota"},
  "aderencia": null,
  "resultado": null
}
```

O campo **`aderencia`** decide se o registro vale. Sem saber se a unidade
executou, "não funcionou" e "não fizeram" viram a mesma coisa — e a base aprende
errado. Aderência se mede pelo próprio portal (a máquina de reviews ligou? o
anúncio subiu?), não por declaração.

E o campo **`contexto`** é o que transforma caso em conhecimento: *"em praça
pequena, com unidade líder em nota e velocity travada, ligar a máquina de
reviews levou X para Y em 90 dias."* Isso é o que se vende para a unidade 341.

**Primeiro registro possível: meados de outubro/2026**, o review de 90 dias de
Riomafra.

---

## 8 · O QUE A IA RESPONDE — E COMO

Perguntas que o sistema responde **por consulta** (sem IA): qual unidade tem a
pior velocity · quem está anunciando em Feira · quantos reviews sem resposta ·
qual praça está no pico.

Perguntas que precisam de IA (leitura, não cálculo): *por que* Riomafra está
perdendo pacientes · o que o playbook do concorrente tem que a gente não tem ·
essa campanha nacional desce bem em Prudente · o que mudou desde a última coleta
e o que isso significa.

**A resposta sempre tem a mesma forma:** a leitura, as evidências clicáveis, as
contra-evidências, o nível de confiança, e o que fazer. Nessa ordem. Sem uma
das cinco, não sai.

---

## 9 · O QUE ENTRA NO PILOTO DE 4

| Entra agora | Fica para depois |
|---|---|
| todas as métricas determinísticas | previsão de churn |
| os 10 alertas com limiar | escolha automática da próxima praça |
| a máquina de estados (travada em CANDIDATA) | promoção a doutrina |
| o Linter A (campanha nacional) | análise de conversa de orçamento |
| o Linter B (peça local) | correlação ação → resultado em escala |
| o contrato de evidência | |
| o registro de intervenção (aberto, sem resultado ainda) | |

Com 4 praças e 2 meses de série, o piloto **não prevê nada**. Ele detecta,
explica e registra. Previsão precisa de amostra, e dizer isso na cara é o que
faz a diretoria confiar no resto.

---

_Camada 2 de 3. A seguir: **casco** — as telas, e quem vê o quê._
