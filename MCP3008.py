#!/usr/bin/python

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

class MCP3008(object):
    """class for reading sensor values over mcp3008 ADC"""
    
    HIGH = True # High Pegel
    LOW = False # Low Pegel

    def __init__(self, sclk, mosi, miso, cs):
        self.mosi = mosi
        self.miso = miso
        self.cs = cs
        self.sclk = sclk
        # Pin Programmierung
        GPIO.setup(sclk, GPIO.OUT)
        GPIO.setup(mosi, GPIO.OUT)
        GPIO.setup(miso, GPIO.IN)
        GPIO.setup(cs, GPIO.OUT)

    def __del__(self):
        try:
            GPIO.cleanup()
        except:
            pass

    # Funktionsdefinition
    def __readAnalogData(self, adcChannel):
        # Pegel vorbereiten
        GPIO.output(self.cs, self.HIGH)
        GPIO.output(self.cs, self.LOW)
        GPIO.output(self.sclk, self.LOW)

        sendcmd = adcChannel
        sendcmd |= 0b00011000 # entspricht 0x18 (1: Startbit, 1:Single/ended)

        # Senden der Bitkombination (Es finden nur 5 Bits Beruecksichtigung)
        for i in range(5):
            if(sendcmd & 0x10): # (Bit an Position 4 pruefen. Zaehlung beginnt bei 0)
                GPIO.output(self.mosi, self.HIGH)
            else:
                GPIO.output(self.mosi, self.LOW)
            # Negative Flanke des Clocksignals generieren
            GPIO.output(self.sclk, self.HIGH)
            GPIO.output(self.sclk, self.LOW)
            sendcmd <<= 1 # Bitfolge eine Position nach links schieben

        # Empfangen der Daten des ADC
        adcvalue = 0 # Ruecksetzen des gelesenen Wertes
        for i in range(11):
            GPIO.output(self.sclk, self.HIGH)
            GPIO.output(self.sclk, self.LOW)
            adcvalue <<= 1 # Position nach links schieben
            if (GPIO.input(self.miso)):
                adcvalue |= 0x01
        return(adcvalue)

    def read_tmp36(self, ADC_Channel):
        """reads voltage from tmp36 and coverts to celsius"""
        adcvalue = self.__readAnalogData(ADC_Channel)
        # 1024 =
        # 0 =
        # provides 250mv at 25 Celsius
        # TMP35 and TMP36 scale of 10mv/1 Grad Celsius
        temperature = 25 + (float(adcvalue) - 250) / 10
        return(temperature)

    def read_photocell(self, ADC_Channel):
        """reads voltage from photocell CdS photoresister"""
        adcvalue = self.__readAnalogData(ADC_Channel)
        # 1024 = very bright
        # 0 = dark
        return(adcvalue)

    def read_ir_sensor(self, ADC_Channel):
        """reads voltage from IR-Sensor TSOP-38238"""
        adcvalue = self.__readAnalogData(ADC_Channel)
        # 1024 =
        # 0 =
        return(adcvalue)
