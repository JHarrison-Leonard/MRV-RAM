#!/usr/bin/python3

# Rewritten module communication manager code for MRV
# by Justin Leonard with team "They Might be Heisenberg"

# This code manages the serial communication with the modules connected to
# the MRV. It constantly searches for a serial device connected to the
# USB port that the leads to the enclosure housing. When a serial device
# is connected, it probes the device to ask for its name. It then asks the
# prgram that handles that module for a communication type and passes
# through the serial communication accordingly.
# There are currently two types of pass through:
# - "piped serial"
# -- Pipes the serial filestream through to the programs stdin and stdout
# -- Has some quirks addressed in the MDM demo code modules/MDM/MDM
# - "full serial"
# -- Passes the serial device as an argument to the program
# -- Program has to initialize serial device itself

import serial
import serial.tools.list_ports as serial_find # For comports()
import subprocess
import time


# Module USB port definition
module_usb_port = "1-1.2" # Bottom USB 3.0 port

# Module executables directory
module_bin_path = "/usr/local/MRV/modules/"

# Serial communication probe string for asking for the module's name when connected
module_probe_string = b"Module?\n"

# Probe delay to keep from occasionally locking up the serial interface
module_probe_interval = 0.01 #seconds

# Serial communications settings
serial_baud_rate = 19200
serial_parity    = serial.PARITY_NONE
serial_stopbits  = serial.STOPBITS_ONE
serial_bytesize  = serial.EIGHTBITS
serial_timeout   = 0.01 #seconds



# Returns a serial_find object for a serial device connected to module_usb_port, if
# available. Retuns None if no serial device is connected.
def port_scan():
	scan = serial_find.comports()
	for ser in scan:
		if  module_usb_port in str(ser.location):
			return ser
	return None

# Given an instantiated serial device, attempts to send the module_probe_string and
# read the result, which is expected to be the name of the module
def serial_probe(serial_device):
	serial_device.write(module_probe_string)
	return serial_device.readline().decode("utf-8").rstrip()

# Function to instantiate a serial device given it's path and using values defined
# under Serial communication settings. This is really just to keep this massive
# block of macros out of readable code.
def serial_build(serial_device_path):
	return serial.Serial(
			port     = serial_device_path,
			baudrate = serial_baud_rate,
			parity   = serial_parity,
			stopbits = serial_stopbits,
			bytesize = serial_bytesize,
			timeout  = serial_timeout)



# Main loop. This code is never meant to close itself, therefore loops forever.
while True:
	module_device_info = port_scan()
	if module_device_info is not None:
		# Probe module until a response is supplied as the serial device will
		# give empty strings until the module finishes booting.
		# If there is an exception (device disconnected) restart scanning
		ser = None
		module_name = ""
		try:
			ser = serial_build(module_device_info.device)
			while module_name == "":
				module_name = serial_probe(ser)
				time.sleep(module_probe_interval)
		except serial.SerialException as e:
			pass
		
		else:
			print("Module connected:", module_name)
			
			# Checks the module name for backslash and null characters, which
			# are illegal in linux file names. This keeps a module from executing
			# arbitrary code on the system.
			if '\0' in module_name or '/' in module_name:
				ser.close()
				print("Invalid module name:", module_name)
				
			else:
				# Obtain module manager type from it's associated program
				module_manager_path = module_bin_path + module_name + "/" + module_name
				module_manager_type = subprocess.check_output([module_manager_path, "type"]).rstrip().decode("utf-8")
				
				# Run module manager and pass through module how it expects
				if  module_manager_type == "piped serial":
					print("Module manager type:", module_manager_type)
					p = subprocess.Popen([module_manager_path], stdin=ser, stdout=ser)
					while port_scan() is not None and p.poll() is None:
						time.sleep(module_probe_interval) # Loops until module is disconnected or manager closes
					p.kill()
					ser.close()
					
				elif module_manager_type == "full serial":
					print("Module manager type:", module_manager_type)
					ser.close()
					subprocess.call([module_manager_path, "--serial-path", module_device_info.device])
					
				else:
					ser.close()
					print("Unknown module manager type:", module_manager_type)
			
			print("Module disconnected")
