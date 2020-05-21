from logzero import logger
from paramiko.client import SSHClient

from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Configuration, Secrets
from dotenv import load_dotenv
import os

def connect(secrets: Secrets = None, ):
    load_dotenv()
    if not secrets:
        raise ActivityFailed(
            "Please set the secrets entry to specify the SSH client settings")
    ssh_remote_addr = os.getenv(secrets.get("remote_addr"))

    username = os.getenv(secrets.get("username"))
    pwd = os.getenv(secrets.get("password"))
    port = os.getenv(secrets.get("port"))
    client = SSHClient()
    client.load_system_host_keys()
    if pwd == "":
        client.connect(ssh_remote_addr)
    else :
        client.connect(ssh_remote_addr, username=username, password=pwd, port=port)
    return client