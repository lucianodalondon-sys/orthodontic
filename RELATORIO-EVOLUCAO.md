# Relatório da evolução — 13 de agosto de 2026

Este documento responde, ponto a ponto, ao pedido de evolução. Todo número
citado aqui sai do disco e pode ser reconferido com o comando ao lado.

---

## 1 · ESTADO ANTES

| | antes | |
|---|---|---|
| praças da rede | 17 | 5 delas recém-abertas e incompletas |
| praças de oportunidade | 6 | Radar |
| unidades próprias com estudo | 45 | de 373 na lista oficial |
| coordenadas na identidade | 45 | recuperadas do bruto, sem chamada nova |
| leitura de presença na busca | **1 escala só** | a cidade inteira, a partir de um ponto |
| nome da unidade na tela | **repetido** | 4 linhas "SP · São Paulo · OrthoDontic" |
| briefings de marketing gerados | **45** | um para cada unidade da rede |
| praças fora do padrão (`padrao.py`) | 5 | São Paulo, Rio, Florianópolis, Uberlândia, Caxias |

O problema de fundo: **a única medida de encontrabilidade era do tamanho do
município**. Em Mafra isso responde. Em São Paulo, o portal afirmava que as
quatro unidades da capital apareciam em **0 de 193 buscas** — verdadeiro, e a
conclusão que qualquer leitor tiraria dali era falsa.

---

## 2 · O QUE FOI FEITO

### 2.1 · A busca ganhou uma segunda escala

`coleta/coletores/perto_da_loja.py` refaz a mesma pergunta a partir do
**endereço de cada clínica**, com viés circular de 3 km — possível porque as
coordenadas já estavam pagas e no disco.

`scripts/aparece_perto_da_loja.py` lê e publica as duas medidas lado a lado.

### 2.2 · Cada unidade ganhou nome próprio

`scripts/nome_da_loja.py`. Toda unidade da rede se chama "OrthoDontic": a base
passa a ser a marca e o que distingue vem do endereço — bairro, depois o resto
do nome cadastrado, depois rua, depois rua e número. **Cada loja sobe só o
degrau de que precisa.**

### 2.3 · O motor de execução parou de inventar trabalho

`scripts/execucao_necessaria.py` agora consulta a leitura de perto antes de
gerar briefing. Loja que se defende no próprio quarteirão não vira job de
agência — e o caso aparece na tela **declarado como não necessário**, porque
esconder faria alguém reabrir o número da cidade e pedir a campanha de novo.

### 2.4 · O Radar ganhou território

Cada linha do Radar leva `territorio`: bairro do topo, concentração e o aviso
de que **concentração não é demanda**.

### 2.5 · Higiene que impedia o resto de ser confiável

- `scripts/dedup_serie.py` — duas execuções simultâneas do mesmo coletor
  gravavam tudo em dobro.
- `build_portal.py` remove página de clínica cujo id não existe em identidade
  nenhuma, e declara o que removeu.
- `cruzamento.coleta()` e o build resolvem o nome de tela pela identidade,
  nunca pela linha gravada na coleta.
- `padrao.py` — duas etapas novas de cobrança, e a muleta `(s)` eliminada.

---

## 3 · O ACHADO QUE MUDA DECISÃO

Quatro unidades de São Paulo, mesma cidade, mesma medição de cidade:

| unidade | na cidade | perto dela |
|---|---|---|
| OrthoDontic · São Miguel Paulista | 0 de 193 | **5 de 5, todas em 1º** |
| OrthoDontic · Tatuapé | 0 de 193 | 3 de 5 |
| OrthoDontic · Lapa | 0 de 193 | 1 de 5 |
| OrthoDontic · República | 0 de 193 | 1 de 5 |

Dois diagnósticos opostos. A tela antiga mandaria os quatro franqueados fazer
a mesma coisa.

Na rede inteira:

- **11 lojas** eram "invisíveis" pela leitura de cidade.
- **9 delas aparecem** quando a busca sai da própria porta.
- **2 não aparecem nem no próprio quarteirão** — e essas são o problema real:
  `RS · Porto Alegre · OrthoDontic · Rio Branco` e
  `MG · Uberlândia · OrthoDontic · Praça Adolfo Fonseca`.

---

## 4 · ESTADO DEPOIS

| | antes | depois |
|---|---|---|
| escalas de medição de busca | 1 | **2**, rotuladas |
| lojas medidas perto de si | 0 | **45**, em 17 praças |
| lojas realmente invisíveis | "11" | **2** |
| briefings de marketing | 45 | **5** |
| casos de operação | 18 | 24 |
| casos medidos e declarados NÃO necessários | 0 | 7 |
| unidades com nome único na tela | 26 de 45 | **45 de 45** |
| páginas de clínica órfãs | 2 | 0 |
| linhas duplicadas em série | 8 | 0 |
| praças fora do padrão | 5 | 2 |

---

## 5 · O QUE NÃO FOI FEITO, E POR QUÊ

- **Nada de dado interno.** Continua valendo: sem CRM, sem contrato, sem
  faturamento, sem lead. O que só a rede pode responder é teto do produto e
  aparece declarado como teto.
- **Google Trends não foi refeito.** Só o RJ, que nunca havia sido medido,
  entrou — curva instável, nada publicável, igual às outras 14 UFs.
- **Canibalização não foi medida.** Quem aparece na frente aparece na frente.
  Isso é posição, não roubo de paciente, e a tela não pode sugerir o contrário.
- **O raio de 3 km não é área de captação.** Distância no mapa não é tempo de
  deslocamento.

---

## 6 · O QUE FICOU FALTANDO

- **Canais de Florianópolis** abaixo do mínimo de 8 com handle. É etapa
  `auto+humano`: o coletor achou o que havia, o resto é trabalho manual.
- **19 dos 23 praças têm uma medição só de categoria**, então o detector de
  mudança de mercado ainda registra linha de base em vez de movimento. Isso é
  tempo, não bug — e a tela diz exatamente isso.
- **Nenhum arco do livro de ações completou 21 dias.** O ciclo só começa a
  responder na coleta que passar dessa distância.
