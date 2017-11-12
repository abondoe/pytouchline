#!/usr/bin/python3

from pytouchline import PyTouchline

py_touchline = PyTouchline()

numberOfDevices = int(py_touchline.get_number_of_devices("http://192.168.1.10"))
devices = []
for x in range(0, numberOfDevices):
	devices.append(PyTouchline(id=x))
	devices[x].update()
	print(devices[x].get_name())
	print(devices[x].get_current_temperature())
	print(devices[x].get_target_temperature())