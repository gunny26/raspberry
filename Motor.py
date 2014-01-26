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

    def __init__(self, max_position, min_position):
        self.float_position = 0.0
        self.max_position = max_position
        self.min_position = min_position
        # define
        self.position = 0.0

    def move_float(self, direction, float_step):
        """
        this method is called from controller
        float_step is bewtween 0.0 < 1.0
        """
        logging.debug("move_float called with %d, %f", direction, float_step)
        assert type(direction) == int
        assert (direction == -1) or (direction == 1)
        assert 0.0 <= float_step <= 1.0
        self.float_position += float_step * direction
        logging.debug("move_float position = %d : float_position = %f", self.position, self.float_position)
        logging.debug("Float to Int Value: %f", abs(self.position - self.float_position))
        while abs(self.position - self.float_position) >= float(1):
            self.__move(direction)
        assert abs(self.position - self.float_position) < float(1)

    def __move(self, direction):
        """
        move number of full integer steps
        """
        logging.debug("Moving Motor One step in direction %s", direction)
        logging.debug("Motor accuracy +/- %s", self.position - self.float_position)
        self.position += direction

    def unhold(self):
        logging.info("Unholding Motor Coils")

    def get_position(self):
        return(self.position)

    def get_position_float(self):
        return(self.position_float)


class LaserMotor(Motor):
    """Laser Motor, reactive if axis moves negative"""

    def __init__(self, laser_pin, max_position, min_position):
        self.laser_pin = laser_pin
        self.float_position = 0.0
        self.max_position = max_position
        self.min_position = min_position
        # define
        self.position = 0.0
        GPIO.setup(self.laser_pin, GPIO.OUT)
        GPIO.setup(self.laser_pin, 0)
 
    def move_float(self, direction, float_step):
        """
        this method is called from controller
        float_step is bewtween 0.0 < 1.0
        """
        logging.debug("move_float called with %d, %f", direction, float_step)
        assert type(direction) == int
        assert (direction == -1) or (direction == 1)
        assert 0.0 <= float_step <= 1.0
        self.float_position += float_step * direction
        distance = abs(self.float_position - self.position)
        if distance >= 1.0:
            self.__move(direction)
        distance = abs(self.float_position - self.position)
        logging.debug("int_position = %d : float_position = %f : distance = %f", self.position, self.float_position, distance)
        assert distance < 1.0

    def __move(self, direction):
        """
        move number of full integer steps
        """
        self.position += direction
        # turn on laser if position < 0
        if self.position < 0.0:
            GPIO.output(self.laser_pin, 1)
        else:
            GPIO.output(self.laser_pin, 0)

    def unhold(self):
        logging.info("Power off laser")

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
        b1
    a1      a1
        b2

    following seuqnece is possible (a1, a2, b1, b2)

    low torque mode
    1 0 0 0 a1
    0 0 1 0 b1
    0 1 0 0 a2
    0 0 0 1 b2
    
    high torque mode - full step mode
    1 0 1 0 between a1/b1
    0 1 1 0 between b1/a2
    0 1 0 1 between a2/b2
    1 0 0 1 between b2/a1

    mixed torque mode - half step mode
    1 0 0 0 a1
    1 0 1 0 between a1/b1
    0 0 1 0 b1
    0 1 1 0 between b1/a2
    0 1 0 0 a2
    0 1 0 1 between a2/b2
    0 0 0 1 b2
    1 0 0 1 between b2/a1

    """
    # low torque mode - also low power as only one coil is powered
    SEQUENCE_LOW = ((1,0,0,0), (0,0,1,0), (0,1,0,0), (0,0,0,1))
    # high torque - full step mode
    SEQUENCE_HIGH = ((1,0,1,0), (0,1,1,0), (0,1,0,1), (1,0,0,1))
    # mixed torque - half step mode
    SEQUENCE_MIXED = ((1,0,0,0), (1,0,1,0), (0,0,1,0), (0,1,1,0), (0,1,0,0), (0,1,0,1), (0,0,0,1), (1,0,0,1))
    # ok
    SEQUENCE = SEQUENCE_MIXED

    def __init__(self, coils, max_position, min_position):
        """init"""
        self.coils = coils
        self.max_position = max_position
        self.min_position = min_position
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
        logging.debug("move_float called with %d, %f", direction, float_step)
        assert type(direction) == int
        assert (direction == -1) or (direction == 1)
        assert 0.0 <= float_step <= 1.0
        self.float_position += (float_step * direction)
        distance = abs(self.position - self.float_position)
        if distance >= 1.0:
            logging.debug("initializing full step, distance %s > 1.0", distance) 
            self.__move(direction)
        else:
            logging.debug("distance %s to small to initialize full step", distance)
        distance = abs(self.float_position - self.position)
        logging.debug("int_position = %d : float_position = %f : distance = %f", self.position, self.float_position, distance)
        assert distance < 1.0

    def __move(self, direction):
        """
        move to given direction number of steps, its relative
        delay_faktor could be set, if this Motor is connected to a controller
        which moves also another Motor
        """
        phase = self.SEQUENCE[self.position % self.num_sequence]
        counter = 0
        for pin in self.coils:
            GPIO.output(pin, phase[counter])
            counter += 1
        self.position += direction

    def unhold(self):
        """
        sets any pin of motor to low, so no power is needed
        """
        for pin in self.coils:
            GPIO.output(pin, False)
