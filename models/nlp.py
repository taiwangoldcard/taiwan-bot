import logging

import numpy as np
import tensorflow as tf
import tensorflow_hub as tfhub


_logger = logging.getLogger(__name__)


class QAModel:
    """A model to find the most relevant answers for specific questions."""

    def __init__(self, questions_answers: list):
        assert len(questions_answers) == 2
        assert len(questions_answers[0]) == len(questions_answers[1])
        questions = questions_answers[0]
        self.answers = questions_answers[1]

        _logger.info('Downloading the model from TensorFlow Hub...')
        self.model = tfhub.load("https://tfhub.dev/google/universal-sentence-encoder/4")

        _logger.info('Extracting embeddings for all questions in the database. This can take some time...')
        batch_size = 10
        embedding_batches = []
        for i in range(0, len(questions), batch_size):
            embedding_batches.append(self.model(questions[i:i+batch_size]))
        self.questions_embeddings = tf.concat(embedding_batches, axis=0)

    def find_best_answer(self, question: str) -> str:
        embedding = self.model([question,])
        scores = self.questions_embeddings @ tf.transpose(embedding)  # compute dot product with each question in the database, returns shape (n_questions, 1)
        return self.answers[np.argmax(tf.squeeze(scores).numpy())]
