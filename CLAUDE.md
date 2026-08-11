# OrthoDontic — o que qualquer sessão precisa saber antes de mexer

## Antes de responder qualquer coisa sobre praça, cidade ou estudo

```bash
python3 scripts/padrao.py
```

Ela responde, com o disco na mão, o que cada praça tem e o que falta — e o
comando exato que preenche cada buraco. **Não responda de memória.** Este
arquivo existe porque a pergunta "o que falta nessa cidade?" foi respondida
de cabeça vezes demais, e sempre diferente.

`python3 scripts/padrao.py --praca <id>` para o detalhe de uma só.

## A régua é SC · Mafra

Mafra é a praça que foi até o fim e cujo relatório a diretoria usou para
decidir. Toda praça nova é comparada com ela, etapa por etapa. Se uma praça
não tem o que Mafra tem, ela **não está pronta** — e `padrao.py` diz qual
etapa falta.

O processo inteiro, escrito, está em **`coleta/NOVA-PRACA.md`** (15 etapas).
O `padrao.py` é a mesma coisa em forma de checagem. O documento ensina; o
script cobra. Quando os dois divergirem, o script é a verdade.

## As regras que não se negociam

- **O casco NUNCA calcula.** Todo número que aparece na tela sai pronto de
  `dados/portal/*.json`, montado por `scripts/build_portal.py`. Se falta um
  número, o conserto é no build, não no casco.
- **Rótulo com a UF na frente:** `MG · Contagem`. Nunca `Contagem/MG`. E o
  casco nunca monta rótulo — recebe pronto.
- **Duas fontes independentes** antes de dizer que a rede não está numa
  cidade: a lista oficial e a busca por nome. Se a lista oficial não
  responder, a cidade sai como NÃO CONFERIDA e não entra em recomendação.
- **A UNIDADE é a menor conta, e loja não se funde com loja.** Cuiabá tem
  três lojas e Londrina duas, e nem sempre é o mesmo dono. Toda leitura que
  fala com franqueado (rival, fila, caixa de respostas, plano) é POR
  `local_id` — a média das lojas de uma cidade não diz nada para nenhum dos
  donos. Análise de MERCADO (tese da praça, portas, canais) pode ser por
  cidade, porque a cidade é uma só.

- **Praça de oportunidade não é praça da rede.** Ela tem identidade igual e
  passa pelos mesmos coletores, mas não entra no placar, não gera plano de
  franqueado e não conta como unidade parada.
- **Zero silencioso é falha.** Etapa que deveria escrever e escreveu nada é
  FALHA, não "ok · +0 registros".
- **Estado vazio é conteúdo.** Ferramenta sem dado aparece apagada com o
  motivo. Esconder o que falta é o que faz a diretoria achar que medimos
  tudo.
- **O veredito de quem disputa aparelho é carimbado, não improvisado.**
  `scripts/produto_do_concorrente.py --salvar` classifica cada concorrente
  (nome + voz do cliente) e grava `produto.disputa_aparelho` na identidade.
  Toda ferramenta de confronto filtra por `cruzamento.disputa_aparelho()`.
  Dos 219 concorrentes medidos, só ~27 disputam aparelho.
- **ODONTOLOGIA NÃO É ORTODONTIA.** O negócio da OrthoDontic é **aparelho**.
  Universidade que faz limpeza, extração e canal de graça **não** disputa
  paciente de aparelho — é outro tratamento, outro ticket, outra decisão.
  Rede de implante idem. Só conta como concorrência do mesmo produto quando
  o texto diz aparelho, ortodontia, bráquete, alinhador ou contenção.
  ⚠ Uma exceção importante: **`dentista` importa como PORTA**, não como
  concorrente. O paciente que digita "dentista" é quem marca a avaliação e
  sai com aparelho. As duas coisas convivem e não podem ser fundidas.

- **Nada de dado interno, e isso é permanente.** O portal é feito
  **inteiramente com informação externa**. Não temos CRM, contrato,
  faturamento, lead, nem o franqueado ao telefone — e não vamos ter. Campo
  que só a rede pode responder não é pendência: é **teto do produto**, e tem
  de aparecer na tela declarado como teto (`scripts/pontos_cegos.py`).
  Nunca escreva ferramenta que espere alguém de dentro preencher.

## O ciclo — a coleta que se repete

A ponta barata roda **toda semana** e é o que alimenta "O que mudou":

```bash
python3 coleta/coletores/unidades_da_rede.py      # a fonte madrinha, primeiro
python3 coleta/coletores/ponta.py --salvar        # 229 fichas, API do Google
python3 scripts/o_que_mudou.py --salvar
python3 scripts/fila.py --salvar                  # grava o histórico → status
python3 scripts/timeline_da_loja.py --salvar      # a vida de cada loja
python3 scripts/onde_cada_loja_aparece.py --salvar        # presença POR LOJA
python3 scripts/plano_do_franqueado.py --todas --salvar --md   # 1 por local_id
python3 scripts/quem_anuncia_aparelho.py --salvar # quem compra mídia de aparelho
python3 scripts/build_portal.py
```

A varredura profunda (texto das avaliações, Apify) roda **por mês** e só nas
lojas onde a ponta acusou movimento — o contador barato decide onde gastar o
caro. Depois dela: classificar → cruzamento → fila → reteste → rival →
padrões → caixa → padrao → build. Períodos curtos são declarados na tela
("o delta ainda diz pouco"); o aviso morre sozinho quando o ciclo engorda.

## Onde as coisas moram

| pasta | o que é |
|---|---|
| `dados/serie/*.jsonl` | o medido, append-only, com `snapshot_date` |
| `dados/identidade/*.json` | a amarração da praça: rótulo, UF, IBGE, locais |
| `dados/conteudo/*.json` | o autorado: tese, dna, citações, plano |
| `dados/portal/*.json` | o que o casco lê — nunca editar à mão |
| `dados/planos/` | plano do franqueado, **um por `local_id`**, só de loja da rede |
| `coleta/coletores/` | um coletor por fonte |
| `scripts/` | a inteligência e o build |

## Armadilhas já pagas — não repita

- **Deduplicação por chave não pega nada se os coletores usam formatos
  diferentes.** Dois coletores gravaram as mesmas avaliações como
  `local_id|<id>` e `google:<place_id>:<id>`; 981 linhas em dobro. Todo
  cálculo de ritmo passa por `cruzamento.reviews_unicos()`.
- **`Riomafra` é o nome LOCAL da região** (Rio Negro + Mafra). A praça é
  `mafra`, mas 13 nomes de terceiros contêm "riomafra" — handle de
  Instagram do concorrente, veículos de imprensa. Nunca troque em massa.
- **Número escrito à mão apodrece.** "4 praças de 340" ficou quatro semanas
  na tela enquanto o bloco ao lado dizia 374 unidades. Se um número aparece
  na tela, ele sai de `build_portal.py`.
- **`--todas` na pasta de identidade pega as praças de oportunidade junto.**
  Foi assim que saíram seis planos falando "a SUA clínica" para franqueado
  que não existe.
- **`ortho` solto marca concorrente como nosso.** "Clínica Ortho Mais" não é
  nossa. Use `orthodontic` sem espaços e sem acento.
- **U+2028 quebra `.splitlines()` do Python.** Leia por `\n`.
- **`local_id` truncado fundiu lojas.** Quatro pares de lojas (ODONTOMAX,
  Vamos Sorrir, DENTEBRAS, Odonto Minas) dividiram o mesmo `local_id` porque
  o id era o nome truncado. `cruzamento.identidades()` agora FALHA ALTO em
  duplicata, e a ponta grava `place_id` em cada medição. Se o guarda gritar,
  o conserto é separar as lojas (identidade + série), nunca afrouxar o guarda.
- **A FONTE MADRINHA É O SITE DA REDE, e ela se consulta ANTES de afirmar.**
  `python3 coleta/coletores/unidades_da_rede.py` baixa a lista oficial e
  compara com o número que o próprio site declara. Nenhuma frase sobre "a
  rede está / não está nessa cidade" sai sem essa lista do dia.
- **Cidade de nome parecido é cidade diferente.** A rede tem unidade em
  `Juazeiro/BA`; o Radar estuda `Juazeiro do Norte/CE` — outro estado, 500 km,
  e o CE inteiro só tem Fortaleza. É a mesma família de "Palmas/TO virou
  Palmas/PR". `padrao.py` etapa 0.5 declara o parecido na tela; nunca conclua
  pelo primeiro nome que casar.
- **Busca de anúncio casa por PALAVRA, não por cidade.** Procurando
  "juazeiro do NORTE" a Biblioteca do Meta devolveu a "Orthodontic Braço do
  NORTE" — unidade real de SC, a 3 mil km — e eu levantei bandeira de
  "unidade fora da lista". A cidade só conta quando vem colada na marca
  (`Orthodontic <cidade>`), e **com acento removido dos dois lados**: a lista
  oficial grava "Braco do Norte", o anúncio escreve "Braço". Procurar o nome
  solto no texto também erra: "Sorriso" é cidade de MT e palavra de anúncio.
- **Plano é POR LOJA, e a média da cidade mente para o dono.** Eram 7 planos
  para 10 lojas: as três de Cuiabá liam o mesmo texto. A loja Dom Bosco não
  aparece em NENHUMA das 151 buscas da cidade e recebia "a sua clínica
  aparece em N das M buscas". Separar não precisa de coleta nova: o mapa do
  Google devolve o contador de avaliações de cada resultado, e o contador é a
  impressão digital da loja (1.222 · 78 · 71 em Cuiabá).
  `scripts/onde_cada_loja_aparece.py` faz o casamento, com folga de 6 e aviso
  declarado para aparição que não casa.
- **`.length` na tela é conta na tela.** Todo "quantos itens tem aqui" sai
  contado do build, ao lado da lista (`estudos`, `itens_total`, `fora_total`,
  `alertas_total`, `candidatas_total`, `lojas_com_fila`). Lista cortada usa
  "ver todas as N" com o total pronto — nunca `total − 8`.
- **Número e nome concordam, sempre.** `cruzamento.conta(n, singular, plural)`
  é o único jeito de juntar os dois. A muleta `(s)` está proibida: o portal
  já escreveu "1 unidades em faixa vermelha" na primeira tela e "ganhou 1
  avaliações em 2 dia(s)".
- **Delta curto não é histórico.** `o_que_mudou` compara as duas últimas
  medições; Mafra, Londrina, Feira e Prudente são medidas desde 15/jul e a
  tela as chamava de "período de só 3 dias" — as quatro praças com MAIS
  histórico apareciam como as menos medidas. Toda leitura de movimento leva
  as duas janelas, e o aviso de amostra curta olha o histórico.
- **Build que não reproduz é build quebrado.** A captação era escrita só para
  a praça medida na última data do arquivo — 1 de 13. As outras 12 telas eram
  sobra de um build anterior: apagar a pasta fazia doze sumirem sem erro. É
  sempre a última medição DE CADA praça, e cada arquivo carrega o próprio
  `snapshot_date`.
- **O pico de procura NÃO EXISTE como dado externo, e isso está medido.**
  12 UFs no Google Trends, 5 anos, termo "aparelho ortodôntico": nenhuma
  passou nas duas travas (volume e repetição do pico). Por cidade é pior —
  das 124 cidades de SC e das 186 do PR, ZERO têm volume publicável,
  Londrina e Mafra inclusas; com o termo mais largo "ortodontista", igual.
  E onde há volume (BA, MG, SP) o mês de pico muda todo ano, então a média
  de 5 anos publicaria uma estação que não existe. `dados/portal/sazonalidade.json`
  guarda o veredito por UF — **não refaça esta coleta** achando que falta;
  ela foi feita, e o resultado é que o Trends não responde nesta escala.
- **A curva de uma região não vale para outra.** A sazonalidade tem 4 pontos,
  todos de SC, e foi Mafra que derrubou a tese nacional de "dezembro e
  janeiro são pico" — lá é vale. Enquanto não houver coleta por cidade, cada
  praça publica `sazonalidade_estado` com o motivo. Herdar curva é inventar.
- **Cidade de oportunidade também tem leitura escrita.** As seis do Radar
  abriam com vinte campos de número e nenhuma manchete, e o `padrao.py` dizia
  "completa" porque a régua só cobrava tese de praça com unidade. Etapa 15.5,
  `escreve_tese_oportunidade.py` — que confere cada número citado contra o
  estudo e falha se não bater.

- **O casco fala língua de balcão.** Palavras internas (casco, escada, ponta,
  andar, régua) nunca aparecem na tela. A home é `franqueadora.json → cards`
  (pergunta + número + frase, 4 grupos); prompt vigente: `PROMPT-CASCO-V6.md`.

- **A tela da CLÍNICA e a tela da PRAÇA respondem perguntas diferentes.**
  Praça = mercado da cidade (tese, temas, portas, quem anuncia): 7 telas.
  Clínica = a unidade (presença na busca, plano, fila, rival, respostas,
  linha do tempo): 10 telas. Bloco de cidade dentro da página da clínica
  vai com `e_da_cidade: true` e é escrito como tal na tela.
- **Quem anuncia aparelho tem tela, e a régua do produto vale ali também.**
  `scripts/quem_anuncia_aparelho.py` → `dados/portal/anuncios.json`. Dos
  677 anúncios ativos coletados, 134 falam de aparelho; os outros 543 são
  implante, clareamento, lente — e um advogado tributarista. Os
  descartados aparecem contados, com o motivo.

- **Design se faz no Claude Design — aqui não.** Este repositório guarda a
  referência aprovada (`referencia-aprovada/OrthoDontic Intelligence.dc.html`,
  o PRIMEIRO design), os dados e o prompt. Nenhum HTML de portal é escrito
  aqui. Quando o zip voltar do Design, o trabalho é conferir a fiação dos
  dados — nunca o visual.

- **Todo arquivo criado ou mudado vai para o chat, sempre.** Commit e push
  não bastam: o arquivo tem de chegar na mão, na conversa, no mesmo turno.
  Isso vale para prompt, payload, relatório e captura de tela.
