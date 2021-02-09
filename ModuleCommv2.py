#!/usr/bin/python3

# Rewritten module

import serial
import serial.tools.list_ports as serial_find # For comports()
import subprocess



# Module USB port definition
module_usb_port = "1-1.2:1.0" # Bottom USB 3.0 port

# Module executables directory
module_bin_path = "/home/pi/modules/"

# Serial communication probe string
module_probe_string = b"Module?\n"

# Serial communications settings
serial_buad_rate = 19200
serial_parity    = serial.PARITY_NONE
serial_stopbits  = serial.STOPBITS_ONE
serial_bytesize  = serial.EIGHTBITS
serial_timeout   = 0.01 #seconds



# Returns a serial_find object for a serial device connected to module_usb_port, if
# available. Retuns None if no serial device is connected.
def port_scan():
	scan = serial_find.comports()
	for ser in scan:
		if ser.location is module_usb_port:
			return ser
	return None

# TODO serial_probe documentation
def serial_probe(serial_device_path):
	try:
		ser = serial_build(serial_device_path)
		ser.write(module_probe_string)
		return ser.readline().decode("utf-8").rstrip()
	except (serial.SerialException, BrokenPipeError) as e:
		return None

# TODO serial_build documentation
def serial_build(serial_device_path):
	return serial.Serial(
			port     = serial_device_path,
			baudrate = serial_baud_rate,
			parity   = serial_parity,
			stopbits = serial_stopbits,
			bytesize = serial_bytesize,
			timeout  = serial_timeout)



# Main loop
while True:
	module_device_info = port_scan()
	if module_device_info is not None:
		module_name = serial_probe(module_device_info.device)
		if module_name is not None:
			ser = serial_build(module_device_info.device)
			try:
				subprocess.run([module_bin_path + module_name], stdin=ser, stdout=ser)
			except (serial.SerialException, BrokenPipeError) as e:
				pass
