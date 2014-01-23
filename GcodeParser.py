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

"""
Changelog

problem in goto, to determine how many steps have to be done

failure in get_center, something under sqrt goes negative
"""


class Motor(object):
    """Abstract Class for Motor"""

    def __init__(self):
        self.float_position = 0.0
        self.position = 0

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
        logging.debug("Moving Motor One steps in direction %s", direction)
        logging.debug("Motor accuracy %s +/- %s", self.position, self.float_position)
        self.position += direction

    def unhold(self):
        logging.info("Unholding Motor Coils")


class Point3d(object):
    """
    three dimension vetor representation
    """

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.X = float(x)
        self.Y = float(y)
        self.Z= float(z)

    def __repr__(self):
        return("Point3d(%s, %s, %s)" % (self.X, self.Y, self.Z))

    def __str__(self):
        return("(%s, %s, %s)" % (self.X, self.Y, self.Z))

    def __add__(self, other):
        return(Point3d(self.X + other.X, self.Y + other.Y, self.Z + other.Z))

    def __iadd__(self, other):
        self.X += other["X"]
        self.Y += other["Y"]
        self.Z += other["Z"]

    def __sub__(self, other):
        return(Point3d(self.X - other.X, self.Y - other.Y, self.Z - other.Z))

    def __isub__(self, other):
        self.X -= other["X"]
        self.Y -= other["Y"]
        self.Z -= other["Z"]

    def __mul__(self, scalar):
        return(Point3d(self.X * scalar, self.Y * scalar, self.Z * scalar))

    def __imul__(self, scalar):
        self.X *= scalar
        self.Y *= scalar
        self.Z *= scalar

    def __div__(self, scalar):
        return(Point3d(self.X / scalar, self.Y / scalar, self.Z / scalar))

    def __idiv__(self, scalar):
        self.X /= scalar
        self.Y /= scalar
        self.Z /= scalar

    def perpendicular2d(self):
        """
        return perpendicular vetor in XY Plane
        """
        return(Point3d(-self.Y, self.X, self.Z))

    def length(self):
        return(math.sqrt(self.X**2 + self.Y**2 + self.Z**2))

    def __old__length2d(self):
        """
        DEPRECATED return length in XY Plane
        """
        length = math.sqrt(self.X ** 2 + self.Y ** 2)
        return(length)

    def unit(self):
        length = self.length()
        return(Point3d(self.X / length, self.Y / length, self.Z / length))

    def __old_unit2d(self):
        """
        DEPRECATED return unit vector in XY Plane
        """
        length = self.length2d()
        return(Point3d(self.X / length, self.Y / length, self.Z / length))

    def product(self, other):
        """
        returns the cross product of self with other
        a = self
        b = other

        cx = ay * bz - az * by
        cy = az * bx - ax * bz
        cz = ax * by - ay * bx
        
        the returned vector is orthogonal to the plan a,b
        """
        cx = self.Y * other.Z - self.Z * other.Y
        cy = self.Z * other.X - self.X * other.Z
        cz = self.X * other.Y - self.Y * other.X
        return(Point3d(xy, cy, cz))


    def rotated_Z(self, theta):
        """
        return rotated version of self around Z-Axis
        theta should be given in radians
        http://stackoverflow.com/questions/14607640/rotating-a-vector-in-3d-space
        |cos θ   -sin θ   0| |x|   |x cos θ - y sin θ|   |x'|
        |sin θ    cos θ   0| |y| = |x sin θ + y cos θ| = |y'|
        |  0       0      1| |z|   |        z        |   |z'|
        """
        xr = self.X * math.cos(theta) - self.Y * math.sin(theta)
        yr = self.X * math.sin(theta) + self.Y * math.cos(theta)
        zr = self.Z
        return(Point3d(xr, yr, zr))

    def rotated_Y(self, theta):
        """
        return rotated version of self around Y-Axis
        theta should be given in radians
        http://stackoverflow.com/questions/14607640/rotating-a-vector-in-3d-space
        | cos θ    0   sin θ| |x|   | x cos θ + z sin θ|   |x'|
        |   0      1       0| |y| = |         y        | = |y'|
        |-sin θ    0   cos θ| |z|   |-x sin θ + z cos θ|   |z'|
        """
        xr = self.X * math.cos(theta) + self.Z * math.sin(theta)
        yr = self.Y
        zr = (-1) * self.X * math.sin(theta) + self.Z * math.cos(theta)
        return(Point3d(xr, yr, zr))

    def rotated_X(self, theta):
        """
        return rotated version of self around X-Axis
        theta should be given in radians
        http://stackoverflow.com/questions/14607640/rotating-a-vector-in-3d-space
        |1     0           0| |x|   |        x        |   |x'|
        |0   cos θ    -sin θ| |y| = |y cos θ - z sin θ| = |y'|
        |0   sin θ     cos θ| |z|   |y sin θ + z cos θ|   |z'|
        """
        xr = self.X
        yr = self.Y * math.cos(theta) - self.Z * math.sin(theta)
        zr = self.Y * math.sin(theta) + self.Z * math.cos(theta)
        return(Point3d(xr, yr, zr))

    def _old_rotate2d(self, radians):
        """ DEPRECATED """
        cos = math.cos(radians)
        sin = math.sin(radians)
        x = self.x * cos - self.y * sin
        y = self.x * sin + self.y * cos
        self.x = x
        self.y = y

    def _old_rotated2d(self, radians):
        """
        rotate self number of radians clockwise, and return new object
        """
        cos = math.cos(radians)
        sin = math.sin(radians)
        new_x = self.X * cos - self.Y * sin
        new_y = self.X * sin + self.Y * cos
        new_z = self.Z
        return(Point3d(new_x, new_y, new_z))

    def _old_normalized(self):
        """
        normalize -> the greteast value = 1 all other are scaled
        """
        max_value = max(abs(self.X), abs(self.Y), abs(self.Z))
        if max_value == 0:
            return(Point3d(0.0, 0.0, 0.0))
        return(Point3d(self.X / max_value, self.Y / max_value, self.Z / max_value))

    def dot(self, other):
        """
        Dot Product of two vectors with the same number of items
        """
        return(self.X * other.X + self.Y * other.Y + self.Z * other.Z)

    def angle(self):
        """
        which angle does this vector has, from his origin
        """
        add_angle = 0
        # corect angle if in 3rd or 4th quadrant
        if self.Y < 0 :
            return(2 * math.pi - math.acos(self.X))
        else:
            return(math.acos(self.X))

    def angle_between(self, other):
        """
        angle between self and other vector
        """
        return(math.acos(self.dot(other)))

class Controller(object):
    """
    Class to receive Gcode Commands and Statements
    and also control a number of motors to do the motion
    """

    def __init__(self, resolution=1.0, default_speed=1.0):
        """
        initialize Controller Object
        @param
        resolution -> step to millimeter or default
        """
        self.default_speed = default_speed
        self.resolution = resolution
        # initialize position
        self.position = Point3d(0, 0, 0)
        # defaults to absolute movements
        self.move = self.move_abs
        # defaults to millimeter
        self.unit = "millimeter"
        # how many steps represent 1 mm
        self.step_factor = int(256 / 32)
        # motors dict
        self.motors = {}
        # pygame specificas to draw correct
        self.pygame_zoom = 0.5
        self.pygame_draw = True
        self.pygame_color = pygame.Color(255,255,255,255) 
        self.draw_grid()

    def get_direction(self, number):
        """get direction of number"""
        if number < 0 : return -1
        if number == 0 : return 0
        if number > 0 : return 1

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
        self.set_speed(data)
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

    def M3(self, *args):
        logging.debug("%s called with %s", inspect.stack()[0][3], args)
        logging.info("M3 start the spindle clockwise at the speed S")

    def M4(self, *args):
        logging.debug("%s called with %s", inspect.stack()[0][3], args)
        logging.info("M4 start the spindle counter-clockwise at the speed S")

    def M5(self, *args):
        logging.debug("%s called with %s", inspect.stack()[0][3], args)
        logging.info("M5 stop the spindle")

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

    def __to_angle(self, offset):
        """
        takes position i and j and returns angle
        """
        logging.info("%s called with %s", inspect.stack()[0][3], offset)
        if (offset.X == 0) and (offset.Y == 0):
            return(math.pi * 2)
        else:
            angle = math.acos(offset.X)
            if offset.Y <= 0:
                angle += math.pi
            return(angle)

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

    def float_iter(self, start, stop, stepsize):
        steps = abs(stop - start) / stepsize
        if stop < start and stepsize > 0:
            stepsize = -stepsize
        for _ in range(steps):
            yield start
            start += stepsize

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
        logging.info("Arc from %s rad to %s rad wtih %s steps in %s radians", start_angle, stop_angle, angle_steps, angle_step)
        angle = 0
        inv_offset = offset * -1
        logging.error("Inverse Offset vector : %s", inv_offset)
        for _ in range(angle_steps):
            newposition = center + inv_offset.rotated_Z(angle)
            self.__goto(newposition)
            angle += angle_step
        if self.position != target:
            logging.error("Actual Position %s should be %s, correcting", self.position, target)
            self.position = target

    def __step(self, *args):
        """
        method to initialize single steps on the different axis
        """
        data = args[0]
        for axis in ("X", "Y", "Z"):
            step = data[axis]
            direction = self.get_direction(step)
            motor_steps = abs(step) * self.step_factor
            logging.debug(" %s scaling from %s mm to %s step in direction %s ", axis, abs(step), motor_steps, direction)
            self.motors[axis].move_float(direction, abs(step) * self.step_factor)

    def __goto(self, newposition):
        """
        method to move to position given
        position is absolute
        """
        logging.debug("moving from %s to %s", self.position, newposition)
        length_x = self.position.X - newposition.X
        length_y = self.position.Y - newposition.Y
        length_z = self.position.Z - newposition.Z
        max_length = max(abs(length_x), abs(length_y), abs(length_z))
        logging.debug("max_length: %s", max_length)
        if max_length == 0:
            logging.info("No Movement detected")
            # no movement at all
            return
        # steps on each axes to move
        step_x = self.step_factor * length_x / max_length
        step_y = self.step_factor * length_y / max_length
        step_z = self.step_factor * length_z / max_length
        data =  { "X":step_x, "Y":step_y, "Z":step_z}
        logging.debug(data)
        for _ in range(int(self.step_factor * max_length)):
            self.__step({ "X":step_x, "Y":step_y, "Z":step_z})
        self.pygame_update(newposition)
        self.position = newposition

    def draw_grid(self):
        color = pygame.Color(0, 50, 0, 255)
        for x in range(0, surface.get_height(), 10):
            pygame.draw.line(surface, color, (x, 0), (x, surface.get_height()), 1)
        for y in range(0, surface.get_width(), 10):
            pygame.draw.line(surface, color, (0, y), (surface.get_width(), y), 1)
        color = pygame.Color(0, 100, 0, 255)
        pygame.draw.line(surface, color, (surface.get_width() / 2, 0), (surface.get_width() / 2, surface.get_height()))
        pygame.draw.line(surface, color, (0, surface.get_height() / 2), (surface.get_width(), surface.get_height() / 2))

    def pygame_update(self, newposition):
        centerx = surface.get_width() / 2
        centery = surface.get_height() / 2
        color = pygame.Color(255, 255, 255, 255)
        start = (self.pygame_zoom * self.position.X + centerx, centery - self.pygame_zoom * self.position.Y)
        stop = (self.pygame_zoom * newposition.X + centerx, centery - self.pygame_zoom * newposition.Y)
        logging.debug("Line from %s to %s", start, stop)
        if self.pygame_draw:
            pygame.draw.line(surface, self.pygame_color, start, stop, 1)
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
        newposition = Point3d(0, 0, 0)
        for axis in ("X", "Y", "Z"):
            if axis in data:
                newposition.__dict__[axis] = self.position.__dict__[axis] + data[axis]
            else:
                newposition.__dict__[axis] = self.position.__dict__[axis]
        logging.info("New Position = %s", newposition)
        self.__goto(newposition)

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
        newposition = Point3d(0, 0, 0)
        for axis in ("X", "Y", "Z"):
            if axis in data:
                newposition.__dict__[axis] = data[axis]
            else:
                newposition.__dict__[axis] = self.position.__dict__[axis]
        logging.info("New Position = %s", newposition)
        self.__goto(newposition)

    def __getattr__(self, name):
        def method(*args):
            logging.info("tried to handle unknown method " + name)
            if args:
                logging.info("it had arguments: " + str(args))
        return method


class Parser(object):
    """
    Class to parse GCode Text Commands
    """

    def __init__(self):
        self.controller = Controller()
        self.controller.add_motor("X", Motor())
        self.controller.add_motor("Y", Motor())
        self.controller.add_motor("Z", Motor())
        self.last_g_code = None

    def parse_xyzijf(self, line):
        result = {}
        parameters = ("X", "Y", "Z", "F", "I", "J", "K", "P", "R")
        for parameter in parameters:
            match = re.search("%s([\+\-]?[\d\.]+)\D?" % parameter, line)
            if match:
                result[parameter] = float(match.group(1))
        return(result)

    def caller(self, methodname=None, args=None):
        logging.info("Methodname = %s" % methodname)
        if methodname is None:
            methodname = self.last_g_code
        else:
            self.last_g_code = methodname
        method_to_call = getattr(self.controller, methodname)
        method_to_call(args)

    def read(self):
        for line in open("spiral.ngc", "rb"):
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
            # controller
            # some status variables
            logging.info("parsing %s", line)
            mcodes = re.findall("([m|M][\d|\.]+\D?)", line)
            if len(mcodes) == 1:
                mcode = mcodes[0].strip()
                self.caller(mcode)
                continue
            else:
                logging.error("There should only be one M-Code in one line")
            gcodes = re.findall("([g|G][\d|\.]+\D)", line)
            if len(gcodes) > 1:
                logging.debug("Multiple G-Codes on one line detected")
                for gcode in gcodes:
                    gcode = gcode.strip()
                    logging.info("Found %s", gcode)
                    self.caller(gcode)
            elif len(gcodes) == 1:
                # G Command
                gcode = gcodes[0].strip()
                logging.debug("Only one G-Code %s detected", gcode)
                result = self.parse_xyzijf(line)
                self.caller(gcode, result)
            else:
                logging.debug("No G-Code on this line assuming last modal G-Code %s" % self.last_g_code)
                result = self.parse_xyzijf(line)
                self.caller(methodname=None, args=result)
            pygame.display.flip()
            while (pygame.event.wait().type != pygame.KEYDOWN): pass
        while (pygame.event.wait().type != pygame.KEYDOWN): pass


if __name__ == "__main__":
    pygame.init()
    surface = pygame.display.set_mode((400, 400))
    surface.fill((0, 0, 0))
    pygame.display.flip()
    parser = Parser()
    parser.read()
    pygame.quit()
