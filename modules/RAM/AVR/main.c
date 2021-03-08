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
				case SHOULDER_THETA_CHAR:
					set_shoulder_turn(atoi(input + 1));
					break;
			}
		}
	}
}


void initialize_PWM()
{
	// Initialize 16-bit clock
	TCCR1A |= _BV(WGM11);                 // <-- Sets timer 1 to fast PWM mode
	TCCR1B |= _BV(WGM13) | _BV(WGM12);    // <-/
	TCCR1B &= ~_BV(CS10);                 // <-- Sets prescaler to 1/8
	TCCR1B |= _BV(CS11);                  // <-/
	ICR1 = (F_CPU / 8) / SERVO_FREQUENCY; // Sets time 1 TOP to get 20 ms period
	
	// Initialize shoulder theta pwm
	DDRB |= _BV(PORTB1);                           // Pin 9 out
	TCCR1A |= _BV(COM1A1) | _BV(COM1A0);           // Inverting pulse (off then on)
	OCR1A = ICR1 - 2*(SHOULDER_TURN_DEFAULT) - 1; // Default pulse width
}

void set_shoulder_turn(uint16_t width)
{
	// Don't change pulsewidth if width is outside of safe bounds
	if(SHOULDER_TURN_MIN <= width && width <= SHOULDER_TURN_MAX)
		OCR1A = ICR1 - 2*width - 1;
}
