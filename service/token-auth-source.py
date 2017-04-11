import os
import requests
import sesamclient
import logging
import sys
from time import sleep

logger = None
update_interval = 84600

##getting token
def create_header(system_token):
    logger.info("Creating header")
    headers = {
        "user":os.environ.get('user'),
        "password":os.environ.get('password'),
        "Content-Type": "application/json"
    }
    resp = requests.get(url=os.environ.get('url'), headers=headers).json()
    token = resp[system_token]
    return token

def create_payload(system_token):
    logger.info("Creating payload")
    data_payload = dict(item.split("=") for item in os.environ.get("data_payload").split(";"))
    resp = requests.post(url=os.environ.get('url'), data=data_payload)
    if resp.status_code == 200:
        token = resp.json()[system_token]
    else:
        logger.info("Got status code " + str(resp.status_code) )
        logger.info(("Error message : " + str(resp.text) ))
        sys.exit(1)

    return token

if __name__ == '__main__':

    format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logger = logging.getLogger('token-auth-service')

    # Log to stdout
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(logging.Formatter(format_string))
    logger.addHandler(stdout_handler)
    logger.setLevel(logging.DEBUG)

    if "node_url" not in os.environ:
        logger.error("node_url configuration missing!")
        sys.exit(1)

    node_url = os.environ.get("node_url")

    if not node_url.endswith("/"):
        node_url += "/"

    if "env_var_key" not in os.environ:
        logger.error("env_var_key configuration missing!")
        sys.exit(1)

    env_var_key = os.environ.get("env_var_key")

    if "update_interval" in os.environ:
        try:
            update_interval = int(os.environ.get("update_interval"))
            logger.info("Setting update interval to %s" % update_interval)
        except:
            logger.warning("Update interval is not an integer! Falling back to default")

    api_connection = sesamclient.Connection(sesamapi_base_url=node_url + "api", timeout=60*10)

    while True:
        token = None
        while True:
            try:
                if os.environ.get('use_header').lower() == "true":
                    token = create_header(os.environ.get("token_name"))
                else:
                    token = create_payload(os.environ.get("token_name"))
                try:
                    env_vars = {}
                    env_vars[env_var_key] = token
                    api_connection.post_env_vars(env_vars)
                except BaseException as e:
                    logger.exception("Updating env vars in node failed!")
                logger.info("Updated token in node, sleeping for %s seconds..." % update_interval)
            except BaseException as e:
                logger.exception("Error while updating!")
                # Sleep for a while then go again
            sleep(update_interval)