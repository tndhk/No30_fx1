import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_path="data/market_data.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS candles (
            instrument TEXT,
            granularity TEXT,
            time TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            PRIMARY KEY (instrument, granularity, time)
        )
        """
        self.conn.execute(query)
        self.conn.commit()

    def save_candles(self, instrument, granularity, candles):
        data = []
        for candle in candles:
            # OANDA returns time in RFC3339 format, e.g., "2023-10-01T00:00:00.000000000Z"
            # We keep it as string for simplicity in SQLite
            time = candle["time"]
            o = float(candle["mid"]["o"])
            h = float(candle["mid"]["h"])
            l = float(candle["mid"]["l"])
            c = float(candle["mid"]["c"])
            v = int(candle["volume"])
            data.append((instrument, granularity, time, o, h, l, c, v))

        query = """
        INSERT OR IGNORE INTO candles (instrument, granularity, time, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.conn.executemany(query, data)
        self.conn.commit()
        print(f"Saved {len(data)} candles for {instrument} {granularity}")

    def close(self):
        self.conn.close()
