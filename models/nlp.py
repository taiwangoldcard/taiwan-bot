import logging

import numpy as np
import tensorflow as tf
import tensorflow_hub as tfhub


_logger = logging.getLogger(__name__)


class UniversalSentenceEncoder:
    """A model to find the most relevant answers for specific questions."""

    def __init__(self):
        _logger.info('Downloading the model from TensorFlow Hub...')
        self.model = tfhub.load("https://tfhub.dev/google/universal-sentence-encoder/4")

    def _get_embeddings(self, sentences, batch_size=10):
        embedding_batches = []
        for i in range(0, len(sentences), batch_size):
            embedding_batches.append(self.model(sentences[i:i+batch_size]))
        sentences_embeddings = tf.concat(embedding_batches, axis=0)

        return sentences_embeddings.numpy()

    def extract_embedding(self, sentence: str) -> np.ndarray:
        return self._get_embeddings([sentence,])

    def extract_embeddings(self, sentences, batch_size=10):
        embedding_batches = []
        for i in range(0, len(sentences), batch_size):
            embedding_batches.append(self._get_embeddings(sentences[i:i+batch_size]))

        return np.concatenate(embedding_batches, axis=0)

    def get_similarity_scores(self, sentence_embedding: np.ndarray, embeddings_list: np.ndarray) -> np.ndarray:
        return embeddings_list @ sentence_embedding.T  # compute dot product with each question in the database, returns shape (n_questions, 1)
