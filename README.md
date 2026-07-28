# Keylogger - Educational Project

This project is a **keylogger built for educational purposes**, developed as part of a learning project to understand how low-level keyboard capture, thread synchronization, and remote log delivery work in practice. It captures keystrokes on Linux (including Wayland sessions), reconstructs the actual typed text, stores it locally with automatic rotation, and can optionally forward it to a Discord channel via webhook.

> ⚠️ **DISCLAIMER:** This tool is for **educational** and **ethical use only**. Unauthorized use of any keylogging software may violate laws and privacy regulations. Use responsibly and only on your own machine, or with explicit consent from the device owner.

---

## Project Structure

```plaintext
keylogger/
│
├── keylogger.py             # Main application: capture, logging, webhook delivery
├── keylogger_tests.py        # Manual test scripts for each component
├── requirements.txt           # Python dependencies
└── README.md
```

---

## Features

- Real keyboard capture via `evdev`, reading directly from `/dev/input/`
- **Wayland-compatible** — bypasses the display-server restrictions that block libraries like `pynput` from capturing keys globally
- Reconstructs actual typed text (handles backspace, space and enter), not just raw key names
- Thread-safe local logging with automatic file rotation by size
- Optional batched delivery to a Discord webhook, configurable at runtime
- Pause/resume logging on demand (`F9`), without stopping keyboard capture
- Automatic detection of **multiple connected keyboards** at once

---

## How to Run

### 1. Clone or Download the Project

```bash
git clone https://github.com/Jarock75/keylogger
cd keylogger
```

### 2. Set Up a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install evdev requests
```

### 4. Run the Keylogger

```bash
python keylogger.py
```

You'll be prompted for a Discord webhook URL (leave empty to log locally only):

[*] Enter the webhook URL (leave empty to skip webhook delivery):


Captured text is saved to `~/keyloggerLogs/keylogger.log`.

---

## Permissions (Linux)

Reading raw keyboard events via `evdev` requires elevated access to `/dev/input/`. You have two options:

**Quick (run with sudo each time):**
```bash
sudo venv/bin/python keylogger.py
```

**No sudo needed afterwards:**
```bash
sudo usermod -aG input $USER
```
Log out and back in for the change to take effect.

---

## Controls

| Key            | Action                        |
|----------------|-------------------------------|
| `F9` (or `Fn+F9` on some laptops) | Pause / resume logging |
| `Ctrl+C`       | Stop the keylogger gracefully |

While paused, keys are still detected but nothing is written to the log or sent
to the webhook, until logging is resumed.

---

## Ethical Use & GDPR Notice

- This project is intended **exclusively for learning and research** in a controlled, personal environment.
- No sensitive data should ever be collected from a device without the explicit consent of its owner.
- The webhook URL is requested interactively at runtime and is never hardcoded or committed to the repository, to avoid accidental exposure.

---

## Platform Notes

- Built and tested on **Arch Linux** with **Wayland**.
- Relies on `evdev`, which is Linux-specific — it will **not** run as-is on Windows or macOS.

---

## Known Limitations

- Does not yet distinguish uppercase from lowercase (Shift/Caps Lock state is not tracked).
- Linux-only, due to its dependency on `evdev`.
- When run with `sudo`, log files are currently saved and owned by `root`instead of the invoking user's own account.
