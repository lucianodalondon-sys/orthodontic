# Os dados do portal OrthoDontic — o contrato

**Esta pasta não é da marca.** É a ponte entre o design system e o sistema de
inteligência que alimenta o portal. Os arquivos aqui são gerados pela coleta e
atualizados a cada rodada — **não edite à mão.**

Gerado em 09/08/2026.

---

## A regra que manda em tudo

**O portal nunca calcula.** Se um número aparece na tela, ele veio pronto de um
destes arquivos. Nada de somar, dividir, tirar média, classificar por faixa ou
montar frase.

Por quê: todo número deste projeto carrega procedência e ressalva. Um
percentual calculado na tela perde as duas — e já aconteceu de uma versão
calcular ritmo no navegador e mostrar `-4,0` para uma clínica cujo contador de
avaliações tinha **caído**. O dado certo era *"o contador caiu 3, avaliação
removida"*, e essa frase já vinha pronta no JSON.

O que a tela pode fazer: **ordenar e filtrar por campo que já existe, e
formatar data.** Só.

E: **nenhum dado dentro do HTML.** Tudo por `fetch` de caminho relativo, a
partir de `./dados/portal/`.

---

## `manifest.json` — o índice, sempre o primeiro fetch

Diz o que existe. **Não presuma que uma tela existe — pergunte a ele.**

| Campo | O que é |
|---|---|
| `corte` | a data dos dados publicados |
| `gerado_em` | quando o build rodou |
| `cobertura` | `{ pracas_medidas: 7, total: 340 }` — a amostra, e ela vai no topo da tela |
| `pracas[]` | cada praça com `praca_id`, `nome`, **`rotulo`**, `uf[]`, `cidades[]` e `tem[]` |
| `arquivos` | o que existe em cada pasta: `rede`, `pracas`, `captacao`, `planos`, `oportunidade` |
| `telas` | a lista completa de payloads publicados |

`pracas[].tem` diz quais telas aquela praça já possui — `["praca","captacao","plano"]`.
**O menu se monta a partir dele:** praça sem plano não mostra aba de plano vazia.

---

## `franqueadora.json` — a sala de comando inteira

### `rede` — os números do topo

```json
{ "unidades": 374, "abertas": 348, "em_implantacao": 26, "cidades": 304,
  "ufs_com_unidade": 23, "ufs_sem_unidade": ["AC","AP","MA","RN"],
  "medido_em": "2026-08-09",
  "fonte": "orthodonticbrasil.com.br/encontre-uma-unidade" }
```

As **26 em implantação** são unidades vendidas e ainda não abertas. Contam como
praça ocupada.

### `mapa[]` — os 27 estados

Uma entrada por UF, sempre as 27, mesmo com zero:

```json
{ "uf":"BA", "unidades":21, "abertas":20, "em_implantacao":1,
  "cidades":19, "pracas_medidas":1 }
```

**Não temos coordenada de unidade** — o dado é por estado. Então não é mapa de
pino: é o Brasil por estado, densidade pelo campo `unidades`.

⚠ **Os quatro com `unidades: 0` — AC, AP, MA, RN — não podem ser só "os mais
claros".** É o achado mais forte da tela, e a ponte natural para o Radar de
Oportunidade: três das seis praças que o radar recomenda estão exatamente
nesses estados.

### `ferramentas[]` — as treze da barra esquerda

```json
{ "chave":"radar", "nome":"Radar de Oportunidade",
  "o_que_responde":"onde vale abrir a próxima unidade",
  "tela":"radar", "disponivel":true,
  "resumo":"6 praças livres estudadas · 2 descartadas por já ter unidade",
  "indisponivel_porque": null }
```

O `resumo` **já vem escrito**. Renderize como está; não reescreva, não resuma
de novo.

⚠ **Ferramenta com `disponivel: false` aparece apagada, com o
`indisponivel_porque` escrito.** Não some da barra. Esconder o que ainda não
tem dado é o que faz a diretoria achar que o sistema mede tudo.

### `reputacao_das_redes[]` — a peça que se usa PARA FORA

Nove redes de odontologia no Reclame Aqui. `nossa: true` marca a OrthoDontic.

```json
{ "marca":"OdontoCompany", "reclamacoes":23283,
  "selo":"NOT_RECOMMENDED", "nota":..., "nossa":false }
```

É a única peça do portal que a franqueadora usa **contra a concorrência**, e
não para olhar para dentro.

### `fichas_da_rede` e `presenca_na_busca`

```json
"fichas_da_rede": { "conferidas":10,
                    "por_categoria":{"Clínica odontológica":9,"Dentista":1},
                    "sem_site":0 },
"presenca_na_busca": { "aparelho":{"dentro":6,"fora":0},
                       "ortodontia":{"dentro":14,"fora":2},
                       "dentista":{"dentro":13,"fora":99} }
```

O contraste de `presenca_na_busca` é a leitura: a rede é dona da porta
**"aparelho"** e quase não existe na porta **"dentista"** — que é a mais
digitada. **O vazio é a mensagem**; desenhe de um jeito que se veja sem ler.

---

## Duas regras de escrita que valem em toda tela

### A UF vem ANTES do nome da cidade

**`MG · Contagem`**, nunca `Contagem/MG`. Vale no menu, na busca, na tabela e
na exportação.

**A tela não monta esse texto** — ele vem pronto no campo `rotulo`. Se estiver
concatenando cidade e UF em algum lugar, está errado.

### Palavra difícil não entra

Quem lê é diretor ou dentista, não analista.

| Não escreva | Escreva |
|---|---|
| velocity, baseline, share of voice | ritmo, ponto de partida, fatia da categoria |
| KPI, benchmark, churn | número, comparação, perda |
| dashboard, insights, overview | painel, achados, panorama |

---

## Onde os arquivos ficam no projeto do portal

```
index.html
assets/…                          (css e js, sem CDN — precisa abrir em rede fechada)
dados/portal/manifest.json        ← primeiro fetch
dados/portal/franqueadora.json    ← a sala de comando
```

---

## Se precisar de um dado que não está aqui

Ele não é inventado nem calculado na tela. **Peça** — a coleta gera e este
arquivo é reescrito. Há muito mais medido do que o que está publicado aqui:
o estudo completo de cada praça, o plano de cada franqueado, as seis praças de
oportunidade com a praça-gêmea de cada uma, as citações de pacientes.
