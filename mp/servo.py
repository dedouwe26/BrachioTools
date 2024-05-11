import time

class Servo:
    def __init__(self):
        pass
    def get(self) -> int:
        raise NotImplementedError()
    def goto(self, pos: int):
        raise NotImplementedError()
    def goto_float(self, pos: float):
        self.goto(round(pos))
    def move(self, start: int, end: int):
        diff = end - start
        angle = start
        length_of_step = diff / abs(diff)
        for i in range(abs(diff)):
            angle += length_of_step
            self.goto_float(angle)
            time.sleep(0.001)

class PicoServo(Servo):
    def __init__(self, port: int):
        import machine
        self.pwm = machine.PWM(machine.Pin(port))
        self.pwm.freq(50)
        machine.time_pulse_us(port, 0)
    def get(self) -> int:
        return 0 # FIXME: fixed value.
    def goto(self, pos: int):
        self.pwm.duty_u16(pos)

# class RPIServo(Servo):
#     def __init__(self, port: int):
#         import machine
#         self.pwm = machine.PWM(machine.Pin(port))
#     def goto(self, pos: int):
#         self.pwm.duty_u16(pos)

