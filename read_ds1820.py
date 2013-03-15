#!/usr/bin/python

import time
import os
import sys
# import kernel modules needed for 1-wire devies at GPIO #4
os.system("sudo modprobe w1-gpio")
os.system("sudo modprobe w1-therm")

def get_ds18b20_temp(serialnum):
    """reads temperature in celsius from ds18b20 at GPIO #4"""
    filename = os.path.join("/sys/bus/w1/devices", serialnum, "w1_slave")
    for i in range(5):
        tfile= open(filename)
        text = tfile.read()
        tfile.close()
        secondline = text.split("\n")[1]
        temperaturedata= secondline.split(" ")[9]
        temperature = float(temperaturedata[2:])
        temperature = temperature / 1000
        firstline = text
        ccrrcc = firstline.split(" ")[11]
        ccrrcc = (ccrrcc[:3]) #take only first 3 characters
        global noflag
        noflag = 0
        if ccrrcc != 'YES':
            print ' NO NO NO NO NO NO NO NO NO NO NO'
            print _serialnum
            noflag = 1
	return(temperature)

def main():
    while True:
        print "-" * 80
        print "DS18B20  : ", get_ds18b20_temp("28-000004474ba7")
        time.sleep(0.5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
        GPIO.cleanup()
