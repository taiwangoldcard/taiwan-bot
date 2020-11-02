#!/bin/bash

# Configure the messenger bot to have a get started button
[ -z "$PAGE_ACCESS_TOKEN" ] && echo "Need to set your PAGE_ACCESS_TOKEN env variable" && exit 1;

curl -X POST -H "Content-Type: application/json" -d "{ 
  \"get_started\":{
    \"payload\":\"get_started\"
  }
}" "https://graph.facebook.com/v8.0/me/messenger_profile?access_token=$PAGE_ACCESS_TOKEN"
