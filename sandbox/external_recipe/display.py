from rpicenter import Device
import rpicenter

import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

class Display(Device):
    # Raspberry Pi pin configuration:
    RST = 24
    # Note the following are only used with SPI:
    #DC = 23
    #SPI_PORT = 0
    #SPI_DEVICE = 0

    def __init__(self, device_object_id, slot, gpio_pin, location, is_local=True):
        super(Display, self).__init__(device_object_id, slot, gpio_pin, location, is_local)

        self.disp = Adafruit_SSD1306.SSD1306_128_32(rst=self.RST)
        self.disp.begin()
        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        self.image = Image.new('1', (self.disp.width, self.disp.height))

        # Get drawing object to draw on image.
        self.draw = ImageDraw.Draw(self.image)

        # Draw a black filled box to clear the image.
        self.draw.rectangle((0,0,self.disp.width,self.disp.height), outline=0, fill=0)

        # Load default font.
        self.font = ImageFont.load_default()
        #print("Initiating Display")

    @rpicenter.command
    def clear(self):
        # Clear display.
        #print("Clearing Display")
        self.disp.clear()
        self.disp.display()    
        return self    

    @rpicenter.command
    def show_message(self, msg, x=1, y=1):
        #print("Showing Msg")
        self.draw.text((x, y), str(msg),  font=self.font, fill=255)
        self.__display__()
        return self

    @rpicenter.command
    def show_image(self, imgName):
        #print("Showing Image")
        self.image = Image.open(imgName).resize((self.disp.width, self.disp.height), Image.ANTIALIAS).convert('1')
        self.__display__()
        return self
    
    def __display__(self):
        self.disp.image(self.image)
        self.disp.display()
        return self
