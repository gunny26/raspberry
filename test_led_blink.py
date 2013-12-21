#!/usr/bin/python

import time
import os
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

HIGH = True # High Pegel
LOW = False # LOw Pegel

def main():
    OUTPIN = 18
    print "Connect at GPIO %d Base of Transistor" % OUTPIN
    sleep = input("sleep in seconds angeben:")
    GPIO.setup(OUTPIN, GPIO.OUT)
    state = True
    print "Set initial State to %s" % state
    GPIO.output(OUTPIN, state)
    print "Let it blink"
    while True:
        state = not state
        GPIO.output(OUTPIN, state)
        print "State now %s" % state
        time.sleep(sleep)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()
