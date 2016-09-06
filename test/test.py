### this is just a test file, the actual rpicenter class still not implmented.
from Display import Display
import time

def main():
    disp = Display()
    try:
        #disp.showMessage("Hello Friend",2,2)
        disp.showImage("happycat_oled_64.ppm")
        time.sleep(5)
    except KeyboardInterrupt:
        print("Shutdown requested...exiting")
    finally:
        disp.clear()
        exit_handler()

def exit_handler():    
    print("App terminated, cleanup!")

if __name__ == '__main__':
    main()



