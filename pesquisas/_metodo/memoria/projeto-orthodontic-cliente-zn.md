---
name: projeto-orthodontic-cliente-zn
description: Pesquisa profunda do paciente Orthodontic na ZN de Londrina → skill orthodontic-anuncios-zn; cliente potencialmente o maior da agência
metadata: 
  node_type: memory
  type: project
  originSessionId: 426e2b5f-e227-4527-8037-6da9a5046a6c
---

Cliente ORTHODONTIC (maior rede de ortodontia do Brasil, 300+ unidades,
**nasceu em Londrina/UEL em 2002** — 5 amigos, missão "democratizar o acesso").
Luciano: "pode ser nosso maior cliente"; querem entender o cliente POR REGIÃO,
começando pela ZN de Londrina. Mesmo método dos estudos Fish King
([[projeto-fishking-anuncios-zn]] — território ZN reaproveitado integralmente).

Dataset `data_ortho/` (config/targets_orthodontic.yaml + FK_* env vars),
entregáveis `output_ortho/`, skill `orthodontic-anuncios-zn` instalada.

**Coletado (recorte CORRIGIDO pelo Luciano: só ORTODONTIA — Oral Sin=implante e
Oralmed=planos EXCLUÍDAS, não são concorrentes):** 615 reviews (438 c/ texto) —
**Odontoclinic 4,9/533 = A LÍDER da categoria em Londrina (acima da OrthoDontic!),
vence por acolhimento: paciente dela disse "aprendi que carinho é competência"**;
OrthoDontic Souza Naves 4,6/561; Dra. Aline Oliver 4,6 (especialista aparelho);
OrthoDontic Centro 3,5; Sorrifácil/OdontoCompany 3,9; Clinics/Dentel Saul. + IG
unidades. "Atendimento" = 54% dos reviews no recorte ortodontia (era 48%). Documental: dente=classe social (IBGE 34mi perderam 13+ dentes, 20mi
nunca foram ao dentista), fenômeno "aparelho chavoso" (status na periferia).

**Descobertas-mestre:** (1) "atendimento" em 48% dos reviews — paciente avalia
COMO FOI TRATADO, não a técnica; (2) confiança é em PESSOA com nome ("Dr. João
nota 10", "as meninas da recepção"); (3) MÃE é a decisora (tratamento do filho
2-5 anos = projeto de família/ascensão) e LÊ reviews antes ("graças a Deus li
os comentários"); (4) payload emocional = FIM do tratamento: "consigo sorrir
novamente!!"; (5) ferida nº1 do setor = pós-venda morto ("só atendem bem na
hora de contratar", Whats/tel mudo) + financeiro predatório ("te amarram...
boletos"); (6) aparelho = STATUS/conquista na periferia, nunca constrangimento;
(7) "nasceu em Londrina" = ativo de orgulho territorial pronto.

ALERTAS: mesma marca 4,6×3,5 entre unidades (operação, não marca — não prometer
o que a unidade não entrega); NÃO localizei unidade dentro da ZN (Souza Naves/
Vila Ipiranga é a mais próxima — confirmar com cliente; ZN 108k hab pode ser
mercado descoberto). PRÓXIMO: dados internos do cliente em data_ortho/raw/proprio/;
replicar método p/ outras regiões. Gasto 2ª chave: US$1,42/5.

APROFUNDAMENTO "impressionar" (2026-07-14): +217 comentários TikTok @dentistadoaparelho
(audiência nacional de aparelho) → 3 rituais p/ conteúdo: manutenção = ritual mensal com
alegria (escolher COR da borrachinha, "vou pôr cinza"/"só uso preto💔"); "tirar o aparelho"
= contagem regressiva/marco de vida; registro que engaja = HUMOR-CONFISSÃO ("não uso fio
dental há 2 anos" 66k likes) — cumplicidade, nunca bronca. BENCHMARK DA LÍDER (output_ortho/benchmark-odontoclinic.md): Odontoclinic 4,9 vence com
(1) EQUIPE como protagonista do conteúdo (trends c/ auxiliares/recepção — audiência comenta
NAS pessoas); (2) humor de bastidor; (3) porta de entrada barata/concreta = limpeza grátis
via parceria local; (4) depoimento+antes/depois como formato fixo; (5) acolher criança
difícil (medo/autista) = review mais emocional. IRONIA: OrthoDontic SN já tem o ativo
(pacientes nomeiam os drs.) mas o IG esconde em posts genéricos — "publicar o que os
pacientes já amam". Resposta: ser A ESPECIALISTA ("só sorriso, nascida em Londrina") +
avaliação ortodôntica gratuita como porta concreta. Capítulo 07 na apresentação (v3).
IG dela coletado (18 posts+35 coment). Gasto US$2,16/5.

CONTEXTO DE USO: a apresentação será ENVIADA (não apresentada ao vivo) a uma decisora
da Orthodontic para demonstrar poder de inteligência/visão de fora e puxar contrato.
v4 "autovendável" (13 capítulos): hero ganhou nota "tudo minerado de fora, sem
briefing, sem dado interno — com seus dados a precisão multiplica"; NOVO cap.04
Jornada da Mãe (6 etapas disparo→pesquisa/reviews→avaliação→conta R$2.400-6.700/
parcela→2-5 anos manutenção→remoção; funil é um CÍRCULO: review da etapa 6 ganha a
etapa 2 da próxima mãe); cap.11 mídia ganhou funil com métricas (awareness/captação=
custo por avaliação agendada/remarketing/reputação); NOVO cap.13 proposta em 3 fases
(Fase 0 prontidão/reviews, Fase 1 campanha ZN, Fase 2 método como produto p/ 300
unidades — "vamos conversar sobre a ZN e sobre as outras 299"). Pacote p/ Claude/
Claude Design em output_ortho/pacote-apresentacao/ (CONTEUDO.md v4 + DESIGN.md +
PROMPTS.md + apresentacao.html + zip). Luciano quer destrinchar conteúdo ANTES de
fazer o design no Claude Design.

CAMADA 2 DE INTELIGÊNCIA (14/jul, dossiê data_ortho/raw/documental/inteligencia-midia-
e-feridas.md): (A) META AD LIBRARY (actor curious_coder/facebook-ads-library-scraper,
$0.00075/ad, 60 ads) — Londrina: Odontoclinic JÁ compra a mãe ("Será que meu filho
precisa usar aparelho?") vs OrthoDontic só promo genérica nacional; PP: OdontoCompany
abandonou aparelho (11 ads só implante), OrthoDontic PP é a ÚNICA comprando orto
("SEMANA DO APARELHO","JULHO LARANJA") mas 100% promo — camada emocional/geracional
vazia nas 2 praças (flanco aberto). (B) RECLAME AQUI (actor viralanalyzer/reclameaqui-
scraper $0.05/reclamação, FREE cap 1 empresa+3 reclamações/run): OrthoDontic 3/3 =
financeiro/contrato incl. juros/multa na TRANSFERÊNCIA ENTRE UNIDADES (ferida exclusiva
de rede) e TODAS SEM RESPOSTA (vitória barata: rotina de resposta); Odontoclinic rede
tem franquias que fecharam sem reembolso ("20 anos no mesmo endereço" vale ouro).
Capítulos inseridos: Londrina CONTEUDO cap.12 (agora 14 caps), PP cap.05 (agora 7).
Gasto US$3,54/5.

SIGILO DE MÉTODO (pedido Luciano): apresentação NUNCA revela como coletamos — sem
@handles, sem nome de plataforma (Google/Meta/TikTok/Reclame Aqui/Apify), sem "legal/
minerado". Rodapé = "Metodologia proprietária de inteligência de mercado da London
Creative". CONTEUDO-PP.md do cliente já sanitizado; pesquisa detalhada c/ handles fica
INTERNA (patterns.md, fora do pacote do cliente). Usar mais AGENTES p/ aprofundar.

CAMADA 3 (agentes, fontes públicas, dossiês em data_ortho_pp/raw/documental/):
DEMANDA (agente-demanda-ortodontia.md): JULHO=pico orto infantil (Julho Laranja/
férias), dez-jan repete; Nov=intenção mas CFO PROÍBE "desconto Black Friday"; público
busca "aparelho" não "ortodontia"; 15 dúvidas (nº1 preço, nº2 dói) = pautas; mensalidade
fixo R$150-350 (popular R$90-170), âncora plano PP ~R$110/mês; alinhador cresce no
ADULTO 30+ (40-50% dos usuários), não rouba fixo popular ainda. MERCADO
(agente-mercado-local.md): ACHADO-BOMBA = clínica-escola UNOESTE GRATUITA (orto+
implante), ~20 mil atendimentos/ano, curso "melhor do Brasil MEC 2025" = concorrente
invisível → OrthoDontic NÃO vence por preço puro, vence por velocidade/estética/
experiência/relação; renda 25% abaixo média SP, classes D/E=54,5%; bairros ricos
(Damha/Bongiovani/Jd Paulista) vs pobres (Humberto Salvador/Ana Jacinta/Brasil Novo);
crescimento Zona Sul premium + Zona Leste popular; planos odonto 35mi/16,2% SP alto;
Uniodonto local 30 anos. OPERAÇÃO (agente-operacao-interna.md): retrato = "MÁQUINA COMERCIAL com casca clínica"
(~180 vagas comerciais CLT × ~14 dentista PJ; lema RH "Eu Conquisto Sorrisos");
dor do cliente está no CONTRATO não na cadeira (multa rescisão, TAXA PRA REMOVER
aparelho, cobrança de falta — Procon-MG Parecer 06/2023 = cláusula abusiva); RA rede
nota 8,0/89,4% resolvido/1º Prêmio RA 2024 (pós-venda FORMAL bom, mas Google/unidades
não respondem); Glassdoor só 52% recomendam; experiência varia por franqueado. PP:
CNPJ Ortodentic Center desde 2005, só 2 processos, nenhuma vaga/reclamação = estável.
REPUTAÇÃO (agente-reputacao-profunda.md): unidade INVISÍVEL fora do Google (sem
Doctoralia/TripAdvisor); vídeo local (TikTok/YT) = espaço VAZIO; 1 única matéria em 20
anos (Diário de Prudente mai/2025, avalia 2ª filial); sócios Leandro Spolador+Nikelson
Mattos = ENGENHEIROS não dentistas (herói de origem local não contado); Unoeste grátis
NÃO é ameaça no produto (fraca em orto adolescente/adulto, só prevenção+infantil).

CONSOLIDADO: 3 capítulos NOVOS na apresentação PP (06 "O tamanho do jogo"/mercado+
concorrente grátis+2 praças; 07 "O calendário da procura"/julho+dez-jan+adulto 30+;
08 "A joia enterrada"/1ª franquia+engenheiros+continuidade vs troca-de-dentista-da-rede),
timeline agora 6 etapas. CONTEUDO-PP v4 = 11 caps, 100% sanitizado (varredura zero
vazamento: sem Unoeste/Glassdoor/RA/handles/sócios/ferramentas). Dossiês internos em
data_ortho_pp/raw/documental/agente-*.md. Chave 3 gasto US$1,39/5 (agentes = web grátis).

PP APROFUNDADA — MAPA DE INFLUÊNCIA COMPLETO (3ª chave Apify, conta toned_hosta,
gasto US$1,39/5): 12 perfis locais coletados guiados pelos públicos da Orthodontic —
mãe (@espacomaecoruja, @precobaixoprudente, @akitembembarato 450k), família
(@sescthermas 50k), jovem (@nyloungeprudente + TikTok @olucascavalcanti 298k = o
"Sukito de Prudente", 240 comentários), cidadão (@prefeituraprudente, @oimparcialsp,
@livepresidenteprudente); @mulhermais.vc bloqueou scraper. Corpus PP = 953 comentários
(930 de audiência local) + 454 reviews = 1.400+ vozes. AS 4 LÍNGUAS: mãe prática/
afetuosa/tradição ("que dia é o evento?","amo canjica"); família opinativa, ama o Sesc;
jovem hype + HUMOR DE FAMÍLIA (mãe do chinelo, pai cético — personagens cômicos
centrais); cidadão EMOTIVO/SOLIDÁRIO/DE FÉ (comentário + curtido do corpus: "nenhum
bem material vale a vida"; "Papai-do-Céu"). JOIA DE TOM: público verbaliza o valor da
categoria — "que tratem as pessoas com DIGNIDADE E HUMANISMO" = régua de toda
comunicação. CONTEUDO-PP v3 com INTRO-TIMELINE (5 etapas com números e achado,
"baseado em dados", 1.400+ vozes, zero achismo) + tabela das 4 línguas no cap.02.
Pedido do Luciano: sempre martelar "baseado em dados" nas apresentações.

PP REFEITA COM MÉTODO COMPLETO (feedback do Luciano: "não é comparação com Londrina,
é a apresentação DA PRAÇA; público primeiro, depois raio-X da clínica, depois
direcionamento"): coletados +175 comentários da audiência das 2 maiores páginas da
cidade (@guia.presidenteprudente 87k, @gastronomiaprudente 58k). PRUDENTINO: indicação
local CONVERTE ("fomos por conta do seu vídeo"), elogio = superlativo local ("o melhor
da cidade"), premia capricho/seriedade, oferta = "achado" não desespero, programa
casal/família, vocaliza desrespeito de fila; cidade universitária (Unoeste/UNESP),
Parque do Povo, rodeio/agro. RAIO-X unidade: 84 reviews c/ texto = 83×5★+1×1★+ZERO
meio; feed esconde as pessoas, prova social (4,9/582) e gerações fora da comunicação,
zero Prudente no conteúdo, ads só urgência; ferida única = agendamento/remarcação.
JOIA: comentário no post dos 20 anos — "me lembro do dia 02/05/2005, dia da
inauguração!!" — a cidade lembra da inauguração. TESE da apresentação: "o tesouro
guardado na gaveta". Territórios: "O sorriso que cresceu com Prudente" (gerações),
"A mais bem avaliada de Prudente", "Aqui você entende tudo antes de decidir".
CONTEUDO-PP v2 standalone (8 caps, sem comparação; capa "A Primeira Praça").
Gasto US$4,19/5 (sobra ~US$0,8).

2ª PRAÇA — PRESIDENTE PRUDENTE (2026-07-14, pedido: "franquia mais relevante"):
é a 1ª unidade franqueada da rede (2006, 20 anos, engenheiros Spolador/Mattos).
Dataset data_ortho_pp/, entregáveis output_ortho_pp/ (patterns + pacote-apresentacao-pp
c/ CONTEUDO-PP.md + prompt Claude Design). 454 reviews (247 c/ texto). ACHADO-MESTRE:
posição INVERTIDA — em PP a OrthoDontic é LÍDER absoluta (4,9/582, maior nota+volume;
concorrentes NEXA 4,7/618 geral, Dentoclinic 5,0/77, Croorto 4,7, Sorrifácil 4,6) vs
Londrina onde é vice. Atendimento=47% (54% LDA) — lei universal. Assinatura de PP:
CLAREZA ("explicam tudo, não tive dúvida") + "planos que cabem no bolso" (léxico
espontâneo) + GERAÇÕES ("já passei por lá e agora são meus filhos" = fosso dos 20
anos). Medo quase ausente (3 menções). Estratégias OPOSTAS: Londrina=RETOMADA,
PP=DEFESA/celebração 20 anos — prova viva da tese "inteligência por praça" p/ 350
unidades. Hero da apresentação PP: citação geracional. Claude Design: consent OK,
design systems confirmados ("London Creative Design System" b4e8de23, "OrthoDontic
Design System" 7aecc444); Luciano mandou a apresentação de Londrina ele mesmo — NÃO
enviar por MCP sem pedir. Gasto US$2,54/5.

APRESENTAÇÃO CLIENTE pronta:
artifact https://claude.ai/code/artifact/a6ecd5ab-9a9e-4987-bd79-0abffff5dcae (cópia em
output_ortho/apresentacao.html) — hero "Consigo sorrir novamente", 10 capítulos, personas,
placar de notas, 3 territórios com copy, mídia, alertas. Gasto: US$1,76/5.
