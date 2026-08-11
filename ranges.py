"""
Funções para trabalhar com ranges de mãos: selecionar o "top X%" de um
ranking e calcular a equity de uma mão específica contra esse range inteiro.
"""

import json
import itertools
import random

from engine import RANKS, NAIPES, avaliar_melhor_de_7

# Quantas combinações de cartas cada tipo de mão representa.
# Par: 6 combinações (ex: 7h7d, 7h7c, 7h7s, 7d7c, 7d7s, 7c7s)
# Suited: 4 combinações (um por naipe)
# Offsuit: 12 combinações
with open("ranking_maos.json") as f:
    RANKING_MAOS = json.load(f)  # lista de [notacao, equity], já ordenada


def _combos_da_mao(notacao):
    r1, r2 = notacao[0], notacao[1]
    if r1 == r2:
        return [(r1 + n1, r2 + n2) for n1, n2 in itertools.combinations(NAIPES, 2)]
    elif notacao.endswith("s"):
        return [(r1 + n, r2 + n) for n in NAIPES]
    else:
        return [(r1 + n1, r2 + n2) for n1 in NAIPES for n2 in NAIPES if n1 != n2]


def selecionar_top_percentual(percentual):
    """
    Recebe um percentual (0 a 100) e devolve a lista de combinações de
    cartas que representam o "top X%" de mãos mais fortes, com base no
    ranking. Usamos CONTAGEM DE COMBINAÇÕES (não número de mãos), porque
    é assim que se mede % de range de verdade no poker: existem 1326
    combinações de 2 cartas possíveis no total (52 escolhe 2), e cada tipo
    de mão contribui com um número diferente de combinações.
    """
    total_combos = 1326
    limite = total_combos * (percentual / 100)

    combos_selecionados = []
    combos_acumulados = 0

    for notacao, equity in RANKING_MAOS:
        combos_da_mao = _combos_da_mao(notacao)
        if combos_acumulados >= limite:
            break
        combos_selecionados.extend(combos_da_mao)
        combos_acumulados += len(combos_da_mao)

    return combos_selecionados


def excluir_maos_especificas(combos, ranks_para_excluir):
    """
    Remove de um range já montado qualquer combinação de PAR cujo rank
    esteja no conjunto informado. Ex: excluir_maos_especificas(combos,
    {"Q", "K", "A"}) tira todos os combos de QQ, KK e AA do range.

    Usa um 'set' (conjunto) para ranks_para_excluir porque checar
    "está dentro" de um set é muito mais rápido que checar numa lista,
    e aqui não precisamos de ordem nem de repetição.
    """
    return [
        c for c in combos
        if not (c[0][0] == c[1][0] and c[0][0] in ranks_para_excluir)
    ]


def equity_vs_range(mao_heroi, combos_range, cartas_board=None, trials=3000):
    """
    Calcula a equity da mão do herói contra TODAS as combinações de um
    range (ex: "top 15% da população"), via Monte Carlo.

    mao_heroi: tupla tipo ('Ah', 'Kh')
    combos_range: lista de tuplas de cartas do oponente (vindo da função acima)
    cartas_board: lista de cartas já reveladas no board (opcional, vazio = pre-flop)
    """
    cartas_board = cartas_board or []

    # Remove do range qualquer combinação que use uma carta que o herói
    # já tem na mão, ou que já esteja no board -- essas combinações são
    # fisicamente impossíveis (a carta já está "em uso").
    cartas_bloqueadas = set(mao_heroi) | set(cartas_board)
    combos_validos = [
        c for c in combos_range
        if c[0] not in cartas_bloqueadas and c[1] not in cartas_bloqueadas
    ]

    if not combos_validos:
        raise ValueError("Nenhuma combinação válida sobrou no range (conflito de cartas).")

    vitorias = 0.0
    for _ in range(trials):
        mao_oponente = random.choice(combos_validos)

        cartas_em_uso = set(mao_heroi) | set(mao_oponente) | set(cartas_board)
        baralho_restante = [
            r + n for r in RANKS for n in NAIPES if (r + n) not in cartas_em_uso
        ]
        random.shuffle(baralho_restante)

        cartas_faltantes_no_board = 5 - len(cartas_board)
        board_completo = list(cartas_board) + [
            baralho_restante.pop() for _ in range(cartas_faltantes_no_board)
        ]

        forca_heroi = avaliar_melhor_de_7(list(mao_heroi) + board_completo)
        forca_oponente = avaliar_melhor_de_7(list(mao_oponente) + board_completo)

        if forca_heroi > forca_oponente:
            vitorias += 1
        elif forca_heroi == forca_oponente:
            vitorias += 0.5

    return vitorias / trials
