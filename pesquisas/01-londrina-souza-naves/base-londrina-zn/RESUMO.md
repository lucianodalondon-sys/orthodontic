# RESUMO — Pesquisa Cliente ORTHODONTIC / Zona Norte de Londrina

_2026-07-06. Dataset `data_ortho/`, entregáveis `output_ortho/`, skill
`orthodontic-anuncios-zn` instalada._

## 1. O que foi coletado

| Fonte | Nota | Reviews (c/ texto) |
|---|---|---|
| **Odontoclinic Londrina** (a LÍDER da categoria) | **4,9** (533 aval.) | 95 |
| **OrthoDontic Souza Naves** (o modelo da casa) | **4,6** (561 aval.) | 91 |
| Dra. Aline Oliver (especialista em aparelho) | **4,6** | 100 |
| **OrthoDontic Centro** (Rua Sergipe) | **3,5** | 49 |
| Sorrifácil · OdontoCompany | 3,9 · 3,9 | 121 |
| Clinics Saul Elkind · Dentel ZN | 3,5 · 4,2 | 9 |
| IG unidades Ortho + concorrente Saul | — | ~39 comentários + captions |

Total: **615 reviews de pacientes (438 com texto)** + IG.
> **Recorte corrigido (pedido do Luciano):** foco em ORTODONTIA. Oral Sin
> (implantes) e Oralmed (planos) foram excluídas — são outra categoria. Reaproveitado: estudo de território ZN
(949 vozes, UEL, Sukito). Documental: dente como classe social (IBGE: 34 mi
perderam 13+ dentes; 20 mi nunca foram ao dentista), fenômeno "aparelho
chavoso", história OrthoDontic (nasceu em Londrina/UEL, 2002).

**Custo Apify:** ~US$ 0,45 nesta pesquisa (2ª chave: US$ 1,42/5 acumulado).

## 2. As 7 descobertas que direcionam o marketing

1. **"Atendimento" está em 54% dos reviews (237/438)** — o paciente não avalia
   ortodontia, avalia como foi tratado. A palavra nº1 da categoria. E a LÍDER
   de nota da cidade (Odontoclinic 4,9 > OrthoDontic 4,6) vence exatamente
   nesse eixo — paciente dela: *"aprendi que carinho é competência"*.
2. **A confiança é em PESSOA com nome** — "Dr. João nota 10", "Dra. Bruna",
   "as meninas da recepção" (29+31 menções). Marca não recebe carinho; gente sim.
3. **A MÃE é a decisora** — tratamento do filho por 2–5 anos = projeto de
   família. E **ela lê os reviews antes de escolher** ("graças a Deus li os
   comentários!") → reviews do Google são o campo de batalha decisivo.
4. **O payload emocional é o FIM do tratamento:** *"me senti acolhido e hoje me
   sinto muito realizado. **Consigo sorrir novamente!!**"* — essa frase é a
   campanha inteira.
5. **A ferida nº1 do setor é o pós-venda morto:** "só prestam bom atendimento
   na hora de contratar", telefone/Whats que ninguém atende, "cada mês um
   número diferente". A nº2: **financeiro predatório** ("te amarram… um monte
   de boletos", cobrança antecipada).
6. **Aparelho é STATUS na periferia** (fenômeno "chavoso" + orgulho ZN "venceu")
   — tratar como conquista, nunca como constrangimento. E **dente é classe
   social no Brasil** — sorriso alinhado = distintivo de ascensão.
7. **A OrthoDontic nasceu em Londrina (UEL, 2002)** — "a maior rede do Brasil
   nasceu aqui" é ativo de orgulho territorial pronto pra ZN.

## 3. Alertas estratégicos

- **Mesma marca, 4,6 × 3,5 entre unidades** — o problema é operação por
  unidade, não marca (mesmo padrão do Fish King). Marketing não conserta
  pós-venda: não prometer o que a unidade não entrega.
- **Não localizei unidade OrthoDontic DENTRO da Zona Norte** (Souza Naves/Vila
  Ipiranga é a mais próxima; Centro na Rua Sergipe). Confirmar com o cliente:
  se não houver, a ZN (108 mil hab.) é mercado descoberto — oportunidade de
  expansão ou de campanha "a ZN merece" puxando pra Souza Naves.
- Reviews negativos ativos no Google do Centro (3,5) precisam de gestão antes
  de escalar mídia — a mãe vai ler.

## 4. Próxima rodada (se quiser aprofundar)

1. **Dados internos do cliente**: perfil real dos pacientes por unidade, DMs,
   motivos de cancelamento — subir em `data_ortho/raw/proprio/`.
2. **TikTok/IG de ortodontia popular** (antes/depois, dia de tirar o aparelho)
   para mecânica de formato.
3. **Outras cidades/regiões** — replicar o método (o pipeline está pronto:
   `config/targets_orthodontic.yaml` + env vars).

## 5. Como reproduzir

```bash
export FK_CONFIG=config/targets_orthodontic.yaml
export FK_RAW=data_ortho/raw FK_CORPUS=data_ortho/corpus
python scripts/collect_google_reviews.py
python scripts/collect_apify.py
python scripts/build_corpus.py
```
