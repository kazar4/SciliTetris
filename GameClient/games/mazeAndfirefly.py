import websocket
import colorsys
import threading
import time
import ssl
import random
import re

# WebSocket URI
_uri = "wss://kazar4.com:9001"

# Globals
width = 20
height = 11
ws_ready = threading.Event()
ws_global = None

# WebSocket handlers
def on_message(ws, message):
    global width
    match = re.match(r"lpe\s+(\d+)", message)
    if match:
        led_per_esp = int(match.group(1))
        width = 5 * led_per_esp
        print(f"[+] Grid width set to: {width}")
        ws_ready.set()

def on_error(ws, error):
    print("Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("### Connection closed ###")

def on_open(ws):
    print("[+] WebSocket connection opened")
    ws.send("game")
    ws.send("getLEDPerEsp")

# Utility
def hsv_to_hex(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return "#{:02x}{:02x}{:02x}".format(int(r*255), int(g*255), int(b*255))

def set_color(ws, x, y, hex_color):
    ws.send(f"setColor {x} {y} {hex_color}")

# 🌟 Firefly Sync
def run_firefly(ws, palette="yellow"):
    print(f"[*] Starting Firefly Sync with palette: {palette}")
    phases = [[random.random() for _ in range(width)] for _ in range(height)]

    # Pick palette
    if palette == "blue":
        base_hue = 0.6  # blue
    elif palette == "pink":
        base_hue = 0.9  # pink/magenta
    elif palette == "random":
        base_hue = random.random()
    else:
        base_hue = 0.15  # original firefly green-yellow

    while True:
        for y in range(height):
            for x in range(width):
                phases[y][x] += 0.02
                if phases[y][x] >= 1.0:
                    phases[y][x] = 0.0
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < width and 0 <= ny < height:
                                phases[ny][nx] += 0.05
                                phases[ny][nx] = min(phases[ny][nx], 1.0)
                brightness = 1.0 - abs(phases[y][x] - 0.5) * 2
                color = hsv_to_hex(base_hue, 1, brightness)
                set_color(ws, x, y, color)
        time.sleep(0.1)

# 🔥 Fire Simulation
def run_fire(ws):
    print("[*] Starting Fire Simulation")

    heat = [[0 for _ in range(width)] for _ in range(height)]

    def heat_to_color(heat_value):
        h = 0.05  # red-orange
        s = 1.0
        v = heat_value
        return hsv_to_hex(h, s, v)

    while True:
        # Step 1: Cool down
        for y in range(height):
            for x in range(width):
                heat[y][x] = max(0, heat[y][x] - random.uniform(0, 0.05))

        # Step 2: Propagate upward
        for y in range(height-2, -1, -1):  # skip bottom row
            for x in range(width):
                below = heat[y+1][x]
                left = heat[y+1][x-1] if x > 0 else below
                right = heat[y+1][x+1] if x < width-1 else below
                heat[y][x] = (below + left + right) / 3.1

        # Step 3: Random heat at bottom
        for x in range(width):
            if random.random() < 0.6:
                heat[height-1][x] = random.uniform(0.6, 1.0)

        # Step 4: Draw
        for y in range(height):
            for x in range(width):
                color = heat_to_color(heat[y][x])
                set_color(ws, x, y, color)
        time.sleep(0.05)

# Menu
def start_animation(ws):
    ws_ready.wait()
    print("\nChoose a simulation:")
    print("1. Firefly Sync")
    print("2. Fire Simulation")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        print("\nChoose firefly color palette:")
        print("• yellow (default)")
        print("• blue")
        print("• pink")
        print("• random")
        palette = input("Color palette: ").strip().lower() or "yellow"
        run_firefly(ws, palette)
    elif choice == "2":
        run_fire(ws)
    else:
        print("Invalid choice.")
        ws.close()

# WebSocket client
def start_client():
    global ws_global
    ws = websocket.WebSocketApp(_uri,
                                 on_message=on_message,
                                 on_error=on_error,
                                 on_close=on_close)
    ws.on_open = on_open
    ws_global = ws

    def run():
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    threading.Thread(target=run).start()
    threading.Thread(target=start_animation, args=(ws,)).start()

# Run
if __name__ == "__main__":
    start_client()
