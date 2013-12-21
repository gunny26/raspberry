#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import curses
import logging

GPIO.cleanup()
GPIO.setmode(GPIO.BCM)

enable_pin = 18

GPIO.setup(enable_pin, GPIO.OUT)
GPIO.output(enable_pin, 1)

xcoils = [4, 17, 23, 24]
for pin in xcoils:
    GPIO.setup(pin, GPIO.OUT)

# if you are using rev 1 raspberry use pin 21 instead of 27
ycoils = [27, 22, 10, 9]
for pin in ycoils:
    GPIO.setup(pin, GPIO.OUT)

sequence = [(1,0,1,0), (0,1,1,0), (0,1,0,1), (1,0,0,1)]
#sequence = [(1,1,0,0), (0,1,1,0), (0,0,1,1), (1,0,0,1)]
# sequence = [(1,0,0,0), (1,1,0,0), (0,1,0,0), (0,1,1,0), (0,0,1,0), (0,0,1,1), (0,0,0,1), (1,0,0,1)]

def forward(delay, steps): 
    for i in range(0, steps):
        setStepX(sequence[x % 4], xcoils)

def backwards(delay, steps):
    for i in range(0, steps):
        setStepX(sequence[x % 4], xcoils)
  
def up(delay, steps): 
    for i in range(0, steps):
        setStepY(sequence[y % 4], ycoils)

def down(delay, steps): 
    for i in range(0, steps):
        setStepY(sequence[y % 4], ycoils)

def setStep(pulses, coils):
    counter = 0
    for pin in coils:
        GPIO.output(pin, pulses[counter])
        counter += 1

delay = int(5) / 1000.0
x = 0
y = 0
stdscr = curses.initscr()
curses.cbreak()
stdscr.keypad(1)

stdscr.addstr(0,10,"Hit 'q' to quit")
stdscr.refresh()

key = ''
stdscr.addstr(10, 2, "X-Position : ")
stdscr.addstr(11, 2, "Y-Position : ")
while key != ord('q'):
    stdscr.refresh()
    key = stdscr.getch()
    stdscr.addch(14, 10, key)
    if key == curses.KEY_LEFT:
        x += 1 
        backwards(delay, 1)
    elif key == curses.KEY_RIGHT: 
        x -= 1
        forward(delay, 1)
    elif key == curses.KEY_UP: 
        y += 1
        up(delay, 1)
    elif key == curses.KEY_DOWN: 
        y -= 1
        down(delay, 1)
    stdscr.addstr(10, 16, "%03d" % x)
    stdscr.addstr(11, 16, "%03d" % y)
    time.sleep(delay)
curses.endwin()
GPIO.cleanup()

