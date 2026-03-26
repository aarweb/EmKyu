# EmKyu
Plataforma de inteligencia predictiva que transforma datos de mercado en tiempo real en proyecciones de valor para criptomonedas mediante baja latencia.

[Backend] Aplicacion backend con *socket* -> python, este es un servicio conectado con los clientes via *socket*, para acceder a los recursos que predecimos nosotros.

[Scraper] Aplicacion *scraper* que es un servicio *socket*.

[Kafka] Recibe y distribuye la información del *scraper* a los servicios correspondientes.

[Procesamiento] Fastapi, para procesar los datos recibidos mediante un proceso de *Machine/Deep Learning* y obtener resultados.

[Apache Druid] Este es el encargado de gestionar todos las lecturas y escrituras de kafka,
Este tendra:
* Transacciones de cuatro monedas (Ethereum, Bitcoin, DogeCoin, Solana).
* Apertura y cierre de mercado.

--- 

# CONTRATO
## 1. Motivación del Proyecto, ¿Qué es lo que se quiere hacer?
Realizar una herramienta para obtener información útil a la hora de realizar predicciones en el mercado de las Criptomonedas.
Para ello se utilizan 3 partes principales conectadas mediante Kafka y Apache Druid.

1.  *Scraper (*socket* Service):* Scraper encargado de recolectar diversos datos de 3 *exchanges* y 4 monedas en cada *exchange*.
    1.  *Exchanges:* Binance, Kraken y ByBit.
    2.  Criptomonedas: Bitcoin, Solana, Ethereum y DogeCoin.
    3.  Valores Scrapeados: Valores identificativos y Precio y Volumen.
        1.  **PRECIO:** Es el límite superior al cual los clientes están dispuestos a pagar, no son operaciones cerradas por los usuarios (*trades*).
        2.  **VOLUMEN:** Es la suma total de todo lo que se ha negociado en las últimas 24 horas.
        3.  **TRADES INSTANTÁNEOS:** Obtener los últimos trades que están habiendo.

2.  Procesamiento: Realizar una modelo de Machine/Deep Learning (a mejorar en función de las pruebas) para poder obtener un resultado que a corto plazo nos diga qué clase es más probable que ocurra. Un **HIGH-FREQUENCY TRADING (HFT)**.

    1.  **¿QUÉ IDENTIFICA EL MODELO?**
        1.  **Identificación de absorción:** Si hay muchas órdenes de venta y el precio no baja la red detecta que hay un comprador gigante absorbiendo todos esos precios por lo que el precio va a rebotar.
        2.  **Barrido de liquidez:** Si hay muchas compras que agotan las órdenes de compra entiende que hay que comprar rápido para seguir el impulso.
        3.  **Presión de ventas:** Si el volumen de las ventas ejecutadas es 3 veces mayor al de las compras en los últimos 10 segundos, la red entiende que el precio va a caer.

    2.  **ESTRUCTURA DE LA PREDICCIÓN**
        1.  **Clase 0:** El precio subirá más de un 'X' % en los próximos 'Y' segundos.
        2.  **Clase 1:** El precio bajará más de un 'X' % en los próximos 'Y' segundos.
        3.  **Clase 2:** El precio se mantendrá igual (**HOLD/NEUTRAL**).

3.  *socket*: Habilitar un *Socket* para que los clientes se puedan conectar y ver según nuestras predicciones cuales son las tendencias del mercado y las operaciones más inteligentes a realizar.

4.  Se tienen pensadas algunas evoluciones del proyecto que en el caso de que nos sobre tiempo del planificado se aplicarán.

---

## 2. Diagrama
*   Se encuentra en el *GitHub* en el cual se está trabajando.
*   Se explican correctamente la forma de proceder en el proyecto.

---

## 3. Descripción de los casos de uso.
En este proyecto cualquier usuario se puede conectar a nuestro *Socket* y obtener las predicciones que realicemos. No van a haber roles en el despliegue.

---

## 4. Capas.
*   **Este proyecto no incluye una interfaz de usuario *frontend*.**

---

## 5. Calendario con los Hitos.
| SEMANA | HITO | FUNCIONALIDAD CRÍTICA |
| :--- | :--- | :--- |
| **Semana 1**<br>*(24 Mar - 31 Mar)* | **Data Pipeline Completo** | Conectar Scraper a Kafka. Configurar el *Supervisor* en Druid para ingerir `Trades`. Los datos deben estar disponibles para consulta inmediata. |
| **Semana 2**<br>*(01 Abr - 07 Abr)* | **Feature & Model Training** | Extracción de datos históricos desde Druid. Definición programática de la lógica de **Absorción** y **Barrido de Liquidez**. Entrenamiento inicial de la red neuronal. |
| **Semana 3**<br>*(08 Abr - 14 Abr)* | **Inferencia & Backend** | Integración del modelo en FastAPI. El Backend debe procesar la salida del modelo y habilitar el servidor de **Sockets** para la conexión de clientes finales. |
| **Semana 4**<br>*(15 Abr - 21 Abr)* | **Stress Test & Deploy** | Prueba de carga **CIERRE Y ENTREGA.** |
---

>AUTORES: Equipo Gatitas (Adrián M. Romero Viró, Aarón Carrera Pascual, Isaías Beneito Ribera)