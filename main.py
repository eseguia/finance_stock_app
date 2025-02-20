# pip install psycopg2-binary websocket-client pandas sqlalchemy

import subprocess

print("Starting WebSocket client...")
subprocess.Popen(["python", "websocket_client.py"])
