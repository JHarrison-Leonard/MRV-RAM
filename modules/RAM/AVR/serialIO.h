#ifndef SERIALIO_H_
#define SERIALIO_H_
#include <stdio.h>

/* Simple serial IO implementation
 * 
 * By including and adding initialize_UART(), enables serial communication
 * over stdin and stdout, allowing for use of standard C IO methods.
 */



/* stdio compatiable file stream structures
 * Allows for use of functions like gets for easier IO
 */
FILE out_UART;
FILE in_UART;

/* Initializes UART registers
 * UBRR0H
 * UBRR0L
 * UCSR0A
 * UCSR0C
 * UCSR0B
 */
void initialize_UART();

/* Basic putchar function
 * Blocks until previous byte was sent to send new one
 * Always sends a '\r' carriage return before '\n' newlines
 */
void putchar_UART(char c, FILE * stream);

/* Basic getchar function
 * Blocks next byte is recieved
 */
char getchar_UART(FILE * stream);

#endif
