import json
import websocket
import time
import threading
from sqlalchemy import create_engine, text
from datetime import datetime
from pytickersymbols import PyTickerSymbols
import pandas as pd
import streamlit as st


stock_data = PyTickerSymbols()
nasdaq_tickers = stock_data.get_stocks_by_index('NASDAQ 100')
all_symbols = []
for stock in nasdaq_tickers:
    all_symbols.append(stock['symbol'])


with open("config.json") as f:
    config = json.load(f)

api_key = config["api_key"]
db_connection = config["db_connection"]

WS_URL = f"wss://ws.finnhub.io?token={api_key}"
symbols = ["TSLA"] # all_symbols # ["AAPL", "TSLA", "GOOGL"]

def get_db_connection():
    return create_engine(db_connection)  

conn = get_db_connection()

def insert_stock(conn, symbol, price, timestamp):
    """Inserts stock data into the database using a persistent connection"""
    try:
        with conn.begin():  
            conn.execute("INSERT INTO stocks (symbol, price, timestamp) VALUES (%s, %s, %s)", (symbol, price, timestamp))
    except Exception as e:
        print(f"Error inserting {symbol} - {price} at {timestamp}: {e}")


def on_message(ws, message):
    """Handles incoming WebSocket messages and inserts them into the database"""
    data = json.loads(message)

    if "data" in data:
        for stock in data["data"]:
            symbol = stock["s"]
            price = stock["p"]
            timestamp = stock["t"]  # ms

            timestamp = datetime.utcfromtimestamp(timestamp / 1000)  # ms -> s
            insert_stock(conn, symbol, price, timestamp)

            print(f"Inserted: {symbol} - {price} at {timestamp}")


def on_error(ws, error):
    print("Error:", error)

def on_close(ws, close_status_code, close_msg):
    print(f"Closed connection: {close_status_code}, {close_msg}")

def on_open(ws):
    print("Connected! Subscribing to symbols...")
    for symbol in symbols:
        ws.send(json.dumps({"type": "subscribe", "symbol": symbol}))  # Subscribe


# # Create WebSocket client
# ws = websocket.WebSocketApp(WS_URL, on_message=on_message, on_error=on_error, on_close=on_close)
# ws.on_open = on_open

# # Run WebSocket in a separate thread
# ws_thread = threading.Thread(target=ws.run_forever, kwargs={"ping_interval": 30, "ping_timeout": 10})
# ws_thread.start()

# # Stop WebSocket after 10 seconds
# time.sleep(10)
# ws.close()
# ws_thread.join()
# print("WebSocket closed after 10 seconds")


# Run the WebSocket in a separate thread to prevent blocking Streamlit
def run_websocket():
    ws = websocket.WebSocketApp(
        WS_URL, on_message=on_message, on_error=on_error, on_close=on_close
    )
    ws.on_open = on_open
    ws.run_forever(ping_interval=30, ping_timeout=10)

# Start the WebSocket thread
websocket_thread = threading.Thread(target=run_websocket)
websocket_thread.start()


# query = """
# SELECT timestamp, price
# FROM stocks
# WHERE symbol = 'TSLA' 
# ORDER BY timestamp;
# """

# # Fetch data into a Pandas DataFrame
# df = pd.read_sql(query, create_engine('postgresql://postgres:postgres@localhost:5432/fin_data'))

# # Check if the data was retrieved correctly
# if not df.empty:
#     # Convert timestamp to a readable datetime
#     df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

#     # Set timestamp as index for plotting
#     df.set_index('timestamp', inplace=True)

#     # Plot the data using Streamlit
#     st.line_chart(df['price'])

#     # Optionally, display the dataframe
#     st.dataframe(df)
# else:
#     st.warning("No data found.")


def fetch_data_from_sql():
    conn = create_engine(db_connection)
    query = """
    SELECT timestamp, price
    FROM stocks
    WHERE symbol = 'TSLA' 
    ORDER BY timestamp;
    """
    df = pd.read_sql(query, conn)
    return df

# # Display graph and data
# def show_graph():
#     df = fetch_data_from_sql()

#     # Plotting the graph
#     st.line_chart(df.set_index('timestamp')['price'])

# # Auto-refresh the data every 5 seconds
# while True:
#     show_graph()
#     time.sleep(5)  # Update every 5 seconds
#     st._rerun()  # Force the page to reload


chart_placeholder = st.empty()

# Function to update the chart
def update_chart():
    df = fetch_data_from_sql()

    # Update the graph with the new data
    chart_placeholder.line_chart(df.set_index('timestamp')['price'])

# Initial chart display
update_chart()

# Set up a loop for auto-refresh
while True:
    time.sleep(20)  # Wait for 5 seconds before refreshing the graph
    update_chart()  # Refresh the chart with new data