#!/usr/bin/python

import time
import os
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

HIGH = True # High Pegel
LOW = False # LOw Pegel

def main():
    coils = (18, 23, 17, 22)
    sequences = ((1,0,0,0), (1,1,0,0), (0,1,0,0), (0,1,1,0), (0,0,1,0), (0,0,1,1), (0,0,0,1), (1,0,0,1))
    sleep = input("sleep in seconds angeben:")
    for coil in coils:
        GPIO.setup(coil, GPIO.OUT)
    while True:
        for sequence in sequences:
            print sequence
            coilcounter = 0
            for coil in coils:
                GPIO.output(coil, sequence[coilcounter])
                coilcounter += 1
            time.sleep(sleep)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()
