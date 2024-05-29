import websocket
import colorsys
import threading
import time
import ssl

# WebSocket URI
_uri = "wss://kazar4.com:9001"

# Function to convert HSV to HEX
def hsv_to_hex(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return "#{:02x}{:02x}{:02x}".format(int(r*255), int(g*255), int(b*255))

# Function to generate a rainbow pattern with an offset for animation
def generate_rainbow_pattern(width, height, offset):
    colors = []
    for y in range(height):
        for x in range(width):
            hue = ((x + offset) / width) + (y / height) / 2.0  # Adjusting the hue based on position and offset
            hex_color = hsv_to_hex(hue % 1.0, 1.0, 1.0)
            colors.append((x, y, hex_color))
    return colors

# WebSocket event handlers
def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    print("Opened connection")
    ws.send("game")
    # Start the animation loop
    threading.Thread(target=animate_rainbow, args=(ws,)).start()

# Function to animate the rainbow pattern
def animate_rainbow(ws):
    width, height = 10, 11
    offset = 0
    while True:
        colors = generate_rainbow_pattern(width, height, offset)
        for x, y, hex_color in colors:
            command = f"setColor {x} {y} {hex_color}"
            ws.send(command)
        offset += 1
        time.sleep(1)

# Create WebSocket connection
ws = websocket.WebSocketApp(_uri,
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)
ws.on_open = on_open

# Run WebSocket with SSL options
ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})