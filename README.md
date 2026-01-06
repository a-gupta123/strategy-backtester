# Moving Average Crossover Strategy Backtester

This project implements a backtest of a moving average crossover trading strategy on SPY.
Results are compared to a simple buy-and-hold SPY baseline using standard performance metrics such as CAGR, volatility, Sharpe ratio, and maximum drawdown.

---

## Overview

Moving average crossover strategies are a simple and commonly used baseline in quantitative trading.
Because they are easy to interpret, they are useful for testing whether a backtest is behaving as expected across different market regimes.

This project is less about finding a profitable strategy and more about implementing the mechanics of a backtest correctly, including:
- Applying signals with a one-day execution lag
- Accounting for transaction costs through daily turnover
- Computing basic risk and return statistics
- Visualizing drawdowns and rolling Sharpe ratios

---

## Strategy Description

Let:
- $P_t$ be the adjusted closing price of SPY on day t
- $MA_{fast}(t)$ be the fast moving average
- $MA_{slow}(t)$ be the slow moving average

The trading signal is defined as:

$Signal_t$ = 1 if $MA_{fast}(t) > MA_{slow}(t)$, else 0

To avoid look-ahead bias, positions are applied with a one-day lag:

$Position_{t+1} = Signal_{t}$

This strategy is either fully invested (long SPY) or fully out of the market.

---

## Backtest Mechanics

### Returns

Daily strategy returns are computed as:

Strategy return = $Position_t$ × Asset return − Transaction cost

where asset returns are the daily percentage returns of SPY.

### Transaction Costs

Transaction costs depend on daily turnover and are applied whenever the position changes.

$Cost_t$ = $Turnover_t$ × Cost rate

Turnover is the absolute change in position from one day to the next.

$Turnover_t = |Position_t − Position_{t−1}|$

Costs are specified in basis points per trade.

---

## Performance Metrics

The backtester reports:
- Compound Annual Growth Rate (CAGR)
- Annualized volatility
- Sharpe ratio
- Maximum drawdown
- Average daily turnover
- Final equity value

Metrics are computed for both:
- The moving average strategy
- A buy-and-hold SPY benchmark

---

## Visualizations

The following plots are produced:

1. Equity curve  
   Strategy vs buy-and-hold performance over time

2. Drawdown curve  
   Peak-to-trough losses of the strategy

3. Rolling Sharpe ratio  
   Rolling risk-adjusted performance over a fixed window

These plots make it easier to see when the strategy performs well, when it struggles, and how volatile its performance is over time.

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
