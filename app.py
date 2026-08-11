import streamlit as st

from engine import RANKS, NAIPES
from ranges import selecionar_top_percentual, excluir_maos_especificas, equity_vs_range
from range_notation import parse_range
from tabelas_populacao import TABELA_RFI, TABELA_JAM

st.set_page_config(page_title="Call ou Fold vs Range", page_icon="🃏")
st.title("🃏 Call ou Fold contra o range da população")
st.caption("Ferramenta de estudo — rode cenários antes/depois da sessão, não durante uma mão ativa.")

NOMES_NAIPE = {"h": "♥ copas", "d": "♦ ouros", "c": "♣ paus", "s": "♠ espadas"}

st.header("1. Sua mão")
col1, col2 = st.columns(2)
with col1:
    rank1 = st.selectbox("Rank carta 1", list(reversed(RANKS)), index=1, key="r1")
    naipe1 = st.selectbox("Naipe carta 1", list(NAIPES), format_func=lambda n: NOMES_NAIPE[n], key="n1")
with col2:
    rank2 = st.selectbox("Rank carta 2", list(reversed(RANKS)), index=3, key="r2")
    naipe2 = st.selectbox("Naipe carta 2", list(NAIPES), format_func=lambda n: NOMES_NAIPE[n], key="n2")

carta1 = rank1 + naipe1
carta2 = rank2 + naipe2

if carta1 == carta2:
    st.error("Você selecionou a mesma carta duas vezes. Ajuste antes de continuar.")
    st.stop()

st.header("2. Range da população (o que você está enfrentando)")

fonte_range = st.radio(
    "Como você quer definir o range?",
    ["Slider (top X% por força)", "Colar range personalizado"],
    horizontal=True,
)

combos_range = None

if fonte_range == "Slider (top X% por força)":
    # Valor inicial do slider, guardado no session_state -- isso permite que o
    # botão "usar esse valor" (mais abaixo) consiga alterar o slider.
    if "percentual_range" not in st.session_state:
        st.session_state["percentual_range"] = 15

    with st.expander("📊 Preencher automaticamente com a tabela de RFI / Open Shove"):
        tipo_tabela = st.radio("Tipo de situação", ["RFI (open raise)", "Open Shove (all-in)"], horizontal=True)
        tabela = TABELA_RFI if tipo_tabela.startswith("RFI") else TABELA_JAM

        col_a, col_b = st.columns(2)
        with col_a:
            posicao = st.selectbox("Posição", ["EP", "LJ", "HJ", "CO", "BTN", "SB"])
        with col_b:
            faixa_stack = st.selectbox("Faixa de stack (BBs)", list(tabela.keys()))

        valor_da_tabela = tabela[faixa_stack][posicao]
        st.write(f"Valor da tabela: **{valor_da_tabela}%**")

        if st.button("Usar esse valor no slider ⬇️"):
            st.session_state["percentual_range"] = valor_da_tabela
            st.rerun()

    percentual_range = st.slider(
        "A população está fazendo essa jogada (shove/resteal) com o top X% das mãos:",
        min_value=1, max_value=100, key="percentual_range",
        help="Ajuste manualmente ou use a tabela acima para preencher automaticamente.",
    )

    combos_range = selecionar_top_percentual(percentual_range)

else:
    texto_range = st.text_area(
        "Cole o range no formato padrão (separado por vírgula):",
        value="JJ+, AKo, AKs",
        help="Aceita: pares (77+), mãos exatas (AKs, T9o), e faixas com '+' (A8s+, JTs+, KTo+).",
    )
    try:
        combos_range = parse_range(texto_range)
        st.caption(f"✅ Range interpretado: {len(combos_range)} combinações de cartas ({len(combos_range) / 1326:.1%} do total).")
    except ValueError as e:
        st.error(f"Não consegui interpretar o range: {e}")
        st.stop()

excluir_premium = st.checkbox(
    "Excluir QQ, KK e AA do range (ex: população sempre limpa/slowplaya essas mãos)"
)

st.header("3. Pot odds")
col3, col4 = st.columns(2)
with col3:
    tamanho_pot = st.number_input("Tamanho do pote ANTES do seu call (em BB ou fichas)", min_value=0.0, value=10.0, step=0.5)
with col4:
    valor_call = st.number_input("Quanto você precisa pagar para dar call", min_value=0.01, value=5.0, step=0.5)

equity_necessaria = valor_call / (tamanho_pot + valor_call)

st.divider()

if st.button("Calcular", type="primary", use_container_width=True):
    with st.spinner("Simulando milhares de mãos..."):
        range_final = combos_range
        if excluir_premium:
            range_final = excluir_maos_especificas(range_final, {"Q", "K", "A"})
        equity_real = equity_vs_range((carta1, carta2), range_final, trials=4000)

    st.subheader("Resultado")

    col5, col6 = st.columns(2)
    col5.metric("Sua equity contra o range", f"{equity_real:.1%}")
    col6.metric("Equity necessária (pot odds)", f"{equity_necessaria:.1%}")

    margem = equity_real - equity_necessaria

    if margem > 0:
        st.success(f"✅ CALL — sua equity supera o necessário em {margem:.1%}")
    else:
        st.error(f"❌ FOLD — sua equity está {abs(margem):.1%} abaixo do necessário")

    aviso_premium = " (QQ/KK/AA excluídos)" if excluir_premium else ""
    st.caption(
        f"{len(range_final)} combinações de mãos no range da população{aviso_premium}, "
        f"simuladas 4.000 vezes contra a sua mão."
    )
