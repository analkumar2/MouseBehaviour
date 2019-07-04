/* NOTE:
 * This file is generated by CMake using config.h.in template. Any changes made
 * to config.h will be lost at compile time. Please edit config.h.in file.
 */
#ifndef  config_h_INC
#define  config_h_INC

#include "protocol.h"

#define         SESSION_NUM         1
#define         ANIMAL_NAME         "k3"

/*-----------------------------------------------------------------------------
 *  PINS
 *-----------------------------------------------------------------------------*/
#define         ROTARY_ENC_A                2   // have callback
#define         ROTARY_ENC_B                3   // have callback.
#define         SHOCK_PWM_PIN               5   // PWM
#define         SHOCK_RELAY_PIN_CHAN_12     4   
#define         SHOCK_RELAY_PIN_CHAN_34     6   
#define         SHOCK_STIM_ISOLATER_PIN     7
#define         TONE_PIN                    8
#define         LED_PIN                     9
#define         CAMERA_TTL_PIN              10
#define         PUFF_PIN                    11
#define         IMAGING_TRIGGER_PIN         12
#define         SHOCK_PAD_READOUT_PIN       A0
#define         SENSOR_PIN                  A5


/*-----------------------------------------------------------------------------
 *  Parameters.
 *-----------------------------------------------------------------------------*/
#define         TONE_FREQ                   4500
#define         PUFF_DURATION               50
#define         TONE_DURATION               50
#define         LED_DURATION                50

// What kind of stimulus is given.
#define         SOUND                   0
#define         LIGHT                   1
#define         MIXED                   2

#endif /* end of include guard: config_h_INC */
