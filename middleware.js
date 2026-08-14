/**
 * middleware.js — a porta do portal.
 *
 * POR QUE ISTO EXISTE, E POR QUE NÃO PODE SER NO NAVEGADOR
 * -------------------------------------------------------
 * O portal é estático: `index.html` + `assets/` + `dados/portal/*.json`
 * buscados por fetch. Login conferido no navegador seria enfeite — o
 * segredo estaria dentro do arquivo que qualquer um baixa, e mesmo passando
 * por ele bastaria pedir `/dados/portal/clinicas_indice.json` na barra do
 * endereço para levar a inteligência da rede inteira.
 *
 * Este middleware roda no servidor da Vercel ANTES de qualquer arquivo ser
 * entregue. Sem cookie de sessão válido, nada sai: nem o HTML, nem o JS,
 * nem um único JSON. É essa a diferença entre uma tela de login e uma porta.
 *
 * O QUE ELE NÃO RESOLVE, E ISSO PRECISA ESTAR ESCRITO
 * ---------------------------------------------------
 * Quem entrou pode baixar todos os payloads — é inerente a portal estático.
 * O controle aqui é saber QUEM entrou e poder cortar o acesso, não impedir
 * a cópia. Como a sessão carrega o e-mail, "quem" é a pessoa, não o grupo:
 * tirar alguém é tirar o e-mail de `EMAILS_AUTORIZADOS`.
 *
 * NENHUM SEGREDO MORA AQUI. `SEGREDO_DA_SESSAO` e `EMAILS_AUTORIZADOS` são
 * variáveis de ambiente da Vercel — mesma regra do `_pipeline/.env`, e ela
 * vale mais ainda num arquivo que vai para o servidor.
 */
import { abreCookie } from "./api/_porta.js";

export const config = {
  /* Tudo é protegido, menos o que a própria tela de login precisa para
     desenhar e os dois endpoints da porta.
     ⚠ A primeira versão liberava `assets/` INTEIRA, e com isso
     `/assets/portal.js` — 176 KB com a lógica do casco e o nome de todos
     os payloads — saía sem login. A tela de login usa só as fontes e os
     dois logos (o CSS dela é embutido), então é só isso que passa. */
  matcher: [
    "/((?!api/entrar|api/pedir-codigo|entrar|assets/fonts/|assets/logo-|favicon).*)",
  ],
};

export default async function middleware(req) {
  const segredo = process.env.SEGREDO_DA_SESSAO;

  /* SEM CONFIGURAÇÃO, A PORTA FECHA — nunca abre.
     Um middleware que "deixa passar quando não está configurado" publica o
     portal inteiro no primeiro deploy em que alguém esquecer a variável, e
     ninguém percebe, porque o site continua funcionando. Falhar fechado é
     barulhento, e barulho aqui é a única coisa que salva. */
  if (!segredo || !process.env.EMAILS_AUTORIZADOS) {
    return new Response(
      "Portal sem SEGREDO_DA_SESSAO ou EMAILS_AUTORIZADOS configurados nas " +
      "variáveis de ambiente da Vercel. A porta fica fechada até isso ser " +
      "feito — ver DEPLOY.md.",
      { status: 503, headers: { "content-type": "text/plain; charset=utf-8" } }
    );
  }

  const email = await abreCookie(
    req.cookies.get("od_sessao")?.value, segredo, "sessao"
  );
  if (email) return;

  const url = new URL(req.url);
  const destino = new URL("/entrar", url.origin);
  /* volta para onde a pessoa queria ir depois de entrar — sem isto, um
     link direto para a página de uma clínica sempre cai na home */
  destino.searchParams.set("de", url.pathname + url.search);
  return Response.redirect(destino, 302);
}
