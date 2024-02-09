/*******************************************************************************
 * THIS SOFTWARE IS PROVIDED IN AN "AS IS" CONDITION. NO WARRANTY AND SUPPORT
 * IS APPLICABLE TO THIS SOFTWARE IN ANY FORM. CYTRON TECHNOLOGIES SHALL NOT,
 * IN ANY CIRCUMSTANCES, BE LIABLE FOR SPECIAL, INCIDENTAL OR CONSEQUENTIAL
 * DAMAGES, FOR ANY REASON WHATSOEVER.
 ********************************************************************************
 * DESCRIPTION:
 *
 * This example shows how to drive 2 motors using 4 PWM pins (2 for each motor)
 * with 2-channel motor driver.
 *
 *
 * CONNECTIONS:
 *
 * Arduino D3  - Motor Driver PWM 1A Input
 * Arduino D9  - Motor Driver PWM 1B Input
 * Arduino D10 - Motor Driver PWM 2A Input
 * Arduino D11 - Motor Driver PWM 2B Input
 * Arduino GND - Motor Driver GND
 *
 *
 * AUTHOR   : Kong Wai Weng
 * COMPANY  : Cytron Technologies Sdn Bhd
 * WEBSITE  : www.cytron.io
 * EMAIL    : support@cytron.io
 *
 *******************************************************************************/

 #include "CytronMotorDriver.h"


// Configure the motor driver.
CytronMD motor1(PWM_PWM, 3, 9);   // PWM 1A = Pin 3, PWM 1B = Pin 9.
CytronMD motor2(PWM_PWM, 10, 11); // PWM 2A = Pin 10, PWM 2B = Pin 11.


// The setup routine runs once when you press reset.
void setup() {

}


// The loop routine runs over and over again forever.
void loop() {
  motor1.setSpeed(13);   // Motor 1 runs forward at 5% speed.
  motor2.setSpeed(-13);  // Motor 2 runs backward at 5% speed.
  delay(10);

  motor1.setSpeed(26);   // Motor 1 runs forward at 10% speed.
  motor2.setSpeed(-26);  // Motor 2 runs backward at 10% speed.
  delay(10);

  motor1.setSpeed(0);     // Motor 1 stops.
  motor2.setSpeed(0);     // Motor 2 stops.
  delay(10);

  motor1.setSpeed(-13);  // Motor 1 runs backward at 5% speed.
  motor2.setSpeed(13);   // Motor 2 runs forward at 5% speed.
  delay(10);

  motor1.setSpeed(-26);  // Motor 1 runs backward at 10% speed.
  motor2.setSpeed(26);   // Motor 2 runs forward at 10% speed.
  delay(10);

  motor1.setSpeed(0);     // Motor 1 stops.
  motor2.setSpeed(0);     // Motor 2 stops.
  delay(10);
}
