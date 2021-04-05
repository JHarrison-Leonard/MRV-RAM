#!/usr/bin/python3

# Rewritten PS3 RC code for MRV
# by Justin Leonard with team "They Might be Heisenberg"

# This was written to replace the existing RC code for the MRV
# Primary changes and general rundown:
# - Globalizaton of constants for easier configuration and readabiliy
# - Optimizations to the controller reconnect code
# -- Was given its own thread to simply it's calls
# -- Using threading.Timer to allow for more exact scheduling
# - Uses pygame events instead of brute force polling for faster, cleaner code
# - Gradually changes ESC pulsewidth to avoid ESC lock-up

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
controller_MAC = "00:19:C1:15:D9:F8" # MRV PS3 controller
#controller_MAC = "70:20:84:5E:F7:5E" # TMBH PS4 controller

# Controller axis and button definitions
controller_throttle = 1 # Forward and backward of left joystick
controller_steer    = 2 # Left and right of right joystick
controller_turbo    = 10 # Front left bumper (L1) PS3
#controller_turbo    = 4 # Front left bumper (L1) PS4
controller_deadzone_upper = 0.3
controller_deadzone_lower = -0.3

# Controller check interval/rate
controller_check_interval = 10 #seconds
controller_init_retry_interval = 0.2 #seconds
controller_init_retry_max = controller_check_interval / controller_init_retry_interval

# Speed manager lock-up surpression
speed_change_max = 100 #pulse width per interval
speed_change_interval = 0.1 #seconds

# Motor straight/stable and weightings
# Currently using Team Rhodium's values
motor_throttle_stable = 1300
motor_throttle_weighting = 100
motor_throttle_turbo_multiplier = 2
motor_steer_straight = 1540
motor_steer_left_weighting  = 355
motor_steer_right_weighting = 370

# pygame event whitelist
desired_pygame_events = [pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP]



# Function that re-intializes pygame controllers and retries controller_init_retry_max times
# The point of the retry is to 1) keep the function from overflowing from to many recursions
# and 2) not overlap check_controller stacks when the controller_manager calls it after
# controller_check_interval seconds later
def init_controller(attempts=0):
	# Exit recursion if controller not connected after controller_check_interval seconds
	if attempts >= controller_init_retry_max:
		return
	
	pygame.joystick.quit()
	pygame.joystick.init()
	joystick_count=pygame.joystick.get_count()
	if not joystick_count:
		time.sleep(controller_init_retry_interval)
		init_controller(attempts+1)
	else:
		for i in range(joystick_count):
			joystick = pygame.joystick.Joystick(i)
			joystick.init()

# Function designed run within it's own thread. Runs every controller_check_interval
# seconds. Checks whether or not the controller defined by controller_MAC is still connected and
# run check_controller to being re-initializaing the pygame controller if it isn't
# I would like to use a proper library instead of subprocess with hcitool, but pybluez can't
def controller_manager():
	while True:
		if not controller_MAC in subprocess.getoutput("hcitool con") or pygame.joystick.get_count() == 0:
			init_controller()
		else:
			time.sleep(controller_check_interval)


# Returns the appropriate ESC pulsewidth given a axis_value and boolean turbo. axis_value
# deviates throttle from motor_throtte_stable by a motor_throttle_weighting. turbo doubles
# the weighting of axis_vaue.
def speed_calc(axis_value, turbo):
	throttle = motor_throttle_stable
	if axis_value < controller_deadzone_lower or controller_deadzone_upper < axis_value:
		if turbo:
			axis_value *= motor_throttle_turbo_multiplier
		throttle += int(axis_value*motor_throttle_weighting)
	return throttle

# Speed and throttle manager. Designed to run in it's own thread with pygame.JOYAXISMOTION,
# pygame.JOYBUTTONDOWN, and pygame.JOYBUTTONUP events passed through via event_queue. The
# queued pygame events are expected to already be for throttle and turbo inputs and are not
# checked. Attempts to gradually set the current pulsewidth to an inputed target pulsewidth
# at a rate of speed_change_max / speed_change_interval.
def speed_manager(gpio_controller, event_queue):
	turbo = False
	target_axis = 0.0
	target_speed = motor_throttle_stable
	current_speed = motor_throttle_stable
	
	while True:
		if current_speed == target_speed:
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
				elif event.type is pygame.JOYBUTTONDOWN:
					turbo = True
				elif event.type is pygame.JOYBUTTONUP:
					turbo = False
				target_speed = speed_calc(target_axis, turbo)
				event_queue.task_done()
			except queue.Empty as e:
				pass
		
		current_speed += max(min(target_speed-current_speed, speed_change_max), -speed_change_max)
		#print("Current PWM:", current_speed, "Target PWM:", target_speed)
		gpio_controller.set_servo_pulsewidth(GPIO_esc, current_speed)


# Given a pygame JOYAXISMOTION event, modifies the pulse width on the GPIO pin corresponding with
# the steer servo.
def steer_event(event, gpio_controller):
	steer = motor_steer_straight
	if event.value < controller_deadzone_lower:
		steer += int(event.value*motor_steer_left_weighting)
	elif controller_deadzone_upper < event.value:
		steer += int(event.value*motor_steer_right_weighting)
	gpio_controller.set_servo_pulsewidth(GPIO_servo, steer)

# Function desiged to run on the same thread that pygame was initialized in. Waits for an event
# listed in desired_pygame_events. If it is a JOYAXISMOTION event, places the event on speed_events
# or calls steer_event if the axis is controller_throttle or controller_steer respectively.
# Passes through JOYBUTTONDOWN and JOYBUTTONUP events to speed_events if the buttonis controller_turbo.
def event_manager(gpio_controller):
	speed_events = queue.Queue()
	thread_speed_manager = threading.Thread(target=speed_manager, args=(gpio_controller, speed_events), daemon=True)
	thread_speed_manager.start()
	
	while True:
		event = pygame.event.wait()
		if event.type is pygame.JOYAXISMOTION:
			if event.axis is controller_throttle:
				speed_events.put(event)
			elif event.axis is controller_steer:
				steer_event(event, gpio_controller)
			
		elif event.type is pygame.JOYBUTTONDOWN:
			if event.button is controller_turbo:
				speed_events.put(event)
			
		elif event.type is pygame.JOYBUTTONUP:
			if event.button is controller_turbo:
				speed_events.put(event)

# Main function for remote control of MRV. Can run on it's own thread. Initializes pigpio object,
# calibrates the ESC, initializes pygame, establishes the allowed pygame events, initializes the
# controller, and calls the controller manager and controller event manager.
def RCPi():
	# Initialize pigpio client and quit if it fails
	pi = pigpio.pi()
	if not pi.connected:
		print("pigpio daemon not running")
		exit()
	
	# Seems to initialize the esc and/or calibrate the stable pulse width
	pi.set_servo_pulsewidth(GPIO_esc, 0)
	time.sleep(1)
	pi.set_servo_pulsewidth(GPIO_esc, motor_throttle_stable)
	time.sleep(1)
	pi.set_servo_pulsewidth(GPIO_esc, 0)
	time.sleep(1)
	pi.set_servo_pulsewidth(GPIO_esc, motor_throttle_stable)
	time.sleep(1)
	
	
	# Initialize pygame, event queue seems to work fine without a display
	pygame.init()
	# Set list of events allowed in event queue to desired_events
	pygame.event.set_blocked(None) # Blocks all events
	pygame.event.set_allowed(desired_pygame_events)
	
	# Initialize controller
	init_controller()
	
	# Call managers
	thread_controller_manager = threading.Thread(target=controller_manager, daemon=True)
	thread_controller_manager.start()
	event_manager(pi)



# Run RCPi
# If ever merged with ModuleCommv2.py, use treading to run in its own thread
RCPi()
