#ifndef MAIN_H_
#define MAIN_H_

#include <stdint.h>


#define MODULE_PROBE_STRING "Module?"
#define MODULE_NAME "RAM"

#define SHOULDER_THETA_CHAR 'S'

#define SERVO_FREQUENCY 50 //Hz

// Shoulder theta pulse width definitions in microseconds (us)
#define SHOULDER_TURN_MIN 800
#define SHOULDER_TURN_MAX 2200
#define SHOULDER_TURN_DEFAULT 1500


int main();

/* Initializes clocks, PWM pins, and intial pulse widths to drive servos
 * Registers effected:
 * TCCR1A
 * TCCR1B
 * ICR1
 * DDRB
 * OCR1A
 */
void initialize_PWM();

/* Safely sets pulsewidth of shoulder turn servo
 * Registers effected:
 * OCR1A
 * Inputs:
 * width - pulse width in microseconds
 */
void set_shoulder_turn(uint16_t width);


#endif
