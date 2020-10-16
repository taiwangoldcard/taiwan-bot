# Taiwan Bot

A chatbot to answer all your questions about [Taiwan Gold Card](https://taiwangoldcard.com/) and many more!
- [Jonathan](https://jonathanbgn.com) built the NLP model using [NLU (natural language understanding)](https://blog.tensorflow.org/2020/08/introducing-semantic-reactor-explore-nlp-sheets.html) with Tensorflow. Here [an overview of how it works](https://jonathanbgn.com/nlp/2020/09/29/chatbot-universal-sentence-encoder.html).
- [Shawn](https://www.linkedin.com/in/shawn-lim-0a307550) the infrastructure
- [Eric](https://twitter.com/eric_khun) connected the data


## Add me on Line

![Taiwan Bot line account](./line.png)

## Add me on Messenger

![Taiwan Bot messenger account](./messenger.png)

## Develop

1. `pip install -r requirements.txt`
2. `uvicorn app:app --reload`

The endpoint where you can query the bot will appear, by default it will be `http://localhost:8000`

If you get the message when starting it: 
```
[...]
tensorflow.python.framework.errors_impl.NotFoundError: /var/[...]/tfhub_modules/539544f0a997d91c327c23285ea00c37588d92cc/tfhub_module.pb; No such file or directory
```
Remove that folder with `sudo rm -rf /var/[...]/tfhub_modules/`

### Test the bot locally
- Install the [bot emulator](https://github.com/Microsoft/BotFramework-Emulator)
- The endpoint is by default `http://localhost:8000/api/messages`
- No credential are needed

## Deployment

Everytime a PR is merged, the [github workflow](./github/workflows/deploy.yml) should automatically deploy the new server code. The chatbot account above is connected to the server so your new changes should be instantly available.
