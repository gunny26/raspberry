#!/usr/bin/python

import time
import os
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

HIGH = True # High Pegel
LOW = False # LOw Pegel

# Funktionsdefinition
def readAnalogData(adcChannel, SCLKPin, MOSIPin, MISOPin, CSPin):
    # Pegel vorbereiten
    GPIO.output(CSPin, HIGH)
    GPIO.output(CSPin, LOW)
    GPIO.output(SCLKPin, LOW)

    sendcmd = adcChannel
    sendcmd |= 0b00011000 # entspricht 0x18 (1: Startbit, 1:Single/ended)

    # Senden der Bitkombination (Es finden nur 5 Bits Beruecksichtigung)
    for i in range(5):
        if(sendcmd & 0x10): # (Bit an Position 4 pruefen. Zaehlung beginnt bei 0)
            GPIO.output(MOSIPin, HIGH)
        else:
            GPIO.output(MOSIPin, LOW)
        # Negative Flanke des Clocksignals generieren
        GPIO.output(SCLKPin, HIGH)
        GPIO.output(SCLKPin, LOW)
        sendcmd <<= 1 # Bitfolge eine Position nach links schieben

    # Empfangen der Daten des ADC
    adcvalue = 0 # Ruecksetzen des gelesenen Wertes
    for i in range(11):
        GPIO.output(SCLKPin, HIGH)
        GPIO.output(SCLKPin, LOW)
        adcvalue <<= 1 # Position nach links schieben
        if (GPIO.input(MISOPin)):
            adcvalue |= 0x01
    return(adcvalue)

def read_tmp36(ADC_Channel, SCLKPin, MOSIPin, MISOPin, CSPin):
    """reads voltage from tmp36 and coverts to celsius"""
    adcvalue = readAnalogData(ADC_Channel, SCLKPin, MOSIPin, MISOPin, CSPin)
    # 1024 =
    # 0 =
    return(adcvalue)

def read_photocell(ADC_Channel, SCLKPin, MOSIPin, MISOPin, CSPin):
    """reads voltage from photocell CdS photoresister"""
    adcvalue = readAnalogData(ADC_Channel, SCLKPin, MOSIPin, MISOPin, CSPin)
    # 1024 = very bright
    # 0 = dark
    return(adcvalue)

def read_ir_sensor(ADC_Channel, SCLKPin, MOSIPin, MISOPin, CSPin):
    """reads voltage from IR-Sensor TSOP-38238"""
    adcvalue = readAnalogData(ADC_Channel, SCLKPin, MOSIPin, MISOPin, CSPin)
    # 1024 =
    # 0 =
    return(adcvalue)

# Variablendefinition
SCLK        = 18 # Serial Clock
MOSI        = 24 # Master-Out Slave-IN
MISO        = 23 # Master-In Slave-Out
CS          = 25 # Chip-Select

# Pin Programmierung
GPIO.setup(SCLK, GPIO.OUT)
GPIO.setup(MOSI, GPIO.OUT)
GPIO.setup(MISO, GPIO.IN)
GPIO.setup(CS, GPIO.OUT)

def main():
    while True:
        print "-" * 80
        print "TMP36-1  : ", read_tmp36(0, SCLK, MOSI, MISO, CS)
        print "Photocell: ", read_photocell(1, SCLK, MOSI, MISO, CS)
        print "TMP36-2  : ", read_photocell(2, SCLK, MOSI, MISO, CS)
        print "IR-SENSOR: ", read_ir_sensor(3, SCLK, MOSI, MISO, CS)
        time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()
