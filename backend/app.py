import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

import ros_bridge


@asynccontextmanager
async def lifespan(app: FastAPI):
    ros_bridge.start()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "publisher": ros_bridge.publisher_alive,
        "subscriber": ros_bridge.subscriber_alive,
        "system": ros_bridge.publisher_alive and ros_bridge.subscriber_alive,
    }


@app.post("/reset")
def reset_counter():
    success = ros_bridge.reset_counter()
    return {"message": "reset sent" if success else "reset failed"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = {
                "publisher": ros_bridge.publisher_value,
                "subscriber": ros_bridge.subscriber_value,
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