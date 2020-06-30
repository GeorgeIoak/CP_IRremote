import board
import busio
import displayio
import terminalio
import IRLib_P03_RC5d  # We only need to decode RC5
import IRrecvPCI
from adafruit_display_text import label
import adafruit_displayio_ssd1306
import digitalio
import pcf8574

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
btnVolUp = 0x121b
btnSrcUp = 4631
btnSrcDwn = 4636

curInput = 0 #What Source Input are we currently at

displayio.release_displays()

#oled_reset = -1 # Change to -1 if reset pin isn't available
ir_inpin = board.D12 # Change to the pin that the TSOP4438 recevier is connected to

# Use for I2C
i2c = board.I2C()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)

myDecoder = IRLib_P03_RC5d.IRdecodeRC5()
myDecoder.ignoreHeader = True # My improve decoding weak signals
myReceiver = IRrecvPCI.IRrecvPCI(ir_inpin) # pin needs to be capable of interrupts
myReceiver.enableIRIn()
print("Time to push a button!")

WIDTH = 128
HEIGHT = 64  # Change to 32 if needed
BORDER = 5

display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT)

# Make the display context
group = displayio.Group(max_size=10)
display.show(group)

# Draw a label
text = "Hello World!"
text_area = label.Label(
    terminalio.FONT, text=text, color=0xFFFFFF, x=28, y=HEIGHT // 2 - 1
)
group.append(text_area)

# PCF8574A Code
pcf = pcf8574.PCF8574(i2c, 0x3F)

while True:
    while (not myReceiver.getResults()):
        pass
    if myDecoder.decode():
        print("success")
        text = "Key Pushed: "
        text += str(myDecoder.value & 0xf7ff) # mask off the toggle bit
        if (myDecoder.value & 0xf7ff) == btnSrcUp:
            if curInput == 8:
                curInput = 0
            else:
                curInput += 1
            while not i2c.try_lock():
                pass
            if curInput == 8:
                pcf.port = 0xF
            else:
                pcf.port = curInput
            i2c.unlock()
        print ("Current Input is: ")
        print(curInput)
        print(text)
        text_area = label.Label(
           terminalio.FONT, text=text, color=0xFFFFFF, x=20, y=50
        )
        group[0] = text_area
        display.show(group)
    #  else:
        #  print("It failed")
    #  myDecoder.dumpResults(False)
    #  myReceiver.enableIRIn()