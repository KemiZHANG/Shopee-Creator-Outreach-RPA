"""Run the Shopee creator BD automation with nickname deduplication."""

from __future__ import annotations

import time
from pathlib import Path

from automation_utils import (
    DB_PATH,
    IMAGES_DIR,
    RunLogger,
    add_creator,
    ask_float,
    ask_int,
    ask_text,
    ask_yes_no,
    click_image_or_point,
    click_point,
    clear_sent_creators,
    count_creators,
    db_connect,
    ensure_dirs,
    get_point,
    get_pyautogui,
    get_pyperclip,
    get_pytesseract,
    has_creator,
    is_chat_window_open,
    is_image_match_enabled,
    locate_private_chat_button_by_ocr,
    load_config,
    read_creator_name,
    validate_creator_name,
)


PRIVATE_CHAT_IMAGE = IMAGES_DIR / "buttons" / "private_chat_icon.png"
UPLOAD_IMAGE_IMAGE = IMAGES_DIR / "buttons" / "upload_image_btn.png"
CHAT_SEND_IMAGE = IMAGES_DIR / "buttons" / "chat_send_btn.png"
CREATOR_CLOSE_IMAGE = IMAGES_DIR / "dialogs" / "creator_page_close_btn.png"


def safe_close_creator_page(pyautogui, config: dict, confidence: float, logger: RunLogger) -> None:
    """Close the creator page and return to the list."""
    click_image_or_point(
        pyautogui=pyautogui,
        image_path=CREATOR_CLOSE_IMAGE,
        fallback_point=get_point(config, "creator_page_close"),
        confidence=confidence,
        label="creator page close",
        logger=logger,
        use_image_match=is_image_match_enabled(config),
    )
    time.sleep(config["timings"]["after_close_click_seconds"])


def scroll_to_next_creator(pyautogui, config: dict, scroll_amount: int, logger: RunLogger) -> None:
    """Move to the configured list area and scroll to the next creator."""
    roll_x, roll_y = get_point(config, "roll_position")
    logger.log(f"Moving to scroll position at ({roll_x}, {roll_y})")
    pyautogui.moveTo(roll_x, roll_y, duration=0.25)
    logger.log(f"Scrolling creator list by {scroll_amount}")
    pyautogui.scroll(scroll_amount)
    time.sleep(config["timings"]["after_scroll_seconds"])


def send_message_and_image(
    pyautogui,
    pyperclip,
    config: dict,
    confidence: float,
    logger: RunLogger,
    message_text: str,
) -> None:
    """Run the chat flow: upload one image, paste text, and click send."""
    click_image_or_point(
        pyautogui=pyautogui,
        image_path=UPLOAD_IMAGE_IMAGE,
        fallback_point=get_point(config, "upload_image_btn"),
        confidence=confidence,
        label="upload image button",
        logger=logger,
        use_image_match=is_image_match_enabled(config),
    )
    time.sleep(config["timings"]["after_upload_click_seconds"])

    click_point(pyautogui, get_point(config, "file_first_image"), "file first image", logger)
    time.sleep(0.3)
    click_point(pyautogui, get_point(config, "file_open_btn"), "file open button", logger)
    time.sleep(config["timings"]["after_file_open_seconds"])

    click_point(pyautogui, get_point(config, "chat_input"), "chat input", logger)
    time.sleep(config["timings"]["after_chat_input_click_seconds"])

    pyperclip.copy(message_text)
    logger.log("Pasting chat message")
    pyautogui.hotkey("ctrl", "v")
    time.sleep(config["timings"]["after_paste_seconds"])

    click_image_or_point(
        pyautogui=pyautogui,
        image_path=CHAT_SEND_IMAGE,
        fallback_point=get_point(config, "chat_send_btn"),
        confidence=confidence,
        label="chat send button",
        logger=logger,
        use_image_match=is_image_match_enabled(config),
    )
    time.sleep(config["timings"]["after_send_click_seconds"])


def open_private_chat_with_confirmation(
    pyautogui,
    pytesseract,
    config: dict,
    confidence: float,
    logger: RunLogger,
) -> bool:
    """Open the private chat and verify that the chat window is ready."""
    fixed_x, fixed_y = get_point(config, "private_chat_click")
    offset_step_y = int(config["ocr"]["private_chat_offset_step_y"])
    offset_attempts_each_direction = int(config["ocr"]["private_chat_offset_attempts_each_direction"])
    allow_fixed_fallback = bool(config["ocr"].get("private_chat_allow_fixed_fallback", False))

    click_candidates: list[tuple[str, tuple[int, int] | None]] = []

    ocr_point = locate_private_chat_button_by_ocr(
        pyautogui=pyautogui,
        pytesseract=pytesseract,
        config=config,
        logger=logger,
        creator_index=0,
    )
    if ocr_point is not None:
        click_candidates.append(("private chat OCR point", ocr_point))

    if allow_fixed_fallback:
        click_candidates.append(("private chat fixed point", (fixed_x, fixed_y)))

        for step_index in range(1, offset_attempts_each_direction + 1):
            click_candidates.append(
                (
                    f"private chat upper offset {step_index}",
                    (fixed_x, fixed_y - offset_step_y * step_index),
                )
            )

        for step_index in range(1, offset_attempts_each_direction + 1):
            click_candidates.append(
                (
                    f"private chat lower offset {step_index}",
                    (fixed_x, fixed_y + offset_step_y * step_index),
                )
            )

    if not click_candidates:
        logger.log("Private chat OCR did not find the target button; fixed fallback is disabled")
        return False

    for attempt_index, (label, point) in enumerate(click_candidates, start=1):
        logger.log(f"Opening private chat attempt {attempt_index}: {label}")
        click_point(pyautogui, point, label, logger)
        time.sleep(config["timings"]["after_private_chat_click_seconds"])

        if is_chat_window_open(pyautogui, pytesseract, config, logger):
            logger.log("Chat window confirmation succeeded")
            return True

        logger.log("Chat window confirmation failed")
        if attempt_index < len(click_candidates):
            time.sleep(config["timings"]["after_private_chat_retry_seconds"])

    return False


def process_single_creator(
    creator_index: int,
    pyautogui,
    pyperclip,
    pytesseract,
    connection,
    config: dict,
    confidence: float,
    logger: RunLogger,
    message_text: str,
) -> str:
    """Process one creator and return the outcome status."""
    logger.log(f"Starting creator {creator_index}")

    click_point(pyautogui, get_point(config, "creator_click"), "creator click", logger)
    time.sleep(config["timings"]["after_creator_click_seconds"])

    raw_name, normalized_name, capture_path = read_creator_name(
        pyautogui=pyautogui,
        pytesseract=pytesseract,
        config=config,
        logger=logger,
        creator_index=creator_index,
    )
    logger.log(f"Nickname screenshot saved to: {capture_path}")

    if not normalized_name:
        logger.log("Creator nickname OCR is empty, skipping this creator to avoid duplicate risk")
        safe_close_creator_page(pyautogui, config, confidence, logger)
        return "ocr_empty"

    is_valid_name, invalid_reason = validate_creator_name(normalized_name, config)
    if not is_valid_name:
        logger.log(
            f"Creator nickname OCR failed quality check, skipping send: {invalid_reason}"
        )
        logger.log(f"Rejected raw creator name: {repr(raw_name)}")
        logger.log(f"Rejected normalized creator name: {repr(normalized_name)}")
        safe_close_creator_page(pyautogui, config, confidence, logger)
        return "ocr_invalid"

    if has_creator(connection, normalized_name):
        logger.log(f"Duplicate creator detected, skipping send: {raw_name or normalized_name}")
        safe_close_creator_page(pyautogui, config, confidence, logger)
        return "duplicate"

    if not open_private_chat_with_confirmation(
        pyautogui=pyautogui,
        pytesseract=pytesseract,
        config=config,
        confidence=confidence,
        logger=logger,
    ):
        logger.log("Private chat could not be opened after double confirmation, skipping creator")
        safe_close_creator_page(pyautogui, config, confidence, logger)
        return "chat_not_open"

    send_message_and_image(
        pyautogui=pyautogui,
        pyperclip=pyperclip,
        config=config,
        confidence=confidence,
        logger=logger,
        message_text=message_text,
    )

    add_creator(connection, raw_name or normalized_name, normalized_name)
    logger.log(f"Recorded creator into database: {raw_name or normalized_name}")

    safe_close_creator_page(pyautogui, config, confidence, logger)
    return "sent"


def check_required_files() -> None:
    """Ensure the required template images exist."""
    return


def main() -> None:
    """Run the creator BD automation."""
    ensure_dirs()
    logger = RunLogger()

    try:
        check_required_files()
        config = load_config()

        clear_database = ask_yes_no("Clear the sent creator database before start?", default=False)
        total_creators = ask_int("Enter total creators to process (default 10): ", 10)
        scroll_amount = ask_int("Enter scroll amount after each creator (default -132): ", -132)
        message_text = ask_text("Enter the message text to send: ")
        start_delay = ask_float(
            "Enter start delay seconds (default 3): ",
            config["timings"]["default_start_delay_seconds"],
        )
        if is_image_match_enabled(config):
            confidence = ask_float(
                "Enter image match confidence (default 0.8): ",
                config["image_match"]["confidence"],
            )
        else:
            confidence = config["image_match"]["confidence"]

        if total_creators < 1:
            raise ValueError("Total creators must be 1 or greater.")

        connection = db_connect()
        if clear_database:
            clear_sent_creators(connection)
            logger.log("Sent creator database has been cleared")

        logger.log(f"Current database path: {DB_PATH}")
        logger.log(f"Current sent creator count: {count_creators(connection)}")

        pyautogui = get_pyautogui()
        pyperclip = get_pyperclip()
        pytesseract = get_pytesseract(config)

        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.2

        logger.log("Run summary")
        logger.log(f"Total creators: {total_creators}")
        logger.log(f"Scroll amount: {scroll_amount}")
        logger.log(f"Image match enabled: {is_image_match_enabled(config)}")
        logger.log(f"Image confidence: {confidence}")
        logger.log(f"Start delay: {start_delay}")
        logger.log("Before the countdown ends, please:")
        logger.log("1. Open the Shopee creator list page")
        logger.log("2. Ensure the first target creator is aligned with your recorded click point")
        logger.log("3. Ensure the file picker is already fixed to the correct folder when it opens")

        time.sleep(start_delay)

        sent_count = 0
        duplicate_count = 0
        skipped_count = 0

        for creator_index in range(1, total_creators + 1):
            try:
                status = process_single_creator(
                    creator_index=creator_index,
                    pyautogui=pyautogui,
                    pyperclip=pyperclip,
                    pytesseract=pytesseract,
                    connection=connection,
                    config=config,
                    confidence=confidence,
                    logger=logger,
                    message_text=message_text,
                )
            except Exception as exc:
                logger.log(f"Creator {creator_index} failed with an exception")
                logger.log(f"Error type: {type(exc).__name__}")
                logger.log(f"Error detail: {repr(exc)}")
                safe_close_creator_page(pyautogui, config, confidence, logger)
                status = "error"

            if status == "sent":
                sent_count += 1
            elif status == "duplicate":
                duplicate_count += 1
            else:
                skipped_count += 1

            if creator_index < total_creators:
                scroll_to_next_creator(pyautogui, config, scroll_amount, logger)

        logger.log("Run finished")
        logger.log(f"Sent count: {sent_count}")
        logger.log(f"Duplicate count: {duplicate_count}")
        logger.log(f"Skipped count: {skipped_count}")
        logger.log(f"Final sent creator count in database: {count_creators(connection)}")
        connection.close()

    except Exception as exc:
        logger.log("Program error")
        logger.log(f"Error type: {type(exc).__name__}")
        logger.log(f"Error detail: {repr(exc)}")


if __name__ == "__main__":
    main()
