#!/usr/bin/env python3
"""
Dedicated HC-SR501 PIR Sensor Hysteresis Diagnostic Tool (v3 - Rock-Solid)
Fixes:
- NEVER starts with 'Motion Detected': Enforces a clean zero-baseline calibration at startup.
- Requires true LOW -> HIGH transition to trigger.
- Full Hysteresis Loop:
    * IDLE / ARMED: Waiting for fresh motion (begins at State 0: NO MOTION).
    * MOTION ACTIVE: Tracking active presence.
    * QUIET RESET: If motion stops for QUIET_TIMEOUT (default 3s), resets cleanly to IDLE.
    * HYSTERESIS IGNORE: If motion is continuous for >= CONTINUOUS_MAX (default 5s),
      the PIR is actively ignored for IGNORE_INTERVAL (default 15s) with a live countdown.
    * RE-ARM SAFEGUARD: After ignore interval, requires pin to return to 0 before re-arming.
"""

import time
import sys

PIN = 17
QUIET_TIMEOUT = 3.0           # Seconds of silence required to return to IDLE
CONTINUOUS_MAX = 5.0          # Seconds of continuous detection before entering ignore mode
IGNORE_INTERVAL = 15.0        # Seconds to ignore/suppress PIR during continuous detection

print("=" * 68)
print("     HC-SR501 PIR SENSOR HYSTERESIS DIAGNOSTIC TOOL (v3)")
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


# ==============================================================================
# STARTUP CALIBRATION: GUARANTEE INITIAL "NO MOTION" BASELINE
# ==============================================================================
print("\n[STARTUP] Calibrating PIR sensor baseline...")
print("[STARTUP] Ensuring initial state is NO MOTION (0)...")

# If pin is currently 1, wait for it to drop to 0
if read_pin() == 1:
    sys.stdout.write("[STARTUP] Sensor pin is currently HIGH. Waiting for sensor to settle to 0...")
    sys.stdout.flush()
    while read_pin() == 1:
        time.sleep(0.2)
    print(" Done.")

# Require 2 continuous seconds of clean LOW (0) to confirm stability
sys.stdout.write("[STARTUP] Verifying 2s clean quiet baseline...")
sys.stdout.flush()
quiet_start = time.time()
while time.time() - quiet_start < 2.0:
    if read_pin() == 1:
        # Interrupted by motion, reset timer
        quiet_start = time.time()
        sys.stdout.write(".")
        sys.stdout.flush()
    time.sleep(0.1)

print("\n[STARTUP COMPLETE] Clean baseline established: State 0 (NO MOTION).")
print("=" * 68)
print("System is ARMED and waiting for movement. (Press Ctrl+C to exit)\n")


# ==============================================================================
# MAIN HYSTERESIS SENSING LOOP
# ==============================================================================
state = "IDLE"
motion_start_time = 0.0
last_high_time = 0.0
ignore_start_time = 0.0
trigger_count = 0
prev_pin_state = 0

try:
    while True:
        pin = read_pin()
        now = time.time()
        clock = time.strftime("%H:%M:%S")

        if state == "IDLE":
            # Strict rising edge detection (must transition 0 -> 1)
            if pin == 1 and prev_pin_state == 0:
                # Debounce check: confirm still 1 after 30ms to reject power spikes
                time.sleep(0.03)
                if read_pin() == 1:
                    trigger_count += 1
                    state = "ACTIVE"
                    motion_start_time = now
                    last_high_time = now
                    print(f"\n[{clock}] >>> [TRIGGER #{trigger_count} DETECTED] Motion active! <<<")

        elif state == "ACTIVE":
            if pin == 1:
                last_high_time = now
                continuous_duration = now - motion_start_time

                # Continuous detection threshold exceeded -> enter Hysteresis Ignore state
                if continuous_duration >= CONTINUOUS_MAX:
                    state = "IGNORED"
                    ignore_start_time = now
                    print(f"\n[{clock}] ⚠️ [HYSTERESIS TRIGGERED] Continuous detection for {continuous_duration:.1f}s!")
                    print(f"[{clock}] ⏸️ [PIR IGNORED] Suppressing sensor for {IGNORE_INTERVAL:.0f}s...")
            else:
                # Pin is currently LOW (0)
                quiet_duration = now - last_high_time
                if quiet_duration >= QUIET_TIMEOUT:
                    # Clean reset: no motion for quiet duration
                    state = "IDLE"
                    print(f"\n[{clock}] --- [STATE: IDLE / ARMED ⚪] Motion quiet for {quiet_duration:.1f}s. Ready for next trigger!")

        elif state == "IGNORED":
            # PIR is blind / suppressed during this window
            elapsed_ignore = now - ignore_start_time
            remaining_ignore = IGNORE_INTERVAL - elapsed_ignore

            if remaining_ignore <= 0:
                print(f"\n[{clock}] 🔔 [IGNORE INTERVAL EXPIRED] Sensor suppression ended.")
                if pin == 0:
                    state = "IDLE"
                    print(f"[{clock}] --- [STATE: IDLE / ARMED ⚪] Sensor is LOW (0). Armed and ready for next trigger!")
                else:
                    state = "WAITING_LOW"
                    print(f"[{clock}] ⏳ Sensor is still physically HIGH. Waiting for pin to drop to 0 before re-arming...")

        elif state == "WAITING_LOW":
            # Wait for pin to return to 0 before allowing new triggers
            if pin == 0:
                # Require 1 second of stable LOW before re-arming
                time.sleep(1.0)
                if read_pin() == 0:
                    state = "IDLE"
                    print(f"\n[{clock}] --- [STATE: IDLE / ARMED ⚪] Sensor settled at 0. Armed and ready for next trigger!")

        prev_pin_state = pin

        # Single-line live terminal status display
        if state == "IDLE":
            status_str = "[ STATE: IDLE / ARMED ⚪ (NO MOTION) ]     "
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

        time.sleep(0.05)

except KeyboardInterrupt:
    print("\n\nStopping test...")
finally:
    cleanup()
    print("GPIO cleaned up safely.")
