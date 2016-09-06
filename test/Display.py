import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

class Display():
    # Raspberry Pi pin configuration:
    RST = 24
    # Note the following are only used with SPI:
    DC = 23
    SPI_PORT = 0
    SPI_DEVICE = 0
    status = None
    lastchange = None

    def __init__(self): #, **kwargs):
        #for key, value in kwargs.items():
        #    setattr(self, key, value)
        #Device.__init__(self)
        RST = 24
        self.disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)
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
        print("Initiating Display")

    def clear(self):
        # Clear display.
        print("Clearing Display")
        self.disp.clear()
        self.disp.display()    
        return self    
    
    def display(self):
        # Display image.
        self.disp.image(self.image)
        self.disp.display()
        return self

    def showMessage(self, msg, x,y):
        print("Showing Msg")
        self.draw.text((x, y), str(msg),  font=self.font, fill=255)
        self.display()
        return self

    def showImage(self, imgName):
        print("Showing Image")
        self.image = Image.open(imgName).resize((self.disp.width, self.disp.height), Image.ANTIALIAS).convert('1')
        self.display()
        return self



