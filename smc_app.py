import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import plotly.io as pio


from smartmoneyconcepts.smc import smc  # Assuming this is your custom library

def process_stock_data(stock_symbol):
# Fetch Reliance stock data
    reliance_data = yf.download(stock_symbol, start='2023-01-01', end=datetime.today().strftime('%Y-%m-%d'))

    # Apply the FVG and Swing High/Low indicators
    fvg_data = smc.fvg(reliance_data)
    swing_data = smc.swing_highs_lows(reliance_data)

    # Combine the data with original OHLC data for plotting
    reliance_data['FVG'] = fvg_data['FVG']
    reliance_data['FVG_Top'] = fvg_data['Top']
    reliance_data['FVG_Bottom'] = fvg_data['Bottom']
    reliance_data['Swing_HighLow'] = swing_data['HighLow']
    reliance_data['Swing_Level'] = swing_data['Level']

    # Create the candlestick chart with Plotly
    fig = go.Figure(data=[go.Candlestick(x=reliance_data.index,
                                        open=reliance_data['Open'],
                                        high=reliance_data['High'],
                                        low=reliance_data['Low'],
                                        close=reliance_data['Close'],
                                        name='Candlestick')])

    # Add Fair Value Gaps (FVG)
    def add_FVG(fig, df, fvg_data):
        for i in range(len(fvg_data["FVG"])):
            if not np.isnan(fvg_data["FVG"][i]):
                x1 = int(
                    fvg_data["MitigatedIndex"][i]
                    if fvg_data["MitigatedIndex"][i] != 0
                    else len(df) - 1
                )
                fig.add_shape(
                    # Filled Rectangle
                    type="rect",
                    x0=df.index[i],
                    y0=fvg_data["Top"][i],
                    x1=df.index[x1],
                    y1=fvg_data["Bottom"][i],
                    line=dict(width=0),
                    fillcolor="yellow",
                    opacity=0.2,
                )
                mid_x = round((i + x1) / 2)
                mid_y = (fvg_data["Top"][i] + fvg_data["Bottom"][i]) / 2
                fig.add_trace(
                    go.Scatter(
                        x=[df.index[mid_x]],
                        y=[mid_y],
                        mode="text",
                        text="FVG",
                        textposition="middle center",
                        textfont=dict(color='rgba(255, 255, 255, 0.4)', size=8),
                    )
                )
        return fig

    # Add Swing Highs and Lows
    def add_swing_highs_lows(fig, df, swing_highs_lows_data):
        indexs = []
        level = []
        for i in range(len(swing_highs_lows_data)):
            if not np.isnan(swing_highs_lows_data["HighLow"][i]):
                indexs.append(i)
                level.append(swing_highs_lows_data["Level"][i])

        # Plot these lines on the graph
        for i in range(len(indexs) - 1):
            fig.add_trace(
                go.Scatter(
                    x=[df.index[indexs[i]], df.index[indexs[i + 1]]],
                    y=[level[i], level[i + 1]],
                    mode="lines",
                    line=dict(
                        color=(
                            "rgba(0, 128, 0, 0.2)"
                            if swing_highs_lows_data["HighLow"][indexs[i]] == -1
                            else "rgba(255, 0, 0, 0.2)"
                        ),
                    ),
                )
            )

        return fig

    bos_choch_data = smc.bos_choch(reliance_data, swing_data)

    # Add BOS and CHOCH to the original data for plotting
    reliance_data['BOS'] = bos_choch_data['BOS']
    reliance_data['CHOCH'] = bos_choch_data['CHOCH']
    reliance_data['BOS_CH_Level'] = bos_choch_data['Level']
    reliance_data['BrokenIndex'] = bos_choch_data['BrokenIndex']

    # Function to add BOS and CHOCH indicators to the figure
    def add_bos_choch(fig, df, bos_choch_data):
        for i in range(len(bos_choch_data['BOS'])):
            if not np.isnan(bos_choch_data['BOS'][i]) or not np.isnan(bos_choch_data['CHOCH'][i]):
                fig.add_trace(
                    go.Scatter(
                        x=[df.index[i]],
                        y=[bos_choch_data['Level'][i]],
                        mode="markers+text",
                        marker=dict(color="blue" if bos_choch_data['BOS'][i] == 1 else "red"),
                        text="BOS" if bos_choch_data['BOS'][i] else "CHOCH",
                        textposition="top center"
                    )
                )
        return fig


    ob_data = smc.ob(reliance_data, swing_data, close_mitigation=False)

    # Add OB data to the main dataframe for plotting
    reliance_data['OB'] = ob_data['OB']
    reliance_data['OBTop'] = ob_data['Top']
    reliance_data['OBBottom'] = ob_data['Bottom']
    reliance_data['OBVolume'] = ob_data['OBVolume']
    reliance_data['OBStrength'] = ob_data['Percentage']

    # Function to add Order Blocks to the chart
    # Function to add Order Blocks to the chart
    def add_order_blocks(fig, df, ob_data):
        for i in range(len(ob_data['OB'])):
            if not np.isnan(ob_data['OB'][i]):
                color = "green" if ob_data['OB'][i] == 1 else "red"  # Green for bullish, red for bearish
                fig.add_shape(
                    type="rect",
                    x0=df.index[i], x1=df.index[i+1] if i+1 < len(df.index) else df.index[i],
                    y0=ob_data['Bottom'][i], y1=ob_data['Top'][i],
                    fillcolor=color, opacity=0.3, line=dict(width=0)
                )
                # Use 'Percentage' instead of 'OBStrength'
                fig.add_trace(
                    go.Scatter(
                        x=[df.index[i]],
                        y=[(ob_data['Top'][i] + ob_data['Bottom'][i]) / 2],
                        mode="text",
                        text=f"OB ({ob_data['Percentage'][i]:.1f}%)",
                        textposition="middle center",
                        showlegend=False
                    )
                )
        return fig



    fig = add_order_blocks(fig, reliance_data, ob_data)
    fig = add_FVG(fig, reliance_data, fvg_data)
    fig = add_swing_highs_lows(fig, reliance_data, swing_data)
    fig = add_bos_choch(fig, reliance_data, bos_choch_data)


    # Customize the layout
    fig.update_layout(
        title="Reliance Stock with FVG and Swing Highs/Lows",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        template="plotly_dark"
    )

    return fig


def generate_plot_html(fig):
    """
    Converts a Plotly figure to an HTML string.
    """
    return pio.to_html(fig, full_html=False)
