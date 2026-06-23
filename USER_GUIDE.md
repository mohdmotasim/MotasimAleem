# Aleem's Investment Dashboard - Complete User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [App Overview](#app-overview)
4. [Research Tab](#research-tab)
5. [Dark Horse Scanner Tab](#dark-horse-scanner-tab)
6. [Portfolio Tab](#portfolio-tab)
7. [Understanding Metrics](#understanding-metrics)
8. [Conviction Tiers](#conviction-tiers)
9. [Tips & Best Practices](#tips--best-practices)
10. [FAQ](#faq)

---

## Introduction

Welcome to Aleem's Investment Dashboard! This is a comprehensive stock research and portfolio management tool designed for NSE (National Stock Exchange of India) investors. The dashboard helps you:

- **Research stocks** with detailed fundamental and technical analysis
- **Screen for "Dark Horse" stocks** - undervalued companies with strong fundamentals
- **Manage your portfolio** with conviction-based tracking
- **Time your entries** using technical indicators
- **Track catalysts** that could drive stock prices

This guide explains every feature in simple, easy-to-understand language.

---

## Getting Started

### What You Need
- Internet connection (the app fetches live data from Yahoo Finance)
- Basic understanding of stock market terms (explained in this guide)
- No software installation - runs in your browser

### How to Access
- **Local**: Run the app on your computer using Streamlit
- **Cloud**: Access via the web URL (if deployed on Streamlit Cloud)

### First Steps
1. **Research Tab**: Start by searching for a stock you're interested in
2. **Scanner Tab**: Run the Dark Horse Scanner to discover new opportunities
3. **Portfolio Tab**: Add stocks you own or are tracking

---

## App Overview

The dashboard has **4 main tabs**:

| Tab | Purpose | Best For |
|-----|---------|----------|
| **Research** | Deep dive into individual stocks | Analyzing specific companies you're interested in |
| **Dark Horse Scanner** | Screen for undervalued stocks | Finding new investment opportunities |
| **Portfolio** | Track holdings & conviction | Managing your actual investments |
| **Conviction Board** (Sidebar) | Organize stocks by conviction level | Categorizing stocks by your confidence level |

---

## Research Tab

### What It Does
The Research tab provides a comprehensive analysis of any NSE stock you search for. It combines fundamental analysis (company health), technical analysis (price trends), and sentiment analysis (news flow).

### How to Use

#### 1. Search for a Stock
- Use the search bar at the top
- Type any letter to see matching NSE stocks
- Click on a stock to load its analysis

#### 2. Understanding the Analysis

**Header Section**
- **Stock Name & Symbol**: Company name and ticker (e.g., "TATASTEEL.NS")
- **Sector & Industry**: Which business the company is in
- **Dark Horse Badge**: Color-coded score (Green/Amber/Red) based on overall quality

**Key Metrics (Top Row)**
- **Price (INR)**: Current stock price
- **Day Change %**: How much the price changed today
- **P/E Ratio**: Price-to-Earnings ratio (explained in Metrics section)
- **Market Cap**: Total company value in rupees

**Entry Timing Panel**
- **52-week position**: Where the current price sits within the stock's 52-week range
- **Below all-time high**: How far the price is from its highest ever price
- **Relative strength (1Y)**: How the stock performed vs S&P 500 over 1 year

**Buy Zone**
- Set your preferred buy range (low and high prices)
- The app alerts you when the price enters your buy zone
- Helps you avoid buying at the wrong time

**Dip Alert**
- Set a target price for a dip you want to buy at
- Get notified when the price reaches that level

**1-Year Price Chart**
- Visual representation of price movement over the past year
- Helps identify trends and patterns

**Fundamentals Table**
Key financial metrics in one place:
- P/E Ratio, EPS, Book Value
- Operating Cash Flow, Free Cash Flow
- Beta (volatility measure)

**Analysis Verdict**
The app analyzes three factors to give you a stance:
- **Momentum**: Is the price moving up or down?
- **52-week Position**: Is it near highs or lows?
- **News Sentiment**: Is recent news positive or negative?

**Possible Verdicts:**
- 🟢 **Bullish**: Positive signals - good for buying
- 🟡 **Neutral**: Mixed signals - wait and watch
- 🔴 **Bearish**: Negative signals - avoid or sell

**News Summary**
- Recent news headlines about the stock
- Color-coded by sentiment (green = positive, red = negative)

---

## Dark Horse Scanner Tab

### What It Does
The Dark Horse Scanner screens NSE stocks to find "Dark Horses" - undervalued companies with strong fundamentals that have the potential to become multibaggers.

### How to Use

#### 1. Run the Scanner
- Set the **Minimum Dark Horse Score** (default: 60)
- Click **"Run Scanner"**
- The app scans Nifty 500 stocks (takes 2-3 minutes)

#### 2. Understanding the Results

**Summary Metrics**
- **Total Scanned**: How many stocks were analyzed
- **Qualified**: How many met your minimum score
- **Top Score**: Best score among all scanned stocks

**Results Table Columns**

| Column | What It Means |
|--------|---------------|
| **Rank** | Ranking by upside potential (highest first) |
| **Symbol** | Stock ticker symbol |
| **Name** | Company name (truncated to 30 chars) |
| **Sector** | Industry sector (truncated to 20 chars) |
| **Score** | Overall Dark Horse score (🟢≥80, 🟡≥60, 🔴<60) |
| **Quality** | Quality bonus from Piotroski F-score, promoter trend, interest coverage |
| **Value** | Value score (PE, PB, price position) |
| **Fund** | Fundamentals score (ROE, ROCE, debt, FCF) |
| **Mom** | Momentum score (50DMA, revenue growth) |
| **Risk** | Risk penalty (negative for risks) |
| **Signal** | Entry signal (BUY NOW, BUY ON PULLBACK, WATCH) |
| **Volume** | Volume signal (ACCUMULATION, DISTRIBUTION, etc.) |
| **Catalyst** | Catalyst score (if tagged) |
| **Rev CAGR** | 3-year revenue growth rate |
| **Price** | Current stock price |
| **PE** | Price-to-Earnings ratio |
| **Upside** | Potential upside to fair value |

#### 3. Using Filters

**Filter by Sector**
- Narrow down to specific sectors (IT, Pharma, Banking, etc.)
- Useful if you want to focus on particular industries

**Filter by Signal**
- **BUY NOW**: Strong buy signal - price is at attractive entry point
- **BUY ON PULLBACK**: Good stock but wait for a dip before buying
- **WATCH**: Monitor but don't buy yet
- **All**: Show all signals

**Volume Signal Filter**
- **All**: Show all stocks regardless of volume
- **Accumulation Only**: Show only stocks with buying pressure (good for finding institutional buying)
- **Exclude Distribution**: Hide stocks with selling pressure

**Catalyst Status Filter**
- **All**: Show all stocks
- **Tagged Only**: Stocks where you've identified a catalyst
- **High Conviction Only**: Stocks with strong catalysts (score ≥ 7)
- **Untagged Only**: Stocks needing catalyst review

**Sort Options**
- **Upside Potential**: Sort by potential gain to fair value
- **Score**: Sort by Dark Horse score
- **PE**: Sort by P/E ratio (lower = cheaper)
- **ROE**: Sort by Return on Equity (higher = better)
- **Price**: Sort by stock price
- **Volume Signal**: Sort by volume quality (accumulation first)
- **Revenue CAGR**: Sort by revenue growth rate

#### 4. Deep Dive Analysis

Click on any stock in the results to see detailed analysis:

**Stock Details**
- Current price, P/E, P/B, ROE, ROCE
- Debt-to-Equity ratio
- DMA (50-day and 200-day moving averages)

**Score Breakdown**
- Visual chart showing how the score was calculated
- Components: PE Score, EPS Growth, Debt + ROE, etc.

**What Makes It a Dark Horse?**
- Reasons why this stock scored well
- Examples: "Low PE (12.5)", "High ROE (22.3%)", "Low debt (0.15)"

**Risk Factors**
- Any red flags identified
- Examples: "High PE (>30)", "High Debt (>2.0)", "Low ROCE (<10%)"

**Entry & Exit Recommendations**
- **Entry Point**: Suggested buy price
- **Fair Value**: Estimated fair price
- **Upside Potential**: Percentage gain to fair value
- **Exit Zones**: Three target prices for selling (20%, fair value, 15% above fair value)
- **Stop Loss**: Price to sell at to limit losses

**Volume Signal Badge**
- **ACCUMULATION**: Buying pressure - good sign
- **DISTRIBUTION**: Selling pressure - caution
- **NEUTRAL**: No clear direction
- **INACTIVE**: Low volume

**Catalyst Tagging**
Tag what could drive the stock price up:
- **Catalyst Type**: Earnings Recovery, Sector Re-rating, Policy Tailwind, etc.
- **Timeline**: Near-term (0-6 months), Medium-term (6-12 months), Long-term (12+ months)
- **Notes**: Your personal notes about the catalyst
- Click "Save Catalyst" to store it

**Data Quality Flag**
- Warning if data is limited (e.g., no analyst target)
- Helps you understand if estimates are approximate

**Sector Distribution**
- Chart showing which sectors dominate your scan results

---

## Portfolio Tab

### What It Does
The Portfolio tab helps you track your actual stock holdings and monitor their performance.

### How to Use

#### 1. Add a Holding
- Enter **Symbol** (e.g., TCS.NS)
- Enter **Quantity** (number of shares)
- Enter **Purchase Price** (price per share)
- Click **"Add Holding"**

#### 2. View Holdings

**Summary Metrics**
- **Total Invested**: Total amount you invested
- **Current Value**: Current value of your holdings
- **Total Profit/Loss**: Overall gain or loss (amount and percentage)

**Holdings Detail Table**
- Symbol, Name, Quantity
- Purchase Price, Current Price
- Invested amount, Current Value
- Profit/Loss (amount and percentage)

#### 3. Manage Holdings

**Edit a Holding**
- Click on a holding to expand it
- Change quantity or purchase price
- Click **"Update"** to save changes

**Remove a Holding**
- Click **"Remove"** to delete a holding from your portfolio

---

## Conviction Tiers (Sidebar)

### What They Are
Conviction tiers help you categorize stocks by your confidence level in them. This is a personal organization system, not a rating from the app.

### The Three Tiers

**Tier 1 - High Conviction**
- **Name**: "Core Holdings - High Conviction"
- **Hint**: Stocks you're most confident about
- **Use for**: Your best picks, long-term holdings

**Tier 2 - Medium Conviction**
- **Name**: "Watchlist - Medium Conviction"
- **Hint**: Stocks you're actively monitoring
- **Use for**: Stocks you're considering buying or recently bought

**Tier 3 - Thesis & Sizing**
- **Name**: "Thesis & Sizing"
- **Hint**: Document your investment thesis and position sizing
- **Use for**: Detailed analysis and allocation planning

### How to Use

#### Add to Conviction Tier
1. Research a stock in the Research tab
2. In the sidebar, click **"Add to Conviction"**
3. Select which tier to add it to

#### Move Between Tiers
1. In the sidebar, find the stock in its current tier
2. Use the **"Move to"** dropdown to select a different tier
3. The stock automatically moves to the new tier

#### Remove from Conviction
1. Find the stock in its tier
2. Click **"×"** to remove it

#### Tier 3 - Thesis & Sizing
For Tier 3 stocks, you can:
- **Investment Thesis**: Write why you believe in this stock
- **Allocation %**: Set what percentage of your portfolio this should be
- Click **"Save"** to store your thesis and allocation

---

## Understanding Metrics

### Fundamental Metrics

#### P/E Ratio (Price-to-Earnings)
**What it is**: How much you pay for each rupee of company earnings

**In simple terms**: 
- P/E of 20 means you're paying ₹20 for every ₹1 the company earns
- Lower P/E = cheaper (but could mean the company is struggling)
- Higher P/E = expensive (but could mean high growth expected)

**Good range**: 10-25 for most Indian stocks
- Below 10: Very cheap (or company has problems)
- Above 30: Expensive (or high-growth company)

#### P/B Ratio (Price-to-Book)
**What it is**: How much you pay for each rupee of company assets

**In simple terms**:
- P/B of 2 means you're paying ₹2 for every ₹1 of the company's net assets
- Below 1: You're buying assets for less than they're worth (good value)
- Above 3: You're paying a premium for the company

**Good range**: 1-3 for most stocks
- Below 1: Undervalued (or company has hidden problems)
- Above 5: Very expensive

#### ROE (Return on Equity)
**What it is**: How efficiently the company uses shareholder money to generate profit

**In simple terms**:
- ROE of 20% means the company generates ₹20 profit for every ₹100 of shareholder equity
- Higher is better - shows efficient use of capital

**Good range**: 15-25% for quality companies
- Above 25%: Excellent (but check if sustainable)
- Below 10%: Poor (company not using capital efficiently)

#### ROCE (Return on Capital Employed)
**What it is**: Similar to ROE but includes debt - shows overall efficiency of all capital

**In simple terms**:
- ROCE of 15% means the company generates ₹15 profit for every ₹100 of total capital (equity + debt)
- More comprehensive than ROE because it includes debt

**Good range**: 12-20% for quality companies
- Above 20%: Excellent
- Below 10%: Poor

#### Debt-to-Equity Ratio
**What it is**: How much debt the company has compared to its equity

**In simple terms**:
- D/E of 0.5 means the company has ₹50 debt for every ₹100 equity
- Lower is generally safer - less debt means less risk

**Good range**: 0-1 for conservative investors
- 0-0.5: Very safe (low debt)
- 0.5-1: Moderate debt
- Above 1: High debt (risky but can boost returns)

#### EPS (Earnings Per Share)
**What it is**: Profit allocated to each outstanding share

**In simple terms**:
- EPS of ₹10 means the company earns ₹10 profit for each share
- Growing EPS over time is a good sign

#### Book Value
**What it is**: Net asset value per share (assets minus liabilities)

**In simple terms**:
- Book value of ₹100 means each share represents ₹100 of net assets
- If price is below book value, you're buying assets cheap

#### Operating Cash Flow
**What it is**: Cash generated from core business operations

**In simple terms**:
- Shows if the business actually generates cash (not just accounting profit)
- Positive and growing is good

#### Free Cash Flow
**What it is**: Cash left after paying for operations and capital expenditures

**In simple terms**:
- Money the company can use for dividends, buybacks, or growth
- Positive FCF is a sign of a healthy business

#### Beta
**What it is**: Measure of stock volatility relative to the market

**In simple terms**:
- Beta of 1: Moves in line with the market
- Beta above 1: More volatile than the market (higher risk, higher potential return)
- Beta below 1: Less volatile than the market (lower risk, lower potential return)

**Good range**: 0.8-1.2 for most investors
- Below 0.8: Defensive (less volatile)
- Above 1.2: Aggressive (more volatile)

### Technical Metrics

#### 52-Week High/Low
**What it is**: Highest and lowest price in the past year

**In simple terms**:
- Shows the price range over the past year
- Helps understand if current price is near highs or lows

#### 52-Week Position
**What it is**: Where current price sits within the 52-week range (0-100%)

**In simple terms**:
- Position of 70% means price is closer to 52-week high
- Position of 30% means price is closer to 52-week low
- Near lows (30% or below) can be good entry points
- Near highs (70% or above) might be overvalued

#### DMA (Daily Moving Average)
**What it is**: Average price over a specific period (50-day, 200-day)

**In simple terms**:
- 50 DMA: Average price over last 50 trading days (~2.5 months)
- 200 DMA: Average price over last 200 trading days (~10 months)
- Price above DMA = uptrend (good)
- Price below DMA = downtrend (bad)

**Golden Cross**: 50 DMA crosses above 200 DMA (bullish signal)
**Death Cross**: 50 DMA crosses below 200 DMA (bearish signal)

#### Volume
**What it is**: Number of shares traded

**In simple terms**:
- High volume = lots of trading activity (interest in the stock)
- Low volume = little trading activity (no interest)
- Volume should confirm price moves (up on high volume is more reliable)

#### Volume Signal
**What the app calculates**:
- **ACCUMULATION**: Price up on high volume = buying pressure
- **STRONG ACCUMULATION**: Very strong buying pressure
- **DISTRIBUTION**: Price down on high volume = selling pressure
- **STRONG DISTRIBUTION**: Very strong selling pressure
- **NEUTRAL**: No clear direction
- **INACTIVE**: Very low volume

### Growth Metrics

#### Revenue Growth
**What it is**: Percentage increase in company revenue over a period

**In simple terms**:
- Revenue growth of 15% means the company's sales increased by 15%
- Shows if the business is growing

**Good range**: 10-20% for established companies
- Above 20%: High growth
- Below 5%: Slow growth or stagnant
- Negative: Shrinking business (bad)

#### Revenue CAGR (Compound Annual Growth Rate)
**What it is**: Average annual growth rate over multiple years

**In simple terms**:
- Revenue CAGR of 12% means revenue grew at an average of 12% per year over 3 years
- Smoother measure than single-year growth (averages out volatility)

**Good range**: 10-15% for quality companies
- Above 15%: Excellent growth
- Below 5%: Slow growth
- Negative: Declining business

#### Earnings Growth
**What it is**: Percentage increase in company earnings (profit)

**In simple terms**:
- Earnings growth of 20% means the company's profit increased by 20%
- Shows if profitability is improving

**Good range**: 10-25% for quality companies
- Above 25%: Excellent
- Below 5%: Slow growth
- Negative: Declining profitability

### Dark Horse Score Components

#### Value Score (43 points max)
Measures how cheap the stock is:
- **PE vs Sector**: Is PE lower than sector average?
- **PB Ratio**: Is PB reasonable?
- **Price vs 200 DMA**: Is price below long-term average?
- **52-Week Position**: Is price closer to lows than highs?

#### Fundamentals Score (27 points max)
Measures company quality:
- **ROE**: Is return on equity high?
- **ROCE**: Is return on capital high?
- **Debt/Equity**: Is debt manageable?
- **FCF Yield**: Does company generate free cash flow?

#### Momentum Score (15 points max)
Measures price momentum:
- **Price vs 50 DMA**: Is price above short-term average?
- **Revenue CAGR**: Is revenue growing?
- **Volume Signal**: Is there buying pressure?

#### Risk Penalty (up to -22 points)
Penalizes risky factors:
- **Trading near 52-week high**: Overvalued risk
- **High D/E**: Too much debt
- **High PE**: Expensive
- **Low ROCE**: Poor capital efficiency
- **Revenue decline**: Business shrinking

#### Catalyst Score (up to 10 points)
Bonus for identifying catalysts:
- **Catalyst Type**: Earnings recovery, policy tailwind, etc.
- **Timeline**: Near-term catalysts worth more
- **Total**: Type score × Timeline multiplier

#### Quality Bonus (additional, outside 100-point score)
Based on advanced metrics:
- **Piotroski F-Score**: Financial strength (0-9 points)
- **Promoter Holding Trend**: Are insiders buying?
- **Interest Coverage**: Can company pay debt interest?

Only shown if at least 50% of components are available.

### Portfolio Metrics

#### Profit/Loss
**What it is**: Difference between current value and invested amount

**In simple terms**:
- Positive = you're making money
- Negative = you're losing money

#### Profit/Loss Percentage
**What it is**: Profit/Loss as a percentage of invested amount

**In simple terms**:
- P/L of +20% means you've made 20% on your investment
- P/L of -10% means you've lost 10% on your investment

---

## Tips & Best Practices

### Using the Research Tab
1. **Start with stocks you know**: Research companies in sectors you understand
2. **Check the verdict**: Pay attention to Bullish/Neutral/Bearish stance
3. **Look at fundamentals**: Focus on ROE, ROCE, and debt levels
4. **Use entry timing**: Don't buy at 52-week highs - wait for pullbacks
5. **Read the news**: Understand what's driving the stock

### Using the Dark Horse Scanner
1. **Run regularly**: Market conditions change - scan weekly
2. **Use filters**: Narrow down to sectors you understand
3. **Focus on quality**: Look for scores above 70
4. **Check catalysts**: Tag catalysts for stocks you're serious about
5. **Verify fundamentals**: Don't rely on score alone - read the deep dive

### Managing Your Portfolio
1. **Diversify**: Don't put all money in one stock or sector
2. **Use conviction tiers**: Separate high-conviction from speculative picks
3. **Track your thesis**: Write down why you bought each stock
4. **Review regularly**: Check holdings monthly
5. **Know when to sell**: Use exit zones from the scanner

### Common Mistakes to Avoid
1. **Buying at 52-week highs**: Wait for pullbacks
2. **Ignoring debt**: High debt can destroy value in downturns
3. **Chasing momentum**: Don't buy just because price is going up
4. **Over-trading**: Too many transactions eat into profits
5. **No exit plan**: Always know when you'll sell before you buy

### When to Buy
- Price is below 200 DMA
- P/E is reasonable (10-25)
- ROE and ROCE are healthy (above 15%)
- Debt is manageable (D/E below 1)
- Revenue and earnings are growing
- Volume shows accumulation

### When to Sell
- Price reaches fair value or exit zone
- Fundamentals deteriorate (ROE/ROCE declining)
- Debt becomes too high
- Catalyst plays out or fails
- Better opportunity elsewhere

---

## FAQ

### Q: Why are scanner results different each time I run it?
**A**: The scanner uses live market data from Yahoo Finance. Prices, volumes, and other metrics change throughout the day, so results will vary based on when you run the scan.

### Q: What's the difference between local and cloud versions?
**A**: Functionally they're the same, but:
- **Local**: Runs on your computer, uses your internet, no rate limits
- **Cloud**: Runs on Streamlit servers, may have API rate limits, always accessible

### Q: How often should I run the scanner?
**A**: Weekly is ideal. Market conditions change, and new opportunities emerge. Running it too frequently (daily) can lead to over-trading.

### Q: What score should I aim for?
**A**: 
- **70+**: Good quality stocks
- **80+**: Excellent stocks (rare)
- **60-70**: Decent but has some weaknesses
- **Below 60**: Generally avoid

### Q: Why is Quality showing "N/A"?
**A**: Quality bonus requires Piotroski F-score, promoter trend, and interest coverage data. If at least 50% of these are unavailable, the app shows "N/A" instead of a partial score.

### Q: Why is Revenue CAGR blank?
**A**: Some stocks don't have 3 years of revenue data available on Yahoo Finance. The app falls back to latest YoY growth if available.

### Q: Should I buy stocks with "WATCH" signal?
**A**: "WATCH" means the stock has good fundamentals but the timing isn't right. Add it to your conviction tier and wait for a pullback before buying.

### Q: What's the difference between BUY NOW and BUY ON PULLBACK?
**A**: 
- **BUY NOW**: Price is at an attractive entry point - you can buy now
- **BUY ON PULLBACK**: Good stock but price is slightly high - wait for a dip

### Q: How do I tag a catalyst?
**A**: 
1. Run the scanner
2. Click on a stock to see deep dive
3. Find the "Catalyst" section
4. Select catalyst type, timeline, and add notes
5. Click "Save Catalyst"

### Q: What catalyst types should I look for?
**A**: Common catalysts:
- **Earnings Recovery**: Company turning profitable after losses
- **Sector Re-rating**: Entire sector becoming popular
- **Policy Tailwind**: Government policy benefiting the sector
- **Debt Reduction**: Company paying down debt
- **Management Change**: New CEO or leadership
- **New Product/Service**: Launch that could boost revenue

### Q: How accurate is the fair value estimate?
**A**: It's an estimate based on:
- Analyst targets (if available)
- PE re-rating based on sector averages
- DCF (Discounted Cash Flow) analysis

It's not guaranteed - use it as a guide, not a guarantee.

### Q: Why do some stocks show "Data quality limited"?
**A**: Some stocks on Yahoo Finance have incomplete data (no analyst target, no EPS, etc.). The app still analyzes them but warns that estimates are approximate.

### Q: Can I rely solely on this app for investment decisions?
**A**: No. This is a research tool, not financial advice. Always:
- Do your own research
- Understand the business
- Consider your risk tolerance
- Consult a financial advisor if needed

### Q: How do I interpret the volume signal?
**A**: 
- **ACCUMULATION**: Smart money buying - good sign
- **DISTRIBUTION**: Smart money selling - caution
- **NEUTRAL**: No clear direction
- **INACTIVE**: No interest in the stock

### Q: What's the difference between conviction tiers and Dark Horse score?
**A**: 
- **Dark Horse Score**: Objective rating by the app based on metrics
- **Conviction Tiers**: Your personal organization based on your research and confidence

### Q: Should I sell when price hits exit zone 1?
**A**: Exit zone 1 is a 20% gain - you can:
- Sell partial position (book some profit)
- Hold for higher targets (zone 2 or 3)
- Depends on your conviction and thesis

### Q: How do I know if a high PE is justified?
**A**: High PE can be justified if:
- Company is growing fast (high revenue/earnings growth)
- ROE and ROCE are excellent
- Has strong competitive advantage (moat)
- Sector is in a bull phase

If these aren't true, high PE might be overvaluation.

### Q: What's more important - value or growth?
**A**: Both matter:
- **Value**: Don't overpay (reasonable PE/PB)
- **Growth**: Company should be growing (revenue/earnings)

The best stocks have reasonable valuations AND good growth.

---

## Glossary

- **NSE**: National Stock Exchange of India
- **Ticker**: Stock symbol (e.g., TCS.NS)
- **Market Cap**: Total value of all shares
- **Dividend Yield**: Annual dividend as percentage of stock price
- **Volatility**: How much the price fluctuates
- **Liquidity**: How easily you can buy/sell shares
- **Multibagger**: Stock that gives multiple times return (e.g., 10x)
- **Pullback**: Temporary price decline in an uptrend
- **Rally**: Sustained price increase
- **Correction**: 10-20% price decline
- **Bear Market**: Market decline of 20% or more
- **Bull Market**: Market rise of 20% or more

---

## Support

If you encounter issues:
1. Check your internet connection (app needs live data)
2. Try refreshing the page
3. Some stocks may have incomplete data on Yahoo Finance
4. API rate limits may temporarily affect data fetching

For feature requests or bug reports, contact the developer.

---

**Disclaimer**: This tool is for research purposes only. It does not constitute financial advice. Always do your own research and consult a qualified financial advisor before making investment decisions. Past performance does not guarantee future results.
