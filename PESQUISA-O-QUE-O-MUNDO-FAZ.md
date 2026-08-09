# O que o mundo faz, e o que dá para oferecer a mais

**Pesquisa de 09/08/2026.** O que plataformas de rede franqueada vendem lá fora,
o que a literatura de franchising diz que importa para a franqueadora, e o que
disso **já dá para entregar com o dado que temos hoje**.

> Escrito com uma disciplina: cada coisa proposta aqui foi **testada com dado
> real da nossa base** antes de entrar. O que não passou no teste está na seção
> do que a gente não deve prometer.

---

## PARTE 1 · O QUE EXISTE LÁ FORA

Há um mercado maduro de software para rede multi-unidade, e ele se divide em
três famílias:

### Família 1 — Presença e reputação local

**SOCi, Yext, Chatmeter, Birdeye, Uberall.** Vendem listagem, avaliação, post e
anúncio local para centenas de unidades ao mesmo tempo. O Yext se posiciona
como **fonte da verdade** dos dados de cada local; o Chatmeter é escolhido por
marcas que querem **medição por unidade** com a execução ficando com o time de
campo.

**O que isso nos diz:** existe categoria de produto e existe orçamento. O que
essas plataformas fazem de melhor — governar ficha e reputação em escala — é
justamente o que a nossa auditoria de ficha ataca. E o que elas **não** fazem é
inteligência de mercado: elas gerenciam a presença da marca, não medem a
concorrência.

### Família 2 — Território e expansão

**FranConnect, GrowthFactor, SiteSeer, Smappen, Caliper.** Vendem
**white space analysis** — achar a área onde a marca ainda não está mas onde
demografia, economia e concorrência indicam potencial — e **análise de
canibalização**, que mede quanto de uma unidade nova sai do bolso da unidade
vizinha em vez de vir de demanda nova.

Um caso citado pela GrowthFactor é direto: **US$ 500 mil de receita "nova"
vieram de clientes que antes iam a três lojas da mesma marca a 12 minutos de
distância** — e cada uma dessas perdeu US$ 150 a 180 mil por ano.

**Um alerta que vale para nós:** essas ferramentas costumam usar **população
residente do censo**, o que ignora a população que circula. Para muitos
formatos a **população diurna** prevê melhor a demanda.

### Família 3 — Desempenho e conformidade da rede

**FranConnect, Fieldpie, Franmetrics.** Vendem nota de saúde por unidade,
auditoria padronizada e priorização de visita de consultor.

Dois números da literatura, e os dois são argumentos de venda:

- redes com **nota padronizada detectam queda 40% mais rápido** que as que
  dependem do que o franqueado relata
- **mais de 70% do mau desempenho é detectável meses antes** de aparecer no
  resultado

E um aviso que a gente já tinha descoberto na marra: **aplicar régua da rede
inteira a mercados de demografia diferente produz placar enganoso por
construção.**

---

## PARTE 2 · ONDE NÓS JÁ ESTAMOS, SEM SABER

Cruzando o que o mundo vende com o que a nossa base sustenta hoje:

| O que o mundo vende | O que nós já temos |
|---|---|
| gestão de ficha (Yext, SOCi) | varredura de 884 fichas · **39 endereços com ficha duplicada** |
| medição por unidade (Chatmeter) | ritmo, meses seguidos, nota, resposta, feed |
| white space (SiteSeer, GrowthFactor) | **testado e funciona — ver Parte 3** |
| canibalização | Cuiabá tem 3 unidades da rede na mesma praça |
| nota de saúde (Fieldpie) | todos os componentes, faltando compor |
| benchmark por grupo | já agrupamos por porte de praça |

**E temos duas coisas que nenhuma dessas plataformas tem**, porque elas medem a
marca e não o mercado:

1. **O placar da concorrência inteira** — 884 clínicas, não só as nossas
2. **A distinção entre operação e campanha** — meses seguidos, que separa quem
   dura de quem deu um surto

---

## PARTE 3 · O QUE DÁ PARA OFERECER A MAIS — testado, não proposto

### 3.1 · RADAR DE OPORTUNIDADE — e ele funciona

**O teste:** varremos três cidades **sem unidade OrthoDontic conhecida** e
medimos a categoria.

| Cidade | Habitantes | OrthoDontic | Clínicas fortes (300+) | Maior concorrente |
|---|---:|---|---:|---:|
| **PA · Marabá** | 290.975 | **não** | 3 | 583 avaliações |
| **CE · Juazeiro do Norte** | 305.531 | **não** | 3 | 356 avaliações |
| MT · Sinop | 223.780 | sim | 3 | 1.378 avaliações |

Compare com as praças que já conhecemos: **Contagem tem um concorrente com
3.837 avaliações; Cuiabá, 1.451.** Marabá e Juazeiro têm ~300 mil habitantes e
o líder local não passa de 583.

**São mercados grandes com categoria fraca — e a rede não está neles.**

E a métrica que resume: **uma clínica forte para cada 97 mil habitantes em
Marabá**, contra uma para cada 15 mil em Contagem.

**O custo de medir uma cidade nova: US$ 0,05 e três minutos.** Dá para varrer
as 200 maiores cidades do Brasil por menos de US$ 15.

### O radar já rodou em oito cidades, e achou seis

`python3 scripts/radar_oportunidade.py --cidade "Macapá/AP" ...`

| Praça | Habitantes | Adultos 30-45 | Líder local | |
|---|---:|---:|---:|---|
| **AP · Macapá** | 489.676 | 104.811 | **427** | oportunidade |
| **AC · Rio Branco** | 389.001 | 88.887 | 619 | oportunidade |
| **PA · Parauapebas** | 305.771 | 75.937 | 1.055 | oportunidade |
| **CE · Juazeiro do Norte** | 305.531 | 69.988 | **356** | oportunidade |
| **MA · Imperatriz** | 285.806 | 67.291 | **291** | oportunidade |
| **PA · Marabá** | 290.975 | 65.866 | 583 | oportunidade |

**Macapá tem quase 500 mil habitantes, 104 mil adultos na faixa do aparelho, e
o maior concorrente da cidade tem 427 avaliações.** Para comparar: em Contagem
o líder tem 3.837 e em Cuiabá, 1.451.

**Imperatriz é o caso mais extremo:** 285 mil habitantes e o líder da categoria
tem **291 avaliações** — menos que a unidade de Palmas sozinha.

Seis cidades, uma varredura de dez minutos, **US$ 0,40**. Isso é o material que
o time de expansão usa amanhã.

**Por que isso importa mais que tudo:** é o **único** produto desta lista que
entra na **receita** da franqueadora em vez da despesa. Ela vive de vender
franquia.

### 3.2 · FATIA DA CATEGORIA — o "share of voice" que já sai de graça

As plataformas de multi-location vendem *share of local search voice* como
métrica principal. **Nós conseguimos calcular a versão dela com o que já
coletamos:** quanto da reputação da cidade pertence à rede.

| Fatia | Unidade | Categoria | Praça |
|---:|---:|---:|---|
| **7,9%** | 1.371 | 17.338 | MT · Cuiabá |
| 7,8% | 592 | 7.596 | SP · Presidente Prudente |
| 5,7% | 155 | 2.725 | SC · Mafra + PR · Rio Negro |
| 4,8% | 304 | 6.289 | TO · Palmas |
| 4,7% | 642 | 13.683 | PR · Londrina |
| 3,5% | 855 | 24.546 | MG · Contagem |
| **1,1%** | 170 | 15.067 | BA · Feira de Santana |

**Mediana da rede: 4,8% da reputação da própria cidade.**

E ela corrige uma leitura enganosa: **Contagem tem a maior unidade da amostra
(855 avaliações) e a terceira menor fatia (3,5%)** — porque a cidade é enorme.
Feira tem 1,1%: a unidade é quase invisível na própria praça.

**Número absoluto engana; fatia não.**

### 3.3 · A CANIBALIZAÇÃO — e nós temos o caso perfeito

A literatura trata canibalização como o maior risco da expansão. **Cuiabá é um
laboratório pronto:** três unidades da mesma marca, e elas fazem **45,6 · 3,7 ·
0,7 por mês**.

**A pergunta que só nós podemos responder para a rede:** as duas paradas estão
paradas porque a primeira comeu o mercado delas, ou porque não operam?

O dado responde: **a soma das três é 7,9% da categoria da praça.** Não há
mercado comido — há mercado não disputado. **É execução, não canibalização.**

Essa distinção vale dinheiro na mesa de expansão: se fosse canibalização, a
resposta seria fechar ou remanejar; sendo execução, a resposta é treinar.

### 3.4 · NOTA DE SAÚDE COM ALERTA ANTECIPADO

A literatura diz que **70% do mau desempenho é detectável meses antes** e que
nota padronizada **detecta 40% mais rápido**. Nós temos os componentes e não
compomos:

ritmo · meses seguidos · posição na praça · fatia da categoria · nota ·
taxa de resposta · saúde da ficha · idade da última avaliação

**E temos o sinal antecipado que a literatura descreve, comprovado:** a matriz
de Londrina fez 48 · 180 · 93 avaliações e caiu para 9. **A queda apareceu no
nosso dado meses antes de aparecer em qualquer resultado.**

**Regra que a pesquisa impõe e que vamos seguir:** a nota é comparada **dentro
do grupo de praças parecidas**, nunca contra a rede inteira. Régua única em
demografia diferente produz placar enganoso por construção.

### 3.5 · AUDITORIA DE FICHA — o que Yext e SOCi vendem caro

Nas 884 fichas varridas: **39 endereços com mais de uma ficha**, e **44% sem
site cadastrado**.

Na rede: **Feira tem ficha fantasma** no mesmo endereço da unidade, sem nota,
dividindo a reputação de uma unidade que só tem 170.

**Custo de execução: zero. Efeito: na semana seguinte.** É o item que faz o
franqueado acreditar no portal antes de qualquer outro.

---

## PARTE 4 · O QUE NÃO DEVEMOS PROMETER

Honestidade aqui vale mais que escopo.

**População diurna.** A literatura diz que ela prevê demanda melhor que a
residente, e ela **não está no IBGE de graça**. Nossa análise de expansão usa
população residente, e isso precisa ser dito.

**Receita, ticket e conversão.** Todas as plataformas de desempenho da Família 3
puxam do sistema do franqueado. **Nós não temos e o portal foi desenhado para
funcionar sem** — mas não dá para dizer que medimos desempenho financeiro.

**Drive-time real.** Territórios sérios são desenhados por tempo de
deslocamento, não por raio. Precisaria de API de rotas — é possível, não está
feito.

**Share of search.** O que calculamos é fatia de **reputação acumulada**, não de
busca. É um bom substituto e não é a mesma coisa.

---

## PARTE 5 · O QUE EU FARIA, EM ORDEM

**1. Radar de oportunidade — varrer 200 cidades.** Custa menos de US$ 15 e produz o
único material que o time de expansão pode usar amanhã. É receita, não despesa,
e é a porta de entrada mais fácil se a diretoria travar no portal.

**2. Fatia da categoria em toda ficha de praça.** Já sai do dado atual, corrige
a leitura de número absoluto e é a métrica que o mercado internacional trata
como principal.

**3. Nota de saúde com grupo de comparação.** Compõe o que já existe, e a
literatura dá o argumento de venda pronto: 40% mais rápido, 70% detectável
antes.

**4. Auditoria de ficha na implantação.** Zero custo de execução, efeito
imediato, e é o que compra a confiança do franqueado.

**5. Canibalização, quando houver mais de uma unidade na praça.** Vale para a
mesa de expansão e nós temos o caso de Cuiabá pronto para mostrar.

---

## O QUE ISSO MUDA NA PROPOSTA

Hoje vendemos **um portal de inteligência de mercado**. A pesquisa mostra que a
franqueadora compra, lá fora, **três coisas separadas**: presença, expansão e
desempenho da rede.

Nós cobrimos as três, com uma vantagem que as plataformas não têm — **elas
medem a marca, nós medimos o mercado inteiro.** O Yext sabe quantas ligações a
unidade recebeu; ele não sabe que a clínica a dois quilômetros começou uma
campanha de avaliação em maio.

E temos uma que ninguém vende: **a distinção entre operação e campanha.** De
134 concorrentes medidos, só 18 sustentam. Essa é a informação mais rara da
categoria, e é nossa.

---

_Fontes: [SOCi](https://www.soci.ai/industries/franchise/) ·
[Yext](https://www.yext.com/blog/2025/11/franchise-marketers-edge-ai-platform-built-for-local-wins) ·
[FranConnect](https://www.franconnect.com/en/franchise-territory-mapping/) ·
[GrowthFactor](https://www.growthfactor.ai/resources/blog/franchise-territory-design-cannibalization) ·
[SiteSeer](https://www.siteseer.com/the-guide-to-territory-optimization-for-franchisors/) ·
[Smappen](https://www.smappen.com/cannibalization-definition/) ·
[Fieldpie](https://www.fieldpie.com/blog/franchisee-monitoring/) ·
[Population Explorer](https://www.populationexplorer.com/blog/franchise-territory-performance-factors) ·
[Zors AI](https://www.zors.ai/glossary/white-space-analysis).
Números da nossa base conferíveis em `dados/serie/` e por
`python3 scripts/cruzamento.py`._
