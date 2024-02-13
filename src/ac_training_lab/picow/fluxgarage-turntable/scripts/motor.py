import time

from machine import PWM, Pin

# Define the motor control pins
motor1A = PWM(Pin(0), freq=20000)  # Motor Driver PWM 1A Input
motor1B = PWM(Pin(1), freq=20000)  # Motor Driver PWM 1B Input
motor2A = PWM(Pin(2), freq=20000)  # Motor Driver PWM 2A Input
motor2B = PWM(Pin(3), freq=20000)  # Motor Driver PWM 2B Input


# Function to set motor speed
def set_motor_speed(motorA, motorB, speed):
    if speed > 0:
        motorA.duty_u16(int(min(speed, 65535)))
        motorB.duty_u16(0)
    elif speed < 0:
        motorA.duty_u16(0)
        motorB.duty_u16(int(min(-speed, 65535)))
    else:
        motorA.duty_u16(0)
        motorB.duty_u16(0)


# Main loop
while True:
    print("loop")
    set_motor_speed(motor1A, motor1B, 32768)  # Motor 1 forward at 50% speed
    set_motor_speed(motor2A, motor2B, -32768)  # Motor 2 backward at 50% speed
    time.sleep(1)

    set_motor_speed(motor1A, motor1B, 65535)  # Motor 1 forward at full speed
    set_motor_speed(motor2A, motor2B, -65535)  # Motor 2 backward at full speed
    time.sleep(1)

    set_motor_speed(motor1A, motor1B, 0)  # Motor 1 stops
    set_motor_speed(motor2A, motor2B, 0)  # Motor 2 stops
    time.sleep(1)

    set_motor_speed(motor1A, motor1B, -32768)  # Motor 1 backward at 50% speed
    set_motor_speed(motor2A, motor2B, 32768)  # Motor 2 forward at 50% speed
    time.sleep(1)

    set_motor_speed(motor1A, motor1B, -65535)  # Motor 1 backward at full speed
    set_motor_speed(motor2A, motor2B, 65535)  # Motor 2 forward at full speed
    time.sleep(1)

    set_motor_speed(motor1A, motor1B, 0)  # Motor 1 stops
    set_motor_speed(motor2A, motor2B, 0)  # Motor 2 stops
    time.sleep(1)
