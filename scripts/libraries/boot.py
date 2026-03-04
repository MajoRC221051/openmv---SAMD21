# March 3rd, 2026 - PAYLOAD-MILO TEAN

import sensor
import time
import ml
import uos
import gc
from pyb import I2C

def init_sensor():
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.set_windowing((240, 240))
    sensor.skip_frames(time=2000)

init_sensor()

net = ml.Model("trained.tflite")
labels = [line.rstrip('\n') for line in open("labels.txt")]

try:
    uos.mkdir("images")
except OSError:
    pass
# I2C
i2c = I2C(2, I2C.SLAVE, addr=0x42)

# VAR
mode = 0

contrast_val = 0
brightness_val = 0
MIN_VAL = -5
MAX_VAL = 5

last_detection_time = 0
cooldown_ms = 5000

best_label = ""
best_score = 0.0
detected_flag = 0
saved_flag = 0

clock = time.clock()

while True:

    saved_flag = 0

    if mode == 1:

        clock.tick()
        img = sensor.snapshot()

        predictions = net.predict([img])[0].flatten().tolist()
        best_label, best_score = max(zip(labels, predictions), key=lambda x: x[1])

        if best_label == "Cloudy_Medium_High" and best_score > 0.8:

            detected_flag = 1
            current_time = time.ticks_ms()

            if time.ticks_diff(current_time, last_detection_time) > cooldown_ms:

                filename = "images/cloudy_%d.jpg" % current_time
                img.save(filename, quality=85)
                gc.collect()

                last_detection_time = current_time
                saved_flag = 1
        else:
            detected_flag = 0

    try:
        data = i2c.recv(1, timeout=10)

        if data:

            cmd = data.decode()
            response = ""

            if cmd == 'M':
                mode = 1
                response = "MODEL ON"

            elif cmd == 'S':
                mode = 0
                response = "MODEL OFF"

            elif cmd == 'C':
                img = sensor.snapshot()
                filename = "images/manual_%d.jpg" % time.ticks_ms()
                img.save(filename, quality=85)
                gc.collect()
                response = "CAPTURE SAVED"

            elif cmd == 's':
                if brightness_val < MAX_VAL:
                    brightness_val += 1
                    sensor.set_brightness(brightness_val)
                response = "BRIGHT {}".format(brightness_val)

            elif cmd == 'x':
                if brightness_val > MIN_VAL:
                    brightness_val -= 1
                    sensor.set_brightness(brightness_val)
                response = "BRIGHT {}".format(brightness_val)

            elif cmd == 'a':
                if contrast_val < MAX_VAL:
                    contrast_val += 1
                    sensor.set_contrast(contrast_val)
                response = "CONTRAST {}".format(contrast_val)

            elif cmd == 'z':
                if contrast_val > MIN_VAL:
                    contrast_val -= 1
                    sensor.set_contrast(contrast_val)
                response = "CONTRAST {}".format(contrast_val)

            elif cmd == 'r':
                response = "C:{} B:{} M:{}".format(
                    contrast_val,
                    brightness_val,
                    mode
                )
            elif cmd == 'q':
                response = "{},{:.2f},{},{}".format(
                    best_label,
                    best_score,
                    detected_flag,
                    saved_flag
                )
            elif cmd == 'y':
                response = "RESET ON"

            if response != "":
                i2c.send(response + "\n")

    except OSError:
        pass
