import asyncio

from socketio import AsyncServer

from .druid.query import PyDruidClient

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
        ts = client.getCurrentSynthData()
        app.emit("tick", {"data": ts})
        asyncio.sleep(1000)


asyncio.run(main)
