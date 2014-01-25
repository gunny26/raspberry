#/usr/bin/python
# -*- coding: utf-8 -*-
#
# parse Gcode
#

try:
    import RPi.GPIO as GPIO
except ImportError:
    from FakeGPIO import FakeGPIO as GPIO
import logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
import time

class Motor(object):
    """Abstract Class for Motor"""

    def __init__(self, max_position, min_position, delay=1.0):
        self.float_position = 0.0
        self.max_position = max_position
        self.min_position = min_position
        self.delay = delay / 10000
        # define
        self.position = 0.0

    def move_float(self, direction, float_step):
        """
        this method is called from controller
        float_step is bewtween 0.0 < 1.0
        """
        new_float_position = self.float_position + float_step
        if (new_float_position - self.float_position) >= 1.0:
            self.__move(direction)

    def __move(self, direction):
        """
        move number of full integer steps
        """
        logging.debug("Moving Motor One step in direction %s", direction)
        logging.debug("Motor accuracy +/- %s", self.position - self.float_position)
        self.position += direction
        time.sleep(self.delay)

    def unhold(self):
        logging.info("Unholding Motor Coils")

    def get_position(self):
        return(self.position)

    def get_position_float(self):
        return(self.position_float)


class BipolarStepperMotor(Motor):
    """
    Class to represent a bipolar stepper motor
    it could only with on one dimension, forward or backwards

    cloil -> set(a1, a2, b1, b2) of GPIO Pins where these connectors are patched
    delay -> int(milliseconds to wait between moves
    max_position -> int(maximum position) is set to safe value of 1
    min_position -> int(minimum position) is set to 0
    """
    # ok
    SEQUENCE = [(1,0,0,0), (0,0,1,0), (0,1,0,0), (0,0,0,1)]
    # also ok
    SEQUENCE = [(1,0,0,0), (1,0,1,0), (0,0,1,0), (0,1,1,0), (0,1,0,0), (0,1,0,1), (0,0,0,1), (1,0,0,1)]

    def __init__(self, coils, delay, max_position, min_position):
        """init"""
        self.coils = coils
        self.max_position = max_position
        self.min_position = min_position
        self.delay = int(delay) / 1000.0
        # define coil pins as output
        for pin in self.coils:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.setup(pin, 0)
        # original one from adafruit
        self.num_sequence = len(self.SEQUENCE)
        # initial position to self.min_position
        self.position = 0
        self.float_position = float(self.position)

    def move_float(self, direction, float_step):
        """
        this method is called from controller
        float_step is bewtween 0.0 < 1.0
        """
        logging.error("move_float called with %s and %s", direction, float_step)
        new_float_position = self.float_position + float_step
        logging.error("%s : %s", self.float_position, new_float_position)
        if (new_float_position - self.float_position) >= 1.0:
            self.__move(direction)

    def __move(self, direction):
        """
        move to given direction number of steps, its relative
        delay_faktor could be set, if this Motor is connected to a controller
        which moves also another Motor
        """
        logging.error("__move called")
        phase = self.SEQUENCE[self.position % self.num_sequence]
        logging.error(phase)
        counter = 0
        for pin in self.coils:
            GPIO.output(pin, phase[counter])
            counter += 1
        self.position += direction
        assert self.position <= self.max_position
        assert self.position >= self.min_position
        # give motor a chance to move
        time.sleep(self.delay)

    def unhold(self):
        """
        sets any pin of motor to low, so no power is needed
        """
        for pin in self.coils:
            GPIO.output(pin, False)
