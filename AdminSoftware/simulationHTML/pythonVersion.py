import asyncio
import websockets
import random

# Simulate LED position to match JavaScript (5 rows × 11 columns = 55)
NUM_ROWS = 1
NUM_COLUMNS = 1
SERVER_URI = "ws://localhost:9001"

async def simulate_esp(row, column):
    uri = SERVER_URI
    try:
        async with websockets.connect(uri) as websocket:
            esp_id = f"M-{row}-{column}"
            print(f"[{esp_id}] Connected")
            await websocket.send(esp_id)

            while True:
                try:
                    message = await websocket.recv()
                    # try:
                    #     decoded_message = message.decode('utf-8')
                    #     print(f"[{esp_id}] Received: {decoded_message}")
                    # except UnicodeDecodeError:
                    #     print(f"[{esp_id}] Received binary data: {message}")
                    print(f"[{esp_id}] Received binary data: {message}")

                    if message == "ping":
                        await websocket.send("pong")

                    # Simulate color updates
                    if random.random() < 0.1:
                        color_code = f"${random.choice(['1', '2'])}{random.randint(0, 0xFFFFFF):06X}"
                        await websocket.send(color_code)
                        print(f"[{esp_id}] Sent color: {color_code}")

                    await asyncio.sleep(1)
                except websockets.ConnectionClosed:
                    print(f"[{esp_id}] Connection closed.")
                    break

    except Exception as e:
        print(f"[{esp_id}] Error: {e}")

async def main():
    tasks = [
        simulate_esp(row, col)
        for row in range(NUM_ROWS)
        for col in range(NUM_COLUMNS)
    ]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
