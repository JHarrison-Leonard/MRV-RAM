#!/usr/bin/python3

# Rewritten PS3 RC code for MRV
# Justin Leonard with team "They Might be Heisenberg"

# This was written to replace the existing RC code for the MRV
# Primary changes and general rundown:
# - Globalizaton of constants for easier configuration and readabiliy
# - Optimizations to the controller reconnect code
# -- Was given its own thread to simply it's calls
# -- Using threading.Timer to allow for more exact scheduling
# - Uses pygame events instead of brute force polling for faster, cleaner code

import time
import pygame
import threading
import pigpio
import subprocess



# GPIO pin definitions
GPIO_esc   = 10 # GPIO 10, Pin 19
GPIO_servo = 23 # GPIO 23, Pin 7


# Controller MAC
#controller_MAC = "00:19:C1:15:D9:F8" # MRV PS3 controller
controller_MAC = "70:20:84:5E:F7:5E" # TMBH PS4 controller

# Controller axis and button definitions
controller_forward = 1 # Forward and backward of left joystick
controller_steer   = 2 # Left and right of right joystick
controller_turbo   = 4 # Front left bumper (L1)

# Controller check interval/rate
controller_check_interval = 10 #seconds
controller_init_retry_interval = 0.2 #seconds
controller_init_retry_max = controller_check_interval / controller_init_retry_interval

# Motor straight/stable values
motor_forward_stable = 1300
motor_steer_straight = 1540


# pygame event whitelist
desired_pygame_events = [pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP]



# Function that re-intializes pygame controllers and retries controller_init_retry_max times
# The point of the retry is to 1) keep the function from overflowing from to many recursions
# and 2) not overlap check_controller stacks when the controller_manager calls it after
# controller_check_interval seconds later
def check_controller(discon=False, attempts=0):
	# Exit recursion if controller not connected after controller_check_interval seconds
	if attempts >= controller_init_retry_max:
		return
	
	pygame.joystick.quit()
	pygame.joystick.init()
	joystick_count=pygame.joystick.get_count()
	if not joystick_count:
		if not discon:
			print("Controller disconnected")
			discon = True
		time.sleep(controller_init_retry_interval)
		check_controller(discon, attmempts+1)
	else:
		for i in range(joystick_count):
			joystick = pygame.joystick.Joystick(i)
			joystick.init()

# Function designed to create and run within it's own thread. Runs every controller_check_interval
# seconds. Checks whether or not the controller defined by controller_MAC is still connected and
# run check_controller to being re-initializaing the pygame controller if it isn't
# TODO find a more python way to check for the controller connection in place of subprocess
def controller_manager():
	t=threading.Timer(controller_check_interval, controller_manager)
	t.daemon = True
	t.start()
	
	blu = subprocess.getoutput("hcitool con")
	if not controller_MAC in blu:
		check_controller()


# Given a pygame JOYAXISMOTION event, modifies the pulse width on the GPIO pin corresponding with
# the drive motor.
# TODO turbo
def accel_event(event):
	global pi
	
	throttle = motor_forward_stable
	if event.value < -0.3 or 0.3 < event.value:
		throttle += int(event.value*100)
	pi.set_servo_pulsewidth(GPIO_esc, throttle)

# Given a pygame JOYAXISMOTION event, modifies the pulse width on the GPIO pin corresponding with
# the steer servo.
def steer_event(event):
	global pi
	
	steer = motor_steer_straight
	if event.value < -0.3:
		steer += int(event.value*355)
	elif 0.3 < event.value:
		steer += int(event.value*370)
	pi.set_servo_pulsewidth(GPIO_servo, steer)

# TODO Placeholders for when I figure out the logic for turbo
def turbo_on_event(event):
	print("Turbo \"on\"")

def turbo_off_event(event):
	print("Turbo \"off\"")

# Function desiged to run on the same thread that pygame was initialized in. Waits for an event
# listed in desired_pygame_events. If it is a JOYAXISMOTION event, calls accel_event or steer_event
# if the axis is controller_forward or controller_steer respectively. If it is a JOYBUTTONDOWN event
# and the button is controller_turbo, calls turbo_on_event. If it is a JOYBUTTONUP event and the
# button is cntroller_turbo, calls turbo_on_event
# TODO Update documentation and code for actual turbo implementation
def event_manager():
	while True:
		event = pygame.event.wait()
		if event.type is pygame.JOYAXISMOTION:
			if event.axis is controller_forward:
				accel_event(event)
			elif event.axis is controller_steer:
				steer_event(event)
		elif event.type is pygame.JOYBUTTONDOWN:
			if event.button is controller_turbo:
				turbo_on_event(event)
		elif event.type is pygame.JOYBUTTONUP:
			if event.button is controller_turbo:
				turbo_off_event(event)


# Main function for remote control of MRV. Can run on it's own thread. Initializes pigpio object,
# calibrates the ESC, initializes pygame, establishes the allowed pygame events, initializes the
# controller, and calls the controller manager and controller event manager.
# TODO pass the pigpio object instead of leaving it global
def RCPi():
	global pi
	
	# Initialize pi and quit if it fails
	pi = pigpio.pi()
	if not pi.connected:
		print("pigpio daemon not running")
		exit()
	
	# Calibrate motors? Unsure how necessary this is, need to test without later
	pi.set_servo_pulsewidth(GPIO_esc, 0)
	time.sleep(1)
	pi.set_servo_pulsewidth(GPIO_esc, motor_forward_stable)
	time.sleep(1)
	pi.set_servo_pulsewidth(GPIO_esc, 0)
	time.sleep(1)
	pi.set_servo_pulsewidth(GPIO_esc, motor_forward_stable)
	
	
	# Initialize pygame, event queue seems to work fine without a display
	pygame.init()
	# Set list of events allowed in event queue to desired_events
	pygame.event.set_blocked(None) # Blocks all events
	pygame.event.set_allowed(desired_pygame_events)
	
	# Initialize controller
	check_controller()
	
	# Call managers
	controller_manager()
	event_manager()



# Run RCPi in a new thread, run as a daemon for clean exit
thread_RCPi = threading.Thread(target=RCPi, daemon=True)
thread_RCPi.start()

while(True):
	# placeholder for ModuleComm.py rewrite
	time.sleep(1)
