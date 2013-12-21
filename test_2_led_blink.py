#!/usr/bin/python

import time
import os
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

HIGH = True # High Pegel
LOW = False # LOw Pegel

def main():
    COIL1 = 18
    COIL2 = 23
    print "Connect at GPIO %d Base of Transistor 1" % COIL1
    print "Connect at GPIO %d Base of Transistor 2" % COIL2
    sleep = input("sleep in seconds angeben:")
    GPIO.setup(COIL1, GPIO.OUT)
    GPIO.setup(COIL2, GPIO.OUT)
    state = True
    print "Set initial State to %s" % state
    GPIO.output(COIL1, state)
    GPIO.output(COIL2, not state)
    print "Let it blink"
    while True:
        state = not state
        GPIO.output(COIL1, state)
        GPIO.output(COIL2, not state)
        print "State COIL1=%s COIL2=%s" % (state, not state)
        time.sleep(sleep)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()
