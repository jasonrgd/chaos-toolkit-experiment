from typing import Tuple
from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Configuration, Secrets
from logzero import logger
from paramiko.client import SSHClient
import ssh, os, base64
from pyrabbit2.api import Client
import time

__all__ = ["probe_app_can_connect_and_send_message_to_rabbit","probe_running_rabbitmq_service", "bring_back_node_in_rabbit_cluster", "node_failure_in_rabbit_cluster"]

def probe_running_rabbitmq_service(configuration: Configuration = None,
           secrets: Secrets = None):
    if not secrets:
        raise ActivityFailed(
            "Please set the secrets entry to specify the SSH client settings")

    client = ssh.connect(secrets)
    stdin, stdout, stderr = client.exec_command('sudo /usr/sbin/rabbitmqctl status | grep pid | grep -Eo \'[0-9]{1,5}\'')
    o, r = stdout.read().decode('utf-8'), stderr.read().decode('utf-8')
    client.close()

    if r != "": 
        logger.warn(r)
        return False
    return True

def probe_app_can_connect_and_send_message_to_rabbit( configuration: Configuration = None,
           secrets: Secrets = None):

    if not secrets:
        raise ActivityFailed(
            "Please set the secrets entry to specify the SSH client settings")

    # Create ssh client
    client = ssh.connect(secrets)

    # Get RabbitMQ connection params from secrets
    rmq_api_rest_endpoint = os.getenv(secrets.get("rabbitmq_restendpoint"))
    rmq_username = os.getenv(secrets.get("rabbitmq_username"))
    rmq_password = os.getenv(secrets.get("rabbitmq_password"))
    rmq_vhost_url = os.getenv(secrets.get("rabbitmq_host"))+"/api/healthchecks/node"
    rabbit_creds = rmq_username+":"+rmq_password

    wait_time = int(os.getenv('WAIT_TIME'))
    if wait_time > 0 :
        logger.info("Waiting for " + str(wait_time) + " secs before connecting to rabbit")
        time.sleep(wait_time)

    rabbitmq_connect_curl = 'curl -s -u {rabbitmq_creds} {rabbitmq_host}'.format(
        rabbitmq_creds=rabbit_creds, rabbitmq_host=rmq_vhost_url
    )

    stdin, stdout, stderr = client.exec_command(rabbitmq_connect_curl)
    o, r = stdout.read().decode('utf-8'), stderr.read().decode('utf-8')
    client.close()

    logger.info(o)

    error = False

    if r != "": 
        logger.warn(r)
        error = True

    rmq_client = rmq_client_connect(configuration, secrets)

    rmq_client.create_vhost("ce_vhost")
    rmq_client.create_exchange("ce_vhost","ce_exc","direct")
    rmq_client.create_queue("ce_vhost", "ce_que")
    rmq_client.create_binding("ce_vhost","ce_exc","ce_que","ce.rtkey")
    if not rmq_client.publish('ce_vhost', 'ce_exc', 'ce.rtkey', 'chaos experiment message'): 
        error = True
    rmq_client.delete_vhost("ce_vhost")

    return not error

def node_failure_in_rabbit_cluster( configuration: Configuration = None,
           secrets: Secrets = None):
    rmq_client = rmq_client_connect(configuration, secrets)
    client = ssh.connect(secrets)
    stdin, stdout, stderr = client.exec_command('sudo /usr/sbin/rabbitmqctl stop_app')
    o, r = stdout.read().decode('utf-8'), stderr.read().decode('utf-8')
    client.close()
    logger.info(o)

    if r != "": 
        logger.warn(r)

def bring_back_node_in_rabbit_cluster(configuration: Configuration = None,
           secrets: Secrets = None):
    rmq_client = rmq_client_connect(configuration, secrets)
    client = ssh.connect(secrets)
    stdin, stdout, stderr = client.exec_command('sudo /usr/sbin/rabbitmqctl start_app')
    client.close()
    rmq_client = rmq_client_connect(configuration, secrets)

def rmq_client_connect(configuration: Configuration = None,
           secrets: Secrets = None):
    rmq_api_rest_endpoint = os.getenv(secrets.get("rabbitmq_restendpoint"))
    rmq_username = os.getenv(secrets.get("rabbitmq_username"))
    rmq_password = os.getenv(secrets.get("rabbitmq_password"))
    return Client(rmq_api_rest_endpoint, rmq_username, rmq_password, scheme='https')