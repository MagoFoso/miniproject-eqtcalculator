"""
Motor de avaliação de poker.
Cartas são representadas como strings de 2 caracteres: rank + naipe.
Ex: "Ah" = Ás de copas (hearts), "Ts" = 10 de espadas (spades).
Ranks: 2 3 4 5 6 7 8 9 T J Q K A
Naipes: h (hearts/copas) d (diamonds/ouros) c (clubs/paus) s (spades/espadas)
"""

import itertools
import random

RANKS = "23456789TJQKA"
NAIPES = "hdcs"

VALOR_RANK = {r: i for i, r in enumerate(RANKS, start=2)}  # "2"->2 ... "A"->14

NOMES_CATEGORIA = [
    "carta alta", "par", "dois pares", "trinca", "sequencia",
    "flush", "full house", "quadra", "straight flush",
]


def criar_baralho():
    return [r + n for r in RANKS for n in NAIPES]


def avaliar_5(cartas):
    """Avalia exatamente 5 cartas. Devolve tupla (categoria, desempates)."""
    ranks = [c[0] for c in cartas]
    naipes = [c[1] for c in cartas]

    contagem = {}
    for r in ranks:
        contagem[r] = contagem.get(r, 0) + 1

    grupos = sorted(contagem.items(), key=lambda kv: (kv[1], VALOR_RANK[kv[0]]), reverse=True)
    padrao = tuple(q for _, q in grupos)
    valores_grupo = tuple(VALOR_RANK[r] for r, _ in grupos)

    valores = sorted((VALOR_RANK[r] for r in ranks), reverse=True)
    flush = len(set(naipes)) == 1

    sequencia_normal = all(valores[i] - valores[i + 1] == 1 for i in range(4))
    if sequencia_normal:
        sequencia, topo = True, valores[0]
    elif valores == [14, 5, 4, 3, 2]:
        sequencia, topo = True, 5
    else:
        sequencia, topo = False, None

    if sequencia and flush:
        return (8, (topo,))
    if padrao[0] == 4:
        return (7, valores_grupo)
    if padrao == (3, 2):
        return (6, valores_grupo)
    if flush:
        return (5, tuple(valores))
    if sequencia:
        return (4, (topo,))
    if padrao[0] == 3:
        return (3, valores_grupo)
    if padrao == (2, 2, 1):
        return (2, valores_grupo)
    if padrao[0] == 2:
        return (1, valores_grupo)
    return (0, tuple(valores))


def avaliar_melhor_de_7(cartas7):
    """
    Recebe 7 cartas (2 da mão + 5 do board) e testa todas as combinações
    possíveis de 5 entre elas (21 no total), devolvendo a MELHOR avaliação.
    itertools.combinations gera essas combinações prontas -- não precisamos
    escrever a lógica combinatória na mão.
    """
    melhor = None
    for combo5 in itertools.combinations(cartas7, 5):
        forca = avaliar_5(combo5)
        if melhor is None or forca > melhor:
            melhor = forca
    return melhor


def nome_da_mao(forca):
    return NOMES_CATEGORIA[forca[0]]
