from devices.device import Device, command
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
        super(Display,self).__init__(device_object_id, slot, gpio_pin, location, is_local)

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

    @command
    def clear(self):
        # Clear display.
        logger.debug("Clearing Display")
        self.cleanup()

    @command
    def show_message(self, msg, x=1, y=1):
        logger.debug("Showing Msg: " + str(msg))
        self.draw.text((x, y), str(msg),  font=self.font, fill=255)
        self.disp.display()
        #self.__display__()

    @command
    def show_image(self, imgName):
        logger.debug("Showing Image: " + str(imgName))
        self.image = Image.open(imgName).resize((self.disp.width, self.disp.height), Image.ANTIALIAS).convert('1')
        self.disp.image(self.image)
        self.disp.display()
        #self.__display__()
    
    def cleanup(self):
        self.disp.clear()
        self.disp.display()    

    def __display__(self):
        self.disp.image(self.image)
        self.disp.display()

