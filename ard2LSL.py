"""
Example program to demonstrate how to send a PPG time series to
LSL from the Arduino Uno by automatically connecting to it over serial.

The sources for significant example code are cited below.
"""
import random
import time
from time import sleep
import serial
from serial import Serial
import serial.tools.list_ports
import sys
import platform
from pylsl import StreamInfo, StreamOutlet, local_clock

from datetime import datetime
import re

# Handle Random Data Case where interface is undefined
deviceSerialInterface = None;

# Need to check device VID/PID (for microcontroller USB interface)
deviceName = "uno"; # Default Device Name
deviceMap = {"uno":"2341:0043","leo":"2341:8036","teensy4.0":"16C0:0483"}

# Blocking Ctrl+Z Program Hiatus on OSX to prevent unclosed Serial Ports
import signal
def handler(signum, frame):
    #raise(KeyboardInterrupt('Ctrl+Z pressed, but ignored'))
    print('Ctrl+Z pressed, but ignored.')
    print()
    print("Quit by KeyboardInterrupt.")
    print()
    quit(0);

# This just handles for multiplatform keyboard interrupts. 
if(platform.system() == 'Windows'):
    signal.signal(signal.SIGTERM, handler)
else: # OSX / Linux / etc...
    signal.signal(signal.SIGTSTP, handler)
    signal.signal(signal.SIGUSR1, handler)
    signal.signal(signal.SIGUSR2, handler)

# CLEAR SCREEN
import os
if(platform.system() == 'Windows'):
    os.system('cls')  # For Windows
else:
    os.system('clear')  # For Linux/OS X


# NEEDED FOR ON EXIT RELEASE OF SERIAL PORT
# import sys
import atexit
import platform # from sys

print("Starting Arduino Analog LSL Stream Program...")
print(platform.system(), platform.release())
print("Python version " + platform.python_version())
print("-----Program Begin-----")
time.sleep(1.0)

# Finds port at program start
# As shown in the post "Get idVendor and idProduct of your Arduino/USB devices", 
# we know VID:PID of Arduino Uno is 2341:0043. So we can compare it with what 
# returned from serial.tools.list_ports.comports() to determine if it is an Arduino Uno. 
# And for simplicity also, it is assumed it is in the VID:PID=2341:0043 format.
# The post can be found here: http://arduino-er.blogspot.com/2015/04/get-idvendor-and-idproduct-of-your.html
# If this method fails, you can hardcode it and comment the autoconnect, or just 
# look up you device's VID:PID based on the article.
# In the future, it would be good to have a way to select which Arduino Uno 
# you want to use if multiple are connected. For now, it uses the first it finds.
def findArduinodevicePort():
    portList = list(serial.tools.list_ports.comports())
    for port in portList:
        if ("VID:PID="+deviceMap["uno"]) in port[0]\
            or ("VID:PID="+deviceMap["uno"]) in port[1]\
            or ("VID:PID="+deviceMap["uno"]) in port[2]:
            print(port)
            #print(port[0])
            #print(port[1])
            #print(port[2])

            #please note: it is not sure [0]
            #returned port[] is no particular order
            #so, may be [1], [2]
            return port[0]

# In case you want to do this with a Teensy or Other uC
# Example: Teensy: Might be VID = 0x16C0, PID = 0x0480 
# Use terminal / CMD / Device manager tools to find the 
# VID/PID numbers of your device & manufacturer. 
def findParticularDevicePort(VID,PID):
    portList = list(serial.tools.list_ports.comports())
    for port in portList:
        if "VID:PID="+VID+":"+PID in port[0]\
            or "VID:PID="+VID+":"+PID in port[1]\
            or "VID:PID="+VID+":"+PID in port[2]:
            print(port)
            #print(port[0])
            #print(port[1])
            #print(port[2])

            #please note: it is not sure [0]
            #returned port[] is no particular order
            #so, may be [1], [2]
            return port[0]

def findNamedDevicePort(d_name):
    portList = list(serial.tools.list_ports.comports())
    for port in portList:
        if ("VID:PID="+deviceMap[d_name]) in port[0]\
            or ("VID:PID="+deviceMap[d_name]) in port[1]\
            or ("VID:PID="+deviceMap[d_name]) in port[2]:
            print(port)
            #print(port[0])
            #print(port[1])
            #print(port[2])

            #please note: it is not sure [0]
            #returned port[] is no particular order
            #so, may be [1], [2]
            return port[0]

# PRINTS ALL COM PORTS!
print("All Connected Ports:")
ports = list(serial.tools.list_ports.comports())
for p in ports:
    print(p)

force_hz = 50; # Default Sampling Rate for this script! <--- set this
use_random=False;
# Allow Skipping Connection & Use Random Data
if(len(sys.argv)>1):
    if(sys.argv[1]=="--skip-connect"):
        use_random = True;
        if(len(sys.argv)>2):
            force_hz = sys.argv[2];
            force_hz = float(re.sub("[^0-9.]", "", force_hz)); 
            print("Forcing Random Frequency to %dHz" % (force_hz))
        else:
            print("Forcing Random Frequency to %dHz since no Freq. Provided" % (force_hz))


# Cannot Start Program without Connected Microcontrollers
devicePort = findNamedDevicePort(deviceName)# findArduinodevicePort()

if(not use_random):
    if(not devicePort):
        print("No %s found" % deviceName)
        if(len(sys.argv) < 2): 
            sys.exit("No %s found - No cmd argument given - Quitting..." % deviceName)
        else:
            print("No %s found - Using 1st cmd argument instead..." % deviceName)
        devicePort = '/dev/cu.usbmodem'+sys.argv[1];
    else:
        print(("%s found: " % deviceName)+ devicePort)
        print()

    # Allows use of "-f" to force use of the specific port even if this detects a device automatically
    if(len(sys.argv)>2):
        if sys.argv[2]=="-f":
            devicePort = '/dev/cu.usbmodem'+sys.argv[1];


    # sys.argv[0] program name
    # sys.argv[1] port num if no autodetect / overrides autodetect - Will run without this
    deviceSerialInterface = serial.Serial(
        port=devicePort,\
        baudrate=9600,\
        parity=serial.PARITY_NONE,\
        stopbits=serial.STOPBITS_ONE,\
        bytesize=serial.EIGHTBITS,\
        timeout=2); # Establish the connection on a specific port //'/dev/cu.usbserial'+sys.argv[1], 9600
    print("deviceSerialInterface.isOpen() = " + str(deviceSerialInterface.isOpen()) + " at port: " + devicePort)
    time.sleep(1.0)
else:
    print("Skipping Serial Connection...");
    time.sleep(1.0)
    print("Using Random Data...")
    import random

# Closes port after program end
def doAtExit():
    if(deviceSerialInterface is not None):
        if(deviceSerialInterface.isOpen()):
            deviceSerialInterface.close()
            print("Close serial")
            print("deviceSerialInterface.isOpen() = " + str(deviceSerialInterface.isOpen()))

atexit.register(doAtExit)

# first create a new stream info (here we set the name to BioSemi,
# the content-type to EEG, 8 channels, 100 Hz, and float-valued data) The
# last value would be the serial number of the device or some other more or
# less locally unique identifier for the stream as far as available (you
# could also omit it but interrupted connections wouldn't auto-recover).
lsl_stream_name = 'AZPPGStream';
lsl_stream_type = 'PPG'; # Voltage
ppg_ch = 1;
ppg_hz = 50; # Should be the same as your sampling rate in the Arduino Code!!!
ppg_datatype = 'float32';
ppg_id= 'AZPPGStream'+str(random.randint(0,255));
info = StreamInfo(lsl_stream_name, lsl_stream_type, ppg_ch, ppg_hz, ppg_datatype, ppg_id);
channels = info.desc().append_child('channels');
labels = ["PPG Voltage"]
for label in labels:
    ch = channels.append_child("channel")
    ch.append_child_value('label', label)
    ch.append_child_value('unit','Volts')
    ch.append_child_value('type','PPG')
    ch.append_child_value('frequency-format','bpm')

#additional Meta Data
info.desc().append_child_value('manufacturer','Embedded-Lab')
info.desc().append_child_value('software-by','Argzero Technologies, LLC')

# next make an outlet
outlet = StreamOutlet(info)
print  ("--------------------------------------\n"+ \
        "LSL Outlet Configuration: \n" + \
        "  PPG Stream: \n" + \
        "      Name: " + lsl_stream_name + " \n" + \
        "      Type: " + lsl_stream_type + " \n" + \
        "      Channel Count: " + str(ppg_ch) + "\n" + \
        "      Sampling Rate: " + str(ppg_hz) + "\n" + \
        "      Channel Format: "+ ppg_datatype + " \n" + \
        "      Source Id: " + ppg_id + " \n" + \
        "---------------------------------------\n")

input("Press Enter to continue...")
time.sleep(1.0)
print("Now sending data...")
time.sleep(0.5)
a = 0.0;
if(len(sys.argv)>1):
    if(sys.argv[1]=="--skip-connect"):
        force_hz = force_hz;
    else:
        force_hz = 0.0;
        use_random = False;
serialConnected = True;
while True:
    try:
        if(not use_random):
            # Make a new random 1-channel sample; this is converted into a
            # pylsl.vector of floats (the data type that is expected by push_sample)
            # Note: readline() waits until the Arduino submits a message and will not proceed until it receives a message. 
            a= str(deviceSerialInterface.readline());
            a = re.sub("[^0-9.]", "", a); 

            # Convert the Serial Analog Read to Voltage!
            a = float(5.0)*float(a)/float(1023.0)

            b= str(deviceSerialInterface.readline());
            b = re.sub("[^0-9.]", "", b); 

            # Convert the Serial Analog Read to Voltage!
            b = float(5.0)*float(a)/float(1023.0)

            a = [(a+b)/2];
        else:
            a = random.random()*1023.0;
            a = [float(5.0)*float(a)/float(1023.0)];

        
        # Get a time stamp in seconds (we pretend that our samples are actually
        # DELAY seconds old, e.g., as if coming from some external hardware).
        delay = 0.003; 

        # At 9600 baud (bits per second), printing a 4-byte float on each update.
        # 4 bytes * 8 bits/byte = 32 bits --> 32bits / (9600 bits/s) = 0.003333... s or 3ms.
        # This means our actual timestamp is 3ms earlier.
        stamp = local_clock()-delay;
        alt_stamp = time.time() - delay;
        # Print Data so the User knows its working...
        datetime_stamp = datetime.fromtimestamp(alt_stamp)#self.timestamp+self.inlet.time_correction())#.strftime("%A, %B %d, %Y %I:%M:%S")
        print(("Datetime: " + str(datetime_stamp)+" ||| Voltage: %1.2fV / 5V") % (a[0]));


        # Now send it and wait for a bit
        outlet.push_sample(a,alt_stamp)
        if(use_random):
            sleep(1.0/force_hz);

        #sleep(1.0/ppg_hz) # PLEASE DO NOT DO THIS!!! The Arduino controls the sampling rate!
    except Exception as err:
        if(serialConnected):
            print("Line Failed To Parse!")
            print(err)
            print(err.args)
            a = 0.0;
        devicePort = findNamedDevicePort(deviceName)
        if(not devicePort):
            print("No %s found..." % deviceName)
            time.sleep(1.0)
        else:
            print(("%s found: " % deviceName) + devicePort)
            print()
            # sys.argv[0] program name
            # sys.argv[1] port num if no autodetect / overrides autodetect - Will run without this
            deviceSerialInterface = serial.Serial(
                                    port=devicePort,\
                                    baudrate=9600,\
                                    parity=serial.PARITY_NONE,\
                                    stopbits=serial.STOPBITS_ONE,\
                                    bytesize=serial.EIGHTBITS,\
                                    timeout=2); # Establish the connection on a specific port //'/dev/cu.usbserial'+sys.argv[1], 9600
            print("Attempted to reopen port: " + str(deviceSerialInterface.isOpen()) + " at port: " + devicePort)
            time.sleep(1.0)
