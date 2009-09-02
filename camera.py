#!/usr/bin/python
from uspp import *
from termios import *
import time

# Functions
def sendToCamera(command):
    pass

def getFromCamera():
    pass

def goHome(tty):
    setAbsPanTilt(tty, 0, 0)

# With a command, we expect a signal saying acknowledged, then completed
# ackSignal = '' + chr(0x90) + chr(0x41) + chr(0xff)
# cplSignal = '' + chr(0x90) + chr(0x51) + chr(0xff)
def sendCmd(tty, command):
    ackSignal = '' + chr(0x90) + chr(0x41) + chr(0xff)
    cplSignal = '' + chr(0x90) + chr(0x51) + chr(0xff)

    tty.write(command)
    counter = 0
    while tty.inWaiting() < len(ackSignal):
        time.sleep(1)
        counter += 1

        if counter == 10:
            print "Camera would not acknowledge our command.  Aborting."
            exit(1)

    data = tty.read(len(ackSignal))

    if data == ackSignal:
        print "Command was acknowledged"

    counter = 0
    while tty.inWaiting() < len(cplSignal):
        time.sleep(1)
        counter += 1

        if counter == 10:
            print "Camera could not complete command.  Aborting."
            exit(1)

    data = tty.read(len(cplSignal))

    if data == cplSignal:
        print "Command was completed"
        return True


# < 0000 - 035D > for left movement
# < FFFF - FCA4 > for right movement
# < 0000 - 011E > for tilt up
# < FFFF - FEE3 > for tilt down
# < 01 - 7F > pan / tilt speed
# First byte in both pan and tilt is either 00 or 0F which indicates sign
def setAbsPanTilt(tty, pan, tilt):
    stepsPerPanDegLeft = 8.6
    stepsPerPanDegRight = 8.61
    stepsPerTiltDegUp = 11.44
    stepsPerTiltDegDown = 11.4
    panFactor = 0
    tiltFactor = 0

    if pan > 100:
        print "Pan cannot be greater than 100!"
        pan = 100;

    if pan < -100:
        print "Pan cannot be less than 100!"
        pan = -100

    if tilt > 25:
        print "Tilt cannot be greater than 25!"
        tilt = 25

    if tilt < -25:
        print "Tilt cannot be less than 25!"
        tilt = -25

    # Convert from degrees to bits
    if pan > 0:
        panFactor = stepsPerPanDegRight
    else:
        panFactor = stepsPerPanDegLeft

    if tilt < 0:
        tiltFactor = stepsPerTiltDegDown
    else:
        tiltFactor = stepsPerTiltDegUp

    panSteps = 0xffff & int(0x10000 + pan * panFactor + 0.5)
    tiltSteps = 0xffff & int(0x10000 + tilt * tiltFactor + 0.5)

    # command id
    sendCommand = '' + chr(0x81) + chr(0x01) + chr(0x06) + chr(0x02)

    # speed
    #sendCommand = sendCommand + chr(0x7f) + chr(0x7f)
    sendCommand = sendCommand + chr(0x11) + chr(0x11)

    # pan
    sendCommand = sendCommand + chr(0xf & (panSteps >> 12))
    sendCommand = sendCommand + chr(0xf & (panSteps >> 8))
    sendCommand = sendCommand + chr(0xf & (panSteps >> 4))
    sendCommand = sendCommand + chr(0xf & panSteps)

    # tilt
    sendCommand = sendCommand + chr(0xf & (tiltSteps >> 12))
    sendCommand = sendCommand + chr(0xf & (tiltSteps >> 8))
    sendCommand = sendCommand + chr(0xf & (tiltSteps >> 4))
    sendCommand = sendCommand + chr(0xf & tiltSteps)

    # stop byte
    sendCommand = sendCommand + chr(0xff)

    return sendCmd(tty, sendCommand)

def initCamera(tty):
    initstring = '' + chr(0x88) + chr(0x30) + chr(0x01) + chr(0xff)
    initSignal = '' + chr(0x88) + chr(0x30) + chr(0x02) + chr(0xff)

    print "Sending: " + str(len(initstring)) + " bytes"
    tty.write(initstring)
    
    tries = 1

    while tty.inWaiting() < 4:
        time.sleep(1)
        tries += 1
        if tries == 10:
            print "No camera detected."
            exit(1)
    
    data = tty.read(4)

    if data == initSignal:
        print "Houston, we have found a camera."
        return True
    else:
        return False

# Setup serial port
tty=SerialPort("/dev/ttyUSB0", 100, 9600, mode='232')

# Signals
ackSignal = '' + chr(0x90) + chr(0x41) + chr(0xff)
cplSignal = '' + chr(0x90) + chr(0x51) + chr(0xff)

initCamera(tty)
goHome(tty)
setAbsPanTilt(tty, 85, 25)
setAbsPanTilt(tty, -85, 25)
setAbsPanTilt(tty, -85, -25)
setAbsPanTilt(tty, 85, -25)
goHome(tty)

