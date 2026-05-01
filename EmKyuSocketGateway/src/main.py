import asyncio

from socketio import AsyncServer

from druid.query import PyDruidClient

app = AsyncServer()


@app.event
def connect():
    pass


@app.event
def disconnect():
    pass


async def main():
    client = PyDruidClient()
    while True:
        ts = client.getCurrentData()
        app.emit("data-tick", {"data": ts})
<<<<<<< Updated upstream
        await asyncio.sleep(5)
        
=======
        await asyncio.sleep(1) 
>>>>>>> Stashed changes


asyncio.run(main())
