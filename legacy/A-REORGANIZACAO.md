# A reorganização do portal

Uma revisão externa leu a base inteira e o casco, sem saber o que a gente
queria ouvir. O veredito foi curto:

> "O produto está perto do problema certo, mas ainda entrega inteligência
> como **acervo**. O valor econômico está em decidir **onde intervir antes que
> uma unidade perca relevância local**."

Este documento é o que fizemos com isso. Não é um plano: já está no
repositório e já roda.

---

## 1 · A pergunta mais cara que os dados já respondem

> **"Em quais unidades a OrthoDontic está perdendo atenção local, para qual
> concorrente, e onde a franqueadora deve intervir primeiro neste mês?"**

"Perder atenção" aqui é participação observável em busca, avaliações,
publicidade e atividade digital. **Não é faturamento**, e a tela é obrigada a
dizer isso.

O portal respondia pedaços dessa pergunta em telas separadas — quem parou,
presença na busca, ficha de praça, plano do franqueado. Nenhuma delas
entregava a lista única, ordenada, com a unidade ameaçada, o concorrente que
avança, a evidência e a intervenção.

Pior: existia uma ferramenta chamada **"Carteira do consultor"** que prometia
responder *"quem visitar primeiro, e por quê"*. O arquivo por trás dela
(`corretor.json`) tinha **quatro pareceres sobre uma peça de anúncio**. A
promessa estava no menu; a entrega, não.

**O que foi feito:** a Carteira do consultor saiu do menu. Quem cumpre a
promessa dela agora é a **fila de intervenção** (`scripts/fila.py` →
`dados/portal/fila.json`), e cumpre com número, concorrente nomeado, gatilho
auditável, ação, prazo e dono.

---

## 2 · A fila, e como ela é montada

Cinco gatilhos. Cada um é uma pergunta de sim ou não que se responde com um
número que está num arquivo. Nenhum é opinião: se não dá para apontar o
arquivo, não entra.

| gatilho | peso | o que dispara |
|---|---|---|
| O contador de avaliações parou | 30 | menos de 3 meses seguidos com movimento acima do típico da própria unidade |
| Um concorrente sustenta e corre mais | 25 | rival com 10+ meses seguidos e ritmo acima do nosso e da mediana da rede |
| Está na metade de baixo da própria praça | 20 | posição no placar da praça |
| Unidade nova que ainda não engatou | 20 | primeira avaliação há menos de 12 meses |
| Nota abaixo da mediana da praça | 15 | diferença de 0,3 ou mais |
| Silêncio publicitário com leilão cheio | 15 | 5+ anunciantes no ar na praça e nenhum é da rede |

Três travas que evitam alerta falso:

- **"Parou" ≠ "acabou de abrir".** São diagnósticos opostos e a ação é outra.
  A data da primeira avaliação separa os dois.
- **Diferença de nota abaixo de 0,3 não é achado, é arredondamento.** Sem essa
  trava, 4,9 contra mediana 5,0 vira alerta e o consultor perde a viagem.
- **Leilão vazio não é silêncio.** Mafra tem *zero* anunciantes na praça
  inteira. Cobrar campanha lá seria inventar um problema.

### A fila de hoje

| # | | urg | unidade | por quê |
|---|---|---|---|---|
| 1 | 🔴 | 90 | PR · Londrina · Centro | parou · Vittallon sustenta 11 meses a 35,6/mês contra 0,8 · 23º de 24 · nota 3,8 contra mediana 5,0 |
| 2 | 🔴 | 75 | MT · Cuiabá · Dom Bosco | parou · ODONTO MEDICINA sustenta 19 meses a 31,4/mês contra 0,7 · 29º de 29 |
| 3 | 🔴 | 75 | BA · Feira de Santana | parou · Central do Sorriso sustenta 12 meses a 38,9/mês contra 3,2 · 17º de 22 |
| 4 | 🔴 | 75 | MT · Cuiabá · Fernando Corrêa | parou · mesmo rival · 16º de 29 |
| 5 | 🟡 | 50 | SC · Mafra | parou · 9º de 15 |
| 6 | 🟢 | 15 | MG · Contagem | nota 4,6 contra mediana 4,9 |
| 7 | 🟢 | 15 | PR · Londrina · Souza Naves | nota 4,6 contra mediana 5,0 |
| 8 | 🟢 | 15 | TO · Palmas | 22 anúncios no ar de 16 anunciantes, nenhum da rede |
| 9 | 🟢 | 0 | MT · Cuiabá Centro Norte | — |

A unidade que a rede mais mostra em apresentação (Souza Naves, a de maior
ritmo) aparece em verde com um problema pequeno. A que ninguém cita
(Londrina Centro, dentro da matriz) abre a fila. Isso é a fila funcionando.

---

## 3 · O risco de morrer no terceiro mês

A revisão foi específica e está certa:

> "Não conseguir demonstrar que **nenhuma decisão ou resultado mudou** por
> causa dele. A suposta série é, na prática, quase toda fotografia de agosto.
> No terceiro mês o portal terá números públicos atualizados, mas não
> responderá: *o que recuperamos?*"

Não dá para consertar isso com mais tela. Só existe uma saída, e ela custa
zero: **fechar o ciclo**.

Cada linha da fila nasce com um bloco `ciclo`:

```json
"ciclo": { "alertado_em": "2026-08-09", "acao_confirmada": null,
           "confirmada_em": null, "resultado": null, "medido_em": null }
```

Nasce vazio de propósito, e a tela é obrigada a mostrar que está vazio. A
partir da segunda coleta, cada alerta carrega o que foi feito e o que
aconteceu depois. Em três ciclos a franqueadora deixa de saber *o que existe
na internet* e passa a saber **quais intervenções funcionam**.

Esse histórico **alerta → ação → resultado** é a única coisa aqui que um
concorrente não copia raspando as mesmas fontes públicas — porque ele não
tem a rede executando.

---

## 4 · O que um concorrente esperto faria

Copiaria as fontes públicas em escala nacional — isso é reproduzível — e
fecharia o circuito com CRM e operação: 374 unidades no primeiro dia, leads e
contratos diários, alerta dentro do WhatsApp do consultor, experimento
controlado por recomendação, relatório mensal em reais.

Em 12 meses ele teria causalidade. A defesa não é ter mais telas. É:

1. **Fechar o ciclo antes dele** — a fila já nasce com o campo.
2. **Ir para as 374** — o coletor da lista oficial já lê todas; o que falta é
   a varredura de reviews, que é custo de API, não de código.
3. **Entrar onde a decisão é tomada** — a fila é curta o suficiente para caber
   numa mensagem semanal. Não precisa de portal para chegar ao consultor.

---

## 5 · O menu: três andares em vez de treze ferramentas

Treze ferramentas lado a lado é um armário. Quem abre não sabe por onde
começar, e uma ferramenta que muda uma decisão fica do lado de uma que só se
consulta.

**AGORA** — uma tela só. A fila. É o que abre.

**DECIDIR** — as quatro que mudam uma decisão de franqueadora neste mês:
Radar de Oportunidade · Quem sustenta, quem parou · Reputação rede contra
rede · Território vazio.

**CONSULTAR** — o acervo. Ninguém abre o portal para ver isto; abre para
conferir de onde veio um número da fila: Mapa da rede · Presença na busca ·
Auditoria de ficha · A escada dos achados · As praças medidas · O plano de
cada franqueado · Calendário da rede (apagado, e o motivo aparece) ·
Biblioteca de evidências.

Nada foi jogado fora. Doze ferramentas continuam lá. O que mudou é que agora
existe uma ordem, e ela responde à pergunta cara.

---

## 6 · O erro que a auditoria achou no caminho

Ao montar a fila, os números não fecharam, e o motivo era real.

**Dois coletores gravaram as mesmas avaliações com chaves de formatos
diferentes.** Um usava `local_id|<id>`; o outro, `google:<place_id>:<id>`. As
chaves nunca casaram, então a deduplicação não pegou nada:

- **981 linhas contadas em dobro**, 2,7% da base, em **10 clínicas**
- avaliações lidas: **25.652 → 25.030**

O que isso publicava de errado:

| | antes | corrigido |
|---|---|---|
| Souza Naves | 57,7/mês · 2º de 24 | **48,1/mês · 3º de 24** |
| Contagem | 50,3/mês · 3º de 15 | **38,7/mês · 4º de 15** |
| Mafra | 3,3/mês · 8º de 15 | **2,4/mês · 9º de 15** |
| banda do achado do atendimento | 53,8% a 71,4% | **53,8% a 72,0%** |

E derrubou um achado falso: a fila acusava *"ODONTO ART sustenta a 54,4/mês e
corre mais que Contagem"*. O ODONTO ART era uma das dez clínicas contadas em
dobro. Com a base limpa, o alerta some — Contagem não está sendo ultrapassada
por ele.

A correção está em um lugar só (`cruzamento.reviews_unicos()`), e o placar, a
fila e a classificação de temas passam por ele. **O achado principal não
mudou de degrau: segue 13 de 13, constante.**

---

## 7 · O que isso ainda não vê

- A rede tem 374 unidades. A fila mede **10**. É 2%.
- Nenhum contrato, lead, agendamento ou receita entra aqui. A fila diz onde a
  atenção está escorrendo, **não quanto isso custou**.
- O ciclo nasce vazio. Ele só vale a partir do segundo mês, quando houver o
  que comparar. Está escrito na própria tela.
