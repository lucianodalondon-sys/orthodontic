# Prompt para terminar a publicação do portal

Cole o bloco abaixo numa janela do Claude Code — no seu PC (dentro da pasta
do repositório) ou aqui. Ele é autossuficiente: não depende de nada que
tenha sido conversado antes.

---

```
Estou publicando o Portal de Inteligência da OrthoDontic. O código já está
pronto e no ar; falta configurar o acesso. Faça o que der para fazer, e me
diga exatamente o que sobrou para mim.

CONTEXTO (tudo já feito, não refazer)
- Repositório: lucianodalondon-sys/orthodontic
- Branch de produção: claude/orthodontic-center-franchise-research-lte9l3
- Projeto na Vercel: orthodontic-portal (time London Creative)
- URL: https://orthodontic-portal-london-creative.vercel.app
- O portal é estático (casco/ + dados/portal/), montado no build por
  scripts/publica_site.py. Quem protege é middleware.js, no servidor:
  sem cookie de sessão assinado, NADA sai — nem HTML, nem JS, nem um
  único JSON.
- A entrada é em duas etapas: e-mail contra lista fechada, depois código
  de 6 dígitos enviado por e-mail (api/pedir-codigo.js e api/entrar.js).
- Hoje o portal responde 503 em tudo, de propósito: o middleware FALHA
  FECHADO enquanto as variáveis de ambiente não existirem.

REGRAS QUE NÃO SE NEGOCIAM
1. NÃO tocar em nenhum outro projeto da Vercel. Este time tem projetos de
   outros clientes (portal-sintonia, fishking-site, aura-360-site e
   outros). Só `orthodontic-portal`. Se o CLI perguntar se é para ligar a
   um projeto existente, a resposta é orthodontic-portal — nunca outro.
2. NENHUM segredo entra no repositório. Nem em arquivo, nem em commit,
   nem em comentário. As variáveis vivem só na Vercel.
3. NÃO editar casco/ — é entrega do Design, só se substitui inteira.
4. NÃO editar dados/portal/ à mão — sai de scripts/build_portal.py.

O QUE FAZER, NESTA ORDEM

Passo 1 — Tornar o repositório privado.
  Hoje ele é público, e isso é o furo maior: dados/portal/ inteiro está
  aberto no GitHub, então a porta que protege o site não protege a cópia.
  Tente:
      gh repo edit lucianodalondon-sys/orthodontic --visibility private \
        --accept-visibility-change-consequences
  Se o gh não estiver instalado ou autenticado, me diga e eu faço pelo
  site (Settings > General > Danger Zone > Change visibility).
  Confirme depois com:  gh repo view lucianodalondon-sys/orthodontic --json visibility

Passo 2 — Gerar o segredo da sessão.
      python3 -c "import secrets; print(secrets.token_urlsafe(48))"
  Guarde o valor para o passo 4. Não escreva ele em arquivo nenhum.

Passo 3 — Me perguntar duas coisas, e esperar a resposta:
  (a) quais e-mails podem entrar no portal (lista separada por vírgula)
  (b) a RESEND_API_KEY
  Sobre (b): é conta gratuita em resend.com (3.000 e-mails/mês). Se eu
  ainda não tiver, me explique em 3 linhas como criar. Importante: sem
  verificar um domínio no Resend, o remetente fica onboarding@resend.dev
  e SÓ entrega para o e-mail dono da conta — serve para testar, não serve
  para a diretoria.

Passo 4 — Configurar as variáveis na Vercel, em Production e Preview:
      SEGREDO_DA_SESSAO    (o valor do passo 2)
      EMAILS_AUTORIZADOS   (a lista do passo 3a)
      RESEND_API_KEY       (a chave do passo 3b)
      REMETENTE            (opcional, depois de verificar o domínio:
                            "OrthoDontic Intelligence <portal@dominio.com.br>")
  Use o Vercel CLI (vercel login, vercel link ao projeto orthodontic-portal,
  vercel env add). Se o CLI não estiver disponível, me dê os valores
  formatados para eu colar em Settings > Environment Variables.
  Depois de configurar, force um novo deploy — variável nova só vale a
  partir do próximo build.

Passo 5 — Conferir. Este é o teste que decide, e não é abrir a home:
      curl -sI https://orthodontic-portal-london-creative.vercel.app/dados/portal/clinicas_indice.json
  TEM de responder 302 (para /entrar).
   . se responder 503, as variáveis não chegaram ou o deploy não refez
   . se responder 200, A PORTA NÃO ESTÁ FECHANDO — pare tudo e me avise
  Confira também que /entrar responde 200 e que /assets/portal.js responde
  302 (a lógica do casco não pode sair sem login).

Passo 6 — Testar a entrada de verdade, com um e-mail da lista: pedir o
  código, receber, entrar, e confirmar que o portal abre. Se algo falhar,
  leia os logs em tempo real (vercel logs) antes de mexer no código.

Passo 7 — Em Settings > Deployment Protection, conferir que a proteção
  nativa da Vercel está DESLIGADA. Ela vem em "all_except_custom_domains",
  que protege só o preview e deixa o domínio próprio aberto — e quem
  protege aqui é o middleware, em todos os endereços. Com as duas ligadas,
  o time pede login duas vezes.

REFERÊNCIA
  DEPLOY.md tem o passo a passo completo e a lista honesta do que esta
  porta NÃO resolve.
  node testes/porta.test.mjs confere a criptografia dos cookies (11
  verificações). Rode antes e depois de qualquer mexida em api/ ou
  middleware.js.

Comece pelo passo 1 e vá me contando o que fez.
```
