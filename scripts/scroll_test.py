"""Run a configurable pure scroll test without clicking."""

from __future__ import annotations

import time


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


def ask_int(prompt: str, default: int) -> int:
    """Read an integer with a default value."""
    raw_value = input(prompt).strip()
    return int(raw_value) if raw_value else default


def ask_float(prompt: str, default: float) -> float:
    """Read a float with a default value."""
    raw_value = input(prompt).strip()
    return float(raw_value) if raw_value else default


def main() -> None:
    """Run a configurable pure scroll test."""
    try:
        pyautogui = get_pyautogui()
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.2

        print("Pure scroll test")
        print("This script will not click or move the mouse.")
        print("Before the countdown ends, move your mouse onto the creator list area.")

        scroll_amount = ask_int("Enter scroll amount per round (default -132): ", -132)
        scroll_count = ask_int("Enter scroll count (default 10): ", 10)
        wait_seconds = ask_float("Enter wait seconds between scrolls (default 1.2): ", 1.2)
        start_delay = ask_float("Enter start delay seconds (default 3): ", 3.0)

        if scroll_count < 1:
            raise ValueError("Scroll count must be 1 or greater.")
        if wait_seconds < 0:
            raise ValueError("Wait seconds must be 0 or greater.")
        if start_delay < 0:
            raise ValueError("Start delay seconds must be 0 or greater.")

        print("Scroll test summary")
        print(f"Scroll amount: {scroll_amount}")
        print(f"Scroll count: {scroll_count}")
        print(f"Wait seconds: {wait_seconds}")
        print(f"Start delay: {start_delay}")

        print(f"{start_delay} seconds later, the script will start.")
        time.sleep(start_delay)
        current_x, current_y = pyautogui.position()
        print(f"Current mouse position: ({current_x}, {current_y})")

        for index in range(1, scroll_count + 1):
            print(f"Scroll {index} / {scroll_count}: {scroll_amount}")
            pyautogui.scroll(scroll_amount)
            if index < scroll_count and wait_seconds > 0:
                time.sleep(wait_seconds)

        print("Scroll test finished")

    except Exception as exc:
        print("Program error")
        print(f"Error type: {type(exc).__name__}")
        print(f"Error detail: {repr(exc)}")


if __name__ == "__main__":
    main()
