import json
import os
import requests
import sesamclient
import logging
import sys
from time import sleep

logger = None
update_interval = 84600


def create_header(config):
    """Retrieve access token based on user/pass header"""
    logger.info("Creating header")
    headers = {
        "user": config["username"],
        "password": config["password"],
        "Content-Type": "application/json"
    }
    resp = requests.get(config["auth_url"], headers=headers)
    if not resp.status_code == 200:
        logger.error("Failed to create header. Server returned {}. Full response:\n{}".format(resp.status_code, resp.text))
        resp.raise_for_status()

    token = resp.json().get(config["token_name"], None)
    if not token:
        logger.error("Auth response does not contain '{}' property. Unable to return access token"
                     .format(config["token_name"]))

    logger.info("Successfully retrieved access token.")
    return token


def create_payload(config):
    """Retrieve access token based on json payload"""
    logger.info("Creating payload")

    payload = config["data_payload"]
    if not isinstance(payload, dict):
        try:
            payload = json.loads(payload)
        except ValueError:
            payload = dict(item.split("=") for item in os.environ.get("data_payload").split(";"))

    resp = requests.post(config["auth_url"], data=payload)
    if resp.status_code != 200:
        logger.error("Failed to create payload. Server returned {}. Full response:\n{}".format(resp.status_code, resp.text))
        resp.raise_for_status()

    token = resp.json()[config["token_name"]]

    logger.info("Successfully retrieved access token.")
    return token


def verify_options(config):
    """Verify given config contains required options"""
    required_options_payload = ["auth_url",
                                "token_name",
                                "secret_key",
                                "data_payload"]

    required_options_header = ["auth_url",
                               "token_name",
                               "secret_key",
                               "username",
                               "password"]

    if "use_header" in config and config["use_header"].lower() == "true":
        for option in required_options_header:
            if option not in config:
                logger.error("Missing option '{}' in config".format(option))
                sys.exit(1)
    else:
        for option in required_options_payload:
            if option not in config:
                logger.error("Missing option '{}' in config".format(option))
                sys.exit(1)


def update_token_with_header(config):
    """Get token based on header and upload to secret store"""
    verify_options(config)

    token = create_header(config)
    if token:
        upload_secret(config["secret_key"], token)


def update_token_with_payload(config):
    """Get token based on payload and upload to secret store"""
    verify_options(config)

    token = create_payload(config)
    if token:
        upload_secret(config["secret_key"], token)


def load_env_vars():
    """Create config dict from list of env vars"""
    config = dict()
    env_vars = ["username",
                "password",
                "secret_key",
                "auth_url",
                "token_name",
                "data_payload"]

    for var in env_vars:
        config[var] = os.getenv(var)
    return config


def upload_secret(secret_key, value):
    """Upload given secret to node secret store"""
    try:
        secrets = dict()
        secrets[secret_key] = value
        api_connection.put_secrets(secrets, dont_encrypt=False)
        logger.info("Successfully uploaded secret '{}' to node secret store".format(secret_key))
    except BaseException as e:
        logger.exception("Failed to upload '{}' to secret store".format(secret_key))


if __name__ == '__main__':

    # Define logger
    format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logger = logging.getLogger('token-auth-service')

    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(logging.Formatter(format_string))
    logger.addHandler(stdout_handler)
    logger.setLevel(logging.DEBUG)

    required_root_options = ["node_url", "node_jwt"]
    for option in required_root_options:
        if option not in os.environ:
            logger.error("Missing option '{}' in config".format(option))

    node_url = os.getenv("node_url")
    if not node_url.endswith("/api"):
        if node_url.endswith("/"):
            node_url += "api"
        else:
            node_url += "/api"

    if os.getenv("update_interval"):
        try:
            update_interval = int(os.environ.get("update_interval"))
            logger.info("Setting update interval to %s" % update_interval)
        except:
            logger.warning("Update interval is not an integer! Falling back to default")

    logger.info("Setting up connection to SESAM with jwt")
    api_connection = sesamclient.Connection(sesamapi_base_url=node_url, timeout=60 * 10,
                                            jwt_auth_token=os.getenv("node_jwt"))

    multi_config = os.getenv("multi_config")
    if multi_config:

        try:
            multi_config = json.loads(multi_config)
        except ValueError:
            logger.error("multi_config does not contain valid json.")
            sys.exit(1)

        if not isinstance(multi_config, list):
            logger.error("multi_config must be an array")
            sys.exit(1)

        while True:
            for config in multi_config:
                try:
                    if "use_header" in config and config["use_header"].lower() == "true":
                        update_token_with_header(config)
                    else:
                        update_token_with_payload(config)
                except:
                    logger.error("Failed to run config for secret '{}'. Will try again next time".format(config.get("secret_key")))

            logger.info("Updated tokens in node, sleeping for {} seconds...".format(update_interval))
            sleep(update_interval)
    else:
        config = load_env_vars()

        while True:
            if "use_header" in config and config["use_header"].lower() == "true":
                update_token_with_header(config)
            else:
                update_token_with_payload(config)

            logger.info("Updated tokens in node, sleeping for {} seconds...".format(update_interval))
            sleep(update_interval)
