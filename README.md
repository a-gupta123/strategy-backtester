# Moving Average Crossover Strategy Backtester

This project implements a simple backtesting framework for a moving average crossover trading strategy on SPY.
The strategy is evaluated against a buy-and-hold benchmark using standard performance metrics, including CAGR, volatility, Sharpe ratio, and maximum drawdown.

---

## Overview

Systematic trading strategies are often evaluated using historical backtests to understand their risk–return profile and failure modes.
Moving average crossover strategies are a common baseline in quantitative finance, as they encode simple trend-following behavior while remaining easy to interpret.

This project focuses less on strategy discovery and more on building a clean, correct backtesting pipeline, including:
- Proper signal timing and execution lag
- Turnover-based transaction costs
- Risk-adjusted performance metrics
- Drawdown and rolling Sharpe analysis

---

## Strategy Description

Let:
- P_t be the adjusted closing price of SPY on day t
- MA_fast(t) be the fast moving average
- MA_slow(t) be the slow moving average

The trading signal is defined as:

Signal_t = 1 if MA_fast(t) > MA_slow(t), else 0

To avoid look-ahead bias, positions are applied with a one-day lag:

Position_{t+1} = Signal_t

The strategy is either fully invested (long SPY) or fully out of the market.

---

## Backtest Mechanics

### Returns

Daily strategy returns are computed as:

Strategy return = Position_t × Asset return − Transaction cost

where asset returns are the daily percentage returns of SPY.

### Transaction Costs

Transaction costs are modeled as proportional to daily turnover:

Cost_t = Turnover_t × Cost rate

Turnover is defined as the absolute change in position:

Turnover_t = |Position_t − Position_{t−1}|

Costs are specified in basis points per trade.

---

## Performance Metrics

The backtester reports:
- CAGR (annualized geometric return)
- Annualized volatility
- Sharpe ratio
- Maximum drawdown
- Average daily turnover
- Final equity value

Metrics are computed for both:
- The moving average strategy
- A buy-and-hold SPY benchmark

---

## Diagnostics and Visualizations

The following plots are produced:

1. Equity curve  
   Strategy vs buy-and-hold performance over time

2. Drawdown curve  
   Peak-to-trough losses of the strategy

3. Rolling Sharpe ratio  
   Rolling risk-adjusted performance over a fixed window

These diagnostics help identify regime dependence, drawdown severity, and return stability.

---

## Data

- Historical SPY price data is downloaded using `yfinance`
- Adjusted close prices are used to account for dividends and splits
- The backtest begins only after sufficient data exists to compute moving averages

---

## How to Run

Install dependencies:
```bash
pip install numpy pandas matplotlib yfinance
