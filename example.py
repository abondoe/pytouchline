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
	print(devices[x].get_target_temperature_high())
	print(devices[x].get_target_temperature_low())
	print(devices[x].get_week_program())
	print(devices[x].get_operation_mode())
	print(devices[x].get_device_id())
	print(devices[x].get_controller_id())
	print("-------------------------------------")

print(devices[0].set_name("Hovedsoverom"))
print(devices[0].set_target_temperature(22.5))
print(devices[0].set_target_temperature_high(30))
print(devices[0].set_target_temperature_low(5))
print(devices[0].set_week_program(0))
print(devices[0].set_operation_mode(0))
