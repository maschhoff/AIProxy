# NEOPIXEL for non neopixel firmware

from machine import Pin
import time

PIN_NUM = 48
pin = Pin(PIN_NUM, Pin.OUT)

# Bit senden (angepasste µs-Dauern)
def send_bit(is_one):
    if is_one:
        pin.on()
        time.sleep_us(1)  # HIGH für "1"
        pin.off()
        time.sleep_us(1)  # LOW für "1"
    else:
        pin.on()
        time.sleep_us(0)  # HIGH für "0" (sehr kurz)
        pin.off()
        time.sleep_us(1)  # LOW für "0"

def send_byte(byte):
    for i in range(8):
        send_bit(byte & (1 << (7 - i)))

def send_color(r, g, b):
    send_byte(g)
    send_byte(r)
    send_byte(b)

def show_white():
    send_color(100, 100, 100)
    time.sleep_us(80)  # Reset-Zeit
    

def show_off(repeat=3):
    for _ in range(repeat):
        send_color(0, 0, 0)
        time.sleep_us(80)

# Test: an, 1 Sekunde warten, dann aus
#show_white()

