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

## ⚠ Projeto separado, sempre

Este portal é de um cliente. **Nada aqui se mistura com outro projeto do
time na Vercel** — projeto próprio, domínio próprio, variáveis próprias.

Este repositório não tem `.vercel/` justamente para não carregar vínculo
com projeto nenhum. Ao rodar `vercel` pela primeira vez, ele pergunta se é
para ligar a um projeto existente: **a resposta é criar um novo.** Ligar ao
projeto errado publica um cliente dentro do endereço do outro, e o
`.vercel/project.json` que ele grava depois faz todo deploy seguinte repetir
o erro calado.

## A porta

Login conferido no navegador não protege nada: o segredo ficaria dentro do
arquivo que qualquer um baixa, e `dados/portal/*.json` continuaria aberto
por URL direta. Por isso a conferência é no servidor:

```
navegador → middleware.js  (roda ANTES de qualquer arquivo sair)
              ├── tem cookie de sessão assinado?  → entrega o portal
              └── não tem                        → /entrar
                                                     │
     1 · e-mail  → api/pedir-codigo.js ────────────────┘
                     confere a lista, sorteia 6 dígitos, manda por e-mail
                     e devolve um cookie de DESAFIO — que leva a
                     assinatura do código, nunca o código

     2 · código → api/entrar.js
                     recalcula a assinatura com o que foi digitado; se
                     bate, abre o cookie de SESSÃO com o e-mail dentro
```

**Não há banco de dados**, e é de propósito: o código não fica guardado em
lugar nenhum. Efeito colateral bom — o código só funciona **no mesmo
navegador que pediu**, então código repassado por WhatsApp não abre nada do
outro lado.

Rodar `node testes/porta.test.mjs` confere a criptografia dos dois cookies:
assinatura adulterada, e-mail trocado, desafio tentando passar por sessão,
prazo vencido. Um erro aí tranca todo mundo para fora, e só apareceria em
produção.

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

**3 · As variáveis de ambiente** (Settings → Environment Variables), em
Production e Preview:

| variável | o que é |
|---|---|
| `SEGREDO_DA_SESSAO` | string longa e aleatória, **só do servidor**. Trocar derruba todas as sessões |
| `EMAILS_AUTORIZADOS` | quem pode entrar, separado por vírgula. **Tirar alguém é tirar daqui** |
| `RESEND_API_KEY` | a chave do provedor que envia o e-mail do código |
| `REMETENTE` | opcional — `OrthoDontic Intelligence <portal@seudominio.com.br>` |

Para gerar o segredo:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

**Nenhuma delas entra no repositório.** É a mesma regra do
`_pipeline/.env`, e vale mais ainda aqui.

Sobre o `RESEND_API_KEY`: é conta no [resend.com](https://resend.com),
gratuita até 3.000 e-mails por mês — muito acima do que um portal de
franqueadora consome. Sem verificar um domínio, o remetente fica
`onboarding@resend.dev` e **só entrega para o e-mail dono da conta**, o que
serve para testar mas não para a diretoria. Para valer, verifique o domínio
da OrthoDontic no Resend e ponha o `REMETENTE` com ele.

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
- **Saber quem entrou não é registrar quem entrou.** A sessão carrega o
  e-mail, mas nada grava um histórico de acessos — não há onde. Para ter
  registro de verdade seria preciso um destino de log, e isso é obra à
  parte.
- **Revogar tem atraso.** Tirar um e-mail de `EMAILS_AUTORIZADOS` impede
  novos acessos na hora, mas a sessão já aberta vale até 7 dias. Para
  derrubar todo mundo agora, troque o `SEGREDO_DA_SESSAO`.
- **O freio de tentativas é por instância.** A Vercel roda várias, cada uma
  com o próprio contador. Segura digitação insistente e script preguiçoso;
  não segura ataque distribuído. Contra isso valem o código de seis dígitos
  com dez minutos de validade e a lista fechada de e-mails.
- **A caixa de e-mail vira a chave.** Quem tiver acesso ao e-mail de alguém
  da lista entra no portal. É o mesmo risco de qualquer "esqueci a senha" —
  vale saber que existe, não vale fingir que não.

## Quando virar rotina semanal

O ciclo de coleta roda deste lado e faz `git push`; a Vercel republica
sozinha. As chaves de coleta (`GOOGLE_API_KEY`, `APIFY_TOKEN*`) **não** vão
para a Vercel — elas só existem em `_pipeline/.env` e, quando houver robô,
em GitHub Secrets. A Vercel só precisa das duas variáveis da porta.
