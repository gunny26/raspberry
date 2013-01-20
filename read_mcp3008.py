#!/usr/bin/python

import time
import os
# import kernel modules needed for 1-wire devies at GPIO #4
os.system("sudo modprobe w1-gpio")
os.system("sudo modprobe w1-therm")
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

HIGH = True # High Pegel
LOW = False # LOw Pegel

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
        print "DS18B20  : ", get_ds18b20_temp("28-000004474f0c")
        time.sleep(0.5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()
