import pygame
import smbus
import time 
import serial 
from PacketSerial import *

# initialize things 
bus = smbus.SMBus(1)
ser = serial.Serial("/dev/ttyAMA0", 9600, timeout=1)
pser = PacketSerial(ser)

# define constants
ARM_ADDRESS = 0x10
SENSOR_ADDRESS = 0x11
DRIVE_ADDRESS = 0x12

SENSOR_2_ADDRESS = 0xA1 # for when we send data over serial 

# define places to hold the data
sensors = [0 for i in range(6)]  # moisture, gas1, gas2, gas3, voltage
joystick_controls_arm = False 

def write(address, data):
    '''
    Write a byte to the i2c connection
    Arguments:
        address (int): i2c address of the receiving device
        data (char): data to be sent
    '''
    bus.write_byte(address, ord(data))

def read(address):
    '''
    Read a byte from the i2c connection
    Argument:
        address (int): i2c address of the receiving device
    '''    
    return bus.read_byte(address)
    
def read_block(address):
    ''' 
    Read a whatever block of data was sent across the i2c connection.
    Will always return a 32-byte array with 255 in the unused positions. 
    Argument: 
        address (int): i2c address of the receiving device 
    '''
    return bus.read_i2c_block_data(address, 0)

def write_block(address, data):
    '''
    Write a block of data across the i2c connection
    ''' 
    if len(data) == 0:
        raise IndexError("You cannot write 0 bytes across the i2c connection")
    elif len(data) == 1:
            bus.write(address, chr(data[0]))
    else:
        bus.write_i2c_block_data(address, data[0], data[1:]) 

def to_strs(*lis):
    return list(chr(i) for i in lis)

while(True):
    data = pser.read() 
    if data is None:
        # Do nothing. no data received. 
        pass
    else:    
        data = [int(i) for i in data] # convert all data into ints
        if data[0] == ARM_ADDRESS: #these might not be separate cases, I might just use write_block for everything
            write(data[1])
        elif data[1] == DRIVE_ADDRESS:
            write_block(DRIVE_ADDRESS, data[1:2])

    # get sensor data
    #sensors = [read(SENSOR_ADDRESS) for i in range(5)] 
    pser.write(to_strs(SENSOR_ADDRESS, sensors[0], sensors[1], sensors[2]))
    pser.write(to_strs(SENSOR_2_ADDRESS, sensors[3], sensors[4], sensors[5]))
    time.sleep(0.25) # poll every 0.25 seconds    
