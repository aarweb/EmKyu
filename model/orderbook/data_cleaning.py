from get_data import get_training_data

# DATAFRAME DE DATOS DESDE EL GET_DATA
df = get_training_data()
# print(df)


# DATA CLEANING
import pandas as pd
import numpy as np
import json

def clean_orderbook(df):
    df = df.copy()

    # 1. Función para extraer el valor de la cadena JSON/String
    def extract_val(val):
        if pd.isna(val) or val is None: return np.nan
        if isinstance(val, dict): return val.get('rhs')
        
        # Si es un string tipo '{"lhs":..., "rhs": 75859.5}'
        if isinstance(val, str) and '{' in val:
            try:    
                # Limpiamos el string por si acaso y cargamos json
                d = json.loads(val.replace("'", '"').replace("None", "null"))
                return d.get('rhs')
            except:
                return np.nan
        return val

    # 2. Aplicar la extracción a las columnas COMPLEX
    complex_cols = [
        'best_bid_price_last', 'best_ask_price_last', 
        'best_bid_qty_last', 'best_ask_qty_last'
    ]
    
    for col in complex_cols:
        if col in df.columns:
            print(f"Procesando columna: {col}...")
            df[col] = df[col].apply(extract_val)
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # 3. PARCHE DE SEGURIDAD (Si 'last' es NaN, usamos min/max)
    # Esto asegura que si el JSON decía "rhs": null, tengamos un precio real
    df['best_bid_price_last'] = df['best_bid_price_last'].fillna(df['best_bid_price_min'])
    df['best_ask_price_last'] = df['best_ask_price_last'].fillna(df['best_ask_price_max'])
    
    # Si después de esto sigue habiendo NaNs (porque min/max también eran NaN), forward fill
    df = df.sort_values(['symbol', '__time'])
    df[['best_bid_price_last', 'best_ask_price_last']] = df.groupby('symbol')[['best_bid_price_last', 'best_ask_price_last']].ffill()

    # 4. Tratamiento de Timestamps
    df['__time'] = pd.to_datetime(df['__time'])
    
    # 5. Agregación por Minuto
    df_min = df.groupby([pd.Grouper(key='__time', freq='1min'), 'symbol']).agg({
        'best_bid_price_last': 'mean',
        'best_ask_price_last': 'mean',
        'best_bid_qty_last': 'sum',
        'best_ask_qty_last': 'sum'
    }).reset_index()

    # 6. Cálculo de Features (Ahora sí con números reales)
    df_min['mid_price'] = (df_min['best_bid_price_last'] + df_min['best_ask_price_last']) / 2
    df_min['spread'] = df_min['best_ask_price_last'] - df_min['best_bid_price_last']
    
    denom = df_min['best_bid_qty_last'] + df_min['best_ask_qty_last']
    df_min['vobi'] = (df_min['best_bid_qty_last'] - df_min['best_ask_qty_last']) / denom.replace(0, 1e-9)

    return df_min

result = clean_orderbook(df)
print(result)
# --- Ejemplo de Integración ---
# df_raw = pd.read_sql(QUERY_ORDERBOOK, conn)
# df_ready = clean_orderbook(df_raw)