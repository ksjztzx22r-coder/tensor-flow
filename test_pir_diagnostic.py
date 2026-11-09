#!/usr/bin/env python3
"""
Dedicated HC-SR501 PIR Sensor Live Diagnostic Tool
Polls BCM GPIO 17 (Physical Pin 11) continuously and prints real-time pin voltage states.
"""

import time
import sys

PIN = 17

print("=" * 60)
print("     HC-SR501 PIR SENSOR LIVE DIAGNOSTIC TOOL")
print(f"     Monitoring BCM GPIO {PIN} (Physical Pin 11)")
print("=" * 60)

# Try gpiozero first (native to Raspberry Pi OS Bookworm)
gpio_mode = None
try:
    from gpiozero import DigitalInputDevice
    pir_device = DigitalInputDevice(PIN, pull_up=False)
    gpio_mode = "gpiozero"
    read_pin = lambda: int(pir_device.value)
    cleanup = lambda: pir_device.close()
    print("[INIT] Using modern 'gpiozero' backend.")
except Exception:
    pass

# Fallback to RPi.GPIO
if gpio_mode is None:
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        gpio_mode = "RPi.GPIO"
        read_pin = lambda: int(GPIO.input(PIN))
        cleanup = lambda: GPIO.cleanup()
        print("[INIT] Using 'RPi.GPIO' backend.")
    except Exception as e:
        print(f"[FATAL ERROR] Cannot initialize GPIO: {e}")
        print("Note: If you see 'GPIO busy', run: sudo systemctl stop wildlife.service")
        sys.exit(1)

print("\n--- Diagnostic Instructions ---")
print("1. Stand still or cover sensor with a cup for 10-15s.")
print("2. Wave your hand 1-2 feet in front of the dome.")
print("3. Watch the LIVE STATE indicator below (0 = IDLE, 1 = MOTION DETECTED).")
print("Press Ctrl+C to exit.\n")

last_val = -1
trigger_count = 0
high_start_time = None

try:
    while True:
        val = read_pin()
        current_time = time.strftime("%H:%M:%S")

        # When state changes
        if val != last_val:
            if val == 1:
                trigger_count += 1
                high_start_time = time.time()
                print(f"\n[{current_time}] >>> MOTION DETECTED! (Trigger #{trigger_count}) <<<")
                print(f"[{current_time}] Holding for 5s cooldown before re-arming...")
                time.sleep(5.0)
                print(f"[{current_time}] --- Re-armed & Idle (Ready for next motion) ---")
            last_val = val

        # Print live status bar on the same line
        indicator = "[ MOTION 🔴 ]" if val == 1 else "[ IDLE   ⚪ ]"
        sys.stdout.write(f"\rCurrent Pin State: {val} {indicator} ")
        sys.stdout.flush()

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n\nStopping test...")
finally:
    cleanup()
    print("GPIO cleaned up safely.")
