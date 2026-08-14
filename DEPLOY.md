# Publicar o portal — Vercel, com porta de verdade

## O que se publica, e de onde vem

O portal tem duas metades que nascem em lugares diferentes:

| pasta | quem faz | pode editar aqui? |
|---|---|---|
| `casco/` | Claude Design | **não** — só substituir por entrega nova |
| `dados/portal/` | `scripts/build_portal.py` | **não** — o conserto é no build |
| `entrada/login.html` | este repositório | sim |
| `api/entrar.js` + `middleware.js` | este repositório | sim |

`scripts/publica_site.py` junta tudo em `site/`, que é o que a Vercel serve.
`site/` fica fora do git: quem manda são as origens.

```bash
python3 scripts/publica_site.py --limpar
```

Ele **falha alto** quando falta peça — inclusive quando o casco pede um
payload que o build não escreveu, que é o erro que sairia como tela em
branco no navegador do cliente sem nenhum aviso no terminal.

## A porta

Login conferido no navegador não protege nada: a senha ficaria dentro do
arquivo que qualquer um baixa, e `dados/portal/*.json` continuaria aberto
por URL direta. Por isso a conferência é no servidor:

```
navegador → middleware.js  (roda ANTES de qualquer arquivo sair)
              ├── tem cookie assinado?  → entrega o portal
              └── não tem              → /entrar
                                           └── api/entrar.js confere o
                                               código e assina o cookie
```

O `matcher` do middleware cobre tudo menos `/assets` (para a própria tela
de login ter marca e tipografia) e `/api/entrar`. **Os JSON estão dentro
do que é protegido** — é esse o ponto.

Se `CODIGO_DE_ACESSO` ou `SEGREDO_DA_SESSAO` não estiverem configurados, o
middleware devolve 503 e **não deixa passar**. Falhar fechado é de
propósito: um middleware que libera quando não está configurado publica o
portal inteiro no primeiro deploy distraído, e o site continua funcionando,
então ninguém percebe.

## Passo a passo

**1 · Repositório privado.** Em Settings → General → Danger Zone. Enquanto
o repositório for público, `dados/portal/` está aberto no GitHub e nenhuma
proteção na Vercel adianta.

**2 · Criar o projeto na Vercel** apontando para este repositório. O
`vercel.json` já traz `buildCommand`, `outputDirectory` e os cabeçalhos.

**3 · As duas variáveis de ambiente** (Settings → Environment Variables),
em Production e Preview:

| variável | o que é |
|---|---|
| `CODIGO_DE_ACESSO` | o que o cliente digita. Longo — frase com 4 palavras é melhor que 8 caracteres |
| `SEGREDO_DA_SESSAO` | string longa e aleatória, **só do servidor**. Trocar derruba todas as sessões |

Para gerar o segredo:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

**Nenhuma das duas entra no repositório.** É a mesma regra do
`_pipeline/.env`, e vale mais ainda aqui.

**4 · Deployment Protection: desligar.** Em Settings → Deployment
Protection, a Vercel vem com `Vercel Authentication` em
`all_except_custom_domains` — **protege o preview e deixa o domínio próprio
aberto**. Quem protege aqui é o middleware, em todos os endereços. Deixar
as duas ligadas faz o time pedir login duas vezes.

**5 · Conferir**, e conferir a coisa certa:

```bash
curl -sI https://<dominio>/dados/portal/clinicas_indice.json | head -1
```

Tem de responder **302** para `/entrar`. Se responder 200, a porta não está
fechando e o resto não importa.

## O que isto NÃO resolve

- **Quem entrou pode baixar todos os payloads.** É inerente a portal
  estático. O controle é saber quem entrou e poder cortar, não impedir a
  cópia.
- **Código único quer dizer que "quem" é o grupo.** Não dá para saber qual
  pessoa abriu, e quando alguém sai da empresa a troca é para todos. Para
  identidade por pessoa, o passo seguinte é **Cloudflare Access** (grátis
  até 50 pessoas, entra com código por e-mail, registra quem abriu o quê) na
  frente da Vercel — exige o DNS do domínio na Cloudflare.
- **O freio de tentativas é por instância.** Segura digitação insistente e
  script preguiçoso; não segura ataque distribuído. Contra isso vale o
  código ser longo.

## Quando virar rotina semanal

O ciclo de coleta roda deste lado e faz `git push`; a Vercel republica
sozinha. As chaves de coleta (`GOOGLE_API_KEY`, `APIFY_TOKEN*`) **não** vão
para a Vercel — elas só existem em `_pipeline/.env` e, quando houver robô,
em GitHub Secrets. A Vercel só precisa das duas variáveis da porta.
