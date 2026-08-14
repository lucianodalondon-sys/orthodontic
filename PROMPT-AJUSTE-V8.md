# Ajuste V8 — três correções pequenas no casco do portal 7

> ## Como devolver o portal — vale para todas as rodadas
>
> No zip de volta vai **só o casco**: `index.html`, `assets/` e nada mais.
>
> **Não inclua a pasta `uploads/`.** Ela é o histórico de arquivos que
> subiram para o projeto — numa entrega anterior eram 73 MB, com imagens
> antigas e até outro projeto dentro, num portal que tem 650 KB. O zip
> passou de 40 MB e não coube no chat.
>
> **Não devolva `dados/portal/`.** O payload sai do nosso build e vai
> sempre no zip de ida; devolver a cópia só cria uma versão para
> divergir da outra.
>
> O que precisamos de volta é exatamente isto:
>
>     portal-casco/
>       index.html
>       assets/  (portal.js, portal.css, fontes, logos)
>
> Foi assim que veio o portal 7, e funcionou: 680 KB.

O portal 7 chegou certo. Sete telas, nenhum erro de página, nenhuma
requisição quebrada, e o zip veio no formato acima. **Não é para refazer
nada.** São três correções pontuais, todas de uma linha ou duas.

Os defeitos que estavam nos DADOS já foram consertados deste lado e vêm no
`dados/portal/` deste zip. Estes três são do casco.

---

## 1 · O rótulo "estudos nesta praça" não conjuga

Na tela **As praças estudadas**, seis dos dezessete cartões dizem:

    1
    estudos nesta praça

O casco monta isso com o número de um lado e o rótulo fixo do outro:

```js
'<div class="met"><div>' + br(p.estudos) + "<i>estudos nesta praça</i></div></div>"
```

**O payload já traz a frase pronta e conjugada**, no mesmo objeto:

```json
{ "rotulo": "MG · Contagem", "estudos": 1,
  "frase_estudos": "1 clínica estudada nesta praça" }
```

```json
{ "rotulo": "RS · Caxias do Sul", "estudos": 3,
  "frase_estudos": "3 clínicas estudadas nesta praça" }
```

**O conserto:** usar `p.frase_estudos` no lugar do par número + rótulo fixo.
O número grande pode continuar sendo `p.estudos`; o texto embaixo é
`p.frase_estudos` sem o número, ou a frase inteira — o que ficar melhor no
cartão. O que não pode é o casco escolher singular ou plural.

Isto vale como **regra geral**, não só aqui: sempre que o payload tiver um
campo `frase_*` ao lado de um número, é a frase que vai na tela. Quem
conjuga é o build.

---

## 2 · O selo do menu da home conta outra coisa

No menu lateral, cada item tem um número à direita:

| item | número | o que ele é |
|---|---|---|
| Clínicas | 45 | unidades acompanhadas |
| Praças | 17 | praças estudadas |
| Radar de cidades | 6 | cidades estudadas |
| Brand Watch | 373 | unidades na lista oficial |
| **Inteligência da rede** | **13** | **lojas em risco** ← |

Os quatro primeiros respondem "quantas coisas tem aqui dentro". O quinto
não: ele lê `fila.em_risco`. A pessoa aprende o padrão nos quatro primeiros
e lê o quinto errado — e a home tem **12 cartões**, não 13.

**O conserto:** trocar o selo da home para o total de cartões, que vem
pronto no payload:

```json
// dados/portal/inteligencia_da_rede.json
{ "blocos_total": 5, "itens_total": 12 }
```

Ou seja, `contaDaSecao("inicio")` devolve `itens_total` de
`inteligencia_da_rede` em vez de `fila.em_risco`.

As 13 lojas em risco continuam importantes — elas já aparecem dentro da
tela, no bloco "qual unidade não pode esperar?". O que não funciona é o
número morar no slot que significa outra coisa.

---

## 3 · Falta favicon

A aba do navegador fica com o ícone genérico, e o console registra um 404
de `/favicon.ico` em todo carregamento. É o único erro que sobra no portal.

**O conserto:** incluir `assets/favicon.png` (ou `.ico`) e a linha no
`<head>`:

```html
<link rel="icon" href="assets/favicon.png">
```

O símbolo da marca que já está no `logo-horizontal.png` serve — só o
símbolo, sem o texto, recortado quadrado.

---

## O que NÃO mudar

- **A estrutura das sete seções.** Está certa.
- **A grade de clínicas.** Resolveu o problema que motivou o V7: 373
  unidades em cartões filtrados, com "ver todas as N" e o total pronto.
- **A tela "O que a rede descobriu, e com quanta força".** É a melhor da
  entrega. Os quatro níveis, o placar à esquerda e o motivo à direita
  funcionam exatamente como deviam.
- **O tamanho do zip.** 680 KB é o alvo. Continue devolvendo assim.

## Uma coisa que mudou nos dados e você vai ver na tela

No bloco "Derrubado pelo dado", o selo do placar agora vem **vazio** nos
itens derrubados, de propósito: um "4/4" verde dentro do bloco vermelho lia
como evidência a favor, e aquele placar era de julho — é justamente o que a
medição de agosto desmentiu. A história inteira está no motivo, ao lado.

Se o casco desenha um traço ou espaço quando `placar` é `null`, está
correto — é assim que já se comporta na tela de hipóteses.
