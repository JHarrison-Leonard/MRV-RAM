# MRV-RAM
Modular Remote Vehicle - Robotic Arm Module

## Installation
This has already been installed on the MRV, though these were the steps taken:
1. Download this repository into `/usr/local/` on the MRV and change the folder name to `MRV`.
2. Add the following lines to `/etc/rc.local`:
```
pigpiod &
/usr/local/MRV/ModuleCommv2.py &
/usr/local/MRV/PS3RCv2.py &
```

## File overview
- [PS3RCv2.py](PS3RCv2.py) Rewrite of original MRV code. Handles car control using the PS3 controller
- [ModuleCommv2.py](ModuleCommv2.py) Rewrite of original MRV code. Handles communication between MRV and modules, as well as executing module specific code
- modules
  - MDM
    - [MDM](modules/MDM/MDM) Recreation of MDM manager code. Acts as new manager for original MDM as well as demo code for piped serial manager type
  - RAM
    - [RAM](modules/RAM/RAM) RAM manager code
    - AVR
      - [main.c](modules/RAM/AVR/main.c) Main C file for RAM Arduino
      - [main.h](modules/RAM/AVR/main.h) Header file for main.c
      - [serialIO.c](modules/RAM/AVR/serialIO.c) Simple serial handler for Arduino
      - [serialIO.h](modules/RAM/AVR/serialIO.h) Header file for serialIO.c
      - [Makefile](modules/RAM/AVR/Makefile) Allows for easy compiling of RAM arduino code with `make` and upload with `make deploy`

## Process flow diagrams
- TODO PS3RCv2.py
- TODO ModuleCommv2.py
- TODO RAM

## Coding your own module manager
TODO
