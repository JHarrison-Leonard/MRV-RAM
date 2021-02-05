import RPi.GPIO as IO
import time
import os
import sys
import subprocess as blucheck
os.system('sudo pigpiod')
time.sleep(1)
import pigpio
import pygame
from pygame.locals import *

Ps3MAC = "00:19:C1:15:D9:F8" # FCC-ID AK8CECHZC01 Serial # 047012203328 Sony Wireless Controller

pygame.init()
discon=False

def check_pad():
    global discon
    global joystick
    global axis
    print('check')
    pygame.joystick.quit()
    pygame.joystick.init()
    joystick_count=pygame.joystick.get_count()
    print('count: %s' % joystick_count)
    if joystick_count == 0:
        if not discon:
            print ("reconnect controller")
            time.sleep(0.2)
            check_pad()
    else:
        for i in range(joystick_count):
            joystick=pygame.joystick.Joystick(0)
            joystick.init()
            axis=joystick.get_numaxes()

def accel():  # 1300 is the value for stable position of the DC motor
    if joystick.get_axis(1) > 0.3 or joystick.get_axis(1) < -0.3:  
        throttle=1300+int(joystick.get_axis(1)*100) # negative for forward, positive for backward
    else: throttle=1300
    return(throttle)
        
def turning(): # 1540 is "straight" with respect to the MRV body.
    if joystick.get_axis(2) < -0.3: # negative for turning left
        steer = 1540+int(355*joystick.get_axis(2))
    elif joystick.get_axis(2) > 0.3: # positive for turning right
        steer = 1540+int(370*joystick.get_axis(2))
    else: steer = 1540
    return(steer)


servo=23  # GPIO 23, Pin 7
esc = 10  # GPIO 10, Pin 19
i=0
print("w/s: acceleration")
print("a/d: steering")
print("esc: exit")
count= 0
check_pad()
pi=pigpio.pi()

pi.set_servo_pulsewidth(esc,0)
time.sleep(1)
pi.set_servo_pulsewidth(esc,1300)
time.sleep(1)
pi.set_servo_pulsewidth(esc,0)
time.sleep(1)
pi.set_servo_pulsewidth(esc,1300)
print("calibrated")
joystick_count=pygame.joystick.get_count()
if joystick_count !=1:
    joystick_count=pygame.joystick.get_count()
    print('count: %s' % joystick_count)
    check_pad()
while True:
   #test,
   pygame.event.pump()
   pi.set_servo_pulsewidth(esc,accel())
   pi.set_servo_pulsewidth(servo,turning())
   print(accel() ," , ", turning())
   if count == 15000:
       count = 0
       BLU_T = blucheck.getoutput('hcitool con')
       test = Ps3MAC in BLU_T  
       if test == False:
           check_pad()
   else:
       count += 1
