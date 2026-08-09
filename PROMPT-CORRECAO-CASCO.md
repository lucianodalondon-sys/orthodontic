# Prompt de correção do casco

> Cole isto no Claude Design, junto com o arquivo atual.
> É correção cirúrgica, não redesenho. **O visual está bom — não mexa nele.**

---

## O QUE ESTÁ ERRADO, EM ORDEM DE GRAVIDADE

### 1 · O template não renderiza. 393 placeholders aparecem como texto na tela.

O arquivo usa `<sc-if>` e `{{ ... }}`, e nada disso vira conteúdo no HTML
exportado. O usuário lê literalmente **`{{ p.name }}`** no lugar do nome da
praça, **`{{ false }}`** dentro dos botões, **`{{ v.city }}`** no lugar da
cidade. São 393 ocorrências.

**Corrija assim:** remova `<sc-if>`, `hint-placeholder-val` e todo `{{ }}` do
HTML. A montagem da tela é feita em **JavaScript puro**, lendo o JSON e criando
os elementos. Nenhuma chave dupla pode sobrar no arquivo final.

**Como conferir antes de entregar:** buscar `{{` no arquivo tem que dar zero.

### 2 · Os dados estão dentro do casco. Precisam vir de fora.

Hoje o arquivo tem `PRACAS = [...]` e `GRID = [...]` escritos no código, com 4
praças fixas. Já temos 6 e vamos ter 340 — e o casco não pode ser reescrito a
cada coleta.

**Corrija assim:** todo dado sai do código e passa a vir de **um único bloco**,
que a nossa automação substitui a cada publicação:

```html
<script id="dados-portal" type="application/json">
{ "gerado_em": "2026-08-08", "pracas": [], "unidades": [], "alertas": [],
  "achados": [], "categoria": [], "canais": [] }
</script>
```

O JavaScript lê com
`JSON.parse(document.getElementById('dados-portal').textContent)`.

**Regra dura: o casco não calcula nada.** Nem média, nem variação, nem posição
no placar. Tudo vem pronto no JSON. Se um número não está lá, a tela mostra
"sem dado" — nunca inventa e nunca conta.

**Enquanto você desenvolve**, deixe no bloco um exemplo com **12 praças e 30
unidades fictícias**, para provar que a tela aguenta lista longa. Não use as 4
reais como se fossem tudo.

### 3 · A UF vem ANTES do nome da cidade, em toda a tela.

**`MG · Contagem`**, nunca `Contagem/MG`.

Vale no título da ficha, no cartão de alerta, no resultado da busca, no filtro
e na lista. Praça com duas cidades repete: **`SC · Mafra + PR · Rio Negro`**.

Três motivos:

- **cidade homônima é armadilha real** — existe Palmas no TO e no PR, e a
  coleta já entrou contaminada por isso uma vez
- **numa lista de 340, o olho agrupa por estado sozinho**, sem coluna extra
- **ordem alfabética vira ordem por estado**, de graça

O JSON já entrega pronto, no campo `rotulo` de cada praça. **O casco não monta
esse texto** — ele mostra o que vem.

---

### 4 · Ainda tem palavra difícil na tela.

`velocity` aparece 13 vezes e `baseline` 4. Troque:

| Está escrito | Escreva |
|---|---|
| velocity | **ritmo de avaliações novas** |
| baseline | **ponto de partida** |

E confira o resto contra o `COMOESCREVER.md` que já foi enviado.

---

## O QUE PRECISA MUDAR DE ESTRUTURA PARA AGUENTAR 340

O portal hoje é uma exposição de 4 casos. Com 340 ele vira uma lista que
ninguém rola. A mudança é de postura:

**Ninguém procura uma unidade. A unidade é que aparece.** A tela inicial não é
um catálogo — é uma **fila de trabalho**: o que mudou desde ontem, ordenado
por gravidade. A ficha da praça se alcança por alerta, por busca ou por filtro.
Nunca por rolagem.

Três coisas concretas:

1. **A busca é o caminho principal**, não um enfeite no canto. Campo grande,
   sempre visível, atalho `/`, e ela busca praça, cidade, unidade, concorrente
   e achado ao mesmo tempo.

2. **Filtros que respondem pergunta de gestor**, e podem combinar:
   região · estado · porte da praça · safra da unidade · consultor responsável ·
   *o que está pegando fogo* · *quem parou* · *quem melhorou*

3. **Lista virtualizada.** 340 linhas não podem existir todas no DOM ao mesmo
   tempo. Renderize o que está na tela.

**Agrupe alerta por causa, não por unidade.** Com 340, "37 unidades pararam de
receber avaliação este mês" é um cartão só, com a lista dentro. Trinta e sete
cartões iguais é ruído.

---

## O QUE TIRAR DA TELA

**"O funil contra a régua"** — os cinco estágios com 40/50/80/90.

Sai. **Não temos esse dado e não vamos ter**: depende do Conecta, e a rede não
vai dar acesso agora. O que existe é o registro de uma unidade, de uma época,
que não se atualiza e não compara com nada.

**No lugar dele, e é melhor:** a peça central da ficha passa a ser o
**histograma de doze meses de avaliações novas**, mês a mês, com a unidade e o
líder da praça lado a lado.

Ele responde o que o funil não responde, e com dado que a gente tem toda
semana:

- **quem sustenta** — a unidade de Cuiabá fez 65·48·43·43·44·34·55·48·45·37·40·46·46
- **quem é campanha** — a Odontologia Prado fazia 1 por mês e explodiu para 70
- **quem desligou** — a matriz de Londrina fez 48·180·93 e caiu para 9

Essa terceira leitura é o produto inteiro numa imagem: *"vocês fizeram a maior
campanha da cidade e desligaram, e ninguém percebeu."*

---

## O QUE ACRESCENTAR

### O selo de constância, ao lado de todo número de ritmo

Velocidade sozinha engana. Ao lado de "43,8/mês" vem sempre:

- 🟢 **OPERAÇÃO** — 10 meses ou mais seguidos
- 🟡 **CAMPANHA** — 3 a 9 meses
- 🔴 **RAJADA** — um mês concentra 60% ou mais
- ⚫ **PAROU** — sem movimento nos últimos 60 dias

De 130 clínicas que medimos, **só quatro sustentam.** É a informação mais rara
que o portal tem, e hoje não aparece.

### O aviso de dado estimado

Quando a praça só tem uma coleta, o número é estimativa. Marque com `~` e um
balão explicando: *"medido pelo intervalo da amostra; a próxima coleta confirma
pelo contador do Google."* Um portal que diz o que ainda não sabe é mais
confiável que um que finge saber tudo.

---

## O QUE NÃO MUDA

O visual, o degradê, a tipografia, o ritmo das telas, a barra lateral, os
medidores redondos. **Está bom e é isso que faz parecer portal de inteligência
e não relatório.** A correção é de funcionamento e de escala, não de estética.

---

## COMO SABER QUE FICOU PRONTO

- [ ] buscar `{{` no arquivo dá **zero**
- [ ] toda cidade na tela aparece como `UF · Cidade`, e o casco não monta esse texto
- [ ] buscar `velocity` e `baseline` dá **zero**
- [ ] existe **um** `<script id="dados-portal">` e nenhum dado no código
- [ ] o exemplo tem 12 praças e 30 unidades, e a tela aguenta
- [ ] a busca abre com `/` e encontra praça, unidade, concorrente e achado
- [ ] o alerta agrupa por causa
- [ ] a ficha abre com o histograma de 12 meses, não com o funil
- [ ] todo ritmo tem selo de constância do lado
- [ ] apagar o JSON não quebra o portal — ele mostra "sem dado"
