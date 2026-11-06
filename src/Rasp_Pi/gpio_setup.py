"""
GPIO peripheral setup & cleanup module for Raspberry Pi.
"""

try:
    import RPi.GPIO as GPIO
    RPI_GPIO_AVAILABLE = True
except ImportError:
    RPI_GPIO_AVAILABLE = False


def initialize():
    if RPI_GPIO_AVAILABLE:
        GPIO.setmode(GPIO.BCM)
        print("[GPIO] BCM mode initialized.")
    else:
        print("[GPIO MOCK] RPi.GPIO not available.")


def cleanup():
    if RPI_GPIO_AVAILABLE:
        try:
            GPIO.cleanup()
            print("[GPIO] All GPIO pins cleaned up.")
        except Exception as e:
            print(f"[GPIO ERROR] Cleanup error: {e}")
    else:
        print("[GPIO MOCK] Cleaned up.")
