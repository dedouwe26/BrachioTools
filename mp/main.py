FILENAME = "drawing.json"

MOTOR1 = 28
MOTOR2 = 27
MOTOR3 = 26
import time
import machine
import servo
from brachiograph import BrachioGraph

servo1 = servo.PicoServo(MOTOR1)
servo2 = servo.PicoServo(MOTOR2)
servo3 = servo.PicoServo(MOTOR3)

bg = BrachioGraph(servo1, servo2, servo3)

bg.plot_file(FILENAME)