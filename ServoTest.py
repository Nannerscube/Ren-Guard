import RPi.GPIO as GPIO
import time

# Setup
servo_pins = [17, 18]  # Servo1 = GPIO17 (Base), Servo2 = GPIO18 (Drop)

GPIO.setmode(GPIO.BCM)
for pin in servo_pins:
    GPIO.setup(pin, GPIO.OUT)

# Initialize PWM at 50Hz
servo1 = GPIO.PWM(servo_pins[0], 50)  # Base rotation
servo2 = GPIO.PWM(servo_pins[1], 50)  # Drop actuator

servo1.start(0)
servo2.start(0)

# Convert angle (0–180) into duty cycle and rotate servo
def set_angle(servo, angle):

    duty = 2 + (angle / 18)  # duty(2%-12%) = 2% + (angle / 18) // 2%(0°), 7%(60°), 12%(120°)
    servo.ChangeDutyCycle(duty)
    time.sleep(0.5)
    servo.ChangeDutyCycle(0)  #Reset cycle

# Material (base_angle, drop_angle)
material_actions = {
    "Cardboard": (0, 0),      # Base 0°, Drop 0°
    "Plastic":   (0, 120),    # Base 0°, Drop 120°
    "Glass":     (60, 0),     # Base 60°, Drop 0°
    "Tin":       (60, 120)    # Base 60°, Drop 120°
}

try:
    test_sequence = ["Cardboard", "Plastic", "Glass", "Tin"]

    while True:
        for material in test_sequence:
            base_angle, drop_angle = material_actions[material]
            print(f"\nTesting: {material} Base {base_angle}°, Drop {drop_angle}°")

            # Base movement
            set_angle(servo1, base_angle)
            time.sleep(1)

            # Drop movement
            set_angle(servo2, drop_angle)
            time.sleep(1)

            # Reset drop to neutral (90°)
            set_angle(servo2, 90)
            time.sleep(1)

except KeyboardInterrupt:
    print("\nStopping...")

# Reset Motors and GPIO
finally:
    servo1.stop()
    servo2.stop()
    GPIO.cleanup()