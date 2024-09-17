import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

ticker = "LT.NS"        # symbol: ^NSEI, HINDUSTAN.NS
data = yf.download(ticker, start="2004-01-01", end="2024-01-01")

print(data.head())

data.fillna(method='ffill', inplace=True)

data['Month'] = data.index.month

monthly_avg_close = data.groupby('Month')['Close'].mean()

min_value = monthly_avg_close.min()
monthly_avg_close_percentage = ((monthly_avg_close - min_value) / monthly_avg_close) * 100

print(monthly_avg_close_percentage)

plt.figure(figsize=(10, 6))
plt.plot(monthly_avg_close_percentage.index, monthly_avg_close_percentage.values, marker='o')

plt.xticks(monthly_avg_close_percentage.index, ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])

plt.xlabel('Month')
plt.ylabel('Average Closing Price as % of Minimum')
plt.title('Seasonality Pattern in Stock Prices (Percentage)')

plt.grid(True)

plt.show()
