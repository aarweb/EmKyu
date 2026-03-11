# EmKyu
Plataforma de inteligencia predictiva que transforma datos de mercado en tiempo real en proyecciones de valor para criptomonedas mediante baja latencia.



Creame un codigo mermaid que forme la arquitectura del siguiente proyecto:

[Backend] Aplicacion backend con websocket -> python, ese sera un servicio que se podra conectar los clientes via websocket, para accedera  recursos de apache druid.

[Scraper] Aplicacion scraper que sera un servicio de websocket, que sera el encargado de conectarse via websocket.

[Kafka] Sera quien reciba la información del scraper para guardarlo en apache druid.

[Procesamiento] Fastapi, para entrenar red neuronal 

[Apache Druid] Este es el encargado de gestionar todos las lecturas y escrituras de kafka,
Este tendra:
* Transacciones de dos monedas (Etherum, Bitcoin, DogeCoin)
* Apertura y cierre de mercado
*  OrderBook