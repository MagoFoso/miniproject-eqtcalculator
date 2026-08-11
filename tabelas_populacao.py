"""
Tabelas de referência da população, fornecidas pelo usuário (baseadas em
seus próprios estudos de MDA). Os valores são o percentual de mãos (%)
com que a população faz RFI (raise first in) ou open-shove (all-in),
por posição e faixa de stack em BBs.

OBS: extraídos manualmente de uma imagem/tabela -- os números pequenos em
subscrito (provavelmente contagem de combos) foram ignorados, só o
percentual principal foi usado. Vale conferir contra a fonte original.
"""

TABELA_RFI = {
    "Overall":       {"EP": 17,  "LJ": 21,  "HJ": 25,  "CO": 31,  "BTN": 42,  "SB": 28},
    "7.5-12.5bb":    {"EP": 3,   "LJ": 3.1, "HJ": 3.2, "CO": 3.3, "BTN": 3.7, "SB": 2.9},
    "10-15bb":       {"EP": 6.2, "LJ": 6.7, "HJ": 7,   "CO": 7.5, "BTN": 8.5, "SB": 4.3},
    "12.5-17.5bb":   {"EP": 10,  "LJ": 12,  "HJ": 12,  "CO": 14,  "BTN": 16,  "SB": 6.7},
    "15-20bb":       {"EP": 13,  "LJ": 16,  "HJ": 18,  "CO": 21,  "BTN": 25,  "SB": 9.8},
    "17.5-22.5bb":   {"EP": 15,  "LJ": 18,  "HJ": 21,  "CO": 26,  "BTN": 31,  "SB": 13},
    "20-50bb":       {"EP": 18,  "LJ": 21,  "HJ": 25,  "CO": 32,  "BTN": 43,  "SB": 26},
    "50bb+":         {"EP": 20,  "LJ": 24,  "HJ": 29,  "CO": 37,  "BTN": 51,  "SB": 38},
}

TABELA_JAM = {
    "5-9bb":   {"EP": 20,  "LJ": 22,  "HJ": 26,  "CO": 30,  "BTN": 37,  "SB": 54},
    "9-10bb":  {"EP": 15,  "LJ": 18,  "HJ": 22,  "CO": 26,  "BTN": 33,  "SB": 49},
    "10-11bb": {"EP": 13,  "LJ": 16,  "HJ": 19,  "CO": 24,  "BTN": 31,  "SB": 47},
    "11-12bb": {"EP": 11,  "LJ": 14,  "HJ": 17,  "CO": 23,  "BTN": 30,  "SB": 45},
    "12-13bb": {"EP": 9,   "LJ": 12,  "HJ": 15,  "CO": 20,  "BTN": 28,  "SB": 42},
    "13-14bb": {"EP": 7,   "LJ": 9.4, "HJ": 13,  "CO": 18,  "BTN": 25,  "SB": 39},
    "14-15bb": {"EP": 5,   "LJ": 6.8, "HJ": 9.4, "CO": 14,  "BTN": 21,  "SB": 36},
    "15-16bb": {"EP": 3.6, "LJ": 5.1, "HJ": 7.4, "CO": 11,  "BTN": 19,  "SB": 33},
    "16-17bb": {"EP": 2.4, "LJ": 3.3, "HJ": 4.9, "CO": 8,   "BTN": 15,  "SB": 29},
    "17-18bb": {"EP": 1.5, "LJ": 2,   "HJ": 3.6, "CO": 5.6, "BTN": 12,  "SB": 25},
    "18-19bb": {"EP": 1.1, "LJ": 1.5, "HJ": 2.2, "CO": 4.4, "BTN": 9.8, "SB": 22},
    "19-20bb": {"EP": 0.8, "LJ": 0.9, "HJ": 1.5, "CO": 3.2, "BTN": 7.7, "SB": 21},
}
