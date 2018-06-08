import socket
import urllib.request
import urllib.error

import boto3


A_DOMAIN = "a.braunly-test.pp.ua"
B_DOMAIN = "b.braunly-test.pp.ua"
C_DOMAIN = "c.braunly-test.pp.ua"

ec2 = boto3.client('ec2')


def is_online(hostname=None):
    """Check server online status."""
    if hostname is not None:
        # HTTP verification
        url = 'http://{}'.format(hostname)
        try:
            http_code = urllib.request.urlopen(url).getcode()
        except urllib.error.URLError:
            http_code = -1

        # TCP verification
        ip = socket.gethostbyname(hostname)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connect_result = sock.connect_ex((ip, 22))

        if http_code == 200 or connect_result == 0:
            return True
    return False


def main():
    for hostname in (A_DOMAIN, B_DOMAIN, C_DOMAIN):
        server_state = is_online(hostname)

        print(server_state)


if __name__ == '__main__':
    main()