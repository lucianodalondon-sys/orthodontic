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
- **Praça de oportunidade não é praça da rede.** Ela tem identidade igual e
  passa pelos mesmos coletores, mas não entra no placar, não gera plano de
  franqueado e não conta como unidade parada.
- **Zero silencioso é falha.** Etapa que deveria escrever e escreveu nada é
  FALHA, não "ok · +0 registros".
- **Estado vazio é conteúdo.** Ferramenta sem dado aparece apagada com o
  motivo. Esconder o que falta é o que faz a diretoria achar que medimos
  tudo.
- **Nada de dado interno.** Nenhum número vem do CRM da rede. Toda tela que
  fala de desempenho precisa dizer isso.

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
