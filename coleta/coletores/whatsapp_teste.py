#!/usr/bin/env python3
"""
whatsapp_teste.py — quanto tempo a clínica leva para responder.

É a ferida nº 1 dos cinco estudos e a ÚNICA das constantes que nenhuma fonte
pública mede. Riomafra converte 5,9% dos interessados em agendamento contra uma
régua de 40% — quem chega, fecha; quem chama, some. E ninguém sabe quanto tempo
o "some" leva, porque esse número não existe em lugar nenhum.

ISTO NÃO É UM RASPADOR. É um protocolo com registro.

Não automatizamos a mensagem, e é decisão, não limitação:
  · mandar mensagem automática para clínica é gerar lead falso — custa o tempo
    de uma recepcionista de verdade e polui o funil de quem estamos medindo
  · o WhatsApp Business API não serve para isto e raspar o WhatsApp Web viola
    os termos
  · e a pergunta precisa soar como paciente. Uma pessoa faz melhor.

Então a máquina faz o que a máquina faz bem: sorteia a ordem, cronometra, guarda
e calcula. A pessoa manda a mensagem.

COMO USAR

  1. Preparar a rodada (imprime as clínicas, a mensagem e o horário):
        python3 coleta/coletores/whatsapp_teste.py --praca riomafra --preparar

  2. Mandar as mensagens à mão, na ordem sorteada, anotando a hora de envio.

  3. Registrar cada resposta conforme chega:
        python3 coleta/coletores/whatsapp_teste.py --registrar lumiere \\
            --enviado "2026-08-09 14:02" --respondido "2026-08-09 14:19" \\
            --quem humano --pediu-nome --ofereceu-horario

     Sem resposta até o fim do dia seguinte:
        python3 coleta/coletores/whatsapp_teste.py --registrar ortho_mafra \\
            --enviado "2026-08-09 14:05" --sem-resposta

  4. Ler o placar:
        python3 coleta/coletores/whatsapp_teste.py --praca riomafra --placar

REGRAS DA MEDIÇÃO, para o número valer alguma coisa

  · sempre em dia útil, entre 9h e 11h ou 14h e 16h — fora disso mede o horário,
    não a clínica
  · a MESMA mensagem para todas, e ela precisa ser uma dúvida real de paciente
  · nunca marque consulta de verdade e nunca use nome de pessoa que existe
  · uma rodada por mês, no mesmo dia da semana
  · se a clínica responder e você não for continuar, diga que vai pensar. Do
    outro lado tem uma pessoa trabalhando.
"""
import argparse, json, pathlib, random, sys
import datetime as dt

RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent
IDENT = RAIZ/"dados"/"identidade"
SERIE = RAIZ/"dados"/"serie"
ARQ = SERIE/"whatsapp.jsonl"

MENSAGEM = ("Oi, boa tarde! Vi vocês no Google. "
            "Queria saber quanto fica o aparelho pra minha filha de 12 anos, "
            "e se precisa marcar avaliação antes.")

# A régua da rede é 40% de agendamento. Não existe régua publicada de TEMPO,
# então usamos a do mercado de serviço local, que é dura e conhecida.
FAIXAS = [(5, "excelente — responde enquanto o paciente ainda está olhando"),
          (30, "bom"),
          (120, "aceitável"),
          (480, "ruim — o paciente já falou com outra"),
          (10**9, "perdido")]


def faixa(minutos):
    for lim, rot in FAIXAS:
        if minutos <= lim:
            return rot
    return "perdido"


def le(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").split("\n") if l.strip()] \
        if p.exists() else []


def locais(praca):
    arq = IDENT/f"{praca}.json"
    if not arq.exists():
        sys.exit(f"praça '{praca}' não tem identidade")
    ident = json.loads(arq.read_text(encoding="utf-8"))
    return ident, [l for l in ident.get("locais", []) if l.get("place_id")]


def preparar(praca, n):
    ident, ls = locais(praca)
    random.shuffle(ls)                      # ordem sorteada: a 1ª da lista não
    ls = ls[:n]                             # pode ser sempre a nossa unidade
    hoje = dt.date.today()
    print(f"\n{'='*72}\n  TESTE DE WHATSAPP · {ident.get('nome', praca)} · {hoje}\n{'='*72}")
    print(f"\n  A MENSAGEM (a mesma para todas, palavra por palavra):\n")
    print(f"    {MENSAGEM}\n")
    print("  QUANDO: dia útil, 9h-11h ou 14h-16h. Fora disso mede o horário.\n")
    print(f"  A ORDEM (sorteada, {len(ls)} clínicas):\n")
    for i, l in enumerate(ls, 1):
        marca = "★ NOSSA" if l.get("papel") == "proprio" else "       "
        print(f"   {i:>2d}. {marca} {(l.get('nome') or l['local_id'])[:44]:44s} [{l['local_id']}]")
    print("\n  Anote a hora de envio de cada uma. Depois registre com --registrar.")
    print("  Sem resposta até o fim do dia seguinte = --sem-resposta.\n")


def registrar(a):
    if not a.enviado:
        sys.exit("--enviado é obrigatório (formato: \"2026-08-09 14:02\")")
    env = dt.datetime.fromisoformat(a.enviado)
    reg = {"snapshot_date": dt.date.today().isoformat(), "praca_id": a.praca,
           "local_id": a.registrar, "enviado_em": env.isoformat(),
           "mensagem": MENSAGEM, "fonte": "teste manual de WhatsApp",
           "filtro": "dia útil 9-11h ou 14-16h, mensagem idêntica"}
    if a.sem_resposta:
        reg.update({"respondeu": False, "minutos": None, "faixa": "perdido"})
    else:
        if not a.respondido:
            sys.exit("use --respondido ou --sem-resposta")
        res = dt.datetime.fromisoformat(a.respondido)
        mins = round((res-env).total_seconds()/60, 1)
        if mins < 0:
            sys.exit("a resposta veio antes do envio — confira as horas")
        reg.update({"respondeu": True, "respondido_em": res.isoformat(),
                    "minutos": mins, "faixa": faixa(mins),
                    "quem_respondeu": a.quem, "pediu_nome": a.pediu_nome,
                    "ofereceu_horario": a.ofereceu_horario,
                    "falou_preco": a.falou_preco})
    ARQ.parent.mkdir(parents=True, exist_ok=True)
    with ARQ.open("a", encoding="utf-8") as f:
        f.write(json.dumps(reg, ensure_ascii=False)+"\n")
    if reg["respondeu"]:
        print(f"  registrado: {a.registrar} respondeu em {reg['minutos']:.0f} min → {reg['faixa']}")
    else:
        print(f"  registrado: {a.registrar} NÃO respondeu")


def placar(praca):
    regs = [r for r in le(ARQ) if r.get("praca_id") == praca]
    if not regs:
        print(f"\n  Nenhum teste registrado para {praca}.")
        print("  Rode --preparar, mande as mensagens e registre com --registrar.\n")
        return
    ident, _ = locais(praca)
    nomes = {l["local_id"]: l.get("nome") or l["local_id"] for l in ident.get("locais", [])}
    ult = {}
    for r in sorted(regs, key=lambda x: x["snapshot_date"]):
        ult[r["local_id"]] = r
    linhas = sorted(ult.values(), key=lambda r: (r["minutos"] is None, r["minutos"] or 0))
    print(f"\n{'='*72}\n  TEMPO ATÉ A PRIMEIRA RESPOSTA · {ident.get('nome', praca)}\n{'='*72}")
    print(f"\n  {'minutos':>8s}  {'quem':>8s}  clínica")
    for r in linhas:
        marca = "★" if nomes.get(r["local_id"], "") and any(
            l.get("local_id") == r["local_id"] and l.get("papel") == "proprio"
            for l in ident.get("locais", [])) else " "
        m = "sem resposta" if r["minutos"] is None else f"{r['minutos']:.0f}"
        print(f"  {m:>8s}  {str(r.get('quem_respondeu') or '—'):>8s} {marca} "
              f"{nomes.get(r['local_id'], r['local_id'])[:42]}  {r.get('faixa','')}")
    resp = [r for r in linhas if r["minutos"] is not None]
    print(f"\n  {len(resp)} de {len(linhas)} responderam.")
    if resp:
        ms = sorted(r["minutos"] for r in resp)
        mediana = ms[len(ms)//2]
        print(f"  Mediana da praça: {mediana:.0f} min ({faixa(mediana)}).")
    nossa = [r for r in linhas if any(l.get("local_id") == r["local_id"]
             and l.get("papel") == "proprio" for l in ident.get("locais", []))]
    for r in nossa:
        if r["minutos"] is None:
            print(f"  ⚠ A NOSSA UNIDADE NÃO RESPONDEU. É o pior resultado possível:")
            print("    o interessado existiu, chamou, e nunca virou agendamento.")
        else:
            print(f"  A nossa unidade: {r['minutos']:.0f} min → {r['faixa']}")
    print("\n  Este número não existe em nenhuma fonte pública. Ele só existe")
    print("  porque alguém mandou a mensagem e anotou a hora.\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--praca")
    ap.add_argument("--preparar", action="store_true")
    ap.add_argument("--placar", action="store_true")
    ap.add_argument("--n", type=int, default=8, help="quantas clínicas na rodada")
    ap.add_argument("--registrar", help="local_id da clínica")
    ap.add_argument("--enviado")
    ap.add_argument("--respondido")
    ap.add_argument("--sem-resposta", action="store_true")
    ap.add_argument("--quem", choices=["humano", "bot", "audio"], default="humano")
    ap.add_argument("--pediu-nome", action="store_true")
    ap.add_argument("--ofereceu-horario", action="store_true")
    ap.add_argument("--falou-preco", action="store_true")
    a = ap.parse_args()
    if a.registrar:
        if not a.praca:
            sys.exit("--praca é obrigatório junto com --registrar")
        registrar(a)
    elif a.placar:
        placar(a.praca)
    elif a.preparar:
        preparar(a.praca, a.n)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
