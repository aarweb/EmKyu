#TODO: Devuelve datos erróneos.
from get_data import get_training_data

# DATAFRAME DE DATOS DESDE EL GET_DATA
df = get_training_data()
# print(df)


# DATA CLEANING
import pandas as pd
import numpy as np
import json

def clean_trades(df_tr):
    df = df_tr.copy()
    
    # 1. Extraer precio (Complex a Float)
    df['price_last'] = df['price_last'].apply(lambda x: x.get('rhs') if isinstance(x, dict) else x)
    # Si es string (como vimos antes), lo parseamos
    df['price_last'] = pd.to_numeric(df['price_last'], errors='coerce')
    
    # 2. Asegurar tipos numéricos en volumen
    df['volume_sum'] = pd.to_numeric(df['volume_sum'], errors='coerce').fillna(0.0)
    
    # 3. Tiempo
    df['__time'] = pd.to_datetime(df['__time'])
    
    # 4. Agregación por minuto y símbolo
    # Calculamos: Precio promedio, Volumen total y Volatilidad (Max-Min)
    df_min = df.groupby([pd.Grouper(key='__time', freq='1min'), 'name']).agg({
        'price_last': 'mean',
        'price_max': 'max',
        'price_min': 'min',
        'volume_sum': 'sum'
    }).reset_index()
    
    # 5. Renombrar columnas para evitar colisiones en el Merge
    df_min = df_min.rename(columns={
        'price_last': 'trade_price_avg',
        'volume_sum': 'trade_volume'
    })
    
    return df_min

result = clean_trades(df)
print(result)