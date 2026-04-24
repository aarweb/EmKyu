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
        await asyncio.sleep(5)
        


asyncio.run(main())
