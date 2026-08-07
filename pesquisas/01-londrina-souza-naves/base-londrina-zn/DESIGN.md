# SPEC DE DESIGN — Apresentação "O Paciente da Zona Norte"

## Conceito
Relatório editorial de pesquisa: as **citações reais dos pacientes são o
protagonista visual** (serifa itálica grande). Motivo-assinatura: **as
borrachinhas de aparelho** — fileiras de pontinhos coloridos como divisor
("uma cor de borrachinha por manutenção"). Tom: consultoria séria com calor
humano; nada de estética "clínica fria" nem dentes de banco de imagem.

## Paleta (tema claro)
- Papel: `#f8f5ef` (off-white quente) · Cartão: `#fffdf8`
- Tinta: `#17333a` (petróleo escuro) · Tinta secundária: `#4a6167` · Linha: `#e2dccd`
- **Acento "borrachinha": `#e14b64`** (rosa-vermelho) — títulos de dado, bordas, CTAs
- Teal `#2e8c96` (eyebrows/links) · Dourado `#d9a23c` (boxes de alerta)
- Semânticos: positivo `#2e7d5b` · negativo `#b8434f`

## Paleta (tema escuro)
- Papel `#0e2227` · Cartão `#14313a` · Tinta `#ece5d6` · Linha `#24444d`
- Acento `#f06a80` · Teal `#5cb8c2` · Dourado `#e3b45f` · ok `#67c29a` · bad `#f08a92`

## Tipografia
- **Display/citações:** serifa (Charter/Georgia), itálico, pesado; hero em
  clamp(44px→86px), line-height 1.04
- **Corpo:** sans de sistema (Segoe UI/-apple-system), 17px, line-height 1.62
- **Dados/numeração de capítulos:** mono (Consolas), `tabular-nums`
- Eyebrows: uppercase, letter-spacing .14em, 12px, cor teal

## Layout
- Coluna única, max-width 900px; texto corrido máx. ~68ch
- Capítulos numerados 01–11 com régua superior grossa (2px, cor tinta) +
  número em mono no acento
- Componentes:
  - **Stat tiles**: grid auto-fit 180px; número grande em serifa; destaque `.hot` no acento
  - **Muro de citações**: cards com quote serifada + legenda pequena
  - **Barras de ranking**: label 150px + trilha + % em mono (1ª barra no acento)
  - **Premia × Detona**: 2 colunas, títulos verde/vermelho com ✓/✗
  - **Territórios**: cards com borda esquerda no acento; roteiro em box tracejado
    com CTA em negrito no acento
  - **Boxes de alerta**: borda esquerda dourada
  - Tabelas com `overflow-x:auto`
- Divisor-assinatura "borrachinhas": círculos 11px nas 5 cores, com legenda
  opcional em uppercase

## Regras
- Ambos os temas (light/dark) via tokens CSS + `prefers-color-scheme` +
  `data-theme` override; `prefers-reduced-motion` respeitado
- Sem imagens externas (tudo tipografia/CSS); sem emoji como marcador de seção
  (emoji só dentro de citações reais)
- CTA sempre 1 por bloco, no acento
