# When the users presses a button, records the GPS location, and buzzes back to the user
# The files are stored in a FRAM memory, so can re-write many times

# Imports
import machine
import array
from machine import Pin
import time
import os
import FRAM_256k

# Big red button
red_button = Pin(0, Pin.IN, Pin.PULL_UP)
# Big red LED
red_led    = Pin(1, Pin.OUT, value = 1)
# Buzzer
buzz = Pin(2, Pin.OUT, value=0)

# Create I2C object
# Use I2C 0
# scl and sda are connected to GP17 and GP16 respectively
# Frequency is set to 400 000 Hz
i2c = machine.SoftI2C(scl=machine.Pin(17), sda=machine.Pin(16), freq=100000)
# Create the FRAM object
fram = FRAM_256k.FRAM_256k(i2c)

# Create the filesystem - will wipe out anything already on the FRAM memory
# os.VfsFat.mkfs(fram)

# Mount the file system
os.mount(fram, '/fram')

print('FRAM mounted')

# Places to store the GPS data
current_record = 0
MAX_RECORD = 64
latitude_array = array.array("f", [0] * MAX_RECORD)
longitude_array = array.array("f", [0] * MAX_RECORD)

# GPS is UART based
uart0 = machine.UART(0, baudrate=9600, parity=None, stop=1, tx=machine.Pin(12), rx=machine.Pin(13))
uart0.init()

uart_buffer = ""

my_latitude = 0
my_longtitude = 0
GPS_STALE_MAX = 30
gps_stale_count = GPS_STALE_MAX

BUTTON_COUNT_MAX = 20
button_count = 0

print("Start loop and wait for GPS...")

go_loop = 1

while go_loop == 1:
    
    # Increment the GPS stale counter
    gps_stale_count = gps_stale_count + 1
    if gps_stale_count > GPS_STALE_MAX:
        gps_stale_count = GPS_STALE_MAX
        
    # Increment the button counter
    button_count = button_count + 1
    if button_count > BUTTON_COUNT_MAX:
        button_count = BUTTON_COUNT_MAX
    
    # Check the button
    if red_button.value() == 1:
        red_led.value(1)
    else:
        # Button has been pushed
        red_led.value(0)
        
        if button_count < BUTTON_COUNT_MAX:
            # Do nothing
            print("Please wait for software button debounce...")
        else:
            if (gps_stale_count < GPS_STALE_MAX):
                # Reset button count
                button_count = 0
                
                # Drop the data in the array
                latitude_array[current_record] = my_latitude
                longitude_array[current_record] = my_longitude
                                
                # Write to the file                
                fd = open("/fram/gps_pothole.txt", 'at')
                #fd.write('Latitude, Longitude\n')
                #for ii in range(MAX_RECORD):
                #    fd.write("{:1.8f}".format(latitude_array[ii]) + ", " + "{:1.8f}".format(-longitude_array[ii]) + "\n")
                #fd.close()
                
                fd.write("{:1.8f}".format(latitude_array[current_record]) + ", " + "{:1.8f}".format(-longitude_array[current_record]) + "\n")
                fd.close()
                
                print("Wrote to file: " + "{:1.8f}".format(latitude_array[current_record]) + ", " + "{:1.8f}".format(-longitude_array[current_record]) + "\n")
                
                # Increment the current record
                current_record = (current_record + 1) % MAX_RECORD
                                
                # Buzz to the user
                buzz.value(1)
                red_led.value(1)
                time.sleep(0.02)
                buzz.value(0)
                red_led.value(0)
                time.sleep(0.02)
                buzz.value(1)
                red_led.value(1)
                time.sleep(0.04)
                buzz.value(0)
                red_led.value(0)
                
                # print("Wrote file!")
                
            else:
                # Buzz to indicate bad GPS data
                for aa in range(3):
                    buzz.value(1)
                    red_led.value(1)
                    time.sleep(0.02)
                    buzz.value(0)
                    red_led.value(0)
                    time.sleep(0.1)
                print("GPS data stale")
    
    if (uart0.any() >= 241):
        # Read the buffer
        temp_buffer = uart0.read()
        temp_buffer.format(1)
        decode_good = 0
        try:
            uart_buffer = temp_buffer.decode()
            decode_good = 1
        except:
            print("Decode issue")
            
        if decode_good == 1:            
            if uart_buffer.find("GNGLL") >= 0:
                #print("Found GNGLL")
                #print(uart_buffer)
                # Process the uart_buffer to find the location
                # Find the text GNGLL            
                GNGLL_loc = uart_buffer.find("GNGLL")
                
                # Find the commas
                comma_good = 0
                com1 = uart_buffer.find(",", GNGLL_loc + 1)
                if com1 >= 0:
                    com2 = uart_buffer.find(",", com1 + 1)
                    if com2 >= 0:
                        com3 = uart_buffer.find(",", com2 + 1)
                        if com3 >= 0:
                            com4 = uart_buffer.find(",", com3 + 1)
                            if com4 >= 0:
                                com5 = uart_buffer.find(",", com4 + 1)
                                if com5 >= 0:
                                    com6 = uart_buffer.find(",", com5 + 1)
                                    if com6 >= 0:
                                        com7 = uart_buffer.find(",", com6 + 1)
                                        if (com7 >= 0) & ((com7 + 1) < len(uart_buffer)):
                                            comma_good = 1
                
                if comma_good == 1:
                    # Check for A,A characters
                    if uart_buffer[com6 + 1] == "A":
                        if uart_buffer[com7 + 1] == "A":
                            # Find the latitude and longitude
                            lat_str = uart_buffer[(com1 + 1) : (com2)]
                            long_str = uart_buffer[(com3 + 1) : (com4)]
                        
                            temp_lat = float(lat_str)
                            temp_lat_dec = temp_lat - float(int(temp_lat))
                            temp_min_lat = int(temp_lat) - 100 * (int(temp_lat / 100))
                            my_latitude = float(int(temp_lat / 100)) + (float(temp_min_lat) + temp_lat_dec) / 60
                        
                            temp_long = float(long_str)
                            temp_long_dec = temp_long - float(int(temp_long))
                            temp_min_long = int(temp_long) - 100 * (int(temp_long / 100))
                            my_longitude = float(int(temp_long / 100)) + (float(temp_min_long) + temp_long_dec) / 60
                        
                            print(str(my_latitude) + ",-" + str(my_longitude))
                            
                            # Reset the stale counter
                            gps_stale_count = 0                            
                            
    time.sleep(0.1)


