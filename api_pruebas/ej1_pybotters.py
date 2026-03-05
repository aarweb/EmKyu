import asyncio
import pybotters
import pandas as pd
from datetime import datetime

class MLFeatureCollector:
    def __init__(self):
        self.data_history = []

    def calculate_features(self, b_store, by_store):
        # 1. Obtener trades recientes
        b_trades = b_store.trade.find()
        by_trades = by_store.trade.find()
        
        if not b_trades or not by_trades:
            return None

        # 2. Ingeniería de Características básica
        last_b_price = float(b_trades[-1]['p'])
        last_by_price = float(by_trades[-1]['p'])
        
        # Ratio de compra/venta (Binance)
        buys = len([t for t in b_trades[-50:] if not t['m']])
        sells = len([t for t in b_trades[-50:] if t['m']])
        buy_ratio = buys / (buys + sells) if (buys + sells) > 0 else 0.5

        # Estructura de la fila
        feature_row = {
            "timestamp": datetime.utcnow().isoformat(),
            "price_binance": last_b_price,
            "price_bybit": last_by_price,
            "spread": last_b_price - last_by_price,
            "binance_buy_ratio": buy_ratio,
            "target_price_60s": None # Esto se llena "en el futuro" para el entrenamiento
        }
        return feature_row

async def main():
    collector = MLFeatureCollector()
    
    async with pybotters.Client() as client:
        b_store = pybotters.BinanceSpotDataStore()
        by_store = pybotters.BybitDataStore()

        await asyncio.gather(
            client.ws_connect("wss://stream.binance.com:9443/ws/btcusdt@trade", hdlr_json=b_store.onmessage),
            client.ws_connect("wss://stream.bybit.com/v5/public/spot", 
                              send_json={"op": "subscribe", "args": ["publicTrade.BTCUSDT"]},
                              hdlr_json=by_store.onmessage)
        )

        print("🧠 Recolectando Features para el modelo de ML...")

        for _ in range(100): # Capturamos 100 muestras de ejemplo
            row = collector.calculate_features(b_store, by_store)
            if row:
                collector.data_history.append(row)
                print(f"Muestra {len(collector.data_history)} capturada. Spread: {row['spread']:.2f}")
            
            await asyncio.sleep(1) # Una muestra por segundo

        # Guardar para entrenamiento
        df = pd.DataFrame(collector.data_history)
        df.to_csv("datos_entrenamiento.csv", index=False)
        print("✅ Archivo 'datos_entrenamiento.csv' creado.")

if __name__ == "__main__":
    asyncio.run(main())