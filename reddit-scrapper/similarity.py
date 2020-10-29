'''
    This is a POC to find how similar are answer between each others
    aimed to be used to grab all question , group them by similarty,
    and know which ones are the most asked
'''

from tensorflow import keras

import tensorflow_hub as hub

embed = hub.load("/path/to/universal-sentence-encoder_4")
embeddings = embed([
    "The quick brown fox jumps over the lazy dog.",
    "I am a sentence for which I would like to get its embedding"])

print(embeddings)

def print_similarity(sentence1, sentence2):
    embeddings = embed([
        sentence1,
        sentence2])
    print("Similarity between `{}` and `{}`:\n{}".format(
        sentence1,
        sentence2,
        keras.losses.cosine_similarity(embeddings[0], embeddings[1]).numpy()))

print_similarity("I like France", "I like Paris")
print_similarity("I like France", "I like pineapple")
print_similarity("I like apple", "I like pineapple")
print_similarity("All birds fly in the sky", "Yesterday I was travelling in Tokyo")
