import random
import ipaddress
from scripts.global_logger import logger

# IPv4 range (start and end of the range for the third octet)
ipv4_third_octet_start = 100
ipv4_third_octet_end = 250
ipv4_base = "10.160"  # Fixed first two octets

# IPv6 range (start and end for the variable parts)
ipv6_variable_start = int('0xc0aa', 16)  # Starting part for the 4th block (c0aa)
ipv6_variable_end = int('0xc0ff', 16)    # Ending part for the 4th block (c0ff)

def generate_ipv4():
    """Generates an IPv4 address in the form 10.160.X.1/24 where X is in the range 200-250."""
    third_octet = random.randint(ipv4_third_octet_start, ipv4_third_octet_end)
    return f"{ipv4_base}.{third_octet}.1"

def generate_ipv6():
    """Generates an IPv6 address in the form fd11:5ee:bad:c0XX::1/64."""
    random_ipv6_part = random.randint(ipv6_variable_start, ipv6_variable_end)
    # Format the variable part and suffix
    ipv6_middle = f"{random_ipv6_part:04x}"  # Directly use the range value
    return f"fd11:5ee:bad:{ipv6_middle}::1"

#if __name__ == "__main__":
#    random_ipv4 = generate_ipv4()
#    random_ipv6 = generate_ipv6()
