# Token auth Source
[![Build Status](https://travis-ci.org/sesam-community/token-auth-source.svg?branch=master)](https://travis-ci.org/sesam-community/token-auth-source)

A small microservice to get a token and place it into a SESAM instance every X seconds.

##### Example configuration:


```
{
  "_id": "token-auth-source",
  "type": "system:microservice",
  "docker": {
    "environment": {
      "user": "theUsername",
      "password": "thePassword",
      "url": "http://token_url.com",
      "node_url": "http://some_url:9042",
      "token_name": "the_token_name_needed",
      "env_var_key": "environment_variable_name_for_token",
      # optional values below
      "sesam_token": "your_jwt_token"
      "use_header": "False",
      "data_payload": "grant_type=password;client_id=vol;client_secret=someSecret12445;username=theUsername;password=thePassword",
      "update_interval": "86400"
    },
    "image": "sesamcommunity/token-auth-source:latest"
  }
}
```

If use_header is set to false you will need to supply data_payload config.

The user and password config will then be redundant.
