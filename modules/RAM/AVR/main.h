#ifndef MAIN_H_
#define MAIN_H_

#include <stdint.h>


#define MODULE_PROBE_STRING "Module?"
#define MODULE_NAME "RAM"

// Command characters
#define SHOULDER_CHAR 'S'
#define ELBOW_CHAR 'E'
#define WRIST_CHAR 'W'
#define CLAW_CHAR 'C'

#define SERVO_FREQUENCY 50 //Hz

// Shoulder pulse width definitions in microseconds (us)
#define SHOULDER_MIN 800
#define SHOULDER_MAX 2200
#define SHOULDER_DEFAULT 1500

// Elbow pulse width definitions in microseconds (us)
#define ELBOW_MIN 500
#define ELBOW_MAX 2500
#define ELBOW_DEFAULT 1500

// Wrist pulse width definitions in microseconds (us)
#define WRIST_MIN 850
#define WRIST_MAX 2350
#define WRIST_DEFAULT 1600

// Claw pulse width definitions in microseconds (us)
#define CLAW_MIN 575
#define CLAW_MAX 2460
#define CLAW_DEFAULT 1265


int main();

/* Initializes clocks, PWM pins, and intial pulse widths to drive servos
 * Registers effected:
 * TCCR0A
 * TCCR0B
 * TCCR1A
 * TCCR1B
 * ICR1
 * DDRB
 * OCR1A
 * OCR1B
 */
void initialize_PWM();

/* Safely sets pulsewidth of shoulder servo
 * Registers effected:
 * OCR1A
 * Inputs:
 * width - pulse width in microseconds
 */
void set_shoulder(uint16_t width);

/* Safely sets pulsewidth of elbow servo
 * Registers effected:
 * OCR1B
 * Inputs:
 * width - pulse width in microseconds
 */
void set_elbow(uint16_t width);

/* Safely sets pulsewidth of wrist servo
 * Registers effected:
 *
 * Inputs:
 * width - pulse width in microseconds
 */
void set_wrist(uint16_t width);

/* Safely set pulsewidth of claw servo
 * Registers effected:
 *
 * Inputs:
 * width - pulse width in microseconds
 */
void set_claw(uint16_t width);

/* Greatest 8-bit factor
 * Returns the greatest 8-bit factor of n
 */
uint8_t G8BF(uint16_t n);


#endif
