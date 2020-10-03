import logging

import numpy as np
import sentencepiece as spm
import tensorflow.compat.v1 as tf
import tensorflow_hub as tfhub


tf.disable_v2_behavior()

_logger = logging.getLogger(__name__)

class UniversalSentenceEncoderLite:
    """A model to encode sentences into embeddings."""

    def __init__(self):
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

    def extract_embedding(self, sentence: str) -> np.ndarray:
        return self._get_embeddings([sentence,])

    def extract_embeddings(self, sentences, batch_size=10):
        embedding_batches = []
        for i in range(0, len(sentences), batch_size):
            embedding_batches.append(self._get_embeddings(sentences[i:i+batch_size]))

        return np.concatenate(embedding_batches, axis=0)

    def get_similarity_scores(self, sentence_embedding: np.ndarray, embeddings_list: np.ndarray) -> np.ndarray:
        return embeddings_list @ sentence_embedding.T  # compute dot product with each question in the database, returns shape (n_questions, 1)

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
