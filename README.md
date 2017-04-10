# Token auth Source

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
      "node_url": "http://some_url:9042"",
      "token_name": "the_token_name_needed",
      "env_var_key": "environment_variable_name_for_token",
      # optional values below
      "update_interval": "86400",
    },
    "image": "sesamcommunity/token-auth-source:latest"
  }
}
```
