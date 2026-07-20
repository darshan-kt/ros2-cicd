import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from ros_bridge import (
    publisher_value,
    subscriber_value,
    publisher_alive,
    subscriber_alive,
    # reset_counter (if you have it, import it)
)

app = FastAPI()


@app.get("/health")
def health():
    return {
        "publisher": publisher_alive,
        "subscriber": subscriber_alive,
        "system": publisher_alive and subscriber_alive,
    }


@app.post("/reset")
def reset_counter():
    # TODO: call actual reset logic if available
    return {"message": "reset sent"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = {
                "publisher": publisher_value,
                "subscriber": subscriber_value,
            }

            await websocket.send_json(data)
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        print("WebSocket disconnected")

    except Exception as e:
        print("WebSocket error:", e)

    finally:
        try:
            await websocket.close()
        except Exception:
            pass