"""Shared helpers for the Shopee creator BD automation project."""

from __future__ import annotations

import json
import re
import sqlite3
import sys
import time
import unicodedata
from datetime import datetime
from pathlib import Path


if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = BASE_DIR / "images"
LOGS_DIR = BASE_DIR / "logs"
CONFIG_PATH = CONFIG_DIR / "automation_config.json"
DB_PATH = DATA_DIR / "sent_creators.db"


class RunLogger:
    """Simple logger that writes to both terminal and a log file."""

    def __init__(self) -> None:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        self.path = LOGS_DIR / f"run_{timestamp_str()}.log"

    def log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {message}"
        print(line)
        with self.path.open("a", encoding="utf-8") as file:
            file.write(line + "\n")


def ensure_dirs() -> None:
    """Ensure the project directories exist."""
    required_dirs = [
        CONFIG_DIR,
        DATA_DIR,
        IMAGES_DIR,
        IMAGES_DIR / "anchors",
        IMAGES_DIR / "buttons",
        IMAGES_DIR / "dialogs",
        IMAGES_DIR / "reference",
        LOGS_DIR,
        BASE_DIR / "scripts",
    ]

    for directory in required_dirs:
        directory.mkdir(parents=True, exist_ok=True)


def timestamp_str() -> str:
    """Return a timestamp safe for filenames."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def load_config() -> dict:
    """Load JSON config from config/automation_config.json."""
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_pyautogui():
    """Import pyautogui with a helpful error message."""
    try:
        import pyautogui  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency: pyautogui. Please install project dependencies first:\n"
            f"pip install -r \"{BASE_DIR / 'requirements.txt'}\""
        ) from exc

    return pyautogui


def get_pyperclip():
    """Import pyperclip with a helpful error message."""
    try:
        import pyperclip  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency: pyperclip. Please install project dependencies first:\n"
            f"pip install -r \"{BASE_DIR / 'requirements.txt'}\""
        ) from exc

    return pyperclip


def get_pytesseract(config: dict):
    """Import pytesseract and configure the tesseract executable path."""
    try:
        import pytesseract  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency: pytesseract. Please install project dependencies first:\n"
            f"pip install -r \"{BASE_DIR / 'requirements.txt'}\""
        ) from exc

    tesseract_path = config["ocr"]["tesseract_path"]
    if Path(tesseract_path).exists():
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
    else:
        raise FileNotFoundError(f"Tesseract executable not found: {tesseract_path}")

    return pytesseract


def ask_int(prompt: str, default: int) -> int:
    """Read an integer with a default value."""
    raw_value = input(prompt).strip()
    return int(raw_value) if raw_value else default


def ask_float(prompt: str, default: float) -> float:
    """Read a float with a default value."""
    raw_value = input(prompt).strip()
    return float(raw_value) if raw_value else default


def ask_yes_no(prompt: str, default: bool = False) -> bool:
    """Read a yes/no answer with a default value."""
    default_text = "y" if default else "n"
    raw_value = input(f"{prompt} (y/n, default {default_text}): ").strip().lower()
    if not raw_value:
        return default
    if raw_value in {"y", "yes"}:
        return True
    if raw_value in {"n", "no"}:
        return False
    raise ValueError("Please enter y or n.")


def ask_text(prompt: str) -> str:
    """Read required non-empty text."""
    value = input(prompt).strip()
    if not value:
        raise ValueError("This value cannot be empty.")
    return value


def get_point(config: dict, point_name: str) -> tuple[int, int]:
    """Return a configured point as (x, y)."""
    point = config["points"][point_name]
    return int(point["x"]), int(point["y"])


def get_region(config: dict, region_name: str) -> tuple[int, int, int, int]:
    """Return a configured region as (left, top, width, height)."""
    region = config["regions"][region_name]
    return (
        int(region["left"]),
        int(region["top"]),
        int(region["width"]),
        int(region["height"]),
    )


def is_image_match_enabled(config: dict) -> bool:
    """Return whether template image matching is enabled."""
    return bool(config.get("image_match", {}).get("enabled", False))


def click_point(pyautogui, point: tuple[int, int], label: str, logger: RunLogger, duration: float = 0.25) -> None:
    """Move to a fixed point and click once."""
    x, y = point
    logger.log(f"Clicking {label} at ({x}, {y})")
    pyautogui.moveTo(x, y, duration=duration)
    pyautogui.click(button="left")


def locate_image(pyautogui, image_path: Path, confidence: float):
    """Locate an image on screen and return the match box or None."""
    if not image_path.exists():
        return None

    try:
        return pyautogui.locateOnScreen(str(image_path), confidence=confidence)
    except Exception as exc:
        if type(exc).__name__ == "ImageNotFoundException":
            return None
        if isinstance(exc, OSError):
            return None
        raise


def click_image_or_point(
    pyautogui,
    image_path: Path,
    fallback_point: tuple[int, int],
    confidence: float,
    label: str,
    logger: RunLogger,
    use_image_match: bool = False,
) -> None:
    """Try clicking an image first, then fall back to a fixed point."""
    match = None
    if use_image_match:
        try:
            match = locate_image(pyautogui, image_path, confidence)
        except Exception as exc:
            logger.log(f"Image match failed for {label}: {repr(exc)}")
            match = None

    if match is not None:
        center_x, center_y = pyautogui.center(match)
        logger.log(f"Clicking {label} by image match at ({center_x}, {center_y})")
        pyautogui.moveTo(center_x, center_y, duration=0.25)
        pyautogui.click(button="left")
        return

    if use_image_match:
        logger.log(f"Image not available for {label}, using fallback point")
    click_point(pyautogui, fallback_point, label, logger)


def capture_region(pyautogui, region: tuple[int, int, int, int]):
    """Capture a screen region and return a PIL image."""
    return pyautogui.screenshot(region=region)


def build_centered_region(
    center_point: tuple[int, int],
    width: int,
    height: int,
    screen_width: int,
    screen_height: int,
) -> tuple[int, int, int, int]:
    """Build a screen-safe region centered around a point."""
    center_x, center_y = center_point
    left = max(0, center_x - width // 2)
    top = max(0, center_y - height // 2)

    if left + width > screen_width:
        left = max(0, screen_width - width)
    if top + height > screen_height:
        top = max(0, screen_height - height)

    return left, top, width, height


def build_ratio_region(
    config: dict,
    screen_width: int,
    screen_height: int,
) -> tuple[int, int, int, int]:
    """Build the private chat OCR search area from screen ratios."""
    ocr_config = config["ocr"]
    left = int(screen_width * float(ocr_config["private_chat_search_left_ratio"]))
    top = int(screen_height * float(ocr_config["private_chat_search_top_ratio"]))
    width = int(screen_width * float(ocr_config["private_chat_search_width_ratio"]))
    height = int(screen_height * float(ocr_config["private_chat_search_height_ratio"]))

    left = max(0, min(left, screen_width - 1))
    top = max(0, min(top, screen_height - 1))
    width = max(1, min(width, screen_width - left))
    height = max(1, min(height, screen_height - top))

    return left, top, width, height


def normalize_creator_name(text: str) -> str:
    """Normalize OCR text into a stable deduplication key."""
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r"\s+", "", text)
    text = text.strip("._-|[](){}<>:;,\"")
    text = text.replace("'", "")
    return text.lower()


def validate_creator_name(normalized_name: str, config: dict) -> tuple[bool, str]:
    """Validate whether an OCR creator name is safe enough to use."""
    if not normalized_name:
        return False, "empty"

    ocr_config = config["ocr"]
    min_length = int(ocr_config.get("creator_name_min_length", 4))
    min_alnum_ratio = float(ocr_config.get("creator_name_min_alnum_ratio", 0.65))
    min_ascii_ratio = float(ocr_config.get("creator_name_min_ascii_ratio", 0.85))
    allowed_pattern = ocr_config.get("creator_name_allowed_pattern", r"^[a-zA-Z0-9._-]+$")

    if len(normalized_name) < min_length:
        return False, f"too short: {len(normalized_name)} < {min_length}"

    if not re.match(allowed_pattern, normalized_name):
        return False, "contains unsupported characters"

    total_chars = max(len(normalized_name), 1)
    ascii_chars = sum(1 for char in normalized_name if ord(char) < 128)
    alnum_chars = sum(1 for char in normalized_name if char.isalnum())
    ascii_ratio = ascii_chars / total_chars
    alnum_ratio = alnum_chars / total_chars

    if ascii_ratio < min_ascii_ratio:
        return False, f"ascii ratio too low: {ascii_ratio:.2f} < {min_ascii_ratio:.2f}"

    if alnum_ratio < min_alnum_ratio:
        return False, f"alnum ratio too low: {alnum_ratio:.2f} < {min_alnum_ratio:.2f}"

    return True, "ok"


def normalize_ocr_word(text: str) -> str:
    """Normalize OCR word tokens for phrase matching."""
    text = unicodedata.normalize("NFKC", text)
    text = text.lower()
    return re.sub(r"[^a-z0-9]+", "", text)


def contains_chat_with_affiliate(normalized_text: str) -> bool:
    """Return whether normalized OCR text contains the target chat phrase."""
    return (
        "chat" in normalized_text
        and "with" in normalized_text
        and "affiliate" in normalized_text
    )


def image_has_meaningful_content(image) -> bool:
    """Return whether the image appears to contain meaningful UI content."""
    from PIL import ImageOps, ImageStat  # type: ignore

    grayscale = ImageOps.grayscale(image)
    stat = ImageStat.Stat(grayscale)
    mean_value = stat.mean[0]
    stddev_value = stat.stddev[0]

    pixels = list(grayscale.getdata())
    dark_pixels = sum(1 for value in pixels if value < 240)
    dark_ratio = dark_pixels / max(len(pixels), 1)

    return stddev_value >= 6 or dark_ratio >= 0.02 or mean_value < 248


def extract_text_from_image(pytesseract, image, lang: str, psm: int) -> tuple[str, str]:
    """Run OCR on several processed variants and return the best text."""
    from PIL import ImageOps  # type: ignore

    enlarged = image.resize((image.width * 3, image.height * 3))
    grayscale = ImageOps.grayscale(enlarged)
    processed = ImageOps.autocontrast(grayscale)
    binary = processed.point(lambda value: 255 if value > 160 else 0)

    ocr_config = f"--psm {psm}"

    attempts = [
        pytesseract.image_to_string(image, lang=lang, config=ocr_config),
        pytesseract.image_to_string(processed, lang=lang, config=ocr_config),
        pytesseract.image_to_string(binary, lang=lang, config=ocr_config),
    ]

    best_text = ""
    best_normalized = ""

    for attempt_text in attempts:
        cleaned_text = attempt_text.strip()
        normalized = normalize_creator_name(cleaned_text)
        if len(normalized) > len(best_normalized):
            best_text = cleaned_text
            best_normalized = normalized

    return best_text, best_normalized


def locate_private_chat_button_by_ocr(
    pyautogui,
    pytesseract,
    config: dict,
    logger: RunLogger,
    creator_index: int,
) -> tuple[int, int] | None:
    """Try to find the 'Chat with Affiliate' button in the action area."""
    from PIL import ImageOps  # type: ignore
    from pytesseract import Output  # type: ignore

    screen_width, screen_height = pyautogui.size()
    search_mode = config["ocr"].get("private_chat_search_mode", "top_right_action_area")
    if search_mode == "centered":
        search_region = build_centered_region(
            center_point=get_point(config, "private_chat_click"),
            width=int(config["ocr"].get("private_chat_search_width", 520)),
            height=int(config["ocr"].get("private_chat_search_height", 180)),
            screen_width=screen_width,
            screen_height=screen_height,
        )
    else:
        search_region = build_ratio_region(config, screen_width, screen_height)

    region_left, region_top, region_width, region_height = search_region
    capture = capture_region(pyautogui, search_region)
    capture_path = LOGS_DIR / f"private_chat_search_{creator_index}_{timestamp_str()}.png"
    capture.save(capture_path)
    logger.log(f"Saved private chat OCR search image to: {capture_path}")

    scale = int(config["ocr"]["private_chat_button_scale"])
    lang = config["ocr"]["private_chat_button_lang"]
    psm = int(config["ocr"]["private_chat_button_psm"])

    enlarged = capture.resize((region_width * scale, region_height * scale))
    processed = ImageOps.autocontrast(ImageOps.grayscale(enlarged))
    data = pytesseract.image_to_data(
        processed,
        lang=lang,
        config=f"--psm {psm}",
        output_type=Output.DICT,
    )

    tokens: list[dict] = []
    for index, raw_text in enumerate(data.get("text", [])):
        normalized = normalize_ocr_word(raw_text)
        if not normalized:
            continue

        tokens.append(
            {
                "text": raw_text.strip(),
                "normalized": normalized,
                "line_key": (
                    int(data["block_num"][index]),
                    int(data["par_num"][index]),
                    int(data["line_num"][index]),
                ),
                "left": int(data["left"][index]),
                "top": int(data["top"][index]),
                "width": int(data["width"][index]),
                "height": int(data["height"][index]),
            }
        )

    logger.log(
        "Private chat OCR tokens: "
        + ", ".join(token["normalized"] for token in tokens[:12])
    )

    lines: dict[tuple[int, int, int], list[dict]] = {}
    for token in tokens:
        lines.setdefault(token["line_key"], []).append(token)

    for line_tokens in lines.values():
        line_text = "".join(token["normalized"] for token in line_tokens)
        if not contains_chat_with_affiliate(line_text):
            continue

        target_tokens = [
            token
            for token in line_tokens
            if token["normalized"].startswith("chat")
            or token["normalized"].startswith("with")
            or token["normalized"].startswith("affiliate")
            or token["normalized"].startswith("affiliat")
        ]
        matched = target_tokens or line_tokens

        left = min(token["left"] for token in matched)
        top = min(token["top"] for token in matched)
        right = max(token["left"] + token["width"] for token in matched)
        bottom = max(token["top"] + token["height"] for token in matched)

        center_x = region_left + int(((left + right) / 2) / scale)
        center_y = region_top + int(((top + bottom) / 2) / scale)

        logger.log(
            f"Found 'Chat with Affiliate' by OCR line near ({center_x}, {center_y})"
        )
        return center_x, center_y

    target_words = ("chat", "with", "affiliate")

    for start_index in range(len(tokens)):
        if not tokens[start_index]["normalized"].startswith(target_words[0]):
            continue

        end_index = start_index
        matched = [tokens[start_index]]
        next_word_index = 1

        for cursor in range(start_index + 1, min(start_index + 5, len(tokens))):
            candidate = tokens[cursor]["normalized"]
            if next_word_index == 1 and candidate.startswith(target_words[1]):
                matched.append(tokens[cursor])
                end_index = cursor
                next_word_index = 2
                continue
            if next_word_index == 2 and (
                candidate.startswith(target_words[2]) or candidate.startswith("affiliat")
            ):
                matched.append(tokens[cursor])
                end_index = cursor
                next_word_index = 3
                break

        if next_word_index != 3:
            continue

        left = min(token["left"] for token in matched)
        top = min(token["top"] for token in matched)
        right = max(token["left"] + token["width"] for token in matched)
        bottom = max(token["top"] + token["height"] for token in matched)

        center_x = region_left + int(((left + right) / 2) / scale)
        center_y = region_top + int(((top + bottom) / 2) / scale)

        logger.log(
            f"Found 'Chat with Affiliate' by OCR near ({center_x}, {center_y})"
        )
        return center_x, center_y

    logger.log("Could not locate 'Chat with Affiliate' by OCR")
    return None


def read_creator_name(pyautogui, pytesseract, config: dict, logger: RunLogger, creator_index: int) -> tuple[str, str, Path]:
    """Capture the nickname region and read the creator name via OCR."""
    region = get_region(config, "creator_name")
    lang = config["ocr"]["lang"]
    psm = int(config["ocr"]["psm"])

    best_text = ""
    best_normalized = ""
    best_capture_path = LOGS_DIR / f"creator_name_{creator_index}_{timestamp_str()}.png"

    for attempt in range(1, 3):
        raw_image = capture_region(pyautogui, region)
        capture_path = LOGS_DIR / f"creator_name_{creator_index}_attempt{attempt}_{timestamp_str()}.png"
        raw_image.save(capture_path)
        best_capture_path = capture_path

        if not image_has_meaningful_content(raw_image):
            logger.log(f"Creator name region looks blank on attempt {attempt}")
            if attempt < 2:
                time.sleep(config["timings"]["after_creator_retry_seconds"])
                continue
            logger.log("Creator name region still looks blank after double confirmation")
            break

        attempt_text, attempt_normalized = extract_text_from_image(
            pytesseract=pytesseract,
            image=raw_image,
            lang=lang,
            psm=psm,
        )
        logger.log(f"Creator OCR attempt {attempt} raw: {repr(attempt_text)}")
        logger.log(f"Creator OCR attempt {attempt} normalized: {repr(attempt_normalized)}")

        if len(attempt_normalized) > len(best_normalized):
            best_text = attempt_text
            best_normalized = attempt_normalized
            best_capture_path = capture_path

        if best_normalized:
            break

        if attempt < 2:
            time.sleep(config["timings"]["after_creator_retry_seconds"])

    logger.log(f"OCR raw creator name: {repr(best_text)}")
    logger.log(f"OCR normalized creator name: {repr(best_normalized)}")

    return best_text, best_normalized, best_capture_path


def is_chat_window_open(pyautogui, pytesseract, config: dict, logger: RunLogger) -> bool:
    """Check whether the chat window is open by OCRing the placeholder text."""
    region = get_region(config, "chat_message_hint")
    image = capture_region(pyautogui, region)
    lang = config["ocr"]["chat_hint_lang"]
    psm = int(config["ocr"]["chat_hint_psm"])
    raw_text, normalized_text = extract_text_from_image(
        pytesseract=pytesseract,
        image=image,
        lang=lang,
        psm=psm,
    )

    logger.log(f"Chat hint OCR raw: {repr(raw_text)}")
    logger.log(f"Chat hint OCR normalized: {repr(normalized_text)}")

    expected_tokens = [
        "typeamessagehere",
        "typeamessage",
        "messagehere",
        "message",
    ]
    return any(token in normalized_text for token in expected_tokens)


def db_connect() -> sqlite3.Connection:
    """Open the SQLite database and ensure the schema exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS sent_creators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_name TEXT NOT NULL,
            normalized_name TEXT NOT NULL UNIQUE,
            sent_at TEXT NOT NULL
        )
        """
    )
    connection.commit()
    return connection


def clear_sent_creators(connection: sqlite3.Connection) -> None:
    """Remove all sent creator records."""
    connection.execute("DELETE FROM sent_creators")
    connection.commit()


def has_creator(connection: sqlite3.Connection, normalized_name: str) -> bool:
    """Return True when the normalized creator name already exists."""
    cursor = connection.execute(
        "SELECT 1 FROM sent_creators WHERE normalized_name = ? LIMIT 1",
        (normalized_name,),
    )
    return cursor.fetchone() is not None


def add_creator(connection: sqlite3.Connection, raw_name: str, normalized_name: str) -> None:
    """Insert a newly contacted creator."""
    connection.execute(
        "INSERT INTO sent_creators (raw_name, normalized_name, sent_at) VALUES (?, ?, ?)",
        (raw_name, normalized_name, datetime.now().isoformat(timespec="seconds")),
    )
    connection.commit()


def count_creators(connection: sqlite3.Connection) -> int:
    """Return the number of creators currently stored in the database."""
    cursor = connection.execute("SELECT COUNT(*) FROM sent_creators")
    row = cursor.fetchone()
    return int(row[0]) if row else 0


def list_creators(connection: sqlite3.Connection) -> list[tuple[int, str, str, str]]:
    """Return stored creators ordered by insertion time."""
    cursor = connection.execute(
        """
        SELECT id, raw_name, normalized_name, sent_at
        FROM sent_creators
        ORDER BY id
        """
    )
    return [
        (int(row[0]), str(row[1]), str(row[2]), str(row[3]))
        for row in cursor.fetchall()
    ]
