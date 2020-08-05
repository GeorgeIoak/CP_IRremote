import board
import board
import busio
import displayio
import terminalio
import IRLib_P03_RC5d  # We only need to decode RC5
import IRrecvPCI
from adafruit_display_text import label
# import adafruit_displayio_ssd1306
import adafruit_ssd1322
import digitalio
import pcf8574
import bitbangio

# IR Library from https://github.com/cyborg5/IRLibCP

#  Test for MP library insertion

# define Remote Codes
# RC5 address is either 4 or 5
# 0x0140 = 0000 0001 0100 0000 (=320)
#          xxSS tsss ssdd dddd
# x=not used
# SS=start bits, always 1
# t=toggle bit
# s=system bits (address)
# (s ssss = 0 0101 = 0x05 = 5)
# d=command (VALUE below)

# The RC5 code is 14 bits long.
# Each code includes 2 start bits, 1 toggle bit, 5 bit address, 6 bit command

# short press (default) = 1 command.
# long press = 3 consecutive identical commands


btnStop = 0 # might need to use the full RC5 code received
btnFF = 1
btnRew = 2
btnSkipP = 3
btnSkipM = 4
btnPlay = 5
btnPause = 6
btnOpenClose = 7
btnPwrOnOff = 8
btnVolUp = 4635
btnVolDwn = 4636
btnSrcUp = 4631
btnSrcDwn = 4632

selInput = ["SPDIF 1", "SPDIF 2", "OPTICAL 1", "OPTICAL 2", "AES", "OPT 2", "DIG", "USB", " "]

curInput = 0 #  What Source Input are we currently at
remCode = 0  #  Current remote code with toggle bit masked off
curVol = 0

displayio.release_displays()

#oled_reset = -1 # Change to -1 if reset pin isn't available
ir_inpin = board.D9 # Change to the pin that the TSOP4438 recevier is connected to


# Newhaven Display
hardspi = busio.SPI(board.D25, board.D24)
tft_cs = board.D1
tft_dc = board.D0
tft_reset = board.D5

display_bus = displayio.FourWire(
	hardspi, command=tft_dc, chip_select=tft_cs, baudrate=1000000
)
# time.sleep(1)

WIDTH = 256 # Changed from 128 for the Newhaven display
HEIGHT = 64  # Change to 32 if needed
BORDER = 5

# display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT) # I2C OLED
display = adafruit_ssd1322.SSD1322(display_bus, width=WIDTH, height=HEIGHT, colstart=28)

# Use for I2C
i2c = board.I2C() #board.D21, board.D22
# display_bus = displayio.I2CDisplay(i2c, device_address=0x3C) # Used for I2C OLED

myDecoder = IRLib_P03_RC5d.IRdecodeRC5()
myDecoder.ignoreHeader = True # My improve decoding weak signals
myReceiver = IRrecvPCI.IRrecvPCI(ir_inpin) # pin needs to be capable of interrupts
myReceiver.enableIRIn()
print("Time to push a button!")

# Make the display context
group = displayio.Group(max_size=10)
display.show(group)

# Draw a label
text = "BLADELIUS"
text_area = label.Label(
    terminalio.FONT, text=text, color=0xFFFFFF, x=28, y=HEIGHT // 2 - 1
)
group.append(text_area)
text_volume = label.Label(
    terminalio.FONT, text=text, color=0xFFFFFF, x=28, y=HEIGHT // 2 - 1
)
group.append(text_volume)

# PCF8574A Code
pcf = pcf8574.PCF8574(i2c, 0x39) ## A0=H, A1=L, A2=L

# Volume Control Code
cs = digitalio.DigitalInOut(board.D10)
cs.direction = digitalio.Direction.OUTPUT
cs.value = True

spi = bitbangio.SPI(board.D11, MOSI=board.D12)

while True:
    while (not myReceiver.getResults()):
        pass
    if myDecoder.decode():
        print("success")
        #  text = "Key Pushed: "
        #  text += str(myDecoder.value & 0xf7ff) # mask off the toggle bit
        remCode = myDecoder.value & 0xf7ff
        print("Remote Code is ", remCode)
        if (remCode == btnSrcUp) or (remCode == btnSrcDwn):
            if curInput == 8 and remCode == btnSrcUp:
                curInput = 0
            else:
                if remCode == btnSrcUp:
                    curInput += 1
                else:
                    print("SOURCE - was pressed")
                    if curInput == 0:
                        curInput = 8
                    else:
                        curInput -= 1
            while not i2c.try_lock():
                pass
            if curInput == 8:
                pcf.port = 0xF
            else:
                pcf.port = curInput
            i2c.unlock()
        print ("Current Input is: ")
        print(curInput)
        text = selInput[curInput]
        print(text)
        # print(myDecoder.dumpResults(True))
        text_area = label.Label(
           terminalio.FONT, text=text, color=0xFFFFFF, x=20, y=50
        )
        group[0] = text_area
        display.show(group)
        if (remCode == btnVolUp) or (remCode == btnVolDwn):
            if (curVol == 255) and (remCode == btnVolUp):
                curVol = curVol
            else:
                if remCode == btnVolUp:
                    curVol += 1
                else:
                    if curVol == 0:
                        curVol = curVol
                    else:
                        curVol -= 1
            while not spi.try_lock():
                pass
            print("Current volume is: ", curVol)
            spi.configure(baudrate=500000, phase=1, polarity=1)
            cs.value = False
            spi.write(bytes([curVol, curVol]))
            #spi.write(bytes([0xC9, 0xC9]))
            cs.value = True
            spi.unlock()
            text = "Vol: " + str(curVol)
            text_volume = label.Label(
                terminalio.FONT, text=text, color=0xFFFFFF, x=20, y=10
            )
            group[1] = text_volume
            display.show(group)
            print(text)
    #  else:
        #  print("It failed")
    #  myDecoder.dumpResults(False)
    #  myReceiver.enableIRIn()