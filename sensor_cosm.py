#!/usr/bin/python

import time
import os
import sys
import eeml
import eeml.datastream
import eeml.unit
# own modules
from MCP3008 import MCP3008 as MCP3008
from OneWire import OneWire as OneWire
from DHT import DHT as DHT

# COSM
# parameters
API_KEY = "4v8OWsHw-K6NI2srUZ2j3Mg7CfaSAKxqS0x4bjV2cmp6VT0g"
API_URL = "/v2/feeds/82543.xml"

# Pin Layout for mcp3008 ADC
SCLK        = 18 # Serial Clock
MOSI        = 24 # Master-Out Slave-IN
MISO        = 23 # Master-In Slave-Out
CS          = 25 # Chip-Select

# DS18B20 Sensor ID
OW_SENSOR = "28-000004474ba7"

def main():
    mcp3008 = MCP3008(SCLK, MOSI, MISO, CS)
    onewire = OneWire()
    dht = DHT(22)
    while True:
        tmp36_temp = mcp3008.read_tmp36(0)
        try:
            ds18b20_temp = onewire.get_ds18b20_temp(OW_SENSOR)
        except StandardError:
            ds18b20_temp = None
        dht11 = dht.read_dht11()
        cpu_temp = float(int(open("/sys/class/thermal/thermal_zone0/temp", "r").read())/1000)
        pac = eeml.datastream.Cosm(API_URL, API_KEY)
        pac.update([
            eeml.Data(0, tmp36_temp, unit=eeml.unit.Celsius()), 
            eeml.Data(1, ds18b20_temp, unit=eeml.unit.Celsius()),
            eeml.Data(2, dht11["temp"], unit=eeml.unit.Celsius()),
            eeml.Data(3, dht11["humidity"]),
            eeml.Data(4, cpu_temp, unit=eeml.unit.Celsius()),
        ])
        try:
            pac.put()
        except StandardError:
            print "Exception on pac.put()"
        time.sleep(60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
