# Orthodontic — Pesquisas de Praça (London Creative)

Consolidação de **todas as pesquisas feitas para a Orthodontic** — as 4 praças
estudadas + o estudo da rede franqueadora. Recuperado do Dropbox
(`/LONDON CREATIVE CLAUDE/CLAUDE CODE VIDEOS/`), julho/2026.

Método comum às 4 praças: escuta social da cidade → avaliações públicas da
categoria → raio-X da unidade → mídia ativa dos concorrentes → mercado/cultura
→ cruzamento em plano de ação. **Tudo construído de fora, sem dado interno**
(exceto Mafra, que ganhou a "prova dos nove" com os dados do BI da rede).

---

## As 4 praças

| # | Praça | Unidade | Nota / avaliações | Vozes analisadas | A tese |
|---|---|---|---|---|---|
| 01 | **Londrina/PR** | Souza Naves (a MATRIZ) | 4,6 · 561 | 1.400+ | "A coroa que está escorregando" — a casa que criou o padrão não é a nº1 da própria cidade (Odontoclinic leva 4,9) |
| 02 | **Presidente Prudente/SP** | 1ª franquia da rede (2005) | 4,9 · 582 | 1.400+ | "O tesouro guardado na gaveta" — líder em nota E volume, 2 gerações de pacientes, e não conta a história |
| 03 | **Feira de Santana/BA** | Centro (calçadão) | 4,7 · 173 | 800+ · 59 anúncios | "Todos os caminhos levam à Feira. Menos o da própria clínica" — bem avaliada, fala como forasteira |
| 04 | **Mafra/SC (Mafra)** | piloto aplicado | 4,9 · 155 | 452 + dados internos | "A melhor clínica da cidade é a mais calada" — reputação de líder, zero anúncios no pico da temporada |

### 01 · Londrina — Souza Naves (matriz)
- `01-londrina-souza-naves/CONTEUDO-SN.md` — a apresentação da matriz
- `01-londrina-souza-naves/base-londrina-zn/` — o estudo-base de Londrina
  (615 reviews / 438 com texto), de onde saiu a skill `orthodontic-anuncios-zn`:
  - `RESUMO.md` — as 7 descobertas que direcionam o marketing
  - `patterns.md` / `pesquisa-completa.md` — os padrões extraídos
  - `benchmark-odontoclinic.md` — o benchmark da líder de nota da cidade
  - `apresentacao.html` — **o único deck HTML que veio junto**
  - `SKILL-orthodontic-anuncios-zn.md` — a skill gerada a partir do estudo

### 02 · Presidente Prudente
- `02-presidente-prudente/CONTEUDO-PP.md` — a apresentação ("A Primeira Praça")
- `02-presidente-prudente/patterns.md` — 930 comentários / 12 perfis, as 4
  línguas da cidade, 454 avaliações da categoria

### 03 · Feira de Santana
- `03-feira-de-santana/CONTEUDO-FSA.md` — a apresentação ("Todos os Caminhos
  Levam à Feira"), inclui o **playbook do gigante local** (doutor com nome,
  1.268 avaliações) e a **guerra de anúncios** (59 ativos, 16 anunciantes)

### 04 · Mafra/SC — o piloto aplicado
- `04-mafra-mafra/CONTEUDO-MAFRA.md` — o estudo mais completo da série:
  18 capítulos, plano de 90 dias, painel de ponteiros, e a **"prova dos nove"**
  (o estudo de fora × os dados internos do BI: funil 5.050→298→147→110, o
  agendamento a 6% contra a régua de 40%, a base caindo 875→677)
- `04-mafra-mafra/KIT-EXECUCAO-MAFRA.md` — o kit de execução

### 05 · Rede franqueadora (não é praça — é o nível nacional)
- `05-rede-franqueadora/CONTEUDO-REDE.md` — o estudo da rede
- `05-rede-franqueadora/CONTEUDO-PARECER-TELO.md` — o parecer "O Embaixador e
  os Dois Andares" (a medição do Michel Teló)
- `05-rede-franqueadora/agente-telo-orthodontic.md` — a pesquisa documental base

---

## `_metodo/`
- `config/targets_orthodontic*.yaml` — os alvos de coleta de cada praça
  (nacional, Londrina/ZN, Souza Naves, PP, FSA, Mafra) + `lexico_orthodontic.yaml`
- `memoria/projeto-orthodontic-*.md` — as memórias de projeto do Claude Code
  (cliente-zn, mafra-piloto, rede-franqueadora)

---

## O que ficou no Dropbox (não copiado aqui)

Os **corpora brutos** de cada praça continuam em
`/LONDON CREATIVE CLAUDE/CLAUDE CODE VIDEOS/data_ortho{,_sn,_pp,_fsa,_mafra,_rede}/`
— reviews do Google por clínica, posts e comentários do Instagram, biblioteca de
anúncios do Meta, SERP, Google Trends, velocity de reviews, fichas e pesquisa
documental. São alguns MB por praça; é a matéria-prima, não o entregável.

Os decks HTML de PP, FSA, SN, Mafra e rede **não estão nos pacotes** — os zips
contêm só o `CONTEUDO-*.md` (o briefing de design). Só Londrina/ZN tem
`apresentacao.html` gerado.

---

## Onde isso já virou produto
A skill `orthodontic-franqueado` (instalada) foi destilada destes 4 estudos +
os dados do BI + o parecer Teló — é a voz para institucional de marca dirigido
ao franqueado.
