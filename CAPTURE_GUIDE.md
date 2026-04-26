# Capture Guide

This guide explains how to capture the local coordinates, OCR regions, and template screenshots required by the Shopee Creator Outreach RPA workflow.

## Open the Project

Run the commands from the project root:

```powershell
cd "path\to\Shopee RPA"
```

## 1. Record Single-Point Coordinates

```powershell
python scripts\record_mouse_position.py
```

This script uses:

- `F8` to record the current mouse position
- `ESC` to exit

Use this for fixed click points such as:

- creator list click point
- private chat click point
- upload image button point
- first image point in the file dialog
- open button point in the file dialog
- chat input point
- send button point
- creator page close point
- creator list scroll position

## 2. Record OCR Region

```powershell
python scripts\record_region.py
```

Use this for regions such as:

- creator nickname area
- chat message placeholder area

## 3. Test Scroll Distance

```powershell
python scripts\scroll_test.py
```

This script lets you input:

- scroll amount
- scroll count
- wait seconds
- start delay

Use it to tune the scroll amount before running the full workflow.

## 4. Test Nickname OCR

```powershell
python scripts\name_ocr_test.py
```

Run this before the full automation to confirm that the nickname OCR region reads the expected creator name.

## 5. Run the Full Automation

```powershell
python scripts\run_creator_bd_rpa.py
```

## Coordinate Keys

Update `config/automation_config.json` with these values:

```text
creator_click
private_chat_click
upload_image_btn
file_first_image
file_open_btn
chat_input
chat_send_btn
creator_page_close
roll_position
```

Each point uses:

```json
{
  "x": 100,
  "y": 100
}
```

## OCR Region Keys

Update these regions:

```text
creator_name
chat_message_hint
```

Each region uses:

```json
{
  "left": 100,
  "top": 100,
  "width": 200,
  "height": 40
}
```

## Template Image Folders

Place local template screenshots into these folders:

- `images/buttons`
- `images/dialogs`
- `images/anchors`
- `images/reference`

Recommended templates:

- `images/buttons/private_chat_icon.png`
- `images/buttons/upload_image_btn.png`
- `images/buttons/chat_send_btn.png`
- `images/dialogs/creator_page_close_btn.png`
- `images/anchors/creator_page_loaded_anchor.png`
- `images/anchors/chat_window_loaded_anchor.png`

## Screenshot Tips

- Keep the browser zoom fixed while capturing and running.
- Keep Windows display scaling fixed while capturing and running.
- Capture under the same theme and page style used for automation.
- Prefer small, high-contrast UI areas.
- Avoid screenshots that include account details, creator data, or private business information.
- Save templates as `.png`.

## Privacy Note

Template screenshots, OCR debug screenshots, logs, local configuration, and SQLite databases are ignored by Git. They should remain local because they may contain creator data, platform UI, account context, or machine-specific coordinates.
