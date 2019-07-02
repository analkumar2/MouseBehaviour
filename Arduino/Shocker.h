/*
 *    Description:  Shock protocol. 
 *        Author :  Upinder Bhalla. See attached file on issue #44.
 *     Maintainer:  Dilawar Singh (), dilawars@ncbs.res.in
 *   Organization:  NCBS Bangalore
 *
 */

#ifndef SHOCKER_H
#define SHOCKER_H

#include "TimerOne/TimerOne.h"

void enableReadingShockPad();
void disableReadingShockPad();

int NUM_SAMPLES        = 100;
unsigned idx           = 0;

// Do analog sampling only 1 in 10 times, for a freq of of 100 Hz.
int SAMPLING_DIVIDER   = 10;
int STIM_INTERVAL      = 150;
int NUM_LOOP_RESET     = 50;

// Minimum reading for foot touch to allow stimulus to go ahead.
int TOUCH_THRESHOLD    = 50;
int numLoops           = 0;
volatile int shock_pin_readout  = 0;

// Enable disable STIM isolator.
void enableInputToStimIsolator()
{
    digitalWrite(SHOCK_STIM_ISOLATER_PIN, HIGH);
}

void disableInputToStimIsolator()
{
    digitalWrite(SHOCK_STIM_ISOLATER_PIN, LOW);
}

// Voltage across shock pad should be 5v.
void disableReadingShockPad()
{
    digitalWrite( SHOCK_RELAY_PIN_CHAN_12, HIGH );
    digitalWrite( SHOCK_RELAY_PIN_CHAN_34, LOW );
}

void enableReadingShockPad()
{
    // For safety.
    digitalWrite( SHOCK_RELAY_PIN_CHAN_12, LOW );
    digitalWrite( SHOCK_RELAY_PIN_CHAN_34, HIGH );
}

void shockMonitor() 
{
    noInterrupts();
    shock_pin_readout = analogRead( SHOCK_PAD_READOUT_PIN );
    interrupts();  // enable interrupts again. We are done reading values.
}


/* --------------------------------------------------------------------------*/
/**
 * @Synopsis  ISR.
 *
 * THIS TIMER IS 8 bit.
 *
 * NOTE: Timer1 controlls pin 5. This PIN acts as a fast switch: switching
 *       between stimulus delivery (when available) and reading value from
 *       SHOCK pad. When reading values from SHOCK_VALUE, a 5V 
 *
 *       TIMER0 is used by millis(), delays() etc. Better I do not touch it.
 *       TIMER2 is used by tone(). You can't use it here.
 *
 *       TIMER1 is used which is 16 bits.
 */
/* ----------------------------------------------------------------------------*/

void configureShockingTimer() 
{
    Serial.println("[INFO] Configuring ShockingTimer --- ");
    // Timer1.initialize(microseconds);
    // Begin using the timer. This function must be called first. "microseconds" 
    // is the period of time the timer takes.
    Timer1.initialize(1000); 
    Timer1.attachInterrupt( shockMonitor );
}


#endif /* end of include guard: SHOCKER_H */
