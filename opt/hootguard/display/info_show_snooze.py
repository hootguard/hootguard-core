from RPLCD.i2c import CharLCD
from display_lock import display_lock

I2C_ADDR = 0x27

lcd = CharLCD(i2c_expander='PCF8574', address=I2C_ADDR, port=3,
              cols=16, rows=2, dotsize=8,
              charmap='A02',
              auto_linebreaks=True,
              backlight_enabled=True)

def get_snooze_time():
    try:
        with open('/opt/hootguard/snooze/snooze-time.txt', 'r') as file:
            snooze_seconds = int(file.read().strip())
            minutes = snooze_seconds // 60
            seconds = snooze_seconds % 60
            return f"{minutes} min {seconds} sec"
    except Exception as e:
        return "Error reading snooze time"

def main():
    with display_lock:
        snooze_time = get_snooze_time()
        lcd.clear()
        lcd.write_string("Snooze Time")
        lcd.crlf()
        lcd.write_string(snooze_time)

if __name__ == "__main__":
    main()
