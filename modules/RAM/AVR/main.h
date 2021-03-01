#ifndef MAIN_H_
#define MAIN_H_

#include <stdint.h>


#define MODULE_PROBE_STRING "Module?"
#define MODULE_NAME "RAM"

#define SHOULDER_THETA_CHAR 'S'

#define SERVO_FREQUENCY 50 //Hz

// Shoulder theta pulse width definitions in microseconds (us)
#define SHOULDER_THETA_MIN 1000
#define SHOULDER_THETA_MAX 2000
#define SHOULDER_THETA_DEFAULT 1500


int main();

void initialize_PWM();

void set_shoulder_theta(uint16_t width);


#endif
