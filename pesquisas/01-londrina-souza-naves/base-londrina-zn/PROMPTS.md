# PROMPTS PRONTOS — gerar a apresentação no Claude e no Claude Design

## Opção 0 (mais rápida): usar o HTML pronto
O arquivo `apresentacao.html` desta pasta já é a apresentação final,
autossuficiente (zero dependências externas, tema claro/escuro). Dá pra:
- abrir direto no navegador;
- anexar no Claude e pedir ajustes;
- importar/colar no Claude Design como ponto de partida.

---

## PROMPT PARA O CLAUDE (claude.ai) — cole junto com CONTEUDO.md e DESIGN.md anexados

```
Crie um artifact HTML de página única com uma apresentação executiva de pesquisa
de público, em português do Brasil, seguindo EXATAMENTE:

1) O conteúdo integral do arquivo CONTEUDO.md (hero + capítulos 01 a 11 + rodapé),
   sem cortar citações — as citações reais dos pacientes são o coração da peça.
2) A especificação visual do arquivo DESIGN.md (paleta clara/escura por tokens
   CSS, serifa itálica para citações, motivo das "borrachinhas" como divisor,
   stat tiles, muro de citações, barras de ranking, premia×detona, cards de
   território com roteiro e CTA, boxes de alerta dourados, tabelas com scroll).

Requisitos técnicos: HTML único autossuficiente (sem fontes/imagens externas),
responsivo, temas claro E escuro (prefers-color-scheme + data-theme override),
prefers-reduced-motion respeitado, números com tabular-nums.

Título da página: "Orthodontic — O Paciente da Zona Norte · Pesquisa de Público".
Não invente dados novos: use somente o que está em CONTEUDO.md.
```

---

## PROMPT PARA O CLAUDE DESIGN — cole junto com CONTEUDO.md (copy integral)

```
Projeto: apresentação de pesquisa de público "Orthodontic — O Paciente da Zona
Norte de Londrina". É uma peça de NEW BUSINESS da London Creative para a
Orthodontic: será ENVIADA (não apresentada ao vivo) a uma decisora da marca,
para demonstrar inteligência e visão de fora e abrir um contrato.

DESIGN SYSTEMS — usar os DOIS, com papéis distintos:
• LONDON CREATIVE = o sistema ANFITRIÃO (a moldura): capa/hero, navegação,
  numeração de capítulos, rodapé, assinatura "pesquisa e inteligência por
  London Creative". É a London falando.
• ORTHODONTIC = o sistema do CONTEÚDO (o assunto): cores/tipografia da marca
  nos dados sobre a marca, no placar, nos territórios de campanha e nos
  mockups de peça. É sobre a Orthodontic.
A hierarquia deve deixar claro quem fala (London) e de quem se fala
(Orthodontic) — co-branding elegante, sem misturar os dois numa coisa só.

CAPA (primeira tela, obrigatória):
• As DUAS logos lado a lado — LONDON CREATIVE e ORTHODONTIC (dos respectivos
  design systems), separadas por um divisor discreto (× ou barra), London à
  esquerda (quem assina), Orthodontic à direita (para quem é).
• Título: "O Paciente da Zona Norte"
• Subtítulo: "Pesquisa de público · Ortodontia · Londrina/PR"
• Linha de rodapé da capa: "Inteligência de mercado por London Creative · julho 2026"
• A capa abre a peça ANTES do hero da citação.

NARRATIVA (copy integral no CONTEUDO.md — não cortar citações):
1. Hero: a citação real "Consigo sorrir novamente!!" + nota "tudo minerado de
   fora, sem briefing — é por estar de fora que enxerga o que a rotina de
   dentro não vê".
2. A TESE: os 5 PONTOS CEGOS — é o coração da peça. Cada ponto cego merece
   destaque visual próprio (marcador/selo recorrente, ex. "PONTO CEGO 01") que
   reaparece nos capítulos que o provam, costurando a narrativa.
3. Capítulos 01–13 (método → pano de fundo → personas → jornada da mãe →
   motivações → confiança/54% → placar → benchmark da líder → vida com
   aparelho → territórios com roteiro → funil de mídia → alertas honestos →
   proposta em 3 fases "o que podemos fazer juntos").
4. Fecho: "Vamos conversar sobre a Zona Norte — e sobre as outras 299."

TOM: consultoria sênior com calor humano. As citações reais dos pacientes são
o protagonista visual (tipografia grande, destaque). Proibido: foto de banco
de imagem de dente/clínica, dentês técnico, gráfico inventado.
TRAVA: não criar nenhum dado novo — usar somente o que está no CONTEUDO.md.
Formato: página longa navegável com sumário, responsiva, otimizada pra ser
lida sozinha no desktop e no celular.
```

---

## Conteúdo desta pasta
| Arquivo | O que é |
|---|---|
| `apresentacao.html` | A apresentação final pronta (a mesma publicada no link do artifact) |
| `CONTEUDO.md` | Todo o conteúdo, capítulo a capítulo (copy integral) |
| `DESIGN.md` | Paleta, tipografia, componentes e regras (light+dark) |
| `pesquisa-completa.md` | A pesquisa profunda por trás (9 seções, com evidências) |
| `benchmark-odontoclinic.md` | Dossiê da líder da categoria (playbook + contraste) |
| `PROMPTS.md` | Este arquivo |

Link do artifact publicado (privado até compartilhar):
https://claude.ai/code/artifact/a6ecd5ab-9a9e-4987-bd79-0abffff5dcae
