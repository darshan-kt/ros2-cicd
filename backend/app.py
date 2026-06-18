from fastapi import FastAPI
from fastapi import WebSocket

from ros_bridge import *

app = FastAPI()


@app.get("/health")
def health():

    return {
        "publisher": publisher_alive,
        "subscriber": subscriber_alive,
        "system":
            publisher_alive and subscriber_alive
    }


@app.post("/reset")
def reset_counter():

    # call ROS service later

    return {
        "message":"reset sent"
    }


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):

    await ws.accept()

    while True:

        await ws.send_json(
            {
                "publisher": publisher_value,
                "subscriber": subscriber_value
            }
        )