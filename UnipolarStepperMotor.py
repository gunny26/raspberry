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
        self.sequence = [(1,0,0,0), (0,1,0,0), (0,0,1,0), (0,0,0,1)]
        # trial, but does not work properly
        #self.sequence = [(1,0,1,0), (0,0,1,0), (0,1,1,0), (0,1,0,0), (0,1,0,1), (0,0,0,1), (1,0,0,1), (1,0,0,0)]
        # ok
        #self.sequence = [(1,0,0,0), (0,0,1,0), (0,1,0,0), (0,0,0,1)]
        # also ok
        # self.sequence = [(1,0,0,0), (1,0,1,0), (0,0,1,0), (0,1,1,0), (0,1,0,0), (0,1,0,1), (0,0,0,1), (1,0,0,1)]
        self.num_sequence = len(self.sequence)
        self.coils = coils
        for pin in self.coils:
            GPIO.setup(pin, GPIO.OUT)
        self.delay = float(delay) / 1000.0
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
        sleeptime = self.delay / delay_faktor
        starttime = time.time()
        for _ in range(steps):
            phase = self.sequence[self.position % self.num_sequence]
            self.position += direction
            GPIO.output(self.coils[0], phase[0])
            GPIO.output(self.coils[1], phase[1])
            GPIO.output(self.coils[2], phase[2])
            GPIO.output(self.coils[3], phase[3])
            time.sleep(sleeptime)
        logging.info("Real Duration = %s should be %s", time.time() - starttime, sleeptime * steps)

    def unhold(self):
        """
        sets any pin of motor to low, so no power is needed
        """
        for pin in self.coils:
            GPIO.output(pin, False)

    def set_delay(self, delayms):
        self.delay = float(delayms) / 1000

    def get_delay(self):
        return(self.delay * 1000)

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


def sign(count):
    """return sign of value as either positive or negative 1"""
    if count > 0:
        return(1)
    elif count < 0:
        return(-1)
    else:
        return(0)

def main():
    # bring GPIO to a clean state
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)

    # delay in ms (milliseconds) for phase change
    delay = 10.0
    maxx = 512
    # first motor on
    motor = UnipolarStepperMotor((24, 25, 8, 7), delay, maxx)

    while True:
        logging.info("M-Position   : %s" % motor.get_position())
        logging.info("M-X(min) : %s" % motor.min_position)
        logging.info("M-Y(max) : %s" % motor.min_position)
        logging.info("M delay  : %f ms" % motor.get_delay())
        logging.info("g<int> to move in direction number of steps")
        logging.info("d<int> to set delay in ms")
        key = raw_input("Bitte gib was ein:")
        if key[0] == "g":
            steps = abs(int(key[1:]))
            direction = sign(int(key[1:]))
            logging.info("move(%s, %s)", direction, steps)
            motor.move(direction, steps)
        elif key[0] == "d": 
            motor.set_delay(int(key[1:]))
        motor.unhold()

if __name__ == "__main__":
    try:
       main()
    except Exception, exc:
       GPIO.cleanup()
       traceback.print_exc()
       raise exc
       sys.exit(1)
