import json
import websocket
from db_ops import insert_stock

with open("config.json") as f:
    config = json.load(f)

api_key = config["api_key"]
db_connection = config["db_connection"]

WS_URL = f"wss://ws.finnhub.io?token={api_key}"
symbols = ["AAPL", "TSLA", "GOOGL"]

def on_message(ws, message):
    data = json.loads(message)
    if "data" in data:
        for stock in data["data"]:
            symbol = stock["s"]
            price = stock["p"]
            timestamp = stock["t"]
            
            insert_query = f"""
            INSERT INTO stock_data (symbol, price, timestamp) 
            VALUES ('{symbol}', {price}, {timestamp});
            """
            conn.execute(insert_query)
            conn.commit()
            print(f"Inserted: {symbol} - {price} at {timestamp}")

def on_error(ws, error):
    print("Error:", error)

def on_close(ws, close_status_code, close_msg):
    print(f"Closed connection: {close_status_code}, {close_msg}")

def on_open(ws):
    print("Connected! Subscribing to symbols...")
    for symbol in symbols:
        ws.send(json.dumps({"type": "subscribe", "symbol": symbol}))  # Subscribe

ws = websocket.WebSocketApp(
    WS_URL, on_message=on_message, on_error=on_error, on_close=on_close
)
ws.on_open = on_open

ws.run_forever(ping_interval=30, ping_timeout=10)