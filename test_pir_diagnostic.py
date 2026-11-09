#!/usr/bin/env python3
"""
Dedicated HC-SR501 PIR Sensor Continuous State Monitor
Tracks Trigger <-> No Trigger states continuously with a clean 5-second silence timeout.
"""

import time
import sys

PIN = 17
INACTIVITY_TIMEOUT = 5.0  # Seconds of silence required to return to IDLE

print("=" * 65)
print("     HC-SR501 CONTINUOUS TRIGGER / NO TRIGGER MONITOR")
print(f"     Pin: BCM GPIO {PIN} (Physical Pin 11)")
print(f"     Inactivity Reset Window: {INACTIVITY_TIMEOUT}s")
print("=" * 65)

# Try gpiozero first (native to Raspberry Pi OS Bookworm)
gpio_mode = None
try:
    from gpiozero import DigitalInputDevice
    pir_device = DigitalInputDevice(PIN, pull_up=False)
    gpio_mode = "gpiozero"
    read_pin = lambda: int(pir_device.value)
    cleanup = lambda: pir_device.close()
    print("[INIT] Using 'gpiozero' backend.")
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
        sys.exit(1)

print("\n--- Diagnostic Instructions ---")
print("• Move your hand: System enters [TRIGGER / MOTION ACTIVE].")
print(f"• Hold still for {INACTIVITY_TIMEOUT}s: System resets to [NO TRIGGER / IDLE].")
print("• Repeat as many times as you want. Press Ctrl+C to exit.\n")

is_triggered = False
last_motion_time = 0
trigger_count = 0

try:
    while True:
        current_state = read_pin()
        now = time.time()
        clock = time.strftime("%H:%M:%S")

        if current_state == 1:
            last_motion_time = now
            if not is_triggered:
                # Transition: NO TRIGGER -> TRIGGER
                is_triggered = True
                trigger_count += 1
                print(f"\n[{clock}] >>> [TRIGGER DETECTED] (Event #{trigger_count}) <<<")

        else:
            # Pin is LOW (0)
            if is_triggered:
                # Check if we have been quiet for INACTIVITY_TIMEOUT
                elapsed_quiet = now - last_motion_time
                if elapsed_quiet >= INACTIVITY_TIMEOUT:
                    # Transition: TRIGGER -> NO TRIGGER
                    is_triggered = False
                    print(f"\n[{clock}] --- [NO TRIGGER / IDLE] (Clear for {elapsed_quiet:.1f}s) --- Ready for next trigger!")

        # Live visual status
        status_text = "[ STATE: TRIGGERED  🔴 ]" if is_triggered else "[ STATE: NO TRIGGER ⚪ ]"
        raw_pin = f"Raw Pin: {current_state}"
        sys.stdout.write(f"\r{raw_pin} | {status_text} ")
        sys.stdout.flush()

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n\nStopping test...")
finally:
    cleanup()
    print("GPIO cleaned up safely.")
