#/usr/bin/python
#
# parse Gcode
#

import re
import logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
import inspect


class Controller(object):

    def g0(self, data):
        pass

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

class Point3d(object):

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __repr__(self):
        return("Point3d(%s, %s, %s)" % (self.x, self.y, self.z))

    def __str__(self):
        return("X=%s, Y=%s, Z=%s" % (self.x, self.y, self.z))

    def __add__(self, rel_dict):
        self.x += rel_dict["x"]
        self.y += rel_dict["y"]
        self.z += rel_dict["z"]

class Controller(object):

    def __init__(self):
        self.position = Point3d(0, 0, 0)

    def G00(self, *args):
        """rapid motion"""
        logging.info("%s called with %s", inspect.stack()[0][3], args)
    G0 = G00

    def G01(self, *args):
        """coordinated motion"""
        logging.info("%s called with %s", inspect.stack()[0][3], args)
    G1 = G01

    def G02(self, *args):
        """coordinated helical motion"""
        logging.info("%s called with %s", inspect.stack()[0][3], args)
    G2 = G02

    def G03(self, *args):
        """coordinated helical motion"""
        logging.info("%s called with %s", inspect.stack()[0][3], args)
    G3 = G03

    def G04(self, *args):
        """Dwell (no motion for P seconds)"""
        logging.info("%s called with %s", inspect.stack()[0][3], args)
        time.sleep(args["P"])
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

    def G91(self, *args):
        """Incremental distance mode"""
        logging.info("%s called with %s", inspect.stack()[0][3], args)

    def G94(self, *args):
        """Units per minute feed rate"""
        logging.info("%s called with %s", inspect.stack()[0][3], args)

    def __getattr__(self, name):
        def method(*args):
            logging.info("tried to handle unknown method " + name)
            if args:
                logging.info("it had arguments: " + str(args))
        return method

class Parser(object):

    def __init__(self):
        self.controller = Controller()
        self.last_g_code = None

    def parse_xyzijf(self, line):
        result = {}
        parameters = ("X", "Y", "Z", "F", "I", "J")
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
        for line in example_gcode:
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

if __name__ == "__main__":
    parser = Parser()
    parser.read()
