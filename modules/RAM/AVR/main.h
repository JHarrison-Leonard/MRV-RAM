#ifndef MAIN_H_
#define MAIN_H_

#include <stdint.h>


#define MODULE_PROBE_STRING "Module?"
#define MODULE_NAME "RAM"

#define SERVO_FREQUENCY 50 //Hz

// Shoulder theta pulse width definitions in microseconds (us)
#define SHOULDER_THETA_MIN 1000
#define SHOULDER_THETA_MAX 2000
#define SHOULDER_THETA_DEFAULT 1500


// Min, max, and saturation macros
#define MIN(a,b) \
	({ __typeof__ (a) _a = (a); \
	 __typeof__ (b) _b = (a); \
	 _a < _b ? _a : _b; })

#define MAX(a,b) \
	({ __typeof__ (a) _a = (a); \
	 __typeof__ (b) _b = (b); \
	 _a > _b ? _a : _b; })

#define SAT(a,x,b) (MIN(MAX(a,x),b))


int main();

void initialize_PWM();

void set_shoulder_theta(uint16_t width);


#endif
