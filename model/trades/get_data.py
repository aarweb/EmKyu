# TRAE DATOS DESDE EL DRUID (TRADES)
# LA CONSULTA TRAE LOS ÚLTIMOS 7 DÍAS
from pydruid.db import connect
import pandas as pd

def get_training_data():
    conn = connect(host='localhost', port=8888, path='/druid/v2/sql/', scheme='http')
    query = """
    SELECT 
        __time, name, side,
        price_last, volume_sum,
        price_max, price_min
    FROM "trades"
    WHERE __time >= CURRENT_TIMESTAMP - INTERVAL '6' HOUR
    """
    df = pd.read_sql(query, conn)
    return df

# df = get_training_data()

# print(df)