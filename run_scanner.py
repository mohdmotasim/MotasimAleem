"""
Standalone Dark Horse Scanner script for scheduled execution.
Run this script independently to scan stocks and save results.
"""
import json
import os
from datetime import datetime as dt_datetime
import yfinance as yf
import pandas as pd
import requests

NSE_SUFFIX = ".NS"
SCANNER_RESULTS_FILE = "scanner_results.json"
SCANNER_PROGRESS_FILE = "scanner_progress.json"


def fetch_nifty_500_stocks():
    """
    Fetch Nifty 500 stocks from NSE website.
    Returns list of stock symbols with .NS suffix.
    """
    try:
        # NSE Nifty 500 CSV URL
        url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Parse CSV
        df = pd.read_csv(pd.io.common.StringIO(response.text))
        
        # Extract symbols and add .NS suffix
        symbols = df['Symbol'].tolist()
        nifty_500_stocks = [f"{sym}.NS" for sym in symbols]
        
        print(f"Fetched {len(nifty_500_stocks)} stocks from Nifty 500")
        return nifty_500_stocks
    except Exception as e:
        print(f"Error fetching Nifty 500 stocks: {e}")
        # Fallback to a basic list if fetch fails
        return []


def _safe_float(value):
    """Safely convert to float, return None if conversion fails."""
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


def calculate_dark_horse_score(sym, info, ticker):
    """
    Calculate Dark Horse score using the same logic as the Scanner tab in app.py.
    """
    # Fetch fundamental metrics
    pe = _safe_float(info.get("trailingPE") or info.get("forwardPE"))
    pb = _safe_float(info.get("priceToBook"))
    debt_to_equity = _safe_float(info.get("debtToEquity"))
    roe = _safe_float(info.get("returnOnEquity"))
    if roe and abs(roe) <= 1:
        roe *= 100
    roce = _safe_float(info.get("returnOnAssets"))
    if roce and abs(roce) <= 1:
        roce *= 100
    
    # Get current price and DMA data
    current_price = _safe_float(info.get("currentPrice") or info.get("regularMarketPrice"))
    dma_50 = None
    dma_200 = None
    week_52_high = _safe_float(info.get("fiftyTwoWeekHigh"))
    
    try:
        hist = ticker.history(period="1y")
        if len(hist) >= 50:
            dma_50 = hist['Close'].tail(50).mean()
        if len(hist) >= 200:
            dma_200 = hist['Close'].tail(200).mean()
    except:
        pass
    
    # Calculate scores
    value_score = 0
    fundamentals_score = 0
    momentum_score = 0
    risk_penalty = 0
    risk_flags = []
    
    # CATEGORY 1 — VALUE (35 pts total)
    sector_median_pe = 20
    if pe:
        pe_discount_pct = ((sector_median_pe - pe) / sector_median_pe) * 100
        if pe_discount_pct >= 20:
            pe_vs_sector_score = 12
        elif pe_discount_pct <= 0:
            pe_vs_sector_score = 0
        else:
            pe_vs_sector_score = (pe_discount_pct / 20) * 12
        pe_vs_sector_score = max(0, min(12, pe_vs_sector_score))
    else:
        pe_vs_sector_score = 0
    value_score += pe_vs_sector_score
    
    if pb:
        if pb < 2:
            pb_score = 8
        elif pb > 5:
            pb_score = 0
        else:
            pb_score = 8 * ((5 - pb) / 3)
        pb_score = max(0, min(8, pb_score))
    else:
        pb_score = 0
    value_score += pb_score
    
    if dma_200 and current_price:
        price_vs_200dma_pct = ((dma_200 - current_price) / dma_200) * 100
        if price_vs_200dma_pct >= 10:
            price_vs_200dma_score = 8
        elif price_vs_200dma_pct <= 0:
            price_vs_200dma_score = 0
        else:
            price_vs_200dma_score = (price_vs_200dma_pct / 10) * 8
        price_vs_200dma_score = max(0, min(8, price_vs_200dma_score))
    else:
        price_vs_200dma_score = 0
    value_score += price_vs_200dma_score
    
    if week_52_high and current_price:
        price_vs_52w_high_pct = ((week_52_high - current_price) / week_52_high) * 100
        if price_vs_52w_high_pct >= 30:
            price_vs_52w_high_score = 7
        elif price_vs_52w_high_pct <= 5:
            price_vs_52w_high_score = 0
        else:
            price_vs_52w_high_score = ((price_vs_52w_high_pct - 5) / 25) * 7
        price_vs_52w_high_score = max(0, min(7, price_vs_52w_high_score))
    else:
        price_vs_52w_high_score = 0
    value_score += price_vs_52w_high_score
    
    # CATEGORY 2 — FUNDAMENTALS (40 pts total)
    # ROE → 15 pts. Score = 15 if ROE > 25%, 10 if ROE 15–25%, 5 if ROE 10–15%, 0 if below 10%
    if roe:
        if roe > 25:
            roe_score = 15
        elif roe >= 15:
            roe_score = 10
        elif roe >= 10:
            roe_score = 5
        else:
            roe_score = 0
    else:
        roe_score = 0
    fundamentals_score += roe_score
    
    # ROCE → 10 pts. Score = 10 if ROCE > 20%, 7 if 15–20%, 4 if 10–15%, 0 if below 10%
    if roce:
        if roce > 20:
            roce_score = 10
        elif roce >= 15:
            roce_score = 7
        elif roce >= 10:
            roce_score = 4
        else:
            roce_score = 0
    else:
        roce_score = 0
    fundamentals_score += roce_score
    
    # OCF Score → 10 pts. Normalize from 25 to 10
    operating_cash_flow = _safe_float(info.get("operatingCashflow"))
    net_income = _safe_float(info.get("netIncomeToCommon"))
    revenue = _safe_float(info.get("totalRevenue"))
    ocf_raw_score = 0
    if operating_cash_flow and net_income:
        ocf_vs_profit = 10 if operating_cash_flow > net_income else 5
        ocf_raw_score += ocf_vs_profit
    if revenue:
        ocf_ratio = operating_cash_flow / revenue
        ocf_ratio_score = max(0, min(5, ocf_ratio * 100))
        ocf_raw_score += ocf_ratio_score
    ocf_positive = 10 if operating_cash_flow > 0 else 0
    ocf_raw_score += ocf_positive
    ocf_normalized_score = (ocf_raw_score / 25) * 10
    ocf_normalized_score = max(0, min(10, ocf_normalized_score))
    fundamentals_score += ocf_normalized_score
    
    # Debt/Equity → 5 pts. Score = 5 if D/E < 0.5, 3 if 0.5–1.0, 1 if 1.0–2.0, 0 if above 2.0
    if debt_to_equity:
        if debt_to_equity < 0.5:
            de_score = 5
        elif debt_to_equity <= 1.0:
            de_score = 3
        elif debt_to_equity <= 2.0:
            de_score = 1
        else:
            de_score = 0
    else:
        de_score = 0
    fundamentals_score += de_score
    
    # CATEGORY 3 — MOMENTUM (15 pts total)
    # Price vs 50 DMA → 8 pts. Score = 8 if price is above 50 DMA (recovery signal), 0 if below
    if dma_50 and current_price:
        if current_price > dma_50:
            price_vs_50dma_score = 8
        else:
            price_vs_50dma_score = 0
    else:
        price_vs_50dma_score = 0
    momentum_score += price_vs_50dma_score
    
    # Existing Dark Horse score → 7 pts. Normalize current dark horse score to 7 pts
    dh_base_score = (roe_score / 15) * 3 + (roce_score / 10) * 2 + (price_vs_50dma_score / 8) * 2
    dh_normalized_score = (dh_base_score / 7) * 7
    dh_normalized_score = max(0, min(7, dh_normalized_score))
    momentum_score += dh_normalized_score
    
    # CATEGORY 4 — RISK PENALTY (subtract up to 10 pts)
    # D/E > 2.0 → subtract 5 pts
    if debt_to_equity and debt_to_equity > 2.0:
        risk_penalty -= 5
        risk_flags.append("High D/E (>2.0)")
    # PE > 30 → subtract 3 pts
    if pe and pe > 30:
        risk_penalty -= 3
        risk_flags.append("High PE (>30)")
    # ROCE < 10% → subtract 2 pts
    if roce and roce < 10:
        risk_penalty -= 2
        risk_flags.append("Low ROCE (<10%)")
    risk_penalty = max(-10, risk_penalty)  # Cap at -10
    
    # Total score
    total_score = value_score + fundamentals_score + momentum_score + risk_penalty
    
    return {
        "score": round(total_score, 1),
        "value_score": round(value_score, 1),
        "fundamentals_score": round(fundamentals_score, 1),
        "momentum_score": round(momentum_score, 1),
        "risk_penalty": round(risk_penalty, 1),
        "risk_flags": risk_flags,
    }


def run_scanner(min_score=60):
    """Run the Dark Horse scanner and save results using Nifty 500 stocks."""
    print(f"Starting Dark Horse Scanner at {dt_datetime.now()}")
    print(f"Scanning Nifty 500 stocks with minimum score {min_score}")
    
    # Fetch Nifty 500 stocks
    stocks_to_screen = fetch_nifty_500_stocks()
    if not stocks_to_screen:
        print("Failed to fetch Nifty 500 stocks. Exiting.")
        return
    
    results = []
    skipped = 0
    
    for idx, sym in enumerate(stocks_to_screen):
        try:
            ticker = yf.Ticker(sym)
            info = ticker.info
            
            current_price = _safe_float(info.get("currentPrice") or info.get("regularMarketPrice"))
            if not current_price:
                skipped += 1
                continue
            
            week_52_high = _safe_float(info.get("fiftyTwoWeekHigh"))
            pe = _safe_float(info.get("trailingPE") or info.get("forwardPE"))
            pb = _safe_float(info.get("priceToBook"))
            roe = _safe_float(info.get("returnOnEquity"))
            if roe and abs(roe) <= 1:
                roe *= 100
            roce = _safe_float(info.get("returnOnAssets"))
            if roce and abs(roce) <= 1:
                roce *= 100
            debt_to_equity = _safe_float(info.get("debtToEquity"))
            
            # Get DMA data
            dma_50 = None
            dma_200 = None
            try:
                hist = ticker.history(period="1y")
                if len(hist) >= 50:
                    dma_50 = hist['Close'].tail(50).mean()
                if len(hist) >= 200:
                    dma_200 = hist['Close'].tail(200).mean()
            except:
                pass
            
            # Calculate score
            score_data = calculate_dark_horse_score(sym, info, ticker)
            
            # Entry/Exit point evaluation
            entry_point = None
            exit_point = None
            entry_signal = "HOLD"
            forecast_50w = None
            
            hist_2w = None
            try:
                hist_2w = ticker.history(period="1mo")
            except:
                pass
            
            if dma_50 and dma_200 and current_price:
                if hist_2w is not None and len(hist_2w) > 0:
                    recent_low = hist_2w['Low'].min()
                    recent_high = hist_2w['High'].max()
                    recent_trend = (current_price - hist_2w['Close'].iloc[0]) / hist_2w['Close'].iloc[0] * 100
                    
                    if current_price > dma_50:
                        entry_point = min(dma_50, recent_low)
                        if current_price < dma_50 * 1.02 or current_price < recent_low * 1.03:
                            entry_signal = "BUY"
                        elif recent_trend < -5:
                            entry_signal = "WAIT"
                    elif current_price > dma_200:
                        entry_point = min(dma_200, recent_low)
                        if current_price < dma_200 * 1.02 or current_price < recent_low * 1.03:
                            entry_signal = "BUY"
                        elif recent_trend < -5:
                            entry_signal = "WAIT"
                    
                    if entry_point and dma_200:
                        upside = ((dma_200 - entry_point) / entry_point) * 100
                        exit_point = entry_point * (1 + upside / 100)
                        forecast_50w = upside
            
            # Generate reasoning
            reasons = []
            if roe and roe > 20:
                reasons.append(f"High ROE ({roe:.1f}%)")
            if roce and roce > 15:
                reasons.append(f"Strong ROCE ({roce:.1f}%)")
            if debt_to_equity and debt_to_equity < 0.3:
                reasons.append(f"Low debt ({debt_to_equity:.2f})")
            if score_data["value_score"] >= 25:
                reasons.append("Strong value metrics")
            if score_data["fundamentals_score"] >= 30:
                reasons.append("Solid fundamentals")
            if score_data["momentum_score"] >= 10:
                reasons.append("Positive momentum")
            
            reasoning = ", ".join(reasons[:3]) if reasons else "Balanced fundamentals"
            
            # Risk flags
            risks = []
            if debt_to_equity and debt_to_equity > 0.4:
                risks.append("Moderate debt")
            if pe and pe > 20:
                risks.append("High PE")
            
            risk_flag = ", ".join(risks) if risks else None
            
            results.append({
                "symbol": sym,
                "name": info.get("longName", sym.removesuffix(NSE_SUFFIX)),
                "sector": info.get("sector", "Unknown"),
                "score": score_data["score"],
                "value_score": score_data["value_score"],
                "fundamentals_score": score_data["fundamentals_score"],
                "momentum_score": score_data["momentum_score"],
                "risk_penalty": score_data["risk_penalty"],
                "risk_flags": score_data.get("risk_flags", []),
                "ocf_score": score_data.get("ocf_score", 0),
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
            
            if (idx + 1) % 10 == 0:
                print(f"Processed {idx + 1}/{len(stocks_to_screen)} stocks...")
            
        except Exception as e:
            skipped += 1
            print(f"Error processing {sym}: {e}")
            continue
    
    # Calculate upside potential and sort
    for r in results:
        if r.get("entry_point") and r.get("exit_point"):
            r["upside_potential"] = ((r["exit_point"] - r["entry_point"]) / r["entry_point"]) * 100
        else:
            r["upside_potential"] = 0
    
    results.sort(key=lambda x: x["upside_potential"], reverse=True)
    
    # Filter by min_score
    filtered_results = [r for r in results if r["score"] >= min_score]
    
    if not filtered_results and results:
        filtered_results = results[:3]
    
    # Save results
    output = {
        "results": filtered_results,
        "skipped": skipped,
        "timestamp": dt_datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "num_stocks_scanned": len(stocks_to_screen),
        "min_score": min_score,
    }
    
    with open(SCANNER_RESULTS_FILE, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Scanner completed at {dt_datetime.now()}")
    print(f"Results saved to {SCANNER_RESULTS_FILE}")
    print(f"Found {len(filtered_results)} stocks meeting criteria")
    print(f"Skipped {skipped} stocks due to errors")


if __name__ == "__main__":
    # Scan Nifty 500 stocks with minimum score 60
    run_scanner(min_score=60)
