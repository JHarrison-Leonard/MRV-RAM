#Team Rhodium 2020
#Module Code

#Youtube video detailing how this code works: https://www.youtube.com/watch?v=ub82Xb1C8os

import serial,sys,glob,select,time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(21,GPIO.OUT)
GPIO.setup(4,GPIO.OUT)
global Connect
global dev
global scan
global serport
global ser
global rate
Connect = 0
rate = "19200"

def portScan(): #Function to constantly scan for USB - This will identify and set up the appropriate USB port
    global Connect
    global dev
    global scan
    global serport
    global ser
    dev  = "/dev/ttyACM*"
    scan = glob.glob(dev)
    rate = "19200"
    if (len(scan) == 0):
        dev  = '/dev/ttyUSB*'
        scan = glob.glob(dev)
        if (len(scan) == 0):
            print ("Unable to find any ports scanning for /dev/[ttyACM*|ttyUSB*]" + dev)
            return # If unable to find any ports return back to main
    try:
        serport = scan[0] ###
        ser = serial.Serial(port=serport,baudrate=rate,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=.01)
        Connect = 1 # If connection is made set set Connect to 1 (True) (USB Connected)
    except (serial.SerialException, BrokenPipeError) as e:  # pywintypes.error as e:
        Connect = 0
        return

def serialTalk(x): # Function handles Serial Communication being sent and received
                   # This implementation of this function allows for hot unplugging
    
        global Connect
        global dev
        global scan
        global serport
        global ser
        
        try:
            ser.write(x)
            line = ser.readline().decode('utf-8').rstrip()
            #print(line) # Uncomment if you want to see the line printed in the shell
            return True, line
        except (serial.SerialException, BrokenPipeError) as e: #Handle Exception
            Connect = 0 # If connection is not made set set Connect to 0 (False) (USB not connected)
            return False, ""
        
##########################################################    MAIN    ###################################################################################
        
if __name__ == '__main__':
    Connect = 0
    GPIO.output(21,GPIO.LOW)
    GPIO.output(4,GPIO.LOW)
# 
    while(Connect == 0):
        portScan() # Function to constantly scan for USB - This identifies and sets up the appropriate USB port
#     
        #print("Welcome")
            
########################################################## GET MODULE ###################################################################################
    
        while (Connect ==1):
            input_string = (b"Module?\n")# Raspberry Sends string to Module for Identification
            output_string = ("  ") # Set up response String for Module
            
            test, output_string = serialTalk(input_string)  # Send Arguments to function:
                                                            # input_string is what is sent to module
                                                            # output_string is what is returned from module

            if(test == False): # If test == False - The USB is disconnected                        #serialTalk#1: Start
                               
                #print("F")
                Connect = 0    # Connect = 0 (Module has been disconnected)
                               # Return to main and wait for Module to be Connected
                
            if(test == True):  # output_string is returned from serialTalk function
                               # This output string Determines which module to run
                               
                #print(output_string) # Uncomment print if you wish to see output in Shell
                                                                                                  #serialTalk#1: Finish 

########################################################## MDM MODULE START #############################################################################
                               
                if(output_string == ("MDM")): # If Module identifies as MDM
                   input_string2 = (b"Recognized\n") # Raspberry Sends string to MDM for Hand Shaking
                   output_string2 = ("  ") # Set up response String for Module
                   
        #** If MDM module accepts hand shake we should see the Green LED on the MDM light up **#
#------------------------------------------------------------------------------------------------------------------------------------------------------#                 
                                                     
                   
                   test, output_string2 = serialTalk(input_string2) # Send Arguments to function:                      #serialTalk#2: Start
                                                                    # input_string2 is what is sent to MDM
                                                                    # output_string2 is what is returned from module
                   if(test == False):
                       #print("F")    # Uncomment print if you wish to see output in Shell
                       Connect = 0    # Connect = 0 (Module has been disconnected)
                                      # Return to main and wait for Module to be Connected
                                      
        #** Here we are doing another handshake - We are making sure the arduino is ready to transmit data**#

                   if(test == True):  # output_string2 is returned from serialTalk function
                                      # output_string2 should equal Ready                                          
                                       
                       #print(output_string2) # Uncomment print if you wish to see output in Shell               
                                                                                                                       #serialTalk#2: Finish        
#------------------------------------------------------------------------------------------------------------------------------------------------------#
                                      
                       if(output_string2 == ("Ready")): # If Response == Ready- 
                           input_string3 = (b"Metal?\n")  # Raspberry Sends string to MDM for Metal Detection
                           output_string3 = ("  ") # Set up response String for Module
                           loop=1 # loop set up to break out out while loop if USB disconnected
                           
                           while(loop == 1):            
                               test, output_string3 = serialTalk(input_string3) # Send Arguments to function:                      #serialTalk#3: Start
                                                                            # input_string3 is what is sent to MDM
                                                                            # output_string3 is what is returned from module
                                                                            # output_string3 should either be Detected or None
                               if(test == False):
                                   #print("F")    # Uncomment print if you wish to see output in Shell
                                   loop = 0
                                   Connect = 0    # Connect = 0 (Module has been disconnected)
                                                  # Return to main and wait for Module to be Connected
                                                  
                    #** Here we want to ping the MDM for voltage readings - If voltage is high we want to turn on Buzzer on Raspberry Pi**#

                               if(test == True):  # output_string3 is returned from serialTalk function
                                                  # output_string3 should equal either Detected or None                            serialTalk#3: Finish   
                                   if(output_string3 == "Detected"):
                                       GPIO.output(21,GPIO.HIGH)
                                       GPIO.output(4,GPIO.HIGH)
                                   else:
                                       GPIO.output(21,GPIO.LOW)
                                       GPIO.output(4,GPIO.LOW)
                                                                                                                                   #serialTalk#3: Finish
                                       
########################################################## MDM MODULE FINISH #############################################################################
                                       
                                       
########################################################## "DIFFERENT" MODULE START ######################################################################
                 
                 #SAMPLE CODE WHERE ANOTHER MODULE WOULD BE PLACED; ONLY FOR SERIAL COMMUNICATION DEVICES USING USB-B TYPE PORT  #
                 
                #elif(output_string == ("Silly")): # If Module identifies as Silly
                   #input_string2 = (b"Recognized\n") # Raspberry Sends string to Silly for Hand Shaking
                   #output_string2 = ("  ") # Set up response String for Module
                   
        #** If Silly module accepts hand shake we should see the Green LED on the Silly light up **#
        #                               
#------------------------------------------------------------------------------------------------------------------------------------------------------#
            
########################################################## "DIFFERENT" MODULE END ########################################################################

                                   