# TRAE DATOS DESDE EL DRUID (ORDERBOOK)
# LA CONSULTA TRAE LOS ÚLTIMOS 7 DÍAS
from pydruid.db import connect
import pandas as pd

def get_training_data():
    conn = connect(host='localhost', port=8888, path='/druid/v2/sql/', scheme='http')
    query = """
        SELECT __time, symbol, broker, 
            best_bid_price_last, best_ask_price_last, 
            best_bid_qty_last, best_ask_qty_last,
            best_bid_price_min, best_ask_price_max
        FROM "orderbook"
        WHERE __time >= CURRENT_TIMESTAMP - INTERVAL '6' HOUR
        """
    df = pd.read_sql(query, conn)
    return df

# df = get_training_data()

# print(df)