from client import SagemcomClient
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("host")
parser.add_argument("-u", "--username", required=True)
parser.add_argument("-p", "--password", required=True)
args = parser.parse_args()


def main():
    client = SagemcomClient(args.password, args.username, args.host)
    client.login()
    client.reboot()


if __name__ == '__main__':
    main()
