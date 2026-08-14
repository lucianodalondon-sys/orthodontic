/**
 * api/entrar.js — quem confere o código, e o único lugar que o conhece.
 *
 * O código vive em variável de ambiente da Vercel, nunca no repositório e
 * nunca no que vai para o navegador. A tela de login manda o que foi
 * digitado; a resposta é só "entra" ou "não entra".
 *
 * O cookie é HttpOnly: o JavaScript da página não lê. Isso não é preciosismo
 * — é o que impede que um script de terceiro (ou uma extensão) leve a
 * sessão embora.
 */
export const config = { runtime: "edge" };

const COOKIE = "od_sessao";
const DIAS = 7;

/* Freio de tentativa POR IP, na memória da instância.
 *
 * É de propósito simples, e o limite disso está escrito aqui para ninguém
 * confundir com proteção séria: a Vercel roda várias instâncias, cada uma
 * com o próprio contador, e elas reciclam. Segura a digitação insistente e
 * o script preguiçoso; NÃO segura ataque distribuído. Contra isso, o que
 * vale é o código ser longo — e o passo seguinte, identidade por e-mail. */
const tentativas = new Map();
const JANELA = 60_000;
const TETO = 8;

function passouDoLimite(ip) {
  const agora = Date.now();
  const t = (tentativas.get(ip) || []).filter((x) => agora - x < JANELA);
  t.push(agora);
  tentativas.set(ip, t);
  if (tentativas.size > 5000) tentativas.clear();   // teto de memória
  return t.length > TETO;
}

function igualEmTempoConstante(a, b) {
  const A = new TextEncoder().encode(a);
  const B = new TextEncoder().encode(b);
  if (A.length !== B.length) return false;
  let dif = 0;
  for (let i = 0; i < A.length; i++) dif |= A[i] ^ B[i];
  return dif === 0;
}

export default async function handler(req) {
  if (req.method !== "POST") return new Response("Método não permitido", { status: 405 });

  const codigoCerto = process.env.CODIGO_DE_ACESSO;
  const segredo = process.env.SEGREDO_DA_SESSAO;
  if (!codigoCerto || !segredo) {
    return new Response("Portal não configurado", { status: 503 });
  }

  const ip = req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || "sem-ip";
  if (passouDoLimite(ip)) return new Response("Muitas tentativas", { status: 429 });

  let digitado = "";
  try {
    digitado = String((await req.json())?.codigo || "");
  } catch {
    return new Response("Pedido inválido", { status: 400 });
  }

  if (!igualEmTempoConstante(digitado, codigoCerto)) {
    /* atraso pequeno e fixo: encarece a tentativa em massa sem punir quem
       só errou de digitação */
    await new Promise((r) => setTimeout(r, 400));
    return new Response("Código não confere", { status: 401 });
  }

  const expira = Date.now() + DIAS * 86_400_000;
  const chave = await crypto.subtle.importKey(
    "raw", new TextEncoder().encode(segredo),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]
  );
  const bruto = await crypto.subtle.sign(
    "HMAC", chave, new TextEncoder().encode(String(expira))
  );
  const assinatura = [...new Uint8Array(bruto)]
    .map((b) => b.toString(16).padStart(2, "0")).join("");

  return new Response(null, {
    status: 204,
    headers: {
      "Set-Cookie":
        `${COOKIE}=${expira}.${assinatura}; Path=/; HttpOnly; Secure; ` +
        `SameSite=Lax; Max-Age=${DIAS * 86_400}`,
    },
  });
}
