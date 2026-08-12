# Auditoria estratégica e arquitetura recomendada

Escrito em 12/ago/2026, com o disco na mão. Todo número aqui foi contado
do repositório, não lembrado. Onde eu não sei, está escrito que não sei.

Este documento é canônico para **o que existe hoje e para onde vai**.
Quando ele divergir de qualquer `.md` da raiz, ele vence — os outros são
histórico (ver §4, redundâncias).

---

## 1 · MAPA DO PRODUTO ATUAL

### O que existe, contado

| camada | quantidade | onde |
|---|---|---|
| coletores | **17** | `coleta/coletores/` |
| scripts de inteligência e build | **30** | `scripts/` |
| séries medidas (append-only) | **25 arquivos, 84.049 linhas** | `dados/serie/` |
| arquivos de payload | **22 + 5 pastas** | `dados/portal/` |
| praças da rede estudadas | **7** | `dados/identidade/` |
| cidades de oportunidade estudadas | **6** | idem, `sem_unidade: true` |
| lojas com estudo | **10** (`local_id`) | `dados/portal/clinicas/` |
| unidades na lista oficial | **374**, em **304 cidades**, **23 UFs** | `dados/serie/rede_fichas.jsonl` |
| telas do portal | **7** no menu | casco (Claude Design) |

### A cobertura real, sem maquiagem

**10 de 374 unidades têm estudo — 2,7% da rede.** As outras 364 aparecem
no índice como não escutadas, o que está certo. Mas toda frase que
comece com "a rede…" hoje se apoia em 10 lojas, e o portal precisa
continuar dizendo isso em cada tela onde a palavra "rede" aparecer.

Das 374 linhas oficiais, **326 foram confirmadas com `place_id`** e 48
não. Três lojas nossas caem entre as não confirmadas (as duas de Cuiabá
e Prudente).

### O maior ativo já construído

Não é o portal. É a **base de 39.771 avaliações** (26.332 já
classificadas por tema) e as **1.254 portas de busca testadas**. Isso é
o que nenhum concorrente tem de graça, e é o que sustenta as leituras.

---

## 2 · MAPA DAS FONTES — fonte → dado → série → inteligência → tela → decisão

| fonte | coletor | série (linhas) | inteligência | payload | decisão que muda |
|---|---|---|---|---|---|
| site da rede | `unidades_da_rede` | `unidades_rede` (748) | `a_rede_inteira` | `rede_inteira`, `clinicas_indice` | onde a rede está / não está — base de tudo |
| Google Places | `ponta`, `google_places` | `places` (468), `categoria` (1.695) | `cruzamento`, `fila` | `fila`, `clinicas/*` | qual unidade tratar primeiro |
| Google avaliações | `google_reviews` | `reviews` (39.771) | `classificar`, `inteligencia` | `temas`, `voz_da_cidade` | o que o paciente reclama |
| Google — buscas | `portas` | `portas` (1.254) | `onde_cada_loja_aparece` | `presenca_por_loja` | onde a loja não aparece |
| ficha pública das 374 | `rede_inteira` | `rede_fichas` (374) | `a_rede_inteira` | `rede_inteira` | alerta de ficha, cobertura |
| Meta Ads Library | `meta_ads` | `anuncios` (735) | `quem_anuncia_aparelho` | `anuncios` | quem compra mídia de aparelho |
| Google Ads Transparency | `google_ads` | `anuncios` | idem | idem | idem |
| Instagram | `instagram`, `comentarios` | `posts` (3.376), `comentarios` (1.380) | `a_voz_da_cidade` | `voz_da_cidade` | o que a cidade fala fora do Google |
| imprensa (RSS) | `imprensa_rss` | `imprensa` (644) | `pontos_cegos` | contagem em 5 payloads | **quase nenhuma — ver §5** |
| Reclame Aqui | `reclame_aqui` | `reclamacoes` (189) | — | `franqueadora` | reputação da marca |
| IBGE | `ibge_nacional` | `ibge_municipios` (5.571) | `funil_nacional` | `funil_nacional` | onde abrir a próxima |
| Google Trends | `sazonalidade` | veredito | — | `sazonalidade` | **nenhuma — medido e negado** |

**Frescor:** 21 das 25 séries foram medidas entre 9 e 11/ago. Quatro
estão paradas: `descida_nacional` (16/jul), `funil` (15/jul),
`sazonalidade` (15/jul, superada pelo veredito) e `regua` (sem data).

---

## 3 · MAPA DAS FUNCIONALIDADES, pelos três motores

### A · NETWORK GROWTH — onde vender/abrir franquia

| peça | estado |
|---|---|
| `funil_nacional` — 5.570 municípios pontuados pelo IBGE | ✅ operacional |
| `radar_oportunidade` — a rede está nessa cidade? duas fontes | ✅ |
| `estudar_oportunidade` + `escreve_tese_oportunidade` — 6 cidades | ✅ |
| dossiê comercial de território (dentro da cidade) | ⚪ não existe |
| canibalização / distância para unidade existente | ⚪ não existe |

### B · LOCAL GROWTH — a unidade capturando mais demanda

| peça | estado |
|---|---|
| `fila` — qual unidade tratar primeiro, com faixa e prazo | ✅ |
| `onde_cada_loja_aparece` — presença por `local_id` | ✅ (a peça mais forte do produto) |
| `plano_do_franqueado` — 1 por loja | ✅ |
| `caixa_de_respostas` — avaliação negativa sem resposta | ✅ |
| `o_que_o_rival_faz` — o rival que ganha, na voz do paciente | 🟡 só rival de aparelho, amostra pequena |
| `quem_anuncia_aparelho` | 🟡 conta anunciantes, **não lê a oferta** |
| `timeline_da_loja` | ✅ |
| geo-grid — em QUE PARTE da cidade aparece | ⚪ não existe |
| jornada do paciente por estágio | ⚪ não existe |

### C · NETWORK LEARNING — o que as unidades ensinam

| peça | estado |
|---|---|
| `padroes_da_rede` — o que se repete entre as 10 | 🟡 amostra de 10 |
| `reteste` — testa cada achado contra TODAS as praças | ✅ (a peça metodologicamente mais madura) |
| ação → resultado → aprendizado | 🔴 **não existe, e é o maior buraco** |
| nível de maturidade do achado (sinal → doutrina) | ⚪ |

### D · INFRAESTRUTURA

`cruzamento` (dedup, `local_id`, concordância), `padrao` (a régua de 20
etapas), `build_portal` (o único lugar que calcula), `rotulo`,
`produto_do_concorrente` (aparelho vs resto), `pontos_cegos`.

### E · LEGADO — candidato a `/legacy`

`injetar_casco`, `promover_canais`, `reimporta_bruto`, `backfill_ibge`,
`whatsapp_teste` (coleta que a rede não autorizou), e **17 dos 24 `.md`
da raiz** (ver §4).

---

## 4 · REDUNDÂNCIAS

**A pior é documental.** A raiz tem **24 arquivos `.md`, 380 KB**, e três
deles descrevem o mesmo produto em momentos diferentes:
`PROJETO.md` (13 KB), `PROJETO-PORTAL-ORTHODONTIC.md` (67 KB) e
`PORTAL-INTELIGENCIA-ORTHODONTIC.md` (56 KB) — 137 KB dizendo coisas
parcialmente contraditórias. Mais cinco prompts de casco vivos ao mesmo
tempo (V2, V3, V6, `PROMPT-CLAUDE-DESIGN-PORTAL`, `PROMPT-CORRECAO-CASCO`)
e dois pilotos (`PILOTO-01`, `PILOTO-02`).

**Isto é risco de produto, não arrumação.** A próxima sessão vai abrir o
arquivo errado e ressuscitar um conceito morto — já aconteceu nesta.

Recomendo: mover 17 para `/legacy`, manter **cinco** canônicos —
`CLAUDE.md` (as regras), este documento (o norte e o mapa),
`coleta/NOVA-PRACA.md` (o processo), `PROMPT-CASCO-V6.md` (o casco) e
`COMO-ESCREVER.md` (a voz).

**Redundância de dado:** `rede.json` e `franqueadora.json` cobrem o mesmo
território, e o casco só pede o segundo. `anuncios.json`, `padrao.json`,
`presenca_por_loja.json` e `rede.json` estão no disco e **nunca são
carregados pelo casco** — os três primeiros porque já vão embutidos nas
páginas; `rede.json` é sobra.

**Redundância de leitura:** `oportunidades_franqueado`,
`plano_do_franqueado` e `onde_cada_loja_aparece` respondem partes da
mesma pergunta ("onde esta loja pode captar mais"). Não precisam virar um
só script, mas precisam de uma **fonte única de verdade da presença** —
hoje é `onde_cada_loja_aparece`, e os outros dois deveriam consumi-la em
vez de recalcular.

---

## 5 · BURACOS — o que coletamos e não usamos, e o que não conseguimos responder

### Dado coletado que não vira decisão

| dado | volume | uso hoje |
|---|---|---|
| **imprensa** | 644 matérias | aparece só como **contador** em 5 payloads. Nenhuma manchete chega à tela. |
| **posts de Instagram** | 3.376 | só `radar.json`. O que o concorrente publica, com que frequência e sobre o quê não é lido. |
| **texto dos anúncios** | 735 anúncios, 134 de aparelho | contamos anunciantes. **Não lemos a oferta.** |
| **reviews classificados** | 26.332 | classificados por TEMA, nunca por **estágio da jornada**. |
| **comentários** | 1.380 | agregados em `voz_da_cidade`; a fala individual não é navegável. |

### Perguntas importantes sem resposta hoje

1. **Em que parte da cidade a loja aparece?** Falta grade geográfica de busca.
2. **O que o concorrente está vendendo?** Falta taxonomia de oferta.
3. **Em que estágio da jornada dói?** Falta taxonomia de jornada.
4. **A recomendação funcionou?** Falta o ciclo ação → resultado.
5. **Quanta confiança tem esta afirmação?** Falta o motor de confiança.
6. **A OrthoDontic está melhor ou pior que as redes rivais?** Só Reclame Aqui.
7. **Esta cidade canibaliza a unidade vizinha?** Falta distância/território.

---

## 6 · RISCOS

**Metodológicos, em ordem de gravidade:**

1. **Amostra.** Tudo que se chama "padrão da rede" vem de 10 lojas — 2,7%.
   Duas delas têm 2 medições. `reteste` já protege contra generalizar de 4
   praças; a mesma trava precisa valer para o vocabulário da tela.
2. **Delta curto lido como tendência.** Já corrigido em `o_que_mudou`
   (duas janelas), mas qualquer leitura nova repete o erro se não herdar
   a regra.
3. **Ausência tratada como zero.** Regra já escrita; falta um campo
   formal (`medido: true/false`) em vez de depender de prosa.
4. **A rede não valida nada.** Sem dado interno, toda causa é hipótese.
   Hoje o portal às vezes escreve inferência com cara de fato.

**Técnicos:**

5. Rotação de tokens Apify com dois tokens mortos no topo da lista —
   cada coleta desperdiça duas tentativas.
6. 48 das 374 fichas sem `place_id`; 3 lojas nossas entre elas.
7. O HTML do portal vive fora do repositório (Claude Design). O
   repositório não consegue rodar o produto sozinho — só o payload.

**De produto:**

8. Os 24 `.md` da raiz (§4).
9. Sete telas no menu e a tentação de virar 25.

---

## 7 · ARQUITETURA RECOMENDADA

Preservar: **a unidade como menor conta**, **o casco que não calcula**,
**a régua `padrao.py`**, **só dado externo**, **o rótulo `UF · Cidade`**.

Acrescentar **três camadas transversais**, que valem para toda leitura:

### 7.1 · Motor de confiança

Todo item de inteligência passa a carregar, no payload:

```json
{"natureza": "fato|inferencia|hipotese|recomendacao",
 "confianca": "alta|media|baixa",
 "amostra": 71, "janela_dias": 26, "medicoes": 3,
 "medido": true,
 "a_favor": ["..."], "contra": ["..."],
 "o_que_aumentaria": "mais duas medições quinzenais",
 "fonte": "dados/serie/reviews.jsonl"}
```

A tela desenha cada natureza diferente. Recomendação nunca com cara de
medição. `medido: false` é diferente de valor zero — e resolve o risco 3.

### 7.2 · Captura observável do mercado local

Em vez de nota mágica, quatro dimensões decomponíveis, todas já
alimentáveis com o que temos:

| dimensão | de onde sai hoje |
|---|---|
| **encontrabilidade** | `presenca_por_loja` (buscas onde aparece) |
| **confiança** | nota, volume, respostas, `caixa_de_respostas` |
| **ritmo** | avaliações novas/mês, meses seguidos |
| **pressão do mercado** | `categoria` + `anuncios` da cidade |

Nenhuma delas fala em faturamento. Nenhuma precisa da rede.

### 7.3 · Livro-razão de ação e resultado

Série nova, append-only: `dados/serie/acoes.jsonl`. Uma linha por
recomendação, e depois a medição seguinte grava o "depois". É o único
ativo que nenhum concorrente consegue copiar coletando Google — e o
`fila_historico` (16 linhas) já é o embrião disso.

---

## 8 · ROADMAP

**P0 — fundação e confiança** (nada novo na tela)
1. Motor de confiança nos payloads que já existem.
2. `/legacy` para os 17 documentos, e este arquivo como norte.
3. `medido: true/false` formal em toda contagem.
4. Limpar os dois tokens mortos e o `rede.json` órfão.

**P1 — valor com o dado que já está no disco** (os quick wins do §9)
5. Jornada do paciente sobre as 26.332 avaliações já classificadas.
6. Oferta do concorrente sobre os 134 anúncios de aparelho.
7. Imprensa e posts saindo de contador para conteúdo.
8. `acoes.jsonl` gravando o ciclo.

**P2 — diferenciais que exigem coleta nova**
9. Geo-grid de busca por coordenada.
10. Comparação entre redes rivais.
11. Território dentro da cidade para expansão.

**P3 — experimento**
12. Visibilidade em resposta de IA, com metodologia e repetição declaradas.

---

## 9 · QUICK WINS — valor sem coleta nova

Tudo abaixo usa dado **já no disco**:

1. **Jornada do paciente.** 26.332 avaliações já classificadas por tema;
   reclassificar por estágio (descoberta → contato → agendamento →
   recepção → clínico → manutenção → cobrança) permite dizer "o problema
   público desta unidade não é clínico, é cobrança". Custo: um script.
2. **A oferta do rival.** O texto dos 134 anúncios de aparelho está
   guardado. Classificar por preço, sem entrada, parcelamento, alinhador,
   urgência, prova social responde "qual é a guerra desta cidade".
3. **Imprensa vira conteúdo.** 644 matérias viram, no mínimo, a manchete
   com data e link na página da praça.
4. **Ritmo do concorrente no Instagram.** 3.376 posts dizem quem publica,
   com que frequência e quando acelerou.
5. **`acoes.jsonl` a partir do `fila_historico`.** As 16 linhas de fila
   já contêm problema, data e desfecho — é o começo do livro-razão.

---

## 10 · NOVAS COLETAS QUE SE JUSTIFICAM

**Sim:** geo-grid de busca (Places API a partir de coordenadas numa
grade sobre a cidade) — é a única coleta nova que abre uma pergunta
inteiramente nova e serve aos dois motores de crescimento.

**Sim, barata:** ficha pública das redes rivais nacionais, para a
comparação de marca.

**Não agora:** INEP e CNES — só entram quando o dossiê de território
existir; hoje virariam número sem decisão. Trends: **medido e negado**,
não refazer.

---

## 11 · ALTERAÇÕES DE DADOS

Campos novos: o bloco de confiança (§7.1) em `fila`, `padroes`, `rival`,
`clinicas/*`; `jornada[]` em `clinicas/*`; `oferta{}` em `anuncios`;
`imprensa[]` e `ritmo_do_rival{}` em `pracas/*`; série `acoes.jsonl`.

---

## 12 · ALTERAÇÕES DE INTERFACE

Nada disso vira menu novo. Jornada, oferta do rival, imprensa e ritmo são
**capítulos** — os três primeiros na clínica ou na praça, conforme sejam
leitura de unidade ou de cidade. Confiança é **adorno de cada bloco**, não
tela. Ação→resultado aparece na linha do tempo da loja e vira uma seção
de Benchmarks quando houver amostra.

---

## 13 · MÉTRICAS DE SUCESSO DO PRÓPRIO PORTAL

| métrica | como medir | de onde |
|---|---|---|
| tarefas resolvidas | `fila_historico`, estado resolvido | já existe |
| tempo até a resolução | abertura → resolução | já existe |
| unidades que melhoraram após ação | métrica antes/depois | precisa de `acoes.jsonl` |
| hipóteses confirmadas ou derrubadas | `reteste` | já existe |
| % da rede monitorada | 10 de 374 | já existe |
| frescor da coleta | dias desde a última medição por série | já existe |

A primeira métrica honesta hoje é **10 de 374**. Enquanto ela não subir,
qualquer outra fala de uma amostra pequena — e o portal deve dizer isso.
