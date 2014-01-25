#/usr/bin/python
# -*- coding: utf-8 -*-
#
# parse Gcode
#

import RPi.GPIO as GPIO
import sys
import re
import logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
import inspect
import math
import pygame
import time
# own modules
from Point3d import Point3d as Point3d
from Motor import Motor as Motor
from Motor import BipolarStepperMotor as BipolarStepperMotor
from Spindle import Spindle as Spindle
from Spindle import Laser as Laser
from Controller import Controller as Controller

# wait for keypress, or wait amount of time
# AUTOMATIC = None
AUTOMATIC = 0.01
# pygame Zoom faktor
ZOOM = 4

class Parser(object):
    """
    Class to parse GCode Text Commands
    """

    def __init__(self):
        # build our controller
        self.controller = Controller(surface=surface)
        self.controller.add_motor("X", BipolarStepperMotor(coils=(4,17,27,22), enable_pin=18, delay=10, max_position=256, min_position=0))
        self.controller.add_motor("Y", BipolarStepperMotor(coils=(24,25,7,8), delay=10, enable_pin=18, max_position=256, min_position=0))
        #self.controller.add_motor("X", Motor())
        #self.controller.add_motor("Y", Motor())
        self.controller.add_motor("Z", Motor())
        self.controller.add_spindle(Laser(power_pin=14))
        # self.controller.add_spindle(Spindle())
        self.last_g_code = None

    def parse_g_params(self, line):
        """parse known Parameters to G-Commands"""
        result = {}
        parameters = ("X", "Y", "Z", "F", "I", "J", "K", "P", "R")
        for parameter in parameters:
            match = re.search("%s([\+\-]?[\d\.]+)\D?" % parameter, line)
            if match:
                result[parameter] = float(match.group(1))
        return(result)

    def parse_m_params(self, line):
        """parse known Parameters to M-Commands"""
        result = {}
        parameters = ("S")
        for parameter in parameters:
            match = re.search("%s([\+\-]?[\d\.]+)\D?" % parameter, line)
            if match:
                result[parameter] = float(match.group(1))
        return(result)

    def caller(self, methodname=None, args=None):
        """
        calls G- or M- code Method

        if no G-Code Method was given, the last methos will be repeated

        fo example G02 results in call of self.controller.G02(args)
        """
        logging.info("Methodname = %s" % methodname)
        if methodname is None:
            methodname = self.last_g_code
        else:
            self.last_g_code = methodname
        method_to_call = getattr(self.controller, methodname)
        method_to_call(args)

    def read(self):
        """
        read input file line by line, and parse gcode Commands
        """
        for line in open("simple_circle.gcode", "rb"):
            # cleanup line
            line = line.strip()
            line = line.upper()
            # filter out some incorrect lines
            if len(line) == 0: continue
            if line[0] == "%": continue
            # start of parsing
            logging.info("-" * 80)
            if line[0] == "(":
                logging.info("Comment: %s", line[1:])
                continue
            logging.info("parsing %s", line)
            # search for M-Codes
            mcodes = re.findall("([m|M][\d|\.]+\D?)", line)
            if len(mcodes) == 1:
                mcode = mcodes[0].strip()
                parameters = self.parse_m_params(line)
                self.caller(mcode, parameters)
                continue
            elif len(mcodes) > 1:
                logging.error("There should only be one M-Code in one line")
            # search for G-Codes
            gcodes = re.findall("([g|G][\d|\.]+\D)", line)
            if len(gcodes) > 1:
                logging.debug("Multiple G-Codes on one line detected")
                for gcode in gcodes:
                    gcode = gcode.strip()
                    logging.info("Found %s", gcode)
                    self.caller(gcode)
            elif len(gcodes) == 1:
                gcode = gcodes[0].strip()
                logging.debug("Only one G-Code %s detected", gcode)
                parameters = self.parse_g_params(line)
                self.caller(gcode, parameters)
            else:
                logging.debug("No G-Code on this line assuming last modal G-Code %s" % self.last_g_code)
                result = self.parse_xyzijf(line)
                self.caller(methodname=None, args=result)
            # pygame drawing and pause after each step
            pygame.display.flip()
            if AUTOMATIC is not None:
                time.sleep(AUTOMATIC)
            else:
                while (pygame.event.wait().type != pygame.KEYDOWN): pass
        # wait for keypress
        while (pygame.event.wait().type != pygame.KEYDOWN): pass


if __name__ == "__main__":
    # bring GPIO to a clean state
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    pygame.init()
    surface = pygame.display.set_mode((400, 400))
    surface.fill((0, 0, 0))
    pygame.display.flip()
    parser = Parser()
    parser.read()
    pygame.quit()
