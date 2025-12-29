# Raspberry Pi Pico W - USB HID Mouse/Keyboard Controller
# Flash this to your Pico W using Thonny or mpremote
# Requires CircuitPython with adafruit_hid library

import usb_hid
from adafruit_hid.mouse import Mouse
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import wifi
import socketpool
import json
import time

# ============ CONFIGURATION ============
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"
SERVER_PORT = 8888
# =======================================

# Initialize HID devices
mouse = Mouse(usb_hid.devices)
keyboard = Keyboard(usb_hid.devices)

# Keycode mapping for common keys
KEY_MAP = {
    "enter": Keycode.ENTER,
    "tab": Keycode.TAB,
    "space": Keycode.SPACE,
    "backspace": Keycode.BACKSPACE,
    "escape": Keycode.ESCAPE,
    "up": Keycode.UP_ARROW,
    "down": Keycode.DOWN_ARROW,
    "left": Keycode.LEFT_ARROW,
    "right": Keycode.RIGHT_ARROW,
    "ctrl": Keycode.CONTROL,
    "alt": Keycode.ALT,
    "shift": Keycode.SHIFT,
    "win": Keycode.GUI,
}

def connect_wifi():
    print(f"Connecting to {WIFI_SSID}...")
    wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
    print(f"Connected! IP: {wifi.radio.ipv4_address}")
    return str(wifi.radio.ipv4_address)

def handle_command(cmd):
    """Process incoming commands"""
    try:
        data = json.loads(cmd)
        action = data.get("action")

        if action == "move":
            # Relative mouse move
            x = int(data.get("x", 0))
            y = int(data.get("y", 0))
            mouse.move(x, y)
            return {"status": "ok", "action": "move"}

        elif action == "move_to":
            # Move to absolute position (in steps)
            x = int(data.get("x", 0))
            y = int(data.get("y", 0))
            steps = max(abs(x), abs(y)) // 10 + 1
            dx = x // steps
            dy = y // steps
            for _ in range(steps):
                mouse.move(dx, dy)
                time.sleep(0.01)
            return {"status": "ok", "action": "move_to"}

        elif action == "click":
            button = data.get("button", "left")
            if button == "left":
                mouse.click(Mouse.LEFT_BUTTON)
            elif button == "right":
                mouse.click(Mouse.RIGHT_BUTTON)
            elif button == "middle":
                mouse.click(Mouse.MIDDLE_BUTTON)
            return {"status": "ok", "action": "click"}

        elif action == "double_click":
            mouse.click(Mouse.LEFT_BUTTON)
            time.sleep(0.1)
            mouse.click(Mouse.LEFT_BUTTON)
            return {"status": "ok", "action": "double_click"}

        elif action == "scroll":
            amount = int(data.get("amount", 0))
            mouse.move(0, 0, amount)
            return {"status": "ok", "action": "scroll"}

        elif action == "type":
            # Type text character by character
            text = data.get("text", "")
            for char in text:
                keyboard.send(Keycode.A + (ord(char.lower()) - ord('a')))
            return {"status": "ok", "action": "type"}

        elif action == "key":
            # Press special key
            key = data.get("key", "").lower()
            if key in KEY_MAP:
                keyboard.send(KEY_MAP[key])
            return {"status": "ok", "action": "key"}

        elif action == "hotkey":
            # Press key combination (e.g., Ctrl+C)
            keys = data.get("keys", [])
            keycodes = [KEY_MAP.get(k.lower()) for k in keys if k.lower() in KEY_MAP]
            if keycodes:
                keyboard.send(*keycodes)
            return {"status": "ok", "action": "hotkey"}

        elif action == "ping":
            return {"status": "ok", "action": "pong"}

        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

def start_server(ip):
    """Start TCP server to receive commands"""
    pool = socketpool.SocketPool(wifi.radio)
    sock = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
    sock.bind((ip, SERVER_PORT))
    sock.listen(1)
    print(f"Server listening on {ip}:{SERVER_PORT}")

    while True:
        try:
            conn, addr = sock.accept()
            print(f"Connection from {addr}")
            buffer = bytearray(1024)

            while True:
                try:
                    size = conn.recv_into(buffer)
                    if size == 0:
                        break

                    cmd = buffer[:size].decode('utf-8').strip()
                    result = handle_command(cmd)
                    conn.send(json.dumps(result).encode('utf-8'))

                except Exception as e:
                    print(f"Error: {e}")
                    break

            conn.close()
        except Exception as e:
            print(f"Server error: {e}")

# Main
ip = connect_wifi()
start_server(ip)
