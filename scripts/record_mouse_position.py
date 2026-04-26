"""Record mouse coordinates by pressing F8 on Windows."""

from __future__ import annotations

import ctypes
import time
from pathlib import Path


VK_F8 = 0x77
VK_ESCAPE = 0x1B
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_PATH = DATA_DIR / "recorded_points.txt"


def get_pyautogui():
    """Import pyautogui with a helpful error message."""
    try:
        import pyautogui  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency: pyautogui. Please install it first with:\n"
            "pip install pyautogui"
        ) from exc

    return pyautogui


def main() -> None:
    """Record coordinates with F8 and exit with ESC."""
    try:
        pyautogui = get_pyautogui()
        pyautogui.FAILSAFE = True

        DATA_DIR.mkdir(parents=True, exist_ok=True)

        print("F8 coordinate recorder started.")
        print("Usage:")
        print("1. Enter a coordinate label")
        print("2. Move the mouse to the target position")
        print("3. Press F8 to record")
        print("4. Press ESC to quit")
        print("")
        print(f"Recorded results will also be appended to: {OUTPUT_PATH}")
        print("")

        while True:
            label = input("Enter coordinate label (example: creator_click, press Enter to use auto name): ").strip()
            if not label:
                label = f"point_{int(time.time())}"

            print(f"Ready to record: {label}")
            print("Move the mouse to the target position, then press F8.")
            print("Press ESC if you want to quit.")

            last_f8_down = False
            last_esc_down = False

            while True:
                x, y = pyautogui.position()
                print(f"\rCurrent mouse position: X={x:<5} Y={y:<5}", end="", flush=True)

                f8_down = bool(ctypes.windll.user32.GetAsyncKeyState(VK_F8) & 0x8000)
                esc_down = bool(ctypes.windll.user32.GetAsyncKeyState(VK_ESCAPE) & 0x8000)

                if esc_down and not last_esc_down:
                    print("\nStopped.")
                    return

                if f8_down and not last_f8_down:
                    record_text = f"{label}_x={x}\n{label}_y={y}\n"
                    with OUTPUT_PATH.open("a", encoding="utf-8") as file:
                        file.write(record_text + "\n")
                    print("")
                    print("Recorded")
                    print(f"{label}_x={x}")
                    print(f"{label}_y={y}")
                    print("")
                    break

                last_f8_down = f8_down
                last_esc_down = esc_down
                time.sleep(0.03)

    except Exception as exc:
        print("")
        print("Program error")
        print(f"Error type: {type(exc).__name__}")
        print(f"Error detail: {repr(exc)}")


if __name__ == "__main__":
    main()
