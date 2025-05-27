import yfinance as yf
import pandas as pd
import time
import os
from datetime import  datetime, timedelta, date


def get_sp500_tickers_from_wiki() -> list[str]:
    '''
    Getting S&P 500 tickers from Wikipedia
    '''
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    table = pd.read_html(url)
    tickers = table[0]['Symbol'].tolist()
    # Convert dots in ticker names to hyphens for yfinance
    tickers = [ticker.replace('.', '-') for ticker in tickers]
    return tickers


def download_data(
        ticker: str,
        period: str | None = None,
        interval: str | None = None ,
        start: date | None = None,
        end: date | None = None
) -> pd.DataFrame | None:
    '''
    Downloading historical data
    :param ticker: string
    :param period: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    :param interval: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
    :param start: string (YYYY-MM-DD)
    :param end: string (YYYY-MM-DD)
    :return: pd.DataFrame
    '''
    try:
        start = start.strftime("%Y-%m-%d") if start else None
        end = end.strftime("%Y-%m-%d") if end else None
        df = yf.download(ticker, period=period, interval=interval, start=start, end=end, group_by="ticker", auto_adjust=False)
        if df.empty:
            return None

        # Reset MultiIndex
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(1)

        df['Ticker'] = ticker
        df.reset_index(inplace=True)
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize('UTC')
            df.rename(columns={'Date': 'Datetime'}, inplace=True)
        return df[['Datetime', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume']]
    except Exception as e:
        print(f"Error during loading {ticker}: {e}")
    return None

def main():
    now = datetime.now()
    periods = (
        ("2y", "1d", None, None),
        #(None, "1h", now - timedelta(days=20), now),
        #(None, "5m", now - timedelta(days=5), now - timedelta(days=3)),
    )

    root_dir = "sp500_data"
    tickers = get_sp500_tickers_from_wiki()
    for period_record in periods:
        period, interval, start, end = period_record
        output_dir = os.path.join(root_dir, period or interval)
        os.makedirs(output_dir, exist_ok=True)

        for i, ticker in enumerate(tickers, 1):
            print(f"[{period or interval}][{i}/{len(tickers)}] Loading {ticker}...")
            data = download_data(ticker, period=period, interval=interval, start=start, end=end)
            if data is not None:
                data.to_csv(f"{output_dir}/{ticker}.csv", index=False)
            time.sleep(1)  # not to overload yfinance


    print("✅ The process is over")

if __name__ == "__main__":
    main()
