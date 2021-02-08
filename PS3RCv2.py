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
import queue
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
controller_deadzone_upper = 0.3
controller_deadzone_lower = -0.3

# Controller check interval/rate
controller_check_interval = 10 #seconds
controller_init_retry_interval = 0.2 #seconds
controller_init_retry_max = controller_check_interval / controller_init_retry_interval

# Speed manager update interval
speed_change_max = 100 #pulse width per interval
speed_change_interval = 0.1 #seconds

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
# I would like to use a proper library instead of subprocess with hcitool, but pybluez can't
def controller_manager():
	while True:
		if not controller_MAC in subprocess.getoutput("hcitool con"):
			check_controller()
		time.sleep(controller_check_interval)


# TODO speed_calc documentation
# TODO Globally define throttle weighting and turbo modifier
def speed_calc(axis_value, turbo):
	throttle = motor_forward_stable
	if axis_value < controller_deadzone_lower or controller_dead_upper < axis_value:
		if turbo:
			axis_value *= 2
		throttle += int(axis_value*100)
	return throttle

# TODO speed_manager documentation
# TODO If possible, make this not quite as redundant
def speed_manager(gpio_controller, event_queue):
	turbo = False
	target_axis = 0.0
	target_speed = motor_forward_stable
	current_speed = motor_forward_stable
	
	while True:
		if current_speed is taget_speed:
			event = event_queue.get()
			if event.type is pygame.JOYAXISMOTION:
				target_axis = event.value
			elif event.type is pygame.JOYBUTTONDOWN:
				turbo = True
			elif event.type is pygame.JOYBUTTONUP:
				turbo = False
			target_speed = speed_calc(target_axis, turbo)
			event_queue.task_done()
			
		else:
			time.sleep(speed_change_interval)
			try:
				event = event_queue.get_nowait()
				if event.type is pygame.JOYAXISMOTION:
					target_axis = event.value
				elif event.type is pygame.JOBUTTONDOWN:
					turbo = True
				elif event.type is pygame.JOYBUTTONUP:
					turbo = False
				target_speed = speed_calc(target_axis, turbo)
				event_queue.task_done()
			except queue.Empty as e:
				pass
		
		current_speed += max(min(target_speed-current_speed, speed_change_max), -speed_change_max)
		gpio_controller(GPIO_esc, current_speed)


# Given a pygame JOYAXISMOTION event, modifies the pulse width on the GPIO pin corresponding with
# the steer servo.
# TODO Globally define left and right steer weightings
def steer_event(event, gpio_controller):
	steer = motor_steer_straight
	if event.value < controller_deadzone_lower:
		steer += int(event.value*355)
	elif controller_deadzone_upper < event.value:
		steer += int(event.value*370)
	gpio_controller.set_servo_pulsewidth(GPIO_servo, steer)

# Function desiged to run on the same thread that pygame was initialized in. Waits for an event
# listed in desired_pygame_events. If it is a JOYAXISMOTION event, calls accel_event or steer_event
# if the axis is controller_forward or controller_steer respectively. If it is a JOYBUTTONDOWN event
# and the button is controller_turbo, calls turbo_on_event. If it is a JOYBUTTONUP event and the
# button is cntroller_turbo, calls turbo_on_event
# TODO Update documentation and code for actual turbo implementation
# TODO Implement cleanup on pygame.QUIT event
def event_manager(gpio_controller):
	speed_events = queue.Queue()
	thread_speed_manager = threading.Thread(target=speed_manager, args=(gpio_controller, speed_events), daemon=True)
	thread_speed_manager.start()
	
	while True:
		event = pygame.event.wait()
		if event.type is pygame.JOYAXISMOTION:
			if event.axis is controller_forward:
				speed_events.put(event)
			elif event.axis is controller_steer:
				steer_event(event, gpio_controller)
			
		elif event.type is pygame.JOYBUTTONDOWN:
			if event.button is controller_turbo:
				speed_event.put(event)
			
		elif event.type is pygame.JOYBUTTONUP:
			if event.button is controller_turbo:
				speed_event.put(event)


# Main function for remote control of MRV. Can run on it's own thread. Initializes pigpio object,
# calibrates the ESC, initializes pygame, establishes the allowed pygame events, initializes the
# controller, and calls the controller manager and controller event manager.
def RCPi():
	# Initialize pigpio client and quit if it fails
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
	thread_controller_manager = threading.Thread(target=controller_manager, daemon=True)
	thread_controller_manager.start()
	event_manager(pi)



# Run RCPi in a new thread
thread_RCPi = threading.Thread(target=RCPi)
thread_RCPi.start()
