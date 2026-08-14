/**
 * api/entrar.js — confere o código digitado e abre a sessão.
 *
 * O código não está guardado em lugar nenhum. O que existe é o cookie de
 * desafio, que traz o e-mail, a validade e a ASSINATURA do código. Aqui se
 * recalcula a assinatura com o que a pessoa digitou: se bate, era o código.
 *
 * Só então nasce o cookie de sessão, que é o que o middleware confere em
 * toda requisição — e ele carrega o e-mail, para o dia em que a
 * franqueadora perguntar quem abriu o portal.
 */
import {
  abreCookie, assina, fazCookie, igualEmTempoConstante, ipDe,
  passouDoLimite, paraB64, autorizados,
} from "./_porta.js";

export const config = { runtime: "edge" };

const DESAFIO = "od_desafio";
const SESSAO = "od_sessao";
const DIAS = 7;

function json(obj, status, extra = {}) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", ...extra },
  });
}

const limpaDesafio =
  `${DESAFIO}=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0`;

export default async function handler(req) {
  if (req.method !== "POST") return json({ erro: "método" }, 405);

  const segredo = process.env.SEGREDO_DA_SESSAO;
  if (!segredo) return json({ erro: "portal não configurado" }, 503);

  if (passouDoLimite(`entrar:${ipDe(req)}`, 10, 300_000)) {
    return json({ erro: "muitas tentativas" }, 429);
  }

  let digitado = "";
  try {
    digitado = String((await req.json())?.codigo || "").replace(/\D/g, "");
  } catch {
    return json({ erro: "pedido inválido" }, 400);
  }

  const cru = req.headers.get("cookie") || "";
  const achado = cru.split(/;\s*/).find((c) => c.startsWith(`${DESAFIO}=`));
  if (!achado) return json({ erro: "expirou" }, 401, { "Set-Cookie": limpaDesafio });

  const [valor, trava] = decodeURIComponent(achado.slice(DESAFIO.length + 1)).split("~");
  const email = await abreCookie(valor, segredo, "desafio");
  if (!email || !trava) {
    return json({ erro: "expirou" }, 401, { "Set-Cookie": limpaDesafio });
  }

  /* A LISTA SE CONFERE DE NOVO AQUI, e não é redundância inútil: entre
     pedir o código e digitá-lo a pessoa pode ter sido removida da lista, e
     um desafio de dez minutos não pode sobreviver à revogação. */
  if (!autorizados().includes(email)) {
    return json({ erro: "sem_acesso" }, 403, { "Set-Cookie": limpaDesafio });
  }

  const expira = valor.split(".")[0];
  const esperada = await assina(
    `codigo|${expira}|${paraB64(email)}|${digitado}`, segredo
  );
  if (!igualEmTempoConstante(trava, esperada)) {
    await new Promise((r) => setTimeout(r, 400));
    return json({ erro: "codigo_errado" }, 401);
  }

  const sessao = await fazCookie(email, segredo, "sessao", DIAS * 86_400_000);

  /* DOIS COOKIES PEDEM DUAS LINHAS DE CABEÇALHO, e `append` é o único
     jeito. Juntar os dois numa string separada por vírgula parece
     funcionar — a vírgula é o separador na especificação antiga — mas
     `Expires` também tem vírgula dentro, e navegador nenhum garante o
     desempate. O sintoma seria a sessão abrir e o desafio não queimar,
     deixando o mesmo código valer de novo. */
  const cabecalhos = new Headers({
    "content-type": "application/json; charset=utf-8",
  });
  cabecalhos.append(
    "Set-Cookie",
    `${SESSAO}=${sessao.valor}; Path=/; HttpOnly; Secure; ` +
    `SameSite=Lax; Max-Age=${DIAS * 86_400}`
  );
  cabecalhos.append("Set-Cookie", limpaDesafio);

  return new Response(JSON.stringify({ ok: true }), {
    status: 200, headers: cabecalhos,
  });
}
