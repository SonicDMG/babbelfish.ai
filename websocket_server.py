# websocket_server.py
from fastapi import FastAPI, WebSocket
import uvicorn
from threading import Thread

class WebSocketServer:
    def __init__(self, host="0.0.0.0", port=8000):
        self.host = host
        self.port = port
        self.app = FastAPI()

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            while True:
                data = await websocket.receive_text()
                # Process the data and send a response
                await websocket.send_text(f"Message received from server: {data}")

    def run(self):
        uvicorn.run(self.app, host=self.host, port=self.port)

    def run_in_thread(self):
        server_thread = Thread(target=self.run)
        server_thread.start()
        return server_thread

# Example usage:
if __name__ == "__main__":
    server = WebSocketServer()
    server.run()
