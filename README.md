# Shopee Creator Outreach RPA

<p align="center">
  <a href="#中文">中文</a>
  ·
  <a href="#english">English</a>
</p>

---

## 中文

一个基于 Python 的 Windows 桌面 RPA 项目，用于演示 Shopee 创作者运营场景中的半自动触达流程。项目通过固定坐标、OCR、SQLite 去重、模板图辅助识别、日志记录和调试截图，把重复性的创作者 BD 操作封装成本地可配置的自动化工具。

> 说明：本仓库是作品集展示版，不包含真实创作者数据、运行日志、OCR 调试截图、模板截图、数据库或本机私有配置。使用者需要遵守目标平台规则，并仅在获得授权的业务场景中使用自动化能力。

### 项目亮点

- 使用 `pyautogui` 完成 Windows 桌面级 RPA 操作，包括点击、滚动、文件选择、文本粘贴和发送。
- 使用 Tesseract OCR 读取创作者昵称，并将昵称归一化成稳定的去重 key。
- 使用 SQLite 记录已触达创作者，避免重复发送。
- 支持通过 OCR 搜索并定位 `Chat with Affiliate` 私聊入口，降低固定坐标失效风险。
- 支持聊天窗口 OCR 二次确认，避免在页面未准备好时继续执行。
- 使用日志和 OCR 调试截图记录关键过程，便于排查识别区域、滚动距离和页面状态问题。
- 提供坐标录制、OCR 区域录制、滚动测试、昵称 OCR 测试等辅助脚本。

### 技术栈

- Python
- PyAutoGUI
- Tesseract OCR / pytesseract
- Pillow
- OpenCV
- SQLite
- pyperclip

### 项目结构

```text
.
├── CAPTURE_GUIDE.md                  # 坐标和模板截图采集说明
├── requirements.txt
├── config/
│   └── automation_config.example.json # 可公开的示例配置
├── data/                              # 本地数据库目录，公开版仅保留占位文件
├── images/                            # 本地模板图目录，公开版不包含实际截图
│   ├── anchors/
│   ├── buttons/
│   ├── dialogs/
│   └── reference/
├── logs/                              # 运行日志与调试截图目录，公开版仅保留占位文件
└── scripts/
    ├── automation_utils.py            # 共享工具：OCR、点击、日志、数据库
    ├── run_creator_bd_rpa.py          # 主流程入口
    ├── list_sent_creators.py          # 查看已触达创作者数据库
    ├── name_ocr_test.py               # 昵称 OCR 测试
    ├── record_mouse_position.py       # 鼠标坐标录制
    ├── record_region.py               # OCR 区域录制
    └── scroll_test.py                 # 滚动参数测试
```

### 工作流概览

1. 点击列表中的当前创作者。
2. 截取昵称区域并执行 OCR。
3. 对昵称进行归一化和质量校验。
4. 查询 SQLite 数据库，已触达则跳过。
5. 通过 OCR 或配置坐标打开私聊入口。
6. 上传图片，粘贴消息文本，并点击发送。
7. 成功后写入已触达创作者数据库。
8. 关闭创作者页面，滚动到下一位创作者。

### 稳定性设计

- 昵称 OCR 会进行双次确认，避免空白区域导致误发。
- 创作者昵称会经过长度、字符比例和格式校验。
- 私聊按钮可通过 OCR 搜索，而不是完全依赖固定坐标。
- 聊天窗口会通过输入提示 OCR 确认是否打开成功。
- 每次运行会生成日志，OCR 关键截图会保存到 `logs/` 便于调试。
- 坐标、OCR 区域、延迟时间和识别阈值都通过配置文件管理。

### 本地运行

安装依赖：

```powershell
pip install -r requirements.txt
```

准备配置：

```powershell
Copy-Item config\automation_config.example.json config\automation_config.json
```

根据自己的屏幕分辨率、浏览器缩放比例和页面布局，更新 `config/automation_config.json` 中的坐标、OCR 区域、Tesseract 路径和延迟参数。

运行主流程：

```powershell
python scripts\run_creator_bd_rpa.py
```

查看已触达创作者：

```powershell
python scripts\list_sent_creators.py
```

测试昵称 OCR：

```powershell
python scripts\name_ocr_test.py
```

### 数据与隐私

以下内容不会提交到公开仓库：

- `config/automation_config.json`
- `data/*.db`
- `logs/` 下的运行日志和 OCR 调试截图
- `images/**/*.png` 本地模板截图
- `.claude/`
- `__pycache__/`

这样可以避免泄露真实创作者昵称、页面截图、账号环境、本机路径和运行数据。

### 适合作品集展示的能力点

这个项目可以体现：

- 将真实运营流程抽象成 RPA 状态流程的能力
- 使用 OCR 解决非结构化页面信息读取问题
- 通过 SQLite 管理轻量业务状态和去重逻辑
- 为不稳定网页界面设计校验、跳过和调试机制
- 编写辅助工具提升本地自动化调参效率

---

## English

A Python-based Windows desktop RPA project that demonstrates a semi-automated creator outreach workflow for Shopee creator operations. The project combines fixed coordinates, OCR, SQLite deduplication, optional template image matching, logging, and debug screenshots to turn a repetitive creator BD process into a configurable local automation tool.

> Note: This repository is a portfolio-friendly version. It does not include real creator data, runtime logs, OCR debug screenshots, template screenshots, databases, or private local configuration. Users should follow the target platform's rules and only use automation in authorized business scenarios.

### Highlights

- Uses `pyautogui` for Windows desktop-level RPA actions, including clicking, scrolling, file selection, text pasting, and sending.
- Uses Tesseract OCR to read creator nicknames and normalize them into stable deduplication keys.
- Uses SQLite to track contacted creators and avoid duplicate outreach.
- Supports OCR-based detection of the `Chat with Affiliate` entry point, reducing reliance on fixed coordinates.
- Confirms the chat window through OCR before continuing the send flow.
- Records logs and OCR debug screenshots for troubleshooting OCR regions, scroll distance, and page states.
- Provides helper scripts for coordinate recording, OCR region recording, scroll testing, and nickname OCR testing.

### Tech Stack

- Python
- PyAutoGUI
- Tesseract OCR / pytesseract
- Pillow
- OpenCV
- SQLite
- pyperclip

### Project Structure

```text
.
├── CAPTURE_GUIDE.md                  # Coordinate and template capture guide
├── requirements.txt
├── config/
│   └── automation_config.example.json # Public example configuration
├── data/                              # Local database folder; placeholder only in public repo
├── images/                            # Local template folder; actual screenshots are not included
│   ├── anchors/
│   ├── buttons/
│   ├── dialogs/
│   └── reference/
├── logs/                              # Runtime logs and debug screenshots; placeholder only
└── scripts/
    ├── automation_utils.py            # Shared OCR, click, logging, and database utilities
    ├── run_creator_bd_rpa.py          # Main workflow entry point
    ├── list_sent_creators.py          # Inspect contacted creator records
    ├── name_ocr_test.py               # Nickname OCR test
    ├── record_mouse_position.py       # Mouse coordinate recorder
    ├── record_region.py               # OCR region recorder
    └── scroll_test.py                 # Scroll parameter tester
```

### Workflow Overview

1. Click the current creator in the list.
2. Capture the nickname region and run OCR.
3. Normalize and validate the creator nickname.
4. Check the SQLite database and skip creators that were already contacted.
5. Open private chat through OCR detection or configured coordinates.
6. Upload an image, paste the message text, and click send.
7. After success, write the creator into the contacted creator database.
8. Close the creator page and scroll to the next creator.

### Reliability Design

- Nickname OCR uses double confirmation to avoid acting on blank regions.
- Creator names are validated by length, character ratio, and allowed format.
- The private chat button can be located through OCR instead of fixed coordinates only.
- The chat window is confirmed through OCR before the send flow continues.
- Each run writes a log file, and key OCR screenshots are saved to `logs/` for debugging.
- Coordinates, OCR regions, timing delays, and recognition thresholds are managed through configuration.

### Local Setup

Install dependencies:

```powershell
pip install -r requirements.txt
```

Prepare local configuration:

```powershell
Copy-Item config\automation_config.example.json config\automation_config.json
```

Then update `config/automation_config.json` based on your screen resolution, browser zoom level, page layout, OCR regions, Tesseract path, and timing parameters.

Run the main workflow:

```powershell
python scripts\run_creator_bd_rpa.py
```

List contacted creators:

```powershell
python scripts\list_sent_creators.py
```

Test nickname OCR:

```powershell
python scripts\name_ocr_test.py
```

### Data and Privacy

The following files are intentionally excluded from the public repository:

- `config/automation_config.json`
- `data/*.db`
- Runtime logs and OCR debug screenshots under `logs/`
- Local template screenshots under `images/**/*.png`
- `.claude/`
- `__pycache__/`

This prevents leaking real creator nicknames, page screenshots, account context, local paths, and runtime artifacts.

### Portfolio Value

This project demonstrates:

- Modeling a real operations workflow as an RPA state flow
- Using OCR to read information from non-structured web interfaces
- Managing lightweight business state and deduplication with SQLite
- Designing validation, skip logic, and debugging support for unstable web UIs
- Building helper tools that improve local automation calibration
