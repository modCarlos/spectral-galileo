# Backtesting Comparison Report

**Date**: 2025-12-26 22:22

**Tickers Analyzed**: 62

---

## 📊 Summary Statistics

### Success Rate
- **OLD**: 61/62 (98.4%)
- **NEW**: 61/62 (98.4%)

### Verdict Distribution

| Verdict | OLD | NEW | Change |
|---------|-----|-----|--------|
| COMPRA 🟢 | 23 | 17 | -6 |
| NEUTRAL ⚪ | 38 | 44 | +6 |

### Confidence Analysis

- **Average OLD Confidence**: 22.3%
- **Average NEW Confidence**: 19.8%
- **Average Delta**: -2.5%

### Warnings Detected (NEW Version)

- **Tickers with Warnings**: 57/61 (93%)
- **Multi-Timeframe Disagreements**: 50
- **Insider Selling Detected**: 27
- **Pre-Earnings Warnings**: 0

## 🔄 Top Confidence Changes


### Biggest Confidence Drops (More Conservative)


| Ticker | OLD Verdict | NEW Verdict | OLD Conf | NEW Conf | Delta | Warnings |
|--------|-------------|-------------|----------|----------|-------|----------|
| WMT | COMPRA 🟢 | COMPRA 🟢 | 43% | 35% | -8% | MTF_DISAGREE, INSIDER_SELLING |
| V | COMPRA 🟢 | COMPRA 🟢 | 40% | 32% | -8% | MTF_DISAGREE, INSIDER_SELLING |
| NVDA | COMPRA 🟢 | COMPRA 🟢 | 33% | 27% | -6% | MTF_DISAGREE, INSIDER_SELLING |
| AAPL | COMPRA 🟢 | COMPRA 🟢 | 32% | 26% | -6% | MTF_DISAGREE, INSIDER_SELLING |
| AMZN | COMPRA 🟢 | COMPRA 🟢 | 31% | 25% | -6% | MTF_DISAGREE, INSIDER_SELLING |
| MSFT | COMPRA 🟢 | COMPRA 🟢 | 30% | 24% | -6% | MTF_DISAGREE, INSIDER_SELLING |
| AMD | COMPRA 🟢 | NEUTRAL ⚪ | 27% | 22% | -5% | MTF_DISAGREE, INSIDER_SELLING |
| AVGO | COMPRA 🟢 | NEUTRAL ⚪ | 27% | 22% | -5% | MTF_DISAGREE, INSIDER_SELLING |
| RIVN | COMPRA 🟢 | NEUTRAL ⚪ | 31% | 26% | -4% | MTF_DISAGREE, INSIDER_SELLING |
| TSLA | NEUTRAL ⚪ | NEUTRAL ⚪ | 22% | 18% | -4% | MTF_DISAGREE, INSIDER_SELLING |

### Biggest Confidence Increases


| Ticker | OLD Verdict | NEW Verdict | OLD Conf | NEW Conf | Delta | Warnings |
|--------|-------------|-------------|----------|----------|-------|----------|
| OXY | NEUTRAL ⚪ | NEUTRAL ⚪ | 8% | 8% | 0% | DEATH_CROSS |
| SONY | NEUTRAL ⚪ | NEUTRAL ⚪ | 21% | 21% | -0% | NONE |
| JPM | NEUTRAL ⚪ | NEUTRAL ⚪ | 19% | 19% | -0% | MTF_DISAGREE, INSIDER_SELLING |
| GS | NEUTRAL ⚪ | NEUTRAL ⚪ | 22% | 22% | -0% | MTF_DISAGREE |
| PLD | COMPRA 🟢 | COMPRA 🟢 | 28% | 27% | -0% | MTF_DISAGREE, INSIDER_SELLING |
| JNJ | COMPRA 🟢 | COMPRA 🟢 | 40% | 40% | -0% | MTF_DISAGREE |
| KO | COMPRA 🟢 | COMPRA 🟢 | 40% | 40% | -0% | MTF_DISAGREE |
| SBUX | NEUTRAL ⚪ | NEUTRAL ⚪ | 9% | 8% | -1% | MTF_DISAGREE |
| HD | NEUTRAL ⚪ | NEUTRAL ⚪ | 8% | 7% | -1% | MTF_DISAGREE, DEATH_CROSS |
| BA | NEUTRAL ⚪ | NEUTRAL ⚪ | 9% | 8% | -1% | MTF_DISAGREE |

## ⚡ Verdict Changes (6 tickers)


| Ticker | OLD → NEW | Conf Delta | Warnings |
|--------|-----------|------------|----------|
| AMD | COMPRA 🟢 → NEUTRAL ⚪ | -5% | MTF_DISAGREE, INSIDER_SELLING |
| RIVN | COMPRA 🟢 → NEUTRAL ⚪ | -4% | MTF_DISAGREE, INSIDER_SELLING |
| CRM | COMPRA 🟢 → NEUTRAL ⚪ | -3% | MTF_DISAGREE |
| AAL | COMPRA 🟢 → NEUTRAL ⚪ | -4% | MTF_DISAGREE, INSIDER_SELLING |
| AVGO | COMPRA 🟢 → NEUTRAL ⚪ | -5% | MTF_DISAGREE, INSIDER_SELLING |
| CAT | COMPRA 🟢 → NEUTRAL ⚪ | -3% | MTF_DISAGREE |

## 🆕 New Features Impact


### Reddit Sentiment
- **Tickers with Reddit Activity**: 11/61
- **Bullish**: 1, **Bearish**: 0

### Earnings Trends
- **BEATING estimates**: 27
- **MISSING estimates**: 8

### Insider Trading
- **Insider Buying detected**: 3
- **Insider Selling detected**: 27

## 📋 Full Comparison Table


| Ticker | OLD | NEW | Δ Conf | Warnings | MTF | Reddit | Earnings | Insider |
|--------|-----|-----|--------|----------|-----|--------|----------|---------|
| MSFT | COMPRA 🟢 30% | COMPRA 🟢 24% | -6% | MTF_DISAGREE,INSIDER | HOLD | NEUT | BEAT | BEAR |
| ARM | NEUTRAL ⚪ 10% | NEUTRAL ⚪ 9% | -1% | - | SELL | NEUT | BEAT | NEUT |
| ORCL | NEUTRAL ⚪ 11% | NEUTRAL ⚪ 9% | -2% | MTF_DISAGREE,INSIDER | HOLD | NEUT | BEAT | BEAR |
| META | NEUTRAL ⚪ 11% | NEUTRAL ⚪ 9% | -2% | MTF_DISAGREE,INSIDER | HOLD | BULL | MISS | BEAR |
| BABA | COMPRA 🟢 36% | COMPRA 🟢 33% | -4% | MTF_DISAGREE | HOLD | NEUT | MISS | NEUT |
| WMT | COMPRA 🟢 43% | COMPRA 🟢 35% | -8% | MTF_DISAGREE,INSIDER | HOLD | NEUT | MEET | BEAR |
| SOFI | NEUTRAL ⚪ 25% | NEUTRAL ⚪ 21% | -4% | MTF_DISAGREE,INSIDER | HOLD | NEUT | BEAT | BEAR |
| NVDA | COMPRA 🟢 33% | COMPRA 🟢 27% | -6% | MTF_DISAGREE,INSIDER | HOLD | NEUT | BEAT | BEAR |
| NKE | NEUTRAL ⚪ 13% | NEUTRAL ⚪ 12% | -1% | DEATH_CROSS | SELL | NEUT | BEAT | NEUT |
| TSLA | NEUTRAL ⚪ 22% | NEUTRAL ⚪ 18% | -4% | MTF_DISAGREE,INSIDER | HOLD | NEUT | MISS | BEAR |
| AMD | COMPRA 🟢 27% | NEUTRAL ⚪ 22% | -5% | MTF_DISAGREE,INSIDER | HOLD | NEUT | MEET | BEAR |
| NU | NEUTRAL ⚪ 22% | NEUTRAL ⚪ 20% | -2% | MTF_DISAGREE | HOLD | NEUT | MEET | NEUT |
| AMZN | COMPRA 🟢 31% | COMPRA 🟢 25% | -6% | MTF_DISAGREE,INSIDER | HOLD | NEUT | BEAT | BEAR |
| RIVN | COMPRA 🟢 31% | NEUTRAL ⚪ 26% | -4% | MTF_DISAGREE,INSIDER | HOLD | NEUT | BEAT | BEAR |
| DIS | COMPRA 🟢 29% | COMPRA 🟢 27% | -2% | MTF_DISAGREE | HOLD | NEUT | BEAT | BULL |
| GOOGL | COMPRA 🟢 32% | COMPRA 🟢 29% | -3% | MTF_DISAGREE | HOLD | NEUT | BEAT | NEUT |
| XOM | COMPRA 🟢 38% | COMPRA 🟢 34% | -4% | MTF_DISAGREE,INSIDER | HOLD | NEUT | MEET | BEAR |
| OXY | NEUTRAL ⚪ 8% | NEUTRAL ⚪ 8% | +0% | DEATH_CROSS | SELL | NEUT | BEAT | BULL |
| LULU | NEUTRAL ⚪ 22% | NEUTRAL ⚪ 18% | -3% | INSIDER_SELLING | SELL | NEUT | BEAT | BEAR |
| CRM | COMPRA 🟢 26% | NEUTRAL ⚪ 24% | -3% | MTF_DISAGREE | HOLD | NEUT | BEAT | NEUT |
| MPW | NEUTRAL ⚪ 20% | NEUTRAL ⚪ 18% | -2% | MTF_DISAGREE,INSIDER | HOLD | NEUT | MISS | BEAR |
| BA | NEUTRAL ⚪ 9% | NEUTRAL ⚪ 8% | -1% | MTF_DISAGREE | HOLD | NEUT | MISS | NEUT |
| JD | NEUTRAL ⚪ 14% | NEUTRAL ⚪ 13% | -1% | MTF_DISAGREE,DEATH_C | HOLD | NEUT | BEAT | NEUT |
| NVO | NEUTRAL ⚪ 16% | NEUTRAL ⚪ 15% | -2% | MTF_DISAGREE | HOLD | NEUT | MEET | NEUT |
| CMG | NEUTRAL ⚪ 13% | NEUTRAL ⚪ 11% | -1% | - | SELL | NEUT | MEET | NEUT |
| INTC | NEUTRAL ⚪ 25% | NEUTRAL ⚪ 22% | -2% | MTF_DISAGREE | HOLD | NEUT | BEAT | NEUT |
| PLD | COMPRA 🟢 28% | COMPRA 🟢 27% | -0% | MTF_DISAGREE,INSIDER | HOLD | NEUT | BEAT | BEAR |
| AAL | COMPRA 🟢 27% | NEUTRAL ⚪ 23% | -4% | MTF_DISAGREE,INSIDER | HOLD | NEUT | BEAT | BEAR |
| FTNT | NEUTRAL ⚪ 10% | NEUTRAL ⚪ 8% | -2% | MTF_DISAGREE,DEATH_C | HOLD | NEUT | BEAT | BEAR |
| URA | NEUTRAL ⚪ 15% | NEUTRAL ⚪ 14% | -2% | MTF_DISAGREE | HOLD | NEUT | UNKN | NEUT |
| XYZ | NEUTRAL ⚪ 12% | NEUTRAL ⚪ 9% | -2% | INSIDER_SELLING | SELL | NEUT | MISS | BEAR |
| HD | NEUTRAL ⚪ 8% | NEUTRAL ⚪ 7% | -1% | MTF_DISAGREE,DEATH_C | HOLD | NEUT | MEET | NEUT |
| PDD | NEUTRAL ⚪ 18% | NEUTRAL ⚪ 16% | -2% | MTF_DISAGREE | HOLD | NEUT | BEAT | NEUT |
| SBUX | NEUTRAL ⚪ 9% | NEUTRAL ⚪ 8% | -1% | MTF_DISAGREE | HOLD | NEUT | MISS | BULL |
| BIDU | COMPRA 🟢 34% | COMPRA 🟢 30% | -3% | MTF_DISAGREE | HOLD | NEUT | BEAT | NEUT |
| LEN | NEUTRAL ⚪ 18% | NEUTRAL ⚪ 17% | -2% | - | SELL | NEUT | MEET | NEUT |
| SONY | NEUTRAL ⚪ 21% | NEUTRAL ⚪ 21% | -0% | - | SELL | NEUT | BEAT | NEUT |
| O | NEUTRAL ⚪ 24% | NEUTRAL ⚪ 22% | -2% | MTF_DISAGREE,INSIDER | HOLD | NEUT | MISS | BEAR |
| MMM | NEUTRAL ⚪ 22% | NEUTRAL ⚪ 20% | -2% | MTF_DISAGREE | HOLD | NEUT | BEAT | NEUT |
| GE | NEUTRAL ⚪ 19% | NEUTRAL ⚪ 18% | -1% | MTF_DISAGREE,INSIDER | HOLD | NEUT | BEAT | BEAR |
| AAPL | COMPRA 🟢 32% | COMPRA 🟢 26% | -6% | MTF_DISAGREE,INSIDER | HOLD | NEUT | MEET | BEAR |
| JPM | NEUTRAL ⚪ 19% | NEUTRAL ⚪ 19% | -0% | MTF_DISAGREE,INSIDER | HOLD | NEUT | BEAT | BEAR |
| V | COMPRA 🟢 40% | COMPRA 🟢 32% | -8% | MTF_DISAGREE,INSIDER | HOLD | NEUT | MEET | BEAR |
| MA | COMPRA 🟢 29% | COMPRA 🟢 26% | -3% | MTF_DISAGREE | HOLD | NEUT | MEET | NEUT |
| GS | NEUTRAL ⚪ 22% | NEUTRAL ⚪ 22% | -0% | MTF_DISAGREE | HOLD | NEUT | BEAT | NEUT |
| UNH | NEUTRAL ⚪ 19% | NEUTRAL ⚪ 17% | -2% | DEATH_CROSS | SELL | NEUT | MEET | NEUT |
| LLY | NEUTRAL ⚪ 20% | NEUTRAL ⚪ 17% | -3% | MTF_DISAGREE,INSIDER | HOLD | NEUT | BEAT | BEAR |
| JNJ | COMPRA 🟢 40% | COMPRA 🟢 40% | -0% | MTF_DISAGREE | HOLD | NEUT | MEET | NEUT |
| ABBV | COMPRA 🟢 25% | COMPRA 🟢 23% | -3% | MTF_DISAGREE | HOLD | NEUT | MEET | NEUT |
| PG | NEUTRAL ⚪ 19% | NEUTRAL ⚪ 17% | -2% | DEATH_CROSS | SELL | NEUT | MEET | NEUT |
| KO | COMPRA 🟢 40% | COMPRA 🟢 40% | -0% | MTF_DISAGREE | HOLD | NEUT | MEET | NEUT |
| COST | NEUTRAL ⚪ 16% | NEUTRAL ⚪ 13% | -3% | DEATH_CROSS,INSIDER_ | SELL | NEUT | MEET | BEAR |
| MCD | COMPRA 🟢 29% | COMPRA 🟢 26% | -3% | MTF_DISAGREE | HOLD | NEUT | MEET | NEUT |
| AVGO | COMPRA 🟢 27% | NEUTRAL ⚪ 22% | -5% | MTF_DISAGREE,INSIDER | HOLD | NEUT | MEET | BEAR |
| NFLX | NEUTRAL ⚪ 15% | NEUTRAL ⚪ 14% | -2% | MTF_DISAGREE,DEATH_C | HOLD | NEUT | MEET | NEUT |
| ADBE | NEUTRAL ⚪ 18% | NEUTRAL ⚪ 16% | -2% | MTF_DISAGREE,INSIDER | HOLD | NEUT | MEET | BEAR |
| NOW | NEUTRAL ⚪ 16% | NEUTRAL ⚪ 14% | -2% | MTF_DISAGREE,DEATH_C | HOLD | NEUT | BEAT | BEAR |
| CAT | COMPRA 🟢 27% | NEUTRAL ⚪ 24% | -3% | MTF_DISAGREE | HOLD | NEUT | MEET | NEUT |
| VOO | NEUTRAL ⚪ 15% | NEUTRAL ⚪ 13% | -2% | MTF_DISAGREE | HOLD | NEUT | UNKN | NEUT |
| SPY | NEUTRAL ⚪ 15% | NEUTRAL ⚪ 13% | -2% | MTF_DISAGREE | HOLD | NEUT | UNKN | NEUT |
| QQQ | NEUTRAL ⚪ 15% | NEUTRAL ⚪ 13% | -2% | MTF_DISAGREE | HOLD | NEUT | UNKN | NEUT |