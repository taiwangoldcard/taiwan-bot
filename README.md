# Taiwan Bot

A chatbot to answer all your questions about [Taiwan Gold Card](https://taiwangoldcard.com/) and many more!

## Add me on Line

![Taiwan Bot line account](./line.png)

## Develop

1. `pip install -r requirements.txt`
2. `uvicorn app:app --reload`

Test with [bot emulator](https://github.com/Microsoft/BotFramework-Emulator)

## Deployment

Everytime a PR is merged, the [github workflow](./github/workflows/deploy.yml) should automatically deploy the server to Heroku. The chatbot account above is connected to the server so your new changes should be instantly available.
