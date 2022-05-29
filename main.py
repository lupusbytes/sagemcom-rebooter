from client import SagemcomClient
from dotenv import dotenv_values
import argparse

# Ensure "host", "username" and "password" parameters are either set by .env file or as command line arguments
# Get values from .env
config = dotenv_values(".env")
env_host = config.get("host")
env_username = config.get("username")
env_password = config.get("password")

# Define command line arguments and set missing values from .env as required
parser = argparse.ArgumentParser()
parser.add_argument("-H", "--host", required=env_host is None)
parser.add_argument("-u", "--username", required=env_username is None)
parser.add_argument("-p", "--password", required=env_password is None)
args = parser.parse_args()

# Get the final values for our client.
# Command line args should take precedence over .env values
host = env_host if args.host is None else args.host
username = env_username if args.username is None else args.username
password = env_password if args.password is None else args.password


def main():
    client = SagemcomClient(host, username, password)
    client.login()
    client.reboot()


if __name__ == '__main__':
    main()
