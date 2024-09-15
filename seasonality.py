import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

ticker = "LT.NS"        #symbol: ^NSEI, HINDUSTAN.NS
data = yf.download(ticker, start="2004-01-01", end="2024-01-01")

print(data.head())

data.fillna(method='ffill', inplace=True)

data['Month'] = data.index.month

monthly_avg_close = data.groupby('Month')['Close'].mean()

print(monthly_avg_close)

plt.figure(figsize=(10, 6))
plt.plot(monthly_avg_close.index, monthly_avg_close.values, marker='o')
plt.xticks(monthly_avg_close.index, ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])

plt.xlabel('Month')
plt.ylabel('Average Closing Price')
plt.title('Seasonality Pattern in Stock Prices (2013-2023)')

plt.grid(True)
plt.show()
