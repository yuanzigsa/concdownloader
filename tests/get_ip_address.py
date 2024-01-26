import  psutil


def get_ip_addresses():
    ip_addresses = []
    for interface_name, interface_addresses in psutil.net_if_addrs().items():
        for address in interface_addresses:
            if str(address.family) == 'AddressFamily.AF_INET' and address.address != '127.0.0.1':
                ip_addresses.append(address.address)
    return ip_addresses

ip_address = get_ip_addresses()

print(len(ip_address))