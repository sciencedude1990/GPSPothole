# Demonstrate reading and writing bytes to the FRAM
# Note that the byte address can run from 0b0000000000000000 to 0b0111111111111111 (i.e., 0 to 32767)

# Imports
import machine
from machine import Pin
import FRAM_256k
import os

# Create I2C object
# Use I2C 0
# scl and sda are connected to GP17 and GP16 respectively
# Frequency is set to 400 000 Hz
i2c = machine.SoftI2C(scl=machine.Pin(17), sda=machine.Pin(16), freq=400000)

# Print out any addresses found
devices = i2c.scan()

if devices:
    for d in devices:
        print("Found:\t" + hex(d))
        

fram = FRAM_256k.FRAM_256k(i2c)

# Create the filesystem - will wipe out anything already on the FRAM memory
# os.VfsFat.mkfs(fram)
# Mount the file system
os.mount(fram, '/fram')
print("Done mounting FRAM")

