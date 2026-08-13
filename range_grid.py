"""
Gera a grade 13x13 clássica de range de poker (mãos iniciais do Hold'em),
com cada célula sombreada de acordo com a fração dela presente no range
informado (0% = célula clara, 100% = célula escura).

Convenção padrão de grade: pares na diagonal, mãos suited acima da
diagonal (linha = carta mais alta), mãos offsuit abaixo (coluna = carta
mais alta).
"""

import itertools

from engine import RANKS, NAIPES

RANKS_DESC = "AKQJT98765432"  # do mais alto pro mais baixo, ordem da grade


def _combos_possiveis(notacao):
    r1, r2 = notacao[0], notacao[1]
    if r1 == r2:
        return list(itertools.combinations(NAIPES, 2))  # 6 combos
    elif notacao.endswith("s"):
        return [(n, n) for n in NAIPES]  # 4 combos
    else:
        return [(n1, n2) for n1 in NAIPES for n2 in NAIPES if n1 != n2]  # 12 combos


def _notacao_da_celula(linha, coluna):
    if linha == coluna:
        return RANKS_DESC[linha] + RANKS_DESC[linha]
    elif linha < coluna:
        return RANKS_DESC[linha] + RANKS_DESC[coluna] + "s"
    else:
        return RANKS_DESC[coluna] + RANKS_DESC[linha] + "o"


def _fracao_no_range(notacao, combos_range_set):
    r1, r2 = notacao[0], notacao[1]
    naipes_possiveis = _combos_possiveis(notacao)
    total = len(naipes_possiveis)
    presentes = 0
    for n1, n2 in naipes_possiveis:
        if (r1 + n1, r2 + n2) in combos_range_set or (r2 + n2, r1 + n1) in combos_range_set:
            presentes += 1
    return presentes / total


def gerar_html_grade(combos_range):
    """Recebe a lista de combos (tuplas de cartas) e devolve o HTML da grade 13x13."""
    combos_range_set = set(combos_range)

    celulas_html = []
    for linha in range(13):
        for coluna in range(13):
            notacao = _notacao_da_celula(linha, coluna)
            fracao = _fracao_no_range(notacao, combos_range_set)

            # Cor: cinza-azulado escurecendo conforme a fração presente.
            opacidade = round(fracao, 2)
            cor_fundo = f"rgba(70, 90, 110, {opacidade})"
            cor_texto = "#ffffff" if fracao > 0.5 else "#888888"

            celulas_html.append(
                f'<div style="background:{cor_fundo}; color:{cor_texto}; '
                f'display:flex; align-items:center; justify-content:center; '
                f'font-size:11px; font-family:monospace; border-radius:3px; '
                f'height:28px;">{notacao}</div>'
            )

    grade = "".join(celulas_html)
    return f"""
    <div style="display:grid; grid-template-columns:repeat(13, 1fr); gap:2px; max-width:460px;">
        {grade}
    </div>
    """
