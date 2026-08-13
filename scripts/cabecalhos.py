#!/usr/bin/env python3
"""
cabecalhos.py — toda ferramenta do portal abre EXPLICANDO o que ela faz.

Por que este arquivo existe
---------------------------
A tela "Alertas nas fichas do Google" abria com um rótulo, quatro números
grandes e uma lista. Quem chegava nela não tinha como saber que pergunta
aquilo responde, para quem serve, nem por que os números importam. Parecia
painel de sistema — e painel de sistema é o que faz a diretoria fechar a
aba.

A régua, daqui em diante:

  NENHUMA FERRAMENTA APARECE NA TELA SEM DIZER, EM UMA FRASE DE BALCÃO,
  QUE PERGUNTA ELA RESPONDE E PARA QUEM.

E o método sai de cima. Ele continua na tela — esconder como se mede é o
que faz o número virar palpite — mas vai para o RODAPÉ, depois do conteúdo,
como nota de fim. Ninguém precisa ler a metodologia para entender a
manchete; quem duvida precisa achá-la sem perguntar.

O que é um cabeçalho
--------------------
    sobrelinha  a família: DA REDE INTEIRA · DESTA CLÍNICA · DESTA CIDADE
    titulo      uma FRASE, não um rótulo. "Onde a marca está mal na rua"
                é rótulo; "Uma ficha errada no Google custa paciente antes
                da primeira consulta" é frase.
    pergunta    a pergunta literal que a ferramenta responde
    para_quem   franqueado · consultor de campo · franqueadora · expansão
    como_ler    a instrução de leitura, quando a tela não é óbvia
    o_que_nao_e o limite, escrito. É o que impede a leitura errada.
    metodo      como foi medido — vai no RODAPÉ

Este script NÃO inventa número: cabeçalho é texto autorado, e todo número
continua saindo do build. Ele também FALHA ALTO quando um payload de tela
não tem cabeçalho — assim nenhuma ferramenta nova estreia muda.

Uso:
    python3 scripts/cabecalhos.py
    python3 scripts/cabecalhos.py --salvar
"""
import argparse, json, pathlib, sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PORTAL = RAIZ/"dados"/"portal"

# Arquivos que NÃO são tela: índice, régua interna, insumo de outra tela.
# Estão listados um a um de propósito — "não tem tela" é uma decisão, e
# decisão não declarada vira buraco silencioso.
SEM_TELA = {
    "manifest":   "o índice que o portal lê antes de tudo",
    "padrao":     "a checagem interna de completude da praça",
    "corretor":   "dicionário de correção de nomes",
    "evidencias": "as fontes citadas, usadas dentro das outras telas",
    "achados":    "texto autorado consumido pela home",
    "rede":       "insumo da tela de praças",
    "watchlist":  "a lista de quem é medido toda semana — insumo da coleta",
    "rede_cruzamento":   "insumo do confronto com o rival",
    "cabecalhos": "o índice dos próprios cabeçalhos, para os blocos que "
                  "vivem dentro da página da clínica",
}

C = {
# ------------------------------------------- as seis capacidades do portal
"inteligencia_da_rede": dict(
    sobrelinha="INTELIGÊNCIA DA REDE",
    titulo="O que a OrthoDontic precisa saber esta semana",
    pergunta="O que está acontecendo na rede que ninguém perceberia "
             "olhando loja por loja?",
    para_quem=["franqueadora", "consultor de campo", "expansão"],
    como_ler="Cinco perguntas, e nada mais. Cada cartão diz o que "
             "aconteceu, por que importa, quem precisa agir, o que fazer "
             "— e traz o texto pronto para encaminhar.",
    o_que_nao_e="Não é atalho para as ferramentas. Nada aqui se repete lá "
                "dentro: cada cartão é um cruzamento de várias delas.",
    metodo="o cruzamento dos motores do portal, filtrado pelo que muda "
           "decisão: aprendizado, agenda, mercado, playbook e radar."),

"rede_aprende": dict(
    sobrelinha="O QUE A REDE ENSINA",
    titulo="O que a rede descobriu, e com quanta força",
    pergunta="Depois de observar dezenas de clínicas, milhares de "
             "pacientes e centenas de concorrentes, o que sabemos hoje que "
             "não sabíamos antes?",
    para_quem=["franqueadora"],
    como_ler="Quatro níveis de força, calculados do próprio placar: "
             "confirmado, ganhando força, em teste e derrubado. O nível "
             "derrubado é o que dá crédito aos outros três.",
    o_que_nao_e="Não é causa. Nenhuma linha prova que fazer X produz Y — "
                "são padrões observados, e um deles já caiu quando a base "
                "cresceu.",
    metodo="cada afirmação é testada contra todas as praças com amostra "
           "para votar, e o nível sai do placar, nunca de rótulo escrito "
           "à mão."),

"agenda": dict(
    sobrelinha="PARA O TIME DE CAMPO",
    titulo="As conversas que a semana pede",
    pergunta="Em quais unidades o consultor precisa entrar esta semana, e "
             "o que ele leva para cada conversa?",
    para_quem=["consultor de campo", "franqueado"],
    como_ler="Cada linha é uma visita: o que vimos, o que conversar, o "
             "que levar como evidência, o que NÃO fazer e quando "
             "verificar de novo.",
    o_que_nao_e="Não marca visita, não guarda quem foi nem confirma "
                "execução. Quem responde se algo aconteceu é a próxima "
                "medição.",
    metodo="a fila de intervenção, colada com os gêmeos da rede e a "
           "jornada do paciente, na ordem em que a conversa acontece."),

"gemeos": dict(
    sobrelinha="DESTA CLÍNICA",
    titulo="A unidade da rede mais parecida com esta — e o que as separa",
    pergunta="Existe outra loja jogando o mesmo jogo? O que ela faz de "
             "diferente?",
    para_quem=["consultor de campo", "franqueado", "franqueadora"],
    como_ler="O gêmeo é escolhido por MERCADO — população, público "
             "adulto, densidade da categoria e idade da loja —, nunca por "
             "resultado: senão a conta seria circular.",
    o_que_nao_e="Não é causa. A tela lista diferenças observáveis; dizer "
                "que uma delas explica o resultado é trabalho da visita.",
    metodo="distância entre lojas em quatro eixos de mercado, com o "
           "número dos dois lados em cada diferença."),

"anomalias": dict(
    sobrelinha="DA REDE INTEIRA",
    titulo="Quem está muito longe do que os semelhantes conseguem",
    pergunta="Que unidade deveria estar melhor do que está — e qual está "
             "fazendo algo que precisamos entender?",
    para_quem=["franqueadora", "consultor de campo"],
    como_ler="A comparação é contra os gêmeos de cada loja, não contra a "
             "mediana da rede: comparar Mafra com a média de 45 unidades, "
             "metade em capital, faria toda cidade pequena parecer "
             "anômala.",
    o_que_nao_e="Não é significância: são poucos pontos de comparação. "
                "Serve para escolher onde olhar, não para concluir.",
    metodo="ritmo de avaliações da loja contra a mediana dos semelhantes, "
           "só entre as leituras comparáveis."),

"playbook": dict(
    sobrelinha="DA REDE INTEIRA",
    titulo="O que os concorrentes que avançam fazem — e o que testamos "
           "e não explicou nada",
    pergunta="Somando todas as praças, o que separa o concorrente que "
             "avança do que não avança?",
    para_quem=["franqueadora", "marketing e agência"],
    como_ler="A segunda metade da tela é a que dá crédito à primeira: "
             "eixo testado que não separou nada fica publicado, com o "
             "número dos dois lados.",
    o_que_nao_e="Não é receita. Frequência que anda junto com ritmo é "
                "pista, não mecanismo — e quando o grupo é pequeno "
                "demais, a comparação não é publicada.",
    metodo="voz do paciente dos concorrentes que disputam aparelho, "
           "somada às ofertas anunciadas em cada praça."),

# ---------------------------------------------------------------- a home
"franqueadora": dict(
    sobrelinha="DA REDE INTEIRA",
    titulo="A rede inteira, lida por fora, todo dia",
    pergunta="O que mudou no mercado das nossas clínicas desde a última "
             "vez que olhamos?",
    para_quem=["franqueadora", "consultor de campo"],
    como_ler="Cada bloco é uma pergunta de negócio com o número ao lado. "
             "Clique no número para ver de onde ele saiu.",
    o_que_nao_e="Não é o resultado da rede. Nada aqui vem de contrato, "
                "lead ou faturamento — o portal só enxerga o que está "
                "publicado na rua.",
    metodo="fontes públicas — ficha e busca do Google, avaliações de "
           "pacientes, biblioteca de anúncios, imprensa local e IBGE — "
           "coletadas sempre do mesmo jeito, semana após semana."),

# ------------------------------------------------------------- clínicas
"clinicas_indice": dict(
    sobrelinha="DA REDE INTEIRA",
    # sem número no título: "número escrito à mão apodrece" — a contagem
    # vem pronta do build, em `frase_da_grade`
    titulo="Todas as unidades da rede, e o que já sabemos de cada uma",
    pergunta="Qual unidade precisa de atenção primeiro — e quanto da rede "
             "ainda não foi escutado?",
    para_quem=["franqueadora", "consultor de campo"],
    como_ler="A grade vem ordenada por alerta: a primeira é a que mais "
             "dói hoje. As unidades apagadas ainda não foram estudadas — "
             "o nome está lá para mostrar o tamanho do que falta.",
    o_que_nao_e="Não é ranking de desempenho. A ordem mede risco "
                "observável na rua, não faturamento.",
    metodo="lista oficial da rede, lida no site da franqueadora, cruzada "
           "com a ficha do Google de cada unidade."),

"fila": dict(
    sobrelinha="DA REDE INTEIRA",
    titulo="Onde ir primeiro, e o que fazer quando chegar lá",
    pergunta="Em quais unidades a OrthoDontic está perdendo atenção "
             "local, para qual concorrente, e onde intervir primeiro?",
    para_quem=["consultor de campo", "franqueadora"],
    como_ler="Cada linha é uma tarefa com dono e prazo, não um aviso. "
             "A cor é o tamanho do risco; o texto embaixo é o motivo "
             "medido que a abriu.",
    o_que_nao_e="Perder atenção não é perder venda: é perder presença em "
                "busca, avaliação, publicidade e movimento — as quatro "
                "coisas que dá para ver de fora.",
    metodo="seis gatilhos, cada um com um número que está num arquivo. "
           "Alerta sem arquivo não entra."),

"timeline": dict(
    sobrelinha="DESTA CLÍNICA",
    titulo="A vida da clínica, medição por medição",
    pergunta="O que mudou nesta unidade desde que começamos a medir?",
    para_quem=["franqueado", "consultor de campo"],
    como_ler="Cada ponto é uma medição, com a data. O que não foi medido "
             "aparece como buraco, não como zero.",
    o_que_nao_e="Não é histórico da clínica: começa no dia em que a "
                "medição começou, e não antes.",
    metodo="a série append-only de cada loja, chaveada por local_id."),

"presenca_por_loja": dict(
    sobrelinha="DESTA CLÍNICA",
    titulo="Quando a cidade procura, esta clínica aparece?",
    pergunta="Em quantas das buscas que a cidade faz esta unidade "
             "aparece — e quem aparece no lugar dela?",
    para_quem=["franqueado", "consultor de campo"],
    como_ler="A conta é por LOJA, não por cidade: em cidade com mais de "
             "uma unidade, cada uma tem o próprio resultado.",
    o_que_nao_e="Aparecer pouco na busca da cidade inteira não quer dizer "
                "invisível — em metrópole o paciente busca de onde está. "
                "Veja também a busca perto da clínica.",
    metodo="frases reais de busca da cidade, mandadas ao mapa do Google, "
           "com a loja identificada pelo contador de avaliações."),

"perto_da_loja": dict(
    sobrelinha="DESTA CLÍNICA",
    titulo="Quem está do lado da clínica encontra a clínica?",
    pergunta="Buscando a partir do endereço desta unidade, ela aparece — "
             "e em que posição?",
    para_quem=["franqueado", "consultor de campo"],
    como_ler="Esta é a segunda escala da busca. São Paulo aparecia em 0 "
             "de 193 buscas da cidade e em 10 de 20 quando a busca parte "
             "do endereço de cada loja. As duas leituras são verdadeiras "
             "e respondem coisas diferentes.",
    o_que_nao_e="O raio NÃO é área de captação, e ficar atrás de um "
                "vizinho NÃO é perder paciente para ele.",
    metodo="as mesmas frases, com viés de local circular no endereço de "
           "cada unidade. Viés é preferência, não barreira."),

"caixa_de_respostas": dict(
    sobrelinha="DESTA CLÍNICA",
    titulo="As avaliações que ficaram sem resposta",
    pergunta="Quais pacientes escreveram e não foram respondidos — e há "
             "quanto tempo?",
    para_quem=["franqueado"],
    como_ler="A lista está ordenada pelo que dói mais: nota baixa e "
             "esperando há mais tempo.",
    o_que_nao_e="Responder não apaga a nota. Muda o que o próximo "
                "paciente lê quando chega na ficha.",
    metodo="avaliações públicas do Google, com e sem resposta do dono, "
           "por loja."),

"jornada": dict(
    sobrelinha="DESTA CLÍNICA",
    titulo="Em que momento do atendimento a clínica dói",
    pergunta="Quando o paciente reclama, ele está falando de qual etapa — "
             "telefone, recepção, cadeira, manutenção ou cobrança?",
    para_quem=["franqueado", "consultor de campo"],
    como_ler="'Atendimento' não é um problema: atendimento na recepção, "
             "na cadeira e no telefone são três problemas de três donos "
             "diferentes. A tela separa os onze momentos, por loja.",
    o_que_nao_e="Não é análise de sentimento do texto. A dor sai da NOTA, "
                "que é medida; o texto só diz de que momento a pessoa "
                "estava falando.",
    metodo="classificação das avaliações nos onze momentos da jornada, "
           "com o sentimento vindo da nota."),

"execucao": dict(
    sobrelinha="DESTA CLÍNICA",
    titulo="O que fazer nesta unidade, nesta semana",
    pergunta="Qual é a próxima ação desta clínica, quanto custa, quem faz "
             "e como saberemos que funcionou?",
    para_quem=["franqueado", "consultor de campo"],
    como_ler="Uma prioridade por vez, com prazo e critério de "
             "verificação. O que não é prioridade fica fora da tela.",
    o_que_nao_e="O portal não sabe se a ação foi executada — ele não fala "
                "com a unidade. Ele sabe refazer a mesma medição depois.",
    metodo="a ação nasce do gatilho que pesa mais na fila, e o critério "
           "de verificação é repetir a medição que abriu o alerta."),

# ---------------------------------------------------------------- praça
"voz_da_cidade": dict(
    sobrelinha="DESTA CIDADE",
    titulo="O que os pacientes desta cidade escrevem",
    pergunta="Do que a cidade fala quando fala de dentista e de aparelho?",
    para_quem=["franqueado", "franqueadora"],
    como_ler="Os temas são da CIDADE, não da loja — é a leitura de "
             "mercado que serve para todas as unidades da praça.",
    o_que_nao_e="Não é pesquisa de opinião: é o que quem já foi atendido "
                "escolheu escrever, e quem escreve não é a cidade toda.",
    metodo="as avaliações públicas de todas as clínicas medidas na "
           "cidade, nossas e da concorrência."),

"oferta": dict(
    sobrelinha="DESTA CIDADE",
    titulo="O que o concorrente está vendendo, com que palavras",
    pergunta="Qual é a guerra comercial desta cidade — preço, urgência, "
             "parcelamento — e que posição está vaga?",
    para_quem=["franqueado", "franqueadora"],
    como_ler="Contar anúncio não é ler a oferta: aqui o texto de cada "
             "anúncio foi lido e classificado por eixo.",
    o_que_nao_e="Não é o quanto o concorrente gasta. A biblioteca de "
                "anúncios mostra o que está no ar, não o orçamento.",
    metodo="texto dos anúncios ativos na biblioteca pública do Meta, "
           "coletados por consulta da própria cidade."),

"anuncios": dict(
    sobrelinha="DESTA CIDADE",
    titulo="Quem compra mídia de aparelho nesta cidade",
    pergunta="Quem está anunciando aparelho aqui, desde quando, e quem "
             "entrou ou saiu do leilão?",
    para_quem=["franqueado", "franqueadora"],
    como_ler="Odontologia não é ortodontia: dos anúncios coletados, só "
             "os que falam de aparelho entram. Os descartados aparecem "
             "contados, com o motivo.",
    o_que_nao_e="Estar fora do leilão só é problema quando o leilão está "
                "cheio. Praça vazia é oportunidade, não ameaça.",
    metodo="biblioteca de anúncios do Meta, consultada pelo nome da "
           "cidade e dos concorrentes locais."),

"bairros": dict(
    sobrelinha="DESTA CIDADE",
    titulo="A cidade por dentro: onde estão as clínicas",
    pergunta="Em que bairros a concorrência se concentra, e onde não há "
             "quase ninguém?",
    para_quem=["franqueadora", "expansão", "franqueado"],
    como_ler="Bairro repetido divide a concentração e inventa espaço "
             "vago: os nomes são agrupados antes de contar.",
    o_que_nao_e="Concentração de clínicas NÃO é demanda, e bairro vazio "
                "não é bairro disponível.",
    metodo="endereço das clínicas varridas na cidade, com o bairro "
           "normalizado e a coordenada que já vinha na ficha."),

"o_que_a_cidade_publica": dict(
    sobrelinha="DESTA CIDADE",
    titulo="O que a imprensa local publicou",
    pergunta="A cidade está falando de saúde, de obra, de emprego — algo "
             "que muda o mercado da clínica?",
    para_quem=["franqueado", "franqueadora"],
    como_ler="É contexto da praça, não sinal de venda. Serve para a "
             "conversa da visita e para entender movimento local.",
    o_que_nao_e="Notícia não é demanda. Nada aqui prova que alguém "
                "procurou aparelho.",
    metodo="feeds públicos de veículos locais, lidos por data de "
           "publicação."),

# ----------------------------------------------------- leitura de rede
"padroes": dict(
    sobrelinha="DA REDE INTEIRA",
    titulo="O que se repete nas lojas que crescem",
    pergunta="O que as unidades acompanhadas ensinam quando lidas juntas "
             "— e quais explicações o dado derrubou?",
    para_quem=["franqueadora"],
    como_ler="Cada hipótese foi testada contra o histórico. As que "
             "caíram ficam na tela: explicação derrubada vale tanto "
             "quanto explicação confirmada.",
    o_que_nao_e="Correlação entre lojas não é causa. Nenhuma linha aqui "
                "prova que fazer X produz Y.",
    metodo="eliminação sobre o histórico completo de avaliações, POR "
           "LOJA. Cuiabá é a praça-controle: três lojas idênticas no "
           "papel, resultados opostos."),

"rival": dict(
    sobrelinha="DA REDE INTEIRA",
    titulo="O que o concorrente que ganha faz, na voz do paciente dele",
    pergunta="Em que a clínica que lidera a praça é elogiada, e nós não?",
    para_quem=["franqueadora", "consultor de campo", "franqueado"],
    como_ler="A comparação é por proporção, dentro da mesma praça. "
             "Quando o mesmo buraco aparece em quase toda a rede, a "
             "decisão deixa de ser da unidade e passa a ser de "
             "franqueadora — e a tela diz de quem é.",
    o_que_nao_e="Não é o que ele fatura nem o que ele gasta. É o que o "
                "paciente dele escolheu escrever.",
    metodo="avaliações dos concorrentes que disputam aparelho, com "
           "amostra mínima por clínica e corte de diferença mínima."),

"acoes": dict(
    sobrelinha="DA REDE INTEIRA",
    titulo="O que a rede fez depois do alerta, e o que aconteceu",
    pergunta="Alguma coisa mudou por causa deste portal?",
    para_quem=["franqueadora"],
    como_ler="Cada arco guarda a métrica antes, a ação recomendada e a "
             "métrica depois. Arco novo demais aparece como 'cedo "
             "demais', não como fracasso.",
    o_que_nao_e="Isto NÃO prova causa: não há grupo de controle e "
                "ninguém de dentro confirma que a ação foi executada.",
    metodo="o mesmo número, medido de novo, na mesma régua, depois de um "
           "prazo mínimo."),

"o_que_mudou": dict(
    sobrelinha="DA REDE INTEIRA",
    titulo="O que se moveu desde a última medição",
    pergunta="O que mudou de uma medição para a outra, em cada praça?",
    para_quem=["franqueadora", "consultor de campo"],
    como_ler="Praça medida uma vez só não tem movimento a declarar: ela "
             "tem linha de base, que é diferente de 'não mudou'.",
    o_que_nao_e="Falta de coleta nunca vira evento. Se não medimos, a "
                "tela diz que não medimos.",
    metodo="comparação entre as duas últimas medições de cada praça, com "
           "a janela declarada."),

"mudancas_do_mercado": dict(
    sobrelinha="DA REDE INTEIRA",
    titulo="Quem entrou, quem saiu e quem acelerou",
    pergunta="Que movimento de concorrente aconteceu desde a última "
             "rodada?",
    para_quem=["franqueadora", "consultor de campo"],
    como_ler="Só entra movimento comparável: quando não se sabe o que "
             "foi perguntado nas duas rodadas, o evento não é publicado.",
    o_que_nao_e="Uma varredura que devolve um conjunto diferente de "
                "clínicas não é mercado que mudou — é coleta que variou. "
                "Por isso o acompanhamento semanal é feito sobre lista "
                "fixa.",
    metodo="lista estável de rivais e unidades, chaveada por place_id, "
           "medida toda semana."),

"rede_inteira": dict(
    sobrelinha="DA REDE INTEIRA",
    titulo="A vitrine da marca na rua: a ficha de cada unidade no Google",
    pergunta="Quando alguém procura uma unidade da OrthoDontic, o que "
             "ele encontra — e onde a marca está mal apresentada?",
    para_quem=["franqueadora", "consultor de campo"],
    como_ler="A ficha do Google é a fachada digital: nota, avaliações, "
             "endereço e horário. Um alerta aqui é conserto de vitrine, "
             "e vários deles não dependem do franqueado.",
    o_que_nao_e="Não é ritmo nem voz do paciente — para isso existe a "
                "varredura completa. Aqui é retrato: como a unidade "
                "aparece agora para quem procura.",
    metodo="uma chamada por unidade à ficha pública do Google, para "
           "todas as unidades da lista oficial."),

# --------------------------------------------------------------- radar
"radar": dict(
    sobrelinha="PARA CRESCER A REDE",
    titulo="As cidades que merecem ser estudadas primeiro",
    pergunta="Onde a OrthoDontic ainda não está, e a categoria comporta "
             "mais uma clínica?",
    para_quem=["expansão", "franqueadora"],
    como_ler="A pergunta não é 'onde abrir'. É 'quais cidades merecem o "
             "estudo profundo antes de qualquer conversa'.",
    o_que_nao_e="Não é projeção de faturamento nem garantia de que abrir "
                "ali funciona. E cidade não conferida em duas fontes "
                "independentes não entra em recomendação.",
    metodo="triagem demográfica dos 5.570 municípios, depois varredura "
           "da categoria na cidade, depois estudo escrito."),

"funil_nacional": dict(
    sobrelinha="PARA CRESCER A REDE",
    titulo="Dos 5.570 municípios até a fila de estudo",
    pergunta="Quantas cidades sobram em cada filtro, e por que as outras "
             "caíram?",
    para_quem=["expansão"],
    como_ler="Cada degrau mostra quantas cidades passaram e qual foi o "
             "corte. O funil existe para tornar o descarte visível.",
    o_que_nao_e="Passar no funil não é aprovação: é entrar na fila de "
                "quem merece ser estudado.",
    metodo="dados públicos do IBGE — população, faixa etária e porte — "
           "cruzados com a presença atual da rede."),

"sazonalidade": dict(
    sobrelinha="DESTA CIDADE",
    titulo="Existe mês de pico para procurar aparelho?",
    pergunta="A procura por aparelho tem estação nesta região?",
    para_quem=["franqueado", "franqueadora"],
    como_ler="O veredito é por estado, e na maior parte deles a resposta "
             "medida foi NÃO — o volume de busca não sustenta publicar "
             "uma curva.",
    o_que_nao_e="Herdar a curva de uma região para outra é inventar. Foi "
                "Mafra que derrubou a tese nacional de que dezembro e "
                "janeiro são pico: lá é vale.",
    metodo="Google Trends por UF, cinco anos, com duas travas: volume "
           "mínimo e repetição do mês de pico."),
}


def aplica(nome, dados):
    """Injeta o cabeçalho no payload. Devolve True quando escreveu."""
    if nome in SEM_TELA or nome.startswith("clinicas/"):
        return False
    cab = C.get(nome)
    if not cab:
        return None                      # sem cabeçalho = falha, lá em cima
    dados["cabecalho"] = dict(cab, e_texto_autorado=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    a = ap.parse_args()

    arquivos = sorted(p for p in PORTAL.glob("*.json"))
    postos, pulados, faltando = [], [], []
    for p in arquivos:
        nome = p.stem
        try:
            dados = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"  ✗ {nome}: {e}")
            sys.exit(1)
        r = aplica(nome, dados)
        if r is None:
            faltando.append(nome)
            continue
        if r is False:
            pulados.append(nome)
            continue
        postos.append(nome)
        if a.salvar:
            p.write_text(json.dumps(dados, ensure_ascii=False, indent=1) + "\n",
                         encoding="utf-8")

    print(f"\n  {len(postos)} telas com cabeçalho · "
          f"{len(pulados)} arquivos sem tela (declarados)")
    for n in postos:
        print(f"    ✓ {n:<24}{C[n]['titulo'][:52]}")
    for n in pulados:
        print(f"    · {n:<24}{SEM_TELA[n]}")

    # O ÍNDICE CENTRAL. A página da clínica junta dez ferramentas numa tela
    # só, e cada bloco precisa do mesmo cabeçalho da ferramenta de onde ele
    # veio. Sem este arquivo o casco teria de abrir dez payloads para
    # escrever dez títulos.
    if a.salvar:
        (PORTAL/"cabecalhos.json").write_text(json.dumps({
            "o_que_e": "O cabeçalho de cada ferramenta do portal: a "
                       "pergunta que ela responde, para quem serve, como "
                       "se lê e como foi medida.",
            "por_que_existe": "ferramenta que não diz o que faz vira "
                              "painel de sistema, e painel de sistema é o "
                              "que faz quem decide fechar a aba",
            "e_texto_autorado": True,
            "onde_vai_o_metodo": "no RODAPÉ da tela, depois do conteúdo — "
                                 "nunca embaixo do título",
            "ferramentas": C,
            "sem_tela": [{"arquivo": k, "porque": v}
                         for k, v in sorted(SEM_TELA.items())],
        }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"  → dados/portal/cabecalhos.json ({len(C)} ferramentas)")

    if faltando:
        # FERRAMENTA SEM EXPLICAÇÃO NÃO ESTREIA. Foi assim que "Alertas nas
        # fichas do Google" foi para a tela com quatro números e nenhuma
        # frase dizendo para que servem.
        print(f"\n  ✗ FALHA: {len(faltando)} payload(es) de tela sem "
              f"cabeçalho:")
        for n in faltando:
            print(f"      {n}")
        print("\n  escreva o cabeçalho em scripts/cabecalhos.py, ou "
              "declare o arquivo em SEM_TELA com o motivo.")
        sys.exit(1)

    if not a.salvar:
        print("\n  (--salvar para gravar nos payloads)")


if __name__ == "__main__":
    main()
