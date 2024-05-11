# from brachiograph import BrachioGraph
# import os

# if __name__ == "__main__":
#     bg = BrachioGraph()

#     FILEPATH = "./lines.json"

#     if (os.path.is_file(FILEPATH)):
#         bg.plot_file(FILEPATH)

import time

MOTOR1 = 28
MOTOR2 = 27
MOTOR3 = 26
# import numpy
import time
import machine
import servo
from brachiograph import BrachioGraph

servo1 = servo.PicoServo(MOTOR1)
servo2 = servo.PicoServo(MOTOR2)
servo3 = servo.PicoServo(MOTOR3)

bg = BrachioGraph(servo1, servo2)

for position in range(1000,9000,50):
    servo.goto(position)
    time.sleep(0.01)