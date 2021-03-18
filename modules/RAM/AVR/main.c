#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <avr/io.h>
#include <avr/interrupt.h>
#include <string.h>

#include "main.h"
#include "serialIO.h"



static uint8_t timer0_utop = 0;
static uint8_t timer0_ucnt = 0;
static uint8_t timer0_ucrb = 0;



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
	
	// Enable global interrupts
	sei();
	
	
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
				case ELBOW_CHAR:
					set_elbow(atoi(input + 1));
					break;
				case WRIST_CHAR:
					set_wrist(atoi(input + 1));
			}
		}
	}
}


void initialize_PWM()
{
	// Initialize 8-bit clock 0
	TCCR0A |= _BV(WGM01) | _BV(WGM00);                   // <-- Sets timer 1 to fast PWM mode
	TCCR0B |= _BV(WGM02);                                // <-/ with TOP and TOV at OCR0A
	TCCR0B &= ~_BV(CS02) & ~_BV(CS00);                   // <-- Sets prescaler to 1/8
	TCCR0B |= _BV(CS01);                                 // <-/
	OCR0A = G8BF((F_CPU / 8) / SERVO_FREQUENCY);         // Sets TOP to 8-bit factor of 20 ms
	timer0_utop = (F_CPU / 8) / SERVO_FREQUENCY / OCR0A; // Interrupts finalize 20 ms period
	TIFR0 &= ~_BV(TOV0);                                 // Clear overflow interrupt flag
	TIMSK0 |= _BV(TOIE0);                                // Enable overflow interrupt
	
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
	DDRD |= _BV(PORTD5);                                         // Pin 5 out
	TCCR0A &= ~_BV(COM0B1) & ~_BV(COM0B0);                       // Normal port operation
	OCR0B = OCR0A - (2*(WRIST_DEFAULT) % OCR0A) - 1;             // <-- Default pulse width
	timer0_ucrb = timer0_utop - (2*(WRIST_DEFAULT) / OCR0A) - 1; // <-/
	
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

void set_wrist(uint16_t width)
{
	// Don't change pulsewidth if width is outside of safe bounds
	if(WRIST_MIN <= width && width <= WRIST_MAX)
	{
		OCR0B = OCR0A - (2*width % OCR0A) - 1;
		timer0_ucrb = tmer0_utop - (2*width / OCR0A) - 1;
	}
}

void set_claw(uint16_t width)
{
	// Don't change pulsewidth ifwidth is outside of safe bounds
	if(CLAW_MIN <= width && width <= CLAW_MAX);
}

uint8_t G8BF(unsigned int n)
{
	for(uint8_t i = UINT8_MAX; i > 0; i--)
		if(n % i == 0)
			return i;
	return 1;
}



// ISR Definitions
ISR(TIMER0_OVF_vect)
{
	timer0_ucnt++;
	if(timer0_ucnt >= timer0_utop)
	{
		timer0_ucnt = 0;
		PORTD &= ~_BV(PORTD5);
	}
	else if(timer0_ucnt == timer0_ucrb)
	{
		TIFR0 &= ~_BV(OCF0B);
		TIMSK0 |= _BV(OCIE0B);
	}
}

ISR(TIMER0_COMPB_vect)
{
	PORTD |= _BV(PORTD5);
	TIMSK0 &= ~_BV(OCIE0B);
}
