/**
 * middleware.js — a porta do portal.
 *
 * POR QUE ISTO EXISTE, E POR QUE NÃO PODE SER NO NAVEGADOR
 * -------------------------------------------------------
 * O portal é estático: `index.html` + `assets/` + `dados/portal/*.json`
 * buscados por fetch. Login conferido no navegador seria enfeite — a senha
 * estaria dentro do arquivo que qualquer um baixa, e mesmo passando por ela
 * bastaria pedir `/dados/portal/clinicas_indice.json` na barra do endereço
 * para levar a inteligência inteira.
 *
 * O middleware roda no servidor da Vercel ANTES de qualquer arquivo ser
 * entregue. Sem cookie válido, nada sai: nem o HTML, nem o JS, nem um único
 * JSON. É essa a diferença entre uma tela de login e uma porta.
 *
 * O QUE ELE NÃO RESOLVE, E ISSO PRECISA ESTAR ESCRITO
 * ---------------------------------------------------
 * Quem entrou pode baixar todos os payloads — é inerente a portal estático.
 * O controle aqui é saber QUEM entrou e poder cortar o acesso, não impedir
 * a cópia. E, com código único, "quem" é o grupo inteiro: para saber a
 * pessoa, o passo seguinte é identidade por e-mail (Cloudflare Access ou
 * código enviado por e-mail).
 *
 * O SEGREDO NÃO MORA AQUI. `CODIGO_DE_ACESSO` e `SEGREDO_DA_SESSAO` são
 * variáveis de ambiente da Vercel. Nenhuma chave entra neste repositório —
 * é a mesma regra do `_pipeline/.env`, e ela vale mais ainda num arquivo
 * que vai para o servidor.
 */
export const config = {
  /* Tudo é protegido, menos o necessário para a própria tela de login
     desenhar (fonte, logo) e o endpoint que confere o código. Sem excluir
     `/assets`, a tela de login apareceria sem marca e sem tipografia. */
  matcher: ["/((?!api/entrar|entrar|assets/|favicon).*)"],
};

const COOKIE = "od_sessao";

/** Compara sem vazar o tempo de resposta — duas strings diferentes devem
 *  demorar o mesmo tanto, senão o próprio relógio entrega o código. */
function igualEmTempoConstante(a, b) {
  const A = new TextEncoder().encode(a);
  const B = new TextEncoder().encode(b);
  if (A.length !== B.length) return false;
  let dif = 0;
  for (let i = 0; i < A.length; i++) dif |= A[i] ^ B[i];
  return dif === 0;
}

/** O cookie é `expira.assinatura`. A assinatura é HMAC-SHA256 do prazo com
 *  o segredo do servidor: sem ele, ninguém forja um cookie válido, e trocar
 *  o segredo derruba todas as sessões de uma vez. */
async function assinaturaValida(valor, segredo) {
  const p = String(valor || "").split(".");
  if (p.length !== 2) return false;
  const [expira, assinatura] = p;
  if (!/^\d+$/.test(expira) || Number(expira) < Date.now()) return false;

  const chave = await crypto.subtle.importKey(
    "raw", new TextEncoder().encode(segredo),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]
  );
  const bruto = await crypto.subtle.sign(
    "HMAC", chave, new TextEncoder().encode(expira)
  );
  const esperada = [...new Uint8Array(bruto)]
    .map((b) => b.toString(16).padStart(2, "0")).join("");
  return igualEmTempoConstante(assinatura, esperada);
}

export default async function middleware(req) {
  const segredo = process.env.SEGREDO_DA_SESSAO;

  /* SEM SEGREDO CONFIGURADO, A PORTA FECHA — nunca abre.
     Um middleware que "deixa passar quando não está configurado" publica o
     portal inteiro no primeiro deploy em que alguém esquecer a variável, e
     ninguém percebe, porque o site funciona. Falhar fechado é barulhento e
     é o certo. */
  if (!segredo || !process.env.CODIGO_DE_ACESSO) {
    return new Response(
      "Portal sem CODIGO_DE_ACESSO ou SEGREDO_DA_SESSAO configurados nas " +
      "variáveis de ambiente da Vercel. A porta fecha até isso ser feito.",
      { status: 503, headers: { "content-type": "text/plain; charset=utf-8" } }
    );
  }

  const cookie = req.cookies.get(COOKIE)?.value;
  if (await assinaturaValida(cookie, segredo)) return;

  const url = new URL(req.url);
  const destino = new URL("/entrar", url.origin);
  /* volta para onde a pessoa queria ir depois de entrar — sem isto, um
     link direto para a página de uma clínica sempre cai na home */
  destino.searchParams.set("de", url.pathname + url.search);
  return Response.redirect(destino, 302);
}
