#include <stdio.h>
#include <avr/io.h>
#include <util/setbaud.h>
#include "serialIO.h"

void initialize_UART()
{
	// Set baud values properly according to the setbaud util
	UBRR0H = UBRRH_VALUE;
	UBRR0L = UBRRL_VALUE;
	#if USE_2x
	UCSR0A |= _BV(U2X0);
	#else
	UCSR0A &= ~(_BV(U2X0));
	#endif
	
	UCSR0C = _BV(UCSZ01) | _BV(UCSZ00); // 8-bit data
	UCSR0B = _BV(RXEN0) | _BV(TXEN0);   // Enable RX and TX
}

void putchar_UART(char c, FILE * stream)
{
	if(c == '\n')  // Carraige return before newlines
		putchar_UART('\r', stream);
	loop_until_bit_is_set(UCSR0A, UDRE0);
	UDR0 = c;
}

char getchar_UART(FILE * stream)
{
	loop_until_bit_is_set(UCSR0A, RXC0);
	return UDR0;
}

FILE out_UART = FDEV_SETUP_STREAM(putchar_UART, NULL, _FDEV_SETUP_WRITE);
FILE in_UART = FDEV_SETUP_STREAM(NULL, getchar_UART, _FDEV_SETUP_READ);
