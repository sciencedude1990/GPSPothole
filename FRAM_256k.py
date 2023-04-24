# References
# Please see the device datasheet, MB85RC256V-DS501-00017-3v0-E.pdf for the I2C details
# Please see the following for "custom block devices", https://docs.micropython.org/en/latest/reference/filesystem.html#custom-block-devices

import machine

class FRAM_256k:
    def __init__(self, soft_i2c):
        assert type(soft_i2c) == machine.SoftI2C, "Must use machine.SoftI2C"
        
        self.i2c = soft_i2c
        
    def readblocks(self, block_num, buf): # Required routine for "os"
        # Checks on the inputs
        assert len(buf) >= 1, "Must have at least 1 byte to read back"
        assert (len(buf) % 512) == 0, "Must read back 512 bytes at a time"
        
        # Number of 512 byte blocks
        nblocks = len(buf) // 512
        
        # Don't read too many blocks
        assert (block_num + nblocks) <= 64, "Too many blocks requested"
        
        # Byte address to start reading at
        addr = block_num * 512
        # Low part of address
        addr_low = addr & 0xFF
        # High part of address
        addr_high = (addr >> 8) & 0xFF
        
        # The I2C communications
        self.i2c.start()
        a1 = self.i2c.write(bytearray([0b10100000]))
        a2 = self.i2c.write(bytearray([addr_high, addr_low]))
        self.i2c.start()
        a3 = self.i2c.write(bytearray([0b10100001]))
        self.i2c.readinto(buf)
        self.i2c.stop()
        
    def writeblocks(self, block_num, buf): # Required routine for "os"
        # Checks on the input
        assert len(buf) >= 1, "Must have at least 1 byte to write"
        assert (len(buf) % 512) == 0, "Must write 512 bytes at a time"
        
        # Number of blocks
        nblocks = len(buf) // 512
        
        # Don't write too many blocks
        assert (block_num + nblocks) <= 64, "Too many blocks requested to be written"
        
        # Byte address to start reading at
        addr = block_num * 512
        # Low part of address
        addr_low = addr & 0xFF
        # High part of address
        addr_high = (addr >> 8) & 0xFF
        
        # The I2C communications
        self.i2c.start()
        a1 = self.i2c.write(bytearray([0b10100000]))
        a2 = self.i2c.write(bytearray([addr_high, addr_low]))
        a3 = self.i2c.write(buf)
        self.i2c.stop()
                    
    def ioctl(self, op, arg): # Required routine for "os"
        if op == 4:  # get number of blocks
            return 64
        if op == 5:  # get block size in bytes
            return 512        
