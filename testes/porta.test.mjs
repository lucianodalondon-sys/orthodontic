/**
 * porta.test.mjs — a porta se testa, porque um erro aqui tranca todo mundo
 * para fora e só aparece em produção.
 *
 *     node testes/porta.test.mjs
 *
 * O que ele cobre é o que quebra calado: assinatura adulterada, e-mail
 * trocado mantendo a assinatura, cookie de desafio tentando passar por
 * cookie de sessão (o "sal" é o que separa os dois), cookie expirado, e a
 * garantia de que o código de seis dígitos NÃO é legível a partir do
 * cookie que o carrega.
 */
import { fazCookie, abreCookie, assina, paraB64, igualEmTempoConstante } from "../api/_porta.js";

const S = "segredo-de-teste-bem-longo-aleatorio-xyz";
let ok = 0, mau = 0;
const t = (nome, cond) => { cond ? ok++ : mau++; console.log(`  ${cond ? "ok  " : "FALHA"} ${nome}`); };

// 1. sessão: ida e volta
const s = await fazCookie("diretoria@orthodontic.com.br", S, "sessao", 60000);
t("sessão válida devolve o e-mail",
  (await abreCookie(s.valor, S, "sessao")) === "diretoria@orthodontic.com.br");

// 2. segredo errado não abre
t("segredo diferente NÃO abre", (await abreCookie(s.valor, "outro", "sessao")) === null);

// 3. sal diferente não abre (cookie de desafio não vira sessão)
t("sal diferente NÃO abre", (await abreCookie(s.valor, S, "desafio")) === null);

// 4. assinatura adulterada
const adulterado = s.valor.slice(0, -1) + (s.valor.slice(-1) === "a" ? "b" : "a");
t("assinatura mexida NÃO abre", (await abreCookie(adulterado, S, "sessao")) === null);

// 5. e-mail trocado mantendo a assinatura
const [exp, , sig] = s.valor.split(".");
t("e-mail trocado NÃO abre",
  (await abreCookie(`${exp}.${paraB64("outro@x.com")}.${sig}`, S, "sessao")) === null);

// 6. expirado
const velho = await fazCookie("a@b.com", S, "sessao", -1000);
t("cookie expirado NÃO abre", (await abreCookie(velho.valor, S, "sessao")) === null);

// 7. o desafio do código: só o código certo reproduz a trava
const d = await fazCookie("a@b.com", S, "desafio", 600000);
const codigo = "409271";
const trava = await assina(`codigo|${d.expira}|${paraB64("a@b.com")}|${codigo}`, S);
const recalc = await assina(`codigo|${d.expira}|${paraB64("a@b.com")}|${codigo}`, S);
t("código certo reproduz a trava", igualEmTempoConstante(trava, recalc));
const errado = await assina(`codigo|${d.expira}|${paraB64("a@b.com")}|409272`, S);
t("código errado NÃO reproduz", !igualEmTempoConstante(trava, errado));

// 8. o código não é legível a partir do cookie
t("o cookie não contém o código", !`${d.valor}~${trava}`.includes(codigo));

// 9. lixo não derruba
t("cookie vazio NÃO abre", (await abreCookie("", S, "sessao")) === null);
t("cookie sem forma NÃO abre", (await abreCookie("a.b", S, "sessao")) === null);

console.log(`\n  ${ok} passaram, ${mau} falharam`);
process.exit(mau ? 1 : 0);
