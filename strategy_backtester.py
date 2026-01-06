import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

# Parameters:
ticker = "SPY"
start = "2005-01-01"
end = None  # The end can be adjusted or left as None to get data up until present day
fast_window = 50
slow_window = 200
cost_bps = 10.0
risk_free_rate = 0.0
rolling_sharpe_window = 126
trading_days = 252

def download_price_data(ticker, start, end):
    df = yf.download(ticker, start=start, end=end, auto_adjust=False, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def compute_signals(prices, fast, slow):
    fast_ma = prices.rolling(fast, min_periods=fast).mean()
    slow_ma = prices.rolling(slow, min_periods=slow).mean()
    signal = (fast_ma > slow_ma).astype(int)
    return signal

def compute_positions_from_signal(signal):
    position = signal.shift(1).fillna(0.0)
    return position

def compute_daily_returns(prices):
    daily_ret = prices.pct_change().fillna(0.0)
    return daily_ret

def compute_turnover(position):
    turnover = position.diff().abs().fillna(0.0)
    return turnover

def run_backtest(df):
    price = df["Adj Close"].copy()

    raw_signal = compute_signals(price, fast_window, slow_window)
    position = compute_positions_from_signal(raw_signal)

    asset_ret = compute_daily_returns(price)

    turnover = compute_turnover(position)

    cost_rate = cost_bps / 10000
    cost = turnover * cost_rate

    strat_ret = position * asset_ret - cost

    equity = (1+strat_ret).cumprod()

    benchmark_equity = (1+asset_ret).cumprod()

    results = pd.DataFrame(index=price.index)
    results["price"] = price
    results["asset_return"] = asset_ret
    results["raw_signal"] = raw_signal
    results["position"] = position
    results["turnover"] = turnover
    results["cost"] = cost
    results["strategy_return"] = strat_ret
    results["equity"] = equity
    results["buyhold_equity"] = benchmark_equity

    results = results.iloc[slow_window:].copy()
    assert results["position"].isin([0.0, 1.0]).all()
    metrics = compute_metrics(results)

    return results, metrics

def compute_drawdown(equity):
    peak = equity.cummax()
    dd = equity / peak - 1.0
    return dd

def annualize_return(equity):
    total_growth = equity.iloc[-1] / equity.iloc[0]
    years = (len(equity) - 1) / trading_days
    return total_growth ** (1 / years) - 1

def annualize_volatility(daily_returns):
    return (daily_returns.std(ddof=1) * np.sqrt(trading_days))

def sharpe_ratio(daily_returns, risk_free_rate):
    rf_daily = risk_free_rate / trading_days
    excess = daily_returns - rf_daily
    sd = excess.std(ddof=1)
    if sd == 0 or np.isnan(sd):
        return float("nan")
    return float((excess.mean() / sd) * np.sqrt(trading_days))

def compute_metrics(results):
    strat_ret = results["strategy_return"]
    bh_ret = results["asset_return"]

    strat_equity = results["equity"]
    bh_equity = results["buyhold_equity"]

    strat_dd = compute_drawdown(strat_equity)
    bh_dd = compute_drawdown(bh_equity)

    avg_daily_turnover = float(results["turnover"].mean())

    metrics = {
        "Strategy CAGR": annualize_return(strat_equity),
        "Strategy Vol (ann.)": annualize_volatility(strat_ret),
        "Strategy Sharpe": sharpe_ratio(strat_ret, risk_free_rate),
        "Strategy Max Drawdown": float(strat_dd.min()),
        "Strategy Final Equity": float(strat_equity.iloc[-1]),
        "Strategy Avg Daily Turnover": avg_daily_turnover,

        "Buy&Hold CAGR": annualize_return(bh_equity),
        "Buy&Hold Vol (ann.)": annualize_volatility(bh_ret),
        "Buy&Hold Sharpe": sharpe_ratio(bh_ret, risk_free_rate),
        "Buy&Hold Max Drawdown": float(bh_dd.min()),
        "Buy&Hold Final Equity": float(bh_equity.iloc[-1]),
    }
    return metrics

def rolling_sharpe(daily_returns, window=126):
    rolling_mean = daily_returns.rolling(window).mean()
    rolling_std = daily_returns.rolling(window).std(ddof=1)
    
    ratio = rolling_mean / rolling_std * np.sqrt(trading_days)
    
    return ratio

def plot_results(results):
    equity = results["equity"]
    buyhold_equity = results["buyhold_equity"]
    dd = compute_drawdown(equity)
    rs = rolling_sharpe(results["strategy_return"], window = rolling_sharpe_window)

    plt.figure()
    plt.plot(equity.index, equity.values, label="MA Crossover Strategy")
    plt.plot(buyhold_equity.index, buyhold_equity.values, label = "Buy and Hold SPY")
    plt.title(f"{ticker} MA Crossover Backtest (fast={fast_window}, slow={slow_window}, cost={cost_bps} bps)")
    plt.xlabel("Date")
    plt.ylabel("Growth of $1")
    plt.legend()
    plt.tight_layout()
    plt.savefig("equity_curve.png", dpi=200, bbox_inches="tight")
    plt.show()

    plt.figure()
    plt.plot(dd.index, dd.values)
    plt.title("Strategy Drawdown")
    plt.xlabel("Date")
    plt.ylabel("Drawdown")
    plt.tight_layout()
    plt.savefig("drawdown_curve.png", dpi=200, bbox_inches="tight")
    plt.show()

    plt.figure()
    plt.plot(rs.index, rs.values)
    plt.title(f"Rolling Sharpe ({rolling_sharpe_window} trading days)")
    plt.xlabel("Date")
    plt.ylabel("Rolling Sharpe")
    plt.tight_layout()
    plt.savefig("rolling_sharpe.png", dpi=200, bbox_inches="tight")
    plt.show()

def print_metrics(m):
    print("\nMA crossover vs buy & hold\n")

    print("Strategy:")
    print(f"  CAGR:        {100*m['Strategy CAGR']:.2f}%")
    print(f"  Volatility:  {100*m['Strategy Vol (ann.)']:.2f}%")
    print(f"  Sharpe:      {m['Strategy Sharpe']:.3f}")
    print(f"  Max DD:      {100*m['Strategy Max Drawdown']:.2f}%")
    print(f"  Final value: {m['Strategy Final Equity']:.3f}")
    print(f"  Turnover:    {100*m['Strategy Avg Daily Turnover']:.2f}%")

    print("\nBuy & hold:")
    print(f"  CAGR:        {100*m['Buy&Hold CAGR']:.2f}%")
    print(f"  Volatility:  {100*m['Buy&Hold Vol (ann.)']:.2f}%")
    print(f"  Sharpe:      {m['Buy&Hold Sharpe']:.3f}")
    print(f"  Max DD:      {100*m['Buy&Hold Max Drawdown']:.2f}%")
    print(f"  Final value: {m['Buy&Hold Final Equity']:.3f}")

def main():
    df = download_price_data(ticker, start, end)
    results, metrics = run_backtest(df)
    print_metrics(metrics)
    plot_results(results)

if __name__ == "__main__":
    main()