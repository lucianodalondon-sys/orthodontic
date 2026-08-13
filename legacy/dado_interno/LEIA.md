# O snapshot do Conecta — fora do produto, de propósito

`funil.jsonl` guarda uma medição interna de Mafra: 5.050 interessados, 298
agendamentos, 147 comparecimentos, 110 fechados, 109 pagos. Veio do Conecta,
uma vez, e está congelada desde então.

**Ela não pode voltar para `dados/serie/`.** A regra do produto é permanente e
está no `CLAUDE.md`:

> O portal é feito **inteiramente com informação externa**. Não temos CRM,
> contrato, faturamento, lead, nem o franqueado ao telefone — e não vamos ter.

Enquanto este arquivo vivia na série, o build montava funil, taxas e régua da
rede para Mafra, e a praça abria com "única com dado interno". Uma exceção
escondida no pipeline destrói o posicionamento inteiro: se a diretoria
pergunta "de onde vem esse número?", a resposta não podia ser "de um lugar
que nós dizemos que não usamos".

O histórico fica aqui porque apagar medição é pior que guardá-la fora do
caminho. `cruzamento.jsonl()` recusa-se a ler `funil` — o guarda está em
`scripts/cruzamento.py`.
