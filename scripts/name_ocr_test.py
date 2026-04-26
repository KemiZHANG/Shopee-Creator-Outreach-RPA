"""Test the configured OCR region for creator nickname recognition."""

from __future__ import annotations

import time

from automation_utils import (
    RunLogger,
    ask_float,
    ensure_dirs,
    get_pyautogui,
    get_pytesseract,
    load_config,
    read_creator_name,
)


def main() -> None:
    """Capture the nickname region once and print the OCR result."""
    ensure_dirs()
    logger = RunLogger()

    try:
        config = load_config()
        pyautogui = get_pyautogui()
        pytesseract = get_pytesseract(config)

        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.2

        start_delay = ask_float(
            "Enter start delay seconds (default 3): ",
            config["timings"]["default_start_delay_seconds"],
        )

        logger.log("Nickname OCR test will start soon.")
        logger.log("Please switch to the creator page before the countdown ends.")
        time.sleep(start_delay)

        raw_name, normalized_name, capture_path = read_creator_name(
            pyautogui=pyautogui,
            pytesseract=pytesseract,
            config=config,
            logger=logger,
            creator_index=1,
        )

        logger.log(f"Saved nickname capture to: {capture_path}")
        logger.log(f"Final raw nickname: {repr(raw_name)}")
        logger.log(f"Final normalized nickname: {repr(normalized_name)}")

    except Exception as exc:
        logger.log("Program error")
        logger.log(f"Error type: {type(exc).__name__}")
        logger.log(f"Error detail: {repr(exc)}")


if __name__ == "__main__":
    main()
