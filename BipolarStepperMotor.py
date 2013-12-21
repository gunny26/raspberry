#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import curses

class BipolarStepperMotor(object):

    def __init__(self, coils, delay):
        self.sequence = [(1,0,1,0), (0,1,1,0), (0,1,0,1), (1,0,0,1)]
        self.num_sequence = len(self.sequence)
        self.coils = coils
        for pin in self.coils:
            GPIO.setup(pin, GPIO.OUT)
        self.delay = int(delay) / 1000.0
        self.position = 0
        self.max_position = None
        self.min_position = None

    def sign(self, count):
        if count > 0:
            return(1)
        elif count < 0:
            return(-1)
        else:
            return(0)

    def move(self, direction, steps):
        for _ in range(steps):
            self.position += direction
            phase = self.sequence[self.position % self.num_sequence]
            counter = 0
            for pin in self.coils:
                GPIO.output(pin, phase[counter])
                counter += 1
            time.sleep(self.delay)

    def unhold(self):
        for pin in self.coils:
            GPIO.output(pin, False)

    def get_position(self):
        return(self.position)

    def set_position(self, position):
        self.position = position

    def set_min(self):
        self.min_position = self.position

    def set_max(self):
        self.max_position = self.position

    def goto(self, target):
        """got from actual position to target"""
        steps = target - self.position
        direction = self.sign(steps)
        self.move(direction, abs(steps))

    def run(self):
        """runs from max to min and back"""
        if (self.max_position is not None) and (self.min_position is not None):
            self.goto(self.min_position)
            self.goto(self.max_position)

class XYController(object):

    def __init__(self, motorx, motory):
        """controls two motors, to coordinate movements"""
        self.motorx = motorx
        self.motory = motory
        self.x_float = 0.0
        self.y_float = 0.0
        # ((0,0), (1024, 768))
        self.boundaries = [[None, None], [None, None]]

    def sign(self, count):
        if count > 0:
            return(1)
        elif count < 0:
            return(-1)
        else:
            return(0)

    def move(self, x, y):
        stepx = self.x_float + x - int(self.x_float)
        stepy = self.y_float + y - int(self.y_float)
        direction_x = self.sign(stepx)
        direction_y = self.sign(stepy)
        self.motorx.move(direction_x, abs(int(stepx)))
        self.motory.move(direction_y, abs(int(stepy)))
        self.x_float += x
        self.y_float += y

    def set_max_x(self):
        self.motorx.set_max()
        self.boundaries[1][0] = self.x_float

    def set_min_x(self):
        self.motorx.set_min()
        self.boundaries[0][0] = self.x_float

    def set_max_y(self):
        self.motory.set_max()
        self.boundaries[1][1] = self.y_float

    def set_min_y(self):
        self.motory.set_min()
        self.boundaries[0][1] = self.y_float

    def goto(self, target_x, target_y):
        lengthx = target_x - self.x_float
        lengthy = target_y - self.y_float
        steps = int(max(lengthx, lengthy))
        stepx = lengthx / steps
        stepy = lengthy / steps
        for i in range(steps):
            self.move(stepx, stepy)

    def run(self):
        if self.boundaries != ((None, None), (None, None)):
            self.goto(self.boundaries[0][0], self.boundaries[0][1])
            self.goto(self.boundaries[1][0], self.boundaries[1][1])

def main():
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)

    enable_pin = 18
    GPIO.setup(enable_pin, GPIO.OUT)
    GPIO.output(enable_pin, 1)

    delay = 10
    motorx = BipolarStepperMotor((4, 17, 23, 24), delay)
    motory = BipolarStepperMotor((27, 22, 10, 9), delay)
    controller = XYController(motorx, motory)


    stdscr = curses.initscr()
    curses.cbreak()
    stdscr.keypad(1)

    stdscr.addstr(0,10,"Hit 'q' to quit")
    stdscr.refresh()

    key = ''
    while key != ord('q'):
        stdscr.refresh()
        key = stdscr.getch()
        stdscr.addch(14, 10, key)
        if key == curses.KEY_LEFT:
            controller.move(-1, 0)
        elif key == curses.KEY_RIGHT: 
            controller.move(1, 0)
        elif key == curses.KEY_UP: 
            controller.move(0, 1)
        elif key == curses.KEY_DOWN: 
            controller.move(0, -1)
        elif key == ord("x"): 
            controller.set_min_x()
        elif key == ord("X"): 
            controller.set_max_x()
        elif key == ord("y"): 
            controller.set_min_y()
        elif key == ord("Y"): 
            controller.set_max_y()
        elif key == ord("r"): 
            controller.run()
        elif key == ord("R"): 
            motory.run()
        stdscr.addstr(10, 2, "X-Position : %10s" % motorx.get_position())
        stdscr.addstr(11, 2, "Y-Position : %10s" % motory.get_position())
        stdscr.addstr(12, 2, "X-Min      : %10s" % motorx.min_position)
        stdscr.addstr(13, 2, "X-Max      : %10s" % motorx.max_position)
        stdscr.addstr(14, 2, "Y-Min      : %10s" % motory.min_position)
        stdscr.addstr(15, 2, "Y-Max      : %10s" % motory.max_position)
        stdscr.addstr(16, 2, "ControllerX: %10s" % controller.x_float)
        stdscr.addstr(17, 2, "ControllerY: %10s" % controller.y_float)
        stdscr.addstr(18, 2, "Controller : %s" % str(controller.boundaries))
        time.sleep(delay / 1000.0)
    curses.endwin()
    GPIO.cleanup()

if __name__ == "__main__":
    main()
