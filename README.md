# Token auth Source
[![Build Status](https://travis-ci.org/sesam-community/token-auth-source.svg?branch=master)](https://travis-ci.org/sesam-community/token-auth-source)

A small microservice to get a token and place it into a SESAM instance every X seconds.

It can run in three different modes
* Retrieve token based on a username/password header
* Retrieve token based on a json payload
* A mix of multiple configurations (shown in example 3)

#### Json payload example configuration:


```
{
  "_id": "token-auth-source",
  "type": "system:microservice",
  "docker": {
    "environment": {
      "auth_url": "http://token_url.com",
      "node_url": "http://some_url:9042",
      "token_name": "the_token_name_needed",
      "secret_key": "name_of_the_secret_to_add_to_node",
      "node_jwt": "your_node_jwt"
      "data_payload": {
          "client_id": "my_client_id",
          "client_secret": "my_client_secret",
          "grant_type": "client_credentials",
          "resource": "some resource"
        },
      "update_interval": "86400"
    },
    "image": "sesamcommunity/token-auth-source:multi-config"
  }
}
```


#### Username/Password example configuration:


```
{
  "_id": "token-auth-source",
  "type": "system:microservice",
  "docker": {
    "environment": {
      "user": "theUsername",
      "password": "thePassword",
      "auth_url": "http://token_url.com",
      "node_url": "http://some_url:9042",
      "token_name": "the_token_name_needed",
      "secret_key": "name_of_the_secret_to_add_to_node",
      "node_jwt": "your_node_jwt"
      "use_header": "False",
      "update_interval": "86400"
    },
    "image": "sesamcommunity/token-auth-source:multi-config"
  }
}
```




#### Example configuration with multi config

```json
{
  "_id": "token-auth-source",
  "type": "system:microservice",
  "docker": {
    "environment": {
      "multi_config": [{
        "data_payload": {
          "client_id": "my_client_id",
          "client_secret": "my_client_secret",
          "grant_type": "client_credentials",
          "resource": "some resource"
        },
        "auth_url": "http://token_url.com",
        "token_name": "the_token_name_needed",
        "secret_key": "name_of_the_secret_to_add_to_node",
      },
      {
        "user": "theUsername",
        "password": "thePassword",
        "auth_url": "http://token_url.com",
        "token_name": "the_token_name_needed",
        "secret_key": "name_of_the_secret_to_add_to_node",
        "use_header": "True"
      }],
      "node_url": "http://some_url:9042",
      "node_jwt": "your_jwt_token",
      "update_interval": "86400",
    },
    "image": "sesamcommunity/token-auth-source:multi-config"
  }
}
```

**Individual update interval for each config is currently not supported**