

connections = []

async def connect(websocket):
    await websocket.accept()
    connections.append(websocket)

def disconnect(websocket):
    if websocket in connections:
        connections.remove(websocket)

async def broadcast(message: str):
    for connection in connections:
        try:
            await connection.send_text(message)
        except:
            disconnect(connection)