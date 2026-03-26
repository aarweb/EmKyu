# Implementación de Brokers

## Heredar de la clase padre BrokerClient e implementar métodos

Nota: Previamente, se pensó en utilizar un paradigma puramente funcional, lo cual sería más eficiente. Sin embargo, por razones de simplificación,
se optó por OOP para agilizar el desarrollo. Se hubiera trabajado con punteros a funciones (referencias de funciones).

### Métodos

#### create

Método estático factory para instanciar la clase.

#### connect

Gestiona la conexión inicial con el socket del broker particular. Se realizarán todas las acciones necesarias para establecer un flujo de conexión fijo durante el programa.

#### onListen

Se encarga de realizar una determinada acción cada vez que el socket escucha y recibe datos. Procesa los datos recibidos para el sistema de queeing de kafka para que se encargue de
inyectar la carga masiva de datos dentro de Apache Druid para su posterior explotación.

#### close

Libera los recursos del socket

### Consideraciones

Debido a las particularidades de los brokers, cada uno de los siguientes métodos deben ser implementados indivualmente por broker, debido a sus diferencias fundamentales
en cuanto a diseño de api. (Ejemplo: Binance recibe la configuración de los topics por URI, mientras que Bybit requiere de un envío de un json previamente para verificar la suscripción a los tópicos).
