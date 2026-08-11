"""
Interpretador de notação de range de poker: recebe texto tipo
"JJ+, AKo, AKs" e devolve a lista de combinações de cartas correspondente.

REGRAS DE INTERPRETAÇÃO DO "+" (convenção padrão de ferramentas como
Equilab/Flopzilla, usada aqui):

1. PAR com "+" (ex: "88+"): inclui esse par e todos os pares acima, até AA.

2. DUAS CARTAS DIFERENTES com "+" (ex: "A8s+", "JTs+"):
   - Se o "gap" (distância) entre as duas cartas é de 1 posição (cartas
     "conectadas", tipo J-T ou 9-8): a carta mais alta E a mais baixa
     SOBEM JUNTAS, mantendo a mesma distância entre elas, até chegar em
     KQ (não avança até AK, que já é considerado hand isolada).
     Ex: "JTs+" = JTs, QJs, KQs

   - Se o gap é de 2 ou mais (ex: A-8, K-T): a carta mais alta fica FIXA
     (é a "âncora"), e só a mais baixa (o kicker) sobe, até uma posição
     abaixo da âncora.
     Ex: "A8s+" = A8s, A9s, ATs, AJs, AQs, AKs
     Ex: "KTs+" = KTs, KJs, KQs

Essa distinção existe porque, com gap de 1, não haveria "espaço" para o
kicker subir sem virar a própria carta âncora -- daí a necessidade da
regra diferente.
"""

import itertools

from engine import RANKS, NAIPES


def _combos_da_mao(notacao):
    """Converte uma notação exata (ex: 'AKs', '77') em combinações de cartas."""
    r1, r2 = notacao[0], notacao[1]
    if r1 == r2:
        return [(r1 + n1, r2 + n2) for n1, n2 in itertools.combinations(NAIPES, 2)]
    elif notacao.endswith("s"):
        return [(r1 + n, r2 + n) for n in NAIPES]
    else:
        return [(r1 + n1, r2 + n2) for n1 in NAIPES for n2 in NAIPES if n1 != n2]


def _expandir_par(rank, tem_plus):
    if tem_plus:
        idx = RANKS.index(rank)
        ranks_alvo = RANKS[idx:]  # do rank informado até "A" (RANKS é 2..A crescente)
    else:
        ranks_alvo = [rank]
    return [r + r for r in ranks_alvo]


def _expandir_nao_par(r1, r2, sufixos, tem_plus):
    i1, i2 = RANKS.index(r1), RANKS.index(r2)
    if i1 < i2:  # garante que i1 é sempre a carta mais alta
        i1, i2 = i2, i1
        r1, r2 = r2, r1

    if not tem_plus:
        return [r1 + r2 + suf for suf in sufixos]

    gap = i1 - i2
    resultado = []

    if gap == 1:
        # cartas conectadas: sobem juntas, mantendo a distância de 1
        idx_k = RANKS.index("K")
        cur1 = i1
        while cur1 <= idx_k:
            cur2 = cur1 - gap
            for suf in sufixos:
                resultado.append(RANKS[cur1] + RANKS[cur2] + suf)
            cur1 += 1
    else:
        # carta alta fixa (âncora), kicker sobe até 1 abaixo dela
        for cur2 in range(i2, i1):
            for suf in sufixos:
                resultado.append(r1 + RANKS[cur2] + suf)

    return resultado


def expandir_token(token):
    """Expande UMA notação (ex: 'JJ+' ou 'A8s+') na lista de notações de mão que ela representa."""
    token = token.strip()
    if not token:
        return []

    tem_plus = token.endswith("+")
    base = token[:-1] if tem_plus else token

    if len(base) == 2 and base[0] == base[1]:
        return _expandir_par(base[0], tem_plus)
    elif len(base) == 3 and base[2] in ("s", "o"):
        return _expandir_nao_par(base[0], base[1], [base[2]], tem_plus)
    elif len(base) == 2 and base[0] != base[1]:
        # sem sufixo 's'/'o': significa AMBOS (suited e offsuit) daquela combinação
        return _expandir_nao_par(base[0], base[1], ["s", "o"], tem_plus)
    else:
        raise ValueError(f"Notação de mão não reconhecida: '{token}'")


def parse_range(texto):
    """
    Recebe uma string com notações separadas por vírgula, ex:
    'JJ+, AKo, AKs' e devolve a lista de combinações de cartas (tuplas).
    """
    notacoes_expandidas = []
    for token in texto.split(","):
        notacoes_expandidas.extend(expandir_token(token))

    # Remove notações duplicadas (pode acontecer se dois tokens se sobrepõem),
    # preservando a ordem -- dict.fromkeys() é um truque comum pra isso.
    notacoes_unicas = list(dict.fromkeys(notacoes_expandidas))

    combos = []
    for notacao in notacoes_unicas:
        combos.extend(_combos_da_mao(notacao))

    combos_unicos = list(dict.fromkeys(combos))
    return combos_unicos
