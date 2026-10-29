from pathlib import Path

import streamlit.components.v1 as components


_COMPONENT_DIR = (
    Path(__file__).resolve().parent.parent
    / "components"
    / "live_charts"
)

live_market_charts = components.declare_component(
    "chronos_live_market_charts",
    path=str(_COMPONENT_DIR),
)


def render_live_charts(
    times,
    prices,
    quantities,
    buy_volume,
    sell_volume,
):
    """Render persistent Plotly.js charts for recent public market trades."""
    return live_market_charts(
        times=times,
        prices=prices,
        quantities=quantities,
        buy_volume=float(buy_volume),
        sell_volume=float(sell_volume),
        key="chronos_live_market_charts",
        default=None,
    )
