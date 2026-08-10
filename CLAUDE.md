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
python3 coleta/coletores/ponta.py --salvar        # 229 fichas, API do Google
python3 scripts/o_que_mudou.py --salvar
python3 scripts/fila.py --salvar                  # grava o histórico → status
python3 scripts/timeline_da_loja.py --salvar      # a vida de cada loja
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
| `dados/planos/` | plano do franqueado, **só de praça com unidade** |
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
- **O casco fala língua de balcão.** Palavras internas (casco, escada, ponta,
  andar, régua) nunca aparecem na tela. A home é `franqueadora.json → cards`
  (pergunta + número + frase, 4 grupos); prompt vigente: `PROMPT-CASCO-V5.md`.
