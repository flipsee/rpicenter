# rpicenter
Rpicenter is a library to manage Raspberry Pi GPIO pin usage and booking when using multiple sensors and actuators


in this design rpicenter will only be a gateway to call the device
- recipe will be at the service that call the rpicenter side
- do we need loop of the device or should it be on the caller side?
- remote device?

rpicenter method?
- register device.
    - put in arr.
    - check makesure that no duplicate.
- list device.
- list method in device.
- search device by name\location\???
- cleanup.

