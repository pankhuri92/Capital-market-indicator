import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

# Fetch Nifty 50 data
ticker = "^NSEI"
data = yf.download(ticker, start="2010-01-01", end="2023-01-01")
data['Close'] = data['Adj Close']

# calculate EMA
def calculate_ema(data, period):
    if period < 1:
        period = 1  # period: at least 1
    return data['Close'].ewm(span=period, adjust=False).mean()

# calculate profit based on EMA crossovers
def calculate_profit(data, ema_short, ema_long):
    signals = pd.DataFrame(index=data.index)
    signals['Signal'] = 0.0
    signals['EMA_Short'] = ema_short
    signals['EMA_Long'] = ema_long

    # Generate buy/sell signals using .loc to avoid chained assignment issues
    signals.loc[signals['EMA_Short'] > signals['EMA_Long'], 'Signal'] = 1.0  # Buy signal
    signals.loc[signals['EMA_Short'] < signals['EMA_Long'], 'Signal'] = -1.0  # Sell signal

    # Calculate returns
    signals['Position'] = signals['Signal'].diff()
    signals['Daily_Return'] = data['Close'].pct_change()
    signals['Strategy_Return'] = signals['Daily_Return'] * signals['Signal'].shift(1)

    return signals['Strategy_Return'].sum()  # Total profit as the sum of strategy returns

# Main loop for finding best EMA ratio
def find_best_ema(data, window_size=10):
    best_ratios = []
    initial_ratios = [(9, 21), (10, 30), (12, 26)]  

    for i in range(0, len(data) - window_size, window_size):
        data_window = data.iloc[i:i+window_size]
        ratio_combinations = initial_ratios + [(np.random.randint(5, 15), np.random.randint(20, 40)) for _ in range(3)]  # More diverse ratios
        
        print(f"Window {i} to {i+window_size} - Testing Ratios:")
        performance_scores = []
        for short, long in ratio_combinations:
            if short >= long:
                continue  
            
            ema_short = calculate_ema(data_window, short)
            ema_long = calculate_ema(data_window, long)
            
            profit = calculate_profit(data_window, ema_short, ema_long)
            print(f"Ratio: ({short}, {long}), Profit: {profit}")
            
            performance_scores.append((short, long, profit))
        
        if performance_scores:
            best_ratio = max(performance_scores, key=lambda x: x[2])
            best_ratios.append(best_ratio[:2])
            
            print(f"Best Ratio for Window: {best_ratio[:2]}")

            # next ratio set: best ratio + 2 new random ratios
            initial_ratios = [
                best_ratio[:2],  # Best ratio stays for next period
                (max(1, best_ratio[0] + np.random.randint(-1, 2)), max(1, best_ratio[1] + np.random.randint(-1, 2))),  # periods must be >= 1
                (np.random.randint(5, 15), np.random.randint(20, 40))  # New random ratio
            ]

    return best_ratios

# Run the dynamic best-fit EMA finder
best_ratios_over_time = find_best_ema(data)

# Convert best ratios to decimal format
best_ratios_decimals = [short / long for short, long in best_ratios_over_time]

import plotly.graph_objects as go

def plot_ratios(ratios, original_ratios):
    x = np.arange(len(ratios))
    y = np.array(ratios)
    
    # Create a smoother line using spline interpolation
    x_smooth = np.linspace(x.min(), x.max(), 300)
    y_smooth = make_interp_spline(x, y)(x_smooth)
    
    # Create the plot
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x_smooth, 
        y=y_smooth, 
        mode='lines+markers',
        line=dict(color='blue'),
        marker=dict(size=4),
        text=[f'Ratio: {orig[0]}/{orig[1]}' for orig in original_ratios],
        hoverinfo='text'
    ))

    fig.update_layout(
        title='Best-Fit EMA Ratios Over Time',
        xaxis_title='Time Periods',
        yaxis_title='EMA Ratio (Short/Long)',
        hovermode='closest'
    )

    fig.show()

# Plot the graph with original ratios
plot_ratios(best_ratios_decimals, best_ratios_over_time)

# # Smooth graph plotting
# def plot_smoothed_ratios(ratios):
#     x = np.arange(len(ratios))
#     y = np.array(ratios)
    
#     # Create a smoother line using spline interpolation
#     x_smooth = np.linspace(x.min(), x.max(), 300)
#     y_smooth = make_interp_spline(x, y)(x_smooth)

#     plt.figure(figsize=(12, 6))
#     plt.plot(x_smooth, y_smooth, color='blue', label='Best-Fit Ratio', marker='o', markersize=3)
#     plt.title('Best-Fit EMA Ratios Over Time')
#     plt.xlabel('Time Periods')
#     plt.ylabel('EMA Ratio')
#     plt.legend()
#     plt.grid(True)
#     plt.show()

# # Plot the smoothed best-fit ratios
# plot_smoothed_ratios(best_ratios_decimals)

# import plotly.graph_objects as go

# def plot_ratios(ratios):
#     x = np.arange(len(ratios))
#     y = np.array(ratios)
    
#     # Create a smoother line using spline interpolation
#     x_smooth = np.linspace(x.min(), x.max(), 300)
#     y_smooth = make_interp_spline(x, y)(x_smooth)
    
#     # Create the plot
#     fig = go.Figure()

#     fig.add_trace(go.Scatter(
#         x=x_smooth, 
#         y=y_smooth, 
#         mode='lines+markers',
#         line=dict(color='blue'),
#         marker=dict(size=4),
#         text=[f'Ratio: {ratio:.2f}' for ratio in ratios],
#         hoverinfo='text'
#     ))

#     fig.update_layout(
#         title='Best-Fit EMA Ratios Over Time',
#         xaxis_title='Time Periods',
#         yaxis_title='EMA Ratio',
#         hovermode='closest'
#     )

#     fig.show()

# # Plot the graph
# plot_ratios(best_ratios_decimals)

