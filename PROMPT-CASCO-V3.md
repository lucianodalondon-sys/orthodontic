# Prompt para o Claude Design — casco v3

Cole isto inteiro. Ele substitui o PROMPT-CASCO-V2.

---

## O que mudou desde a versão que você entregou

O design está aprovado. **Não redesenhe nada.** Tipografia, paleta, anéis
concêntricos, sombras, pílulas, o mapa, a barra lateral — tudo fica.

O problema é de **organização**, não de estilo: treze ferramentas lado a lado
viraram um armário. Quem abre não sabe por onde começar, e a ferramenta que
muda uma decisão fica do lado da que só se consulta.

O payload mudou para resolver isso. Três coisas novas em
`dados/portal/franqueadora.json`, e um arquivo novo.

---

## 1 · A porta de entrada: `franqueadora.json → agora`

Este bloco é **a primeira coisa da tela**, acima do mapa e acima do menu.
Se ele for `null`, some com a seção inteira — não invente estado vazio.

```json
"agora": {
  "pergunta": "Em quais unidades a OrthoDontic está perdendo atenção local, para qual concorrente, e onde intervir primeiro neste mês?",
  "manchete": "4 de 10 unidades medidas estão em faixa vermelha. A primeira é PR · Londrina.",
  "em_risco": 4,
  "unidades": 10,
  "o_que_e_atencao": "participação observável em busca, avaliações, publicidade e atividade digital. Não é faturamento — nenhum número desta tela vem de dado interno da rede.",
  "primeiras": [ /* as 3 primeiras linhas da fila, resumidas */ ],
  "tela": "fila"
}
```

Como desenhar:

- `pergunta` em cima, pequena, como olho — é ela que justifica o portal existir.
- `manchete` grande. É o único número que a diretoria precisa ler em pé.
- `o_que_e_atencao` logo abaixo, discreto mas **sempre visível**. Não é
  rodapé, não é tooltip. Se sumir, o portal vira promessa de faturamento.
- `primeiras` como três cartões, e um CTA em pílula levando para `tela: "fila"`.

---

## 2 · O menu em três andares: `franqueadora.json → andares` + `ferramentas`

Cada ferramenta agora tem `andar`. Agrupe por `andares` (que vem na ordem
certa e traz `nome` e `explica`), e renderize as ferramentas de cada andar.

```
AGORA      onde intervir primeiro neste mês          → 1 ferramenta
DECIDIR    as quatro que mudam uma decisão           → 4 ferramentas
CONSULTAR  de onde veio cada número                  → 8 ferramentas
```

Peso visual proporcional: **AGORA** domina, **DECIDIR** é o corpo do menu,
**CONSULTAR** é uma gaveta — menor, mais discreta, pode nascer recolhida.

`disponivel: false` continua igual à v2: item apagado, **com o
`indisponivel_porque` visível**. Esconder o que falta é o que faz a diretoria
achar que o portal mede tudo.

---

## 3 · A tela nova: `dados/portal/fila.json`

Uma tela, uma lista, ordenada. É a tela mais importante do portal inteiro.

```json
{
  "pergunta": "...", "o_que_e_atencao": "...",
  "manchete": "...", "unidades": 10, "em_risco": 4,
  "criterio": [ {"chave","titulo","peso"} ],
  "faixas":   [ {"de": 60, "nome": "vermelha"}, ... ],
  "fila": [ {
      "pos": 1, "urgencia": 90, "faixa": "vermelha",
      "rotulo": "PR · Londrina", "unidade_curta": "Centro",
      "ritmo": 0.8, "meses": 2, "nota": 3.8, "avaliacoes": 76,
      "posicao": 23, "de": 24,
      "quem_avanca": {"nome": "Vittallon Odontologia", "ritmo": 35.6, "meses": 11, "nota": 4.9, "posicao": 1},
      "gatilhos": [ {"chave","titulo","fato","peso","fonte"} ],
      "acao": {"o_que","prazo","dono","custo","por_causa_de"},
      "ciclo": {"alertado_em","acao_confirmada","confirmada_em","resultado","medido_em"}
  } ],
  "o_que_isso_nao_ve": [ "...", "...", "..." ]
}
```

Como desenhar cada linha, na ordem:

1. **`pos` e `faixa`.** A faixa é cor (vermelha / amarela / verde) — use a
   paleta que você já definiu, não invente vermelho e verde de semáforo.
   `urgencia` é um número de 0 a 100 e aparece pequeno, ao lado.
2. **`rotulo`** e, **só se `unidade_curta` não for `null`**, ` · ` +
   `unidade_curta`. Quando é `null`, a praça tem uma unidade só e repetir o
   rótulo ao lado dele mesmo é ruído. **O casco nunca monta rótulo** — a UF já
   vem na frente, pronta.
3. **`quem_avanca`** ao lado, como confronto: o nome do concorrente, o ritmo
   dele contra o nosso. Se for `null`, não desenhe o bloco.
4. **`gatilhos`** — a lista de evidências, cada uma com `titulo` (curto) e
   `fato` (a frase com o número). O `fonte` é o arquivo de onde saiu: mostre
   em hover ou num pé de linha discreto. Ele é o que faz alguém acreditar.
5. **`acao`** — em destaque, no fim da linha: `o_que`, e abaixo
   `prazo · dono · custo`. Um alerta sem dono é boletim, e boletim ninguém
   executa.
6. **`ciclo`** — o bloco que fecha a linha. **Hoje ele está todo `null`, e é
   assim que tem de aparecer.** Desenhe três degraus:

   ```
   alertado em 09/08  →  ação confirmada: —  →  resultado: —
   ```

   Com uma legenda fixa: *"o ciclo começa na próxima coleta"*. Esse estado
   vazio é decisão de produto, não bug. É a promessa visível de que no mês que
   vem esta tela responde "o que recuperamos?" — e é o que separa este portal
   de um relatório.

No fim da tela, **`o_que_isso_nao_ve`** como bloco fechado e legível, não como
letra miúda. Ele diz que a fila mede 10 de 374 unidades e que não enxerga
contrato nem receita. Não amenize.

**`criterio`** vira um "como esta fila é montada", recolhido por padrão. Quem
duvida da ordem abre e vê os pesos.

---

## 4 · A ferramenta que saiu

**"Carteira do consultor" não existe mais no menu.** Ela prometia *"quem
visitar primeiro, e por quê"* e entregava quatro pareceres sobre uma peça de
anúncio. Quem cumpre essa promessa agora é a fila. Se você tiver a rota
`#/consultor` no casco, remova-a.

`corretor.json` continua no repositório e continua sendo lido pela tela de
praça — só não é mais ferramenta de primeiro nível.

---

## 5 · As regras da v2 que continuam valendo

- **O casco NUNCA calcula.** Nenhuma soma, média, porcentagem, ordenação por
  valor ou montagem de rótulo. Todo número que aparece na tela sai pronto do
  JSON. Se faltou um número, o conserto é no `build_portal.py`, não no casco.
- **`manifest.json` é o índice.** Leia ele primeiro; ele diz quais telas
  existem. `fila` já está na lista `arquivos.rede`.
- **Rótulo com UF na frente:** `MG · Contagem`. Nunca `Contagem/MG`.
- **Estado vazio é conteúdo.** Ferramenta apagada mostra o porquê; ciclo vazio
  mostra que está vazio; `o_que_isso_nao_ve` aparece em toda tela que tem.
- **Nada de dado interno.** Nenhum número deste portal vem do CRM da rede, e
  toda tela que fala de desempenho precisa dizer isso.

---

## 6 · O que NÃO fazer

- Não redesenhe o mapa, a barra lateral, a tipografia ou a paleta.
- Não transforme a fila em tabela densa. Cada linha é um caso com narrativa:
  quem está caindo, contra quem, por qual evidência, o que fazer.
- Não esconda `o_que_e_atencao` nem `o_que_isso_nao_ve` atrás de ícone.
- Não preencha o `ciclo` com placeholder simpático ("aguardando execução ✨").
  Escreva o travessão e a legenda, e pronto.
- Não some com as oito ferramentas de CONSULTAR. Elas ficam — recolhidas,
  não deletadas.
