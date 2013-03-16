#!/usr/bin/python

import time
import os
import sys
from MCP3008 import MCP3008 as MCP3008
from OneWire import OneWire as OneWire
from DHT import DHT as DHT

# Pin Layout for mcp3008 ADC
SCLK        = 18 # Serial Clock
MOSI        = 24 # Master-Out Slave-IN
MISO        = 23 # Master-In Slave-Out
CS          = 25 # Chip-Select

def main():
    mcp3008 = MCP3008(SCLK, MOSI, MISO, CS)
    onewire = OneWire()
    dht = DHT(22)
    while True:
        print "-" * 80
        print "TMP36-1   : %f C" % mcp3008.read_tmp36(0)
        print "Photocell : %f" % mcp3008.read_photocell(1)
        print "TMP36-2   : %f C" % mcp3008.read_photocell(2)
        print "IR-SENSOR : %f" % mcp3008.read_ir_sensor(3)
        print "DS18B20   : %f C" % onewire.get_ds18b20_temp("28-000004474ba7")
        dht11 = dht.read_dht11()
        print "DHT11 Temp: %(temp)s C" % dht11
        print "DHT11 Hum : %(humidity)s %%" % dht11
        time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
