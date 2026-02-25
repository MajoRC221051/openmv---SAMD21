# Capture with I2C Feb 25 2026

import sensor
from pyb import I2C
import machine
import os
import random

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)

try:
    os.mkdir("images")
except OSError:
    pass

i2c = I2C(2, I2C.SLAVE, addr=0x12)

capture_count = 0

led = machine.LED("LED_BLUE")

while True:
    led.toggle()
    sensor.snapshot()
    try:
        data = i2c.recv(1, timeout=500)

        print("Dato recibido:", data)

        if data == b'\x55':
            capture_count += 1
            img = sensor.snapshot()
            print("Captura #", capture_count)
            print("Captura lista")
            led.off()

            rand_num = random.randint(0, 99999)
            filename = "images/img_%d.jpg" % rand_num
            img.save(filename)

    except OSError:
        pass
