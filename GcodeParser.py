#/usr/bin/python
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
"""


example_gcode = [
"G17 G20 G90 G94 G54",
"G0 Z0.25",
"X-0.5 Y0.",
"Z0.1",
"G01 Z0. F5.",
"G02 X0. Y0.5 I0.5 J0. F2.5",
"X0.5 Y0. I0. J-0.5",
"X0. Y-0.5 I-0.5 J0.",
"X-0.5 Y0. I0. J0.5",
"G01 Z0.1 F5.",
"G00 X0. Y0. Z0.25"
]


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
        logging.info("Moving Motor One steps in direction %s", direction)
        logging.info("Motor accuracy %s +/- %s", self.position, self.float_position)
        self.position += direction

    def unhold(self):
        logging.info("Unholding Motor Coils")


class Point3d(object):

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

    def perpendicular_z(self):
        return(Point3d(-self.Y, self.X, self.Z))

    def length_z(self):
        # get length in X-Y plane
        length = math.sqrt(self.X ** 2 + self.Y ** 2)
        return(length)

    def unit_z(self):
        """ return unit vector in X-Y Plane """
        length = self.length_z()
        return(Point3d(self.X / length, self.Y / length, self.Z / length))

    def rotate_around_z(self, radians):
        cos = math.cos(radians)
        sin = math.sin(radians)
        x = self.x * cos - self.y * sin
        y = self.x * sin + self.y * cos
        self.x = x
        self.y = y

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
        self.move(data)
    G0 = G00

    def G01(self, *args):
        """linear motion with given speed"""
        logging.info("%s called with %s", inspect.stack()[0][3], args)
        data = args[0]
        self.set_speed(data)
        self.move(data)
    G1 = G01

    def G02(self, *args):
        """clockwise helical motion"""
        logging.info("%s called with %s", inspect.stack()[0][3], args)
        data = args[0]
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

    def __to_angle(self, i, j):
        """
        takes position i and j and returns angle
        """
        angle = 0
        if j < 0:
            angle = math.pi
        angle += math.acos(i)
        return(angle)

    def __get_center(self, point1, point2, radius):
        """
        return center point and i, j, k, points to point 1
        """
        logging.info("%s called with %s", inspect.stack()[0][3], (point1, point2, radius))
        assert type(point1) == Point3d
        assert type(point2) == Point3d
        # calculate vector c between point a and point b
        vector_c = (point1 - point2)
        logging.info("vector_c=%s", vector_c)
        # get height from vector c to center
        logging.info("radius=%s", radius)
        logging.info("length(vector_c)/2=%s", vector_c.length_z() / 2)
        height = math.sqrt(radius ** 2 - (vector_c.length_z() ** 2 ) / 4)
        # calculate point c
        point_c = point1 + vector_c * 0.5 
        # perpendicular to this point in distance r
        vector_d = vector_c.perpendicular_z()
        # get the unit vector of vector_d
        vector_d_u = vector_d.unit_z()
        # multiply with radius and add to point_c
        center = point_c + vector_d_u * height
        logging.info("Found center at %s", center)
        ijk = point1 - center
        logging.info("Vector from point to center %s", ijk)
        return(ijk)


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
        data = args[0]
        ccw = args[1]
        x1 = data["X"]
        y1 = data["Y"]
        if "Z" in data:
            z1 = data["Z"]
        else:
            z1 = self.position.Z
        end_position = Point3d(x1, y1, z1)
        i = j = k = 0.0
        # either R or IJK are given
        if "R" in data:
            ijk = self.__get_center(self.position, end_position, data["R"])
            i = ijk.X
            j = ijk.Y
            k = ijk.Z
        else:
            i = data["I"]
            j = data["J"]
            if "K" in data:
                k = data["K"]
        center = Point3d(self.position.X+i, self.position.Y+j, self.position.Z+k)
        radius = math.sqrt(x1 ** 2 + y1 ** 2)
        start_angle = self.__to_angle(i / radius, j / radius)
        stop_angle = self.__to_angle(x1 / radius, y1 / radius)
        arc_step = math.pi / 180
        angle_steps = abs(int((start_angle - stop_angle) / arc_step))
        logging.info("Actual Position at %s", self.position)
        logging.info("Center of arc at %s", center)
        logging.info("Endpoint of arc at %s", end_position)
        logging.info("Radius: %s", radius)
        logging.info("Arc from %s rad to %s rad", start_angle, stop_angle)
        logging.info("needing %d steps of %s rad", angle_steps, arc_step)
        direction = 1
        # in wich direction should i count the angle up
        if start_angle < stop_angle:
            direction = -1
        angle = start_angle
        for _ in range(angle_steps):
            # if G02 counter clockwise
            newposition = Point3d(radius * math.cos(angle), radius * math.sin(angle))
            self.__goto(newposition + center)
            logging.debug("Angle %s rad position %s", angle, newposition)
            angle += arc_step * direction * ccw
        logging.info("Actual Position %s should be %s", self.position, end_position)

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

    def pygame_update(self, newposition):
        centerx = surface.get_width() / 2
        centery = surface.get_height() / 2
        zoom = 100
        color = pygame.Color(255, 255, 255, 255)
        start = (zoom * self.position.X + centerx, zoom * self.position.Y + centery)
        stop = (zoom * newposition.X + centerx, zoom * newposition.Y + centery)
        logging.info("Line from %s to %s", start, stop)
        pygame.draw.line(surface, pygame.Color(255, 255, 255, 255), start, stop, 1)
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
        if methodname is None:
            methodname = self.last_g_code
        else:
            self.last_g_code = methodname
        method_to_call = getattr(self.controller, methodname)
        method_to_call(args)

    def read(self):
        for line in open("simple.ngc", "rb"):
            logging.info("-" * 80)
            # controller
            # some status variables
            line = line.upper()
            logging.info("parsing %s", line)
            gg = re.findall("([g|G][\d|\.]+\D)", line)
            if len(gg) > 1:
                logging.debug("Multiple G-Codes on one line detected")
                for g_code in gg:
                    g_code = g_code.strip()
                    logging.info("Found %s", g_code)
                    self.caller(g_code)
            elif len(gg) == 1:
                # G Command
                g_code = gg[0].strip()
                logging.debug("Only one G-Code %s detected", g_code)
                result = self.parse_xyzijf(line)
                self.caller(g_code, result)
            else:
                logging.debug("No G-Code on this line assuming %s" % self.last_g_code)
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
