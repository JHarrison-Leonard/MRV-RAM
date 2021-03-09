#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <avr/io.h>
#include <string.h>

#include "main.h"
#include "serialIO.h"


int main()
{
	// Variable definitions
	char input[256];
	
	// Initialize PWM clocks and pins
	initialize_PWM();
	
	// Initialize UART and std IO with serialIO
	initialize_UART();
	stdout = &out_UART;
	stdin = &in_UART;
	
	
	// Main loop
	for(;;)
	{
		// Get serial input
		gets(input);
		
		// Respond with MODULE_NAME if it probes
		if(!strcmp(input, MODULE_PROBE_STRING))
			printf("%s\n", MODULE_NAME);
		else
		{
			// Change servo pulsewidth given servo select character
			switch(input[0])
			{
				case SHOULDER_CHAR:
					set_shoulder(atoi(input + 1));
					break;
			}
		}
	}
}


void initialize_PWM()
{
	// Initialize 8-bit clock 0
	TCCR0A |= _BV(WGM01) | _BV(WGM00);
	TCCR0B |= _BV(WGM02);
	// TODO Need to use clock 2 interrupts to change T0
	// to get finer control of clock 0 to get a 20 ms period
	
	// Initialize 16-bit clock 1
	TCCR1A &= ~_BV(WGM10);                // <-- Sets timer 1 to fast PWM mode
	TCCR1A |= _BV(WGM11);                 //   | with TOP equaling ICR1
	TCCR1B |= _BV(WGM13) | _BV(WGM12);    // <-/
	TCCR1B &= ~_BV(CS10);                 // <-- Sets prescaler to 1/8
	TCCR1B |= _BV(CS11);                  // <-/
	ICR1 = (F_CPU / 8) / SERVO_FREQUENCY; // Sets timer 1 TOP to get 20 ms period
	
	// Initialize shoulder pwm
	DDRB |= _BV(PORTB1);                     // Pin 9 out
	TCCR1A |= _BV(COM1A1) | _BV(COM1A0);     // Inverting pulse (off then on)
	OCR1A = ICR1 - 2*(SHOULDER_DEFAULT) - 1; // Default pulse width
	
	// Initialize elbow pwm
	DDRB |= _BV(PORTB2);                  // Pin 10 out
	TCCR1A |= _BV(COM1B1) | _BV(COM1B0);  // Inverting pulse (off then on)
	OCR1B = ICR1 - 2*(ELBOW_DEFAULT) - 1; // Default pulse width
	
	// Initialize wrist pwm
	
	// Initialize claw pwm
}

void set_shoulder(uint16_t width)
{
	// Don't change pulsewidth if width is outside of safe bounds
	if(SHOULDER_MIN <= width && width <= SHOULDER_MAX)
		OCR1A = ICR1 - 2*width - 1;
}

void set_elbow(uint16_t width)
{
	// Don't change pulsewidth if width is outside of safe bounds
	if(ELBOW_MIN <= width && width <= ELBOW_MAX)
		OCR1B = ICR1 - 2*width - 1;
}

void set_wrist(uint8_t width)
{
}

void set_claw(uint8_t width)
{
}
