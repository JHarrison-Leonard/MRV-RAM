#ifndef SERIALIO_H_
#define SERIALIO_H_
#include <stdio.h>

// Input and output filestreams using UART
FILE UART_out;
FILE UART_in;

// Initializes UART registers
void UART_initialize();

// Sends c over UART, sending '\r' first if c is '\n'
// Waits until sent before exiting
void UART_putchar(char c, FILE * stream);

// Waits until byte recieved, returning recieved byte
char UART_getchar(FILE * stream);

#endif
