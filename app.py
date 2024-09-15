import matplotlib
matplotlib.use('Agg')  # Set the backend to 'Agg' for non-GUI environments

from flask import Flask, render_template, request, jsonify, session
import requests
from models import db, SelectedStock
import matplotlib.pyplot as plt
import os
import yfinance as yf
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required to use sessions


@app.route('/')
def index():
    return render_template('home.html')

@app.route('/markets')
def markets():
    return render_template('markets.html')

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stocks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def create_db():
    """Create database tables if they do not exist."""
    with app.app_context():
        db.create_all()

# Function to fetch stock data from the unofficial NSE API
def get_nse_stock_data(symbol):
    url = f"https://www.nseindia.com/api/search/autocomplete?q={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0",  # Required to avoid being blocked
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Route to handle stock search queries
@app.route('/search_stock', methods=['GET'])
def search_stock():
    query = request.args.get('q')
    if query:
        stock_data = get_nse_stock_data(query)
        if stock_data:
            results = [
                {
                    'symbol': stock.get('symbol', ''),
                    'name': stock.get('symbol_info', '')
                }
                for stock in stock_data.get('symbols', [])
            ]
            return jsonify(results)
    return jsonify([])

# Route to add selected stocks to the database
@app.route('/add_stock', methods=['POST'])
def add_stock_route():
    stock_symbol = request.json.get('symbol')
    if stock_symbol:
        # Add stock to the database
        existing_stock = SelectedStock.query.filter_by(symbol=stock_symbol).first()
        if not existing_stock:
            new_stock = SelectedStock(symbol=stock_symbol)
            db.session.add(new_stock)
            db.session.commit()
    # Fetch updated stocks from the database
    selected_stocks = [stock.symbol for stock in SelectedStock.query.all()]
    return jsonify(selected_stocks)

# Route to remove stock from the database
@app.route('/remove_stock', methods=['POST'])
def remove_stock_route():
    stock_symbol = request.args.get('symbol')
    if stock_symbol:
        stock = SelectedStock.query.filter_by(symbol=stock_symbol).first()
        if stock:
            db.session.delete(stock)
            db.session.commit()
    # Fetch updated stocks from the database
    selected_stocks = [stock.symbol for stock in SelectedStock.query.all()]
    return jsonify(selected_stocks)

# Route to get selected stocks
@app.route('/get_selected_stocks', methods=['GET'])
def get_selected_stocks_route():
    selected_stocks = [stock.symbol for stock in SelectedStock.query.all()]
    return jsonify(selected_stocks)

# Route to analyze stock and store in session
@app.route('/set_stock_for_analysis', methods=['POST'])
def set_stock_for_analysis():
    stock_symbol = request.json.get('symbol')
    if stock_symbol:
        session['stock_symbol'] = stock_symbol + ".NS"  # Set the symbol in session
        return jsonify({'message': f'Stock {stock_symbol} set for analysis'}), 200
    return jsonify({'error': 'No stock symbol provided'}), 400


# Route to display indicators for analysis
@app.route('/indicators')
def indicators():
    stock_symbol = session.get('stock_symbol')  # Retrieve the stock symbol from the session
    return render_template('indicators.html', stock_symbol=stock_symbol, indicators=indicators)

@app.route('/seasonality')
def seasonality():
    # Retrieve the stock symbol from the session
    stock_symbol = session.get('stock_symbol')
    
    if not stock_symbol:
        return "No stock symbol found in session.", 400

    # Download stock data using the symbol from session
    data = yf.download(stock_symbol, start="2004-01-01", end="2024-01-01")
    
    if data.empty:
        return f"No data found for symbol: {stock_symbol}.", 404

    # Convert index to DatetimeIndex if it's not already
    if not isinstance(data.index, pd.DatetimeIndex):
        data.index = pd.to_datetime(data.index)

    # Fill missing data
    data.fillna(method='ffill', inplace=True)

    # Extract month and calculate monthly average closing price
    data['Month'] = data.index.month
    monthly_avg_close = data.groupby('Month')['Close'].mean()

    # Plot the seasonality graph
    plt.figure(figsize=(10, 6))
    plt.plot(monthly_avg_close.index, monthly_avg_close.values, marker='o')
    plt.xticks(monthly_avg_close.index, ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    plt.xlabel('Month')
    plt.ylabel('Average Closing Price')
    plt.title(f'Seasonality Pattern in Stock Prices ({stock_symbol})')

    plt.grid(True)

    # Save the plot as an image
    img_path = os.path.join('static', 'seasonality_plot.png')
    plt.savefig(img_path)
    plt.close()

    # Serve the image to the front-end
    return render_template('seasonality.html', img_path=img_path)

if __name__ == '__main__':
    create_db()  # Ensure tables are created
    app.run(debug=True)
