"""Live mouse position tracker. Run, move the mouse, read X/Y. Ctrl+C to quit.
Press Enter to freeze/print a line you can note down."""
import pyautogui, time, threading, sys

hit = threading.Event()
threading.Thread(target=lambda: [sys.stdin.readline() or hit.set() for _ in iter(int, 1)], daemon=True).start()
w, h = pyautogui.size()
print(f"Screen {w}x{h}. Enter = log current position, Ctrl+C = quit")
try:
    while True:
        x, y = pyautogui.position()
        print(f"\rX: {x:4d}  Y: {y:4d}   ", end="", flush=True)
        if hit.is_set():
            print(f"\rLOGGED -> [{x}, {y}]          "); hit.clear()
        time.sleep(0.05)
except KeyboardInterrupt:
    print("\nbye")
