#!/usr/bin/python

import subprocess
import re
import os

class DHT(object):
    """reads data from DHT11 Sensor at given GPIO Pin"""

    def __init__(self, gpiopin):
        self.gpiopin = gpiopin
        self.binary = "./Adafruit_DHT"
        if not os.path.isfile(self.binary):
            raise(StandardError("Adafruit_DHT Binary not in current directory"))

    def read_dht11(self, type=11):
        # Run the DHT program to get the humidity and temperature readings!
        # first parameter sensor type, second GPIO Port
        output = subprocess.check_output([self.binary, str(type), str(self.gpiopin)]);
        temp = None
        humidity = None
        matches = re.search("Temp =\s+([0-9.]+)", output)
        if matches is not None:
            temp = float(matches.group(1))
        matches = re.search("Hum =\s+([0-9.]+)", output)
        if matches is not None:
            humidity = float(matches.group(1))
        return({"temp" : temp, "humidity" : humidity})
