# Como escrever neste projeto

> A regra: **quem lê é a diretoria da OrthoDontic, não quem construiu o
> sistema.** Se a palavra existe só porque foi assim que a gente fez, ela não
> entra na tela.

---

## O troca-troca

| Não escrever | Escrever |
|---|---|
| taxonomia | **lista de palavras** |
| taxonomia v1.1 | **lista de palavras · versão 1.1** |
| hipótese | **sinal isolado** |
| candidata | **se repete** |
| constante | **vale para a rede** |
| doutrina | **virou regra** |
| derrubada | **caiu** |
| corpus | **o que foi coletado** |
| coorte | **unidades parecidas** |
| baseline | **ponto de partida** |
| snapshot | **coleta do dia** |
| append-only | **só acrescenta, nunca apaga** |
| velocity | **ritmo de avaliações novas** |
| procedência | **de onde veio o número** |
| contra-evidência | **o que pesa contra** |
| registro do criativo | **o jeito que o anúncio fala** |
| share de posts | **quantos por cento dos posts** |
| digital rastreável | **o que dá para ver na internet** |
| o denominador não reconcilia | **as contas não fecham** |
| sub-tese | **a parte que dizia que…** |
| artefato de busca | **erro da busca** |
| medidor radial | **medidor redondo** |
| controle segmentado | **botões de trocar o período** |
| estado vazio | **quando não tem dado** |
| classificação temática | **separar por assunto** |
| índice de resposta | **quantas a clínica respondeu** |
| geotargeting | **mostrar o anúncio só naquela região** |
| pay-per-event | **paga por item coletado** |

---

## A UF vem antes do nome da cidade. Sempre.

**`MG · Contagem`**, nunca `Contagem/MG` nem `Contagem - MG`.

Vale na tela do portal, no relatório, no e-mail e no nome de arquivo. Três
motivos, e o primeiro já custou caro:

**Cidade homônima é armadilha real.** Existe Palmas no Tocantins e no Paraná.
Existe Palmas de Monte Alto na Bahia. A coleta já entrou contaminada por isso
— a prefeitura de Palmas/PR foi tratada como se fosse a nossa. **Com a UF na
frente, o erro salta aos olhos antes de virar dado.**

**Numa lista de 340 unidades, a leitura agrupa sozinha.** `MG ·`, `MG ·`,
`MG ·`, `MT ·` — o olho separa por estado sem precisar de coluna extra e sem
ordenar nada.

**Ordena certo por padrão.** Ordem alfabética de `MG · Contagem` já é ordem por
estado. Ordem alfabética de `Contagem/MG` é ordem por acaso.

Praça com mais de uma cidade repete a UF em cada uma:
**`SC · Mafra`** — porque é exatamente isso que ela é, uma
cidade partida pela divisa.

O rótulo pronto está em `dados/identidade/<praca>.json`, campo `rotulo`, e o
código está em `scripts/rotulo.py`. **Ninguém deve montar isso à mão.**

---

## O que a gente NÃO troca

São as palavras da própria rede. Usar elas é falar de dentro:

**ponteiros** (os números que a CEO acompanha) · **a régua** (o funil ideal:
40% agenda · 50% comparece · 80% fecha · 90% paga) · **safra** (ano em que a
unidade abriu) · **same store** · **unidade madura** · **Conecta** ·
**Acelera** · **consultor** · **sell-out** · **praça**.

E as palavras normais de agência que o cliente já usa: **peça**, **criativo**,
**feed**, **placar**, **verba**.

---

## Três hábitos

**Frase curta.** Se a frase tem vírgula demais, quebra em duas.

**O número antes da explicação.** *"Zero avaliações novas em 23 dias"* funciona.
*"Observou-se ausência de incremento no volume de avaliações"* não.

**Diga o que fazer.** Todo número na tela vem com a ação do lado. Número sozinho
vira cobrança; número com ação vira ajuda.

---

## A escada dos achados, em português

Era assim:
`HIPÓTESE → CANDIDATA → CONSTANTE → DOUTRINA → DERRUBADA`

Fica assim:

| Na tela | Quer dizer |
|---|---|
| **SINAL ISOLADO** | vimos em 1 ou 2 praças |
| **SE REPETE** | vimos em 3 ou mais |
| **VALE PARA A REDE** | vimos em praças bem diferentes entre si |
| **VIROU REGRA** | a rede decidiu agir com base nisso |
| **❌ CAIU** | uma praça mostrou o contrário |

Ninguém precisa de legenda para entender essa escada.
