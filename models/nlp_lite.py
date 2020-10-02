import logging

import numpy as np
import sentencepiece as spm
import tensorflow.compat.v1 as tf
import tensorflow_hub as tfhub


tf.disable_v2_behavior()

_logger = logging.getLogger(__name__)


class QAModelLite:
    """A model to find the most relevant answers for specific questions. Lite Version."""

    def __init__(self, questions_answers: list, logger=None):
        assert len(questions_answers) == 2
        assert len(questions_answers[0]) == len(questions_answers[1])
        self.questions = questions_answers[0]
        self.answers = questions_answers[1]
        self.logger = logger

        _logger.info('Downloading the model from TensorFlow Hub...')
        with tf.Session() as sess:
            module = tfhub.Module("https://tfhub.dev/google/universal-sentence-encoder-lite/2")
            spm_path = sess.run(module(signature="spm_path"))  # spm_path now contains a path to the SentencePiece model stored inside the TF-Hub module
        self.sp = spm.SentencePieceProcessor()
        self.sp.Load(spm_path)

        self.input_placeholder = tf.sparse_placeholder(tf.int64, shape=[None, None])
        self.embeddings_model = module(
            inputs=dict(
                values=self.input_placeholder.values,
                indices=self.input_placeholder.indices,
                dense_shape=self.input_placeholder.dense_shape
            )
        )

        _logger.info('Extracting embeddings for all questions in the database. This can take some time...')
        batch_size = 10
        embedding_batches = []
        for i in range(0, len(self.questions), batch_size):
            embedding_batches.append(self._get_embeddings(self.questions[i:i+batch_size]))
        self.questions_embeddings = np.concatenate(embedding_batches, axis=0)

    def find_best_answer(self, question: str) -> str:
        embedding = self._get_embeddings([question,])
        scores = self.questions_embeddings @ embedding.T  # compute dot product with each question in the database, returns shape (n_questions, 1)
        most_similar_id = np.argmax(scores)
        most_similar_question = self.questions[most_similar_id]
        best_answer = self.answers[most_similar_id]
        if self.logger is not None:
            self.logger.log_answers(question, most_similar_question, best_answer, float(scores[most_similar_id]))
        return best_answer

    def _process_to_IDs_in_sparse_format(self, sentences):
        # An utility method that processes sentences with the sentence piece processor
        # 'sp' and returns the results in tf.SparseTensor-similar format:
        # (values, indices, dense_shape)
        ids = [self.sp.EncodeAsIds(x) for x in sentences]
        max_len = max(len(x) for x in ids)
        dense_shape=(len(ids), max_len)
        values=[item for sublist in ids for item in sublist]
        indices=[[row,col] for row in range(len(ids)) for col in range(len(ids[row]))]
        return (values, indices, dense_shape)

    def _get_embeddings(self, sentences):
        values, indices, dense_shape = self._process_to_IDs_in_sparse_format(sentences)

        with tf.Session() as sess:
            sess.run([tf.global_variables_initializer(), tf.tables_initializer()])
            message_embeddings = sess.run(
                self.embeddings_model,
                feed_dict={self.input_placeholder.values: values,
                            self.input_placeholder.indices: indices,
                            self.input_placeholder.dense_shape: dense_shape})

        return np.array(message_embeddings)
