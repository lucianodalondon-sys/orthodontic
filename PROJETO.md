# PROJETO — o portal de inteligência da OrthoDontic

Este documento existe porque o projeto cresceu ferramenta a ferramenta e
ficou bagunçado: 19 telas, praça misturando cidade, layout indo e voltando.
Aqui está o pensamento inteiro, numa página.

**Este arquivo diz o que o produto É** — o modelo, as definições, os dois
gols. **O estado de hoje, o que existe medido e o roadmap estão em
`AUDITORIA-E-ARQUITETURA.md`.** Os dois não se repetem: um define, o
outro presta contas. Histórico encerrado está em `/legacy`. Quando uma decisão nova
contrariar este documento, ou a decisão está errada ou este documento
precisa mudar — nunca os dois ao mesmo tempo em silêncio.

---

## 1 · O que este produto é

**Um portal de inteligência EXTERNA para a franqueadora.** Ele traz o que
a rede NÃO consegue ver de dentro: como cada clínica aparece na rua digital
da sua cidade, o que o paciente diz em público, o que o concorrente de
aparelho faz, onde a marca está exposta, onde cabe crescer.

O que ele **não** é: um espelho da operação. A franqueadora já sabe a
qualidade das suas clínicas — não precisamos escancarar o que eles já
sabem. Cada tela se justifica respondendo: *"que informação de fora, que
eles não têm, isto entrega — e que decisão dispara?"*

**Quem usa:** diretoria e gerentes de rede (tudo), consultor de campo (as
praças dele), e — na fase 2 — o franqueado, que vê **só a página da
clínica dele**. A página da clínica é a mesma; muda o alcance do login.

**A matéria-prima é 100% pública, para sempre:** Google (fichas, avaliações,
busca), Instagram, biblioteca de anúncios da Meta, Reclame Aqui, imprensa
local, IBGE. Campo que só a rede pode responder é teto do produto e aparece
declarado na tela.

---

## 2 · O modelo — as definições que não se misturam

```
REDE      374 unidades em 304 cidades (lista oficial). Camada rasa:
          ficha do Google de todas, alertas, mapa.
PRAÇA     UMA cidade. Nunca duas, nem coladas (Cuiabá ≠ Várzea Grande;
          Mafra ≠ Rio Negro). É onde a coleta profunda acontece.
UNIDADE   a menor conta. Cidade com 3 unidades tem 3 páginas de clínica,
          porque nem sempre é o mesmo dono. Nada franqueado-facing é
          por cidade.
OPORTUNIDADE  cidade estudada para expansão. Mesmo processo de coleta,
          mas NUNCA entra em conta da rede, placar ou plano.
CONCORRENTE   só quem disputa APARELHO (veredito carimbado por
          produto_do_concorrente.py). Clínica geral e implante são
          paisagem, não rival.
```

### Correção estrutural pendente (fase 1)

- **Separar Cuiabá de Várzea Grande.** Os 3 consultórios são de Cuiabá; 2
  concorrentes (RedeOrto VG, AmorSaúde VG) são de Várzea Grande e saem da
  praça — VG vira vizinha medida, com identidade própria se um dia tiver
  unidade. Rótulo volta a ser `MT · Cuiabá`.
- **Separar Mafra de Rio Negro.** OdontoCompany Rio Negro e Odontoimagem
  Rio Negro saem da praça de Mafra e ficam como vizinhas medidas.
- Depois disso: rótulos de praça voltam a ser sempre `UF · Cidade`, uma
  cidade só.

### As 10 praças (meta)

Hoje, depois da separação: **7 praças / 10 unidades** — Londrina (2),
Cuiabá (3), Contagem, Feira de Santana, Mafra, Palmas, Presidente
Prudente. Faltam **3 praças novas**, com o processo completo de
`coleta/NOVA-PRACA.md` (15 etapas, verificadas por `padrao.py`).

Candidatas na rede, por porte e região (unidades na lista oficial):

| cidade | unidades | por quê |
|---|---|---|
| **PR · Curitiba** | 8 | maior praça do Sul, vizinha de Londrina, multi-dono |
| **RS · Porto Alegre** | 9 | a maior da rede em unidades |
| **GO · Goiânia** | 4 | Centro-Oeste, porte médio-grande |
| SP · São Paulo | 5 | maior mercado do país (praça gigante — coleta mais cara) |
| MG · Uberlândia | 3 | interior forte do Sudeste |
| SC · Joinville | 3 | Sul industrial, porte médio |

**Recomendação:** Curitiba + Goiânia + Uberlândia (15 unidades novas,
regiões diversas, coleta viável com a cota atual). Porto Alegre e São
Paulo são as mais representativas, mas dobram o custo de coleta — decisão
do cliente. ⚠ Cada praça nova consome cota Apify (avaliações de ~14
concorrentes + nossas unidades).

---

## 3 · A arquitetura das telas — pouco, fundo, prático

O erro das versões anteriores: 19 ferramentas rasas lado a lado. O acerto
do que o cliente descreveu: **poucas ferramentas, e a página da clínica
como coração**. As leituras por-loja (linha do tempo, avaliações sem
resposta, rival, o que mudou) NÃO são telas do menu — são **capítulos da
página da clínica**.

```
HOME  (o primeiro layout: cabeçalho INTELLIGENCE, mapa do Brasil,
       e os alertas na frente)
  ├── ALERTAS DAS CLÍNICAS  → clique = abre a página da clínica
  ├── mapa da rede (374, por UF, vazio é informação)
  └── índice de ferramentas (cards, como no primeiro design)

PÁGINA DA CLÍNICA  (o coração; futura visão do franqueado)
  no formato da apresentação de Mafra, por unidade:
  ├── quem ela é na cidade (nota, posição, ritmo, ficha)
  ├── O QUE MUDOU entre coletas (melhorou / piorou)
  ├── a voz do paciente (temas, elogios, críticas)
  ├── avaliações esperando resposta
  ├── os rivais de aparelho DELA (o que fazem melhor)
  ├── linha do tempo (eventos observáveis)
  └── a tarefa aberta (o que fazer, prazo, dono, status)

PÁGINA DA PRAÇA  (mercado da cidade: portas, canais, busca, leilão
  de anúncios, imprensa — análise de MERCADO pode ser por cidade)

FERRAMENTAS DE REDE  (menu enxuto)
  ├── O que a rede ensina        (ex-padrões: o que separa quem cresce,
  │                              bom e ruim, decisão de franqueadora)
  ├── Radar de oportunidades     (funil nacional dos 5.570 → estudos
  │                              profundos das candidatas)
  ├── A marca                    (Reclame Aqui rede contra rede, fichas,
  │                              alertas graves das 374)
  └── + 3 ferramentas novas      (do estudo de referências — seção 4)
```

Regras de tela que continuam valendo: o casco nunca calcula; rótulo com
UF na frente; estado vazio declarado; linguagem de balcão; nada de
palavra interna.

---

## 4 · Os dois gols — e a ferramenta que faltava

A franqueadora quer duas coisas: **performance das clínicas** e **vender
mais clínicas**. Toda ferramenta do portal serve a um dos dois gols ou
sai. A segunda opinião (Codex) apontou o buraco: o plano estava forte em
performance e **órfão no gol comercial** — selecionar cidade não é vender
franquia.

### O produto do gol comercial: O DOSSIÊ DA CIDADE

A ferramenta central de expansão é um **dossiê exportável, feito para
ser apresentado ao candidato a franqueado**: o tamanho do público-alvo
(IBGE), a presença da marca e a distância das unidades vizinhas, a
demanda digital observável, a oferta real (quem vende aparelho, reputação
e intensidade publicitária de cada um), a comparação com cidades
parecidas onde a rede já opera e prospera — e, sempre, **evidência
separada de inferência e do desconhecido**. Nunca promessa de
faturamento: prova de que a franqueadora conhece o território como
ninguém. Os 6 estudos de oportunidade que já existem são o embrião; o
dossiê é a versão comercial deles.

O funil nacional continua como triagem — mas mostrando **dimensões
separadas** (demanda, concorrência, presença da marca, renda), não uma
nota mágica de "viabilidade".

## 4b · As ferramentas novas — decididas pelo estudo + segunda opinião

O estudo (Reputation.com, Chatmeter, Yext, Birdeye, BrightLocal, SOCi)
mostrou que a indústria inteira converge em seis padrões — e que a "página
inteira da clínica" que o cliente pediu É o padrão da indústria
("location detail"). O que separa portal de inteligência de dashboard:

1. **um score memorável por loja** que se decompõe em causas;
2. **leaderboard interno** (melhores, piores, quem mais melhorou);
3. **explicação da variação** ("caiu por X e Y"), não só o gráfico;
4. **benchmark contra o rival da esquina**, nunca média genérica;
5. **alerta = tarefa com dono e idade**, não notificação;
6. a inteligência **vai até o usuário** (resumo semanal), não espera login.

As ferramentas novas, escolhidas por esses padrões + os dados que o ciclo
semanal já coleta:

1. ⭐ **O DOSSIÊ DA CIDADE** (gol: vender clínicas) — descrito acima. O
   material que a equipe de expansão põe na mesa do candidato.
2. ⭐ **A NOTA DA CLÍNICA** (gol: performance) — índice DIAGNÓSTICO por
   unidade (nota Google + ritmo + taxa de resposta + presença na busca),
   sempre com a fórmula, os pesos e a decomposição visíveis, e a variação
   explicada: "caiu por causa de X". A segunda opinião foi clara: nota
   única fechada vira política interna e contestação — então ela é
   ferramenta de diagnóstico do consultor, **não** placar público. Sem
   "10 piores": o que se publica é **evolução** (quem mais melhorou) e
   grupos comparáveis (cidade de porte parecido com porte parecido).
3. ⭐ **O RIVAL DA PORTA** (gol: performance) — por unidade: o rival de
   aparelho DELA está acelerando? Ritmo de avaliações, nota, anúncios
   ativos e Instagram do rival contra a clínica. A escolha do rival é
   auditável (o veredito de produto está carimbado na identidade) e pode
   haver mais de um. Limite declarado: biblioteca da Meta não vê todo o
   marketing — "zero anúncios" é "zero anúncios NA META", nunca "zero
   marketing".
4. **QUEM APARECE NA BUSCA** (gol: performance) — quando a cidade digita
   "dentista"/"aparelho", quem aparece. Com método declarado na tela:
   consultas fixas, frequência padronizada, e o aviso de que busca varia
   por ponto e dispositivo — medimos tendência, não verdade absoluta.
5. **DO QUE FALAM** não é ferramenta de menu: é capacidade que alimenta
   "O que a rede ensina" (padrões bons e ruins por tema) e o capítulo de
   voz do paciente na página da clínica.

A caixa de respostas segue viva com a régua do estudo: cada negativa sem
resposta ganha **idade** e vira tarefa. Sobre "dono e prazo": são a
RECOMENDAÇÃO da franqueadora (nós sugerimos, ela atribui) — e o fechamento
continua sendo medido por fora (tarefa resolvida = o gatilho sumiu na
medição seguinte). O teto continua declarado: sem CRM, "conversão" nunca
aparece como promessa.

---

## 5 · O design — a identidade que fica

- **O primeiro layout é a base.** Cabeçalho com o lockup tipográfico
  "INTELLIGENCE" que o cliente aprovou, o mapa do Brasil presente na
  entrada, cards como índice. ⚠ O primeiro design está no primeiro zip
  do Claude Design — precisamos recuperá-lo (re-upload do cliente ou
  histórico do projeto) para extrair o cabeçalho e a tipografia exatos.
- Design System OrthoDontic de verdade: navy `#001E78` estrutural, cyan
  `#00B9FF` só para dado vivo, Gotham (Light nos números grandes), anéis
  concêntricos discretos, linhas finas.
- Densidade de ferramenta nas páginas internas (tabela, série, mapa),
  clareza de card na home. O que foi construído em `scripts/build_casco.py`
  (app de arquivo único com dados embutidos) vira a base técnica — a
  identidade visual é que muda para a do primeiro layout.

---

## 6 · Ordem de execução

O gol comercial não espera o fim da fila — ele ganha um piloto já na
fase 2, com o que já está coletado.

```
FASE 1 · o modelo certo (sem tela nova)
  1. separar Cuiabá/VG e Mafra/Rio Negro (identidade + série + rótulos)
  2. padrao.py e build passando com praça = uma cidade
FASE 2 · piloto do gol comercial (com o que já existe)
  3. o primeiro DOSSIÊ DA CIDADE, de uma das 6 já estudadas, exportável,
     para a equipe de expansão testar com candidato real
FASE 3 · as 10 praças
  4. cliente escolhe as 3 cidades → NOVA-PRACA.md nelas (coleta completa)
FASE 4 · o portal reorganizado
  5. build gera: home + página de clínica (capítulos) + página de praça
     + ferramentas de rede enxutas — payloads novos, menos telas
  6. casco no primeiro layout, com o INTELLIGENCE e o mapa
FASE 5 · as ferramentas novas, por prioridade
  7. Nota da Clínica (diagnóstica) → Rival da Porta → Quem Aparece na
     Busca — cada uma com "que decisão dispara" escrito na tela
FASE 6 · a visão do franqueado
  8. a página da clínica vira o produto do franqueado (acesso restrito)
```

Cada fase termina com `padrao.py --exigir` verde e commit. Nada de fase
nova com a anterior pela metade.

## 7 · Riscos declarados (da segunda opinião — para não esquecer)

- **10 praças são amostra de demonstração**, não base estatística sobre
  374 unidades. As telas dizem isso (cobertura sempre visível).
- **Viés de seleção**: escolher cidade nova por facilidade de coleta faz
  portfólio bonito, não amostra representativa — a escolha é do cliente,
  com critério de negócio.
- **Praça = cidade é a identidade; expansão precisa de área de
  influência.** Paciente atravessa município. O dossiê traz distância das
  unidades vizinhas; canibalização entra pela régua hab/unidade.
- **Cadência**: campanha curta de rival pode passar entre duas medições
  mensais. A ponta semanal decide onde adensar.
- **Manutenção é custo real**: concorrente muda de nome, ficha duplica,
  unidade fecha. Os guardas (duplicata de local_id, duas fontes,
  reclassificação de produto) rodam a cada ciclo.
- **Com candidato a franqueado, evidência ≠ inferência**: todo dossiê
  separa o que foi medido, o que foi inferido e o que não sabemos.
