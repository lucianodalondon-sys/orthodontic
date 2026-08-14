/**
 * _porta.js — as peças que a porta usa nos dois lados.
 *
 * O middleware e os endpoints precisam assinar e conferir a mesma coisa.
 * Duas cópias da mesma função HMAC divergem no dia em que alguém arruma um
 * lado só — e o sintoma seria "ninguém mais consegue entrar", em produção.
 */

/** Compara sem vazar o tempo de resposta: duas strings diferentes têm de
 *  demorar o mesmo tanto, senão o relógio entrega o segredo. */
export function igualEmTempoConstante(a, b) {
  const A = new TextEncoder().encode(String(a ?? ""));
  const B = new TextEncoder().encode(String(b ?? ""));
  if (A.length !== B.length) return false;
  let dif = 0;
  for (let i = 0; i < A.length; i++) dif |= A[i] ^ B[i];
  return dif === 0;
}

export async function assina(texto, segredo) {
  const chave = await crypto.subtle.importKey(
    "raw", new TextEncoder().encode(segredo),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]
  );
  const bruto = await crypto.subtle.sign(
    "HMAC", chave, new TextEncoder().encode(texto)
  );
  return [...new Uint8Array(bruto)]
    .map((b) => b.toString(16).padStart(2, "0")).join("");
}

/* O e-mail entra no cookie em base64url porque cookie não aceita qualquer
   caractere, e porque assim o valor não muda de forma entre navegadores. */
export const paraB64 = (s) =>
  btoa(String(s)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
export const deB64 = (s) => {
  try {
    return atob(String(s).replace(/-/g, "+").replace(/_/g, "/"));
  } catch { return ""; }
};

/**
 * Confere um cookie no formato `expira.emailB64.assinatura`.
 * Devolve o e-mail quando vale, `null` quando não.
 */
export async function abreCookie(valor, segredo, sal) {
  const p = String(valor || "").split(".");
  if (p.length !== 3) return null;
  const [expira, emailB64, assinatura] = p;
  if (!/^\d+$/.test(expira) || Number(expira) < Date.now()) return null;
  const esperada = await assina(`${sal}|${expira}|${emailB64}`, segredo);
  if (!igualEmTempoConstante(assinatura, esperada)) return null;
  return deB64(emailB64) || null;
}

export async function fazCookie(email, segredo, sal, duracaoMs) {
  const expira = Date.now() + duracaoMs;
  const emailB64 = paraB64(email);
  const assinatura = await assina(`${sal}|${expira}|${emailB64}`, segredo);
  return { valor: `${expira}.${emailB64}.${assinatura}`, expira };
}

/**
 * A lista de quem pode entrar, da variável de ambiente.
 *
 * É uma lista em variável, não um banco: revogar alguém é editar a
 * variável e reimplantar, e isso é bom o bastante para dezenas de pessoas.
 * Se um dia forem centenas, aí sim vale um provedor de identidade.
 */
export function autorizados() {
  return String(process.env.EMAILS_AUTORIZADOS || "")
    .split(/[,\s;]+/)
    .map((e) => e.trim().toLowerCase())
    .filter((e) => e.includes("@"));
}

export function ipDe(req) {
  return req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || "sem-ip";
}

/* Freio de tentativa na memória da instância.
 *
 * O limite está escrito para ninguém confundir com proteção séria: a Vercel
 * roda várias instâncias, cada uma com o próprio contador, e elas reciclam.
 * Segura digitação insistente e script preguiçoso; não segura ataque
 * distribuído. Contra isso valem o código de 6 dígitos com validade curta
 * e a lista fechada de e-mails. */
const balde = new Map();
export function passouDoLimite(chave, teto, janelaMs) {
  const agora = Date.now();
  const t = (balde.get(chave) || []).filter((x) => agora - x < janelaMs);
  t.push(agora);
  balde.set(chave, t);
  if (balde.size > 5000) balde.clear();
  return t.length > teto;
}
