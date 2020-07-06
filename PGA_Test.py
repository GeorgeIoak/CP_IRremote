# Write your code here :-)
import board
import busio
import time
import digitalio

cs = digitalio.DigitalInOut(board.D10)
cs.direction = digitalio.Direction.OUTPUT
cs.value = True

spi = busio.SPI(board.SCK, MOSI=board.MOSI)

while not spi.try_lock():
    pass

spi.configure(baudrate=1000000, phase=1, polarity=1)
cs.value = False
spi.write(bytes([0x1F, 0x11]))
cs.value = True

spi.unlock()