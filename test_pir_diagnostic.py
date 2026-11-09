#!/usr/bin/env python3
"""
Dedicated HC-SR501 PIR Sensor Hysteresis Diagnostic Tool
Demonstrates the Hysteresis sensing loop:
- State 1: IDLE / ARMED (Waiting for movement)
- State 2: TRIGGERED / ACTIVE (Motion detected, tracking continuous presence)
- State 3: QUIET RESET (If motion stops for QUIET_TIMEOUT, cleanly resets to IDLE)
- State 4: HYSTERESIS IGNORE (If motion persists continuously for >= CONTINUOUS_MAX,
           the PIR is completely ignored for IGNORE_INTERVAL seconds before re-arming)
"""

import time
import sys

PIN = 17
QUIET_TIMEOUT = 3.0           # Seconds of silence required to return to IDLE
CONTINUOUS_MAX = 5.0          # Seconds of continuous detection before entering ignore mode
IGNORE_INTERVAL = 15.0        # Seconds to ignore/suppress PIR during continuous detection

print("=" * 68)
print("     HC-SR501 PIR SENSOR HYSTERESIS DIAGNOSTIC TOOL")
print(f"     Monitoring BCM GPIO {PIN} (Physical Pin 11)")
print(f"     Settings: Quiet Reset = {QUIET_TIMEOUT}s | Max Continuous = {CONTINUOUS_MAX}s")
print(f"               Ignore Window = {IGNORE_INTERVAL}s")
print("=" * 68)

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

print("\n--- How to Test the Hysteresis Loop ---")
print("1. [Quick Pass]: Wave hand briefly and stop -> Pin goes to 0 -> Cleans up in 3s -> IDLE.")
print(f"2. [Continuous Motion]: Keep waving for > {CONTINUOUS_MAX:.0f}s -> Hysteresis activates!")
print(f"   The PIR will be completely IGNORED for {IGNORE_INTERVAL:.0f}s.")
print("3. [Re-arm]: Once the ignore window ends, it cleanly returns to IDLE for Trigger #2.")
print("Press Ctrl+C to exit.\n")

# State variables:
# "IDLE", "ACTIVE", "IGNORED", "WAITING_LOW"
state = "IDLE"
motion_start_time = 0.0
last_high_time = 0.0
ignore_start_time = 0.0
trigger_count = 0

try:
    while True:
        pin = read_pin()
        now = time.time()
        clock = time.strftime("%H:%M:%S")

        if state == "IDLE":
            if pin == 1:
                # Transition: IDLE -> ACTIVE
                trigger_count += 1
                state = "ACTIVE"
                motion_start_time = now
                last_high_time = now
                print(f"\n[{clock}] >>> [TRIGGER #{trigger_count} DETECTED] Motion active! <<<")

        elif state == "ACTIVE":
            if pin == 1:
                last_high_time = now
                continuous_duration = now - motion_start_time

                # Hysteresis check: continuous motion exceeded threshold!
                if continuous_duration >= CONTINUOUS_MAX:
                    state = "IGNORED"
                    ignore_start_time = now
                    print(f"\n[{clock}] ⚠️ [HYSTERESIS TRIGGERED] Continuous detection for {continuous_duration:.1f}s!")
                    print(f"[{clock}] ⏸️ [PIR IGNORED] Suppressing sensor for {IGNORE_INTERVAL:.0f}s...")
            else:
                # Pin dropped to 0
                quiet_duration = now - last_high_time
                if quiet_duration >= QUIET_TIMEOUT:
                    # Clean quiet reset back to IDLE
                    state = "IDLE"
                    print(f"\n[{clock}] --- [STATE: IDLE / ARMED ⚪] Motion quiet for {quiet_duration:.1f}s. Ready for next trigger!")

        elif state == "IGNORED":
            elapsed_ignore = now - ignore_start_time
            remaining_ignore = IGNORE_INTERVAL - elapsed_ignore

            if remaining_ignore <= 0:
                print(f"\n[{clock}] 🔔 [IGNORE INTERVAL EXPIRED] Sensor suppression ended.")
                if pin == 0:
                    state = "IDLE"
                    print(f"[{clock}] --- [STATE: IDLE / ARMED ⚪] Sensor is LOW. Ready for next trigger!")
                else:
                    state = "WAITING_LOW"
                    print(f"[{clock}] ⏳ Sensor is still physically HIGH. Waiting for pin to drop LOW before re-arming...")

        elif state == "WAITING_LOW":
            if pin == 0:
                state = "IDLE"
                print(f"\n[{clock}] --- [STATE: IDLE / ARMED ⚪] Sensor dropped to LOW. Armed and ready for next trigger!")

        # Format live single-line status display
        if state == "IDLE":
            status_str = "[ STATE: IDLE / ARMED ⚪ ]               "
        elif state == "ACTIVE":
            if pin == 1:
                dur = now - motion_start_time
                status_str = f"[ STATE: MOTION ACTIVE 🔴 ({dur:.1f}s) ]       "
            else:
                q = now - last_high_time
                status_str = f"[ STATE: QUIET WAIT ({q:.1f}s/{QUIET_TIMEOUT:.0f}s) 🟡 ]       "
        elif state == "IGNORED":
            rem = max(0.0, IGNORE_INTERVAL - (now - ignore_start_time))
            status_str = f"[ STATE: IGNORED / BLIND ⏸️ ({rem:.1f}s left) ]"
        elif state == "WAITING_LOW":
            status_str = "[ STATE: WAITING FOR PIN TO DROP LOW ⏳ ]  "

        sys.stdout.write(f"\rRaw Pin: {pin} | {status_str} ")
        sys.stdout.flush()

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n\nStopping test...")
finally:
    cleanup()
    print("GPIO cleaned up safely.")
