import socket
from RPLCD.i2c import CharLCD
from display_lock import display_lock

I2C_ADDR = 0x27

lcd = CharLCD(i2c_expander='PCF8574', address=I2C_ADDR, port=3,
              cols=16, rows=2, dotsize=8,
              charmap='A02',
              auto_linebreaks=True,
              backlight_enabled=True)

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "No IP found"
    finally:
        s.close()
    return ip

def main():
    with display_lock:
        ip_address = get_ip_address()
        lcd.clear()
        lcd.write_string("IP Address")
        lcd.crlf()
        lcd.write_string(ip_address)

if __name__ == "__main__":
    main()
