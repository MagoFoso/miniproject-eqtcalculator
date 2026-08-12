import streamlit as st

from engine import RANKS, NAIPES
from ranges import selecionar_top_percentual, excluir_maos_especificas, equity_vs_range
from range_notation import parse_range
from tabelas_populacao import TABELA_RFI, TABELA_JAM
from pushfold import equity_necessaria_pushfold, risk_premium

st.set_page_config(page_title="Calculadora de Equity vs Range", page_icon="🃏")
st.title("🃏 Calculadora de Equity vs Range")
st.caption("Ferramenta de estudo — rode cenários antes/depois da sessão, não durante uma mão ativa.")

NOMES_NAIPE = {"h": "♥ copas", "d": "♦ ouros", "c": "♣ paus", "s": "♠ espadas"}


def selecionar_mao(prefixo):
    """
    Mostra os 4 seletores de mão (rank/naipe x2) e devolve a tupla das
    2 cartas escolhidas. 'prefixo' evita que os widgets de uma aba
    colidam em nome (key) com os da outra aba.
    """
    col1, col2 = st.columns(2)
    with col1:
        rank1 = st.selectbox("Rank carta 1", list(reversed(RANKS)), index=1, key=f"{prefixo}_r1")
        naipe1 = st.selectbox("Naipe carta 1", list(NAIPES), format_func=lambda n: NOMES_NAIPE[n], key=f"{prefixo}_n1")
    with col2:
        rank2 = st.selectbox("Rank carta 2", list(reversed(RANKS)), index=3, key=f"{prefixo}_r2")
        naipe2 = st.selectbox("Naipe carta 2", list(NAIPES), format_func=lambda n: NOMES_NAIPE[n], key=f"{prefixo}_n2")

    carta1, carta2 = rank1 + naipe1, rank2 + naipe2
    if carta1 == carta2:
        st.error("Você selecionou a mesma carta duas vezes. Ajuste antes de continuar.")
        st.stop()
    return carta1, carta2


def selecionar_range(prefixo):
    """
    Mostra o seletor de range (slider top X%, com tabela de apoio, ou
    range colado à mão) e devolve a lista de combos escolhida.
    """
    fonte_range = st.radio(
        "Como você quer definir o range?",
        ["Slider (top X% por força)", "Colar range personalizado"],
        horizontal=True,
        key=f"{prefixo}_fonte",
    )

    chave_slider = f"{prefixo}_percentual"

    if fonte_range == "Slider (top X% por força)":
        if chave_slider not in st.session_state:
            st.session_state[chave_slider] = 15

        with st.expander("📊 Preencher automaticamente com a tabela de RFI / Open Shove"):
            tipo_tabela = st.radio(
                "Tipo de situação", ["RFI (open raise)", "Open Shove (all-in)"],
                horizontal=True, key=f"{prefixo}_tipo_tabela",
            )
            tabela = TABELA_RFI if tipo_tabela.startswith("RFI") else TABELA_JAM

            col_a, col_b = st.columns(2)
            with col_a:
                posicao = st.selectbox("Posição", ["EP", "LJ", "HJ", "CO", "BTN", "SB"], key=f"{prefixo}_posicao")
            with col_b:
                faixa_stack = st.selectbox("Faixa de stack (BBs)", list(tabela.keys()), key=f"{prefixo}_faixa")

            valor_da_tabela = tabela[faixa_stack][posicao]
            st.write(f"Valor da tabela: **{valor_da_tabela}%**")

            if st.button("Usar esse valor no slider ⬇️", key=f"{prefixo}_usar_tabela"):
                st.session_state[chave_slider] = valor_da_tabela
                st.rerun()

        percentual_range = st.slider(
            "A população está fazendo essa jogada com o top X% das mãos:",
            min_value=1, max_value=100, key=chave_slider,
            help="Ajuste manualmente ou use a tabela acima para preencher automaticamente.",
        )
        combos_range = selecionar_top_percentual(percentual_range)

    else:
        texto_range = st.text_area(
            "Cole o range no formato padrão (separado por vírgula):",
            value="JJ+, AKo, AKs",
            help="Aceita: pares (77+), mãos exatas (AKs, T9o), e faixas com '+' (A8s+, JTs+, KTo+).",
            key=f"{prefixo}_texto_range",
        )
        try:
            combos_range = parse_range(texto_range)
            st.caption(f"✅ Range interpretado: {len(combos_range)} combinações ({len(combos_range) / 1326:.1%} do total).")
        except ValueError as e:
            st.error(f"Não consegui interpretar o range: {e}")
            st.stop()

    excluir_premium = st.checkbox(
        "Excluir QQ, KK e AA do range (ex: população sempre limpa/slowplaya essas mãos)",
        key=f"{prefixo}_excluir_premium",
    )
    if excluir_premium:
        combos_range = excluir_maos_especificas(combos_range, {"Q", "K", "A"})

    return combos_range, excluir_premium


def mostrar_resultado(equity_real, equity_necessaria, n_combos, excluir_premium, rotulo_acao=("CALL", "FOLD")):
    st.subheader("Resultado")
    col5, col6 = st.columns(2)
    col5.metric("Sua equity contra o range", f"{equity_real:.1%}")
    col6.metric("Equity necessária", f"{equity_necessaria:.1%}")

    margem = equity_real - equity_necessaria
    acao_positiva, acao_negativa = rotulo_acao

    if margem > 0:
        st.success(f"✅ {acao_positiva} — sua equity supera o necessário em {margem:.1%}")
    else:
        st.error(f"❌ {acao_negativa} — sua equity está {abs(margem):.1%} abaixo do necessário")

    aviso_premium = " (QQ/KK/AA excluídos)" if excluir_premium else ""
    st.caption(f"{n_combos} combinações no range{aviso_premium}, simuladas 4.000 vezes contra a sua mão.")


aba_normal, aba_pushfold, aba_m_medio = st.tabs([
    "📞 Call ou Fold (pot odds normal)",
    "🎯 All-in ou Fold (stack curto)",
    "📊 M médio dos jogadores restantes",
])

with aba_normal:
    st.header("1. Sua mão")
    carta1, carta2 = selecionar_mao("normal")

    st.header("2. Range da população")
    combos_range, excluir_premium = selecionar_range("normal")

    st.header("3. Pot odds")
    col3, col4 = st.columns(2)
    with col3:
        tamanho_pot = st.number_input("Tamanho do pote ANTES do seu call (BB)", min_value=0.0, value=10.0, step=0.5, key="normal_pot")
    with col4:
        valor_call = st.number_input("Quanto você precisa pagar para dar call", min_value=0.01, value=5.0, step=0.5, key="normal_call")

    equity_necessaria = valor_call / (tamanho_pot + valor_call)

    st.divider()
    if st.button("Calcular", type="primary", use_container_width=True, key="normal_calcular"):
        with st.spinner("Simulando milhares de mãos..."):
            equity_real = equity_vs_range((carta1, carta2), combos_range, trials=4000)
        mostrar_resultado(equity_real, equity_necessaria, len(combos_range), excluir_premium)

with aba_pushfold:
    st.caption(
        "Para quando seu stack está curto (tipicamente 0-10bb) e você está decidindo "
        "entre ir all-in ou foldar contra um raise. Assume que o vilão sempre paga "
        "(não considera fold equity)."
    )

    st.header("1. Sua mão")
    carta1_pf, carta2_pf = selecionar_mao("pushfold")

    st.header("2. Range de abertura da população")
    combos_range_pf, excluir_premium_pf = selecionar_range("pushfold")

    st.header("3. Stack e pote")
    col_pf1, col_pf2 = st.columns(2)
    with col_pf1:
        stack_bb = st.number_input("Seu stack total (BB)", min_value=0.1, value=8.71, step=0.1, key="pf_stack")
    with col_pf2:
        pote_antes = st.number_input(
            "Pote antes do raise: blinds + antes (BB)", min_value=0.0, value=1.5, step=0.1, key="pf_pote",
            help="Soma do small blind + big blind + antes (se houver), ANTES do raise que você está enfrentando.",
        )

    equity_necessaria_pf_base = equity_necessaria_pushfold(stack_bb, pote_antes)

    st.header("4. Risk premium (opcional)")
    aplicar_premium = st.checkbox(
        "Aumentar a equity necessária por jogadores que ainda vão agir depois de você",
        key="pf_aplicar_premium",
        help="Útil em fases late-game de torneio: mais gente pra acordar atrás de você = mais risco de dominação.",
    )

    if aplicar_premium:
        jogadores_restantes = st.slider(
            "Quantos jogadores ainda vão agir depois de você?",
            min_value=0, max_value=8, value=3, key="pf_jogadores_restantes",
        )
        premio = risk_premium(jogadores_restantes)
        equity_necessaria_pf = equity_necessaria_pf_base + premio
        st.caption(
            f"Base: {equity_necessaria_pf_base:.1%} + risk premium ({jogadores_restantes} jogador(es) × 1%): "
            f"{premio:.1%} → **{equity_necessaria_pf:.1%}** necessária"
        )
    else:
        equity_necessaria_pf = equity_necessaria_pf_base
        st.caption(f"Fórmula: {stack_bb:.2f} ÷ (2×{stack_bb:.2f} + {pote_antes:.2f}) = {equity_necessaria_pf:.1%}")

    st.divider()
    if st.button("Calcular", type="primary", use_container_width=True, key="pf_calcular"):
        with st.spinner("Simulando milhares de mãos..."):
            equity_real_pf = equity_vs_range((carta1_pf, carta2_pf), combos_range_pf, trials=4000)
        mostrar_resultado(
            equity_real_pf, equity_necessaria_pf, len(combos_range_pf), excluir_premium_pf,
            rotulo_acao=("ALL-IN", "FOLD"),
        )

with aba_m_medio:
    st.caption(
        "Preencha o stack (em big blinds) de cada jogador que ainda vai agir na mão. "
        "Deixe em 0 as caixas que não forem usar (até 6 jogadores)."
    )

    st.header("Stacks dos jogadores (BB)")
    colunas = st.columns(3)
    stacks_informados = []
    for i in range(6):
        with colunas[i % 3]:
            valor = st.number_input(f"Jogador {i + 1}", min_value=0.0, value=0.0, step=0.5, key=f"m_stack_{i}")
            stacks_informados.append(valor)

    stacks_validos = [s for s in stacks_informados if s > 0]

    st.divider()

    if stacks_validos:
        m_medio = sum(stacks_validos) / len(stacks_validos)
        st.metric("M médio", f"{m_medio:.2f} BB", help="Média simples dos stacks preenchidos, em big blinds.")
        st.caption(f"Calculado com {len(stacks_validos)} jogador(es): {', '.join(f'{s:.1f}' for s in stacks_validos)} BB")
    else:
        st.info("Preencha pelo menos um stack acima para calcular o M médio.")
