from RPLCD.i2c import CharLCD
from display_lock import display_lock

I2C_ADDR = 0x27

lcd = CharLCD(i2c_expander='PCF8574', address=I2C_ADDR, port=3,
              cols=16, rows=2, dotsize=8,
              charmap='A02',
              auto_linebreaks=True,
              backlight_enabled=True)

def main():
    with display_lock:
        lcd.clear()
        lcd.backlight_enabled = False

if __name__ == "__main__":
    main()
