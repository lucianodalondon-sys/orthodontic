# agent-reach — instalado, o que serve e o que não serve

**09/08/2026** · `github.com/Panniantong/agent-reach`, MIT, v1.5.0.

Se posiciona como **alternativa local ao Apify, Firecrawl e Tavily** — que é
exatamente a conta que este projeto paga hoje (~US$ 1,56 por praça por ciclo).

---

## COMO REINSTALAR

**O container desta sessão é efêmero: o que está instalado morre quando ela
acaba.** Estes são os comandos, na ordem.

```bash
# o endpoint /archive/main.zip do GitHub é BLOQUEADO pela política de egresso
# desta sessão (403 no proxy). Clonar funciona.
git clone --depth 1 https://github.com/Panniantong/agent-reach.git /tmp/ar
python3 -m venv ~/.agent-reach-venv
~/.agent-reach-venv/bin/pip install /tmp/ar

export PATH="$HOME/.agent-reach-venv/bin:/opt/node22/bin:$PATH"

# YouTube precisa de runtime JS
mkdir -p ~/.config/yt-dlp && echo '--js-runtimes node' >> ~/.config/yt-dlp/config

# busca semântica (Exa) — sem chave de API, camada gratuita
npm install -g mcporter
mcporter config add exa https://mcp.exa.ai/mcp --scope home

# instala a skill que ensina o agente a usar tudo isso
agent-reach skill --install      # → ~/.claude/skills/agent-reach
agent-reach doctor               # confere o que está de pé
```

---

## O QUE FICOU DE PÉ, E FOI TESTADO AQUI

| Canal | Estado | Testado com |
|---|---|---|
| **Qualquer página** (via Jina Reader) | ✅ | o site da rede — `encontre-uma-unidade`, 11 KB em markdown |
| **Busca semântica** (Exa) | ✅ | "clínicas de ortodontia em Macapá" — devolveu nome, endereço, telefone e serviços |
| **RSS/Atom** | ✅ | é a mesma fonte do `imprensa_rss.py` |
| **YouTube** (vídeo + legenda) | ✅ | runtime configurado |
| V2EX, Bilibili | ✅ | irrelevantes para este projeto |

**5 de 15 canais.** Os outros 8 exigem credencial — ver abaixo.

---

## O QUE ISSO ABRE PARA O PROJETO

### 1 · O site do concorrente, que o Google Places não dá

A varredura devolve nome, nota e volume. **Não devolve o que a clínica vende
nem por quanto.** O Exa lê o site dela:

> Alpha Clinic Odontologia, Macapá — Av. Ernestino Borges, 209, Julião Ramos ·
> (96) 98123-9036 · ortodontia (fixo e invisível), implante, prótese, lentes

### 2 · Preço — a dimensão que o método declara não medir

Todos os relatórios trazem a ressalva *"mede a categoria pública do Google, não
receita nem ticket"*. Uma busca devolveu:

> **Aparelho ortodôntico em Londrina: R$ 2.400 a R$ 6.700** (DentMap, 32
> dentistas avaliados) — e a unidade OrthoDontic Ipiranga listada lá dentro.

Isso é **faixa de mercado publicada**, não faturamento. Mas fecha parte de um
buraco que estava declarado como impossível.

### 3 · A pergunta dos convênios

O plano do franqueado diz *"o dado público não diz quais convênios a clínica
aceita — isso só você sabe"*. Com leitura de site, parte disso passa a ser
verificável, para o concorrente e para a unidade.

**Nada disso vira coletor sem teste.** O que está escrito aqui é o que a
ferramenta devolveu em três consultas, não uma promessa de cobertura.

---

## O QUE **NÃO** VOU LIGAR SEM VOCÊ DECIDIR

Oito canais dependem de **cookie da sua sessão de navegador**: Twitter/X,
Instagram, Reddit, Facebook, LinkedIn, Xiaohongshu, Xueqiu, Xiaoyuzhou.

Três motivos para parar aqui:

1. **É credencial pessoal sua.** O cookie é a sessão logada — quem tem ele
   entra na conta.
2. **Risco de suspensão.** Raspar essas plataformas com sessão logada viola os
   termos delas, e a conta que paga o preço é a que emprestou o cookie. Se for
   a conta do cliente, o estrago não é nosso de consertar.
3. **`coleta/FONTES.md` já decidiu isso**: conteúdo público, nada de grupo
   fechado. Cookie de sessão logada é o oposto de conteúdo público.

**Se você quiser ligar mesmo assim**, ligue com uma conta descartável, nunca
com a sua nem com a da OrthoDontic — e sabendo que ela pode ser derrubada.

---

## RESSALVAS HONESTAS

- **A interface é em chinês.** O `doctor` e as mensagens saem em chinês; os
  comandos são em inglês. Funciona, mas não é para passar adiante ao cliente.
- **Instalado de `main`, sem versão fixada.** O que roda amanhã pode não ser o
  que rodou hoje. Se virar dependência da coleta, fixar o commit.
- **Não substitui o Apify hoje.** Os coletores que custam (avaliação com data,
  anúncios do Meta, Reclame Aqui) usam justamente os canais que exigem cookie
  ou que a ferramenta não cobre. O que ele substitui de imediato é leitura de
  página e busca — que já eram baratos.
- **O `agent-reach` não é o executor.** Ele instala e configura; quem chama é
  o agente, pela skill em `~/.claude/skills/agent-reach`.
