# Python Library for Roth Touchline

A simple helper library for controlling a Roth Touchline heat pump controller

```py

from pytouchlineplus import PyTouchline

py_touchline = PyTouchline()

numberOfDevices = int(py_touchline.get_number_of_devices("http://192.168.1.10"))
device1 = PyTouchline(id=1)
device1.update()
print(device1.get_name())
print(device1.get_current_temperature())
print(device1.get_target_temperature())
```
