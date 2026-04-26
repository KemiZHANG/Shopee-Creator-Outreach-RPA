"""Record a screen region by capturing top-left and bottom-right mouse points."""

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


def countdown(seconds: int, message: str) -> None:
    """Show a simple countdown."""
    for remaining in range(seconds, 0, -1):
        print(f"{message} {remaining}...")
        time.sleep(1)


def main() -> None:
    """Record a region for OCR or screenshot capture."""
    try:
        pyautogui = get_pyautogui()
        pyautogui.FAILSAFE = True

        label = input("Enter region label (default nickname_region): ").strip() or "nickname_region"
        wait_seconds_raw = input("Enter countdown seconds before each capture (default 3): ").strip()
        wait_seconds = int(wait_seconds_raw) if wait_seconds_raw else 3
        if wait_seconds < 1:
            raise ValueError("Countdown seconds must be 1 or greater.")

        print("Step 1: move the mouse to the TOP-LEFT corner of the target region.")
        countdown(wait_seconds, "Capturing top-left in")
        left, top = pyautogui.position()
        print(f"Top-left captured: ({left}, {top})")

        print("Step 2: move the mouse to the BOTTOM-RIGHT corner of the target region.")
        countdown(wait_seconds, "Capturing bottom-right in")
        right, bottom = pyautogui.position()
        print(f"Bottom-right captured: ({right}, {bottom})")

        region_left = min(left, right)
        region_top = min(top, bottom)
        region_width = abs(right - left)
        region_height = abs(bottom - top)

        print("")
        print("Region result")
        print(f"{label}_left={region_left}")
        print(f"{label}_top={region_top}")
        print(f"{label}_width={region_width}")
        print(f"{label}_height={region_height}")

        if region_width == 0 or region_height == 0:
            print("Warning: width or height is 0, please record again.")

    except Exception as exc:
        print("Program error")
        print(f"Error type: {type(exc).__name__}")
        print(f"Error detail: {repr(exc)}")


if __name__ == "__main__":
    main()
