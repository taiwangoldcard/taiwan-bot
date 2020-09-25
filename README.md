# Taiwan Bot

A chatbot to answer all your questions about [Taiwan Gold Card](https://taiwangoldcard.com/) and many more!
- [Jonathan](https://jonathanbgn.com) built the NLP model using [NLU (natural language understanding)](https://blog.tensorflow.org/2020/08/introducing-semantic-reactor-explore-nlp-sheets.html) with Tensorflow
- [Shawn](https://www.linkedin.com/in/shawn-lim-0a307550) the infrastructure
- [Eric](https://twitter.com/eric_khun) connected the data


## Add me on Line

![Taiwan Bot line account](./line.png)

## Add me on Messenger

![Taiwan Bot messenger account](./messenger.png)

## Develop

1. `pip install -r requirements.txt`
2. `uvicorn app:app --reload`

Test with [bot emulator](https://github.com/Microsoft/BotFramework-Emulator)

## Deployment

Everytime a PR is merged, the [github workflow](./github/workflows/deploy.yml) should automatically deploy the new server code. The chatbot account above is connected to the server so your new changes should be instantly available.
