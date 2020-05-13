from typing import Tuple
from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Configuration, Secrets
from logzero import logger
from paramiko.client import SSHClient
import ssh

__all__ = ["say_it","probe_running_rabbitmq_service"]

def probe_running_rabbitmq_service(message: str = "hello", configuration: Configuration = None,
           secrets: Secrets = None) -> Tuple[str, str]:
    if not secrets:
        raise ActivityFailed(
            "Please set the secrets entry to specify the SSH client settings")

    client = ssh.connect(secrets)
    stdin, stdout, stderr = client.exec_command('sudo /usr/sbin/rabbitmqctl status | grep pid | grep -Eo \'[0-9]{1,5}\'')
    o, r = stdout.read().decode('utf-8'), stderr.read().decode('utf-8')
    client.close()
    logger.info(o)
    if r != "": 
        logger.warn(r)
        return False
    return True

def say_it(message: str = "hello", configuration: Configuration = None,
           secrets: Secrets = None):
    pass