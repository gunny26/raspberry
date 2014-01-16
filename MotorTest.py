#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import sys
import logging
logging.basicConfig(level=logging.DEBUG)
import traceback
import math

class UnipolarStepperMotor(object):
    """
    Class to represent a unipolar stepper motor
    it could only with on one dimension, forward or backwards

    cloil -> set(a1, a2, b1, b2) of GPIO Pins where these connectors are patched
    delay -> int(milliseconds to wait between moves
    max_position -> int(maximum position) is set to safe value of 1
    min_position -> int(minimum position) is set to 0
    """

    def __init__(self, coils, delay, max_position=1, min_position=0):
        """init"""
        # original one from adafruit
        self.sequence = [(1,0,1,0), (0,1,1,0), (0,1,0,1), (1,0,0,1)]
        # trial, but does not work properly
        self.sequence = [(1,0,1,0), (0,0,1,0), (0,1,1,0), (0,1,0,0), (0,1,0,1), (0,0,0,1), (1,0,0,1), (1,0,0,0)]
        # ok
        self.sequence = [(1,0,0,0), (0,0,1,0), (0,1,0,0), (0,0,0,1)]
        # also ok
        self.sequence = [(1,0,0,0), (1,0,1,0), (0,0,1,0), (0,1,1,0), (0,1,0,0), (0,1,0,1), (0,0,0,1), (1,0,0,1)]
        self.num_sequence = len(self.sequence)
        self.coils = coils
        for pin in self.coils:
            GPIO.setup(pin, GPIO.OUT)
        self.delay = int(delay) / 1000.0
        self.position = 0
        self.max_position = max_position
        self.min_position = min_position

    def sign(self, count):
        """return sign of value as either positive or negative 1"""
        if count > 0:
            return(1)
        elif count < 0:
            return(-1)
        else:
            return(0)

    def move(self, direction, steps, delay_faktor=1):
        """
        move to given direction number of steps, its relative
        delay_faktor could be set, if this Motor is connected to a controller
        which moves also another Motor
        """
        assert type(direction) == int
        assert -1 <= direction <= 1
        assert type(steps) == int
        for _ in range(steps):
            self.position += direction
            phase = self.sequence[self.position % self.num_sequence]
            counter = 0
            for pin in self.coils:
                GPIO.output(pin, phase[counter])
                counter += 1
            time.sleep(self.delay / delay_faktor)

    def unhold(self):
        """
        sets any pin of motor to low, so no power is needed
        """
        for pin in self.coils:
            GPIO.output(pin, False)

    def get_position(self):
        """
        return actual position, always int
        """
        return(self.position)

    def set_position(self, position):
        """
        set actual position without movin, for calibration use only
        """
        assert type(position) == int
        self.position = position

    def set_min(self):
        """set minimum value, for calibration use only"""
        self.min_position = self.position

    def set_max(self):
        """set maximum value, for calibration use only"""
        self.max_position = self.position

    def goto(self, target):
        """go from actual position to targeti, target is given absolute"""
        assert type(target) == int
        steps = target - self.position
        direction = self.sign(steps)
        self.move(direction, abs(steps))

    def run(self):
        """runs from max to min and back, for testing"""
        if (self.max_position is not None) and (self.min_position is not None):
            self.goto(self.min_position)
            self.goto(self.max_position)




class BipolarStepperMotor(object):
    """
    Class to represent a bipolar stepper motor
    it could only with on one dimension, forward or backwards

    cloil -> set(a1, a2, b1, b2) of GPIO Pins where these connectors are patched
    delay -> int(milliseconds to wait between moves
    max_position -> int(maximum position) is set to safe value of 1
    min_position -> int(minimum position) is set to 0
    """

    def __init__(self, coils, delay, max_position=1, min_position=0):
        """init"""
        # original one from adafruit
        self.sequence = [(1,0,1,0), (0,1,1,0), (0,1,0,1), (1,0,0,1)]
        # trial, but does not work properly
        self.sequence = [(1,0,1,0), (0,0,1,0), (0,1,1,0), (0,1,0,0), (0,1,0,1), (0,0,0,1), (1,0,0,1), (1,0,0,0)]
        # ok
        self.sequence = [(1,0,0,0), (0,0,1,0), (0,1,0,0), (0,0,0,1)]
        # also ok
        self.sequence = [(1,0,0,0), (1,0,1,0), (0,0,1,0), (0,1,1,0), (0,1,0,0), (0,1,0,1), (0,0,0,1), (1,0,0,1)]
        self.num_sequence = len(self.sequence)
        self.coils = coils
        for pin in self.coils:
            GPIO.setup(pin, GPIO.OUT)
        self.delay = int(delay) / 1000.0
        self.position = 0
        self.max_position = max_position
        self.min_position = min_position

    def sign(self, count):
        """return sign of value as either positive or negative 1"""
        if count > 0:
            return(1)
        elif count < 0:
            return(-1)
        else:
            return(0)

    def move(self, direction, steps, delay_faktor=1):
        """
        move to given direction number of steps, its relative
        delay_faktor could be set, if this Motor is connected to a controller
        which moves also another Motor
        """
        assert type(direction) == int
        assert -1 <= direction <= 1
        assert type(steps) == int
        for _ in range(steps):
            self.position += direction
            phase = self.sequence[self.position % self.num_sequence]
            counter = 0
            for pin in self.coils:
                GPIO.output(pin, phase[counter])
                counter += 1
            time.sleep(self.delay / delay_faktor)

    def unhold(self):
        """
        sets any pin of motor to low, so no power is needed
        """
        for pin in self.coils:
            GPIO.output(pin, False)

    def get_position(self):
        """
        return actual position, always int
        """
        return(self.position)

    def set_position(self, position):
        """
        set actual position without movin, for calibration use only
        """
        assert type(position) == int
        self.position = position

    def set_min(self):
        """set minimum value, for calibration use only"""
        self.min_position = self.position

    def set_max(self):
        """set maximum value, for calibration use only"""
        self.max_position = self.position

    def goto(self, target):
        """go from actual position to targeti, target is given absolute"""
        assert type(target) == int
        steps = target - self.position
        direction = self.sign(steps)
        self.move(direction, abs(steps))

    def run(self):
        """runs from max to min and back, for testing"""
        if (self.max_position is not None) and (self.min_position is not None):
            self.goto(self.min_position)
            self.goto(self.max_position)

class Point(object):
    """arbitrary point class"""

    def __init__(self):
        self.x = 0.0
        self.y = 0.0

    def get(self):
        return((self.x, self.y))

    def getx(self):
        return(self.x)

    def gety(self):
        return(self.y)

    def getx_int(self):
        return(int(round(self.x)))

    def gety_int(self):
        return(int(round(self.y)))

    def set(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return("(%s, %s)" % (self.x, self.y))

class XYController(object):
    """controls 2 Motors"""

    def __init__(self, motorx, motory):
        """controls two motors, two coordinate movements"""
        self.motorx = motorx
        self.motory = motory
        # internal coordinates are stored in float
        self.position = Point()
        # after calibration set ((0,0), (1024, 768))
	self.min_boundary = Point()
	self.max_boundary = Point()

    def sign(self, count):
        """returns sign of count as either +1 or -1"""
        if count > 0:
            return(1)
        elif count < 0:
            return(-1)
        else:
            return(0)

    def move(self, stepx, stepy):
        """
        move to given x,y ccordinates
        x,y are given relative to actual position

        so to move in both direction at the same time,
        parameter x or y has to be sometime float
        """
        assert type(stepx) == float
        assert type(stepy) == float
        assert -1.0 <= stepx <= 1.0
        assert -1.0 <= stepy <= 1.0
        # if all both axis are moved, the delay could be halfed
        delay_faktor = 1
        if stepx <> 0.0 and stepy <> 0.0:
            delay_faktor = 2
        if stepx <> 0.0:
            self.position.x += stepx
            direction = self.sign(stepx)
            # should motor move one full step
            # length between controller position and motor position
            length = abs(self.position.x - self.motorx.position)
            step = int(round(length))
            # only if step is rounded to 1 a full step will be done
            if step == 1:
                self.motorx.move(direction, step, delay_faktor)
        if stepy <> 0.0:
            self.position.y += stepy
            direction = self.sign(stepy)
            # should motor move one full step
            # length between controller position and motor position
            length = abs(self.position.y - self.motory.position)
            step = int(round(length))
            # only if step is rounded to 1 a full step will be done
            if step == 1:
                self.motory.move(direction, step, delay_faktor)

    def set_max_x(self):
        """set maximum x coordinates"""
        self.motorx.set_max()
        self.max_boundary.x = self.position.x

    def set_min_x(self):
        """set minimum x coordinates"""
        self.motorx.set_min()
        self.min_boundary.x = self.position.x

    def set_max_y(self):
        """set maximum y coordinates"""
        self.motory.set_max()
        self.max_boundary.y = self.position.y

    def set_min_y(self):
        """set minimum y coordinates"""
        self.motory.set_min()
        self.min_boundary.y = self.position.y

    def goto(self, target_x, target_y):
        """goto abosulte x,y position"""
        assert type(target_x) == int
        assert type(target_y) == int
        lengthx = target_x - self.position.getx()
        lengthy = target_y - self.position.gety()
        # maximum steps = maximum(length(x), length(y))
        steps = max(abs(lengthx), abs(lengthy))
        if steps > 0:
            stepx = float(lengthx / steps)
            stepy = float(lengthy / steps)
            logging.info("steps: %s, stepx : %s, stepy : %s", steps, stepx, stepy)
            for i in range(int(steps)):
                self.move(stepx, stepy)
        logging.info("Controller (%s, %s) != Motors (%s, %s)", self.position.x, self.position.y, self.motorx.position, self.motory.position)
        # round position to eliminate floating point errors
        self.position.x = round(self.position.x, 2)
        self.position.y = round(self.position.y, 2)
        logging.info("Controller (%s, %s) != Motors (%s, %s)", self.position.x, self.position.y, self.motorx.position, self.motory.position)
        assert self.motorx.position == self.position.x
        assert self.motory.position == self.position.y

    def run(self):
        """goto every boundary, for testing purposes"""
        # left up corner
        self.goto(self.max_boundary.x, self.max_boundary.y)
        self.goto(self.max_boundary.x, self.min_boundary.y)
        self.goto(self.min_boundary.x, self.max_boundary.y)
        self.goto(self.min_boundary.x, self.min_boundary.y)

    def get_max(self):
        """get maximum point"""
        return(self.max_boundary)

    def get_min(self):
        """get minimum point"""
        return(self.min_boundary)

    def get_boundaries(self):
        """get area"""
        return((self.get_min(), self.get_max()))

    def get_position(self):
        """get actual position"""
        return(self.position)

    def unhold(self):
        """unhold motor to prevent power consumption"""
        self.motorx.unhold()
        self.motory.unhold()

def main():
    # bring GPIO to a clean state
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)

    # enable lm293d with pin 18 HIGH
    enable_pin = 18
    GPIO.setup(enable_pin, GPIO.OUT)
    GPIO.output(enable_pin, 1)

    # delay in ms (milliseconds) for phase change
    delay = 1.0
    maxx = 512
    maxy = 512
    # first motor on
    # a1=4
    # a2=17
    # b1=23
    # b2=24
    motorx = BipolarStepperMotor((4, 17, 23, 24), delay, maxx)
    # second motor
    # a1=27
    # a2=22
    # b1=10
    # b2=9
    motory = BipolarStepperMotor((27, 22, 10, 9), delay, maxy)
    motorz = UnipolarStepperMotor((24, 25, 8, 7), delay, maxy)
    # let controller handle these two motors
    controller = XYController(motorx, motory)

    # calculate a circle
    points = []
    step = math.pi / 360
    for degree in range(360):
        x = int(maxx / 2 + math.cos(degree * step) * maxx / 2)
        y = int(maxy / 2 + math.sin(degree * step) * maxy / 2)
        points.append((x, y))

    key = ''
    while True:
        logging.info("M-Position   : %s, %s" % (motorx.get_position(), motory.get_position()))
        logging.info("M-X(min/max) : %s, %s" % (motorx.min_position, motorx.max_position))
        logging.info("M-Y(min/max) : %s, %s" % (motory.min_position, motory.max_position))
        logging.info("C-Position   : %s" % str(controller.get_position()))
        logging.info("C-(min/max)  : %s" % str(controller.get_boundaries()))
        logging.info("Press V to draw Circle")
        logging.info("press X to got from min to max on X-Axis")
        logging.info("press Y to got from min to max on Y-Axis")
 
        key = raw_input("Bitte gib was ein:")
        if key == "a":
            controller.move(-1.0, 0.0)
        elif key == "d": 
            controller.move(1.0, 0.0)
        elif key == "w": 
            controller.move(0.0, 1.0)
        elif key == "x": 
            controller.move(0.0, -1.0)
        elif key == "q": 
            controller.move(-1.0, 1.0)
        elif key == "e": 
            controller.move(1.0, 1.0)
        elif key == "y": 
            controller.move(-1.0, -1.0)
        elif key == "c": 
            controller.move(1.0, -1.0)
        elif key == "s": 
            controller.unhold()
        elif key == "center":
            controller.goto(maxx / 2, maxy / 2)
        elif key == "zero":
            controller.goto(0, 0)
        elif key == "max":
            controller.goto(maxx, maxy)
        elif key == "C": 
            logging.info("Diagonal")
            controller.goto(maxx, maxy)
            controller.goto(0, 0)
            logging.info("Diagonal half y")
            controller.goto(maxx, maxy / 2)
            controller.goto(0, 0)
            logging.info("Diagonal half x")
            controller.goto(maxx / 2, maxy)
            controller.goto(0, 0)
        elif key == "X":
            controller.goto(0, 0)
            controller.goto(maxx, 0)
            controller.goto(0, 0)
        elif key == "Y":
            controller.goto(0, 0)
            controller.goto(0, maxy)
            controller.goto(0, 0) 
        elif key == "V":
            controller.goto(0, maxy/2)
            for point in points:
                controller.goto(point[0], maxy/2)
            controller.goto(0, 0)
            for point in points:
                controller.goto(maxx/2, point[1])
            controller.goto(0, 0)
            for point in points:
                controller.goto(point[0], point[1])
            controller.goto(0, 0)
        controller.unhold()
        time.sleep(delay / 1000.0)
    GPIO.cleanup()

if __name__ == "__main__":
    try:
       main()
    except Exception, exc:
       GPIO.cleanup()
       traceback.print_exc()
       raise exc
       sys.exit(1)
