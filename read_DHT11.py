#!/usr/bin/python

import subprocess
import re
import sys
import time
import datetime


# Continuously append data
while(True):
  # Run the DHT program to get the humidity and temperature readings!

  # first parameter sensor type, second GPIO Port
  output = subprocess.check_output(["./Adafruit_DHT", "11", "22"]);
  print output
  matches = re.search("Temp =\s+([0-9.]+)", output)
  if (not matches):
	time.sleep(3)
	continue
  temp = float(matches.group(1))
  
  # search for humidity printout
  matches = re.search("Hum =\s+([0-9.]+)", output)
  if (not matches):
	time.sleep(3)
	continue
  humidity = float(matches.group(1))

  print "Temperature: %.1f C" % temp
  print "Humidity:    %.1f %%" % humidity
 
  time.sleep(30)
