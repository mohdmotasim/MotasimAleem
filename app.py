import difflib
import json
import os
import re
import statistics
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from io import StringIO

import feedparser
import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf

NSE_SUFFIX = ".NS"
SP500_SYMBOL = "^GSPC"
DEFAULT_WATCHLIST = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]
NSE_EQUITY_CSV_URL = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
FALLBACK_NSE_SYMBOLS = [
    ("RELIANCE", "Reliance Industries"),
    ("TCS", "Tata Consultancy Services"),
    ("INFY", "Infosys"),
    ("HDFCBANK", "HDFC Bank"),
    ("ICICIBANK", "ICICI Bank"),
    ("SBIN", "State Bank of India"),
    ("BHARTIARTL", "Bharti Airtel"),
    ("ITC", "ITC"),
    ("HINDUNILVR", "Hindustan Unilever"),
    ("KOTAKBANK", "Kotak Mahindra Bank"),
    ("LT", "Larsen & Toubro"),
    ("AXISBANK", "Axis Bank"),
    ("BAJFINANCE", "Bajaj Finance"),
    ("MARUTI", "Maruti Suzuki"),
    ("TATAMOTORS", "Tata Motors"),
    ("SUNPHARMA", "Sun Pharmaceutical"),
    ("WIPRO", "Wipro"),
    ("HCLTECH", "HCL Technologies"),
    ("NTPC", "NTPC"),
    ("ONGC", "Oil & Natural Gas Corp"),
    ("POWERGRID", "Power Grid Corporation"),
    ("ADANIENT", "Adani Enterprises"),
    ("ADANIPORTS", "Adani Ports"),
    ("TITAN", "Titan Company"),
    ("ASIANPAINT", "Asian Paints"),
    ("ULTRACEMCO", "UltraTech Cement"),
    ("NESTLEIND", "Nestle India"),
    ("M&M", "Mahindra & Mahindra"),
    ("BEL", "Bharat Electronics"),
    ("HAL", "Hindustan Aeronautics"),
    ("HINDALCO", "Hindalco Industries"),
    ("CGPOWER", "CG Power"),
]
RATE_LIMIT_MSG = (
    "Data temporarily unavailable — yfinance rate limited. Try again in 30s."
)


def nse_not_found_error(user_input: str) -> None:
    st.error(
        f"'{user_input}' not found on NSE. Try the full ticker e.g. TATAMOTORS, BAJFINANCE"
    )


def _active_page_title(symbol: str | None) -> str:
    if not symbol:
        return "NSE Dashboard"
    return f"{symbol.removesuffix(NSE_SUFFIX)} | NSE Dashboard"


@st.cache_data(ttl=86400)
def load_nse_symbol_directory() -> pd.DataFrame:
    try:
        request = urllib.request.Request(
            NSE_EQUITY_CSV_URL,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        with urllib.request.urlopen(request, timeout=12) as response:
            raw = response.read().decode("utf-8", errors="ignore")
        df = pd.read_csv(StringIO(raw))
        df.columns = [str(c).strip().upper() for c in df.columns]
        symbol_col = "SYMBOL" if "SYMBOL" in df.columns else df.columns[0]
        name_col = next((c for c in df.columns if "NAME" in c), df.columns[1] if len(df.columns) > 1 else symbol_col)
        directory = pd.DataFrame(
            {
                "symbol": df[symbol_col].astype(str).str.strip().str.upper(),
                "name": df[name_col].astype(str).str.strip(),
            }
        )
        return directory.dropna(subset=["symbol"]).drop_duplicates(subset=["symbol"])
    except Exception:
        return pd.DataFrame(FALLBACK_NSE_SYMBOLS, columns=["symbol", "name"])


@st.cache_data(ttl=300)
def fuzzy_search_nse(query: str, limit: int = 8) -> list[tuple[str, str]]:
    needle = (query or "").strip().upper()
    if len(needle) < 1:
        return []

    directory = load_nse_symbol_directory()
    if directory.empty:
        return []

    scored: list[tuple[int, str, str]] = []

    for _, row in directory.iterrows():
        sym = str(row["symbol"])
        name_upper = str(row["name"]).upper()
        display_name = str(row["name"])
        score = 0
        if sym.startswith(needle):
            score += 120 + max(0, 20 - (len(sym) - len(needle)))
        elif needle in sym:
            score += 70
        if name_upper.startswith(needle):
            score += 60
        elif needle in name_upper:
            score += 45
        if score > 0:
            scored.append((score, sym, display_name))

    if len(scored) < limit:
        symbols = directory["symbol"].tolist()
        fuzzy_hits = difflib.get_close_matches(needle, symbols, n=limit * 2, cutoff=0.45)
        existing = {sym for _, sym, _ in scored}
        name_map = dict(zip(directory["symbol"], directory["name"]))
        for sym in fuzzy_hits:
            if sym in existing:
                continue
            scored.append((35, sym, str(name_map.get(sym, sym))))
            existing.add(sym)

    scored.sort(key=lambda row: (-row[0], row[1]))
    return [(sym, name) for _, sym, name in scored[:limit]]


@st.cache_data(ttl=300)
def search_nse_stock(query: str) -> tuple[bool, str, str]:
    raw = (query or "").strip().upper()
    if not raw:
        return False, "", ""

    ticker_symbol = raw if raw.endswith(NSE_SUFFIX) else f"{raw}{NSE_SUFFIX}"

    try:
        fast = yf.Ticker(ticker_symbol).fast_info
    except Exception:
        return False, ticker_symbol, ticker_symbol.removesuffix(NSE_SUFFIX)

    if not fast:
        return False, ticker_symbol, ticker_symbol.removesuffix(NSE_SUFFIX)

    has_price = bool(fast.get("last_price") or fast.get("regular_market_price"))
    has_symbol = bool(fast.get("symbol"))
    valid = has_price or has_symbol

    display_name = (
        fast.get("short_name")
        or fast.get("long_name")
        or ticker_symbol.removesuffix(NSE_SUFFIX)
    )
    return valid, ticker_symbol, str(display_name)


CONVICTION_TIER_INFO = {
    "1": {"name": "Watching", "hint": "Researching, no position", "cap": 0.0, "default_alloc": 0.0},
    "2": {"name": "Starter", "hint": "<2% portfolio each", "cap": 2.0, "default_alloc": 1.5},
    "3": {"name": "High conviction", "hint": "Up to 8% each", "cap": 8.0, "default_alloc": 5.0},
}

CONVICTION_STATE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".data", "conviction_state.json"
)

HOLDINGS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".data", "holdings.json"
)


def _default_conviction_tiers() -> dict[str, list[str]]:
    return {"1": list(DEFAULT_WATCHLIST), "2": [], "3": []}


def _default_holdings() -> list[dict]:
    return []


def _load_holdings_from_disk() -> list[dict] | None:
    if not os.path.isfile(HOLDINGS_FILE):
        return None
    try:
        with open(HOLDINGS_FILE, encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, list):
            return None
        return data
    except (OSError, json.JSONDecodeError, TypeError):
        return None


def _save_holdings_to_disk(holdings: list[dict]) -> None:
    try:
        os.makedirs(os.path.dirname(HOLDINGS_FILE), exist_ok=True)
        with open(HOLDINGS_FILE, "w", encoding="utf-8") as handle:
            json.dump(holdings, handle, indent=2)
    except OSError:
        pass


def get_holdings() -> list[dict]:
    if "holdings" not in st.session_state:
        loaded = _load_holdings_from_disk()
        st.session_state["holdings"] = loaded if loaded else _default_holdings()
    return st.session_state["holdings"]


def add_holding(symbol: str, quantity: float, purchase_price: float) -> None:
    holdings = get_holdings()
    holdings.append({
        "symbol": symbol,
        "quantity": quantity,
        "purchase_price": purchase_price,
        "added_date": datetime.now().strftime("%Y-%m-%d"),
    })
    st.session_state["holdings"] = holdings
    _save_holdings_to_disk(holdings)


def remove_holding(index: int) -> None:
    holdings = get_holdings()
    if 0 <= index < len(holdings):
        holdings.pop(index)
        st.session_state["holdings"] = holdings
        _save_holdings_to_disk(holdings)


def update_holding(index: int, quantity: float, purchase_price: float) -> None:
    holdings = get_holdings()
    if 0 <= index < len(holdings):
        holdings[index]["quantity"] = quantity
        holdings[index]["purchase_price"] = purchase_price
        st.session_state["holdings"] = holdings
        _save_holdings_to_disk(holdings)


def _normalize_tiers(tiers: dict) -> dict[str, list[str]]:
    return {
        "1": list(tiers.get("1", [])),
        "2": list(tiers.get("2", [])),
        "3": list(tiers.get("3", [])),
    }


def _load_conviction_from_disk() -> dict | None:
    if not os.path.isfile(CONVICTION_STATE_FILE):
        return None
    try:
        with open(CONVICTION_STATE_FILE, encoding="utf-8") as handle:
            data = json.load(handle)
        tiers = data.get("tiers")
        if not isinstance(tiers, dict):
            return None
        return {
            "tiers": _normalize_tiers(tiers),
            "meta": data.get("meta") if isinstance(data.get("meta"), dict) else {},
            "selected_symbol": data.get("selected_symbol"),
        }
    except (OSError, json.JSONDecodeError, TypeError):
        return None


def _save_conviction_to_disk() -> None:
    try:
        os.makedirs(os.path.dirname(CONVICTION_STATE_FILE), exist_ok=True)
        payload = {
            "tiers": _normalize_tiers(st.session_state.get("conviction_tiers", _default_conviction_tiers())),
            "meta": st.session_state.get("conviction_meta", {}),
            "selected_symbol": st.session_state.get("selected_symbol"),
        }
        with open(CONVICTION_STATE_FILE, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
    except OSError:
        pass


def get_conviction_tiers() -> dict[str, list[str]]:
    if "conviction_tiers" in st.session_state:
        tiers = st.session_state["conviction_tiers"]
    else:
        saved = _load_conviction_from_disk()
        tiers = saved["tiers"] if saved else _default_conviction_tiers()
    return _normalize_tiers(tiers)


def init_conviction_state() -> None:
    if "conviction_loaded" not in st.session_state:
        saved = _load_conviction_from_disk()
        if saved:
            st.session_state["conviction_tiers"] = saved["tiers"]
            st.session_state["conviction_meta"] = saved["meta"]
            if saved.get("selected_symbol"):
                st.session_state["selected_symbol"] = saved["selected_symbol"]
        else:
            st.session_state["conviction_tiers"] = _default_conviction_tiers()
            st.session_state["conviction_meta"] = {}
        st.session_state["conviction_loaded"] = True
    if "conviction_meta" not in st.session_state:
        st.session_state["conviction_meta"] = {}
    tiers = get_conviction_tiers()
    for sym in all_conviction_symbols(tiers):
        _ensure_conviction_meta(sym)
    _sync_flat_watchlist()


def save_conviction_tiers(tiers: dict[str, list[str]]) -> None:
    st.session_state["conviction_tiers"] = _normalize_tiers(tiers)
    _sync_flat_watchlist()
    _save_conviction_to_disk()


def _ensure_conviction_meta(symbol: str) -> dict:
    meta = st.session_state["conviction_meta"].setdefault(
        symbol,
        {"allocation_pct": 0.0, "thesis": ""},
    )
    tier = _find_symbol_tier(get_conviction_tiers(), symbol)
    if tier == "1":
        meta["allocation_pct"] = 0.0
    elif tier in CONVICTION_TIER_INFO:
        info = CONVICTION_TIER_INFO[tier]
        cap = float(info["cap"])
        current = float(meta.get("allocation_pct") or 0.0)
        if current <= 0 or current > cap:
            meta["allocation_pct"] = min(float(info["default_alloc"]), cap)
    return meta


def get_conviction_meta(symbol: str) -> dict:
    init_conviction_state()
    return _ensure_conviction_meta(symbol)


def all_conviction_symbols(tiers: dict[str, list[str]] | None = None) -> list[str]:
    if tiers is None:
        tiers = get_conviction_tiers()
    seen: set[str] = set()
    ordered: list[str] = []
    for tier_key in ("1", "2", "3"):
        for sym in tiers[tier_key]:
            if sym not in seen:
                seen.add(sym)
                ordered.append(sym)
    return ordered


def _sync_flat_watchlist() -> None:
    st.session_state["watchlist"] = all_conviction_symbols()


def _find_symbol_tier(tiers: dict[str, list[str]], symbol: str) -> str | None:
    for tier_key in ("1", "2", "3"):
        if symbol in tiers.get(tier_key, []):
            return tier_key
    return None


def _apply_tier_moves(old_tiers: dict[str, list[str]], new_tiers: dict[str, list[str]]) -> None:
    symbols = set(all_conviction_symbols()) | set(
        sym for tier in new_tiers.values() for sym in tier
    )
    for sym in symbols:
        old_tier = _find_symbol_tier(old_tiers, sym)
        new_tier = _find_symbol_tier(new_tiers, sym)
        if not new_tier or old_tier == new_tier:
            continue
        info = CONVICTION_TIER_INFO[new_tier]
        meta = get_conviction_meta(sym)
        if new_tier == "1":
            meta["allocation_pct"] = 0.0
        else:
            cap = float(info["cap"])
            current = float(meta.get("allocation_pct") or 0.0)
            if current <= 0 or current > cap:
                meta["allocation_pct"] = min(float(info["default_alloc"]), cap)
            else:
                meta["allocation_pct"] = min(current, cap)


def tier_allocation_total(tier_key: str) -> float:
    tiers = get_conviction_tiers()
    total = 0.0
    for sym in tiers.get(tier_key, []):
        total += float(get_conviction_meta(sym).get("allocation_pct") or 0.0)
    return total


def add_to_conviction(symbol: str, tier: str = "1") -> None:
    old_tiers = get_conviction_tiers()
    tiers = get_conviction_tiers()
    for key in tiers:
        tiers[key] = [s for s in tiers[key] if s != symbol]
    if symbol not in tiers[tier]:
        tiers[tier].append(symbol)
    save_conviction_tiers(tiers)
    _ensure_conviction_meta(symbol)
    _apply_tier_moves(old_tiers, tiers)


def remove_from_conviction(symbol: str) -> None:
    tiers = get_conviction_tiers()
    for tier_list in tiers.values():
        if symbol in tier_list:
            tier_list.remove(symbol)
    save_conviction_tiers(tiers)
    st.session_state.get("conviction_meta", {}).pop(symbol, None)
    if st.session_state.get("selected_symbol") == symbol:
        remaining = all_conviction_symbols(tiers)
        st.session_state["selected_symbol"] = remaining[0] if remaining else None
        _save_conviction_to_disk()


def get_watchlist() -> list[str]:
    init_conviction_state()
    return all_conviction_symbols()


def save_watchlist(symbols: list[str]) -> None:
    save_conviction_tiers({"1": list(symbols), "2": [], "3": []})


SECTOR_CONCENTRATION_LIMIT_PCT = 30.0
STOCK_CONCENTRATION_LIMIT_PCT = 10.0

MEGA_TREND_BY_SECTOR: dict[str, str] = {
    "Technology": "Digital & AI",
    "Communication Services": "Digital & AI",
    "Financial Services": "India financials",
    "Consumer Cyclical": "Consumer & discretionary",
    "Consumer Defensive": "Consumer staples",
    "Healthcare": "Healthcare & demographics",
    "Energy": "Energy & commodities",
    "Basic Materials": "Energy & commodities",
    "Industrials": "Infrastructure & capex",
    "Utilities": "Energy transition",
    "Real Estate": "Infrastructure & capex",
}

INDUSTRY_MEGA_TREND_KEYWORDS: list[tuple[list[str], str]] = [
    (["renewable", "solar", "wind", "green hydrogen", "ev ", "electric vehicle"], "Energy transition"),
    (["software", "it services", "information technology", "cloud", "digital"], "Digital & AI"),
    (["bank", "nbfc", "insurance", "lending", "finance"], "India financials"),
    (["pharma", "hospital", "health", "biotech"], "Healthcare & demographics"),
    (["infrastructure", "construction", "engineering", "capital goods"], "Infrastructure & capex"),
    (["metal", "mining", "steel", "aluminium", "chemical"], "Energy & commodities"),
    (["fmcg", "consumer", "retail", "apparel"], "Consumer staples"),
]


def infer_mega_trend(data: dict) -> str:
    industry = (data.get("industry") or "").lower()
    for keywords, tag in INDUSTRY_MEGA_TREND_KEYWORDS:
        if any(kw in industry for kw in keywords):
            return tag
    sector = (data.get("sector") or "").strip()
    return MEGA_TREND_BY_SECTOR.get(sector, "Diversified / other")


def build_portfolio_holdings() -> list[dict]:
    holdings: list[dict] = []
    # Use actual holdings data instead of conviction tiers
    current_holdings = get_holdings()

    if not current_holdings:
        # Fallback to conviction tiers with allocation if no holdings exist
        for sym in all_conviction_symbols():
            meta = get_conviction_meta(sym)
            alloc = float(meta.get("allocation_pct") or 0.0)
            if alloc <= 0:
                continue
            data = fetch_stock_data(sym)
            short = sym.removesuffix(NSE_SUFFIX)
            holdings.append(
                {
                    "symbol": sym,
                    "short_label": short,
                    "name": data.get("name") or short,
                    "allocation_pct": alloc,
                    "sector": data.get("sector") or "Unknown",
                    "mega_trend": infer_mega_trend(data),
                    "history_1y": data.get("history_1y"),
                }
            )
    else:
        # Build holdings from actual positions
        total_invested = 0.0
        for holding in current_holdings:
            qty = holding["quantity"]
            purchase_price = holding["purchase_price"]
            invested = qty * purchase_price
            total_invested += invested

        for holding in current_holdings:
            sym = holding["symbol"]
            qty = holding["quantity"]
            purchase_price = holding["purchase_price"]
            invested = qty * purchase_price
            data = fetch_stock_data(sym)
            short = sym.removesuffix(NSE_SUFFIX)
            # Calculate allocation percentage based on invested amount
            alloc_pct = (invested / total_invested * 100) if total_invested > 0 else 0
            holdings.append(
                {
                    "symbol": sym,
                    "short_label": short,
                    "name": data.get("name") or short,
                    "allocation_pct": alloc_pct,
                    "sector": data.get("sector") or "Unknown",
                    "mega_trend": infer_mega_trend(data),
                    "history_1y": data.get("history_1y"),
                }
            )
    return holdings


def _price_return_correlation(
    hist_a: pd.DataFrame | None, hist_b: pd.DataFrame | None
) -> float | None:
    if (
        hist_a is None
        or hist_b is None
        or hist_a.empty
        or hist_b.empty
        or "Close" not in hist_a.columns
        or "Close" not in hist_b.columns
    ):
        return None

    a = hist_a[["Date", "Close"]].copy()
    b = hist_b[["Date", "Close"]].copy()
    a["Date"] = pd.to_datetime(a["Date"])
    b["Date"] = pd.to_datetime(b["Date"])
    merged = pd.merge(a, b, on="Date", suffixes=("_a", "_b"))
    if len(merged) < 20:
        return None
    ret_a = merged["Close_a"].pct_change()
    ret_b = merged["Close_b"].pct_change()
    corr = ret_a.corr(ret_b)
    if corr is None or pd.isna(corr):
        return None
    return float(max(-1.0, min(1.0, corr)))


def _proxy_correlation(hold_a: dict, hold_b: dict) -> float:
    score = 0.12
    sector_a = (hold_a.get("sector") or "").strip()
    sector_b = (hold_b.get("sector") or "").strip()
    if sector_a and sector_a == sector_b:
        score += 0.52
    trend_a = hold_a.get("mega_trend") or ""
    trend_b = hold_b.get("mega_trend") or ""
    if trend_a and trend_a == trend_b:
        score += 0.28
    elif trend_a and trend_b and trend_a.split()[0] == trend_b.split()[0]:
        score += 0.12
    return float(min(0.92, score))


def build_correlation_matrix(holdings: list[dict]) -> tuple[pd.DataFrame, pd.DataFrame]:
    labels = [h["short_label"] for h in holdings]
    n = len(labels)
    corr = pd.DataFrame(1.0, index=labels, columns=labels)
    methods = pd.DataFrame("—", index=labels, columns=labels)

    for i in range(n):
        for j in range(i + 1, n):
            live = _price_return_correlation(
                holdings[i].get("history_1y"), holdings[j].get("history_1y")
            )
            if live is not None:
                value, method = live, "price"
            else:
                value, method = _proxy_correlation(holdings[i], holdings[j]), "proxy"
            corr.iloc[i, j] = corr.iloc[j, i] = value
            methods.iloc[i, j] = methods.iloc[j, i] = method

    return corr, methods


def _allocation_weights(holdings: list[dict]) -> dict[str, float]:
    total = sum(h["allocation_pct"] for h in holdings)
    if total <= 0:
        equal = 100.0 / len(holdings)
        return {h["symbol"]: equal for h in holdings}
    return {h["symbol"]: (h["allocation_pct"] / total) * 100.0 for h in holdings}


def render_concentration_warnings(holdings: list[dict]) -> None:
    weights = _allocation_weights(holdings)
    sector_totals: dict[str, float] = {}
    for hold in holdings:
        sector = hold["sector"]
        sector_totals[sector] = sector_totals.get(sector, 0.0) + weights[hold["symbol"]]

    warnings: list[str] = []
    for sector, pct in sorted(sector_totals.items(), key=lambda x: -x[1]):
        if pct > SECTOR_CONCENTRATION_LIMIT_PCT:
            warnings.append(
                f"**Sector concentration:** {sector} is **{pct:.1f}%** of the portfolio "
                f"(limit {SECTOR_CONCENTRATION_LIMIT_PCT:.0f}%)."
            )

    for hold in holdings:
        pct = weights[hold["symbol"]]
        if pct > STOCK_CONCENTRATION_LIMIT_PCT:
            warnings.append(
                f"**Single-name risk:** {hold['short_label']} is **{pct:.1f}%** "
                f"(limit {STOCK_CONCENTRATION_LIMIT_PCT:.0f}%)."
            )

    if warnings:
        render_section_header("Concentration risk")
        for msg in warnings:
            st.warning(msg)
    else:
        st.success(
            "No concentration flags — no sector above "
            f"{SECTOR_CONCENTRATION_LIMIT_PCT:.0f}% and no single stock above "
            f"{STOCK_CONCENTRATION_LIMIT_PCT:.0f}%."
        )


def render_correlation_heatmap(holdings: list[dict]) -> None:
    render_section_header("Correlation grid", "Live returns or sector / mega-trend proxy.")
    if len(holdings) < 2:
        st.info("Need at least two held positions to show correlations.")
        return

    corr, methods = build_correlation_matrix(holdings)
    live_pairs = int((methods.values == "price").sum() / 2)
    proxy_pairs = int((methods.values == "proxy").sum() / 2)
    st.caption(
        f"Uses 1Y daily return correlation when data is available ({live_pairs} pair(s)); "
        f"otherwise estimates from **sector + mega-trend** overlap ({proxy_pairs} pair(s))."
    )

    hover = corr.copy().astype(str)
    for i in corr.index:
        for j in corr.columns:
            method = methods.loc[i, j]
            if i == j:
                hover.loc[i, j] = "1.00 (same stock)"
            elif method == "price":
                hover.loc[i, j] = f"{corr.loc[i, j]:.2f} (live returns)"
            else:
                hover.loc[i, j] = f"{corr.loc[i, j]:.2f} (sector/trend proxy)"

    fig = px.imshow(
        corr,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        labels=dict(color="Correlation"),
    )
    apply_chart_theme(fig, height=max(280, 52 * len(holdings)), title="Pairwise correlation")
    fig.update_traces(customdata=hover.values, hovertemplate="%{x} vs %{y}<br>%{customdata}<extra></extra>")
    st.plotly_chart(fig, use_container_width=True)


def _donut_figure(df: pd.DataFrame, names_col: str, title: str):
    fig = px.pie(
        df,
        names=names_col,
        values="weight",
        hole=0.48,
        title=title,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    apply_chart_theme(fig, height=320, title=title)
    fig.update_layout(showlegend=False)
    return fig


def render_portfolio_donuts(holdings: list[dict]) -> None:
    render_section_header("Portfolio mix", "Weighted by your allocation percentages.")
    weights = _allocation_weights(holdings)

    sector_rows: dict[str, float] = {}
    trend_rows: dict[str, float] = {}
    for hold in holdings:
        w = weights[hold["symbol"]]
        sector_rows[hold["sector"]] = sector_rows.get(hold["sector"], 0.0) + w
        trend_rows[hold["mega_trend"]] = trend_rows.get(hold["mega_trend"], 0.0) + w

    sector_df = pd.DataFrame(
        [{"sector": k, "weight": v} for k, v in sector_rows.items()]
    ).sort_values("weight", ascending=False)
    trend_df = pd.DataFrame(
        [{"mega_trend": k, "weight": v} for k, v in trend_rows.items()]
    ).sort_values("weight", ascending=False)

    st.plotly_chart(
        _donut_figure(sector_df, "sector", "By sector"),
        use_container_width=True,
    )
    st.plotly_chart(
        _donut_figure(trend_df, "mega_trend", "By mega-trend"),
        use_container_width=True,
    )


def render_portfolio_health_tab() -> None:
    render_section_header(
        "Portfolio Health",
        "Concentration, correlation, and sector mix for positions with allocation % set.",
    )

    with st.spinner("Loading held positions and market data…"):
        holdings = build_portfolio_holdings()

    if not holdings:
        st.warning(
            "No held positions yet. Assign **allocation %** to stocks in Tier 2 (Starter) "
            "or Tier 3 (High conviction) in the sidebar to populate this view."
        )
        preview = [s for s in all_conviction_symbols()]
        if preview:
            st.markdown(
                '<p class="section-sub">On watchlist (no allocation): '
                + ", ".join(s.removesuffix(NSE_SUFFIX) for s in preview)
                + "</p>",
                unsafe_allow_html=True,
            )
        return

    total_alloc = sum(h["allocation_pct"] for h in holdings)
    h1, h2 = st.columns(2)
    h1.metric("Held positions", len(holdings))
    h2.metric("Total modeled allocation", f"{total_alloc:.1f}%")

    render_concentration_warnings(holdings)
    col_left, col_right = st.columns([1.25, 1])
    with col_left:
        render_correlation_heatmap(holdings)
    with col_right:
        render_portfolio_donuts(holdings)

    with st.expander("Position detail", expanded=False):
        detail = pd.DataFrame(
            [
                {
                    "Ticker": h["short_label"],
                    "Allocation %": h["allocation_pct"],
                    "Sector": h["sector"],
                    "Mega-trend": h["mega_trend"],
                }
                for h in holdings
            ]
        )
        st.dataframe(detail, use_container_width=True, hide_index=True)


def _mapping_get(mapping, *keys, default=None):
    if mapping is None:
        return default
    for key in keys:
        try:
            if isinstance(mapping, dict) and key in mapping:
                value = mapping[key]
            elif hasattr(mapping, "get"):
                value = mapping.get(key)
            else:
                value = getattr(mapping, key, None)
            if value is not None:
                return value
        except Exception:
            continue
    return default


def _safe_float(value) -> float | None:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except Exception:
        pass
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_ticker_news(raw_news: list) -> list[dict]:
    items = []
    for entry in (raw_news or [])[:6]:
        if not isinstance(entry, dict):
            continue

        content = entry.get("content") if isinstance(entry.get("content"), dict) else {}
        title = (
            content.get("title")
            or entry.get("title")
            or entry.get("headline")
        )
        link = entry.get("link")
        if not link and isinstance(content.get("canonicalUrl"), dict):
            link = content["canonicalUrl"].get("url")
        if not link and isinstance(content.get("clickThroughUrl"), dict):
            link = content["clickThroughUrl"].get("url")
        if not link:
            link = content.get("url")

        publisher = entry.get("publisher")
        if not publisher and isinstance(content.get("provider"), dict):
            publisher = content["provider"].get("displayName")

        snippet = (
            content.get("description")
            or content.get("summary")
            or entry.get("summary")
            or ""
        )
        if isinstance(snippet, str):
            snippet = _strip_html(snippet)[:500]

        items.append(
            {
                "title": title or "Untitled",
                "link": link or "",
                "publisher": publisher,
                "snippet": snippet,
            }
        )
    return items


def _strip_html(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", cleaned).strip()


@st.cache_data(ttl=600)
def fetch_google_news_stories(stock_name: str, limit: int = 8) -> list[dict]:
    query = urllib.parse.quote_plus(f"{stock_name} stock")
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(rss_url)
    items = []
    for entry in (feed.entries or [])[:limit]:
        source = entry.get("source")
        publisher = source.get("title") if isinstance(source, dict) else None
        items.append(
            {
                "title": getattr(entry, "title", "Untitled"),
                "link": getattr(entry, "link", ""),
                "publisher": publisher,
                "snippet": _strip_html(getattr(entry, "summary", ""))[:500],
            }
        )
    return items


def merge_news_sources(*sources: list[dict]) -> list[dict]:
    merged: list[dict] = []
    seen: set[str] = set()
    for batch in sources:
        for item in batch or []:
            title = (item.get("title") or "").strip()
            if not title:
                continue
            key = re.sub(r"[^a-z0-9]", "", title.lower())[:96]
            if key in seen:
                continue
            seen.add(key)
            merged.append(item)
    return merged[:8]


NEWS_THEMES = {
    "earnings & results": ["earnings", "profit", "revenue", "quarter", "results", "ebitda", "margin"],
    "orders & growth": ["order", "contract", "expansion", "growth", "capex", "capacity"],
    "regulatory risk": ["sebi", "regulator", "probe", "investigation", "penalty", "fine", "compliance"],
    "management & strategy": ["ceo", "md", "board", "restructuring", "merger", "acquisition", "stake"],
    "sector & macro": ["sector", "industry", "policy", "budget", "rates", "inflation", "crude"],
    "analyst action": ["upgrade", "downgrade", "target", "rating", "initiate", "outperform", "underperform"],
}


def generate_news_decision_summary(
    stock_name: str,
    news_items: list[dict],
    *,
    day_change_pct: float | None = None,
    position_52w: float | None = None,
) -> tuple[str, list[str]]:
    if not news_items:
        return (
            f"No recent headlines were found for {stock_name}. Recheck the ticker or refresh in a minute.",
            ["Wait for fresher headlines before making a news-driven decision."],
        )

    bullish_words = {
        "surge", "rally", "gain", "gains", "strong", "beats", "upgrade", "growth",
        "record", "bullish", "profit", "profits", "outperform", "buy", "jump", "soar",
    }
    bearish_words = {
        "fall", "falls", "drop", "drops", "weak", "miss", "downgrade", "loss", "losses",
        "concern", "bearish", "sell", "underperform", "decline", "slump", "cut",
    }

    pos_score = 0
    neg_score = 0
    story_lines: list[str] = []
    combined_text = ""

    for item in news_items:
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        blob = f"{title}. {snippet}".lower()
        combined_text += f" {blob}"
        story_lines.append(title)
        pos_score += sum(1 for w in bullish_words if w in blob)
        neg_score += sum(1 for w in bearish_words if w in blob)

    if pos_score > neg_score * 1.2:
        tone = "positive"
    elif neg_score > pos_score * 1.2:
        tone = "negative"
    else:
        tone = "mixed"

    active_themes = [
        label for label, keywords in NEWS_THEMES.items() if any(k in combined_text for k in keywords)
    ]

    headline_sample = "; ".join(story_lines[:3])
    summary = (
        f"Reviewing {len(news_items)} recent stories on **{stock_name}**, the news flow looks "
        f"**{tone}**. Headlines cluster around "
        f"{', '.join(active_themes[:3]) if active_themes else 'general market chatter'}."
    )

    if tone == "positive":
        summary += (
            " Reports highlight constructive triggers such as growth, beats, or favourable analyst action."
        )
    elif tone == "negative":
        summary += (
            " Coverage flags pressure from misses, downgrades, regulatory worries, or demand concerns."
        )
    else:
        summary += " Bullish and bearish headlines are balanced, so conviction should come from price action."

    if day_change_pct is not None:
        if day_change_pct > 0 and tone == "positive":
            summary += f" Today's +{day_change_pct:.2f}% move aligns with the headline tone."
        elif day_change_pct < 0 and tone == "negative":
            summary += f" Today's {day_change_pct:.2f}% move aligns with the headline tone."
        elif day_change_pct > 0 and tone == "negative":
            summary += (
                f" Despite today's +{day_change_pct:.2f}% move, headlines still lean cautious — treat the bounce as fragile."
            )
        elif day_change_pct < 0 and tone == "positive":
            summary += (
                f" Headlines are constructive but price is down {day_change_pct:.2f}% today — wait for confirmation."
            )

    if position_52w is not None:
        if position_52w >= 75:
            summary += " Price is near its 52-week highs, so good news may already be partly priced in."
        elif position_52w <= 25:
            summary += " Price is near its 52-week lows, so negative headlines may already be discounted."

    takeaways: list[str] = []
    if active_themes:
        takeaways.append(f"Main themes to watch: {', '.join(active_themes[:3])}.")
    takeaways.append(f"Sample headlines: {headline_sample}.")
    if tone == "positive":
        takeaways.append("Decision lean: favourable news supports holding/adding only if valuation still looks reasonable.")
    elif tone == "negative":
        takeaways.append("Decision lean: consider trimming risk or waiting for clarity before adding exposure.")
    else:
        takeaways.append("Decision lean: stay selective — let the next earnings or sector datapoint break the tie.")

    return summary, takeaways[:3]


DARK_HORSE_WEIGHTS = {
    "fcf_yield": 0.20,
    "revenue_cagr": 0.15,
    "analyst_inverse": 0.10,
    "inst_inverse": 0.10,
    "insider_ratio": 0.10,
    "gm_trend": 0.10,
    "pe_ratio": 0.15,
    "operating_cashflow": 0.10,
}

SECTOR_FCF_PEERS: dict[str, list[str]] = {
    "Technology": ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS"],
    "Financial Services": ["HDFCBANK.NS", "ICICIBANK.NS", "KOTAKBANK.NS", "AXISBANK.NS", "SBIN.NS"],
    "Energy": ["RELIANCE.NS", "ONGC.NS", "NTPC.NS", "BPCL.NS", "GAIL.NS"],
    "Consumer Defensive": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS", "DABUR.NS"],
    "Consumer Cyclical": ["TITAN.NS", "MARUTI.NS", "TATAMOTORS.NS", "M&M.NS", "BAJAJ-AUTO.NS"],
    "Healthcare": ["SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "DIVISLAB.NS", "APOLLOHOSP.NS"],
    "Industrials": ["LT.NS", "HAL.NS", "BEL.NS", "SIEMENS.NS", "ABB.NS"],
    "Basic Materials": ["TATASTEEL.NS", "HINDALCO.NS", "JSWSTEEL.NS", "VEDL.NS", "COALINDIA.NS"],
    "Communication Services": ["BHARTIARTL.NS", "IDEA.NS", "INDIGO.NS", "ZEEL.NS", "PVRINOX.NS"],
    "Utilities": ["NTPC.NS", "POWERGRID.NS", "ADANIGREEN.NS", "TATAPOWER.NS", "TORNTPOWER.NS"],
}
DEFAULT_FCF_PEERS = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ITC.NS", "LT.NS"]


def _scale_linear(value: float, low: float, high: float) -> float:
    if high <= low:
        return 50.0
    pct = (value - low) / (high - low) * 100
    return float(max(0.0, min(100.0, pct)))


def _fcf_yield_from_info(info: dict) -> float | None:
    fcf = _safe_float(info.get("freeCashflow"))
    mcap = _safe_float(info.get("marketCap"))
    if fcf is None or mcap in (None, 0):
        return None
    return fcf / mcap


@st.cache_data(ttl=86400)
def get_sector_median_fcf_yield(sector: str | None) -> float:
    peers = SECTOR_FCF_PEERS.get(sector or "", DEFAULT_FCF_PEERS)
    yields: list[float] = []
    for peer in peers:
        try:
            peer_info = yf.Ticker(peer).info or {}
            yld = _fcf_yield_from_info(peer_info)
            if yld is not None:
                yields.append(yld)
        except Exception:
            continue
    if yields:
        return float(statistics.median(yields))
    return 0.04


def _revenue_cagr_3y(ticker: yf.Ticker, info: dict) -> tuple[float | None, str]:
    try:
        financials = ticker.financials
        if financials is not None and not financials.empty:
            revenue_row = None
            for label in ("Total Revenue", "Revenue", "Operating Revenue"):
                if label in financials.index:
                    revenue_row = financials.loc[label]
                    break
            if revenue_row is not None:
                series = pd.to_numeric(revenue_row, errors="coerce").dropna().sort_index()
                if len(series) >= 2:
                    start = float(series.iloc[0])
                    end = float(series.iloc[-1])
                    years = max(len(series) - 1, 1)
                    if start > 0 and end > 0:
                        cagr = ((end / start) ** (1 / years) - 1) * 100
                        return cagr, f"{cagr:.1f}% 3yr revenue CAGR (financials)"
    except Exception:
        pass

    growth = _safe_float(info.get("revenueGrowth"))
    if growth is not None:
        if abs(growth) <= 1:
            growth *= 100
        return growth, f"{growth:.1f}% revenue growth (latest YoY proxy)"
    return None, "Revenue growth unavailable"


def _insider_buy_sell_ratio_6m(ticker: yf.Ticker) -> tuple[float | None, str]:
    try:
        tx = ticker.insider_transactions
        if tx is None or tx.empty:
            return None, "No insider transaction data"
        df = tx.copy()
        if "Start Date" in df.columns:
            df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce")
            cutoff = datetime.now() - timedelta(days=183)
            df = df[df["Start Date"] >= cutoff]
        buys = 0.0
        sells = 0.0
        text_col = next((c for c in df.columns if "Text" in c or "Transaction" in c), None)
        shares_col = next((c for c in df.columns if "Shares" in c or "Value" in c), None)
        for _, row in df.iterrows():
            label = str(row.get(text_col, "")).lower() if text_col else ""
            qty = abs(_safe_float(row.get(shares_col)) or 0) if shares_col else 1.0
            if "buy" in label or "purchase" in label:
                buys += qty
            elif "sale" in label or "sell" in label:
                sells += qty
        if buys == 0 and sells == 0:
            return None, "No classified insider trades in last 6mo"
        if sells == 0:
            return 3.0, f"Insider buy/sell ratio {buys:.0f}:{sells:.0f} (6mo)"
        ratio = buys / sells
        return ratio, f"Insider buy/sell ratio {ratio:.2f} (6mo)"
    except Exception:
        return None, "Insider activity unavailable"


def _gross_margin_trend(ticker: yf.Ticker, info: dict) -> tuple[float | None, str]:
    try:
        financials = ticker.financials
        if financials is not None and not financials.empty:
            gp_row = next((financials.loc[r] for r in financials.index if "Gross Profit" in str(r)), None)
            rev_row = None
            for label in ("Total Revenue", "Revenue", "Operating Revenue"):
                if label in financials.index:
                    rev_row = financials.loc[label]
                    break
            if gp_row is not None and rev_row is not None:
                gp = pd.to_numeric(gp_row, errors="coerce").dropna().sort_index()
                rev = pd.to_numeric(rev_row, errors="coerce").dropna().sort_index()
                if len(gp) >= 2 and len(rev) >= 2:
                    margin_old = float(gp.iloc[0]) / float(rev.iloc[0]) if rev.iloc[0] else None
                    margin_new = float(gp.iloc[-1]) / float(rev.iloc[-1]) if rev.iloc[-1] else None
                    if margin_old and margin_new is not None:
                        change_pp = (margin_new - margin_old) * 100
                        return change_pp, f"Gross margin change {change_pp:+.1f}pp (multi-year)"
    except Exception:
        pass
    gm = _safe_float(info.get("grossMargins"))
    if gm is not None:
        gm_pct = gm * 100 if abs(gm) <= 1 else gm
        return gm_pct, f"Gross margin level {gm_pct:.1f}% (snapshot)"
    return None, "Gross margin trend unavailable"


def compute_dark_horse_score(sym: str, info: dict, ticker: yf.Ticker) -> dict:
    components: dict[str, dict] = {}
    weighted_total = 0.0
    weight_used = 0.0

    sector = info.get("sector")
    fcf_yield = _fcf_yield_from_info(info)
    sector_median = get_sector_median_fcf_yield(sector)
    if fcf_yield is not None and sector_median > 0:
        relative = fcf_yield / sector_median
        comp_score = _scale_linear(relative, 0.5, 2.0)
        detail = f"FCF yield {fcf_yield*100:.2f}% vs sector median {sector_median*100:.2f}%"
    else:
        comp_score = 50.0
        detail = "FCF yield vs sector median unavailable"
    components["fcf_yield"] = {"score": comp_score, "weight_pct": 25, "detail": detail}
    weighted_total += comp_score * DARK_HORSE_WEIGHTS["fcf_yield"]
    weight_used += DARK_HORSE_WEIGHTS["fcf_yield"]

    rev_growth, rev_detail = _revenue_cagr_3y(ticker, info)
    if rev_growth is not None:
        comp_score = _scale_linear(rev_growth, -5, 25)
    else:
        comp_score = 50.0
    components["revenue_cagr"] = {"score": comp_score, "weight_pct": 20, "detail": rev_detail}
    weighted_total += comp_score * DARK_HORSE_WEIGHTS["revenue_cagr"]
    weight_used += DARK_HORSE_WEIGHTS["revenue_cagr"]

    analysts = _safe_float(info.get("numberOfAnalystOpinions"))
    if analysts is not None:
        comp_score = _scale_linear(30 - analysts, 0, 30)
        detail = f"{int(analysts)} analysts (fewer coverage = higher dark-horse score)"
    else:
        comp_score = 50.0
        detail = "Analyst coverage count unavailable"
    components["analyst_inverse"] = {"score": comp_score, "weight_pct": 15, "detail": detail}
    weighted_total += comp_score * DARK_HORSE_WEIGHTS["analyst_inverse"]
    weight_used += DARK_HORSE_WEIGHTS["analyst_inverse"]

    inst = _safe_float(info.get("heldPercentInstitutions"))
    if inst is not None:
        inst_pct = inst * 100 if inst <= 1 else inst
        comp_score = _scale_linear(80 - inst_pct, 0, 80)
        detail = f"{inst_pct:.1f}% institutional ownership (lower = higher score)"
    else:
        comp_score = 50.0
        detail = "Institutional ownership unavailable"
    components["inst_inverse"] = {"score": comp_score, "weight_pct": 15, "detail": detail}
    weighted_total += comp_score * DARK_HORSE_WEIGHTS["inst_inverse"]
    weight_used += DARK_HORSE_WEIGHTS["inst_inverse"]

    insider_ratio, insider_detail = _insider_buy_sell_ratio_6m(ticker)
    if insider_ratio is not None:
        comp_score = _scale_linear(insider_ratio, 0.3, 2.5)
    else:
        comp_score = 50.0
    components["insider_ratio"] = {"score": comp_score, "weight_pct": 15, "detail": insider_detail}
    weighted_total += comp_score * DARK_HORSE_WEIGHTS["insider_ratio"]
    weight_used += DARK_HORSE_WEIGHTS["insider_ratio"]

    gm_change, gm_detail = _gross_margin_trend(ticker, info)
    if gm_change is not None:
        if "snapshot" in gm_detail.lower():
            comp_score = _scale_linear(gm_change, 15, 55)
        else:
            comp_score = _scale_linear(gm_change, -5, 10)
    else:
        comp_score = 50.0
    components["gm_trend"] = {"score": comp_score, "weight_pct": 10, "detail": gm_detail}
    weighted_total += comp_score * DARK_HORSE_WEIGHTS["gm_trend"]
    weight_used += DARK_HORSE_WEIGHTS["gm_trend"]

    # P/E ratio component - lower P/E is generally better for value
    pe_ratio = _safe_float(info.get("trailingPE") or info.get("forwardPE"))
    if pe_ratio is not None and pe_ratio > 0:
        comp_score = _scale_linear(50 - pe_ratio, 0, 50)
        detail = f"P/E ratio {pe_ratio:.2f} (lower = higher score)"
    else:
        comp_score = 50.0
        detail = "P/E ratio unavailable"
    components["pe_ratio"] = {"score": comp_score, "weight_pct": 15, "detail": detail}
    weighted_total += comp_score * DARK_HORSE_WEIGHTS["pe_ratio"]
    weight_used += DARK_HORSE_WEIGHTS["pe_ratio"]

    # Operating cash flow component - higher is better
    ocf = _safe_float(info.get("operatingCashflow"))
    mcap = _safe_float(info.get("marketCap"))
    if ocf is not None and mcap is not None and mcap > 0:
        ocf_yield = ocf / mcap
        comp_score = _scale_linear(ocf_yield * 100, 0, 15)
        detail = f"Operating cash flow yield {ocf_yield*100:.2f}%"
    else:
        comp_score = 50.0
        detail = "Operating cash flow unavailable"
    components["operating_cashflow"] = {"score": comp_score, "weight_pct": 10, "detail": detail}
    weighted_total += comp_score * DARK_HORSE_WEIGHTS["operating_cashflow"]
    weight_used += DARK_HORSE_WEIGHTS["operating_cashflow"]

    final_score = weighted_total / weight_used if weight_used else 50.0
    if final_score >= 70:
        tier = "green"
    elif final_score >= 45:
        tier = "amber"
    else:
        tier = "red"

    breakdown_lines = [
        f"FCF yield (20%): {components['fcf_yield']['score']:.0f}/100 — {components['fcf_yield']['detail']}",
        f"Revenue growth (15%): {components['revenue_cagr']['score']:.0f}/100 — {components['revenue_cagr']['detail']}",
        f"Analyst coverage ↓ (10%): {components['analyst_inverse']['score']:.0f}/100 — {components['analyst_inverse']['detail']}",
        f"Institutional own. ↓ (10%): {components['inst_inverse']['score']:.0f}/100 — {components['inst_inverse']['detail']}",
        f"Insider buy/sell (10%): {components['insider_ratio']['score']:.0f}/100 — {components['insider_ratio']['detail']}",
        f"Gross margin trend (10%): {components['gm_trend']['score']:.0f}/100 — {components['gm_trend']['detail']}",
        f"P/E ratio (15%): {components['pe_ratio']['score']:.0f}/100 — {components['pe_ratio']['detail']}",
        f"Operating cash flow (10%): {components['operating_cashflow']['score']:.0f}/100 — {components['operating_cashflow']['detail']}",
    ]

    return {
        "score": round(final_score, 1),
        "tier": tier,
        "components": components,
        "breakdown_lines": breakdown_lines,
    }


def _tiers_changed(
    before: dict[str, list[str]], after: dict[str, list[str]]
) -> bool:
    for key in ("1", "2", "3"):
        if list(before.get(key, [])) != list(after.get(key, [])):
            return True
    return False


def _move_symbol_to_tier(symbol: str, to_tier: str) -> None:
    old_tiers = get_conviction_tiers()
    new_tiers = {k: list(v) for k, v in old_tiers.items()}
    for key in new_tiers:
        new_tiers[key] = [s for s in new_tiers[key] if s != symbol]
    if symbol not in new_tiers[to_tier]:
        new_tiers[to_tier].append(symbol)
    _apply_tier_moves(old_tiers, new_tiers)
    save_conviction_tiers(new_tiers)


def render_conviction_tier_board(tiers: dict[str, list[str]]) -> None:
    """Native Streamlit tier board (reliable vs custom iframe component)."""
    tier_order = ("1", "2", "3")
    for tier_key in tier_order:
        info = CONVICTION_TIER_INFO[tier_key]
        symbols = tiers.get(tier_key, [])
        st.sidebar.markdown(
            f"**{info['name']}** · <span style='color:#94a3b8;font-size:0.75rem'>"
            f"{info['hint']}</span>",
            unsafe_allow_html=True,
        )
        if not symbols:
            st.sidebar.caption("No stocks in this tier")
            continue
        for sym in symbols:
            label = sym.removesuffix(NSE_SUFFIX)
            selected = sym == st.session_state.get("selected_symbol")
            chip_cls = "conviction-chip conviction-chip-selected" if selected else "conviction-chip"
            st.sidebar.markdown(
                f'<div class="{chip_cls}">{label}</div>',
                unsafe_allow_html=True,
            )
            open_col, tier_col, rm_col = st.sidebar.columns([2, 2.2, 1])
            with open_col:
                if st.button("Open", key=f"tier_open_{sym}", use_container_width=True):
                    st.session_state["selected_symbol"] = sym
                    st.rerun()
            with tier_col:
                move_to = st.selectbox(
                    "Move to",
                    options=tier_order,
                    index=tier_order.index(tier_key),
                    format_func=lambda t: CONVICTION_TIER_INFO[t]["name"],
                    key=f"tier_move_{sym}",
                    label_visibility="collapsed",
                )
                if move_to != tier_key:
                    _move_symbol_to_tier(sym, move_to)
                    st.rerun()
            with rm_col:
                if st.button("×", key=f"tier_rm_{sym}"):
                    remove_from_conviction(sym)
                    if st.session_state.get("selected_symbol") == sym:
                        remaining = all_conviction_symbols()
                        st.session_state["selected_symbol"] = (
                            remaining[0] if remaining else None
                        )
                    st.rerun()


# Sector stock lists for top stocks display
SECTOR_STOCKS = {
    "💻 IT & AI": [
        "TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "LTIM.NS", "TECHM.NS", "MPHASIS.NS", "COFORGE.NS"
    ],
    "⚡ Renewables": [
        "TATAPOWER.NS", "ADANIGREEN.NS", "RENUKA.NS", "SJVN.NS", "NHPC.NS", "NTPC.NS", "POWERGRID.NS"
    ],
    "💊 Pharma": [
        "SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "AUROPHARMA.NS", "DIVISLAB.NS", "LUPIN.NS", "TORNTPHARM.NS"
    ],
    "🛡️ Defence": [
        "HAL.NS", "BEL.NS", "MIDHANI.NS", "BHEL.NS", "BEML.NS", "Mazagon.NS", "GRSE.NS"
    ],
    "🏦 BFSI": [
        "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS", "BAJFINANCE.NS", "CHOLAFIN.NS"
    ]
}


@st.cache_data(ttl=604800)  # Cache for 7 days (1 week)
def fetch_sector_stocks_data() -> dict:
    """Fetch and cache sector stocks data for 1 week."""
    sector_data_dict = {}
    for sector, stocks in SECTOR_STOCKS.items():
        sector_data = []
        for sym in stocks[:4]:  # Get top 4 stocks
            try:
                ticker = yf.Ticker(sym)
                info = ticker.info or {}
                current_price = _safe_float(info.get("currentPrice") or info.get("regularMarketPrice"))
                pe = _safe_float(info.get("trailingPE") or info.get("forwardPE"))
                market_cap = _safe_float(info.get("marketCap"))
                
                # Calculate 1-week change
                change_1w = None
                try:
                    hist = ticker.history(period="1w")
                    if len(hist) >= 2:
                        start_price = hist['Close'].iloc[0]
                        end_price = hist['Close'].iloc[-1]
                        change_1w = ((end_price - start_price) / start_price) * 100
                except:
                    pass
                
                if current_price:
                    sector_data.append({
                        "symbol": sym,
                        "name": sym.removesuffix(NSE_SUFFIX),
                        "price": current_price,
                        "pe": pe,
                        "market_cap": market_cap,
                        "change_1w": change_1w
                    })
            except Exception:
                pass
        
        # Sort by market cap (descending) and keep top 4
        sector_data.sort(key=lambda x: x["market_cap"] or 0, reverse=True)
        sector_data_dict[sector] = sector_data[:4]
    
    return sector_data_dict


def render_sector_stocks() -> None:
    """Display top 4 stocks from each sector with key metrics in compact format."""
    sector_data_dict = fetch_sector_stocks_data()
    
    for sector, stocks in sector_data_dict.items():
        # Sector header
        st.sidebar.markdown(f"**{sector}**")
        
        # Display each stock with metrics in pipe-separated format
        for stock in stocks:
            pe_str = f"PE {stock['pe']:.1f}" if stock['pe'] else "PE -"
            change_str = f"{stock['change_1w']:+.1f}%" if stock['change_1w'] is not None else "-"
            
            # Single line with pipe-separated format including button
            stock_line = f"{stock['name']} || ₹{stock['price']:.0f} || {pe_str} || {change_str}"
            
            # Display line with inline button
            if st.sidebar.button(f"{stock_line} 📊", key=f"sector_open_{stock['symbol']}", help=f"Open {stock['name']}", use_container_width=True):
                st.session_state["selected_symbol"] = stock['symbol']
                st.rerun()
        
        st.sidebar.markdown("---")

def render_dark_horse_badge(data: dict) -> None:
    dh = data.get("dark_horse")
    if not dh or dh.get("score") is None:
        st.markdown(
            '<span class="dh-badge dh-amber" title="Insufficient data for Dark Horse score">Dark Horse N/A</span>',
            unsafe_allow_html=True,
        )
        return

    score = dh["score"]
    tier = dh.get("tier", "amber")
    tooltip_html = "<br/>".join(dh.get("breakdown_lines", []))
    st.markdown(
        f"""
        <div class="dh-wrap">
            <span class="dh-badge dh-{tier}">Dark Horse {score:.0f}</span>
            <div class="dh-tooltip">
                <strong>Score breakdown (0–100)</strong><br/>
                {tooltip_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(ttl=300)
def _sp500_1y_return_pct() -> float | None:
    try:
        hist = yf.Ticker(SP500_SYMBOL).history(period="1y")
        if hist is None or hist.empty or len(hist) < 2:
            return None
        start = float(hist["Close"].iloc[0])
        end = float(hist["Close"].iloc[-1])
        if start <= 0:
            return None
        return ((end / start) - 1.0) * 100.0
    except Exception:
        return None


def _compute_rs_vs_sp500(history_1y: pd.DataFrame) -> float | None:
    if history_1y is None or history_1y.empty or len(history_1y) < 2:
        return None
    stock_start = float(history_1y["Close"].iloc[0])
    stock_end = float(history_1y["Close"].iloc[-1])
    if stock_start <= 0:
        return None
    stock_ret = ((stock_end / stock_start) - 1.0) * 100.0
    sp_ret = _sp500_1y_return_pct()
    if sp_ret is None:
        return None
    return stock_ret - sp_ret


def _compute_ath_metrics(
    ticker: yf.Ticker, info: dict, current_price: float | None
) -> tuple[float | None, float | None]:
    ath = _safe_float(info.get("allTimeHigh"))
    try:
        hist_long = ticker.history(period="10y")
        if hist_long is not None and not hist_long.empty:
            peak = _safe_float(hist_long["High"].max())
            if peak is not None:
                ath = peak if ath is None else max(ath, peak)
    except Exception:
        pass
    pct_below = None
    if ath is not None and ath > 0 and current_price is not None:
        pct_below = max(0.0, ((ath - current_price) / ath) * 100.0)
    return ath, pct_below


def _empty_stock_data(sym: str, *, rate_limited: bool = False) -> dict:
    empty_history = pd.DataFrame(columns=["Date", "Close"])
    return {
        "symbol": sym,
        "name": None,
        "sector": None,
        "industry": None,
        "current_price": None,
        "prev_close": None,
        "day_change_pct": None,
        "week_52_high": None,
        "week_52_low": None,
        "position_52w": None,
        "volume": None,
        "avg_volume": None,
        "market_cap": None,
        "pe_ratio": None,
        "eps": None,
        "book_value": None,
        "dividend_yield": None,
        "operating_cashflow": None,
        "free_cashflow": None,
        "history_1y": empty_history.copy(),
        "news": [],
        "beta": None,
        "dark_horse": None,
        "all_time_high": None,
        "pct_below_ath": None,
        "rs_vs_sp500_1y": None,
        "rate_limited": rate_limited,
    }


@st.cache_data(ttl=120)
def fetch_stock_data(symbol: str) -> dict:
    sym = (symbol or "").strip().upper()
    if sym and not sym.endswith(NSE_SUFFIX):
        sym = f"{sym}{NSE_SUFFIX}"

    try:
        empty_history = pd.DataFrame(columns=["Date", "Close"])
        ticker = yf.Ticker(sym)

        try:
            info = ticker.info or {}
        except Exception:
            info = {}
        if not isinstance(info, dict):
            info = {}

        try:
            fast = ticker.fast_info
        except Exception:
            fast = {}

        try:
            hist = ticker.history(period="1y")
        except Exception:
            hist = pd.DataFrame()

        try:
            raw_news = ticker.news or []
        except Exception:
            raw_news = []

        current_price = _safe_float(
            _mapping_get(fast, "last_price", "regular_market_price", default=None)
            or info.get("currentPrice")
            or info.get("regularMarketPrice")
        )
        prev_close = _safe_float(
            _mapping_get(fast, "previous_close", default=None)
            or info.get("previousClose")
            or info.get("regularMarketPreviousClose")
        )

        week_52_high = _safe_float(info.get("fiftyTwoWeekHigh"))
        week_52_low = _safe_float(info.get("fiftyTwoWeekLow"))

        if not hist.empty:
            week_52_high = week_52_high or _safe_float(hist["High"].max())
            week_52_low = week_52_low or _safe_float(hist["Low"].min())
            history_1y = hist[["Close"]].copy().reset_index()
            date_col = history_1y.columns[0]
            if date_col != "Date":
                history_1y = history_1y.rename(columns={date_col: "Date"})
            history_1y = history_1y[["Date", "Close"]]
        else:
            history_1y = empty_history.copy()

        position_52w = None
        if current_price is not None and week_52_high is not None and week_52_low is not None:
            band = week_52_high - week_52_low
            if band > 0:
                position_52w = max(0.0, min(100.0, ((current_price - week_52_low) / band) * 100))

        day_change_pct = None
        if current_price is not None and prev_close not in (None, 0):
            day_change_pct = ((current_price - prev_close) / prev_close) * 100

        stock_label = info.get("shortName") or info.get("longName") or sym.removesuffix(NSE_SUFFIX)
        merged_news = merge_news_sources(
            _parse_ticker_news(raw_news),
            fetch_google_news_stories(stock_label),
        )

        dark_horse = compute_dark_horse_score(sym, info, ticker)
        all_time_high, pct_below_ath = _compute_ath_metrics(ticker, info, current_price)
        rs_vs_sp500_1y = _compute_rs_vs_sp500(history_1y)

        result = _empty_stock_data(sym, rate_limited=False)
        result.update(
            {
                "name": stock_label,
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "current_price": current_price,
                "prev_close": prev_close,
                "day_change_pct": day_change_pct,
                "week_52_high": week_52_high,
                "week_52_low": week_52_low,
                "position_52w": position_52w,
                "volume": _safe_float(
                    info.get("volume") or _mapping_get(fast, "last_volume", default=None)
                ),
                "avg_volume": _safe_float(info.get("averageVolume")),
                "market_cap": _safe_float(info.get("marketCap")),
                "pe_ratio": _safe_float(info.get("trailingPE") or info.get("forwardPE")),
                "eps": _safe_float(
                    info.get("trailingEps") or info.get("epsTrailingTwelveMonths")
                ),
                "book_value": _safe_float(info.get("bookValue")),
                "dividend_yield": _safe_float(info.get("dividendYield")),
                "operating_cashflow": _safe_float(info.get("operatingCashflow")),
                "free_cashflow": _safe_float(info.get("freeCashflow")),
                "history_1y": history_1y,
                "news": merged_news,
                "beta": _safe_float(info.get("beta")),
                "dark_horse": dark_horse,
                "all_time_high": all_time_high,
                "pct_below_ath": pct_below_ath,
                "rs_vs_sp500_1y": rs_vs_sp500_1y,
            }
        )
        return result
    except Exception:
        return _empty_stock_data(sym, rate_limited=True)


def load_stock_data(symbol: str) -> dict:
    label = (symbol or "").removesuffix(NSE_SUFFIX)
    with st.spinner(f"Fetching live data for {label}..."):
        return fetch_stock_data(symbol)


init_conviction_state()
if "selected_symbol" not in st.session_state:
    _wl = all_conviction_symbols()
    st.session_state["selected_symbol"] = _wl[0] if _wl else None


st.set_page_config(
    page_title=_active_page_title(st.session_state.get("selected_symbol")),
    layout="wide",
    initial_sidebar_state="expanded",
)


CHART_BG = "#1c2433"
CHART_PAPER = "#232d3d"
PLOTLY_FONT = "Inter, system-ui, sans-serif"


def inject_global_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600&display=swap');

        :root {
            --font-display: 'DM Sans', system-ui, sans-serif;
            --font-body: 'Inter', system-ui, sans-serif;
            --font-mono: 'IBM Plex Mono', ui-monospace, monospace;
            --ink: #f1f5f9;
            --ink-muted: #94a3b8;
            --surface: #2a3548;
            --surface-elevated: #323f54;
            --border: #4a5d78;
            --accent: #f97316;
            --accent-soft: rgba(249, 115, 22, 0.15);
            --radius: 12px;
            --radius-lg: 16px;
        }

        html, body, .stApp, [data-testid="stAppViewContainer"] {
            font-family: var(--font-body);
            color: var(--ink);
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        .stApp {
            background: linear-gradient(165deg, #1e2736 0%, #2a3548 42%, #252f40 100%);
        }

        .block-container {
            padding-top: 1rem;
            padding-bottom: 1.5rem;
            max-width: 1180px;
        }

        h1, h2, h3, h4, .app-title, .stock-title, .section-title {
            font-family: var(--font-display) !important;
            letter-spacing: -0.025em;
            font-weight: 600;
        }

        p, li, label, .stMarkdown, span {
            font-family: var(--font-body);
        }

        div[data-testid="stMetricValue"] {
            font-family: var(--font-mono) !important;
            font-weight: 600;
            letter-spacing: -0.03em;
            color: #ffffff !important;
        }

        div[data-testid="stMetricLabel"],
        div[data-testid="stMetricLabel"] label,
        div[data-testid="stMetricLabel"] p,
        [data-testid="stMetric"] label {
            font-family: var(--font-body) !important;
            font-size: 0.78rem !important;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #ffffff !important;
        }

        label[data-testid="stWidgetLabel"],
        [data-testid="stNumberInput"] label,
        [data-testid="stTextInput"] label {
            color: #ffffff !important;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #2f3d52 0%, #283648 100%);
            border-right: 1px solid var(--border);
        }

        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            font-family: var(--font-display) !important;
        }

        [data-testid="stSidebar"] .stMarkdown {
            color: var(--ink);
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(36, 48, 66, 0.65);
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-lg) !important;
            padding: 0.85rem 1rem !important;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18);
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: rgba(28, 36, 51, 0.6);
            border-radius: 999px;
            padding: 6px;
            border: 1px solid var(--border);
        }

        .stTabs [data-baseweb="tab"] {
            font-family: var(--font-display);
            font-weight: 600;
            font-size: 0.9rem;
            letter-spacing: -0.01em;
            border-radius: 999px;
            padding: 8px 20px;
            color: var(--ink-muted);
            background: transparent;
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #f97316, #ea580c) !important;
            color: #fff !important;
        }

        .stButton > button {
            font-family: var(--font-display);
            font-weight: 600;
            letter-spacing: -0.01em;
            background: linear-gradient(135deg, #f97316 0%, #ea580c 55%, #fb923c 100%);
            color: #ffffff;
            border: 1px solid #fdba74;
            border-radius: 10px;
            box-shadow: 0 4px 14px rgba(249, 115, 22, 0.3);
            transition: transform 0.12s ease, box-shadow 0.12s ease;
        }

        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 18px rgba(249, 115, 22, 0.4);
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        textarea {
            font-family: var(--font-mono) !important;
            font-size: 0.88rem !important;
            background-color: #2d3a4f !important;
            color: #f8fafc !important;
            border: 1px solid var(--border) !important;
            border-radius: 10px !important;
        }

        div[data-testid="stTextInput"] input:focus {
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 2px var(--accent-soft) !important;
        }

        [data-testid="stDataFrame"] {
            font-family: var(--font-mono);
            font-size: 0.85rem;
        }

        .app-hero {
            display: flex;
            flex-wrap: wrap;
            align-items: flex-end;
            justify-content: space-between;
            gap: 12px;
            margin-bottom: 1.25rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--border);
        }

        .app-kicker {
            font-family: var(--font-mono);
            font-size: 0.72rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.14em;
            color: var(--accent);
            margin: 0 0 4px 0;
        }

        .app-title {
            font-size: 1.85rem;
            font-weight: 700;
            margin: 0;
            color: #fff;
            line-height: 1.15;
        }

        .app-sub {
            font-size: 0.9rem;
            color: var(--ink-muted);
            margin: 0;
            max-width: 420px;
            line-height: 1.5;
        }

        .toolbar-card-label {
            font-size: 0.72rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: var(--ink-muted);
            margin: 0 0 0.5rem 0;
        }

        .stock-hero {
            display: flex;
            flex-wrap: wrap;
            align-items: flex-start;
            justify-content: space-between;
            gap: 12px;
            margin-bottom: 0.75rem;
        }

        .stock-title {
            font-size: 1.55rem;
            margin: 0 0 8px 0;
            color: #fff;
            line-height: 1.2;
        }

        .chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            align-items: center;
        }

        .meta-chip {
            display: inline-block;
            font-family: var(--font-mono);
            font-size: 0.72rem;
            font-weight: 500;
            padding: 4px 10px;
            border-radius: 999px;
            background: rgba(15, 23, 42, 0.45);
            border: 1px solid var(--border);
            color: #cbd5e1;
        }

        .section-head {
            margin: 1.35rem 0 0.65rem 0;
        }

        .section-title {
            font-size: 1.05rem;
            margin: 0;
            color: #fff;
        }

        .section-sub {
            font-size: 0.82rem;
            color: var(--ink-muted);
            margin: 4px 0 0 0;
            line-height: 1.45;
        }

        .inline-metric-strip {
            margin-bottom: 0.5rem;
        }

        .footer-meta {
            font-family: var(--font-mono);
            font-size: 0.75rem;
            color: var(--ink-muted);
            letter-spacing: 0.02em;
        }

        .suggest-label {
            color: #b8c5d6;
            font-size: 0.8rem;
            font-weight: 500;
            margin: 0.25rem 0 0.35rem 0;
        }

        .conviction-chip {
            display: inline-block;
            font-family: var(--font-mono);
            font-size: 0.82rem;
            font-weight: 600;
            padding: 6px 10px;
            border-radius: 8px;
            background: linear-gradient(135deg, #3a4a62, #35435a);
            border: 1px solid #5b7190;
            color: #fff;
            margin-bottom: 4px;
        }

        .conviction-chip-selected {
            border-color: #f97316;
            background: linear-gradient(135deg, #ea580c, #c2410c);
        }

        .suggest-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 8px 10px 10px;
            margin-bottom: 8px;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
        }

        .suggest-name {
            color: #0f172a !important;
            font-size: 0.78rem;
            font-weight: 500;
            line-height: 1.35;
            margin: 6px 0 0 0;
        }

        div[data-testid="stVerticalBlock"]:has(.suggest-card) button[kind="secondary"] p,
        div[data-testid="stVerticalBlock"]:has(.suggest-card) button p {
            color: #0f172a !important;
            font-weight: 700 !important;
        }

        .news-summary {
            background: rgba(36, 48, 66, 0.8);
            border: 1px solid var(--border);
            border-left: 4px solid var(--accent);
            border-radius: var(--radius);
            padding: 14px 16px;
            line-height: 1.6;
            color: var(--ink);
            font-size: 0.92rem;
        }

        .dh-wrap {
            position: relative;
            display: inline-block;
        }

        .dh-badge {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 999px;
            font-family: var(--font-mono);
            font-weight: 600;
            font-size: 0.8rem;
            letter-spacing: 0.02em;
            cursor: help;
            border: 1px solid transparent;
        }

        .dh-red {
            background: linear-gradient(135deg, #ef4444, #b91c1c);
            color: #fff;
            border-color: #fca5a5;
        }

        .dh-amber {
            background: linear-gradient(135deg, #f59e0b, #d97706);
            color: #1f2937;
            border-color: #fcd34d;
        }

        .dh-green {
            background: linear-gradient(135deg, #22c55e, #15803d);
            color: #fff;
            border-color: #86efac;
        }

        .dh-tooltip {
            visibility: hidden;
            opacity: 0;
            width: 340px;
            max-width: 90vw;
            background: #1e293b;
            color: #e2e8f0;
            text-align: left;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 12px 14px;
            position: absolute;
            z-index: 1000;
            right: 0;
            top: 125%;
            font-size: 0.78rem;
            line-height: 1.45;
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.35);
            transition: opacity 0.15s ease;
            pointer-events: none;
        }

        .dh-wrap:hover .dh-tooltip {
            visibility: visible;
            opacity: 1;
        }

        .conviction-stock-block {
            background: rgba(36, 48, 66, 0.7);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 10px 12px;
            margin-bottom: 10px;
        }

        .conviction-stock-block.tier-3-block {
            border-left: 4px solid #22c55e;
        }

        .conviction-stock-block.tier-2-block {
            border-left: 4px solid #f59e0b;
        }

        .entry-range-wrap { margin: 10px 0 6px; }

        .entry-range-label {
            font-size: 0.8rem;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 6px;
        }

        .entry-range-track {
            position: relative;
            height: 18px;
            background: linear-gradient(90deg, #1e3a5f 0%, #475569 50%, #1e3a5f 100%);
            border-radius: 999px;
            border: 1px solid var(--border);
            overflow: visible;
            margin: 8px 4px 4px;
        }

        .entry-buy-zone-shade {
            position: absolute;
            top: 1px;
            bottom: 1px;
            background: rgba(34, 197, 94, 0.45);
            border: 1px solid #4ade80;
            border-radius: 999px;
            z-index: 1;
        }

        .entry-range-marker {
            position: absolute;
            top: 50%;
            width: 6px;
            height: 26px;
            margin-top: -13px;
            background: linear-gradient(180deg, #fb923c, #ea580c);
            border-radius: 3px;
            transform: translateX(-50%);
            z-index: 2;
            box-shadow: 0 0 8px rgba(249, 115, 22, 0.55);
            pointer-events: none;
        }

        .entry-range-captions {
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            align-items: end;
            gap: 8px;
            font-family: var(--font-mono);
            font-size: 0.75rem;
            color: #ffffff;
            margin-top: 8px;
        }

        .entry-range-captions span:first-child { text-align: left; }
        .entry-range-captions span:nth-child(2) { text-align: center; color: #f97316; }
        .entry-range-captions span:last-child { text-align: right; }

        .buy-zone-hit-banner {
            background: linear-gradient(135deg, #15803d 0%, #22c55e 100%);
            color: #fff;
            border-radius: 10px;
            padding: 10px 14px;
            font-family: var(--font-display);
            font-weight: 600;
            margin: 10px 0 6px;
            text-align: center;
            border: 1px solid #86efac;
        }

        .entry-alert-note {
            background: rgba(36, 48, 66, 0.85);
            border: 1px solid var(--border);
            border-left: 4px solid #38bdf8;
            border-radius: 8px;
            padding: 10px 12px;
            font-size: 0.86rem;
            line-height: 1.5;
            color: #e2e8f0;
            margin-top: 8px;
        }

        .entry-alert-triggered {
            border-left-color: var(--accent);
            background: var(--accent-soft);
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_chart_theme(fig, *, height: int | None = None, title: str | None = None):
    layout = dict(
        template="plotly_dark",
        plot_bgcolor=CHART_BG,
        paper_bgcolor=CHART_PAPER,
        font=dict(family=PLOTLY_FONT, color="#e2e8f0", size=12),
        margin=dict(l=12, r=12, t=44 if title else 12, b=12),
        title=dict(text=title, font=dict(family="DM Sans, sans-serif", size=14)) if title else None,
    )
    if height is not None:
        layout["height"] = height
    fig.update_layout(**{k: v for k, v in layout.items() if v is not None})
    return fig


inject_global_styles()


def render_section_header(title: str, subtitle: str = "") -> None:
    sub_html = f'<p class="section-sub">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f'<div class="section-head"><h3 class="section-title">{title}</h3>{sub_html}</div>',
        unsafe_allow_html=True,
    )


def render_app_hero() -> None:
    st.markdown(
        """
        <div class="app-hero">
            <div>
                <p class="app-kicker">NSE · Live research</p>
                <h1 class="app-title">Aleem's Investment Dashboard</h1>
            </div>
            <p class="app-sub">Conviction tiers, entry timing, and portfolio health — one workspace.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stock_hero_header(data: dict) -> None:
    name = data.get("name") or data.get("symbol", "")
    symbol = data.get("symbol", "")
    sector = data.get("sector") or "—"
    industry = data.get("industry") or "—"
    st.markdown(
        f"""
        <div class="stock-hero">
            <div>
                <h2 class="stock-title">{name}</h2>
                <div class="chip-row">
                    <span class="meta-chip">{symbol}</span>
                    <span class="meta-chip">{sector}</span>
                    <span class="meta-chip">{industry}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_inr(n: float | None, decimals: int = 2) -> str:
    if n is None:
        return "N/A"
    negative = n < 0
    n = abs(float(n))
    if decimals == 0:
        int_str = str(int(round(n)))
        dec_str = None
    else:
        formatted = f"{n:.{decimals}f}"
        int_str, dec_str = formatted.split(".") if "." in formatted else (formatted, None)

    if len(int_str) <= 3:
        grouped = int_str
    else:
        last3 = int_str[-3:]
        rest = int_str[:-3]
        parts: list[str] = []
        while rest:
            parts.insert(0, rest[-2:])
            rest = rest[:-2]
        grouped = ",".join(parts + [last3])

    text = "₹" + grouped
    if dec_str is not None:
        text += "." + dec_str
    return ("-" if negative else "") + text


_fmt_inr = format_inr


def _fmt_pct(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value:+.2f}%"


def _fmt_market_cap(value: float | None) -> str:
    if value is None:
        return "N/A"
    if value >= 1e7:
        return f"{format_inr(value / 1e7)} Cr"
    if value >= 1e5:
        return f"{format_inr(value / 1e5)} L"
    return format_inr(value, decimals=0)


def get_entry_timing_prefs(symbol: str) -> dict:
    if "entry_timing" not in st.session_state:
        st.session_state["entry_timing"] = {}
    if symbol not in st.session_state["entry_timing"]:
        st.session_state["entry_timing"][symbol] = {
            "buy_zone_low": None,
            "buy_zone_high": None,
            "alert_dip_price": None,
            "alert_set_at": None,
        }
    return st.session_state["entry_timing"][symbol]


def _price_to_range_pct(
    price: float | None, range_low: float | None, range_high: float | None
) -> float | None:
    if price is None or range_low is None or range_high is None:
        return None
    band = range_high - range_low
    if band <= 0:
        return None
    return max(0.0, min(100.0, ((price - range_low) / band) * 100.0))


def render_entry_52w_visual(data: dict, timing: dict) -> None:
    pos = data.get("position_52w")
    low = data.get("week_52_low")
    high = data.get("week_52_high")
    current = data.get("current_price")

    if low is None or high is None or high <= low:
        st.caption("52-week range unavailable — refresh data or try again shortly.")
        return

    marker_pct = pos
    if marker_pct is None and current is not None:
        marker_pct = _price_to_range_pct(current, low, high)
    if marker_pct is None:
        marker_pct = 50.0
    marker_pct = max(0.0, min(100.0, float(marker_pct)))

    zone_html = ""
    bz_lo = timing.get("buy_zone_low")
    bz_hi = timing.get("buy_zone_high")
    if bz_lo is not None and bz_hi is not None:
        left_pct = _price_to_range_pct(min(bz_lo, bz_hi), low, high)
        right_pct = _price_to_range_pct(max(bz_lo, bz_hi), low, high)
        if left_pct is not None and right_pct is not None:
            zone_left = min(left_pct, right_pct)
            zone_width = abs(right_pct - left_pct)
            if zone_width > 0:
                zone_html = (
                    f'<div class="entry-buy-zone-shade" '
                    f'style="left:{zone_left:.1f}%;width:{max(zone_width, 1.0):.1f}%"></div>'
                )

    st.markdown(
        f"""
        <div class="entry-range-wrap">
            <div class="entry-range-label">Current price within 52-week range</div>
            <div class="entry-range-track">
                {zone_html}
                <div class="entry-range-marker" style="left:{marker_pct:.1f}%"></div>
            </div>
            <div class="entry-range-captions">
                <span>Low {format_inr(low)}</span>
                <span><strong>{format_inr(current)}</strong></span>
                <span>High {format_inr(high)}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        f"Position in range: **{marker_pct:.1f}%** (0% = 52W low, 100% = 52W high)"
    )


def render_entry_timing_panel(data: dict, *, compact: bool = False) -> None:
    symbol = data.get("symbol") or ""
    timing = get_entry_timing_prefs(symbol)
    current = data.get("current_price")
    pos_52w = data.get("position_52w")
    pct_ath = data.get("pct_below_ath")
    rs = data.get("rs_vs_sp500_1y")
    ath = data.get("all_time_high")
    
    # Auto-calculate buy zone if not set and 52-week data is available
    week_52_low = data.get("week_52_low")
    week_52_high = data.get("week_52_high")
    if timing.get("buy_zone_low") is None and timing.get("buy_zone_high") is None:
        if week_52_low is not None and week_52_high is not None and current is not None:
            # Calculate reasonable buy zone: 10% above 52-week low to current price
            band = week_52_high - week_52_low
            if band > 0:
                suggested_low = week_52_low + (band * 0.10)  # 10% above 52-week low
                suggested_high = current  # Current price as upper bound
                timing["buy_zone_low"] = round(suggested_low, 2)
                timing["buy_zone_high"] = round(suggested_high, 2)

    def _panel_body() -> None:
        m1, m2, m3 = st.columns(3)
        m1.metric(
            "52-week position",
            f"{pos_52w:.1f}%" if pos_52w is not None else "N/A",
            help="Where price sits between 52-week low and high",
        )
        m2.metric(
            "Below all-time high",
            f"{pct_ath:.1f}%" if pct_ath is not None else "N/A",
            help=f"ATH: {format_inr(ath)}" if ath else "All-time high from 10Y history",
        )
        m3.metric(
            "Relative strength (1Y)",
            f"{rs:+.1f}%" if rs is not None else "N/A",
            help="Stock 1-year return minus S&P 500 (^GSPC) 1-year return",
        )

        render_entry_52w_visual(data, timing)

        st.markdown("**Your buy zone**")
        bz1, bz2 = st.columns(2)
        low_input = bz1.number_input(
            "Buy zone low (INR)",
            min_value=0.0,
            value=float(timing["buy_zone_low"] or 0.0),
            step=1.0,
            key=f"entry_bz_low_{symbol}",
            help="Lower bound of your entry range (0 = not set)",
        )
        high_input = bz2.number_input(
            "Buy zone high (INR)",
            min_value=0.0,
            value=float(timing["buy_zone_high"] or 0.0),
            step=1.0,
            key=f"entry_bz_high_{symbol}",
            help="Upper bound of your entry range (0 = not set)",
        )
        timing["buy_zone_low"] = low_input if low_input > 0 else None
        timing["buy_zone_high"] = high_input if high_input > 0 else None

        bz_lo = timing.get("buy_zone_low")
        bz_hi = timing.get("buy_zone_high")
        if bz_lo is not None and bz_hi is not None and current is not None:
            zone_min, zone_max = min(bz_lo, bz_hi), max(bz_lo, bz_hi)
            if zone_min <= current <= zone_max:
                st.markdown(
                    '<div class="buy-zone-hit-banner">✓ Price is inside your buy zone</div>',
                    unsafe_allow_html=True,
                )
            else:
                if current < zone_min:
                    gap = zone_min - current
                    st.caption(
                        f"Price is **{format_inr(gap)}** below your buy zone "
                        f"({format_inr(zone_min)} – {format_inr(zone_max)})."
                    )
                else:
                    gap = current - zone_max
                    st.caption(
                        f"Price is **{format_inr(gap)}** above your buy zone "
                        f"({format_inr(zone_min)} – {format_inr(zone_max)})."
                    )
        elif bz_lo or bz_hi:
            st.caption("Set both low and high to define a buy zone.")

        st.markdown("**Dip alert**")
        alert_col, btn_col = st.columns([2, 1])
        alert_default = float(timing["alert_dip_price"] or 0.0)
        dip_input = alert_col.number_input(
            "Target dip price (INR)",
            min_value=0.0,
            value=alert_default,
            step=1.0,
            key=f"entry_alert_{symbol}",
            help="Price you want to be notified about (0 = clear)",
        )
        if btn_col.button(
            "Set alert",
            key=f"entry_set_alert_{symbol}",
            use_container_width=True,
        ):
            if dip_input > 0:
                timing["alert_dip_price"] = dip_input
                timing["alert_set_at"] = datetime.now().strftime("%d %b %Y, %I:%M %p")
                st.toast(f"Alert noted: target dip {format_inr(dip_input)}")
            else:
                timing["alert_dip_price"] = None
                timing["alert_set_at"] = None
                st.toast("Alert cleared.")

        alert_price = timing.get("alert_dip_price")
        if alert_price is not None:
            triggered = current is not None and current <= alert_price
            alert_cls = "entry-alert-note entry-alert-triggered" if triggered else "entry-alert-note"
            set_at = timing.get("alert_set_at") or "—"
            trigger_line = (
                f" <strong>Current price is at or below this target.</strong>"
                if triggered
                else ""
            )
            st.markdown(
                f'<div class="{alert_cls}">'
                f"🔔 Alert set: watch for dip to <strong>{format_inr(alert_price)}</strong> "
                f"(saved {set_at}).{trigger_line}</div>",
                unsafe_allow_html=True,
            )

    if compact:
        with st.expander("Entry timing", expanded=False):
            _panel_body()
    else:
        render_section_header(
            "Entry timing",
            "52-week position, relative strength, buy zone, and dip alerts.",
        )
        with st.container(border=True):
            _panel_body()


def render_52w_position_bar(data: dict) -> None:
    render_entry_52w_visual(data, get_entry_timing_prefs(data.get("symbol") or ""))


def _fmt_yield(value: float | None) -> str:
    if value is None:
        return "N/A"
    pct = value * 100 if abs(value) <= 1 else value
    return f"{pct:.2f}%"


def generate_rule_based_analysis(
    momentum_pct: float,
    position_52w: float,
    headlines: list[tuple[str, str]],
    *,
    momentum_label: str = "Day change",
) -> tuple[str, list[str]]:
    bullish_words = {
        "surge",
        "rally",
        "gain",
        "gains",
        "strong",
        "beats",
        "upgrade",
        "growth",
        "record",
        "bullish",
        "profit",
        "profits",
        "outperform",
        "buy",
    }
    bearish_words = {
        "fall",
        "falls",
        "drop",
        "drops",
        "weak",
        "miss",
        "downgrade",
        "loss",
        "losses",
        "concern",
        "bearish",
        "sell",
        "underperform",
        "decline",
    }

    news_score = 0
    matched_positive = 0
    matched_negative = 0
    for title, _ in headlines:
        t = title.lower()
        pos_hits = sum(1 for w in bullish_words if w in t)
        neg_hits = sum(1 for w in bearish_words if w in t)
        matched_positive += pos_hits
        matched_negative += neg_hits
        news_score += pos_hits - neg_hits

    signal_score = 0
    reasons = []

    if momentum_pct >= 2:
        signal_score += 2
        reasons.append(
            f"{momentum_label} is strongly positive at {momentum_pct:.2f}%, showing upward momentum."
        )
    elif momentum_pct >= 0:
        signal_score += 1
        reasons.append(
            f"{momentum_label} is positive at {momentum_pct:.2f}%, indicating moderate strength."
        )
    elif momentum_pct <= -2:
        signal_score -= 2
        reasons.append(
            f"{momentum_label} is sharply negative at {momentum_pct:.2f}%, reflecting near-term weakness."
        )
    else:
        signal_score -= 1
        reasons.append(
            f"{momentum_label} is negative at {momentum_pct:.2f}%, which is a near-term caution."
        )

    if position_52w >= 70:
        signal_score += 1
        reasons.append(
            f"Price is at {position_52w:.2f}% of its 52-week range, closer to yearly highs."
        )
    elif position_52w <= 30:
        signal_score -= 1
        reasons.append(
            f"Price is at {position_52w:.2f}% of its 52-week range, closer to yearly lows."
        )
    else:
        reasons.append(f"Price sits mid-range at {position_52w:.2f}% of the 52-week band.")

    signal_score += news_score
    if matched_positive > matched_negative:
        reasons.append(
            f"Recent news tone is positive ({matched_positive} positive vs {matched_negative} negative keyword hits)."
        )
    elif matched_negative > matched_positive:
        reasons.append(
            f"Recent news tone is negative ({matched_negative} negative vs {matched_positive} positive keyword hits)."
        )
    else:
        reasons.append("Recent news flow is mixed/neutral with no strong directional bias.")

    if signal_score >= 2:
        stance = "Bullish"
    elif signal_score <= -2:
        stance = "Bearish"
    else:
        stance = "Neutral"

    return stance, reasons[:3]


def render_stock_view(data: dict) -> None:
    if data.get("rate_limited"):
        st.warning(RATE_LIMIT_MSG)
        return

    hero_left, hero_right = st.columns([5, 1])
    with hero_left:
        render_stock_hero_header(data)
    with hero_right:
        render_dark_horse_badge(data)

    day_chg = data.get("day_change_pct")
    pos_52w = data.get("position_52w")
    with st.container(border=True):
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Price (INR)", format_inr(data.get("current_price")))
        m2.metric("Day Change %", _fmt_pct(day_chg))
        m3.metric(
            "P/E Ratio",
            f"{data['pe_ratio']:.2f}" if data.get("pe_ratio") is not None else "N/A",
        )
        m4.metric("Market Cap", _fmt_market_cap(data.get("market_cap")))

    render_entry_timing_panel(data)

    render_section_header("1-Year price chart")
    history = data.get("history_1y")
    if history is not None and not history.empty:
        price_fig = px.line(history, x="Date", y="Close", template="plotly_dark")
        apply_chart_theme(price_fig, height=380)
        price_fig.update_layout(xaxis_title="", yaxis_title="Close (INR)")
        st.plotly_chart(price_fig, use_container_width=True)
    else:
        st.info("No historical price data available.")

    volume = data.get("volume")
    avg_volume = data.get("avg_volume")
    if volume is not None and avg_volume not in (None, 0):
        vol_text = (
            f"{format_inr(volume, decimals=0)} vs avg "
            f"{format_inr(avg_volume, decimals=0)} ({volume / avg_volume * 100:.0f}% of avg)"
        )
    else:
        vol_text = "N/A"

    render_section_header("Fundamentals")
    fundamentals = pd.DataFrame(
        {
            "Metric": [
                "P/E Ratio",
                "EPS",
                "Book Value",
                "Operating Cash Flow",
                "Free Cash Flow",
                "Beta",
                "Dividend Yield",
                "Volume vs Avg Volume",
            ],
            "Value": [
                f"{data['pe_ratio']:.2f}" if data.get("pe_ratio") is not None else "N/A",
                _fmt_inr(data.get("eps")),
                _fmt_inr(data.get("book_value")),
                _fmt_inr(data.get("operating_cashflow")),
                _fmt_inr(data.get("free_cashflow")),
                f"{data['beta']:.2f}" if data.get("beta") is not None else "N/A",
                _fmt_yield(data.get("dividend_yield")),
                vol_text,
            ],
        }
    )
    st.dataframe(fundamentals, use_container_width=True, hide_index=True)

    render_section_header("News intelligence", "Synthesized headline tone — not financial advice.")
    news_items = data.get("news") or []
    stock_label = data.get("name") or data.get("symbol", "")
    summary_text, takeaways = generate_news_decision_summary(
        stock_label,
        news_items,
        day_change_pct=day_chg,
        position_52w=pos_52w,
    )
    with st.container(border=True):
        st.markdown(f'<div class="news-summary">{summary_text}</div>', unsafe_allow_html=True)
        for point in takeaways:
            st.markdown(f"- {point}")
    st.caption(f"Based on {len(news_items)} recent headline(s).")
    render_section_header("Analysis verdict")
    headlines = [(a.get("title", ""), a.get("link", "")) for a in news_items]
    outlook, reasons = generate_rule_based_analysis(
        momentum_pct=float(day_chg or 0.0),
        position_52w=float(pos_52w or 0.0),
        headlines=headlines,
        momentum_label="Day change",
    )
    if outlook == "Bullish":
        st.success(f"**Outlook: {outlook}**")
    elif outlook == "Bearish":
        st.error(f"**Outlook: {outlook}**")
    else:
        st.info(f"**Outlook: {outlook}**")
    for reason in reasons:
        st.markdown(f"- {reason}")


def _normalize_history(history: pd.DataFrame) -> pd.DataFrame:
    if history is None or history.empty:
        return pd.DataFrame(columns=["Date", "Normalized"])
    first_close = history["Close"].iloc[0]
    out = history.copy()
    if first_close in (None, 0) or pd.isna(first_close):
        out["Normalized"] = 100.0
    else:
        out["Normalized"] = (out["Close"] / float(first_close)) * 100
    return out


def render_compare_summary(data: dict) -> None:
    if data.get("rate_limited"):
        st.warning(RATE_LIMIT_MSG)
        return

    name = data.get("name") or data.get("symbol", "")
    day_chg = data.get("day_change_pct")

    st.markdown(f"### {name}")
    st.caption(data.get("symbol", ""))
    render_dark_horse_badge(data)
    st.metric("Price (INR)", format_inr(data.get("current_price")))
    st.metric(
        "Day Change %",
        _fmt_pct(day_chg),
        delta=f"{day_chg:.2f}%" if day_chg is not None else None,
    )
    st.metric("P/E Ratio", f"{data['pe_ratio']:.2f}" if data.get("pe_ratio") is not None else "N/A")
    render_entry_timing_panel(data, compact=True)
    st.metric("Market Cap", _fmt_market_cap(data.get("market_cap")))


def render_normalized_compare_chart(data_a: dict, data_b: dict) -> None:
    render_section_header("1-Year performance", "Indexed to 100 at start of period.")
    series_frames = []
    for data in (data_a, data_b):
        history = data.get("history_1y")
        if history is None or history.empty:
            continue
        normalized = _normalize_history(history)
        part = normalized[["Date", "Normalized"]].copy()
        part["Symbol"] = data.get("symbol", "")
        series_frames.append(part)

    if len(series_frames) < 2:
        st.info("Not enough historical data to compare both stocks.")
        return

    combined = pd.concat(series_frames, ignore_index=True)
    compare_fig = px.line(
        combined,
        x="Date",
        y="Normalized",
        color="Symbol",
        template="plotly_dark",
    )
    apply_chart_theme(compare_fig, height=400)
    compare_fig.update_layout(
        xaxis_title="",
        yaxis_title="Indexed price (start = 100)",
        legend_title="",
    )
    compare_fig.update_traces(mode="lines")
    st.plotly_chart(compare_fig, use_container_width=True)


def render_stock_comparison(data_a: dict, data_b: dict) -> None:
    render_section_header("Stock comparison", "Side-by-side metrics and indexed performance.")
    col_left, col_right = st.columns(2)
    with col_left:
        render_compare_summary(data_a)
    with col_right:
        render_compare_summary(data_b)
    render_normalized_compare_chart(data_a, data_b)


render_app_hero()

get_watchlist()
if "selected_symbol" not in st.session_state:
    wl = get_watchlist()
    st.session_state["selected_symbol"] = wl[0] if wl else None

with st.container(border=True):
    st.markdown('<p class="toolbar-card-label">Search & add to watchlist</p>', unsafe_allow_html=True)
    top_left, top_mid, top_right = st.columns([4, 1, 1.4])
    with top_left:
        search_query = st.text_input(
            "Search NSE stock",
            placeholder="Type a letter to see matches…",
            key="nse_search_input",
            label_visibility="collapsed",
        )
        needle = search_query.strip()
        if len(needle) >= 1:
            suggestions = fuzzy_search_nse(needle, limit=8)
            if suggestions:
                st.markdown(
                    '<p class="suggest-label">Matching NSE stocks — click to load</p>',
                    unsafe_allow_html=True,
                )
                suggest_cols = st.columns(4)
                for idx, (sym, company_name) in enumerate(suggestions):
                    with suggest_cols[idx % 4]:
                        st.markdown(
                            f'<div class="suggest-card">'
                            f'<p class="suggest-name"><strong>{sym}</strong><br/>'
                            f"{company_name[:48]}</p></div>",
                            unsafe_allow_html=True,
                        )
                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            if st.button(
                                "Open",
                                key=f"fuzzy_pick_{sym}_{idx}",
                                use_container_width=True,
                                help=f"Load {sym} — {company_name}",
                            ):
                                st.session_state["selected_symbol"] = f"{sym}{NSE_SUFFIX}"
                                st.rerun()
                        with btn_col2:
                            ticker_with_suffix = f"{sym}{NSE_SUFFIX}"
                            if st.button(
                                "+ Add",
                                key=f"fuzzy_add_{sym}_{idx}",
                                use_container_width=True,
                                help=f"Add {sym} to watchlist",
                            ):
                                if ticker_with_suffix in get_watchlist():
                                    st.info(f"{ticker_with_suffix} is already in your watchlist.")
                                else:
                                    add_to_conviction(ticker_with_suffix, "1")
                                    st.success(f"Added {ticker_with_suffix} to watchlist.")
                                st.rerun()
            else:
                st.caption("No NSE matches yet — keep typing or try the full ticker.")
    with top_mid:
        search_clicked = st.button("Search", use_container_width=True)
    with top_right:
        refresh_clicked = st.button("🔄 Refresh data", use_container_width=True)

if refresh_clicked:
    st.cache_data.clear()
    st.rerun()

if search_clicked:
    query = search_query.strip()
    if not query:
        st.warning("Enter a stock name or ticker to search.")
    else:
        valid, ticker, _ = search_nse_stock(query)
        if not valid:
            nse_not_found_error(query)
        else:
            st.session_state["selected_symbol"] = ticker
            st.rerun()

st.sidebar.markdown("### Top Sector Stocks")
render_sector_stocks()

st.sidebar.markdown("---")
compare_on = st.sidebar.toggle("Compare", key="compare_enabled")

if "compare_symbol" not in st.session_state:
    st.session_state["compare_symbol"] = ""

if compare_on:
    compare_default = st.session_state["compare_symbol"].removesuffix(NSE_SUFFIX)
    compare_query = st.sidebar.text_input(
        "Second symbol",
        value=compare_default,
        placeholder="e.g. TCS, HDFCBANK",
        key="compare_symbol_input",
    )
    if compare_query.strip():
        valid_compare, compare_ticker, _ = search_nse_stock(compare_query)
        if valid_compare:
            st.session_state["compare_symbol"] = compare_ticker
        else:
            st.session_state["compare_symbol"] = ""
            st.sidebar.error(
                f"'{compare_query.strip()}' not found on NSE. "
                "Try the full ticker e.g. TATAMOTORS, BAJFINANCE"
            )
    else:
        st.session_state["compare_symbol"] = ""

tab_research, tab_portfolio_health, tab_holdings, tab_scanner = st.tabs(["Research", "Portfolio Health", "Current Holdings", "Dark Horse Scanner"])

selected = st.session_state.get("selected_symbol")
compare_symbol = st.session_state.get("compare_symbol", "")

with tab_research:
    if selected:
        show_comparison = (
            compare_on
            and compare_symbol
            and compare_symbol != selected
        )
        if compare_on and compare_symbol == selected:
            st.warning("Choose a different symbol for comparison.")

        if show_comparison:
            primary_data = load_stock_data(selected)
            compare_data = load_stock_data(compare_symbol)
            render_stock_comparison(primary_data, compare_data)
        else:
            stock_data = load_stock_data(selected)
            render_stock_view(stock_data)
            if compare_on and not compare_symbol:
                st.info("Enter a second symbol in the sidebar to compare.")
    else:
        st.info("Search for an NSE stock or select one from the watchlist sidebar.")

with tab_portfolio_health:
    render_portfolio_health_tab()

with tab_holdings:
    render_section_header(
        "Current Holdings",
        "Track your actual positions with quantity, purchase price, and profit/loss calculation."
    )

    holdings = get_holdings()

    # Add new holding form
    with st.expander("Add new holding", expanded=False):
        add_col1, add_col2, add_col3, add_col4 = st.columns(4)
        with add_col1:
            new_symbol = st.text_input("Symbol", placeholder="e.g. RELIANCE.NS", key="add_holding_symbol")
        with add_col2:
            new_qty = st.number_input("Quantity", min_value=0.0, step=1.0, value=0.0, key="add_holding_qty")
        with add_col3:
            new_price = st.number_input("Purchase Price (INR)", min_value=0.0, step=1.0, value=0.0, key="add_holding_price")
        with add_col4:
            add_holding_btn = st.button("Add", use_container_width=True, key="add_holding_btn")

        if add_holding_btn:
            if new_symbol and new_qty > 0 and new_price > 0:
                symbol = new_symbol.strip().upper()
                if not symbol.endswith(NSE_SUFFIX):
                    symbol = f"{symbol}{NSE_SUFFIX}"
                add_holding(symbol, new_qty, new_price)
                st.success(f"Added {symbol} to holdings.")
                st.rerun()
            else:
                st.warning("Please fill in all fields with valid values.")

    if not holdings:
        st.info("No holdings yet. Add your first holding using the form above.")
    else:
        # Fetch current prices for all holdings
        holdings_data = []
        total_invested = 0.0
        total_current_value = 0.0

        for holding in holdings:
            symbol = holding["symbol"]
            qty = holding["quantity"]
            purchase_price = holding["purchase_price"]

            try:
                stock_data = fetch_stock_data(symbol)
                current_price = stock_data.get("current_price")
                name = stock_data.get("name", symbol.removesuffix(NSE_SUFFIX))
            except Exception:
                current_price = None
                name = symbol.removesuffix(NSE_SUFFIX)

            invested = qty * purchase_price
            current_value = qty * current_price if current_price else 0
            profit_loss = current_value - invested
            profit_loss_pct = (profit_loss / invested * 100) if invested > 0 else 0

            total_invested += invested
            total_current_value += current_value

            holdings_data.append({
                "symbol": symbol,
                "name": name,
                "quantity": qty,
                "purchase_price": purchase_price,
                "current_price": current_price,
                "invested": invested,
                "current_value": current_value,
                "profit_loss": profit_loss,
                "profit_loss_pct": profit_loss_pct,
            })

        # Summary metrics
        total_profit_loss = total_current_value - total_invested
        total_profit_loss_pct = (total_profit_loss / total_invested * 100) if total_invested > 0 else 0

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Invested", format_inr(total_invested))
        m2.metric("Current Value", format_inr(total_current_value))
        m3.metric(
            "Total Profit/Loss",
            f"{format_inr(total_profit_loss)} ({total_profit_loss_pct:+.2f}%)",
            delta=f"{total_profit_loss_pct:+.2f}%" if total_profit_loss != 0 else None,
        )

        # Holdings table
        st.markdown("### Holdings Detail")
        display_data = []
        for idx, h in enumerate(holdings_data):
            display_data.append({
                "Symbol": h["symbol"],
                "Name": h["name"],
                "Quantity": h["quantity"],
                "Purchase Price": format_inr(h["purchase_price"]),
                "Current Price": format_inr(h["current_price"]) if h["current_price"] else "N/A",
                "Invested": format_inr(h["invested"]),
                "Current Value": format_inr(h["current_value"]),
                "Profit/Loss": f"{format_inr(h['profit_loss'])} ({h['profit_loss_pct']:+.2f}%)",
            })

        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Edit/Remove holdings
        st.markdown("### Manage Holdings")
        for idx, holding in enumerate(holdings):
            with st.expander(f"{holding['symbol']} - {holding['quantity']} shares @ {format_inr(holding['purchase_price'])}"):
                edit_col1, edit_col2, edit_col3, edit_col4, edit_col5 = st.columns(5)
                with edit_col1:
                    edit_qty = st.number_input(
                        "Quantity",
                        min_value=0.0,
                        step=1.0,
                        value=holding["quantity"],
                        key=f"edit_qty_{idx}",
                    )
                with edit_col2:
                    edit_price = st.number_input(
                        "Purchase Price",
                        min_value=0.0,
                        step=1.0,
                        value=holding["purchase_price"],
                        key=f"edit_price_{idx}",
                    )
                with edit_col3:
                    update_btn = st.button("Update", key=f"update_{idx}", use_container_width=True)
                with edit_col4:
                    remove_btn = st.button("Remove", key=f"remove_{idx}", use_container_width=True)

                if update_btn:
                    update_holding(idx, edit_qty, edit_price)
                    st.success(f"Updated {holding['symbol']}.")
                    st.rerun()

                if remove_btn:
                    remove_holding(idx)
                    st.success(f"Removed {holding['symbol']}.")
                    st.rerun()

with tab_scanner:
    render_section_header(
        "Dark Horse Scanner",
        "Screen NSE stocks for undervalued, cash-generating companies with strong fundamentals."
    )

    # Scanner controls
    col1, col2, col3 = st.columns(3)
    with col1:
        num_stocks = st.selectbox("Number of stocks to screen", [50, 100, 200, 500], index=1)
    with col2:
        min_score = st.slider("Minimum Dark Horse Score", 0, 100, 60)
    with col3:
        scan_btn = st.button("Run Scanner", use_container_width=True)

    if scan_btn:
        # Use top N stocks from NIFTY 50, 100, 200, 500 as proxy for screening
        # In production, you'd use nsepython or jugaad-trader to get full NSE list
        nse_stocks = [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
            "HINDUNILVR.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS",
            "LICI.NS", "AXISBANK.NS", "LT.NS", "BAJFINANCE.NS", "WIPRO.NS",
            "TATAMOTORS.NS", "MARUTI.NS", "HCLTECH.NS", "SUNPHARMA.NS", "TITAN.NS",
            "NTPC.NS", "ULTRACEMCO.NS", "POWERGRID.NS", "BAJAJ-AUTO.NS", "NESTLEIND.NS",
            "DRREDDY.NS", "ASIANPAINT.NS", "TATASTEEL.NS", "MAHINDRA.NS", "JSWSTEEL.NS",
            "DIVISLAB.NS", "M&M.NS", "ADANIENT.NS", "TATACONSUM.NS", "HINDALCO.NS",
            "CIPLA.NS", "GRASIM.NS", "WELCORP.NS", "DLF.NS", "BRITANNIA.NS",
            "EICHERMOT.NS", "HEROMOTOCO.NS", "ACC.NS", "AMBUJACEM.NS", "ZOMATO.NS",
            "DMART.NS", "PERSISTENT.NS", "TRENT.NS", "APOLLOHOSP.NS", "BERGEPAINT.NS",
            # Additional stocks for 100+ screening
            "GODREJCP.NS", "HINDALCO.NS", "TATASTEEL.NS", "JSWSTEEL.NS", "COALINDIA.NS",
            "ONGC.NS", "IOC.NS", "BPCL.NS", "GAIL.NS", "MUTHOOTFIN.NS",
            "BAJAJFINSV.NS", "CHOLAHLDNG.NS", "IBULHSGFIN.NS", "MFIN.NS", "TATASTEEL.NS",
            "UPL.NS", "DABUR.NS", "GODREJPROP.NS", "PIIND.NS", "LUPIN.NS",
            "CADILAHC.NS", "AUROPHARMA.NS", "ALKEM.NS", "BIOCON.NS", "JUBLPHARM.NS",
            "MRF.NS", "APOLLOTYRE.NS", "CEAT.NS", "JKTYRE.NS", "BRIDGETYRE.NS",
            "EXIDEIND.NS", "AMARAJABAT.NS", "HCLTECH.NS", "TECHM.NS", "MPHASIS.NS",
            "LTIM.NS", "COFORGE.NS", "PERSISTENT.NS", "TATAELXSI.NS", "LTIM.NS",
            "IDFCFIRSTB.NS", "FEDERALBNK.NS", "BANDHANBNK.NS", "RBLBANK.NS", "INDUSINDBK.NS",
            "AUBANK.NS", "J&KBANK.NS", "KARURVYSYA.NS", "SOUTHBANK.NS", "DCBBANK.NS",
            "TATACHEM.NS", "NAVINFLUOR.NS", "PIIND.NS", "SRF.NS", "DEEPAKNTR.NS",
            "GUJALKALI.NS", "TATACONSUM.NS", "BRITANNIA.NS", "HINDUNILVR.NS", "ITC.NS",
            "NESTLEIND.NS", "DMART.NS", "TRENT.NS", "VBL.NS", "TANLA.NS",
            "GRINDWELL.NS", "SANDHAR.NS", "BALKRISIND.NS", "MOTHERSON.NS", "BOSCHLTD.NS",
            "M&MFIN.NS", "BAJFINANCE.NS", "CHOLAFIN.NS", "MUTHOOTFIN.NS", "MANAPPURAM.NS",
            "TATAPOWER.NS", "ADANIPORTS.NS", "GMRINFRA.NS", "L&TINFRA.NS", "IRB.NS",
            "PNCINFRA.NS", "RECLTD.NS", "PFC.NS", "REC.NS", "HUDCO.NS",
            "DLF.NS", "GODREJPROP.NS", "BRIGADE.NS", "PHOENIXLTD.NS", "OBEROIRLTY.NS",
            "PRESTIGE.NS", "GODREJWOOD.NS", "MAHINDRALIFE.NS", "HDFCLIFE.NS", "ICICIPRULI.NS",
            "SBILIFE.NS", "MAXFIN.NS", "PNBGRIFFIN.NS", "TATAMOTORS.NS", "M&M.NS",
            "MARUTI.NS", "EICHERMOT.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS", "TATAMTRDVR.NS",
        ]

        # Limit to selected number
        stocks_to_screen = nse_stocks[:num_stocks]

        results = []
        skipped = 0

        progress_bar = st.progress(0, text="Starting scanner...")
        status_text = st.empty()

        for idx, sym in enumerate(stocks_to_screen):
            progress = (idx + 1) / len(stocks_to_screen)
            progress_bar.progress(progress, text=f"Analyzing {sym} ({idx + 1}/{len(stocks_to_screen)})")
            status_text.text(f"Current: {sym} | Found: {len(results)} | Skipped: {skipped}")

            try:
                data = fetch_stock_data(sym)
                info = yf.Ticker(sym).info or {}

                # Fundamental metrics (for scoring, not strict filtering)
                pe = _safe_float(info.get("trailingPE") or info.get("forwardPE"))
                pb = _safe_float(info.get("priceToBook"))
                debt_to_equity = _safe_float(info.get("debtToEquity"))
                revenue_growth = _safe_float(info.get("revenueGrowth"))
                if revenue_growth and abs(revenue_growth) <= 1:
                    revenue_growth *= 100
                eps_growth = _safe_float(info.get("earningsQuarterlyGrowth"))
                if eps_growth and abs(eps_growth) <= 1:
                    eps_growth *= 100
                roe = _safe_float(info.get("returnOnEquity"))
                if roe and abs(roe) <= 1:
                    roe *= 100
                roce = _safe_float(info.get("returnOnAssets"))  # Proxy for ROCE
                if roce and abs(roce) <= 1:
                    roce *= 100
                market_cap = _safe_float(info.get("marketCap"))
                promoter_holding = _safe_float(info.get("heldPercentInsiders"))
                if promoter_holding and promoter_holding <= 1:
                    promoter_holding *= 100

                # Calculate 50 DMA and 200 DMA from historical data
                dma_50 = None
                dma_200 = None
                try:
                    hist = yf.Ticker(sym).history(period="1y")
                    if len(hist) >= 50:
                        dma_50 = hist['Close'].tail(50).mean()
                    if len(hist) >= 200:
                        dma_200 = hist['Close'].tail(200).mean()
                except:
                    pass

                current_price = data.get("current_price")

                # Skip if essential data is missing
                if pe is None or pb is None or roe is None or current_price is None:
                    skipped += 1
                    continue

                # Calculate dark horse score
                score = 0
                ocf_score = 0

                # PE score (15 pts) - lower is better
                pe_score = max(0, min(15, (25 - pe) / 20 * 15))
                score += pe_score

                # EPS growth score (15 pts)
                eps_score = max(0, min(15, (eps_growth - 10) / 40 * 15))
                score += eps_score

                # Debt + ROE score (15 pts)
                debt_score = max(0, min(7.5, (0.5 - debt_to_equity) / 0.5 * 7.5))
                roe_score = max(0, min(7.5, (roe - 12) / 28 * 7.5))
                score += debt_score + roe_score

                # Institutional interest score (15 pts) - proxy with volume
                avg_volume = _safe_float(info.get("averageVolume"))
                inst_score = 7.5 if avg_volume and avg_volume > 1000000 else 0
                score += inst_score

                # Price position score (15 pts) - near 52-week low
                week_52_low = data.get("week_52_low")
                week_52_high = data.get("week_52_high")
                if week_52_low and week_52_high and current_price:
                    position_52w = (current_price - week_52_low) / (week_52_high - week_52_low) * 100
                    price_score = max(0, min(15, (50 - position_52w) / 50 * 15))
                    score += price_score
                else:
                    price_score = 7.5
                    score += price_score

                # ROCE score (10 pts) - higher is better
                if roce:
                    roce_score = max(0, min(10, (roce - 10) / 20 * 10))
                    score += roce_score
                else:
                    roce_score = 5
                    score += roce_score

                # DMA trend score (10 pts) - price above 50 DMA and 200 DMA
                dma_score = 0
                if dma_50 and dma_200:
                    if current_price > dma_50 > dma_200:
                        dma_score = 10  # Strong uptrend
                    elif current_price > dma_50:
                        dma_score = 7  # Above 50 DMA
                    elif current_price > dma_200:
                        dma_score = 5  # Above 200 DMA
                    else:
                        dma_score = 2  # Below both DMAs
                elif dma_50:
                    if current_price > dma_50:
                        dma_score = 7
                    else:
                        dma_score = 3
                else:
                    dma_score = 5  # Default if DMA data unavailable
                score += dma_score

                # Entry/Exit point evaluation
                entry_point = None
                exit_point = None
                entry_signal = "HOLD"
                forecast_50w = None

                # Get 2-week historical data for entry analysis
                hist_2w = None
                try:
                    hist_2w = yf.Ticker(sym).history(period="2w")
                except:
                    pass

                if dma_50 and dma_200 and current_price:
                    # Entry point analysis using 2-week data
                    if hist_2w is not None and len(hist_2w) > 0:
                        recent_low = hist_2w['Low'].min()
                        recent_high = hist_2w['High'].max()
                        recent_trend = (current_price - hist_2w['Close'].iloc[0]) / hist_2w['Close'].iloc[0] * 100

                        # Determine entry point based on 2-week analysis
                        if current_price > dma_50:
                            # Price above 50 DMA - look for pullback to DMA or recent low
                            entry_point = min(dma_50, recent_low)
                            if current_price < dma_50 * 1.02 or current_price < recent_low * 1.03:
                                entry_signal = "BUY"
                            elif recent_trend < -5:  # Recent downtrend
                                entry_signal = "WAIT"
                        elif current_price > dma_200:
                            # Price between 50 and 200 DMA
                            entry_point = min(dma_200, recent_low)
                            if current_price < dma_200 * 1.02 or current_price < recent_low * 1.03:
                                entry_signal = "BUY"
                            elif recent_trend < -10:  # Strong recent downtrend
                                entry_signal = "WAIT"
                        else:
                            # Price below 200 DMA - current price is the entry point
                            entry_point = current_price
                            entry_signal = "BUY"
                    else:
                        # Fallback to original logic if 2-week data unavailable
                        if current_price > dma_50:
                            entry_point = dma_50
                            if current_price < dma_50 * 1.02:
                                entry_signal = "BUY"
                        elif current_price > dma_200:
                            entry_point = dma_200
                            if current_price < dma_200 * 1.02:
                                entry_signal = "BUY"
                        else:
                            # Price below 200 DMA - current price is the entry point
                            entry_point = current_price
                            entry_signal = "BUY"

                    # 50-week forecast for exit criteria
                    # Use historical volatility and trend to project 50-week target
                    try:
                        hist_1y = yf.Ticker(sym).history(period="1y")
                        if len(hist_1y) > 50:
                            # Calculate annualized return and volatility
                            returns = hist_1y['Close'].pct_change().dropna()
                            annual_return = (1 + returns.mean()) ** 252 - 1
                            volatility = returns.std() * (252 ** 0.5)

                            # Conservative forecast: expected return with risk adjustment
                            expected_50w_return = annual_return * 0.5  # Conservative estimate
                            risk_adjusted_return = expected_50w_return - (volatility * 0.3)

                            # Calculate exit point based on forecast
                            forecast_50w = current_price * (1 + risk_adjusted_return)

                            # Ensure exit point is reasonable (between 10% and 50% gain)
                            min_exit = entry_point * 1.10 if entry_point else current_price * 1.10
                            max_exit = entry_point * 1.50 if entry_point else current_price * 1.50
                            forecast_50w = max(min_exit, min(max_exit, forecast_50w))
                        else:
                            # Fallback if insufficient historical data
                            forecast_50w = current_price * 1.25  # 25% target
                    except:
                        forecast_50w = current_price * 1.25  # Default 25% target

                    # Final exit point: use forecast but cap at 52-week high
                    exit_point = forecast_50w
                    if week_52_high:
                        exit_point = min(exit_point, week_52_high * 0.95)

                # OCF score (25 pts) - highest weight
                ocf = _safe_float(info.get("operatingCashflow"))
                net_income = _safe_float(info.get("netIncomeToCommon"))
                revenue = _safe_float(info.get("totalRevenue"))

                if ocf and net_income:
                    # OCF > Net Profit (10 pts)
                    ocf_vs_profit = 10 if ocf > net_income else 5
                    ocf_score += ocf_vs_profit

                    # OCF to Revenue ratio (5 pts)
                    if revenue:
                        ocf_ratio = ocf / revenue
                        ocf_ratio_score = max(0, min(5, ocf_ratio * 100))
                        ocf_score += ocf_ratio_score

                    # Positive OCF (10 pts)
                    ocf_positive = 10 if ocf > 0 else 0
                    ocf_score += ocf_positive

                score += ocf_score

                # Generate reasoning
                reasons = []
                if pe < 15:
                    reasons.append(f"Low PE ({pe:.1f})")
                if eps_growth > 20:
                    reasons.append(f"Strong EPS growth ({eps_growth:.1f}%)")
                if debt_to_equity < 0.3:
                    reasons.append(f"Low debt ({debt_to_equity:.2f})")
                if roe > 18:
                    reasons.append(f"High ROE ({roe:.1f}%)")
                if roce and roce > 15:
                    reasons.append(f"High ROCE ({roce:.1f}%)")
                if dma_score >= 7:
                    reasons.append("Strong DMA trend")
                if ocf_score > 20:
                    reasons.append("Strong cash generation")

                reasoning = ", ".join(reasons[:3]) if reasons else "Balanced fundamentals"

                # Risk flags
                risks = []
                if debt_to_equity > 0.4:
                    risks.append("Moderate debt")
                if promoter_holding < 50:
                    risks.append("Low promoter holding")
                if pe > 20:
                    risks.append("High PE")

                risk_flag = ", ".join(risks) if risks else None

                results.append({
                    "symbol": sym,
                    "name": data.get("name", sym.removesuffix(NSE_SUFFIX)),
                    "sector": data.get("sector", "Unknown"),
                    "score": round(score, 1),
                    "ocf_score": round(ocf_score, 1),
                    "current_price": current_price,
                    "pe": pe,
                    "pb": pb,
                    "roe": roe,
                    "roce": roce,
                    "debt_to_equity": debt_to_equity,
                    "dma_50": dma_50,
                    "dma_200": dma_200,
                    "entry_point": entry_point,
                    "exit_point": exit_point,
                    "forecast_50w": forecast_50w,
                    "entry_signal": entry_signal,
                    "reasoning": reasoning,
                    "risk_flag": risk_flag,
                })

            except Exception as e:
                skipped += 1
                continue

        # Cleanup progress indicators
        progress_bar.empty()
        status_text.empty()

        # Calculate upside potential and sort by it
        for r in results:
            if r.get("entry_point") and r.get("exit_point"):
                r["upside_potential"] = ((r["exit_point"] - r["entry_point"]) / r["entry_point"]) * 100
            else:
                r["upside_potential"] = 0
        
        # Sort by upside potential in descending order
        results.sort(key=lambda x: x["upside_potential"], reverse=True)

        # Filter by min_score
        filtered_results = [r for r in results if r["score"] >= min_score]

        # If no results meet criteria, show top 3 from all scanned stocks
        if not filtered_results:
            if results:
                filtered_results = results[:3]
                st.warning(f"No stocks met your minimum score of {min_score}. Showing top 3 candidates from scanned stocks.")
            else:
                st.warning("No stocks had sufficient data for analysis. Try again later or check your internet connection.")

        st.session_state["scanner_results"] = filtered_results
        st.session_state["scanner_skipped"] = skipped
        st.session_state["scanner_timestamp"] = datetime.now().strftime("%d %b %Y, %I:%M %p")

        st.success(f"Scan complete! Found {len(filtered_results)} dark horse candidates out of {len(stocks_to_screen)} stocks screened.")
        st.rerun()

    # Display results
    if "scanner_results" in st.session_state and st.session_state["scanner_results"]:
        results = st.session_state["scanner_results"]
        skipped = st.session_state["scanner_skipped"]
        timestamp = st.session_state["scanner_timestamp"]

        st.caption(f"Last updated: {timestamp} | Skipped: {skipped} stocks (didn't meet criteria)")

        # Summary metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Dark Horses Found", len(results))
        m2.metric("Average Score", f"{sum(r['score'] for r in results) / len(results):.1f}")
        m3.metric("Top Score", f"{results[0]['score']:.1f}")

        # Results table
        st.markdown("### Dark Horse Candidates")

        # Filter controls
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        with filter_col1:
            sector_filter = st.selectbox("Filter by Sector", ["All"] + list(set(r["sector"] for r in results)))
        with filter_col2:
            sort_by = st.selectbox("Sort by", ["Upside Potential", "Score", "OCF Score", "PE", "ROE", "Price"])
        with filter_col3:
            sort_order = st.selectbox("Sort Order", ["Descending", "Ascending"])

        # Apply filters
        filtered_results = results
        if sector_filter != "All":
            filtered_results = [r for r in results if r["sector"] == sector_filter]

        # Sort
        reverse = sort_order == "Descending"
        if sort_by == "Score":
            filtered_results.sort(key=lambda x: x["score"], reverse=reverse)
        elif sort_by == "OCF Score":
            filtered_results.sort(key=lambda x: x["ocf_score"], reverse=reverse)
        elif sort_by == "Upside Potential":
            filtered_results.sort(key=lambda x: x.get("upside_potential", 0), reverse=reverse)
        elif sort_by == "PE":
            filtered_results.sort(key=lambda x: x["pe"], reverse=not reverse)
        elif sort_by == "ROE":
            filtered_results.sort(key=lambda x: x["roe"], reverse=reverse)
        elif sort_by == "Price":
            filtered_results.sort(key=lambda x: x["current_price"] or 0, reverse=reverse)

        display_data = []
        for idx, r in enumerate(filtered_results, 1):
            score_color = "🟢" if r["score"] >= 80 else "🟡" if r["score"] >= 60 else "🔴"
            signal_emoji = "🟢" if r.get("entry_signal") == "BUY" else "🟡" if r.get("entry_signal") == "HOLD" else "🔴"
            upside = r.get("upside_potential", 0)
            display_data.append({
                "Rank": idx,
                "Symbol": r["symbol"],
                "Name": r["name"][:30],
                "Sector": r["sector"][:20],
                "Score": f"{score_color} {r['score']}",
                "Signal": f"{signal_emoji} {r.get('entry_signal', '-')}",
                "Price": format_inr(r["current_price"]),
                "50 DMA": format_inr(r.get("dma_50")) if r.get("dma_50") else "-",
                "200 DMA": format_inr(r.get("dma_200")) if r.get("dma_200") else "-",
                "PE": f"{r['pe']:.1f}",
                "ROE": f"{r['roe']:.1f}%",
                "ROCE": f"{r.get('roce', 0):.1f}%" if r.get("roce") else "-",
                "D/E": f"{r['debt_to_equity']:.2f}",
                "Entry": format_inr(r.get("entry_point")) if r.get("entry_point") else "-",
                "Exit": format_inr(r.get("exit_point")) if r.get("exit_point") else "-",
                "Upside %": f"{upside:.1f}%" if upside else "-",
                "50W Forecast": format_inr(r.get("forecast_50w")) if r.get("forecast_50w") else "-",
                "Reasoning": r["reasoning"],
                "Risk": r["risk_flag"] or "-",
            })

        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Deep dive panel
        st.markdown("### Deep Dive Analysis")
        selected_stock = st.selectbox("Select a stock for deep dive analysis", [r["symbol"] for r in filtered_results])

        if selected_stock:
            stock_data = next((r for r in results if r["symbol"] == selected_stock), None)
            if stock_data:
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"#### {stock_data['name']}")
                    st.markdown(f"**Symbol:** {stock_data['symbol']}")
                    st.markdown(f"**Sector:** {stock_data['sector']}")
                    st.markdown(f"**Dark Horse Score:** {stock_data['score']}/100")
                    st.markdown(f"**OCF Score:** {stock_data['ocf_score']}/25")

                with col2:
                    st.markdown("#### Key Ratios")
                    st.markdown(f"**PE:** {stock_data['pe']:.1f}")
                    st.markdown(f"**PB:** {stock_data['pb']:.1f}")
                    st.markdown(f"**ROE:** {stock_data['roe']:.1f}%")
                    if stock_data.get('roce'):
                        st.markdown(f"**ROCE:** {stock_data['roce']:.1f}%")
                    st.markdown(f"**Debt/Equity:** {stock_data['debt_to_equity']:.2f}")
                    st.markdown(f"**Current Price:** {format_inr(stock_data['current_price'])}")
                    if stock_data.get('dma_50'):
                        st.markdown(f"**50 DMA:** {format_inr(stock_data['dma_50'])}")
                    if stock_data.get('dma_200'):
                        st.markdown(f"**200 DMA:** {format_inr(stock_data['dma_200'])}")

                # What makes it a dark horse
                st.markdown("#### What makes it a Dark Horse?")
                reasons = []
                if stock_data['pe'] < 15:
                    reasons.append(f"✓ Attractive valuation with PE of {stock_data['pe']:.1f}")
                if stock_data['ocf_score'] > 20:
                    reasons.append("✓ Strong operating cash flow generation")
                if stock_data['roe'] > 18:
                    reasons.append(f"✓ High return on equity at {stock_data['roe']:.1f}%")
                if stock_data['debt_to_equity'] < 0.3:
                    reasons.append(f"✓ Low debt with D/E ratio of {stock_data['debt_to_equity']:.2f}")
                if not reasons:
                    reasons.append("✓ Balanced fundamentals across multiple metrics")

                for reason in reasons:
                    st.markdown(f"- {reason}")

                # Risk factors
                if stock_data['risk_flag']:
                    st.markdown("#### Risk Factors")
                    risks = stock_data['risk_flag'].split(", ")
                    for risk in risks:
                        st.markdown(f"- ⚠️ {risk}")

                # Entry/Exit recommendations
                st.markdown("#### Entry & Exit Recommendations")
                if stock_data.get('entry_signal'):
                    signal_color = "🟢" if stock_data['entry_signal'] == "BUY" else "🟡" if stock_data['entry_signal'] == "HOLD" else "🔴"
                    st.markdown(f"**Current Signal:** {signal_color} {stock_data['entry_signal']}")
                if stock_data.get('entry_point'):
                    st.markdown(f"**Suggested Entry Price:** {format_inr(stock_data['entry_point'])}")
                    st.caption("Based on 2-week historical analysis and DMA support levels")
                if stock_data.get('exit_point'):
                    st.markdown(f"**Target Exit Price:** {format_inr(stock_data['exit_point'])}")
                    st.caption("Based on 50-week forecast using historical volatility and trend")
                    if stock_data.get('current_price') and stock_data.get('entry_point'):
                        potential_gain = ((stock_data['exit_point'] - stock_data['entry_point']) / stock_data['entry_point']) * 100
                        st.markdown(f"**Potential Gain:** {potential_gain:.1f}%")
                if stock_data.get('forecast_50w'):
                    st.markdown(f"**50-Week Forecast:** {format_inr(stock_data['forecast_50w'])}")

                # Score breakdown (simple bar chart)
                st.markdown("#### Score Breakdown")
                score_components = {
                    "PE Score": 15,
                    "EPS Growth": 15,
                    "Debt + ROE": 15,
                    "Institutional Interest": 15,
                    "Price Position": 15,
                    "ROCE Score": 10,
                    "DMA Trend": 10,
                    "OCF Score": 25,
                }

                # Estimate component scores based on total score
                estimated_scores = {}
                remaining_score = stock_data['score']
                for component, max_score in score_components.items():
                    if component == "OCF Score":
                        estimated_scores[component] = stock_data['ocf_score']
                        remaining_score -= stock_data['ocf_score']
                    else:
                        # Distribute remaining score proportionally
                        component_score = min(max_score, max_score * (remaining_score / sum(v for k, v in score_components.items() if k != "OCF Score")))
                        estimated_scores[component] = round(component_score, 1)

                score_df = pd.DataFrame([
                    {"Component": k, "Score": v, "Max": score_components[k]}
                    for k, v in estimated_scores.items()
                ])

                score_fig = px.bar(
                    score_df,
                    x="Component",
                    y="Score",
                    color="Score",
                    color_continuous_scale="RdYlGn",
                    range_y=[0, 25],
                    title="Score Breakdown by Component",
                )
                apply_chart_theme(score_fig, height=300)
                st.plotly_chart(score_fig, use_container_width=True)

        # Sector distribution
        if results:
            st.markdown("### Sector Distribution")
            sectors = {}
            for r in results:
                sectors[r["sector"]] = sectors.get(r["sector"], 0) + 1

            sector_df = pd.DataFrame([
                {"Sector": k, "Count": v}
                for k, v in sorted(sectors.items(), key=lambda x: -x[1])
            ])

            # Create heatmap-style visualization using bar chart
            sector_fig = px.bar(
                sector_df,
                x="Count",
                y="Sector",
                orientation="h",
                color="Count",
                color_continuous_scale="RdYlGn",
                title="Dark Horses by Sector",
            )
            apply_chart_theme(sector_fig, height=300)
            sector_fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(sector_fig, use_container_width=True)

    else:
        st.info("Click 'Run Scanner' to start screening stocks.")

last_refresh = datetime.now().strftime("%d %b %Y, %I:%M:%S %p")
st.markdown(
    f'<p class="footer-meta">Last refresh · {last_refresh}</p>',
    unsafe_allow_html=True,
)
