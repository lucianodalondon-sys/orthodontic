# DOSSIÊ — Mafra/SC — Mafra, o piloto aplicado (único com dados internos do BI)

_Extraído dos arquivos-fonte e auditado contra eles. London Creative, julho/2026._

---

## 1 · IDENTIDADE

**Cidade / praça real:** o primeiro achado do estudo corrige o próprio nome do projeto — *"a praça não é "Mafra" — é RIOMAFRA."* A unidade fica em **Mafra/SC**, mas a praça de mercado é o par de cidades gêmeas **Mafra (SC) + Rio Negro (PR)**.

- **UF:** SC (Mafra) e PR (Rio Negro) — duas margens, uma cidade.
- **Unidade:** **OrthoDontic Mafra** (grafada "OrthoDontic" no conteúdo; "Orthodontic" no nome da rede).
- **Endereço / região:** **Rua Felipe Schmidt, Alto de Mafra** (spot de rádio 4b: *"Rua Felipe Schmidt, Alto de Mafra"*). A memória de projeto registra: *"Corredor odonto = R. Felipe Schmidt (4 clínicas)"*. O Instituto Lumière fica **a 70 metros da porta**, em **F. Schmidt 1204**.
- **População:** **~87 mil pessoas numa malha urbana contínua** (memória: *"Mafra(SC,55k)+Rio Negro(PR,31k) = UMA colônia de 1829 partida pela divisa pós-Contestado; ~87k hab, mesmo DDD 47"*). A margem paranaense (Rio Negro) é citada no cap. 07 como **~31 mil hab**.
- **Apelido da cidade:** **"Mafra"** — *"a mídia local inteira se chama "Mafra". Falar "Mafra" é falar de dentro; tratar Rio Negro como outra cidade é o erro do forasteiro."*
- **Papel na rede:** **piloto aplicado e pago**, único com dados internos do BI. Memória: *"PILOTO PAGO (2026-07-15): Paula (decisora OrthoDontic) gostou do material e pediu piloto em MAFRA/SC — "agora é valendo", porta de entrada na rede (~350 unidades)."* No BI Conecta a rede aparece com **340 unidades ativas**; a unidade é classificada como **"Madura", safra 2019**. Camada política: *"A UNIDADE DE MAFRA ESTÁ EM NEGOCIAÇÃO DE RENOVAÇÃO DE CONTRATO de franquia e "precisa virar alguns ponteiros de resultado" — o piloto não é aleatório: é ferramenta da renovação"*. Fecho do estudo: *"Mafra — o piloto — vira o primeiro cérebro vivo da rede: o que funcionar aqui vira aprendizado testável nas outras centenas de unidades."*
- **Ano de abertura:** **2019** (safra 2019). *"em 2019, os dois decidiram voltar à cidade natal para abrir a clínica."* O estudo fala de **7 anos de casa** ("há 7 anos no mesmo endereço", "7 anos de sorrisos concluídos"); o comentário do YAML sobre o Instagram diz *"A voz da unidade (6 anos, ~2019)"*.
- **Donos / operadores:** **um casal de ortodontistas mafrenses que voltou para a cidade natal.** A memória de projeto nomeia: *"donos da unidade = CASAL DE ORTODONTISTAS MAFRENSES que voltaram pra cidade natal (Dra. Vanessa STOEBERL Gomes CRO12379/SC especialista + Dr. Luiz Henrique Gomes; Stoeberl = sobrenome da colônia). 2019, 7 anos, FICHA LIMPA no RA, 4,9/155 Google."* Dossiê de história: *"Dra. Vanessa CRO12379/SC especialista ORTO, RT+CNES; Stoeberl = sobrenome bucovino c/ RUAS nas 2 cidades (⚠️ validar parentesco); de 2 p/ 9 especialistas; ⚠️ marido pode ser RT da OrthoDontic RIO NEGRINHO (Luis Henrique de Abreu Gomes CRO8682 endodontia — validar)."* — a grafia do nome do marido diverge entre os dois trechos do mesmo arquivo ("Luiz Henrique Gomes" × "Luis Henrique de Abreu Gomes") e o checklist do kit exige validação: *"O Dr. é ortodontista ou endodontista de registro? (peça A1 cita "casal de ortodontistas" só se confirmado)"*.
- **Equipe:** cresceu **de 2 dentistas para 9 especialistas**. Membro da equipe com vazamento identificado: *"Dra. Rubia Lenz (equipe) tem clínica própria Invisalign (LENZ 4,9×52)"*.
- **Stakeholders do lado da rede:** **Paula** (decisora Orthodontic, campeã interna) e **Loraine** — *"CEO da OrthoDontic hoje, chefe da Paula"*. Do lado da London Creative: **Luciano**.

---

## 2 · COLETA E MÉTODO

**N total de vozes:** **452 vozes reais analisadas**, *"classificadas por método reproduzível e auditável — construído 100% de fora e, ao final, validado ponto a ponto pelos dados internos da rede (cap. 14)."*
**Data de corte:** **15/jul/2026** (repetida em todo o documento; rodapé: *"452 vozes reais (corte 15/jul/2026), classificação temática reproduzível e auditável, baseline congelado para medição em 90/180 dias."*).

### Fontes e o N que cada uma rendeu
| Fonte | N | Observação literal |
|---|---|---|
| Avaliações públicas de pacientes com texto (toda a categoria, duas cidades) | **224** | *"224 vozes de pacientes com texto, todas as clínicas de aparelho das duas cidades (corte 15/jul/2026, classificação reproduzível)"* |
| Google reviews unidade + OC Mafra + OC Rio Negro | **100 cada, ~120 c/ texto** | memória: *"Google reviews unidade+OC Mafra+OC RN (100 each, ~120 c/ texto)"* |
| Instagram: 3 páginas da cidade + a clínica | **183 comentários** | *"IG 3 páginas cidade+clínica (183 comentários, cidade comenta POUCO — engajamento baixo é característica da praça)"* |
| Corpus após o 1º lote | **~300 vozes** | *"Corpus ~300 vozes. LOTE 2 rodando"* |
| Série mensal de reviews datados (velocity) | **14 meses** | raw/velocity/*.json |
| Série de comportamento de busca | **5 anos (estado de SC)** | trends_sc.csv |
| Biblioteca pública de anúncios | todos os anúncios ativos da categoria | corte 15/jul/2026; scrape Meta Ads id `b0v2ivjul` |
| SERP / busca local | raw/serp.json | *"unidade domina "aparelho mafra" MAS via IG (SEM SITE)"* |
| Registro público de empresas (CNPJ, capital), imprensa local, RA | — | *"inclusive o registro público de cada empresa"* |
| Censo 2022 / SIDRA (dados duros) | — | agente-dados-duros.md |
| BI Conecta da rede (dados internos, 16/jul) | prints do BI — 340 unidades ativas | dossiê dados-internos-conecta.md |
| Últimos 100 reviews da unidade | **97 de cinco estrelas** | cap. 04 |

### As etapas do método (7 movimentos)
*"escutamos a **cidade** → aplicamos a **ciência** (antropologia e comportamento) → escutamos os **pacientes** da categoria inteira → radiografamos a **clínica** → abrimos o **playbook** de cada vizinho → mapeamos a **mídia ativa e a temporada** → **cruzamos tudo** num plano de 90 dias."*

1. **ETAPA 1 — Ouvimos a CIDADE.** *"As páginas que concentram a atenção de Mafra e Rio Negro, segmento por segmento (notícia, consumo, família, jovem). → Achado: a praça é UMA cidade com duas margens — e tem três territórios de atenção vazios."*
2. **ETAPA 2 — Aplicamos a CIÊNCIA.** *"Antropologia e economia comportamental da decisão em cidade pequena, com literatura consolidada. → Achado: aqui, o marketing mais eficiente é engenharia de indicação."*
3. **ETAPA 3 — Ouvimos os PACIENTES.** *"Avaliações públicas de toda a categoria nas duas cidades — 224 vozes de pacientes com texto. → Achado: 69% falam de COMO FORAM TRATADOS (N=224, corte 15/jul/2026) — o índice se repete em todas as praças que estudamos."*
4. **ETAPA 4 — Radiografamos a CLÍNICA.** *"Reputação, comunicação atual, resposta da audiência. → Achado: reputação de líder, comunicação de coadjuvante."*
5. **ETAPA 5 — Abrimos o PLAYBOOK dos vizinhos.** *"Quem cresce, como cresce, onde é fraco — inclusive o registro público de cada empresa. → Achado: a vizinha que ultrapassou tem 9 meses de vida e nenhuma raiz."*
6. **ETAPA 6 — Mapeamos a TEMPORADA e a mídia ativa.** *"A série de 5 anos do comportamento de busca da região + todos os anúncios ativos da categoria. → Achado: o pico anual é julho-setembro — é AGORA — e a unidade está muda."*
7. **ETAPA 7 — CRUZAMOS tudo.** *"Cidade × ciência × pacientes × vizinhos × tempo. → Resultado: o plano de 90 dias, com evidência, meta e dono em cada ação."*

**As 6 perguntas que o estudo responde:** *"1. Quem é o riomafrense e em que língua ele fala? 2. O que a ciência diz sobre como uma cidade pequena decide? 3. Onde a unidade ganha e onde perde — e de quem? 4. Por que os vizinhos que crescem, crescem — e onde são fracos? 5. Quando a cidade procura aparelho — e quem está lá nessa hora? 6. O que fazer, em que ordem, medido como?"*

**A promessa metodológica:** *"cada número deste estudo carrega o tamanho da base e a data da coleta. Onde não há evidência, não há recomendação — e há uma página inteira sobre o que este método não enxerga."*

**Infra do método:** dataset `data_ortho_mafra/`, config `targets_orthodontic_mafra.yaml`, dossiês em `data_ortho_mafra/raw/documental/` (agente-alma-mafra, agente-ciencia-aplicada, agente-mercado-unidade, agente-playbook-lumiere.md, agente-historia-unidade.md, agente-mapa-influencia.md, agente-dados-duros.md, dados-internos-conecta.md), entregável em `output_ortho_mafra/`. Taxonomia **bd67982156e8**; **léxico ortho v1.1**; **ficha_mafra.json** = *"1ª ficha validada do sistema"*; **monitor_praca.py (M5)** criado, 1ª rodada ago/26. Comando de coleta: `FK_CONFIG=config/targets_orthodontic_mafra.yaml FK_RAW=data_ortho_mafra/raw FK_CORPUS=data_ortho_mafra/corpus python scripts/collect_*.py`. Chaves: *".env atual = quintessential_creeper (~4,6 livre); reserva APIFY_TOKEN_NEXT = yawning_celeriac ($5)"*. Custo do Lote 5: **~US$ 0,9**.

**Alerta de coleta gravado no YAML e na memória:** *"CUIDADO: existe Mafra em PORTUGAL — "clínica dentária"/beclinique = PT. Filtrar tudo por SC/Brasil."*

### LISTA COMPLETA DOS ALVOS COLETADOS (targets_orthodontic_mafra.yaml)
Cabeçalho do arquivo: *"ALVOS — Público de MAFRA/SC + RIO NEGRO/PR (cidades gêmeas) / OrthoDontic Mafra — PILOTO VALENDO — estudo será aplicado na unidade. Profundidade máxima."*

**Bloco 1 — PRÓPRIO + CONCORRENTES (reviews Google)** — comentário: *"reviews Google — baratos, rodar primeiro"*
| name | layer | plataforma | query | enabled | papel (comentário literal do arquivo) |
|---|---|---|---|---|---|
| `ortho_mafra_google` | proprio | google | "OrthoDontic Mafra SC" | true | a própria unidade |
| `odontocompany_mafra_google` | concorrente | google | "OdontoCompany Mafra" | true | — |
| `odontocompany_rionegro_google` | concorrente | google | "OdontoCompany Rio Negro PR" | true | — |
| `dentista_mafra_google` | concorrente | google | "ortodontia aparelho ortodôntico Mafra SC" | **false** | *"descoberta: quem é o gigante local"* |
| `dentista_rionegro_google` | concorrente | google | "ortodontia aparelho ortodôntico Rio Negro PR" | **false** | — |

**Bloco 2 — TERRITÓRIO / VOZ DO RIOMAFRENSE (IG)** — comentário do bloco: *"Identidade confirmada: a praça se chama "Mafra" (Mafra+Rio Negro = UMA comunidade). Bio da maior página: "QUEM É DAQUI ACESSA!" — puro endogrupo."*
| name | layer | handle | max_posts / comments_per_post | enabled | papel |
|---|---|---|---|---|---|
| `riomaframix_ig` | influencer | `riomaframixoficial` | 12 / 30 | true | *"A MAIOR (53k > população de Mafra)"* |
| `diarioderiomafra_ig` | influencer | `diarioderiomafra` | 10 / 30 | true | *""o jornal do cidadão riomafrense" (23k)"* |
| `clickriomafra_ig` | influencer | `clickriomafra` | 10 / 30 | true | *"o portal pioneiro (20k, desde 2007)"* |

**Bloco 3 — LOTE 2: os locais fortes** — comentário: *"reviews c/ texto = o playbook deles"*
| name | layer | plataforma | query | enabled | papel |
|---|---|---|---|---|---|
| `lumiere_google` | concorrente | google | "Instituto Lumière Odontologia Mafra SC" | true | *"o gigante da porta (5,0×197, a 70m)"* |
| `cuidadoprevencao_google` | concorrente | google | "Clínica Cuidado e Prevenção Mafra SC" | true | *"o local de 20+ anos (4,9×135)"* |
| `edgardgoes_google` | concorrente | google | "Edgard Góes Odontologia Rio Negro PR" | true | *"o gigante de Rio Negro (5,0×103)"* |

**Bloco 4 — A PRÓPRIA CLÍNICA**
| name | layer | handle | max_posts / comments | enabled | papel |
|---|---|---|---|---|---|
| `ortho_mafra_ig` | proprio | `orthodontic.mafra` | 15 / 30 | true | *"A voz da unidade (6 anos, ~2019)"* |

*Nota do arquivo neste ponto:* *"(pendente pós-agentes: IG do gigante local, humor/achadinhos mafra)"*

**Bloco 5 — LOTE 3: playbooks de IG + voz da cidade aprofundada**
| name | layer | handle | max_posts / comments | enabled | papel |
|---|---|---|---|---|---|
| `odontocompany_riomafra_ig` | concorrente | `odontocompanyriomafra` | 15 / 30 | true | *"o concorrente das 2 margens"* |
| `riomaframix_deep_ig` | influencer | `riomaframixoficial` | 30 / 40 | true | *"aprofunda a voz da cidade (1º lote raso)"* |

**Bloco 6 — LOTE 4: segmentos do mapa de influência**
| name | layer | handle | max_posts / comments | enabled | papel |
|---|---|---|---|---|---|
| `dicasriomafra_ig` | influencer | `dicasriomafra` | 12 / 30 | true | *"CONSUMO — o indicador neutro"* |
| `vitorino_ig` | influencer | `restaurante.vitorino` | 10 / 30 | true | *"GASTRONOMIA — o + seguido da praça"* |
| `mafrafutsal_ig` | influencer | `mafra_futsal_oficial` | 10 / 30 | true | *"JOVEM/FAMÍLIA — escolinha 9-15 = público orto"* |
| `maternidade_ig` | influencer | `maternidadecatarinakuss` | 10 / 30 | true | *"MÃE — toda mãe da região passa lá"* |

**Total: 18 alvos declarados — 16 habilitados, 2 desabilitados (`dentista_mafra_google`, `dentista_rionegro_google`).**

### O léxico de classificação (lexico_orthodontic.yaml, versão 1.1)
Cabeçalho: *"LÉXICO ORTHODONTIC v1.0 — temas específicos de odontologia/ortodontia (pt-BR). Mesclado com metodologia/taxonomia.yaml pelo classify_corpus.py."* Nota de versão: *"v1.1: auditoria da amostra (Mafra) pegou variantes femininas/nominais ausentes na base → extensão do tema "atendimento" aqui (base intocada p/ não recontar outros estudos; PROTOCOLO §4)."* — **ou seja, a praça de Mafra é a que fez o léxico da rede evoluir de v1.0 para v1.1.**

| Tema | Descrição | Termos |
|---|---|---|
| `atendimento` | *"Extensão pt-BR: variantes femininas e nominais"* | bem atendida, mal atendida, atencao, gentileza, gentil, querida, queridos, querido, carinho, carinhosa, carinhoso, cuidadosa, cuidadoso, prestativa, prestativo, receptiva, receptivo, humanizado, humanizada, acolhimento, acolhedora, recepcao, recepcionista |
| `dor_medo_dentista` | *"Dor, medo de dentista, ansiedade, trauma, 'nem doeu'"* | dor, doi, doeu, doendo, medo, medinho, panico, trauma, traumatizada, traumatizado, fobia, ansiedade, ansiosa, ansioso, tranquilo, tranquila, "sem dor", "nem doeu", "não doeu", calma, paciencia, cuidadoso, cuidadosa, delicada, delicado |
| `resultado_autoestima` | *"Transformação, autoestima, voltar a sorrir, sonho realizado"* | autoestima, resultado, resultados, transformacao, transformou, sorriso novo, "sorrir novamente", "voltei a sorrir", "consigo sorrir", sonho, realizado, realizada, "antes e depois", mudou minha vida, vergonha, confiante, satisfeita, satisfeito, feliz, felicidade, maravilhoso, maravilhosa, perfeito sorriso |
| `explicacao_clareza` | *"Explicaram tudo, tiraram dúvidas, transparência"* | explica, explicou, explicaram, explicacao, duvida, duvidas, esclareceu, esclarecimento, transparente, transparencia, detalhou, informou, orientou, orientacao, "entendi tudo", didatica, didatico |
| `aparelho_tratamento` | *"Menções ao aparelho/tratamento ortodôntico em si"* | aparelho, aparelhos, ortodontia, ortodontico, ortodontica, ortodontista, manutencao, borrachinha, borrachinhas, alinhador, alinhadores, invisalign, bracket, brackets, contencao, "tirar o aparelho", documentacao, banda, fio |
| `familia_filhos` | *"Mãe/pai falando de filho em tratamento (a decisora)"* | filho, filha, filhos, filhas, meu menino, minha menina, crianca, criancas, pequena, pequeno, adolescente, "minha pequena", odontopediatria, odontopediatra, "meu piá", pia |
| `tempo_relacao` | *"Anos de casa, gerações, cliente antigo, relação longa"* | anos, "desde o inicio", "ha anos", geracao, geracoes, "cliente ha", "faco tratamento desde", antiga, antigo, "toda a familia", "familia toda", sempre fui, "acompanha desde" |

---

## 3 · PLACAR DE REPUTAÇÃO

**O placar da praça (as duas margens, jul/2026 — corte 15/jul/2026):**

| Clínica | Nota | Avaliações |
|---|---|---|
| OdontoCompany Mafra | 4,7 | **338** |
| **Instituto Lumière (9 meses de vida, a 70 m)** | **5,0** | **197** |
| OdontoCompany Rio Negro | 4,7 | 188 |
| **OrthoDontic Mafra** | **4,9** | **155** |
| Cuidado e Prevenção (20 anos, dona do infantil) | 4,9 | 135 |
| Edgard Góes Odontologia (Rio Negro) | 5,0 | 103 |
| Especialistas locais menores | 4,7–5,0 | 7–85 |

**Fora da tabela mas registrada na memória:** *"Dra. Rubia Lenz (equipe) tem clínica própria Invisalign (LENZ 4,9×52)"*.

**Nota de recorte (verbatim):** *"o placar compara REPUTAÇÃO, não produto — no mapa, a mãe vê todas essas notas lado a lado, sem separar especialidade. Vale registrar: o volume da Lumière foi construído vendendo implante e prótese (zero menção a aparelho nas avaliações dela) — ela entra no placar porque disputa o mesmo balcão de confiança e porque acabou de invadir a ortodontia. As franquias de implante puro (Oral Sin, Oral Unic) ficam fora do recorte. E o detalhe que resume o tabuleiro: a OrthoDontic é a ÚNICA clínica da praça especializada em ortodontia — todas as outras vendem aparelho como um item do cardápio."*

**As três leituras do placar:**
1. *"A rede popular joga as DUAS margens: 526 avaliações somadas — mais de 3x o volume da OrthoDontic — enquanto a unidade joga só o lado catarinense."*
2. *"A vizinha de porta fez 197 avaliações em 9 meses (a OrthoDontic fez 155 em 7 anos). Volume de reputação é construção deliberada, não acaso."*
3. *"A rua da clínica é o corredor odontológico da cidade — 4 clínicas na mesma rua. O paciente compara a pé, vitrine a vitrine."*

### Série de VELOCITY — reviews novos por mês (todos os reviews datados, 14 meses)
| | OrthoDontic | OdontoCompany (Mafra) | Lumière | Cuidado e Prevenção |
|---|---|---|---|---|
| média/mês | **0,7** | ~13 | ~28 desde jan | ~9 desde mar |
| melhor mês | 4 | **33** (mai/26) | **72** (mar/26!) | 10 |

*"A OrthoDontic somou 10 avaliações em 14 meses. A Lumière fez 72 num único mês. Até a Cuidado e Prevenção, de 20 anos, ligou uma máquina em março. Todo mundo na praça está correndo — a unidade está estacionada. Não é impressão: é série mensal com data (corte 15/jul/2026)."*

Complemento do playbook da Lumière: *"uma fábrica de avaliações na primeira visita (~22/mês)"*. Gap de volume declarado no painel: **3,4x vs líder das 2 margens**.

---

## 4 · A CONSTANTE DO ATENDIMENTO

**O número:** **atendimento = 69%**, sobre **N = 224 vozes de pacientes com texto**, **corte 15/jul/2026**, todas as clínicas de aparelho das duas cidades, classificação reproduzível.

*"atendimento: 69% — o índice mais alto de todas as praças que já estudamos (as anteriores: 54%, 47%, 63%). Aqui, mais que em qualquer lugar, o paciente avalia COMO FOI TRATADO."*

**A NOTA DE MÉTODO (verbatim):** *"(Nota de método: como as clínicas da praça são todas multi-serviço, a base inclui pacientes de toda a odontologia local; nas praças anteriores, com recorte estrito de ortodontia, a mesma constante deu 54-63% — o achado não depende do recorte.)"*

**Os demais temas da mesma base (N=224):** *"qualidade/resultado: 54% · recomendação explícita: 30% · autoestima: 12%"*.

Como o achado é repetido na Etapa 3: *"69% falam de COMO FORAM TRATADOS (N=224, corte 15/jul/2026) — o índice se repete em todas as praças que estudamos."*

E a consequência estratégica: *"a assinatura do líder de volume é exatamente o pecado nº 1 da categoria (atendimento = 69% do que a praça avalia). Numa cidade onde o erro tem memória, isso é pólvora armazenada."*

---

## 5 · PERSONA DA CIDADE

### Identidade de base
*"Mafra (SC) e Rio Negro (PR) nasceram como UMA colônia em 1829 e foram partidas ao meio pela divisa dos estados. Hoje: mesmo DDD, ônibus urbano que cruza a ponte, ~87 mil pessoas numa malha urbana contínua"*. Memória: *"UMA colônia de 1829 partida pela divisa pós-Contestado; ~87k hab, mesmo DDD 47"*.

### Temperamento
- **Colônia-mosaico:** *"de alemães-boêmios (bucovinos — Mafra é a maior colônia bucovina do mundo), poloneses e ucranianos. Sobrenome aqui é identidade: a cidade tem ruas com nomes de famílias da colônia."* Memória: *"colônia mosaico eslavo-germânico (BUCOVINOS raros no mundo, poloneses, ucranianos)"*.
- **Temperamento de colônia:** *"discreto, comunitário, de tradição. Desconfia de promessa grande; respeita trabalho, constância e palavra cumprida. A voz pública da cidade é vigilante e sarcástica com quem decepciona — e calorosa com o que é de família"*.
- **Comenta pouco em público:** *"cidade comenta POUCO — engajamento baixo é característica da praça"* / *"o silêncio digital daqui é característica, não ausência de opinião."*
- **Endogrupo declarado:** bio da maior página da região — *"QUEM É DAQUI ACESSA!"* — descrita no YAML como *"puro endogrupo"*.

### Léxico real (gírias e expressões)
- **"piá"** (e a variante coletiva **"piazada"**, usada no kit: *"quem cuida do aparelho da piazada é ortodontista especialista, gente daqui"*; *"o esporte que forma a piazada das duas cidades"*). No léxico de classificação aparece como termo: `"meu piá"`, `pia`.
- **"vina"** (memória: *"língua curitibana-planaltense (piá, vina; JAMAIS bah/tchê nem Blumenau-genérico)"*).
- **"chimarrão"** — inclusive como nome de programa de rádio: *"Cablocão/Hora do Chimarrão p/ testemunhal"*, *"o programa da hora do chimarrão"*.
- **"Mafra"** — o gentílico/topônimo de dentro; a unidade *"já usa o nome da praça na comunicação ("Mafra")"* e *"#mafra (instinto local ok)"*.
- **"geia"** (do calendário editorial: *"cuidar de você enquanto lá fora geia"*).
- **"inverno de verdade"**, *"o falar do planalto"*.
- A frase-afeto do corpus, para um comércio local: *"Loja linda, família linda, equipe linda!"*

### Valores e orgulhos
- **Sobrenome como identidade** — *"a cidade tem ruas com nomes de famílias da colônia"*; *"Numa praça onde confiança é sobrenome"*.
- **A neve de 2013** — *"memória afetiva coletiva"*.
- **Os fósseis** — memória: *"fósseis CENPALEO = orgulho escolar real"*.
- **O trem / ferrovia** — *"Pery Ferroviário"*.
- **Fé** — *"fé católica+ucraniana+João Maria"*; o rádio local inclui *"a emissora fundada pela própria paróquia"*.
- **Ser a maior colônia bucovina do mundo.**
- **A ferida da cidade é SAÚDE:** *"fila de madrugada no posto, especialidade só viajando ~2h. O morador está treinado a esperar, viajar ou desistir"*. Memória: *"Ferida nº1 da cidade: SAÚDE = "esperar, viajar (Curitiba 115km) ou desistir"."*

### Sub-segmentos e como cada um fala
- **A mãe (a decisora):** fala pelos filhos — *"meu filho é cuidado há 4 anos"*, *"minha filha de 11 anos"*. O post mais compartilhado da cidade no FB orgânico foi *"férias c/ filhos no parque (34 shares, reflexo da mãe)"*.
- **O povão dos classificados:** *"os grupos públicos de classificados (onde o povão compra e comenta)"*.
- **A família de supermercado:** *"os perfis de ofertas dos supermercados (o "jornal" da família)"*.
- **A mãe e a avó:** *"o RÁDIO (três emissoras fortes, uma da própria paróquia — a mídia da mãe e da avó)"*.
- **O jovem/adolescente:** o público ortodôntico de 9-15 anos, *"escolinha de 9-15 anos das duas cidades — o público ortodôntico exato com os pais na arquibancada"*. E os que saem: *"Os jovens vão embora (o polo universitário e o emprego ficam a ~2h)"*.
- **O interior rural:** alvo explícito da concorrência — *"prótese/implante para o interior rural — ela anuncia por cidade: "atenção Itaiópolis", "agricultores de Mafra e região""*. Cidades do interior nomeadas no kit: Itaiópolis, Papanduva, Quitandinha, Campo do Tenente, Monte Castelo.
- **O trabalhador:** memória — *"Renda R$2,8k (operário madeira/móveis, servidor)"*.
- **O idoso:** território do concorrente da outra margem — *"vence com o dono respondendo cada avaliação e carinho com idosos"*.

### Canais de atenção, em ordem de peso (cap. 11)
1. **A maior página da região — 53 mil** (*"mais seguidores que a população de Mafra"*) → `@riomaframixoficial`.
2. **Os grupos públicos de classificados** (*"onde o povão compra e comenta"*).
3. **O RÁDIO** — *"três emissoras fortes, uma da própria paróquia — a mídia da mãe e da avó"*. Memória: *"Rádio forte (Nova Era 1986, São José da paróquia)"*.
4. **Os perfis de ofertas dos supermercados** — *"o "jornal" da família"*.
5. **A agenda pública da cidade** (prefeitura/prefeito, **24-25 mil**).
6. **A grande festa de setembro** — *"dezenas de milhares de pessoas — estande e presença"*.
7. **O futsal local** — *"escolinha de 9-15 anos das duas cidades — o público ortodôntico exato com os pais na arquibancada"*.
8. **O perfil-indicador de consumo da praça e a gastronomia mais seguida** (parcerias de indicação) → `@dicasriomafra`, `@restaurante.vitorino`.

Outros ativos da praça mapeados: `@diarioderiomafra` (23k, *"o jornal do cidadão riomafrense"*), `@clickriomafra` (20k, *"o portal pioneiro… desde 2007"*), `@maternidadecatarinakuss` (*"toda mãe da região passa lá"*), `@mafra_futsal_oficial`.

**As três lacunas (ninguém ocupa):** *"não existe página de humor da cidade, não existe mãe-influencer local e não existe criador de vídeo local. Quem chegar primeiro nesses territórios fala sozinho."* (memória: *"3 LACUNAS (sem página de humor, sem mãe-influencer, sem tiktoker local)"*).

**Dois atalhos abertos pelo levantamento:** *"(a) o rádio da praça se compra num telefonema — um único balcão comercial vende 3 das 4 frequências relevantes, incluindo a emissora de 15 kW que cobre a região inteira; e a rádio da outra margem tem locutores-personagem queridos (o programa da hora do chimarrão) perfeitos para testemunhal; (b) o circuito de prestígio local funciona por adesão — o "prêmio de melhores do ano" e o guia do comércio são acessíveis comercialmente, e um concorrente já foi "eleito ortodontista destaque do ano" por essa via. Se a especialista de verdade não ocupa o título, o título fica com quem chegar primeiro."* Memória: *"prêmio local = ADESÃO (publieditorial; Grahl "eleito ortodontista destaque" 2022)"*; *"1 balcão vende 3 frequências (Rede Nova)"*; *"Prêmio local anual COM categoria dentista"*; *"guia do comércio (CDL)"*.

### Calendário cultural
- **Julho:** *"Festival de Inverno e a festa da colônia em julho"* → memória: *"Bucovina Fest+Festival de Inverno jul"*.
- **Setembro:** *"a grande festa da cidade em setembro (dezenas de milhares de pessoas)"* → memória: **"MAFRA FEST 5-8/set"**; no plano de ação: *"18 mil pessoas na festa"*.
- **O ano todo:** *"as festas de paróquia o ano todo."*
- **Inverno:** *"o inverno concentra a família dentro de casa, no celular — a decisão é tomada no sofá."* Memória: *"Inverno: decisão dentro de casa (SAD subclínico 20%)."*
- **Férias escolares (duas ondas — ver cap. 9).**

### PROIBIÇÕES DE TOM
- *"Jamais gíria gaúcha, jamais estética de Oktoberfest — aqui a colônia é outra."*
- Memória: *"JAMAIS bah/tchê nem Blumenau-genérico"*.
- *"Jamais: hype, urgência de liquidação, "última chance" (o radar antivigarista da colônia queima a marca), gíria gaúcha, estética de Oktoberfest genérica."*
- Kit: *"PROIBIDO: hype, "últimas vagas", urgência de liquidação, gíria gaúcha, estética Blumenau."*
- *"O frio como cúmplice, não como piada."* / *"nunca piada COM o frio."*
- *"sem leilão de desconto"* (na resposta à objeção de preço).
- *"sem autoelogio, só presença"* (no post de comunidade).
- *"cumplicidade com o adolescente, nunca bronca"* (no bastidor da manutenção).
- *"deixar o locutor falar do jeito DELE — testemunhal engessado morre no ar"*.
- *"variar; nunca copiar-colar idêntico"* (respostas a reviews).
- *"sempre com rosto, nunca cupom"* (publi com o perfil-indicador).
- Do prompt de design: *"Proibido: foto de banco de imagem de dente/clínica, urgência de varejo, ícones infantis"*; *"sobriedade de consultoria com a identidade do frio do planalto (nada tropical, nada de estética de liquidação)"*.

---

## 6 · PERSONA DO PACIENTE

### Quem decide
**A mãe.** *"os pais falam dos filhos ("meu filho é cuidado há 4 anos", "minha filha de 11 anos") — a decisora é a mãe"*. Memória: *"Mãe decisora."* O léxico de classificação carrega o tema `familia_filhos` com a descrição *"Mãe/pai falando de filho em tratamento (a decisora)"*.
Segmentos de decisão usados nos anúncios do kit: **mãe 28-50** (A1), **pais 40-55** (A4), **público geral, renda C** (A3).

### Elogios-assinatura (o que a praça elogia, verbatim)
- *"Ótimo atendimento, preço justo e lugar aconchegante"*
- *"Clínica limpa e cheirosa, ambiente super agradável e profissionais mto atenciosos"*
- *"A melhor clínica e os melhores dentistas!!!"*
- *"os melhores dentistas!!! Saudades"*
- Perfil temático: **atendimento 69% · qualidade/resultado 54% · recomendação explícita 30% · autoestima 12%** (N=224).
- E o padrão de forma: *"atendimento e ambiente que viram elogio · preço justo reconhecido"*.

### Dores → antídotos (tabela do cap. 12, verbatim)
| Dor | Antídoto |
|---|---|
| **Medo de golpe / "cair numa cilada" aos olhos da cidade** | Contrato claro + o sobrenome local + 7 anos de casa + zero reclamação |
| **"Quanto fica por mês?"** (renda ~R$ 2,8 mil) | Parcela transparente, "cabe no orçamento" — sem leilão de desconto |
| **Medo de dentista (do filho e o próprio)** | A recepção que já é elogio + explicar passo a passo + "você controla o ritmo" |
| **Ser esquecido entre manutenções** | Protocolo de comunicação blindado — e a promessa pública "manutenção mensal DE VERDADE" |
| **"E se meu filho for embora estudar?"** | A rede: o tratamento continua em qualquer unidade do Brasil |

### Objeções reais (as perguntas que a praça faz)
Do "People Also Ask" da busca — *"as perguntas que o público faz junto com essas buscas são todas de PREÇO"*:
- *"qual o valor mensal de um aparelho?"*
- *"é normal ficar 7 anos de aparelho?"*
- *"Dói pra colocar?"* (2ª/3ª perguntas da busca, segundo o calendário editorial)
- *"Meu filho vai estudar fora — e o aparelho?"*
- **A pergunta-armadilha do cliente-oculto:** *"se meu filho for estudar fora, dá problema?"* — *"apostamos que só uma clínica da praça tem resposta para ela."*
- Script 5a do kit: *"Pergunta de preço (a nº1): NUNCA silêncio, NUNCA "só na avaliação""*.

### Gatilhos de decisão
- **Indicação:** *"Indicação não é um canal de marketing: é O canal de decisão."* / *"aqui, o marketing mais eficiente é engenharia de indicação."*
- **Prova social provinciana:** *""Sorrisos de Mafra e Rio Negro" vale mais que "milhões no Brasil""* (memória: *""300 sorrisos em Mafra" > "milhões no Brasil""*).
- **Sobrenome conhecido / rosto local:** *"a confiança real é na família, no vizinho, no sobrenome conhecido"*; *"O antídoto documentado: um rosto local na frente, a rede como garantia atrás."*
- **Clareza e garantia > desconto:** *"O medo da mãe é duplo: perder dinheiro E ser vista como "a mãe que caiu no golpe" (aversão à perda + custo social do erro). Clareza e garantia valem mais que desconto."*
- **Parcela que cabe:** *"praça de aparelho parcelado (entrada baixa, parcela pequena)"*.
- **Continuidade nacional:** *"se o seu filho for estudar fora, o tratamento continua em qualquer unidade do Brasil."*
- **A criança sem medo:** *"a clínica local que é dona do território infantil vence exatamente com "atendimento em que seu filho não tem medo de ir ao dentista""*.
- **Velocidade de resposta:** *"responder em minutos não é operação, é posicionamento"* / *"TODA mensagem respondida em <30 min em horário comercial"*.
- **Reputação com memória:** *"Os primeiros pacientes definem a reputação dos próximos anos; um paciente mal atendido é uma emissora de rádio."* (memória: *"50 primeiros pacientes definem 5 anos"*).

---

## 7 · RAIO-X DA UNIDADE

### ✅ O QUE FAZ CERTO (verbatim)
*"a melhor reputação entre as grandes (4,9×155, 97 de 5 estrelas nos últimos 100) · atendimento e ambiente que viram elogio · preço justo reconhecido · aparece em 1º na busca local da categoria · patrocina a comunidade (escoteiros) · já usa o nome da praça na comunicação ("Mafra")."*

Complementos: *"quase nenhuma ferida"*; *"FICHA LIMPA no RA"*; *"a OrthoDontic é a ÚNICA clínica da praça especializada em ortodontia"*; comparecimento na régua e fechamento/pagamento acima dela (cap. 14); *"Sem agendamento futuro só 17 (higiene de agenda ok)"*.

### ❌ O QUE DEIXA NA MESA (os 6 pontos, verbatim)
1. *"**A história está no cofre.** Os donos são um casal de ortodontistas da cidade que voltou pra casa — publicado na imprensa local, com sobrenome que está no MAPA das duas cidades — e o feed não conta. Numa praça onde confiança é sobrenome, é o maior ativo parado da cidade."*
2. *"**O feed abandonou a especialidade.** A clínica "Especializada em Aparelho" posta facetas, implante, canal, prótese — brigando no território dos vizinhos e deixando o próprio vago."*
3. *"**Muda na mídia paga: zero anúncios ativos** contra 10 da Lumière e 7 da OdontoCompany — no pico anual de procura."*
4. *"**Metade da praça sem luta.** A margem paranaense (Rio Negro, ~31 mil hab) é atendida pela rede concorrente; a unidade não fala com ela."*
5. *"**A máquina de avaliações desligada:** 155 em 7 anos (a Lumière fez 197 em 9 meses pedindo). Cada paciente satisfeito que sai sem avaliar é um tijolo que o concorrente coloca no muro dele."*
6. *"**A única ferida (operacional):** falha de comunicação interna que deixou paciente 1 mês sem manutenção — pequena hoje, mas é exatamente a categoria de erro que cidade pequena não esquece."*

Complementos do diagnóstico na memória: *"IG 2,1k fraco: feed ABANDONOU a ortodontia (posta faceta/implante/canal = território da Lumière) e ZERO rosto"*; *"a unidade não tem site próprio"*; vazamento na busca do alinhador para a clínica particular de uma dentista da própria equipe.

### A FERIDA PRINCIPAL
**Externa (pública):** a única avaliação-mancha da unidade — *"falta de comunicação entre a equipe… fiquei 1 mês sem manutenção"* — descrita como *"(a ferida a blindar, e é operacional, não clínica)"*.

**Interna (a real, revelada pelo BI):** **o estágio interessado → agendamento, a 6% contra uma régua de 40%.** *"A leitura em uma frase: quem chega, fecha. Quem chama, some. O comparecimento bate a régua (49% ≈ 50%), o fechamento e o pagamento estão ACIMA dela (75-99%) — a cadeira e o contrato funcionam. O único estágio quebrado é o primeiro: de cada 100 interessados, só 6 viram avaliação agendada — a régua da rede espera 40. O problema está entre a primeira mensagem e a agenda — exatamente a linha de frente que o estudo apontou de fora."*

E a **segunda ferida**: *"os dados internos revelaram uma SEGUNDA sangria: o pagamento… As duas sangrias se somam: entra pouco (6% de agendamento) e parte do que entra escorre (a safra que para de pagar)."*

**A tese que resume o raio-X:** *"O problema da unidade não é qualidade. **É presença.** E presença se resolve."*

---

## 8 · CONCORRÊNCIA

### O LÍDER
Há dois "líderes" distintos no arquivo, por critério:
- **Líder de VOLUME de reputação:** **OdontoCompany** — **526 avaliações somadas nas duas margens** (338 Mafra + 188 Rio Negro), *"mais de 3x o volume da OrthoDontic"*; individualmente, OdontoCompany Mafra é a maior da praça em volume (338).
- **Líder de VELOCIDADE / a ameaça imediata:** **Instituto Lumière**, *"a vizinha de 9 meses"*, *"a 70 metros da porta"*, que *"construiu com tráfego pago o dobro da velocidade de reputação — e acaba de invadir a ortodontia."*

### O PLAYBOOK DO LÍDER, PASSO A PASSO

**INSTITUTO LUMIÈRE (5,0 × 197) — o playbook completo:**
1. **Capital.** *"Registro público: aberta em out/2025, com capital 28x maior que o da unidade."* Memória: *"CNPJ out/25, capital R$840k (28x), sócias 20 e poucos, agência DigiOdonto/RJ"*.
2. **Um produto só no tráfego pago.** *"prótese/implante para o interior rural"*.
3. **Segmentação por cidade.** *"ela anuncia por cidade: "atenção Itaiópolis", "agricultores de Mafra e região""*.
4. **Isca.** *"avaliação gratuita com exame de imagem na casa como isca"*.
5. **Fechamento por mensagem.**
6. **Fábrica de avaliações na primeira visita.** *"(~22/mês)"* — 197 em 9 meses; **72 num único mês (mar/26)**.
7. **Criativos longevos.** *"os mesmos criativos no ar há 2+ meses (quem paga o mesmo anúncio por 2 meses está tendo retorno)"*.
8. **Invasão da ortodontia (jul/26).** *"campanha de julho: "aparelho sem entrada, no boleto""*.

**As BRECHAS do líder (Lumière), verbatim:** *"as avaliações são todas de primeira impressão (recepção, café, ambiente) — **zero menção a aparelho, zero tratamento longo concluído**; não há ortodontista nomeado em lugar nenhum (a única profissional pública é implantodontista recém-formada); não tem raiz local (nem site próprio; sem imprensa; comunidade zero — se a verba de anúncio parar, o fluxo para)."*
**A primeira rachadura:** *"a única avaliação negativa com texto dela (jan/26) é sobre contrato: "assinei contrato que oferecia limpeza… nunca recebi; só entregaram a prótese quando terminei os pagamentos." O brinde da isca não entregue e o produto refém do pagamento — a categoria de ferida que os reviews de primeira impressão escondem, e que tende a crescer conforme os tratamentos dela amadurecem."*

### OS OUTROS CONCORRENTES — força e fraqueza

**ODONTOCOMPANY (4,7 × 526, duas margens)**
- **Força real:** *"duas unidades, 7 anos, volume."*
- **Fraqueza dupla:** *"comunicação de megafone vazio (as legendas são "agende agora mesmo" repetido; engajamento zero nas duas redes sociais — tem seguidores, não tem comunidade)"* e *"as únicas feridas públicas documentadas da praça: vendeu um material e entregou outro, negativou uma mãe no cadastro de inadimplentes, manutenção prometida mensal feita a cada três meses."* Memória: *"Munição anti-OC documentada (RA): vendeu "safira" entregou cerâmica + NEGATIVOU mãe no SPC; manutenção "mensal" trimestral."*
- **O mapa das negativas:** *"as 14 feridas com texto são TODAS de recepção e espera — "não consegui passar da recepção, me abandonaram", "1 hora esperando", e até funcionária "falando mal de mim para as outras" — a assinatura do líder de volume é exatamente o pecado nº 1 da categoria (atendimento = 69% do que a praça avalia). Numa cidade onde o erro tem memória, isso é pólvora armazenada."*
- Facebook orgânico: *"OC = megafone morto (0 engaj)"*.

**CUIDADO E PREVENÇÃO (4,9 × 135, 20 anos de casa)**
- **Força:** *"É dona do território da CRIANÇA — e agora com número: 22% de todas as avaliações dela falam de filho/criança ("seu filho não ter medo de dentista", espaço temático, a doutora nomeada pelos pais — 9% citam profissional pelo nome, o dobro da nossa unidade)."* Também *"ligou uma máquina em março"* (~9 reviews/mês desde março, melhor mês 10).
- **Fraqueza:** *"Respeitável — mas não é especialista em ortodontia e não tem rede."*

**EDGARD GÓES ODONTOLOGIA (5,0 × 103, Rio Negro)**
- **Força:** *"referência da margem paranaense… vence com o dono respondendo cada avaliação e carinho com idosos"*; na busca por dentista na margem paranaense *"o consultório-referência de lá aparece em 1º com link de agendamento online"*.
- **Fraqueza:** *"Nenhum dos dois disputa o aparelho do adolescente com especialista."*

**Concorrentes menores / laterais registrados:**
- *"Especialistas locais menores: 4,7–5,0 · 7–85 avaliações."*
- **LENZ** — *"Dra. Rubia Lenz (equipe) tem clínica própria Invisalign (LENZ 4,9×52)"*, domina a busca do alinhador: *"Quem procura o alinhador invisível na cidade encontra em 1º, 3º, 4º e 5º a clínica particular de uma dentista da própria equipe — o tratamento premium vaza na busca, comprovado."*
- **Odonto Excellence** — *"chegando"*.
- **Oral Sin, Oral Unic** — *"As franquias de implante puro… ficam fora do recorte."*
- **CEO/SUS** — *"CEO/SUS sem orto; planos populares não cobrem aparelho."*

### A CONCORRÊNCIA GRATUITA (clínica-escola)
**A UnC — a universidade local.** *"a UnC (a universidade local) forma a primeira turma de ~50 dentistas entre o fim de 2026 e o início de 2027 — e uma turma nova por ano depois disso. A clínica-escola já atende a comunidade e o estágio já inclui triagem ortodôntica infantil. Tradução: em ~5 meses começa uma inundação anual de dentistas novos na praça, brigando por clínica geral e preço. A janela para consolidar a posição de ESPECIALISTA — antes que a oferta exploda — é agora."*
Memória: *"UnC abriu odonto em Mafra 2022 (clínica-escola, SEM orto)"* e *"BOMBA UnC: 1ª turma ~50 dentistas cola grau dez/26-início/27 + 50/ano depois, estágio já tem orto infantil → consolidar ESPECIALISTA antes da inundação."*

### A MÍDIA ATIVA (biblioteca pública de anúncios, corte 15/jul/2026)
| Anunciante | Anúncios ativos | Padrão criativo | Exemplos de texto real |
|---|---|---|---|
| **Instituto Lumière** | **~10** (memória registra 8 na 1ª leitura) | *"os mesmos criativos no ar há 2+ meses"*; segmentação por cidade do interior; *""Avaliação gratuita" como porta"* | *"atenção Itaiópolis"* · *"agricultores de Mafra e região"* · *"aparelho sem entrada, no boleto"* (campanha de julho) · *"avaliação gratuita"* |
| **OdontoCompany** | **~7** (memória registra 6 na 1ª leitura) | parcelamento; assinatura odontológica barata; selo de geografia das duas margens | *"12x no boleto, sem entrada"* · *"📍 Rio Negro e Mafra"* · (orgânico) *"agende agora mesmo"* |
| **OrthoDontic Mafra** | **ZERO** | *"inclusive no histórico da biblioteca (não é pausa; é ausência)"* / *"ZERO da unidade tb no histórico"* | — |

**Quem domina o leilão:** o Instituto Lumière — maior número de anúncios ativos, criativos com 2+ meses de sobrevivência (*"quem paga o mesmo anúncio por 2 meses está tendo retorno"*), geografia por cidade e agora invadindo a especialidade da unidade. *"E o detalhe que muda o jogo: a Lumière começou a anunciar APARELHO em julho — invadindo a especialidade da unidade, no pico da temporada, enquanto a especialista está calada."*

**A batalha da busca (a outra metade da guerra), verbatim:**
- *"Quem procura "aparelho ortodôntico" na cidade encontra a unidade em 1º — mas pelo perfil de rede social, porque a unidade não tem site próprio."*
- *"Quem procura o alinhador invisível na cidade encontra em 1º, 3º, 4º e 5º a clínica particular de uma dentista da própria equipe — o tratamento premium vaza na busca, comprovado."*
- *"Quem procura dentista na margem paranaense não encontra a unidade em lugar nenhum — e o consultório-referência de lá aparece em 1º com link de agendamento online."*
- *"E as perguntas que o público faz junto com essas buscas são todas de PREÇO ("qual o valor mensal de um aparelho?", "é normal ficar 7 anos de aparelho?") — pautas prontas para o conteúdo que responde antes do concorrente."*

**A síntese do tabuleiro:** *"cada vizinho é dono de um território — estrutura/implante, volume popular, criança pequena, idoso da outra margem. O território "ESPECIALISTA EM APARELHO" — que é literalmente o nome da unidade — está vago. É a bandeira mais barata e mais defensável da praça."*

---

## 9 · MERCADO

### Renda e classe
- **Renda mediana: R$ 1.333 por pessoa/mês**, em **~31 mil domicílios** — *"idêntica nas duas margens"* (Censo 2022, dado oficial / SIDRA).
- **Renda de referência do domicílio: R$ 2,8 mil** — usada na tabela de dores (*""Quanto fica por mês?" (renda ~R$ 2,8 mil)"*). Memória: *"Renda R$2,8k (operário madeira/móveis, servidor)"*.
- **Classe-alvo dos anúncios:** *"público geral, renda C"* (criativo A3 do kit).
- **Tradução do estudo:** *"praça de aparelho parcelado (entrada baixa, parcela pequena), alvo grande mas finito"*.

### Dimensionamento do público-alvo
- **~7.700 crianças e adolescentes de 9-15 anos** + **~21.000 adultos de 30-45** (Censo 2022 / SIDRA).
- **População elegível consolidada na ficha: 28.700.**
- *"cada 1% do público jovem capturado são ~77 pacientes. Aqui não se queima público: a praça não perdoa churn."*
- **Share real da unidade:** *"Share real ~34% dos tratamentos ativos da praça (677/~2.000)."*

### Sazonalidade
Série de 5 anos do comportamento de busca da região (estado de SC):
- **Pico anual: JULHO (índice 34)**, seguido de **agosto (23)** e **setembro (22)**. *"Férias + volta às aulas + a grande festa da cidade em setembro."*
- **Vale: dezembro e janeiro (2,5–7,9)** — *"a tese "férias de fim de ano" que vale em outras regiões NÃO vale aqui. O verão do litoral não é o verão do planalto."* Memória: *"DERRUBOU a candidata "férias dez/jan" (sazonalidade é VARIÁVEL por UF)."*
- **Confirmação por dentro:** *"julho/25 foi o maior mês de interessados do ano (4.120 — quatro vezes a média), batendo com a curva de busca de 5 anos. Julho/26, até o dia 12: 69. A torneira está desligada no pico. Os dados internos também confirmam que dez/jan não é temporada aqui (494 e 78)."*
- **A urgência:** *"a temporada de captação de Mafra é JUL-SET — e este estudo foi entregue em julho. Cada semana de silêncio agora é a temporada inteira escapando."*
- **As DUAS ONDAS de férias (detalhe tático):** *"as duas margens entram de férias em datas DIFERENTES (calendários oficiais das duas redes estaduais): a margem paranaense sai dia 13/07 e volta 27/07; a catarinense sai 23/07 e volta 03/08. A janela combinada da praça vai de 13/07 a 02/08 — e o criativo troca de margem no dia 23. Quem programa uma janela única desperdiça metade da cidade."* — **divergência entre arquivos:** a memória registra *"DUAS ONDAS de férias (PR 13-24/07, SC 23/07-02/08, criativo troca margem dia 23!)"* e o kit registra *"Férias PR: até 27/07 · férias SC: 23/07-02/08"*. As três versões estão nos arquivos; a data de volta do PR diverge (27/07 × 24/07).

### Âncora de preço
- **Não há faixa de preço numérica nos arquivos.** O kit deixa placeholders explícitos: *"o tratamento com aparelho fixo fica entre R$ [X] e R$ [Y] por mês"*, e o checklist exige *"Faixas reais de preço/parcela pro script 5a e anúncio A3"*.
- **As âncoras narrativas usadas no lugar do número:** *"preço justo reconhecido"*; *"Parcela transparente, "cabe no orçamento" — sem leilão de desconto"*; *"parcelas que cabem no orçamento, no boleto, sem surpresa no contrato e sem taxa escondida"*; *"parcelamento no boleto"*; *"parcela que cabe no bolso"*.
- **As âncoras do mercado (concorrência):** OdontoCompany — *"12x no boleto, sem entrada"* + *"assinatura odontológica barata"*; Lumière — *"aparelho sem entrada, no boleto"* + *"avaliação gratuita"*.
- **Contexto de renda que ancora a decisão:** renda mediana R$ 1.333/pessoa/mês; renda de referência R$ 2,8 mil.
- **Cobertura:** *"planos populares não cobrem aparelho"*; *"CEO/SUS sem orto"*.

### Geografia de captação e expansão
- **Hoje:** a unidade *"joga só o lado catarinense"*; *"Metade da praça sem luta. A margem paranaense (Rio Negro, ~31 mil hab) é atendida pela rede concorrente; a unidade não fala com ela."*
- **Expansão prioritária:** *"Reivindicar as duas margens + o interior (geotargeting Rio Negro e cidades vizinhas, criativo por cidade)"* — ação 6 do plano, prazo 60 dias.
- **Cidades do interior nomeadas para criativo por cidade (kit, A5):** **Itaiópolis, Papanduva, Quitandinha, Campo do Tenente, Monte Castelo**.
- **A geografia que o concorrente ensinou:** *"a geografia invertida do vizinho funciona (2+ meses no ar)"*; ele anuncia *"atenção Itaiópolis"* e *"agricultores de Mafra e região"*.
- **Distâncias que moldam o mercado:** *"especialidade só viajando ~2h"*; *"Curitiba 115km"*; *"o polo universitário e o emprego ficam a ~2h"*.
- **A promessa geográfica da rede:** *"a OrthoDontic tem centenas de unidades no Brasil — ele continua de onde parou, em qualquer cidade."*

---

## 10 · A JOIA ENTERRADA

*"A joia enterrada (a história que ninguém pode copiar)"* — cap. 08, verbatim:

- **"O casal de ortodontistas que voltou pra casa."** *"Já publicado na imprensa local: em 2019, os dois decidiram voltar à cidade natal para abrir a clínica. De 2 dentistas para 9 especialistas — crescimento paciente a paciente, o oposto exato do foguete de capital da porta ao lado."* (memória: publicado pelo Mafra Mix, matéria dos 6 anos.)
- **"A especialista assina com nome e registro."** *"Responsável técnica com especialidade em Ortodontia registrada — num raio de 70 metros onde se vende aparelho sem nenhum ortodontista nomeado."* (memória: Dra. Vanessa, CRO12379/SC, especialista ORTO, RT + CNES.)
- **"O sobrenome está no mapa."** *"A família é da colônia que fundou a região — há ruas com o sobrenome nas DUAS cidades (validar a linha familiar com a clínica antes de publicar)."* (memória: *"Stoeberl = sobrenome bucovino c/ RUAS nas 2 cidades (⚠️ validar parentesco)"*; checklist: *"Genealogia Stoeberl (só usar "família da colônia" com confirmação)"*.)
- **"A rede como garantia, não como fachada:"** *""clínica de gente daqui, com a segurança de uma rede nacional — e se seu filho for estudar fora, o tratamento continua em qualquer unidade do Brasil." Nenhum vizinho pode dizer nenhuma das duas metades dessa frase."*

**Por que está enterrada:** *"A história está no cofre… e o feed não conta. Numa praça onde confiança é sobrenome, é o maior ativo parado da cidade."* Memória: *"A PEPITA… O antídoto ao "franquia=forasteiro" (Elias/Scotson) JÁ EXISTE e está escondido atrás da fachada."*

**Joias secundárias que a unidade também não conta:** *"patrocina a comunidade (escoteiros)"* (⚠️ *"@passeiopedrabranca NÃO é escoteiros de Mafra (é Palhoça) — handle real a confirmar"*); *"7 anos de sorrisos concluídos"* — *"o único conteúdo que a vizinha de 9 meses não consegue ter"*; ser **a única clínica especializada em ortodontia da praça**.

---

## 11 · TERRITÓRIOS DE CAMPANHA, TOM E FORMATOS

### Os 4 territórios de campanha (cap. 13, verbatim)
1. **"A especialista daqui"** — *"o casal que voltou pra casa, o nome, o registro, os 7 anos, os 9 especialistas. A resposta estrutural à vizinha sem rosto e à rede sem alma."*
2. **"Aparelho é com especialista"** — *"reocupar o nome da casa: quem acompanha um tratamento de anos é ortodontista com registro, não "nossos especialistas" genérico."*
3. **"Nas duas margens da ponte"** — *"Mafra inteira: geotargeting incluindo Rio Negro e o interior (a geografia que a vizinha ensinou, com a mensagem que ela não tem)."*
4. **"O dia de tirar o aparelho"** — *"o review de RESULTADO: 7 anos de sorrisos concluídos, o único conteúdo que a vizinha de 9 meses não consegue ter."*

### O tom
*"**Tom:** sóbrio, concreto, de palavra cumprida — prova antes de promessa. Mafra sempre (as duas margens). O frio como cúmplice, não como piada."*
Kit: *"Tom obrigatório da praça: sóbrio, concreto, palavra cumprida."*
Registro do documento (prompt de design): *"consultoria sênior, analítica, com calor humano. Documento de inteligência — não é peça de venda."*
Proibições: ver seção 5.

### Os formatos fixos de feed
Regra do kit: *"4 formatos fixos em rodízio. 3 posts/semana + stories diários simples."* Feed **80% ortodontia** (ação 4: *"Reocupar a especialidade no feed (80% ortodontia: bastidor, explica-tudo, o dia de tirar o aparelho)"*).

Os formatos nomeados no calendário de 30 dias:
- **"Explica-tudo #N"** — responde a pergunta real da busca. #1 *"Quanto custa um aparelho por mês?"* (*"a pergunta nº1 da região na busca — responder de frente, com faixas e parcelamento"*); #2 *"Dói pra colocar?" + "é normal ficar 7 anos de aparelho?"* (*"a resposta honesta é diferencial"*); #3 *"Meu filho vai estudar fora — e o aparelho?"* (*"o argumento de rede que ninguém na praça tem"*).
- **"Conheça quem cuida #N"** — #1 *"[DRA. NOME], especialista em ortodontia (CRO/SC [nº]) — 3 perguntas rápidas em vídeo (por que ortodontia? o que mais gosta? um conselho pra quem tem medo)"*; #2 *"a recepção pelo nome (as pessoas que a audiência já ama)"*.
- **"O dia de tirar o aparelho"** — *"primeiro depoimento de resultado [paciente com autorização]. Formato-âncora — repetir todo mês."*
- **"Bastidor"** — *"a manutenção mensal como ritual (a cor da borrachinha do mês — cumplicidade com o adolescente, nunca bronca)."*
- **"Prova social do mês"** — *"print de 3 reviews reais (anonimizados) + o número do mês ("X famílias avaliaram a gente em julho — obrigado, Mafra")."*
- **Posts de território/comunidade:** *"Viemos pra casa"* (post-manifesto), *"Mafra é uma cidade só"*, o patrocínio/comunidade (*"sem autoelogio, só presença"*), *"O inverno como cúmplice"*.
- **Stories diários (rodízio simples):** *"bastidor da manhã · enquete boba ("borrachinha azul ou verde?") · resposta a 1 dúvida · repost de marcação."*

### O calendário editorial de 30 dias (estrutura literal)
- **SEMANA 1 — A HISTÓRIA (o destravamento do rosto):** S1P1 *"Viemos pra casa"* · S1P2 *Conheça quem cuida #1* · S1P3 *Explica-tudo #1*.
- **SEMANA 2 — A ESPECIALIDADE:** S2P1 *O dia de tirar o aparelho* · S2P2 *Explica-tudo #2* · S2P3 *Bastidor*.
- **SEMANA 3 — AS DUAS MARGENS:** S3P1 *"Mafra é uma cidade só"* · S3P2 *Conheça quem cuida #2* · S3P3 *Explica-tudo #3*.
- **SEMANA 4 — A COMUNIDADE:** S4P1 *O patrocínio dos escoteiros* · S4P2 *O inverno como cúmplice* · S4P3 *Prova social do mês*.

### Os 6 anúncios do kit (ação 5 — clique-WhatsApp)
- **A1 · O ROSTO** — mãe 28-50, Mafra + 10km.
- **A2 · AS DUAS MARGENS** — Rio Negro + interior PR (*"criativo A2 troca de margem dia 23/07"*).
- **A3 · O PREÇO CLARO** — público geral, renda C.
- **A4 · O FILHO QUE VAI EMBORA** — pais 40-55.
- **A5 · O INTERIOR** — Itaiópolis, Papanduva, Quitandinha, Campo do Tenente, Monte Castelo (criativo POR CIDADE).
- **A6 · A AVALIAÇÃO COM A ESPECIALISTA** — *"(neutraliza a isca do vizinho)"*.
Métrica: *"custo por conversa iniciada e custo por avaliação agendada, por criativo, semanal. Matar o pior, escalar o melhor, nunca menos que 4 ativos."*

### Rádio
- **4a. Testemunhal 30s** — *"programa vespertino de Rio Negro (locutor-personagem)"*.
- **4b. Spot 15s** — *"FM principal (rotativo, manhã + fim de tarde)"*.

---

## 12 · PLANO DE AÇÃO

**O PLANO DE 90 DIAS (cap. 15) — ordem de execução com evidência, KPI, prazo, esforço→impacto e dono (tabela verbatim):**

| # | Ação | Evidência que sustenta | KPI / meta | Prazo | Esforço→Impacto | Dono |
|---|---|---|---|---|---|---|
| 1 | **Blindar a manutenção E a retenção** (protocolo de confirmação/remarcação + régua de relacionamento nos meses 2-6 + alerta de paciente sumido + cobrança humanizada preventiva) e assumir a promessa "manutenção mensal de verdade" | a única ferida própria + a ferida documentada do concorrente + a safra que para de pagar entre o mês 3 e o 6 (dados internos) | nota ≥ 4,8 · safra pagando no m6 +10 pontos | 15 dias | baixo→ALTO | unidade |
| 2 | **Ligar a máquina de avaliações** (pedir a cada paciente satisfeito + responder 100%) com prioridade ao review de tratamento CONCLUÍDO | gap de volume 3,4x; a vizinha faz 22/mês pedindo; review de resultado é incopiável | ≥15 avaliações novas/mês → ultrapassar o líder de volume em ~14 meses | 15 dias | baixo→alto | unidade |
| 3 | **Destravar o rosto** — a história do casal no feed, na fachada, na ficha pública e nos anúncios | a praça premia pessoas; ciência do "de fora"; a história já foi publicada na imprensa local | engajamento/feed local; avaliações citando nomes | 30 dias | baixo→alto | unidade+agência |
| 4 | **Reocupar a especialidade no feed** (80% ortodontia: bastidor, explica-tudo, o dia de tirar o aparelho) | o território do próprio nome está vago; hoje o feed briga nos territórios dos vizinhos | share de posts de orto | 30 dias | baixo→alto | agência |
| 5 | **Entrar na mídia paga JÁ — o pico é agora** (4-6 anúncios sempre-ativos: rosto + especialista + parcela clara + mensagem direta), programada nas DUAS ondas de férias: margem PR até 27/07, margem SC 23/07-02/08, criativo trocando de margem dia 23 | pico anual jul-set (série de 5 anos) + calendários escolares oficiais das 2 redes; 0 ads vs 10+7; o criativo sobrevivente do vizinho valida o formato | custo por avaliação agendada; 4-6 ativos | **7-14 dias** | médio→alto | agência |
| 6 | **Reivindicar as duas margens + o interior** (geotargeting Rio Negro e cidades vizinhas, criativo por cidade) | 526 avaliações do concorrente vêm das duas margens; a geografia invertida do vizinho funciona (2+ meses no ar) | % pacientes novos de fora de Mafra | 60 dias | médio→médio | agência |
| 7 | **Parcerias de comunidade** (futsal 9-15 anos, maternidade, perfil-indicador) + presença na festa de setembro | mapa da atenção; o decisor está na arquibancada; 18 mil pessoas na festa | pacientes por indicação rastreada | 90 dias | médio→médio | unidade+agência |

**O teste que fecha o diagnóstico:** *"um cliente-oculto padronizado (roteiro pronto, entregue junto deste estudo) medirá o funil de resposta da unidade E dos concorrentes — antes e depois do plano. A pergunta-armadilha do roteiro: "se meu filho for estudar fora, dá problema?" — apostamos que só uma clínica da praça tem resposta para ela."* (Memória: *"teste-funil-kit.md (cliente oculto, roteiro mãe do piá 12 anos + pergunta-armadilha "se ele estudar fora?") pronto p/ equipe London executar (NUNCA no pacote do cliente — tem nomes/fones de concorrentes)."*)

**Ação 8 — medição (kit):** *"planilha semanal — conversas iniciadas · avaliações agendadas · comparecimento · reviews novos · nota. Monitor mensal roda em agosto; review de 90 dias em outubro."*

**Protocolos operacionais que acompanham as ações (kit):**
- Reviews: pedido por QR na recepção, mensagem pós-manutenção *"até 2h depois da consulta"*, pedido presencial no dia de tirar o aparelho, **resposta a 100% dos reviews em até 48h**.
- WhatsApp: *"TODA mensagem respondida em <30 min em horário comercial."*
- Manutenção: lembrete na véspera; *"Falta sem aviso: ligar no MESMO dia e reagendar em até 7 dias. Paciente sem manutenção há 35+ dias = alerta na planilha da recepção."*
- Parcerias (ação 7): escolinha de futsal (uniforme + *"Sorriso do Atleta do Mês"*), maternidade regional (palestra *"saúde bucal do bebê"* — *"é semear confiança 10 anos antes da venda"*), perfil-indicador (publi trimestral), **prêmio local + guia do comércio (CDL): "aderir JÁ"**.

**Checklist de validação interna antes de publicar qualquer peça (kit, verbatim):**
*"[ ] Grafia oficial e CRO dos dois — e AUTORIZAÇÃO de imagem do casal · [ ] O Dr. é ortodontista ou endodontista de registro? (peça A1 cita "casal de ortodontistas" só se confirmado) · [ ] Genealogia Stoeberl (só usar "família da colônia" com confirmação) · [ ] Faixas reais de preço/parcela pro script 5a e anúncio A3 · [ ] Handle e nome corretos do grupo escoteiro · [ ] Situação da profissional com clínica própria de alinhadores (definir a política de Invisalign ANTES de anunciar alinhador) · [ ] Autorização de cada paciente em depoimento/foto (termo simples, LGPD) · [ ] Link curto de avaliação Google testado no QR"*

**Pendências do projeto (memória, 16/jul):** *"gerar PDF no Claude Design (prompt embutido); rodada cliente-oculto (humano); validações internas c/ clínica (lista no dossiê história); monitor mensal a partir de ago; review 90 dias ~out/26."*

---

## 13 · PAINEL DE PONTEIROS

*"Este estudo não termina em recomendação: termina em medição armada. Seja qual for o ponteiro que importa para a rede, ele está neste painel — com baseline congelado na data do estudo e meta de 90 dias."*

**BLOCO A — ponteiros de PRESENÇA** *(medidos de fora, todo mês, automaticamente — baseline já congelado em 15/jul/2026)*
| Ponteiro | Hoje | Meta 90 dias |
|---|---|---|
| Avaliações novas/mês | 0,7 | **≥15** |
| Nota | 4,9 | ≥4,8 (manter) |
| Volume total de avaliações | 155 | ~200 |
| Anúncios ativos | 0 | 4-6 sempre-ativos |
| Posição na busca local da categoria | 1º (sem site) | 1º + presença na margem PR |
| Gap de volume vs líder (2 margens) | 3,4x | em queda mês a mês |

**BLOCO B — ponteiros COMERCIAIS** *(baseline real dos dados internos, 2026)*
| Ponteiro | Hoje | Meta 90 dias |
|---|---|---|
| Agendamento (interessado → avaliação agendada) | **6%** (11% em jun) | **maior ou igual a 20%** — rumo à régua de 40% |
| Comparecimento | 49% | manter na régua (50%) |
| Fechamento | 75-96% | manter (já acima da régua) |
| Interessados/mês | em rajadas (de 69 a 4.120) | fluxo constante de 400+/mês |

**BLOCO C — ponteiros de RESULTADO** *(baseline real)*
| Ponteiro | Hoje | Meta 90 dias |
|---|---|---|
| Base de pacientes ativos | **677 (caindo ~8/mês há 24 meses)** | **estancar a queda até o mês 3** |
| Contratos pagos/mês | **~28** (2025: ~43 · meta da rede: 50) | 40+, rumo à meta de 50 |
| Safra ainda pagando no 6º mês | ~40-55% (validar quitação × abandono) | +10 pontos |
| Atendimentos vs ano anterior | menos 12% | curva revertendo |
| % pacientes de Rio Negro/interior | a medir no 1º mês | crescer (a metade cedida da praça) |

**A engrenagem (verbatim):** *"todo mês, o mesmo pipeline do estudo recoleta o Bloco A e compara — com alerta automático se a nota cair, se a máquina de avaliações desacelerar ou se um concorrente novo entrar anunciando. A unidade alimenta os Blocos B e C numa planilha simples. Em 90 dias, o painel inteiro responde com números o que virou ponteiro — e em 180, vira o case replicável da rede."*

**Nota política (memória):** *"ALINHAR COM PAULA QUAIS PONTEIROS valem p/ a renovação antes do review (avaliações agendadas? contratos? faturamento?) p/ medir o que a decisão precisa."*

---

## 14 · DADOS INTERNOS / BI

**Origem:** *"DADOS INTERNOS RECEBIDOS (16/jul, prints do BI Conecta da rede — 340 unidades ativas; dossiê dados-internos-conecta.md)"*. Classificação da unidade no BI: **"Madura", safra 2019**.
**Enquadramento do capítulo 14 ("A PROVA DOS NOVE"):** *"Tudo até aqui foi construído de fora, sem nenhum dado interno. Com o diagnóstico fechado, a rede abriu os números da unidade — e eles fazem as duas coisas que um cruzamento pode fazer: confirmam o estudo e apontam o milímetro exato do vazamento."*

### O FUNIL (2026)
**5.050 interessados → 298 agendamentos (6%) → 147 comparecimentos (49%) → 110 fechados (75%) → 109 pagos (99%)**

### A RÉGUA DA REDE (para o mesmo funil)
**agendamento 40% · comparecimento 50% · fechamento 80% · pagamento 90%**

**A leitura:** *"quem chega, fecha. Quem chama, some."* — *"O comparecimento bate a régua (49% ≈ 50%), o fechamento e o pagamento estão ACIMA dela (75-99%) — a cadeira e o contrato funcionam. O único estágio quebrado é o primeiro: de cada 100 interessados, só 6 viram avaliação agendada — a régua da rede espera 40."*

### BASE DE PACIENTES
- **875 (ago/24) → 677 (jul/26)** = **-23% em dois anos**, *"uma sangria de ~8 pacientes/mês"*.
- **Atendimentos:** **-12% vs 2025 (mesma loja)** — memória: **5.617 → 4.940**.
- **Share real:** *"~34% dos tratamentos ativos da praça (677/~2.000)"*.
- **Higiene de agenda:** *"Sem agendamento futuro só 17 (higiene de agenda ok)."*

### CONTRATOS
- **2025: ~43/mês** · **2026: ~28/mês** · **meta da rede: 50/mês** · **julho, até o dia 12: 13**.
- Origem: *"As campanhas respondem por ~6 de cada 10 contratos; o resto vem de indicação e balcão."*

### INTERESSADOS (leads) — o padrão de rajada
- **jul/25 = 4.120** — *"o maior mês de interessados do ano (quatro vezes a média), batendo com a curva de busca de 5 anos"*.
- **jul/26 até o dia 12 = 69** — *"A torneira está desligada no pico."*
- **dez = 494 · jan = 78** — *"confirmam que dez/jan não é temporada aqui"*.
- *"os interessados chegam em RAJADAS de campanha — e na rajada o agendamento desaba (a linha de frente afoga). O plano troca rajada por fluxo constante, com resposta em minutos."*
- Agendamento: **6% no ano, 11% em junho**.

### O PRÊMIO, EM NÚMERO (com os MESMOS interessados de 2026)
| Agendamento | Contratos/ano (projeção) | vs hoje |
|---|---|---|
| 6% (hoje) | ~110 | — |
| **20% (metade da régua)** | **~370** | **3,4x** |
| 40% (a régua da rede) | ~740 | 6,7x |

*"(Projeção sobre o funil de campanhas, que gera ~60% dos contratos; o efeito total é maior, porque a mesma linha de frente atende indicação e balcão.)"*

### A SAFRA DE PAGAMENTO (a segunda sangria)
*"A análise por safra de contrato mostra que, em várias safras, só metade dos contratos continua pagando entre o 3º e o 6º mês — e 20-35% no 12º. Num tratamento de anos, queda tão cedo não é conclusão de contrato: é abandono, inadimplência ou quitação antecipada (o mix exato é uma validação interna — mas o formato da curva é alarme). As duas sangrias se somam: entra pouco (6% de agendamento) e parte do que entra escorre (a safra que para de pagar). Por isso a ação 1 do plano ganha uma camada de RETENÇÃO: régua de relacionamento nos meses 2-6, alerta de paciente sumido e cobrança humanizada preventiva — numa praça finita, reter vale mais que adquirir."*
No painel (Bloco C), o baseline registrado é **~40-55% ainda pagando no 6º mês (validar quitação × abandono)**, com meta de **+10 pontos**.

**Fecho:** *"Nenhuma outra alavanca da unidade tem o tamanho dessas duas. É por isso que o plano a seguir começa pela linha de frente e pela retenção — e é assim que uma base que derrete há 24 meses volta a crescer."* Memória: *"O piloto agora é business case com prêmio quantificado."*

---

## 15 · CITAÇÕES REAIS

### A · VOZES REAIS COLETADAS (público espontâneo, corpus de 452 vozes)
1. **"A melhor clínica e os melhores dentistas!!!"** — seguidor da unidade, comentário público espontâneo; é o HERO do estudo. Atribuição do arquivo: *"seguidor da unidade, comentário público espontâneo. A cidade já sabe quem são os melhores. A comunicação é que ainda não conta."*
2. **"os melhores dentistas!!! Saudades"** — audiência do Instagram da unidade (memória, diagnóstico do IG: *"ZERO rosto — audiência ama as pessoas"*).
3. **"Loja linda, família linda, equipe linda!"** — *"o comentário mais afetuoso do corpus é para um comércio local"* (voz da cidade, não da clínica).
4. **"Ótimo atendimento, preço justo e lugar aconchegante"** — avaliação pública da própria unidade.
5. **"Clínica limpa e cheirosa, ambiente super agradável e profissionais mto atenciosos"** — avaliação pública da própria unidade.
6. **"falta de comunicação entre a equipe… fiquei 1 mês sem manutenção"** — *"A única mancha"* da unidade; *"(a ferida a blindar, e é operacional, não clínica)"*.
7. **"meu filho é cuidado há 4 anos"** — pai/mãe em avaliação; evidência de que *"a decisora é a mãe"*.
8. **"minha filha de 11 anos"** — idem.
9. **"não consegui passar da recepção, me abandonaram"** — avaliação negativa da OdontoCompany.
10. **"1 hora esperando"** — avaliação negativa da OdontoCompany.
11. **"falando mal de mim para as outras"** — avaliação negativa da OdontoCompany, sobre funcionária.
12. **"assinei contrato que oferecia limpeza… nunca recebi; só entregaram a prótese quando terminei os pagamentos."** — *"a única avaliação negativa com texto"* do Instituto Lumière, jan/26.
13. **"seu filho não ter medo de dentista"** — trecho das avaliações da Cuidado e Prevenção (22% delas falam de filho/criança).
14. **"QUEM É DAQUI ACESSA!"** — bio da maior página da praça (@riomaframixoficial, 53k); o YAML comenta: *"puro endogrupo"*.
15. **"qual o valor mensal de um aparelho?"** — pergunta pública do público na busca (PAA).
16. **"é normal ficar 7 anos de aparelho?"** — pergunta pública do público na busca (PAA).

### B · FALAS DOS CONCORRENTES (anúncios e comunicação reais)
17. **"atenção Itaiópolis"** — anúncio do Instituto Lumière, segmentação por cidade do interior.
18. **"agricultores de Mafra e região"** — anúncio do Instituto Lumière.
19. **"aparelho sem entrada, no boleto"** — campanha de julho do Instituto Lumière, a invasão da ortodontia. (Memória: *"INVADIU a orto em jul/26 ("sem entrada no boleto")"*.)
20. **"avaliação gratuita"** / **"Avaliação gratuita"** — a isca/porta do Instituto Lumière nos anúncios.
21. **"12x no boleto, sem entrada"** — anúncio da OdontoCompany.
22. **"📍 Rio Negro e Mafra"** — anúncio da OdontoCompany.
23. **"agende agora mesmo"** — legenda repetida da OdontoCompany; o estudo classifica como *"comunicação de megafone vazio"*.
24. **"eleito ortodontista destaque do ano"** — título obtido por um concorrente via o circuito de prestígio local por adesão. (Memória: *"Grahl "eleito ortodontista destaque" 2022"*.)
25. **"safira"** — memória, munição anti-OdontoCompany no Reclame Aqui: *"vendeu "safira" entregou cerâmica + NEGATIVOU mãe no SPC; manutenção "mensal" trimestral."*

### C · FALAS DE STAKEHOLDERS (memória de projeto)
26. **"agora é valendo"** — Paula, decisora da OrthoDontic, ao pedir o piloto em Mafra (15/07/2026).
27. **"precisa virar alguns ponteiros de resultado"** — Paula, sobre a unidade de Mafra em negociação de renovação de contrato de franquia (áudio de 15/jul, transcrito).
28. **"formatar um tipo de CONSULTORIA PRA REDE como um todo"** — Paula, endgame confirmado por ela.
29. **"clínica dentária"/beclinique = PT** — nota de coleta no YAML e na memória: *"CUIDADO: existe Mafra em PORTUGAL"*.

### D · FRASES-ÂNCORA DO PRÓPRIO ESTUDO (London Creative)
30. **"A melhor clínica da cidade é a mais calada."** — a tese; título da capa: **"A Melhor Clínica da Cidade É a Mais Calada"**.
31. **"O problema da unidade não é qualidade. É presença. E presença se resolve."**
32. **"Falar "Mafra" é falar de dentro; tratar Rio Negro como outra cidade é o erro do forasteiro."**
33. **"Desconfia de promessa grande; respeita trabalho, constância e palavra cumprida."**
34. **"esperar, viajar ou desistir"** — a ferida da cidade. (Memória: *"SAÚDE = "esperar, viajar (Curitiba 115km) ou desistir""*.)
35. **"Os primeiros pacientes definem a reputação dos próximos anos; um paciente mal atendido é uma emissora de rádio."**
36. **"Indicação não é um canal de marketing: é O canal de decisão."**
37. **"O antídoto documentado: um rosto local na frente, a rede como garantia atrás."**
38. **"Sorrisos de Mafra e Rio Negro"** vale mais que **"milhões no Brasil"**. (Memória: **"300 sorrisos em Mafra" > "milhões no Brasil"**.)
39. **"a mãe que caiu no golpe"** — o custo social do erro. *"Clareza e garantia valem mais que desconto."*
40. **"se o seu filho for estudar fora, o tratamento continua em qualquer unidade do Brasil."**
41. **"clínica de gente daqui, com a segurança de uma rede nacional — e se seu filho for estudar fora, o tratamento continua em qualquer unidade do Brasil."** — *"Nenhum vizinho pode dizer nenhuma das duas metades dessa frase."*
42. **"A OrthoDontic somou 10 avaliações em 14 meses. A Lumière fez 72 num único mês."**
43. **"Volume de reputação é construção deliberada, não acaso."**
44. **"Todo mundo na praça está correndo — a unidade está estacionada."**
45. **"a assinatura do líder de volume é exatamente o pecado nº 1 da categoria"** … **"Numa cidade onde o erro tem memória, isso é pólvora armazenada."**
46. **"o território "ESPECIALISTA EM APARELHO" — que é literalmente o nome da unidade — está vago."** / **"o território ESPECIALISTA EM APARELHO está vago"**
47. **"É a bandeira mais barata e mais defensável da praça."**
48. **"A história está no cofre."**
49. **"o maior ativo parado da cidade"**
50. **"Cada paciente satisfeito que sai sem avaliar é um tijolo que o concorrente coloca no muro dele."**
51. **"o oposto exato do foguete de capital da porta ao lado."**
52. **"O casal de ortodontistas que voltou pra casa."**
53. **"validar a linha familiar com a clínica antes de publicar"** / **"a validar com a clínica"**
54. **"o pico anual de procura é AGORA — julho a setembro."**
55. **"Cada semana de silêncio agora é a temporada inteira escapando."**
56. **"O verão do litoral não é o verão do planalto."**
57. **"Quem programa uma janela única desperdiça metade da cidade."**
58. **"não é pausa; é ausência"** — sobre os zero anúncios da unidade.
59. **"quem paga o mesmo anúncio por 2 meses está tendo retorno"**
60. **"pautas prontas"** — sobre as perguntas de preço na busca.
61. **"Quem chegar primeiro nesses territórios fala sozinho."**
62. **"Se a especialista de verdade não ocupa o título, o título fica com quem chegar primeiro."**
63. **"manutenção mensal DE VERDADE"** / **"manutenção mensal de verdade"**
64. **"você controla o ritmo"**
65. **"quem chega, fecha. Quem chama, some."** / **"Quem chega, fecha; quem chama, some."**
66. **"responder em minutos não é operação, é posicionamento"**
67. **"numa praça finita, reter vale mais que adquirir."**
68. **"uma base que derrete há 24 meses volta a crescer."**
69. **"se meu filho for estudar fora, dá problema?"** — a pergunta-armadilha do cliente-oculto. (Memória: *"se ele estudar fora?"*)
70. **"apostamos que só uma clínica da praça tem resposta para ela."**
71. **"em 90 dias, o painel responde com números o que virou ponteiro"**
72. **"o silêncio digital daqui é característica, não ausência de opinião."**
73. **"Mafra — o piloto — vira o primeiro cérebro vivo da rede: o que funcionar aqui vira aprendizado testável nas outras centenas de unidades."**
74. **"A janela para consolidar a posição de ESPECIALISTA — antes que a oferta exploda — é agora."**
75. **"o marketing mais eficiente é engenharia de indicação."**
76. **"reputação de líder, comunicação de coadjuvante."**
77. **"a vizinha que ultrapassou tem 9 meses de vida e nenhuma raiz."**
78. **"O frio como cúmplice, não como piada."**
79. **"prova antes de promessa."**
80. **"tem seguidores, não tem comunidade"**
81. Eyebrow: **"Pesquisa de público · Ortodontia · Mafra/SC — piloto aplicado"**; subtítulo de capa: **"Estudo-piloto · Ortodontia · Mafra/SC · com plano de 90 dias"**; rodapé de capa: **"Inteligência de mercado por London Creative · julho 2026"**.
82. Setup narrativo anotado no prompt de design: **"então está tudo bem…"**
83. **"o triplo de contratos com os mesmos interessados."**

### E · COPY PRODUZIDA PELA LONDON PARA A UNIDADE (kit de execução — peças, não vozes coletadas)
84. QR na recepção: *"Gostou de como te tratamos hoje? Conta pra Mafra — leva 1 minuto e ajuda outra família a escolher com confiança."*
85. Pós-manutenção: *"Oi, [NOME]! Aqui é a [RECEPCIONISTA], da OrthoDontic. Obrigada pela visita de hoje 💙 Se puder, deixa sua avaliação aqui — pra gente é o maior obrigado que existe, e ajuda outras famílias de Mafra e Rio Negro: [link curto]"*
86. Review de resultado: *"Hoje é o seu dia! Se quiser contar como foi o tratamento inteiro — do primeiro dia até hoje — sua história vale ouro pra quem ainda tem medo de começar."* — *"É o único review que uma clínica de 9 meses não consegue pedir."*
87. Resposta a review positivo: *"Obrigado, [NOME]! Cuidar de você é um orgulho pra nossa equipe. Um abraço da [DRA. NOME] e de todos aqui. 💙"*
88. Resposta a review negativo: *"Sentimos muito, [NOME] — não é o padrão que a gente promete. A [RESPONSÁVEL] vai te chamar hoje pra resolver. Obrigado por nos avisar."* — *"(e LIGAR de verdade — em cidade pequena, a resolução vira contra-história)"*
89. **A1 · O ROSTO:** *"Aparelho é um tratamento de anos. Por isso, aqui em Mafra, quem acompanha o seu filho do primeiro ao último dia é ortodontista especialista de verdade: a [DRA. NOME] (CRO/SC [nº]) — mafrense, há 7 anos no mesmo endereço. Avaliação com a especialista: agende pelo WhatsApp."*
90. **A2 · AS DUAS MARGENS:** *"Do lado de lá da ponte também é Mafra. A clínica especializada em aparelho do Alto de Mafra atende as duas margens — com hora marcada e a mesma especialista do início ao fim. Agende pelo WhatsApp."*
91. **A3 · O PREÇO CLARO:** *"Quanto custa um aparelho? Aqui a resposta é clara antes de você assinar qualquer coisa: parcelas que cabem no orçamento, no boleto, sem surpresa no contrato e sem taxa escondida. Avaliação com a especialista — agende."*
92. **A4 · O FILHO QUE VAI EMBORA:** *"Seu filho começou o aparelho e vai estudar fora? Aqui o tratamento não para: a OrthoDontic tem centenas de unidades no Brasil — ele continua de onde parou, em qualquer cidade. Só uma rede pode prometer isso. E só a nossa tem uma especialista mafrense cuidando do começo."*
93. **A5 · O INTERIOR:** *"[CIDADE], o aparelho do seu filho não precisa de aventura: no Alto de Mafra, com ortodontista especialista, hora marcada e parcelamento no boleto. Vale a viagem — uma vez por mês, com dia e hora respeitados."*
94. **A6 · A AVALIAÇÃO COM A ESPECIALISTA:** *"Avaliação ortodôntica com a especialista + plano de tratamento explicado por inteiro: o que precisa, quanto tempo leva, quanto custa por mês. Você sai sabendo tudo — e decide em casa, sem pressão. Agende pelo WhatsApp."*
95. **Rádio 4a (testemunhal 30s):** *"Ó, gente… sabe aquela história de marcar dentista e esperar uma hora? Na OrthoDontic, no Alto de Mafra, é hora marcada DE VERDADE — e quem cuida do aparelho da piazada é ortodontista especialista, gente daqui. Das duas margens, todo mundo é bem recebido. Liga lá ou chama no WhatsApp: [fone]. OrthoDontic — a especialista em aparelho de Mafra."*
96. **Rádio 4b (spot 15s):** *"Aparelho é com especialista. OrthoDontic Mafra: ortodontista de verdade, hora marcada, parcela que cabe no bolso. Rua Felipe Schmidt, Alto de Mafra. WhatsApp [fone]."*
97. **WhatsApp 5a (preço):** *"Oi, [NOME]! Boa pergunta — e a gente responde de verdade: o tratamento com aparelho fixo fica entre R$ [X] e R$ [Y] por mês, dependendo do caso, no boleto, sem entrada obrigatória e sem surpresa no contrato. O valor exato sai na avaliação com a Dra. [NOME], que te explica tudo antes de qualquer assinatura. Quer que eu veja um horário pra você?"*
98. **WhatsApp 5b ("é pra meu filho"):** *"Que bom que você está cuidando disso agora — a avaliação certa na idade certa evita tratamento maior depois. Aqui quem avalia é a própria especialista, e a primeira consulta é pra explicar tudo pra VOCÊ, sem compromisso. Prefere de tarde ou sábado de manhã?"*
99. **WhatsApp 5c (a pergunta-armadilha):** *"Pode ficar tranquila: a OrthoDontic tem centenas de unidades no Brasil. Se ele for estudar em outra cidade, o tratamento continua de onde parou, sem começar do zero e sem pagar de novo. É a única clínica da região que pode garantir isso."*
100. **WhatsApp 5d (véspera da manutenção):** *"Oi [NOME]! Lembrete da manutenção de amanhã às [hora]. Confirma pra gente? Se precisar mudar, a gente já encaixa outro dia — sem buraco no seu tratamento. 💙"*
101. **Post-manifesto S1P1:** *"Viemos pra casa"* … *"Mafra e Rio Negro: obrigado por esses 7 anos."*
102. **S3P1:** *"Mafra é uma cidade só"*
103. **S4P2:** *"cuidar de você enquanto lá fora geia"*
104. **S4P3:** *"X famílias avaliaram a gente em julho — obrigado, Mafra"*
105. **Stories:** *"borrachinha azul ou verde?"*
106. **Parceria futsal:** *"Sorriso do Atleta do Mês"* · abordagem: *"queremos apoiar o esporte que forma a piazada das duas cidades."*
107. **Parceria maternidade:** *"saúde bucal do bebê"* — *"(a Dra. em pessoa — é semear confiança 10 anos antes da venda)"*.
108. **Prêmio local:** *"aderir JÁ — se o título "ortodontista destaque do ano" existe por adesão, ele tem que ser da especialista de verdade, não de quem chegar primeiro."*
109. **Explica-tudo (pautas):** *"Quanto custa um aparelho por mês?"* · *"Dói pra colocar?"* · *"é normal ficar 7 anos de aparelho?"* · *"Meu filho vai estudar fora — e o aparelho?"*

---

## 16 · TODOS OS NÚMEROS

| Métrica | Valor | Fonte / N |
|---|---|---|
| Vozes reais analisadas (corpus total) | **452** | corte 15/jul/2026, corpus do estudo |
| Vozes de pacientes com texto (categoria inteira, 2 cidades) | **224** | base da classificação temática, corte 15/jul/2026 |
| Comentários de Instagram coletados (3 páginas cidade + clínica) | **183** | memória de projeto |
| Reviews Google coletados por clínica no 1º lote | **100 cada** (unidade, OC Mafra, OC RN); **~120 com texto** | memória de projeto |
| Corpus após o 1º lote | **~300 vozes** | memória de projeto |
| % de reviews que fala de ATENDIMENTO | **69%** | N=224, corte 15/jul/2026 |
| % qualidade/resultado | **54%** | N=224 |
| % recomendação explícita | **30%** | N=224 |
| % autoestima | **12%** | N=224 |
| Índice de atendimento nas 3 praças anteriores | **54%, 47%, 63%** | comparativo do cap. 04 |
| Índice de atendimento com recorte estrito de ortodontia (praças anteriores) | **54-63%** | nota de método do cap. 04 |
| Reviews 5 estrelas nos últimos 100 da unidade | **97** | cap. 04 / cap. 07 |
| Nota × avaliações — OrthoDontic Mafra | **4,9 × 155** | placar jul/2026 |
| Nota × avaliações — OdontoCompany Mafra | **4,7 × 338** | placar jul/2026 |
| Nota × avaliações — Instituto Lumière | **5,0 × 197** | placar jul/2026 |
| Nota × avaliações — OdontoCompany Rio Negro | **4,7 × 188** | placar jul/2026 |
| Nota × avaliações — Cuidado e Prevenção | **4,9 × 135** | placar jul/2026 |
| Nota × avaliações — Edgard Góes Odontologia | **5,0 × 103** | placar jul/2026 |
| Nota × avaliações — especialistas locais menores | **4,7–5,0 × 7–85** | placar jul/2026 |
| Nota × avaliações — LENZ (clínica de dentista da equipe) | **4,9 × 52** | memória de projeto |
| Soma OdontoCompany nas duas margens | **526** (338+188) | placar |
| Gap de volume vs líder das 2 margens | **3,4x** | painel Bloco A |
| Tempo para a unidade fazer 155 avaliações | **7 anos** | cap. 05 |
| Tempo para a Lumière fazer 197 avaliações | **9 meses** | cap. 05 |
| Clínicas na mesma rua (corredor odontológico) | **4** | cap. 05 / memória (R. Felipe Schmidt) |
| Distância da Lumière até a unidade | **70 metros** (F. Schmidt 1204) | cap. 06 / memória |
| Velocity — OrthoDontic | **0,7 reviews/mês**; melhor mês **4** | série 14 meses, corte 15/jul/2026 |
| Velocity — OdontoCompany Mafra | **~13/mês**; melhor mês **33 (mai/26)** | série 14 meses |
| Velocity — Instituto Lumière | **~28/mês desde jan**; melhor mês **72 (mar/26)** | série 14 meses |
| Velocity — Cuidado e Prevenção | **~9/mês desde mar**; melhor mês **10** | série 14 meses |
| Avaliações da unidade em 14 meses | **10** | série de velocity |
| Ritmo de avaliações da Lumière na 1ª visita | **~22/mês** | cap. 06 |
| Capital social da Lumière vs unidade | **28x maior**; **R$ 840k** | registro público / memória |
| Abertura da Lumière (CNPJ) | **out/2025** | registro público |
| Idade da Lumière no corte | **9 meses** | cap. 06 |
| Avaliações negativas com texto — OdontoCompany | **14**, todas de recepção e espera | cap. 06 |
| Avaliações negativas com texto — Lumière | **1** (jan/26), sobre contrato | cap. 06 |
| % das avaliações da Cuidado e Prevenção que falam de filho/criança | **22%** | cap. 06 |
| % das avaliações da Cuidado e Prevenção que citam profissional pelo nome | **9%** (*"o dobro da nossa unidade"*) | cap. 06 |
| Anos de casa — Cuidado e Prevenção | **20 anos** | placar / cap. 06 |
| Anúncios ativos — Instituto Lumière | **~10** (memória registra **8** na 1ª leitura) | biblioteca pública, corte 15/jul/2026 |
| Anúncios ativos — OdontoCompany | **~7** (memória registra **6**) | biblioteca pública, corte 15/jul/2026 |
| Anúncios ativos — OrthoDontic | **0**, inclusive no histórico | biblioteca pública, corte 15/jul/2026 |
| Tempo no ar dos criativos sobreviventes da Lumière | **2+ meses** | biblioteca pública |
| Posições da clínica de alinhadores da funcionária na busca "invisalign mafra" | **1º, 3º, 4º e 5º** | raw/serp.json |
| Posição da unidade em "aparelho ortodôntico" | **1º** (via perfil de rede social, sem site próprio) | raw/serp.json |
| Posição da unidade na busca da margem paranaense | **ausente** | raw/serp.json |
| Formatura da 1ª turma da UnC | **~50 dentistas**, fim de 2026 / início 2027; **~50/ano** depois | agente-dados-duros |
| Prazo até a inundação de dentistas novos | **~5 meses** | cap. 06 |
| Ano de abertura do curso de odontologia da UnC em Mafra | **2022** | memória |
| Índice de busca — julho | **34** | série de 5 anos (SC), trends_sc.csv |
| Índice de busca — agosto | **23** | série de 5 anos |
| Índice de busca — setembro | **22** | série de 5 anos |
| Índice de busca — dezembro/janeiro (vale) | **2,5–7,9** | série de 5 anos |
| Férias escolares margem PR | sai **13/07**, volta **27/07** (memória: **13-24/07**; kit: **até 27/07**) | calendários oficiais das redes estaduais |
| Férias escolares margem SC | sai **23/07**, volta **03/08** (kit e cap. 15: **23/07-02/08**) | calendários oficiais |
| Janela combinada da praça | **13/07 a 02/08**, criativo troca de margem **dia 23** | cap. 09 |
| População da praça (malha contínua) | **~87 mil** | cap. 02 / memória |
| População Mafra/SC | **55 mil** | memória |
| População Rio Negro/PR | **31 mil** | memória / cap. 07 |
| Ano de fundação da colônia | **1829** | cap. 02 |
| DDD comum | **47** | memória |
| Crianças e adolescentes 9-15 anos | **~7.700** | Censo 2022 / SIDRA |
| Adultos 30-45 anos | **~21.000** | Censo 2022 / SIDRA |
| População elegível (ficha) | **28.700** | ficha_mafra.json |
| Domicílios | **~31 mil** | Censo 2022 |
| Renda mediana por pessoa/mês | **R$ 1.333** — *"idêntica nas duas margens"* | Censo 2022 |
| Renda de referência do domicílio | **R$ 2,8 mil** | cap. 12 / memória |
| Pacientes por 1% do público jovem capturado | **~77** | cap. 02 |
| Share real da unidade nos tratamentos ativos da praça | **~34%** (677 / ~2.000) | BI Conecta |
| Seguidores da maior página da região | **53 mil** | mapa da atenção |
| Seguidores @diarioderiomafra | **23k** | YAML |
| Seguidores @clickriomafra | **20k** (desde 2007) | YAML |
| Seguidores da agenda pública (prefeitura/prefeito) | **24-25 mil** | mapa da atenção |
| Seguidores do Instagram da unidade | **2,1k** | memória |
| Público da grande festa de setembro | *"dezenas de milhares"* / **18 mil pessoas** | cap. 11 / plano ação 7 |
| Data da grande festa | **MAFRA FEST 5-8/set** | memória |
| Frequências de rádio vendidas por um único balcão | **3 das 4 relevantes** (Rede Nova) | agente-dados-duros |
| Potência da emissora que cobre a região | **15 kW** | cap. 11 |
| Ano de fundação da Rádio Nova Era | **1986** | memória |
| Ano do título "ortodontista destaque" de um concorrente | **2022** | memória |
| Compartilhamentos do post mais compartilhado da cidade (FB) | **34 shares** | agente-mapa-influencia |
| Distância até Curitiba | **115 km** | memória |
| Tempo de viagem para especialidade / polo universitário | **~2h** | cap. 02 / cap. 03 |
| Brasileiros que dizem confiar na maioria das pessoas | **~7%** | literatura citada no cap. 03 |
| Prevalência estimada de SAD subclínico (inverno) | **20%** | memória (ciência) |
| Ano da neve que virou memória afetiva | **2013** | cap. 02 / memória |
| **FUNIL 2026 — interessados** | **5.050** | BI Conecta |
| **FUNIL 2026 — agendamentos** | **298 (6%)** | BI Conecta |
| **FUNIL 2026 — comparecimentos** | **147 (49%)** | BI Conecta |
| **FUNIL 2026 — fechados** | **110 (75%)** | BI Conecta |
| **FUNIL 2026 — pagos** | **109 (99%)** | BI Conecta |
| Régua da rede — agendamento | **40%** | BI Conecta |
| Régua da rede — comparecimento | **50%** | BI Conecta |
| Régua da rede — fechamento | **80%** | BI Conecta |
| Régua da rede — pagamento | **90%** | BI Conecta |
| Agendamento em junho/26 | **11%** | painel Bloco B |
| Base de pacientes ativos — ago/24 | **875** | BI Conecta |
| Base de pacientes ativos — jul/26 | **677** | BI Conecta |
| Queda da base em 2 anos | **-23%**, ~**8 pacientes/mês** (24 meses) | BI Conecta |
| Atendimentos YoY | **-12%** (**5.617 → 4.940**) | BI Conecta, mesma loja |
| Contratos pagos/mês — 2025 | **~43** | BI Conecta |
| Contratos pagos/mês — 2026 | **~28** | BI Conecta |
| Meta da rede para a unidade | **50 contratos/mês** | BI Conecta |
| Contratos em julho/26 até o dia 12 | **13** | BI Conecta |
| Participação das campanhas nos contratos | **~6 de cada 10 (~60%)** | BI Conecta |
| Interessados jul/25 | **4.120** (*"quatro vezes a média"*) | BI Conecta |
| Interessados jul/26 até dia 12 | **69** | BI Conecta |
| Interessados dezembro | **494** | BI Conecta |
| Interessados janeiro | **78** | BI Conecta |
| Pacientes sem agendamento futuro | **17** | BI Conecta |
| Prêmio — agendamento 6% (hoje) | **~110 contratos/ano** | projeção sobre o funil de campanhas |
| Prêmio — agendamento 20% | **~370 contratos/ano (3,4x)** | projeção |
| Prêmio — agendamento 40% (régua) | **~740 contratos/ano (6,7x)** | projeção |
| Safra ainda pagando entre o 3º e o 6º mês | **~metade** (painel: **~40-55%**) | análise por safra, BI |
| Safra ainda pagando no 12º mês | **20-35%** | análise por safra, BI |
| Unidades da rede (memória/BI) | **~350** / **340 ativas** | memória / BI Conecta |
| Crescimento da equipe da unidade | **de 2 dentistas para 9 especialistas** | cap. 08 |
| CRO da responsável técnica | **CRO 12379/SC** (Dra. Vanessa Stoeberl Gomes) | memória |
| CRO citado do marido | **CRO 8682** (endodontia — validar) | memória |
| Meta de avaliações novas/mês | **≥15** | plano ação 2 / painel A |
| Prazo para ultrapassar o líder de volume | **~14 meses** (ultrapassar 338) | plano ação 2 / kit |
| Meta de anúncios ativos | **4-6 sempre-ativos** (*"nunca menos que 4"*) | plano ação 5 / kit |
| Meta de volume total de avaliações em 90 dias | **~200** | painel A |
| Meta de nota | **≥4,8 (manter)** | painel A |
| Meta de fluxo de interessados | **400+/mês constante** | painel B |
| Meta de contratos/mês em 90 dias | **40+** | painel C |
| Meta da safra no 6º mês | **+10 pontos** | painel C / plano ação 1 |
| Prazos do plano | **7-14 dias** (ação 5) · **15 dias** (1 e 2) · **30 dias** (3 e 4) · **60 dias** (6) · **90 dias** (7) | cap. 15 |
| SLA de resposta a reviews | **100%, em até 48h** | kit |
| SLA de resposta no WhatsApp | **<30 min em horário comercial** | kit |
| Janela da mensagem pós-manutenção | **até 2h depois da consulta** | kit |
| Prazo de reagendamento após falta sem aviso | **até 7 dias** (ligar no mesmo dia) | kit |
| Gatilho de alerta de paciente sumido | **35+ dias sem manutenção** | kit |
| Posts por semana no calendário editorial | **3 posts/semana + stories diários**; **4 formatos fixos** em rodízio | kit |
| Anúncios prontos no kit | **6 (A1-A6)** | kit |
| Scripts de WhatsApp no kit | **4 (5a-5d)** | kit |
| Peças de rádio no kit | **2 (30s e 15s)** | kit |
| Itens do checklist de validação interna | **8** | kit |
| Alvos declarados no YAML | **18** (16 habilitados, 2 desabilitados) | targets_orthodontic_mafra.yaml |
| Temas do léxico ortodôntico | **7** | lexico_orthodontic.yaml v1.1 |
| Custo do Lote 5 de coleta | **~US$ 0,9** | memória |
| Crédito das chaves de coleta | quintessential_creeper **~4,6 livre**; yawning_celeriac **$5** | memória |
| ID da taxonomia | **bd67982156e8** | memória |
| Datas do ciclo de medição | monitor mensal a partir de **ago/26**; review de 90 dias em **out/26** | kit / memória |
| Nº de gaps do briefing do sistema | **20** | memória |
| Nº de capítulos do conteúdo | **17 caps + prompt PDF** (renumerados 14-17 → 15-18 após o cap. 14 novo) | memória |
| Nº de páginas do mapa do PDF | **P1 a P21** (+ P9b, P17b se necessário) | prompt de design |

---

## 17 · LIMITES METODOLÓGICOS

**O QUE O ESTUDO VÊ (verbatim):** *"a voz espontânea pública (sem viés de entrevistador), a reputação comparada das duas margens, a mídia ativa de cada concorrente, a temporada de busca, a cultura do território, o registro público das empresas."*

**O QUE NÃO VÊ (verbatim):** *"quem desistiu no orçamento e não escreveu; quem nunca considerou aparelho; as conversas nos grupos fechados da cidade (onde parte do boca a boca acontece); o share real de receita."*

**VIESES CONHECIDOS (verbatim):** *"avaliações públicas concentram extremos; cidade pequena comenta pouco em público — o silêncio digital daqui é característica, não ausência de opinião."*

**O QUE VALIDA OU DERRUBA NA FASE 2 (verbatim):** *"o cliente-oculto (kit pronto), uma pesquisa declarada curta, entrevistas com desistentes de orçamento — e a escuta de dentro (a máquina que aprende)."*

**Ressalvas adicionais explicitadas nos arquivos:**
- **Nota de método do 69%:** *"como as clínicas da praça são todas multi-serviço, a base inclui pacientes de toda a odontologia local"* — a base **não é** de ortodontia pura.
- **Nota de recorte do placar:** *"o placar compara REPUTAÇÃO, não produto"*; franquias de implante puro (Oral Sin, Oral Unic) ficam fora do recorte.
- **Escopo geográfico da série de busca:** *"Série de 5 anos do comportamento de busca da região (estado de SC)"* — é dado estadual, não municipal.
- **A projeção do prêmio é projeção:** *"(Projeção sobre o funil de campanhas, que gera ~60% dos contratos; o efeito total é maior…)"*
- **A safra de pagamento carrega mix não decomposto:** *"é abandono, inadimplência ou quitação antecipada (o mix exato é uma validação interna — mas o formato da curva é alarme)"*; o painel registra *"(validar quitação × abandono)"*.
- **Validações pendentes com a clínica:** genealogia Stoeberl (*"validar a linha familiar com a clínica antes de publicar"*), registro/especialidade do marido, handle correto do grupo escoteiro (*"@passeiopedrabranca NÃO é escoteiros de Mafra (é Palhoça)"*), faixas reais de preço, política de alinhadores, autorizações de imagem (LGPD).
- **Risco de coleta:** *"existe Mafra em PORTUGAL… Filtrar tudo por SC/Brasil."*
- **Divergências internas entre os arquivos (registradas, não resolvidas):** contagem de anúncios ativos (10+7 no conteúdo × 8+6 na memória); data de retorno das férias do PR (27/07 × 24/07); idade do Instagram da unidade (*"6 anos, ~2019"*) × os *"7 anos"* usados no texto; grafia do nome do sócio ("Luiz Henrique Gomes" × "Luis Henrique de Abreu Gomes"); fechamento no painel B aparece como **"75-96%"** enquanto o funil do cap. 14 traz **75%**.
- **Trava de conteúdo do entregável:** *"usar SOMENTE o que está neste arquivo (TRAVA — nada de dado inventado); números sempre com N e data de corte em nota discreta"*; *"nenhum nome próprio de PESSOA além do que o arquivo traz"*; *"Varredura sigilo limpa, sem nomes próprios (validações ⚠️ pendentes c/ clínica)."*
- **O que não pode ir para o cliente:** o roteiro de cliente-oculto — *"NUNCA no pacote do cliente — tem nomes/fones de concorrentes."*

---

## 18 · ACHADOS ÚNICOS DESTA PRAÇA

1. **O nome do estudo estava errado.** *"O primeiro achado corrige o próprio nome do estudo: a praça não é "Mafra" — é RIOMAFRA."* Uma colônia de 1829 partida ao meio pela divisa dos estados; mesmo DDD 47, ônibus urbano cruzando a ponte, ~87 mil pessoas, mídia local inteira chamada Mafra. **Nenhuma outra praça do método teve o próprio recorte geográfico reescrito pelo achado.**
2. **69% de atendimento — o recorde das 4 praças estudadas** (as anteriores: 54%, 47%, 63%). *"Aqui, mais que em qualquer lugar, o paciente avalia COMO FOI TRATADO."*
3. **A maior colônia bucovina do mundo.** *"alemães-boêmios (bucovinos — Mafra é a maior colônia bucovina do mundo)"* — e a proibição de tom que decorre disso: *"Jamais gíria gaúcha, jamais estética de Oktoberfest — aqui a colônia é outra."*
4. **A sazonalidade invertida.** *"Dezembro e janeiro são VALE (2,5–7,9) — a tese "férias de fim de ano" que vale em outras regiões NÃO vale aqui. O verão do litoral não é o verão do planalto."* Memória: *"DERRUBOU a candidata "férias dez/jan" (sazonalidade é VARIÁVEL por UF)."* — **um achado que corrige a metodologia da rede inteira, não só esta praça.**
5. **As DUAS ONDAS de férias.** Duas redes estaduais, dois calendários, uma cidade — *"o criativo troca de margem no dia 23. Quem programa uma janela única desperdiça metade da cidade."* Só existe porque a praça é interestadual.
6. **A vizinha de 9 meses a 70 metros que fez 72 avaliações num único mês** enquanto a unidade fazia 10 em 14 meses — e que *"acabou de invadir a ortodontia"* no pico da temporada.
7. **O território do próprio nome está vago.** *"a OrthoDontic é a ÚNICA clínica da praça especializada em ortodontia"* e, ao mesmo tempo, *"o feed abandonou a especialidade"*. O território *"ESPECIALISTA EM APARELHO"* — *"que é literalmente o nome da unidade"* — sem dono.
8. **O vazamento interno na busca:** *"Quem procura o alinhador invisível na cidade encontra em 1º, 3º, 4º e 5º a clínica particular de uma dentista da própria equipe."*
9. **A joia do sobrenome no mapa.** *"A família é da colônia que fundou a região — há ruas com o sobrenome nas DUAS cidades."* O antídoto ao *"franquia = forasteiro"* já existia, engavetado.
10. **O rádio se compra num telefonema:** *"um único balcão comercial vende 3 das 4 frequências relevantes, incluindo a emissora de 15 kW que cobre a região inteira."*
11. **O prestígio local funciona por adesão:** *"um concorrente já foi "eleito ortodontista destaque do ano" por essa via."* O título de especialista da praça está à venda, e não é da especialista.
12. **As três lacunas de atenção:** *"não existe página de humor da cidade, não existe mãe-influencer local e não existe criador de vídeo local."*
13. **A ferida da cidade é SAÚDE, não dinheiro:** *"esperar, viajar ou desistir"* — e uma especialidade com hora marcada na própria rua ataca a dor mais documentada da cidade.
14. **A inundação de dentistas com data marcada:** a UnC forma **~50 dentistas** entre o fim de 2026 e o início de 2027, e ~50/ano depois — *"a janela para consolidar a posição de ESPECIALISTA… é agora."*
15. **É a única praça com dados internos do BI** — e o cruzamento produziu o diagnóstico cirúrgico da rede: **"quem chega, fecha. Quem chama, some."** O único estágio quebrado é interessado→agendamento (6% contra régua de 40%).
16. **A segunda sangria, invisível de fora:** *"em várias safras, só metade dos contratos continua pagando entre o 3º e o 6º mês — e 20-35% no 12º."*
17. **O prêmio quantificado:** *"o triplo de contratos com os mesmos interessados"* — 6%→20% = **3,4x**; 6%→40% = **6,7x**. Memória: *"O piloto agora é business case com prêmio quantificado."*
18. **Esta praça fez o léxico da rede subir de versão:** *"v1.1: auditoria da amostra (Mafra) pegou variantes femininas/nominais ausentes na base"* — e produziu a **1ª ficha validada do sistema** (ficha_mafra.json) e o **monitor_praca.py (M5)**.
19. **O enquadramento diplomático como ativo:** *"enquadramento "melhor clínica, mais calada" é diplomaticamente perfeito p/ renovação (elogia a qualidade do franqueado, problema é presença = solucionável, motiva em vez de acusar)"* — a única praça em que o estudo é, ao mesmo tempo, **ferramenta de renovação de contrato de franquia**.
20. **O destino do piloto:** *"Mafra — o piloto — vira o primeiro cérebro vivo da rede: o que funcionar aqui vira aprendizado testável nas outras centenas de unidades."*

---

# ⚠️ LAUDO DE AUDITORIA DESTE DOSSIÊ

_Auditor independente releu os arquivos-fonte e conferiu este dossiê linha por linha._

**Veredito:** HÁ ERROS — mas nenhum deles é numérico-de-dado nem citação adulterada. Conferi UM A UM todos os números do dossiê contra as fontes (placar 4,7×338 / 5,0×197 / 4,7×188 / 4,9×155 / 4,9×135 / 5,0×103 / 4,7–5,0×7–85; velocity 0,7-4 / ~13-33 mai/26 / ~28-72 mar/26 / ~9-10; 452 vozes; N=224; 69/54/30/12%; anteriores 54/47/63%; 97 de 5 estrelas; 526 e 3,4x; funil 5.050→298(6%)→147(49%)→110(75%)→109(99%); régua 40/50/80/90; 875→677 = -23% e ~8/mês; 5.617→4.940 = -12%; contratos ~43/~28/50/13; leads 4.120/69/494/78; 17 sem agendamento; prêmio ~110/~370/~740 = 3,4x/6,7x; safra ~metade e 20-35% e painel ~40-55%; 340 ativas vs ~350; 87k/55k/31k/1829/DDD 47; 7.700+21.000=28.700; R$1.333; R$2,8k; ~31 mil domicílios; ~77 por 1%; 34% (677/~2.000); busca 34/23/22 e vale 2,5–7,9; 53k/23k/20k/24-25 mil/2,1k; capital 28x e R$840k; 22% e 9%; 14 negativas da OC e 1 da Lumière; ~10 e ~7 ads (8 e 6 na memória); 15 kW; 3 das 4 frequências; 34 shares; 115 km; ~7%; SAD 20%; 18 alvos 16/2; 7 temas; 8 itens de checklist; ~US$0,9; 20 gaps; P1–P21) — TODOS batem. Conferi também palavra por palavra as ~109 citações, incluindo as 26 peças de copy do kit (A1–A6, scripts 5a–5d, rádio 4a/4b, QR, respostas a review), as falas da Paula, as negativas da OdontoCompany e da Lumière, a nota de método do 69%, a nota de recorte do placar, as brechas da Lumière, as duas ondas de férias e a engrenagem do painel: as aspas batem, sem adulteração. O léxico foi reproduzido termo a termo nos 7 temas, sem erro; a lista de 18 alvos do YAML está correta, inclusive queries, handles, max_posts/comments e os 2 desabilitados. O QUE ENCONTREI: (1) um erro numérico real — "17 capítulos" quando CONTEUDO-MAFRA.md tem 18 (o "17" é a contagem pré-cap.14 da memória); (2) três erros de atribuição — "guia do comércio (CDL)" e o texto integral do alerta de Portugal creditados à memória (são do kit e do YAML), e os 70 m creditados ao cap. 06; (3) três invenções/extrapolações apresentadas como fato, todas concentradas na seção 18 do dossiê — "nenhuma outra praça teve o recorte geográfico reescrito", "a única praça em que o estudo é ferramenta de renovação" e "um achado que corrige a metodologia da rede inteira" — nenhuma delas existe nos arquivos; (4) quatro imprecisões menores (nome do "projeto" vs "estudo", o corte 15/jul colado no placar, os ordinais 2ª/3ª numa pergunta só, e a citação do YAML filada como fala de stakeholder). AS OMISSÕES SÃO O PONTO MAIS FRACO: o dossiê engoliu o cap. 18 inteiro (a máquina que aprende / LGPD), o propósito declarado da Página 2, o cap. 03 sem nenhuma fonte científica nomeada, quase todo o prompt de design (formato PDF travado, proibições duras, os dois design systems, a estrutura em 4 atos) e — mais grave — deixou de registrar a divergência de que o RODAPÉ do estudo ainda diz "Tudo construído de fora, sem nenhum dado interno" apesar do cap. 14 e da memória afirmarem que o rodapé foi ajustado. Resumo: dossiê confiável para números e citações; incompleto para método, ciência, entregável e camada política; e com três afirmações de superlativo ("nenhuma outra praça", "a única praça") que precisam ser removidas ou marcadas como inferência.

**Erros apontados (11):**

1. Nº de capítulos do conteúdo — dossiê (§16): "17 caps + prompt PDF (renumerados 14-17 → 15-18 após o cap. 14 novo)" — fonte: CONTEUDO-MAFRA.md tem 18 capítulos numerados (01 a 18, terminando em '## 18 · A máquina que aprende (fase 2)'). O '17 caps' da memória é a contagem ANTERIOR ao cap. 14 novo; a própria memória registra 'caps renumerados 14-17→15-18'. Ao publicar '17' como o número de capítulos do conteúdo, o dossiê contradiz o arquivo.
2. Atribuição de 'guia do comércio (CDL)' — dossiê (§5, bloco 'Dois atalhos'): lista *"guia do comércio (CDL)"* entre as citações precedidas de 'Memória:' — fonte: a memória de projeto NÃO contém 'guia do comércio' nem 'CDL' em lugar nenhum. A expressão vem do KIT-EXECUCAO-MAFRA.md §6 ('Prêmio local + guia do comércio (CDL): aderir JÁ') e, sem o '(CDL)', do CONTEUDO cap. 11 ('o guia do comércio').
3. Atribuição do alerta de coleta — dossiê (§2): 'Alerta de coleta gravado no YAML **e na memória**: "CUIDADO: existe Mafra em PORTUGAL — 'clínica dentária'/beclinique = PT. Filtrar tudo por SC/Brasil."' — fonte: esse texto integral existe SÓ no targets_orthodontic_mafra.yaml (linhas 88-89). A memória traz apenas a versão curta 'CUIDADO: existe Mafra em PORTUGAL (filtrar SC/BR).' — sem 'clínica dentária', sem 'beclinique', sem 'Filtrar tudo por SC/Brasil'.
4. Invenção (§18, achado 1) — dossiê: '**Nenhuma outra praça do método teve o próprio recorte geográfico reescrito pelo achado.**' — fonte: afirmação inexistente nos cinco arquivos. Nenhum deles compara as praças quanto a recorte geográfico; a única comparação entre praças nos arquivos é o índice de atendimento (54/47/63/69).
5. Invenção (§18, achado 19) — dossiê: '**a única praça em que o estudo é, ao mesmo tempo, ferramenta de renovação de contrato de franquia**' — fonte: a memória diz apenas que a unidade de Mafra está em negociação de renovação e que 'o piloto não é aleatório: é ferramenta da renovação'. Não há nenhuma afirmação de exclusividade em relação às outras praças.
6. Extrapolação apresentada como fato (§18, achado 4) — dossiê: '**um achado que corrige a metodologia da rede inteira, não só esta praça**' — fonte: a memória registra somente '(sazonalidade é VARIÁVEL por UF)'. Nem a memória nem o conteúdo falam em corrigir metodologia de rede.
7. Atribuição de fonte da distância de 70 m — dossiê (§16): 'Distância da Lumière até a unidade | 70 metros (F. Schmidt 1204) | **cap. 06** / memória' — fonte: o cap. 06 não cita 70 metros. Os '70 m' aparecem na tabela do cap. 05, na TESE e no cap. 08 ('num raio de 70 metros'); o 'F. Schmidt 1204' só na memória e no YAML (comentário do lumiere_google, 'a 70m').
8. Paráfrase do achado-mestre (§1) — dossiê: 'o primeiro achado do estudo corrige o próprio nome do **projeto**' — fonte (cap. 02): 'O primeiro achado corrige o próprio nome do **estudo**'. O próprio dossiê cita corretamente 'estudo' em §18, contradizendo-se.
9. Classificação errada de citação (§15, item 29) — dossiê: coloca '"clínica dentária"/beclinique = PT' dentro do bloco '**C · FALAS DE STAKEHOLDERS (memória de projeto)**' — fonte: não é fala de stakeholder nem está na memória: é comentário técnico de coleta dentro do YAML.
10. Ordinal das perguntas de busca (§6) — dossiê: '"Dói pra colocar?" (**2ª/3ª perguntas da busca**, segundo o calendário editorial)' — fonte (KIT, S2P2): 'Explica-tudo #2: "Dói pra colocar?" + "é normal ficar 7 anos de aparelho?" (2ª e 3ª perguntas da busca...)' — os dois ordinais se repartem entre DUAS perguntas; o dossiê cola ambos numa só.
11. Corte atribuído ao placar (§3) — dossiê: título '**O placar da praça (as duas margens, jul/2026 — corte 15/jul/2026)**' — fonte (cap. 05): o cabeçalho é 'O placar da praça (as duas margens, jul/2026)'. O 'corte 15/jul/2026' aparece no arquivo apenas amarrado à SÉRIE DE VELOCITY ('Não é impressão: é série mensal com data (corte 15/jul/2026)'), não à tabela de notas.

**Omissões apontadas (21):**

- CAPÍTULO 18 INTEIRO ('A máquina que aprende — fase 2') praticamente ausente: o dossiê só reaproveita a frase final do 'cérebro vivo'. Ficou de fora o mecanismo: 'A palavra exata que faz o riomafrense fechar ou desistir acontece dentro da clínica, na conversa do orçamento'; 'Com o consentimento de cada paciente (LGPD), grava-se o que já acontece, a voz vira inteligência mês a mês, e a comunicação se afina sozinha: os anúncios passam a responder às objeções reais antes de o paciente entrar.'
- PÁGINA 2 · 'O QUE ESTA PESQUISA VISA' — o propósito declarado do estudo foi omitido: 'este não é um estudo para admirar — é para APLICAR. A tarefa que recebemos: encontrar onde está o problema da unidade e traçar o caminho para resolvê-lo, com evidência em cada passo.' O dossiê traz as 6 perguntas e a promessa, mas não o propósito.
- O CAP. 03 (CIÊNCIA) ficou sem seção própria e sem as fontes nomeadas: Coleman; Gluckman; Elias & Scotson; Cialdini ('experimento clássico'). Só 'Elias/Scotson' sobrevive, e via citação da memória. Também some a estrutura dos 6 blocos científicos listada no prompt (P6): 'reputação tem memória · confiança no próximo · estabelecidos × de fora · prova social provinciana · o medo duplo da mãe · os jovens vão embora'. Da memória, some 'fofoca = SO da cidade'.
- O PROMPT DE DESIGN (≈150 linhas, quase metade do arquivo de conteúdo) foi reduzido a 3 fragmentos de tom + o mapa P1-P21. Ficaram de fora: o formato travado (PDF ESTÁTICO HORIZONTAL 16:9, páginas fixas 1920×1080, @page landscape, page-break-inside: avoid, corpo ≈24px nunca <18px, numerar e assinar TODAS as páginas, entrega em HTML de página única para 'Imprimir → Salvar como PDF'); a lista de PROIBIÇÕES DURAS (animação, @keyframes, scroll/overflow, hover, accordion, carrossel, aba, tooltip, sticky, JavaScript de comportamento, vídeo/GIF, fonte/imagem externa, 100vh); os DOIS design systems com papéis distintos (LONDON = anfitrião/assinatura; ORTHODONTIC = conteúdo); e a regra estrutural 'A ORDEM É SAGRADA — o PDF é uma INVESTIGAÇÃO em 4 ATOS' (Ato I A CIDADE, Ato II A CATEGORIA, Ato III O PROBLEMA em 4 camadas, Ato IV A VIRADA), com a instrução de não adiantar a tese antes de P13.
- DIVERGÊNCIA INTERNA NÃO REGISTRADA (a mais séria que o dossiê deixou passar): o RODAPÉ do CONTEUDO ainda afirma 'Tudo construído de fora, sem nenhum dado interno.' — enquanto o cap. 14 e o HERO usam dados internos do BI, e a memória declara 'hero/rodapé ajustados ("construído de fora, validado por dentro")'. O rodapé NÃO foi ajustado. O dossiê cita o rodapé cortando exatamente essa frase.
- MÉTODO EM DUAS VERSÕES: o dossiê só reporta os '7 movimentos'. O cabeçalho do arquivo traz outra cadeia, de 11 passos: 'alma da cidade → ciência → pacientes → placar → playbook dos vizinhos → raio-X → temporada → guerra de anúncios → mapa da atenção → plano de 90 dias → medição.'
- HERO: some a afirmação metodológica 'tudo de fora, **sem briefing**' (subtítulo do hero), que é uma das travas de credibilidade do estudo.
- MEMÓRIA — bloco da Paula: omitidos os itens (1) 'ela mostrou o estudo pra LORAINE... (confirmado pelo Luciano; o material chega direto ao topo da rede)'; (3) 'PAULA vai fazer ela mesma um plano de ação p/ estruturar com a unidade a partir do estudo → nosso plano de 90 dias + kit devem ser fáceis de ELA adotar como dela'; (5) 'ela vai reportar a evolução dos resultados → parceira do review de 90 dias'. O dossiê só chama Paula de 'campeã interna'.
- MEMÓRIA — briefing do Luciano omitido por inteiro: 'profundidade máxima (antropologia+neurociência), usar quantas chaves precisar, achar ONDE ESTÁ O PROBLEMA e resolver. Método de [[projeto-orthodontic-rede-franqueadora]] + camada ciência nova.' — inclusive o vínculo com o projeto-pai da rede franqueadora.
- MEMÓRIA — achado estratégico omitido: 'Feridas da praça são TODAS de franquia.' (fecho do item 5 do diagnóstico). É uma leitura de tabuleiro que não aparece em lugar nenhum do dossiê.
- MEMÓRIA — omitidos: o entregável em .zip ('output_ortho_mafra/pacote-apresentacao-mafra/ ... + .zip', 'Varredura limpa, zip refeito') e 'ficha (share 34, **4 KPIs internos**)'.
- MEMÓRIA (ciência) — omitido o argumento na forma como está escrito: 'evasão jovem → argumento "aparelho = futuro do filho + continua em qualquer unidade da rede se ele for estudar fora"'. O dossiê guarda só a segunda metade.
- CAP. 14 — omitida a frase que amarra o dado interno ao achado externo: '(a ferida nº 1 da praça inteira é recepção que abandona; responder em minutos não é operação, é posicionamento)'. O dossiê guarda só a segunda metade (citação 66). A mesma tese reaparece no KIT §5 ('A ferida nº1 do concorrente é recepção que abandona — nossa resposta rápida É o posicionamento') e também foi omitida.
- CAP. 11 — 'As três parcerias prioritárias' na formulação do estudo: a maternidade como 'a clínica no momento de máxima atenção da mãe' e o perfil-indicador como 'publi neutra nas duas margens'; e o 'uniforme + "sorriso do atleta do mês"'. O dossiê só traz a versão operacional do kit.
- KIT — omitido que o documento é o 'Módulo 6 do sistema' e que os placeholders ([DRA. NOME]/[DR. NOME]/[FOTO]) devem ser 'preenchidos após validação interna'.
- KIT — divergência de meta de nota não registrada: o kit fixa 'Meta: ≥15 reviews novos/mês · **manter 4,9** · ultrapassar 338 em ~14 meses', enquanto o painel A e a ação 1 do plano usam '≥4,8 (manter)'. O dossiê só reporta o ≥4,8.
- KIT — omitidas condições operacionais das peças: 1a é 'display de balcão, arte com o rosto da equipe'; 1b só vai 'para paciente que saiu satisfeito — recepção sinaliza'; 1c tem a meta 'TODO paciente que conclui tratamento recebe esse convite'; 1d positivo pede 'citar algo específico do review quando possível'.
- KIT — omitidas todas as direções de imagem dos 6 anúncios ([FOTO da Dra. e do Dr. na clínica], [FOTO ponte/equipe], [FOTO recepção], [FOTO adolescente/formatura], [FOTO fachada]) e o enquadramento da janela ('Janela de lançamento: AGORA (pico jul-set) ... Depois: sempre-ativos'). Também some que o RÁDIO é parte da ação 7 e se resolve com 'cotação num telefonema'.
- PLACAR / FESTA — o dossiê registra 'dezenas de milhares de pessoas' (cap. 11) e '18 mil pessoas na festa' (cap. 15) lado a lado sem apontar que são estimativas incompatíveis; essa divergência ficou fora da lista de 'divergências internas' de §17.
- FORMATOS DE FEED — o dossiê reproduz a regra '4 formatos fixos em rodízio' e depois lista 6+ formatos nomeados no calendário (Explica-tudo, Conheça quem cuida, O dia de tirar o aparelho, Bastidor, Prova social do mês, posts de território/comunidade) sem sinalizar a incoerência do próprio kit.
- YAML — o dossiê conta '18 alvos' sem notar que o handle riomaframixoficial aparece DUAS vezes (riomaframix_ig raso e riomaframix_deep_ig), ou seja, são 17 alvos distintos; e omite o campo 'platform' e a instrução de versionamento do léxico ('Estrutura idêntica à taxonomia base. Mudou? Suba a versão e registre.').
