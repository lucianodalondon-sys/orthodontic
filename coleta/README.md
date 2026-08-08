# A coleta — como rodar

```bash
python3 coleta/ciclo.py            # o que está vencido
python3 coleta/ciclo.py --rodar    # roda o vencido e reconstrói o payload
python3 coleta/ciclo.py --plano    # o catálogo inteiro, com o que falta construir
```

O `ciclo.py` é o relógio: sabe a frequência de cada fonte, quando cada uma
rodou por último, e roda **só o que venceu**. Recoletar o que não venceu é
gastar crédito para gravar a mesma linha.

Estado em `dados/serie/_ciclo.json` · log em `dados/serie/_ciclo.log`.

---

## O que já roda

| Coletor | Freq. | Custo | O que entrega |
|---|---|---|---|
| `google_reviews` | semanal | ~US$ 0,04/praça | nota, volume, **velocity**, taxa de resposta, distribuição de estrelas |
| `meta_ads` | semanal | ~US$ 0,10/praça | quem anuncia, com que texto, **há quantos dias no ar** |
| `imprensa_rss` | semanal | grátis | a joia enterrada, o que a cidade noticia |

**3 de 19.** O resto está catalogado em [`FONTES.md`](FONTES.md) com a pergunta
que cada um responde, e listado em `ciclo.py --plano` com status.

---

## Credenciais

Ficam em `_pipeline/.env`, que está no `.gitignore`. **Nunca versionar.**

```
APIFY_TOKEN=...
GOOGLE_API_KEY=...
```

Duas armadilhas que já custaram tempo:

1. **O `.env` do Dropbox está com quebra de linha do Windows.** Cada token
   carrega um `\r` no fim e toda chamada falha com erro de autenticação que
   parece de credencial. `sed -i 's/\r$//' .env` resolve.
2. **O cliente Python da Apify não atravessa o proxy** desta máquina
   (`ConnectionReset` no transporte). Por isso os coletores daqui falam com a
   **API REST por urllib**, não com o `apify-client`. Se for portar um coletor
   do pipeline legado, troque o cliente.

---

## O contrato de saída

Todo coletor grava em dois níveis — ver [`../dados/CONTRATO.md`](../dados/CONTRATO.md):

```
dados/bruto/<praca>/<fonte>/<snapshot>/   imutável, o que veio da fonte
dados/serie/<fonte>.jsonl                 append-only, com snapshot_date
```

E toda linha carrega `first_seen_snapshot` e `last_seen_snapshot`. **É daí que
saem duas métricas de graça:**

- **velocity** — reviews novos por mês, por clínica, sem a fonte informar nada
- **dias no ar** — `last_seen − first_seen` num anúncio. Criativo que sobrevive
  dois meses está performando. É o melhor proxy grátis de performance que existe.

**Nada é sobrescrito.** Se a coleta de agosto contradiz a de julho, as duas
ficam. A contradição é dado.

---

## Quando a coleta termina

```bash
python3 scripts/build_portal.py          # monta dados/portal/*.json
python3 scripts/injetar_casco.py casco.html   # embute e gera o publicável
git add -A && git commit && git push      # a série ganha mais um ponto
```

O `--rodar` do ciclo já dispara o `build_portal.py` no fim.

---

## Ordem de construção do que falta

Em [`FONTES.md`](FONTES.md), resumida:

**Semana 1 — nada depende de ninguém:** Reclame Aqui completo (o de maior
valor — mede operação por unidade), Google Ads Transparency (toda a análise de
mídia era só Meta), teste de WhatsApp.

**Semana 2 — os alertas:** diff do mapa, CNPJ novo, vagas.

**Semana 3 — a voz que falta:** Doctoralia, grupos públicos de Facebook,
perguntas da ficha do Google.

**Quando o acesso vier:** GBP Insights (4 fichas) e o CSV do Conecta.

---

## Sobre a chave do Google

Válida, mas o projeto tem quase tudo desativado. Hoje só a **YouTube Data v3**
responde. Ativar a **Places API (New)** resolveria os `place_id` reais da tabela
de identidade e daria nota e volume por via oficial — mais estável que raspagem.
