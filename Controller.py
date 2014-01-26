#/usr/bin/python
# -*- coding: utf-8 -*-
#
# parse Gcode
#

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

# wait for keypress, or wait amount of time
# AUTOMATIC = None
AUTOMATIC = 0.01
# pygame Zoom faktor
ZOOM = 4

class Controller(object):
    """
    Class to receive Gcode Commands and Statements
    and also control a number of motors to do the motion

    Motors up to three
    Spindle -> could be also a laser or something else
    """

    def __init__(self, surface, resolution=1.0, default_speed=1.0, delay=100):
        """
        initialize Controller Object
        @param
        resolution -> 1.0 means 1 step 1 mm
        for our purpose - laser engraver - 256 steps are 36mm so resultion is 36 / 256 = 0,1406
        gcode mm to steps = 1 mm = 256/36 = 
        """
        self.default_speed = default_speed
        self.resolution = resolution
        self.surface = surface
        self.delay = 100 / 10000 # in ms
        # initialize position
        self.position = Point3d(0, 0, 0)
        # defaults to absolute movements
        self.move = self.move_abs
        # defaults to millimeter
        self.unit = "millimeter"
        # motors dict
        self.motors = {}
        self.spindle = None
        self.speed = 0.0
        # pygame specificas to draw correct
        self.pygame_zoom = 1
        self.pygame_draw = True
        self.pygame_color = pygame.Color(255,255,255,255) 

    def get_position(self):
        return(self.position)

    def get_direction(self, number):
        """get direction of number"""
        if number < 0 : return -1
        if number == 0 : return 0
        if number > 0 : return 1

    def add_spindle(self, spindle_object):
        """ add spindle to controller """
        self.spindle = spindle_object

    def add_motor(self, axis, motor_object):
        """ add specific axis motor to controller """
        self.motors[axis] = motor_object

    def G00(self, *args):
        """rapid motion with maximum speed"""
        logging.info("%s called with %s", inspect.stack()[0][3], args)
        data = args[0]
        self.pygame_color = pygame.Color(50, 50, 50, 255)
        self.move(data)
    G0 = G00

    def G01(self, *args):
        """linear motion with given speed"""
        logging.info("%s called with %s", inspect.stack()[0][3], args)
        data = args[0]
        self.pygame_color = pygame.Color(0, 128, 0, 255)
        # self.set_speed(data)
        self.move(data)
    G1 = G01

    def G02(self, *args):
        """clockwise helical motion"""
        logging.info("%s called with %s", inspect.stack()[0][3], args)
        data = args[0]
        self.pygame_color = pygame.Color(0, 0, 255, 255)
        if "F" not in data:
            data["F"] = self.default_speed
        if "P" not in data:
            data["P"] = 1
        assert type(data["P"]) == int
        self.__arc(data, -1)
    G2 = G02

    def G03(self, *args):
        """counterclockwise helical motion"""
        logging.info("%s called with %s", inspect.stack()[0][3], args)
        data = args[0]
        self.pygame_color = pygame.Color(0, 255, 255, 255)
        if "F" not in data:
            data["F"] = self.default_speed
        if "P" not in data:
            data["P"] = 1
        assert type(data["P"]) == int
        self.__arc(data, 1)
    G3 = G03

    def G04(self, *args):
        """Dwell (no motion for P seconds)"""
        logging.info("%s called with %s", inspect.stack()[0][3], args)
        data = args[0]
        time.sleep(data["P"])
    G4 = G04

    def G17(self, *args):
        """Select XY Plane"""
        logging.info("%s called with %s", inspect.stack()[0][3], args)

    def G18(self, *args):
        """Select XZ plane"""
        logging.info("%s called with %s", inspect.stack()[0][3], args)
 
    def G19(self, *args):
        """Select YZ plane"""
        logging.info("%s called with %s", inspect.stack()[0][3], args)
 
    def G20(self, *args):
        """Inches"""
        logging.info("%s called with %s", inspect.stack()[0][3], args)

    def G21(self, *args):
        """Millimeters"""
        logging.info("%s called with %s", inspect.stack()[0][3], args)

    def G54(self, *args):
        """Select coordinate system"""
        logging.info("%s called with %s", inspect.stack()[0][3], args)

    def G90(self, *args):
        """Absolute distance mode"""
        logging.info("%s called with %s", inspect.stack()[0][3], args)
        self.move = self.move_abs

    def G91(self, *args):
        """Incremental distance mode"""
        logging.info("%s called with %s", inspect.stack()[0][3], args)
        self.move = self.move_inc

    def G94(self, *args):
        """Units per minute feed rate"""
        logging.info("%s called with %s", inspect.stack()[0][3], args)

    def M2(self, *args):
        logging.debug("%s called with %s", inspect.stack()[0][3], args)
        logging.info("M2 end the program")
        # back to origin
        self.__goto(Point3d(0, 0, 0))
        # unhold everything
        for axis, motor in self.motors.items():
            motor.unhold()
        # stop spindle
        self.spindle.unhold()
        raise StandardError("M02 received, end of prgram")

    def M3(self, *args):
        logging.debug("%s called with %s", inspect.stack()[0][3], args)
        logging.info("M3 start the spindle clockwise at the speed S")
        data = args[0]
        if "S" not in data :
            self.spindle.rotate(self.spindle.CW)
        else:
            self.spindle.rotate(self.spindle.CW, data["S"])
            
    def M4(self, *args):
        logging.debug("%s called with %s", inspect.stack()[0][3], args)
        logging.info("M4 start the spindle counter-clockwise at the speed S")
        data = args[0]
        if "S" not in data :
            self.spindle.rotate(self.spindle.CCW)
        else:
            self.spindle.rotate(self.spindle.CCW, data["S"])

    def M5(self, *args):
        logging.debug("%s called with %s", inspect.stack()[0][3], args)
        logging.info("M5 stop the spindle")
        data = args[0]
        self.spindle.unhold()

    def M6(self, *args):
        logging.debug("%s called with %s", inspect.stack()[0][3], args)
        logging.info("M6 Tool change")

    def M7(self, *args):
        logging.debug("%s called with %s", inspect.stack()[0][3], args)
        logging.info("M7 turn mist coolant on")

    def M8(self, *args):
        logging.debug("%s called with %s", inspect.stack()[0][3], args)
        logging.info("M8 turn flood coolant on")

    def M9(self, *args):
        logging.debug("%s called with %s", inspect.stack()[0][3], args)
        logging.info("M9 turn all coolant off")

    def __get_center(self, target, radius):
        logging.info("%s called with %s", inspect.stack()[0][3], (target, radius))
        d = target - self.position
        x = d.X
        y = d.Y
        r = radius
        logging.info("x=%s, y=%s, r=%s", x, y, r)
        h_x2_div_d = math.sqrt(4 * r**2 - x**2 - y**2) / math.sqrt(x**2 + y**2)
        i = (x - (y * h_x2_div_d))/2
        j = (y + (x * h_x2_div_d))/2
        return(Point3d(i, j, 0.0))

    def __arc(self, *args):
        """
        given actual position and 
        x, y, z relative position of stop point on arc
        i, j, k relative position of center

        i am not sure if this implementation is straight forward enough
        semms more hacked than methematically correct
        TODO: Improve
        """
        logging.info("%s called with %s", inspect.stack()[0][3], args)
        logging.info("Actual Position at %s", self.position)
        data = args[0]
        ccw = args[1]
        # correct some values if not specified
        if "X" not in data: data["X"] = self.position.X
        if "Y" not in data: data["Y"] = self.position.Y
        if "Z" not in data: data["Z"] = self.position.Z
        if "I" not in data: data["I"] = 0.0
        if "J" not in data: data["J"] = 0.0
        if "K" not in data: data["K"] = 0.0
        target = Point3d(data["X"], data["Y"], data["Z"])
        logging.info("Endpoint of arc at %s", target)
        # either R or IJK are given
        offset = None
        if "R" in data:
            offset = self.__get_center(target, data["R"])
        else:
            offset = Point3d(data["I"], data["J"], data["K"])
        logging.info("Offset = %s", offset)
        center = self.position + offset
        logging.info("Center of arc at %s", center)
        radius = offset.length()
        logging.info("Radius: %s", radius)
        # get the angle bewteen the two vectors
        target_vec = (target - center).unit()
        logging.info("target_vec : %s; angle %s", target_vec, target_vec.angle())
        position_vec = (self.position - center).unit()
        logging.info("position_vec : %s; angle %s", position_vec, position_vec.angle())
        angle = target_vec.angle_between(position_vec)
        logging.info("angle between target and position is %s", target_vec.angle_between(position_vec))
        start_angle = None
        stop_angle = None
        angle_step = math.pi / 180
        if ccw == 1:
            # G3 movement
            # angle step will be added
            # target angle should be greater than position angle
            # if not so correct target_angle = 2 * math.pi - target_angle 
            if target_vec.angle() < position_vec.angle():
                start_angle = position_vec.angle()
                stop_angle = 2 * math.pi - target_vec.angle()
            else:
                start_angle = position_vec.angle()
                stop_angle = target_vec.angle()
        else:
            # G2 movement
            # so clockwise, step must be negative
            # target angle should be smaller than position angle
            # if not correct target_angle = 2 * math.pi - target_angle
            angle_step = -angle_step
            # should go from position to target
            if target_vec.angle() > position_vec.angle():
                start_angle = position_vec.angle()
                stop_angle = 2 * math.pi - target_vec.angle()
            else:
                start_angle = position_vec.angle()
                stop_angle = target_vec.angle()
        # this indicates a full circle
        if start_angle == stop_angle:
            stop_angle += math.pi * 2
        angle_steps = abs(int((start_angle - stop_angle) / angle_step))
        logging.info("Arc from %s rad to %s rad with %s steps in %s radians", start_angle, stop_angle, angle_steps, angle_step)
        inv_offset = offset * -1
        logging.error("Inverse Offset vector : %s", inv_offset)
        angle = angle_step * angle_steps
        while abs(angle) > abs(angle_step):
            inv_offset = inv_offset.rotated_Z(angle_step)
            self.__goto(center + inv_offset)
            angle -= angle_step
            logging.error("angle=%s, start_angle=%s, stop_angle=%s", start_angle + angle, start_angle, stop_angle)
        # rotate last tiny fraction left
        inv_offset = inv_offset.rotated_Z(angle_step)
        self.__goto(center + inv_offset)
        # calculate drift of whole arc
        arc_drift = self.position - target
        logging.error("Arc-Drift: Actual=%s, Target=%s, Drift=%s(%s)", self.position, target, arc_drift, arc_drift.length())
        assert arc_drift.length() < Point3d(1.0, 1.0, 1.0).length()
        self.__drift_management(target)

    def __drift_management(self, target):
        """can be called to get closer to target"""
        drift = self.position - target
        logging.error("Drift-Management-before: Actual=%s, Target=%s, Drift=%s(%s)", self.position, target, drift, drift.length())
        assert drift.length() < Point3d(1.0, 1.0, 1.0).length()
        self.__goto(target)
        drift = self.position - target
        logging.error("Drift-Management-after: Actual=%s, Target=%s, Drift=%s(%s)", self.position, target, drift, drift.length())
        assert drift.length() < Point3d(1.0, 1.0, 1.0).length()

    def __step(self, *args):
        """
        method to initialize single steps on the different axis
        the size here is already steps, not units as mm or inches
        scaling is done in __goto
        """
        logging.debug("%s called with %s", inspect.stack()[0][3], args)
        data = args[0]
        for axis in ("X", "Y", "Z"):
            step = data.__dict__[axis]
            assert -1.0 <= step <= 1.0
            if step == 0.0 : 
                continue
            direction = self.get_direction(step)
            self.motors[axis].move_float(direction, abs(step))

    def __goto(self, target):
        """
        calculate vector between actual position and target position
        scale this vector to motor-steps-units und split the
        vector in unit vectors with length 1, to control single motor steps
        """
        logging.debug("%s called with %s", inspect.stack()[0][3], target)
        logging.debug("moving from %s mm to %s mm", self.position, target)
        logging.debug("moving from %s steps to %s steps", self.position * self.resolution, target * self.resolution)
        move_vec = target - self.position
        if move_vec.length() == 0.0:
            logging.info("move_vec is zero, nothing to draw")
            # no movement at all
            return
        move_vec_unit = move_vec.unit()
        # steps on each axes to move
        # scale from mm to steps
        move_vec_steps = move_vec * self.resolution
        move_vec_steps_unit = move_vec_steps.unit()
        #logging.error("move_vec_steps_unit=%s", move_vec_steps_unit)
        #logging.error("scaled %s mm to %s steps", move_vec, move_vec_steps)
        length_unit = move_vec_steps_unit.length()
        length = move_vec_steps.length()
        #logging.error("move_vec_steps.length() = %s", move_vec_steps.length())        
        # use while loop the get to the exact value
        while move_vec_steps.length() > 1.0:
            self.__step(move_vec_steps_unit)
            #logging.error("actual length left to draw in tiny steps: %f", move_vec_steps.length())
            move_vec_steps = move_vec_steps - move_vec_steps_unit
        # the last fraction left
        self.__step(move_vec_steps)
        if self.surface is not None:
            self.pygame_update(target)
        self.position = target
        # after move check controller position with motor positions
        motor_position = Point3d(self.motors["X"].get_position(), self.motors["Y"].get_position(), self.motors["Z"].get_position())
        drift = self.position * self.resolution - motor_position
        logging.debug("Target Drift: Actual=%s; Target=%s; Drift=%s", self.position, target, self.position - target)
        logging.debug("Steps-Drift : Motor=%s; Drift %s length=%s; Spindle: %s", \
            motor_position, drift, drift.length(), self.spindle.get_state())
        # drift should not be more than 1 step
        # drift could be in any direction 0.999...
        assert drift.length() < Point3d(1.0, 1.0, 1.0).length()
        #logging.info("Unit-Drift: Motor: %s; Drift %s; Spindle: %s", \
        #    motor_position / self.resolution, self.position - motor_position / self.resolution, self.spindle.get_state())

    def pygame_update(self, newposition):
        pan_x = self.surface.get_width() / 2
        pan_y = self.surface.get_height() / 2
        start = (self.resolution* self.position.X, self.resolution * self.position.Y)
        stop = (self.resolution * newposition.X, self.resolution * newposition.Y)
        color = pygame.Color(0, 50, 0, 255)
        if self.motors["Z"].position < 0:
            color = pygame.Color(0, 0, 255, 255)
        if self.pygame_draw:
            pygame.draw.line(self.surface, self.pygame_color, start, stop, 1)
        # set red dot at motor position
        self.surface.set_at((self.motors["X"].position, self.motors["Y"].position), pygame.Color(255,0,0,255))
        pygame.display.flip()

    def set_speed(self, *args):
        """
        set speed, if data["F"] is given, defaults to default_speed if not specified
        """
        data = args[0]
        if "F" in data:
            self.speed = data["F"]
        else:
            self.speed = self.default_speed

    def move_inc(self, stepx, stepy):
        """
        incremental movement, parameter represents relative position change
        move to given x,y ccordinates
        x,y are given relative to actual position

        so to move in both direction at the same time,
        parameter x or y has to be sometime float
        """
        data = args[0]
        target = Point3d(0, 0, 0)
        for axis in ("X", "Y", "Z"):
            if axis in data:
                target.__dict__[axis] = self.position.__dict__[axis] + data[axis]
            else:
                target.__dict__[axis] = self.position.__dict__[axis]
        logging.info("target = %s", target)
        self.__goto(target)

    def move_abs(self, *args):
        """
        absolute movement to position
        args[X,Y,Z] are interpreted as absolute positions
        it is not necessary to give alle three axis, when no value is
        present, there is not movement on this axis
        """
        logging.info("%s called with %s", inspect.stack()[0][3], args)
        data = args[0]
        if data is None: return
        target = Point3d(0.0, 0.0, 0.0)
        for axis in ("X", "Y", "Z"):
            if axis in data:
                target.__dict__[axis] = data[axis]
            else:
                target.__dict__[axis] = self.position.__dict__[axis]
        logging.info("target = %s", target)
        self.__goto(target)

    def __getattr__(self, name):
        def method(*args):
            logging.info("tried to handle unknown method " + name)
            if args:
                logging.info("it had arguments: " + str(args))
        return method

