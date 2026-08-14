/**
 * api/pedir-codigo.js — manda o código de seis dígitos para o e-mail.
 *
 * SEM BANCO DE DADOS, E ISSO É DE PROPÓSITO.
 * O código não fica guardado em lugar nenhum: sai daqui dentro de um cookie
 * ASSINADO, onde vai só o HMAC dele — nunca o código em si. Quem recebe o
 * cookie não consegue ler o código a partir dele, e o servidor confere
 * depois recalculando a assinatura com o que a pessoa digitar.
 *
 * Efeito colateral bom: o código só funciona NO MESMO NAVEGADOR que pediu.
 * Código repassado por WhatsApp não abre nada do outro lado.
 */
import {
  autorizados, fazCookie, assina, ipDe, passouDoLimite, paraB64,
} from "./_porta.js";

export const config = { runtime: "edge" };

const DESAFIO = "od_desafio";
const VALE_MINUTOS = 10;

function json(obj, status) {
  return new Response(JSON.stringify(obj), {
    status, headers: { "content-type": "application/json; charset=utf-8" },
  });
}

async function mandaEmail(para, codigo) {
  const chave = process.env.RESEND_API_KEY;
  const de = process.env.REMETENTE || "OrthoDontic Intelligence <onboarding@resend.dev>";
  const r = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${chave}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      from: de,
      to: [para],
      subject: `${codigo} — seu código do portal OrthoDontic`,
      text:
        `Seu código de acesso é ${codigo}.\n\n` +
        `Ele vale por ${VALE_MINUTOS} minutos e só funciona no navegador ` +
        `onde você pediu.\n\n` +
        `Se não foi você que pediu, ignore este e-mail — sem o código ` +
        `ninguém entra.\n\n` +
        `Portal de Inteligência da rede OrthoDontic — uso restrito.`,
    }),
  });
  return r.ok;
}

export default async function handler(req) {
  if (req.method !== "POST") return json({ erro: "método" }, 405);

  const segredo = process.env.SEGREDO_DA_SESSAO;
  const lista = autorizados();

  /* FALHA FECHADO. Sem segredo, sem lista ou sem provedor de e-mail, a
     porta não abre — e diz por quê, para o conserto ser óbvio. Um endpoint
     que "deixa passar quando não está configurado" é como o portal vaza. */
  if (!segredo || !lista.length || !process.env.RESEND_API_KEY) {
    return json({ erro: "portal não configurado" }, 503);
  }

  let email = "";
  try {
    email = String((await req.json())?.email || "").trim().toLowerCase();
  } catch {
    return json({ erro: "pedido inválido" }, 400);
  }
  if (!email.includes("@")) return json({ erro: "e-mail inválido" }, 400);

  if (passouDoLimite(`ip:${ipDe(req)}`, 10, 600_000) ||
      passouDoLimite(`em:${email}`, 4, 600_000)) {
    return json({ erro: "muitas tentativas" }, 429);
  }

  /* DIZER QUE O E-MAIL NÃO ESTÁ NA LISTA É ESCOLHA, E ELA TEM MOTIVO.
     O manual mandaria responder igual nos dois casos, para ninguém
     descobrir quem tem acesso. Aqui o custo dessa descoberta é baixo (é
     uma lista de gente da franqueadora) e o custo do contrário é alto: um
     diretor olhando "confira seu e-mail" para uma mensagem que nunca vai
     chegar. Ferramenta interna, escolhe-se o erro que não trava a pessoa. */
  if (!lista.includes(email)) {
    return json({ erro: "sem_acesso" }, 403);
  }

  /* seis dígitos vindos do gerador criptográfico, sem viés de módulo:
     sorteia de novo o que cai fora da faixa redonda */
  let n;
  const buf = new Uint32Array(1);
  do { crypto.getRandomValues(buf); } while (buf[0] >= 4_294_000_000);
  n = buf[0] % 1_000_000;
  const codigo = String(n).padStart(6, "0");

  if (!(await mandaEmail(email, codigo))) {
    return json({ erro: "envio_falhou" }, 502);
  }

  const { valor, expira } = await fazCookie(
    email, segredo, "desafio", VALE_MINUTOS * 60_000
  );
  /* o cookie carrega o e-mail e a validade; o código entra só como
     assinatura, e é ela que a conferência vai reproduzir */
  const trava = await assina(
    `codigo|${expira}|${paraB64(email)}|${codigo}`, segredo
  );

  return new Response(JSON.stringify({ ok: true }), {
    status: 200,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "Set-Cookie":
        `${DESAFIO}=${valor}~${trava}; Path=/; HttpOnly; Secure; ` +
        `SameSite=Lax; Max-Age=${VALE_MINUTOS * 60}`,
    },
  });
}
