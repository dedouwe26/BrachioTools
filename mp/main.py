FILENAME = "drawing.json"

SERVO1 = 28
SERVO2 = 27
SERVO3 = 26

import servo
from brachiograph import BrachioGraph

servo1 = servo.PicoServo(SERVO1)
servo2 = servo.PicoServo(SERVO2)
servo3 = servo.PicoServo(SERVO3)

bg = BrachioGraph(servo1, servo2, servo3)

bg.plot_file(FILENAME)