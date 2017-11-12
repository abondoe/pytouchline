#!/usr/bin/python3

from touchline import Touchline

touchline = Touchline()

numberOfDevices = int(touchline.get_number_of_devices("http://192.168.1.10"))
device1 = Touchline(id=1)
device1.update()
print(device1.get_name())
print(device1.get_current_temperature())
print(device1.get_target_temperature())