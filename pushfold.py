"""
Fórmula de pot odds para decisões de ALL-IN ou FOLD com stack curto
(situações de push/fold, tipicamente 0-10bb, enfrentando um raise).

RACIOCÍNIO: quando você dá all-in com stack S e o vilão te cobre (tem
mais fichas que você), se ele pagar, ele sempre completa até igualar
exatamente o seu stack -- não importa o tamanho do raise original dele.
Por isso:
  - Você coloca: S (seu stack inteiro)
  - Ele coloca: também S (completa até seu stack)
  - Pote final: 2S + o que já estava na mesa antes do raise (blinds/antes)

Note que o tamanho do RAISE do vilão não entra na conta -- só importa
seu stack e o pote "morto" (blinds + antes) que já existia antes de
qualquer ação na mão.
"""


def equity_necessaria_pushfold(stack_bb, pote_antes_do_raise_bb):
    """
    stack_bb: seu stack total, em big blinds (é o quanto você arrisca).
    pote_antes_do_raise_bb: soma de blinds + antes que já estavam na mesa
                              ANTES do raise que você está enfrentando.
    Devolve a equity mínima necessária (0.0 a 1.0) para o shove ser lucrativo,
    assumindo que o vilão sempre paga (não considera fold equity).
    """
    return stack_bb / (2 * stack_bb + pote_antes_do_raise_bb)


def risk_premium(jogadores_restantes, premio_por_jogador=0.01):
    """
    Calcula o acréscimo de equity necessária por conta do "risk premium":
    quanto mais jogadores ainda vão agir depois de você, maior a chance de
    algum deles acordar com uma mão forte -- então exige-se uma margem
    extra de equity pra compensar esse risco adicional. Regra prática:
    +1% de equity necessária por jogador restante (ajustável).

    Devolve o acréscimo (ex: 0.03 para 3 jogadores a 1% cada), NÃO o total.
    """
    return jogadores_restantes * premio_por_jogador
