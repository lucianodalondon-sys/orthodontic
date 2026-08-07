# A COLETA — inventário completo de fontes
### Piloto de 4 praças · o que entra, de onde, com que frequência

> **O princípio:** cada fonte responde uma pergunta que o portal precisa
> responder. Fonte que não responde pergunta nenhuma não entra — vira custo e
> ruído. Cada linha abaixo declara a pergunta.

**Legenda de status**
`✅ roda hoje` · `🔨 construir` (sem bloqueio) · `🔑 precisa acesso` ·
`💰 precisa verba` · `⚠️ cuidado de uso`

---

## O DIAGNÓSTICO DE HOJE

Os quatro estudos concluíram a mesma coisa — **a ferida é operação**: agenda,
resposta, espera, contrato. E a coleta atual **não mede operação em nada**.

Ela mede reputação (Google), comunicação (Instagram, Meta Ad Library) e
contexto (SERP, Trends, Censo). Tudo isso é *resultado*. A *causa* está fora.

Além disso, a fonte que mais importava foi usada pela metade: o Reclame Aqui
bateu no limite gratuito de **3 reclamações** — e com três já se concluiu
*"100% financeiro/contrato, todas sem resposta"*.

Este documento fecha os dois buracos.

---

## BLOCO 1 · REPUTAÇÃO — a voz do paciente

| # | Fonte | A pergunta que responde | Freq. | Status |
|---|---|---|---|---|
| 1 | **Google reviews** (própria + concorrentes) | como o paciente descreve o que viveu? | semanal | ✅ |
| 2 | **Google Places** | nota e volume agregados, horários, atributos | semanal | ✅ |
| 3 | **Google — Perguntas e respostas da ficha** | o que o paciente pergunta **antes** de decidir | mensal | 🔨 |
| 4 | **Reclame Aqui completo** | qual unidade tem ferida de contrato — e responde? | mensal | 💰 |
| 5 | **Consumidor.gov.br** | reclamação oficial, base independente do RA | mensal | 🔨 |
| 6 | **Doctoralia / BoaConsulta** | avaliação por **profissional nomeado** | mensal | 🔨 |
| 7 | **Facebook — avaliações da página** | a voz que não está no Google | mensal | 🔨 |

**Por que 4 é a prioridade nº 1 de construção.** É por CNPJ, ou seja, **por
unidade**, e entrega o que nenhuma outra fonte pública entrega: volume de
reclamação, índice de resposta, tempo de resposta e taxa de solução. É a única
medição pública de operação que existe — exatamente a ferida das quatro praças.

**Por que 6 importa mais do que parece.** A constante nº 3 do projeto é *"a
confiança é em gente com nome"*. A Doctoralia avalia **o profissional**, não a
clínica. É a única plataforma que mede diretamente a constante — e ficou de fora.

### Saída → `serie/reviews.jsonl`
```json
{"snapshot_date":"2026-08-12","praca_id":"riomafra","local_id":"ortho_mafra",
 "plataforma":"google","review_id":"…","nota":5,"texto":"…","data":"2026-07-30",
 "respondida":true,"resposta_em_dias":2,"cita_profissional":true,
 "first_seen_snapshot":"2026-08-12","last_seen_snapshot":"2026-08-12"}
```

### Saída → `serie/reclamacoes.jsonl`
```json
{"snapshot_date":"2026-08-12","praca_id":"riomafra","local_id":"ortho_mafra",
 "plataforma":"reclame_aqui","total":12,"respondidas":3,"indice_resposta":0.25,
 "tempo_medio_resposta_dias":9,"taxa_solucao":0.18,
 "temas":{"financeiro_contrato":0.83,"atendimento":0.17}}
```

---

## BLOCO 2 · A CIDADE — a voz do território

| # | Fonte | A pergunta que responde | Freq. | Status |
|---|---|---|---|---|
| 8 | **Instagram** (própria, concorrentes, páginas locais) | como a cidade fala, o que premia | mensal | ✅ |
| 9 | **Facebook** (posts) | idem, público mais velho | mensal | ✅ |
| 10 | **Grupos públicos de Facebook da cidade** | **a decisão acontecendo** — "alguém indica ortodontista?" | mensal | 🔨⚠️ |
| 11 | **TikTok local** | o público jovem e o formato que engaja | mensal | 🔨 |
| 12 | **Comentários do YouTube** (canais locais) | idem | trimestral | 🔨 |
| 13 | **Imprensa local** (RSS / Google News) | a joia enterrada, e o que a cidade noticia | semanal | 🔨 |

**Por que 10 é a joia deste bloco.** As outras fontes capturam opinião *depois*
do consumo. O grupo de bairro captura **a escolha em tempo real**: a mãe
perguntando, os vizinhos indicando, e as objeções aparecendo na mesma conversa.
Não existe fonte melhor para entender por que o paciente escolhe.

**Por que 13 não é decoração.** A joia de Riomafra — o casal que voltou pra
casa — saiu de matéria em jornal local. Não foi sorte: foi busca documental.
Vira rotina.

### Saída → `serie/vozes.jsonl`
```json
{"snapshot_date":"2026-08-12","praca_id":"riomafra","plataforma":"facebook_grupo",
 "origem":"grupo-classificados-riomafra","camada":"territorio",
 "segmento":"mae","texto":"…","curtidas":14,"data":"2026-08-03",
 "temas":["indicacao","preco"],"taxonomia_versao":"1.1"}
```

⚠️ **Cuidado com 10 e 11.** Só grupo **público**, só conteúdo público, sem
identificar autor, com o texto anonimizado no corpus. Nada de grupo fechado.

---

## BLOCO 3 · MÍDIA E BUSCA — o que o concorrente faz

| # | Fonte | A pergunta que responde | Freq. | Status |
|---|---|---|---|---|
| 14 | **Meta Ad Library** | quem anuncia, o quê, há quantos dias | semanal | ✅ |
| 15 | **Google Ads Transparency Center** | **quem compra a busca** — nunca olhamos | semanal | 🔨 |
| 16 | **SERP** | quem aparece quando o paciente procura | mensal | ✅ |
| 17 | **Autocomplete + "as pessoas também perguntam"** | as dúvidas reais, em pauta pronta | mensal | ✅ |
| 18 | **Google Trends** | quando a praça procura | mensal | ✅ |

**15 é um buraco grande.** Toda a análise de mídia dos quatro estudos é do
**Meta**. Se o concorrente compra "aparelho ortodôntico [cidade]" no Google, ele
está invisível para nós — e é justamente onde a intenção de compra é maior. O
Centro de Transparência de Anúncios do Google é público.

### Saída → `serie/anuncios.jsonl`
```json
{"snapshot_date":"2026-08-12","praca_id":"riomafra","anunciante":"lumiere",
 "plataforma":"meta","ad_id":"…","texto":"…","produto":"aparelho",
 "registro":"urgencia_desconto","geo_declarada":["Mafra","Itaiópolis"],
 "first_seen_snapshot":"2026-07-15","last_seen_snapshot":"2026-08-12","dias_no_ar":28}
```

`dias_no_ar` sai de `last_seen − first_seen`. **Criativo que sobrevive 2 meses
está performando** — é o melhor proxy grátis de performance que existe.

---

## BLOCO 4 · OPERAÇÃO — a ferida que ninguém mede

**Este bloco não existe hoje. É o mais importante.**

| # | Fonte | A pergunta que responde | Freq. | Status |
|---|---|---|---|---|
| 19 | **Google Business Profile — Insights** | quantos buscaram, viram, clicaram e **ligaram** | mensal | 🔑 |
| 20 | **Tempo de 1ª resposta no WhatsApp** | quanto o paciente espera para ser atendido | quinzenal | 🔨 |
| 21 | **Popular times** | a espera é pico ou é processo? | mensal | 🔨 |
| 22 | **Resposta a review** (derivado de 1) | a clínica responde? em quanto tempo? | semanal | 🔨 |
| 23 | **Cliente-oculto** | a experiência real de quem chega | trimestral | 🔨 |

**19 é o pedido de maior retorno e menor custo político do projeto.** As fichas
já são da rede — é convite de parceiro por ficha, não passa por TI nem
jurídico. E entrega **ligações por mês por unidade**: topo de funil real, sem
depender do Conecta.

**20 mede a ferida nº 1 das quatro praças e ninguém tem esse número.** Faz na
própria unidade **e nas concorrentes** — o comparativo é o que dá o argumento.

### Saída → `serie/operacao.jsonl`
```json
{"snapshot_date":"2026-08-01","praca_id":"riomafra","local_id":"ortho_mafra",
 "fonte":"gbp_insights","mes":"2026-07",
 "buscas":3120,"visualizacoes":8940,"cliques_site":210,"ligacoes":186,"rotas":94}
```
```json
{"snapshot_date":"2026-08-12","praca_id":"riomafra","local_id":"ortho_mafra",
 "fonte":"whatsapp_teste","enviado_em":"2026-08-12T10:14",
 "primeira_resposta_min":47,"horario_comercial":true,"respondeu":true}
```

---

## BLOCO 5 · ALERTA ANTECIPADO — ver o concorrente antes dele abrir

| # | Fonte | A pergunta que responde | Freq. | Status |
|---|---|---|---|---|
| 24 | **CNPJ novo** (Receita / Junta) | quem vai abrir na praça | mensal | 🔨 |
| 25 | **Diff do mapa** | quem apareceu no raio desde a última coleta | mensal | 🔨 |
| 26 | **Vagas de emprego** | concorrente expandindo · nossa rotatividade | mensal | 🔨 |
| 27 | **Registro do CRO** | quantos ortodontistas na cidade, em qual clínica | trimestral | 🔨 |
| 28 | **Glassdoor / Indeed** | **a voz do funcionário da linha de frente** | trimestral | 🔨 |

**26 lê nos dois sentidos.** Concorrente contratando três ortodontistas =
expansão. Nossa unidade publicando "recepcionista" pela segunda vez em seis
meses = rotatividade **exatamente onde o funil quebra**.

**28 é a fonte que ninguém pensa em olhar.** A recepção é a ferida nº 1 em todas
as praças. Funcionário insatisfeito na linha de frente explica o agendamento de
6% melhor que qualquer análise de mídia.

**24 foi feito uma vez, à mão** — foi assim que se descobriu que a Lumière tinha
capital 28x maior. Vira rotina e você vê o concorrente **antes de ele abrir**.

### Saída → `serie/concorrentes.jsonl`
```json
{"snapshot_date":"2026-08-12","praca_id":"riomafra","evento":"novo_cnpj",
 "razao_social":"…","cnae":"8630-5/04","capital":150000,"abertura":"2026-07-28",
 "distancia_km":1.2,"fonte":"junta_comercial"}
```

---

## BLOCO 6 · CONTEXTO — o tabuleiro

| # | Fonte | A pergunta | Freq. | Status |
|---|---|---|---|---|
| 29 | **IBGE / SIDRA** | tamanho e renda do público-alvo | anual | ✅ |
| 30 | **Calendários escolares estaduais** | quando a mãe decide | anual | ✅ |
| 31 | **Calendário cultural local** | o ano que a cidade vive | anual | autorado |

---

## BLOCO 7 · INTERNO — o que só a rede tem

| # | Fonte | A pergunta | Freq. | Status |
|---|---|---|---|---|
| 32 | **Conecta — funil** | onde o interessado evapora | mensal | 🔑 |
| 33 | **Conecta — base e safra** | a base derrete? a safra para de pagar? | mensal | 🔑 |

Riomafra já entregou uma vez, via print de tela. **Pedir das quatro, em CSV, é
a menor escada possível** — o precedente existe.

---

## A ESCADA DE PEDIDOS (o que depende da rede)

Não se pede o Conecta na primeira conversa. Pede-se na quarta.

| # | O pedido | Custo político | O que destrava |
|---|---|---|---|
| 1 | **CSV de funil das 4 unidades, de um mês** | mínimo — é export | o mapa do vazamento; e se travar, você sabe em agosto |
| 2 | **Parceiro nas 4 fichas do Google** | baixo — a ficha é da rede | ligações, cliques, buscas, e responder review pelo portal |
| 3 | **Parceiro no Meta Business das unidades** | médio | verba, leads e custo por lead reais |
| 4 | **Integração com o Conecta** | alto — TI, jurídico | tudo, para as 340 |

---

## ORDEM DE CONSTRUÇÃO

**Semana 1 — o que não depende de ninguém**
1. Recoletar as 4 com o pipeline que já roda *(o 2º ponto da série)*
2. Reclame Aqui completo, por CNPJ *(💰 — o coletor de maior valor)*
3. Resposta a review + tempo de resposta *(derivado, sai de graça da coleta 1)*
4. Primeiro teste de WhatsApp nas 4 + concorrentes

**Semana 2 — os alertas antecipados**
5. Google Ads Transparency *(o buraco de mídia)*
6. Diff do mapa + CNPJ novo
7. Imprensa local por RSS
8. Vagas de emprego

**Semana 3 — a voz que falta**
9. Doctoralia *(avaliação por profissional nomeado)*
10. Grupos públicos de Facebook das 4 cidades
11. Perguntas e respostas da ficha do Google
12. Consumidor.gov.br

**Quando o acesso vier**
13. GBP Insights *(pedido 2)*
14. Conecta *(pedidos 1 e 4)*

---

## O CALENDÁRIO EM REGIME

```
SEMANAL   · reviews (própria + concorrentes) → velocity, nota, resposta
          · Meta Ad Library + Google Ads Transparency
          · Places (nota e volume)
          · imprensa local

QUINZENAL · teste de WhatsApp (própria + concorrentes)

MENSAL    · Instagram, Facebook, grupos públicos, TikTok
          · SERP + autocomplete + Trends
          · GBP Insights · popular times
          · Reclame Aqui · Consumidor.gov · Doctoralia
          · diff do mapa · CNPJ novo · vagas
          · CSV do Conecta

TRIMESTRAL· CRO · Glassdoor/Indeed · cliente-oculto · YouTube

ANUAL     · IBGE/SIDRA · calendários escolares · calendário cultural
```

**Por que reviews e anúncios são semanais:** são os únicos sinais que se movem
rápido o bastante para virar alerta. Concorrente que começa a anunciar no pico
— o que aconteceu em Riomafra em julho — precisa ser detectado em dias.

---

## CUSTO

| Bloco | Por praça/mês |
|---|---|
| O que já roda (reviews, IG, FB, ads, SERP, Trends) | ~US$ 1,20 |
| Reclame Aqui completo | ~US$ 1 a 3 *(por reclamação)* |
| Coletores novos (mapa, CNPJ, vagas, imprensa, Doctoralia) | ~US$ 0,50 |
| GBP Insights, Conecta | grátis — é acesso, não coleta |
| **Total, 4 praças** | **~US$ 12 a 20/mês** |

O dado não é o custo deste projeto. O custo é construir os coletores.

---

## CUIDADOS DE USO

- **Só conteúdo público.** Nada de grupo fechado, nada de perfil privado.
- **Texto anonimizado no corpus.** O paciente não é identificado — nem por
  nome, nem por foto, nem por link.
- **Citação nunca é reescrita.** A imperfeição é a prova.
- **Reclamação e avaliação negativa** entram como dado agregado e tema; o caso
  individual não vira peça de comunicação.
- **Dado de funcionário** (Glassdoor) só em agregado — nunca cita pessoa.
- Respeitar limite de requisição de cada fonte. Coletor que apanha é coletor
  que some no meio da série.

---

## O QUE A COLETA CONTINUA SEM VER

Registrar isto é parte do método — o estudo tem uma página inteira sobre isso.

1. **Quem ouviu o preço e foi embora sem escrever nada.** Nenhuma fonte pública
   tem essa voz. Só cliente-oculto, entrevista com desistente, ou a gravação do
   orçamento.
2. **As conversas em grupo fechado** — parte do boca a boca acontece lá.
3. **O share real de receita** — o placar compara reputação, não faturamento.
4. **Lembrança de marca** — só a rede pode medir, e nunca divulgou.

O portal declara esses quatro buracos na tela. Um sistema que diz o que não vê
é mais confiável que um que finge ver tudo.
