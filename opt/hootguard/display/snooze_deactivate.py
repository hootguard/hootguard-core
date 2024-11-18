from RPLCD.i2c import CharLCD
from display_lock import display_lock
import RPi.GPIO as GPIO

# Define the I2C address (replace with your detected address)
I2C_ADDR = 0x27

# Initialize the LCD on bus 3
lcd = CharLCD(i2c_expander='PCF8574', address=I2C_ADDR, port=3,
              cols=16, rows=2, dotsize=8,
              charmap='A02',
              auto_linebreaks=True,
              backlight_enabled=True)  # Enable backlight initially

# GPIO setup for the LED
LED_PIN = 16  # GPIO pin for the LED
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

def main():
    with display_lock:
        lcd.clear()
        lcd.write_string("Snooze deactive")
        lcd.crlf()

    # Turn off the LED
    GPIO.output(LED_PIN, GPIO.LOW)
    GPIO.cleanup()  # Clean up GPIO resources

if __name__ == "__main__":
    main()
