# Como entrar numa cidade nova

**O processo, exato.** Escrito depois de oito praças — Riomafra, Londrina,
Feira, Prudente, Cuiabá, Palmas e Contagem — e corrigido por cada erro que
elas custaram.

> **A regra que organiza tudo: primeiro a cidade, depois a clínica.**
> Quem começa pela clínica só enxerga o que a clínica já sabe. A cidade
> explica a clínica; a clínica nunca explica a cidade.

**Tempo:** ~40 min de máquina + ~3,5h de gente · **Custo:** ~US$ 2 por praça

---

## O DESENHO

```
   ┌─────────────────────────────────────────────────────────────┐
   │  PARTE 1 · A CIDADE          (nada de clínica ainda)        │
   ├─────────────────────────────────────────────────────────────┤
   │  0  definir a praça ............... humano, 30 min          │
   │  1  a cidade em números ........... IBGE, grátis            │
   │  2  quem fala com a cidade ........ 9 canais + portais      │
   │  3  escutar a cidade .............. 800-1.400 vozes         │
   │  4  o público exato ............... quem decide e quem usa  │
   └───────────────────────────┬─────────────────────────────────┘
                               ▼
   ┌─────────────────────────────────────────────────────────────┐
   │  PARTE 2 · A CATEGORIA       (todo mundo, não os óbvios)    │
   ├─────────────────────────────────────────────────────────────┤
   │  5  varrer a categoria inteira .... ~135 clínicas           │
   │  6  ritmo e meses seguidos ........ quem corre, quem dura   │
   └───────────────────────────┬─────────────────────────────────┘
                               ▼
   ┌─────────────────────────────────────────────────────────────┐
   │  PARTE 3 · A CLÍNICA         (agora sim)                    │
   ├─────────────────────────────────────────────────────────────┤
   │  7  a unidade por dentro .......... feed, anúncio, resposta │
   │  8  a reclamação .................. a rede e as rivais      │
   │  9  a joia enterrada .............. imprensa + conversa     │
   └───────────────────────────┬─────────────────────────────────┘
                               ▼
   ┌─────────────────────────────────────────────────────────────┐
   │  PARTE 4 · A INTELIGÊNCIA    (sem isto, é dado parado)      │
   ├─────────────────────────────────────────────────────────────┤
   │ 10  o que não vamos ver ........... declarado, obrigatório  │
   │ 11  a inteligência ................ 8 leituras:             │
   │       11.1 o placar: ritmo E meses seguidos                 │
   │       11.2 o histograma de 12 meses ..... quem desligou     │
   │       11.3 mesma marca, mesma cidade .... controla tudo     │
   │       11.4 as hipóteses recalculadas                        │
   │       11.5 o que pesa contra ............ obrigatório       │
   │       11.6 a leitura dos textos ......... humano            │
   │       11.7 a resposta por eliminação .... humano            │
   │       11.8 o degrau na escada do achado                     │
   │ 12  o dossiê ...................... o que fica              │
   └─────────────────────────────────────────────────────────────┘
```

**O atalho:** `python3 coleta/entrar.py --cidade "Contagem/MG"` faz as etapas
1, 2, 3, 5, 6, 7 e as cinco primeiras leituras da 11, em 14 minutos. As
humanas — a 0, a 4, a 9, a 10, a 11.6, a 11.7 e a 12 — ele lista no fim.

**As duas leituras humanas da inteligência (11.6 e 11.7) foram as que deram os
achados mais fortes do projeto.** Não são opcionais e não são automatizáveis.

---

# PARTE 1 · A CIDADE

## ETAPA 0 · Definir a praça — 30 min, humano

**A praça não é o município. É o raio real de onde vem o paciente.**

Riomafra ensinou do jeito difícil: Mafra/SC e Rio Negro/PR são **uma cidade
partida pela divisa dos estados** — mesmo DDD, ônibus urbano cruzando a ponte,
mídia local que se chama "Riomafra". Tratar como duas era erro de forasteiro.

Cuiabá repetiu: conurbada com Várzea Grande, 1.010.797 habitantes somados.

E o oposto também vale. **Londrina tem uma Zona Norte de 108 mil habitantes sem
unidade dentro.** Uma cidade pode ser praças diferentes.

Contagem é o caso do meio: dentro da região metropolitana de BH, mas com
imprensa, prefeitura e identidade próprias. **Tratar como bairro de BH seria
errado; tratar como isolada também.**

Quatro perguntas fecham:
- tem cidade grudada do outro lado de rio, divisa ou rodovia?
- o ônibus urbano sai do município?
- a mídia local cobre as duas?
- o paciente atravessa para se tratar?

> ⚠ **Cidade homônima.** Existe Palmas no TO e no PR. Existe Palmas de Monte
> Alto na BA. **Sempre escreva a UF** — e a coleta já entrou contaminada por
> isso uma vez.

**Sai:** `praca_id`, lista de cidades com UF, e uma linha explicando por quê.

---

## ETAPA 1 · A cidade em números — automático, grátis

```bash
python3 coleta/descobrir_praca.py --cidade "Contagem/MG"
python3 coleta/descobrir_praca.py --cidade "Mafra/SC" --mais "Rio Negro/PR" --id riomafra
```

Traz do IBGE:

| O quê | De onde | Por que importa |
|---|---|---|
| população estimada | agregado 6579 | o tamanho do mercado |
| censo 2022 | agregado 4709 | a base confiável |
| massa salarial | agregado 5938 | quanto a cidade ganha |
| **população por faixa de idade** | **agregado 9514** | **o alvo real** |

**O número que muda a estratégia é o último.** São dois públicos e eles não se
parecem:

| Praça | 9-15 anos | 30-45 anos | O adulto é |
|---|---:|---:|---:|
| Contagem | 52.795 | 155.079 | **2,9× maior** |
| Palmas | 32.089 | 78.759 | 2,5× maior |
| Riomafra | ~7.700 | ~21.000 | 2,7× maior |

**Em todas as praças o adulto é 2,5 a 3 vezes maior — e é o menos falado.**
A comunicação da rede mira o adolescente; o mercado é do adulto.

**Também traz:** os veículos de imprensa que cobrem a cidade, pelo Google News.

> ⚠ **O IBGE derruba chamada em rajada.** O script tenta 3 vezes e, se não
> vier, escreve `⚠ não veio` em vez de deixar em branco. **Número que some
> calado vira conclusão errada sobre a cidade.**

> ⚠ **`--sobrescrever` preserva as clínicas já ancoradas.** Ele refaz os
> números, não apaga o trabalho. Aprendido depois de apagar 14 locais de
> Palmas rodando só para atualizar a idade.

---

## ETAPA 2 · Quem fala com a cidade — automático + 1h de conferência

```bash
python3 coleta/coletores/canais.py --praca contagem
python3 coleta/coletores/imprensa_rss.py --praca contagem
```

São **nove tipos de canal**, e cada um responde uma pergunta diferente:

| # | Tipo | O que entrega |
|---|---|---|
| 1 | **A voz da cidade** | como a cidade fala, o que a move |
| 2 | **A imprensa local** | a notícia, e a joia enterrada |
| 3 | **A mãe** | **É ELA QUEM DECIDE O APARELHO** |
| 4 | **O preço / achadinho** | como a cidade fala de dinheiro |
| 5 | **O humor** | o que viraliza, a língua solta |
| 6 | **O jovem** | o público de 15-25 |
| 7 | **A gastronomia** | onde a indicação converte |
| 8 | **A prefeitura** | onde o cidadão reclama e celebra |
| 9 | **O esporte de base** | **O PÚBLICO DE 9-15 COM OS PAIS JUNTO** |

### Os três achados que essa etapa já deu

**O canal da mãe existe em 1 de 7 praças.** Só Feira tem (@sambademaes,
31.606). Riomafra, Londrina, Prudente, Cuiabá, Palmas e Contagem não têm
nenhuma voz materna de escala. **É a maior brecha que este projeto encontrou**,
e como se repete em praças que não têm nada a ver entre si, é decisão de
franqueadora.

**O esporte de base existe em quase todas, e nenhuma unidade aparece nele.**
Em Contagem a escola de futsal é **da prefeitura** — parceria pública, custo
baixo. Dois dos maiores são futsal feminino, que é onde o aparelho é mais
procurado.

**O canal que NÃO existe é informação.** Território vazio: quem chegar primeiro
fala sozinho. Anote sempre.

### ⚠ A armadilha que custou mais caro aqui

**A busca do Instagram casa por pedaço de palavra e devolve o mundo inteiro.**

| O que entrou | O que era |
|---|---|
| @giopalmas82, 1,8M seguidores | italiana de cosméticos, "Palmas" é sobrenome |
| @maestrapizza | pizzaria — "maes" casou dentro de "maestra" |
| @louiseposoperatorio | pós-operatório de plástica, entrou como "mãe" |
| @prefeitura.pma | Palmas de Monte Alto, **Bahia** |
| @prefeituradepalmas_pr | Palmas do **Paraná** |

**31% do levantamento de Palmas era lixo. E lixo com número grande parece dado
bom.** O coletor hoje tem três travas: o perfil precisa se identificar com a
cidade, precisa ter palavra do próprio assunto na bio, e a UF desempata cidade
homônima.

**Mesmo assim, confira à mão.** É 1h de trabalho e é onde o método ganha ou
perde.

---

## ETAPA 3 · Escutar a cidade — automático, ~US$ 0,35

```bash
python3 coleta/coletores/escutar_cidade.py --praca contagem --posts 80
python3 scripts/classificar.py
```

**Mapear quem fala não é escutar.** São coisas diferentes, e a segunda é a que
entrega o produto.

**Meta: 800 a 1.400 vozes.** Foi o que as praças renderam.

O que sai daqui e não sai de nenhuma outra fonte:
- **as palavras da cidade** — como ela fala, não como a gente escreve
- **onde ela reage** — em Palmas, imprensa (184 curtidas medianas) e prefeitura
  (171); preço é o mais fraco (7). Em Contagem, a voz da cidade **é uma página
  de memes** com 164 mil seguidores
- **o que nunca dizer** — o "axé litorâneo" que soaria falso em Feira, a gíria
  gaúcha que queimaria em Riomafra

> A escuta é o único jeito de auditar a etapa 2. Foi lendo as palavras — 
> "maestra", "pizza", "cirurgiaplastica" — que os canais falsos apareceram.

---

## ETAPA 4 · O público exato — 30 min, humano

Junte a etapa 1 com a etapa 3 e escreva, em uma página:

1. **Quantos são** os dois alvos (9-15 e 30-45), em número absoluto
2. **Quem decide** — é a mãe, e o canal dela provavelmente não existe
3. **Como a cidade fala** — as palavras que apareceram na escuta
4. **Onde ela presta atenção** — o tipo de canal com mais engajamento
5. **O que nunca dizer** — o registro que soaria falso ali

**E o contexto que só a imprensa dá.** Em Contagem, dois episódios graves na
categoria: um homem morreu durante tratamento de canal (cobertura nacional) e
um dentista foi preso suspeito de abusar de **uma adolescente** — que é
exatamente a paciente de aparelho, e cuja mãe leu a notícia.

**Numa praça assim, comunicação de preço e volume soa pior que em qualquer
outra.** Nenhum número mostraria isso.

---

# PARTE 2 · A CATEGORIA

## ETAPA 5 · Varrer a categoria inteira — automático, ~US$ 0,05

```bash
python3 coleta/coletores/google_places.py --praca contagem
```

Seis termos de busca por cidade, três páginas cada. Devolve **~135 clínicas**
por praça, com nota, volume, site, telefone e `place_id`.

### Por que varrer em vez de listar

**Este é o erro que mais custou ao projeto.** As quatro primeiras praças foram
montadas com 3 a 5 concorrentes escolhidos a mão. Quando varremos:

| Praça | Na lista | Reais | Posição no estudo | Posição real |
|---|---:|---:|---:|---:|
| Riomafra | 5 | 87 | 2ª | **7ª** |
| Feira | 3 | 144 | 2ª | **20ª** |
| Londrina | 3 | 151 | 1ª | **5ª** |
| Prudente | 5 | 121 | 2ª | **3ª** |

**Em quatro de cinco a unidade estava pior do que dissemos, e o erro tem sempre
a mesma direção:** a lista feita a mão pega a rede rival conhecida e perde o
consultório grande sem marca nacional — que é justamente quem lidera.

> **Amostra de conveniência não erra pouco. Erra de sinal.** No mesmo dia, o
> mesmo cálculo deu +0,49 e −0,62 conforme quem estava na lista.

### ⚠ Duas travas do varredor

**Filtro de cidade.** Buscar "Várzea Grande" trouxe uma unidade de "Várzea
Paulista/SP" para dentro de Cuiabá. Casa pela última palavra do nome mais a UF
— porque o Google abrevia "Presidente Prudente" como "Pres. Prudente", e
exigir o nome inteiro **zerou a praça de Prudente sem avisar**.

**A unidade da rede é reconhecida pelo SITE, não pelo nome.** "You Align
Orthodontics", em Contagem, entrou como se fosse da rede porque "orthodontics"
contém "orthodontic". Hoje confere `orthodonticbrasil.com.br`, que é exato.

**A varredura também ancora**: escreve as maiores clínicas na identidade da
praça. Sem isso o coletor de avaliação devolve zero locais.

---

## ETAPA 6 · Ritmo e meses seguidos — automático, ~US$ 0,60

```bash
python3 coleta/coletores/google_reviews.py --praca contagem --max-reviews 150
# e para o histograma de 12 meses dos líderes:
python3 coleta/coletores/google_reviews.py --praca contagem --max-reviews 500
```

**Duas medidas, e a segunda é a que quase ninguém tem.**

**RITMO** responde *quanto*. **MESES SEGUIDOS** responde *há quanto tempo* — e
é o segundo que diz se dá para copiar. **Campanha não se copia; operação sim.**

De 130 clínicas medidas, **só quatro sustentam volume alto mês após mês.**
Todo o resto liga, brilha três meses e desliga:

| Clínica | Últimos meses | |
|---|---|---|
| ★ OrthoDontic Cuiabá | 65·48·43·43·44·34·55·48·45·37·40·46·46 | **operação** |
| ★ OrthoDontic Contagem | 82·29·73·57·33·36·32·31·12·29·30·32·24 | **operação** |
| Odontologia Prado | 1·1·1·1·2·1·**33·70·57·44·60** | ligou em março |
| Vitae Center (Contagem) | nada · nada · **87·180·196·37** | ligou em maio |
| Clínica Goya | 41·64·72·86·90·74·47·83·35·**4·2·1·1** | morreu em abril |
| ★ OrthoDontic Londrina | 18·7·6·**48·180·93**·35·9 | **fez e desligou** |

### ⚠ Três armadilhas de medição, todas já cometidas

**1. O teto da amostra.** A conta ingênua (total ÷ 12) deu 12,5/mês para cinco
clínicas ao mesmo tempo — era o limite da coleta, não o ritmo. O real era 45,6.

**2. Duas medidas discordam.** O contador do Google entre duas coletas é
observação direta; o intervalo da amostra é estimativa. Só concordam quando a
clínica é rápida de verdade. Na matriz de Londrina a amostra dizia 51,7/mês e
o contador subiu 3 em 23 dias. **O contador manda.**

**3. Amostra curta não vira taxa.** 100 avaliações em 5 dias não são 608/mês —
são "está em campanha e não sabemos o ritmo".

O `inteligencia.py` marca as três sozinho: `~estimado`, `⚠ amostra de Nd` e
`⚡ RAJADA`.

---

# PARTE 3 · A CLÍNICA

## ETAPA 7 · A unidade por dentro — automático, ~US$ 0,50

```bash
python3 coleta/coletores/meta_ads.py --praca contagem
python3 coleta/coletores/instagram.py --praca contagem
python3 coleta/coletores/google_ads.py --praca contagem
```

**As cinco perguntas:**

1. **A unidade anuncia?** Em que plataforma, com que texto, há quantos dias.
   Ausência é resposta — e ausência **no pico da temporada** é alerta.
2. **O feed fala de aparelho?** Conta os posts. Não confie em olhar o perfil.
3. **A unidade responde avaliação?**
4. **Tem rosto?** Quantos posts mostram gente.
5. **Quanto engaja?** Mediana de curtidas.

### O achado que isso já deu, e é grande

**A unidade de Cuiabá faz 43,8 avaliações/mês há treze meses. O Instagram dela
tem mediana de UMA curtida.** E ela passou de janeiro a abril quase sem postar
— enquanto as avaliações continuavam entrando a 45/mês.

Contagem repete: 15 posts, mediana de 8 curtidas.

**Nas duas praças a máquina roda com o feed parado.** Somando: não vem do
Instagram, não vem de anúncio (nenhuma das duas anuncia), não vem de responder
avaliação (as duas respondem 0%), e nenhuma palavra separa o texto das
avaliações delas das unidades que perdem.

**Sobra o balcão.** A campeã tem mediana de 22 caracteres por avaliação e 72%
com até 40 — *"Ótimo atendimento 😍😍"*. É avaliação pedida na hora.

**Isso é a melhor notícia possível para a rede:** o que funciona não custa
verba, não depende de agência e não some quando o orçamento aperta. É
procedimento, e procedimento se treina em 340 unidades.

---

## ETAPA 8 · A reclamação — automático, ~US$ 1

```bash
python3 coleta/coletores/reclame_aqui.py --empresa orthodontic \
    --tambem orthopride --tambem odontocompany --n 20
```

**Sem concorrente, o número não quer dizer nada.** 3.133 reclamações é muito ou
pouco para uma rede de 340 unidades? Só se sabe comparando:

| Rede | Total | Respondidas | Resolvidas | Voltaria | Selo |
|---|---:|---:|---:|---:|---|
| OdontoCompany | 23.283 | 67,7% | 38,5% | 21,1% | **NÃO RECOMENDADA** |
| Sorridents | 11.425 | 45% | 31,8% | 19,2% | **NÃO RECOMENDADA** |
| Orthopride | 6.670 | 100% | 88,5% | 59,8% | GREAT |
| **OrthoDontic** | **3.133** | **98,6%** | **86,4%** | **63,3%** | **GREAT** |
| Odontoclinic | 2.457 | 91,5% | 96,3% | 76,6% | RA1000 |

**Sempre colete as rivais da praça junto.** Em Contagem apareceu que a Oral
Unic acabou de inaugurar já **não recomendada** — 34 reclamações, nenhuma
respondida.

> ⚠ **Esta etapa já produziu o pior erro do projeto.** O actor antigo devolvia
> sempre 3 reclamações de 3.133, e com essas 3 escrevemos *"a marca não
> responde"* — que virou alerta CRÍTICO no prompt do portal, pronto para ir à
> diretoria. **Era falso.** Amostra de três não descreve uma rede de 340.

---

## ETAPA 9 · A joia enterrada — 1h, humano + imprensa

**O ativo local que ninguém copia — e que quase sempre está escondido.**

| Praça | A joia |
|---|---|
| Londrina | **é a matriz** da rede |
| Prudente | foi a **primeira franquia** |
| Riomafra | **o casal de ortodontistas que voltou pra casa** |
| Contagem | a voz da cidade é uma **página de memes** de 164 mil |
| Feira, Palmas, Contagem | **a unidade não tem nenhuma** |

**Não ter também é informação** — muda a estratégia de "desenterrar" para
"construir".

Onde procurar: a imprensa local (o coletor já traz), o registro público de
empresa, o "sobre" da unidade, e **a conversa com o franqueado** — a fonte mais
barata e a mais pulada.

**E procure a joia do concorrente.** Em Feira, o líder começou dentro de uma
grande franquia e depois personalizou tudo no próprio nome. Isso explica o
placar inteiro.

---

## ETAPA 10 · O que não vamos ver — 30 min, obrigatório

**A coleta só enxerga o que fica público na internet.** Antes de concluir
qualquer coisa, registre o que ficou de fora:

rádio · TV local · outdoor e panfleto · patrocínio de time e evento · parceria
com escola e convênio · **indicação boca a boca**, que os estudos apontam como
*o* canal de decisão.

**A pergunta que resolve metade disso, e é uma só:**

> **"O que vocês fazem de mídia que não está na internet?"**

Sem isso, a gente escreve "a unidade está muda" sobre uma clínica que pode
estar no rádio da cidade toda semana. Em Riomafra o rádio é canal forte — três
emissoras, uma da paróquia — e a unidade patrocina os escoteiros.

**Sai:** `dados/serie/midia_offline.jsonl` preenchido, com status
`nao_medido` / `parcialmente_conhecido` / `declarado`.

---

## ETAPA 11 · A INTELIGÊNCIA — automático + humano, e nunca opcional

```bash
python3 scripts/inteligencia.py --praca contagem
python3 scripts/inteligencia.py --todas      # para ver o que a praça nova mudou
```

**Coleta sem inteligência é dado parado.** Nenhuma praça vira dossiê sem passar
por aqui, e não é etapa que se faz quando sobra tempo.

São **sete leituras**. As cinco primeiras o script faz sozinho; as duas últimas
são humanas e é onde estão os achados que mais valeram.

---

### 11.1 · O placar pelo ritmo — e pelos meses seguidos

Duas colunas, e a segunda é a que quase ninguém tem:

```
 ritmo  meses  total  nota  resp  clínica
  250.1     3   3837   4.4   35%   Vitae Center            ⚡ RAJADA
   54.4    12   1727   4.8    0%   Odonto Art 24 Horas
   50.3    13    855   4.6    0% ★ OrthoDontic
```

O script marca sozinho quatro coisas que já enganaram a gente:

| Marca | Quer dizer |
|---|---|
| `~estimado` | só há uma coleta; o número vem do intervalo da amostra |
| `⚠ amostra dizia N` | o contador do Google e a amostra discordam — vale o contador |
| `⚠ amostra de Nd` | intervalo curto demais para virar taxa mensal |
| `⚡ RAJADA` | um único mês concentra 60% ou mais |
| `N+` | a amostra encheu antes de alcançar o passado: é piso, não medida |

**Leia nesta ordem:**

1. **Quem lidera em VOLUME**, não em nota. Nota alta com volume baixo é o
   padrão da rede — e é o problema, não a virtude.
2. **Quem lidera em RITMO.**
3. **Quem lidera em MESES SEGUIDOS.** Quase nunca é o mesmo dos dois primeiros.
4. **Que tipo de concorrente é cada um** — rede popular, clínica geral bem
   avaliada, **doutor com nome próprio**, clínica-escola, startup de tráfego
   pago, especialista de nicho. Muda tudo o que vem depois.
5. **A clínica-escola** — ela quase nunca faz aparelho de adolescente e adulto.
   É a brecha que apareceu em todas as praças.

---

### 11.2 · O histograma de doze meses — a leitura que decide

**O número de ritmo sozinho não distingue operação de campanha.** Só o mês a
mês distingue, e é onde estão os três achados mais fortes do projeto:

```
★ OrthoDontic Cuiabá    65 48 43 43 44 34 55 48 45 37 40 46 46   MÁQUINA
  Odontologia Prado      1  1  1  1  2  1 33 70 57 44 60         ligou em março
  Clínica Goya          41 64 72 86 90 74 47 83 35  4  2  1  1   morreu em abril
★ OrthoDontic Londrina  18  7  6 48 180 93 35  9                 FEZ E DESLIGOU
```

**Três perguntas, sempre:**

- **quem sustenta?** dez meses ou mais com movimento
- **quem acabou de ligar?** os líderes de hoje costumam ter três a cinco meses
- **quem desligou?** é o achado mais valioso, porque é o mais fácil de resolver

A matriz de Londrina saiu de ~170 para 566 avaliações em seis meses — a maior
campanha da cidade — **e desligou**. Ninguém percebeu, porque ninguém media.
A conversa que sai disso é outra: não é *"você vai mal"*, é ***"você fez melhor
que todo mundo. Por que parou?"***

---

### 11.3 · Mesma marca, mesma cidade — quando existe, é a leitura mais forte

Quando a praça tem mais de uma unidade da rede, **mercado, preço, marca e
concorrência ficam controlados de graça.** O que sobra é a unidade.

Em Cuiabá: **45,6 · 3,7 · 0,7 por mês.** Sessenta e cinco vezes de diferença.

E 0,7 é exatamente o número de Riomafra — que a gente tinha atribuído à cidade
pequena. Numa capital de um milhão, a mesma marca produz o mesmo 0,7.
**0,7 é o que uma unidade produz quando não faz nada. Não é característica de
praça.**

Sempre procure outra unidade da rede na praça. A busca custa nada.

---

### 11.4 · As hipóteses, recalculadas

O script recalcula, com o dado novo, os padrões que o projeto já levantou:

```
responder avaliação faz crescer      r = +0.54  → separa um pouco
nota alta acompanha ritmo            r = +0.74  → separa bem
avaliação curta acompanha ritmo      r = -0.25  → quase não separa
```

Ele traduz o coeficiente para português, porque ninguém na diretoria lê `r`.

**Uma praça nova pode matar um padrão antigo, e isso é resultado, não
problema.** Mas atenção ao que já aconteceu: com a lista de concorrentes feita
a mão, "responder avaliação faz crescer" dava **negativo em quatro de cinco
praças**. Com a varredura completa, **inverteu para positivo em quatro de
cinco**.

> **Amostra de conveniência não erra pouco. Erra de sinal.**

---

### 11.5 · O que pesa contra

O script procura o contraexemplo de cada achado e imprime junto:

```
· Sorrize tem 70% de avaliação curta e ritmo 4,9 — curta não produz ritmo sozinha
· OrthoDontic Centro Norte lidera em ritmo respondendo 0% das avaliações
· Open Odonto responde 95% e faz só 6,6/mês
```

**Achado sem contraexemplo procurado não é achado, é torcida.**

E se ele não encontrar nenhum contraexemplo, isso é motivo de desconfiança —
não de comemoração.

Ele também avisa duas coisas que já corromperam placar:

- **dois registros apontando para o mesmo lugar** — em Feira, Moisés Suzart
  estava contado duas vezes e o placar somava duplicado, calado
- **praça sem canais offline declarados** — sem isso, "a unidade está parada"
  pode ser mentira sobre uma clínica que está no rádio toda semana

---

### 11.6 · A leitura dos textos — humano, e é onde estava a resposta

**O script conta assunto. Ele não lê.** E foi lendo que apareceu o achado
principal do projeto.

Três coisas para fazer à mão, comparando a unidade que vai bem com as que vão
mal na mesma praça:

**Procure a palavra que separa.** Em Cuiabá, procuramos termos que aparecessem
muito mais nas avaliações da campeã. **Não existe nenhum.** O paciente descreve
exatamente a mesma coisa nas três unidades. **A diferença não está na
experiência.**

**Olhe a FORMA, não o conteúdo.** A campeã tem mediana de **22 caracteres** por
avaliação e 72% com até 40 — *"Ótimo atendimento 😍😍"*. Isso é assinatura de
avaliação **pedida na hora**, no balcão. A que perde tem 126 caracteres, com
elogio detalhado e reclamação de espera: avaliação espontânea.

**Conte quem é citado pelo nome.** Zero por cento na campeã. Se ninguém é
citado, a relação não é com uma pessoa.

---

### 11.7 · A resposta por eliminação — humano

**Quando uma unidade vai muito melhor que as outras, descubra de onde isso vem
riscando as fontes uma a uma.** Foi assim que a pergunta mais cara do projeto
foi respondida:

| Fonte | O que achamos |
|---|---|
| Instagram | mediana de **1 curtida**, e ficou 4 meses sem postar enquanto as avaliações continuavam a 45/mês |
| Anúncio no Meta | **nenhum** — nem ela, nem as concorrentes de Cuiabá |
| Anúncio no Google | **zero** em todo o Brasil, em 4 variantes de nome |
| Responder avaliação | **0%**, igual às que perdem |
| Texto das avaliações | **nenhuma palavra** separa das que perdem |

**Sobrou o balcão.**

E essa é a melhor notícia possível para a rede: **o que funciona não custa
verba, não depende de agência, não precisa de aprovação de mídia e não some
quando o orçamento aperta. É procedimento** — e procedimento se escreve, se
treina e se cobra em 340 unidades.

**O que pesa contra, e precisa ser dito junto:** avaliação curta sozinha não
produz ritmo (a Sorrize tem 70% de curtas e faz 4,9/mês). Então isto é **sinal
forte, não prova** — e a prova custa uma visita e uma pergunta: *quem pede a
avaliação, em que momento, com que frase?*

---

### 11.8 · Onde o achado entra na escada

Todo achado sai da inteligência com um degrau declarado:

| Degrau | Quer dizer |
|---|---|
| **SINAL ISOLADO** | vimos em 1 ou 2 praças |
| **SE REPETE** | vimos em 3 ou mais |
| **VALE PARA A REDE** | vimos em praças bem diferentes entre si |
| **VIROU REGRA** | a rede decidiu agir com base nisso |
| **❌ CAIU** | uma praça mostrou o contrário |

**Exemplo de promoção:** *"a rede não é a mais rápida, é a mais constante"*
nasceu SINAL ISOLADO em Cuiabá, virou SE REPETE com Palmas e Contagem — três
regiões diferentes.

**Exemplo de queda e ressurreição:** *"responder avaliação faz crescer"* foi
dado como ❌ CAIU com a amostra errada, e voltou a SE REPETE quando a amostra
ficou completa. **Registre as duas coisas.** Um método que só guarda os
acertos não é método.

---

### O QUE A INTELIGÊNCIA PRECISA DEVOLVER, SEMPRE

- [ ] o placar com ritmo **e** meses seguidos
- [ ] o histograma de 12 meses da unidade e do líder
- [ ] quem sustenta, quem ligou agora, **quem desligou**
- [ ] a comparação entre unidades da mesma rede, se houver
- [ ] as hipóteses recalculadas, em português
- [ ] **o contraexemplo de cada achado**
- [ ] a leitura dos textos: a palavra que separa, a forma, quem é citado
- [ ] o degrau de cada achado na escada
- [ ] o que a coleta não viu

## ETAPA 12 · O dossiê

Um arquivo em `pesquisas/_dossies/DOSSIE-NN-<praca>.md`, com:

a frase da praça · por que esta cidade · a praça em números · o placar e por
que o primeiro lugar engana · o contexto que nenhum número mostraria · quem
fala com a cidade · a reclamação comparada · o feed da unidade · a joia · o que
não estamos vendo · o que fazer, em ordem.

---

# O CHECKLIST DE ENTREGA

Uma praça só está pronta quando tem:

- [ ] a praça definida, com a justificativa do raio **e a UF escrita**
- [ ] população, renda e **o tamanho dos dois alvos** (9-15 e 30-45)
- [ ] 8 a 14 canais mapeados, com o tipo de cada um, **conferidos à mão**
- [ ] **os canais que NÃO existem, anotados**
- [ ] 800+ vozes coletadas e separadas por assunto
- [ ] como a cidade fala + **o que nunca dizer**
- [ ] a categoria varrida inteira, não uma lista escolhida
- [ ] o placar com **ritmo e meses seguidos**
- [ ] o tipo de cada concorrente preenchido
- [ ] a clínica-escola verificada
- [ ] a unidade por dentro: anúncio, feed, resposta, rosto, engajamento
- [ ] a reclamação **comparada com as rivais**
- [ ] a joia enterrada — ou a declaração de que não tem
- [ ] o calendário: férias escolares do estado + festas da cidade
- [ ] **o que não estamos vendo, declarado**
- [ ] `inteligencia.py` rodado — **as 8 leituras, não só as 5 automáticas**
- [ ] o dossiê escrito
- [ ] ponto de partida congelado com data, para a próxima coleta comparar

---

# COMO ESCOLHER A PRÓXIMA CIDADE

Não é por tamanho nem por quem gritou mais alto. É por **o que falta na
amostra** — cada praça nova precisa ensinar algo que as outras não ensinam.

Onde estamos, com 7 praças de 340:

| Região | Praças |
|---|---|
| Sul | 2 (Londrina, Riomafra) |
| Sudeste | 2 (Prudente, Contagem) |
| Centro-Oeste | 1 (Cuiabá) |
| Norte | 1 (Palmas) |
| Nordeste | 1 (Feira) |

**O que ainda falta ensinar:**

- **unidade de safra recente** — a mais nova da amostra tem 7 anos
- **capital do Nordeste** — só temos interior baiano
- **unidade que está indo mal numa praça grande** — as duas metropolitanas que
  temos estão bem
- **praça com duas unidades brigando entre si** — Cuiabá tem três, mas uma só
  domina

**Uma praça que preenche um buraco vale mais que três parecidas com as que já
temos** — porque é ela que diz se os padrões valem para a rede ou só para o
pedaço que já olhamos.

---

# AS ARMADILHAS, EM UMA PÁGINA

Cada uma custou alguma coisa de verdade.

| Onde | O que aconteceu | Como se defende hoje |
|---|---|---|
| Definir a praça | Palmas/TO virou Palmas/PR | sempre escrever a UF |
| IBGE | rede caiu e o número sumiu calado | 3 tentativas, e avisa quando falta |
| Canais | 31% do levantamento era lixo | 3 travas + conferência humana |
| Varredura | Várzea Paulista/SP entrou em Cuiabá | filtro de cidade + UF |
| Varredura | "You Align Orthodontics" virou unidade da rede | confere pelo site |
| Ritmo | teto da amostra virou ritmo | contador do Google manda |
| Ritmo | 100 avaliações em 5 dias viraram 608/mês | marca amostra curta |
| Reclamação | 3 de 3.133 viraram "a marca não responde" | actor novo + comparação |
| Lista de concorrentes | 4 de 5 praças com posição errada | varrer, nunca listar |
| Coletores | praça nova devolvia zero, calada | tudo lê da identidade |
| `--sobrescrever` | apagou 14 locais ancorados | preserva o que tem place_id |

> **A lição que resume todas:** amostra de conveniência não erra pouco, **erra
> de sinal**. E o erro chega à diretoria com a mesma cara de confiança que o
> acerto.

---

_Processo escrito em 08/08/2026, depois de sete praças. Cada praça nova
encontra um defeito que as antigas escondiam — o que é argumento para entrar
em mais cidades, não em menos._
