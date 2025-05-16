import websocket
import colorsys
import threading
import time
import ssl
import re

# WebSocket URI
_uri = "wss://kazar4.com:9001"

# Globals (shared between threads)
width = 30  # default, will be updated
height = 11
offset = 0
ws_ready = threading.Event()

# Function to convert HSV to HEX
def hsv_to_hex(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return "#{:02x}{:02x}{:02x}".format(int(r*255), int(g*255), int(b*255))

# Function to generate a rainbow pattern with an offset for animation
def generate_rainbow_pattern(width, height, offset):
    colors = []
    for y in range(height):
        for x in range(width):
            hue = ((x + offset) / width) + (y / height) / 2.0
            hex_color = hsv_to_hex(hue % 1.0, 1.0, 1.0)
            colors.append((x, y, hex_color))
    return colors

# WebSocket event handlers
def on_message(ws, message):
    global width
    print("Received:", message)

    match = re.match(r"lpe\s+(\d+)", message)
    if match:
        led_per_esp = int(match.group(1))
        width = 5 * led_per_esp
        print(f"LEDs per ESP: {led_per_esp}, Setting width to: {width}")
        ws_ready.set()  # Signal that we're ready to start animation

def on_error(ws, error):
    print("Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("### Connection closed ###")

def on_open(ws):
    print("Opened connection")
    ws.send("game")
    ws.send("getLEDPerEsp")
    # Start animation thread after we receive width info
    threading.Thread(target=wait_and_animate, args=(ws,)).start()

# Wait until we receive LED count, then start animation
def wait_and_animate(ws):
    ws_ready.wait()
    animate_rainbow(ws)

# Function to animate the rainbow pattern
def animate_rainbow(ws):
    global offset
    while True:
        colors = generate_rainbow_pattern(width, height, offset)
        for x, y, hex_color in colors:
            ws.send(f"setColor {x} {y} {hex_color}")
        offset += 1
        time.sleep(0.2)

# Create WebSocket connection
ws = websocket.WebSocketApp(_uri,
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)
ws.on_open = on_open

# Run WebSocket with SSL options
ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
