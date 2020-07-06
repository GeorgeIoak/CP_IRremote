# Write your code here :-)
import board
import busio
import bitbangio
import digitalio

cs = digitalio.DigitalInOut(board.D10)
cs.direction = digitalio.Direction.OUTPUT
cs.value = True

#spi = busio.SPI(board.SCK, MOSI=board.MOSI)
spi = bitbangio.SPI(board.D11, MOSI=board.D12)

while not spi.try_lock():
    pass

spi.configure(baudrate=500000, phase=1, polarity=1)
cs.value = False
spi.write(bytes([0xFF, 0x05]))
cs.value = True

spi.unlock()