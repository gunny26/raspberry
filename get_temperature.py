#!/usr/bin/python

import ow
import eeml

# parameters
API_KEY = "4v8OWsHw-K6NI2srUZ2j3Mg7CfaSAKxqS0x4bjV2cmp6VT0g"
API_URL = "/v2/feeds/82543.xml"

# 1-wire sensors
ow.use_logging = True
ow.init("/dev/ttyUSB0")
sensors = ow.Sensor("/").sensorList()
#print sensors
s1 = ow.Sensor("/28.0EA745020000")
#print s1.entryList()
sensor_temp_1 = float(s1.temperature.strip())
ow.finish()
# print "Sensor Temperature: %s" % temperature
cpu_temp = float(int(open("/sys/class/thermal/thermal_zone0/temp", "r").read())/1000)
# print "CPU Temperature: %s" % cpu_temp
pac = eeml.Cosm(API_URL, API_KEY)
pac.update([eeml.Data(0, sensor_temp_1, unit=eeml.Celsius()), eeml.Data(1, cpu_temp, unit=eeml.Celsius())])
pac.put()
