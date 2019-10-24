import numpy as np
import os
import tensorflow as tf

tf.logging.set_verbosity(tf.logging.INFO)

from .data_utils import minibatches, pad_sequences, get_chunks, write_result
from .general_utils import Progbar
from .base_model import BaseModel


class NERModel(BaseModel):
    """Specialized class of Model for NER"""

    def __init__(self, config):
        super(NERModel, self).__init__(config)
        self.idx_to_tag = {idx: tag for tag, idx in
                           self.config.vocab_tags.items()}

    def add_placeholders(self):
        """Define placeholders = entries to computational graph"""
        # shape = (batch size, max length of sentence in batch)
        self.word_ids = tf.placeholder(tf.int32, shape=[None, None],
                        name="word_ids")

        # shape = (batch size)
        self.sequence_lengths = tf.placeholder(tf.int32, shape=[None],
                        name="sequence_lengths")

        # shape = (batch size, max length of sentence, max length of word)
        self.char_ids = tf.placeholder(tf.int32, shape=[None, None,
                                                        self.config.max_len_of_word
                                                        if self.config.use_chars == 'cnn' else None],
                        name="char_ids")

        # shape = (batch size, max length of sentence, max length of word)
        self.ortho_ids = tf.placeholder(tf.int32, shape=[None, None,
                                                        self.config.max_len_of_word
                                                        if self.config.use_chars == 'cnn' else None],
                        name="ortho_ids")

        # shape = (batch_size, max_length of sentence)
        self.word_lengths = tf.placeholder(tf.int32, shape=[None, None],
                        name="word_lengths")

        # shape = (batch size, max length of sentence in batch)
        self.labels = tf.placeholder(tf.int32, shape=[None, None],
                        name="labels")

        # hyper parameters
        self.dropout = tf.placeholder(dtype=tf.float32, shape=[],
                        name="dropout")
        self.lr = tf.placeholder(dtype=tf.float32, shape=[],
                        name="lr")

    def get_feed_dict(self, words, labels=None, lr=None, dropout=None):
        """Given some data, pad it and build a feed dictionary

        Args:
            words: list of sentences. A sentence is a list of ids of a list of
                words. A word is a list of ids
            labels: list of ids
            lr: (float) learning rate
            dropout: (float) keep prob

        Returns:
            dict {placeholder: value}

        """
        # perform padding of the given data
        if self.config.use_chars:
            ortho_ids, char_ids, word_ids = zip(*words)
            word_ids, sequence_lengths = pad_sequences(word_ids, 0)
            char_ids, word_lengths = pad_sequences(char_ids, pad_tok=0,
                nlevels=2, max_len=self.config.max_len_of_word)
            ortho_ids, word_lengths = pad_sequences(ortho_ids, pad_tok=0,
                nlevels=2, max_len=self.config.max_len_of_word)
        else:
            word_ids, sequence_lengths = pad_sequences(words, 0)

        # build feed dictionary
        feed = {
            self.word_ids: word_ids,
            self.sequence_lengths: sequence_lengths
        }

        if self.config.use_chars:
            feed[self.char_ids] = char_ids
            feed[self.ortho_ids] = ortho_ids
            feed[self.word_lengths] = word_lengths

        if labels is not None:
            labels, _ = pad_sequences(labels, 0)
            feed[self.labels] = labels

        if lr is not None:
            feed[self.lr] = lr

        if dropout is not None:
            feed[self.dropout] = dropout

        return feed, sequence_lengths

    def add_word_embeddings_op(self):
        """Defines self.word_embeddings

        If self.config.embeddings is not None and is a np array initialized
        with pre-trained word vectors, the word embeddings is just a look-up
        and we don't train the vectors. Otherwise, a random matrix with
        the correct shape is initialized.
        """
        with tf.variable_scope("words"):
            if self.config.use_pretrained is None:
                self.logger.info("WARNING: randomly initializing word vectors")
                _word_embeddings = tf.get_variable(
                        name="_word_embeddings",
                        dtype=tf.float32,
                        shape=[self.config.nwords, self.config.dim_word])

                word_embeddings = tf.nn.embedding_lookup(_word_embeddings,
                                                         self.word_ids, name="word_embeddings")
            else:
                if "w2v" in self.config.use_pretrained:
                    _word_embeddings_w2v = tf.Variable(
                            self.config.embeddings_w2v,
                            name="_word_embeddings_w2v",
                            dtype=tf.float32,
                            trainable=self.config.train_embeddings)

                    word_embeddings_w2v = tf.nn.embedding_lookup(_word_embeddings_w2v,
                            self.word_ids, name="word_embeddings_w2v")
                    word_embeddings = word_embeddings_w2v

                if "ft" in self.config.use_pretrained:
                    _word_embeddings_ft = tf.Variable(
                            self.config.embeddings_ft,
                            name="_word_embeddings_ft",
                            dtype=tf.float32,
                            trainable=self.config.train_embeddings)

                    word_embeddings_ft = tf.nn.embedding_lookup(_word_embeddings_ft,
                            self.word_ids, name="word_embeddings_ft")
                    word_embeddings = word_embeddings_ft

                if "m2v" in self.config.use_pretrained:
                    _word_embeddings_m2v = tf.Variable(
                        self.config.embeddings_m2v,
                        name="_word_embeddings_m2v",
                        dtype=tf.float32,
                        trainable=self.config.train_embeddings)

                    word_embeddings_m2v = tf.nn.embedding_lookup(_word_embeddings_m2v,
                                                                self.word_ids, name="word_embeddings_m2v")
                    word_embeddings = word_embeddings_m2v

                # Multiple embeddings are used at the same time, we should concatenate them
                if len(self.config.use_pretrained.split(',')) > 1:
                    _embeddings = list()
                    if "w2v" in self.config.use_pretrained:
                        _embeddings.append(word_embeddings_w2v)
                    if "ft" in self.config.use_pretrained:
                        _embeddings.append(word_embeddings_ft)
                    if "m2v" in self.config.use_pretrained:
                        _embeddings.append(word_embeddings_m2v)
                    word_embeddings = tf.concat(_embeddings, axis=-1)

        with tf.variable_scope("chars"):
            if self.config.use_chars is not None:
                # get char embeddings matrix
                _char_embeddings = tf.get_variable(
                    name="_char_embeddings",
                    dtype=tf.float32,
                    shape=[self.config.nchars, self.config.dim_char])
                char_embeddings = tf.nn.embedding_lookup(_char_embeddings,
                                                         self.char_ids, name="char_embeddings")
                # put the time dimension on axis=1
                s = tf.shape(char_embeddings)

                char_embeddings = tf.reshape(char_embeddings,
                                             shape=[s[0] * s[1], s[-2], self.config.dim_char])
                word_lengths = tf.reshape(self.word_lengths, shape=[s[0] * s[1]])

                # bi lstm on chars
                cell_fw = tf.contrib.rnn.LSTMCell(self.config.hidden_size_char,
                                                  state_is_tuple=True)
                cell_bw = tf.contrib.rnn.LSTMCell(self.config.hidden_size_char,
                                                  state_is_tuple=True)
                _output = tf.nn.bidirectional_dynamic_rnn(
                    cell_fw, cell_bw, char_embeddings,
                    sequence_length=word_lengths, dtype=tf.float32)

                # read and concat output
                _, ((_, output_fw), (_, output_bw)) = _output
                output = tf.concat([output_fw, output_bw], axis=-1)

                # shape = (batch size, max sentence length, char hidden size)
                output = tf.reshape(output,
                                    shape=[s[0], s[1], 2 * self.config.hidden_size_char])
                word_embeddings = tf.concat([word_embeddings, output], axis=-1)

        # ORTHO
        with tf.variable_scope("ortho"):
            if self.config.use_chars is not None:
                # get char embeddings matrix
                _ortho_embeddings = tf.get_variable(
                    name="_ortho_embeddings",
                    dtype=tf.float32,
                    shape=[self.config.northo, self.config.dim_char])
                ortho_embeddings = tf.nn.embedding_lookup(_ortho_embeddings,
                                                         self.ortho_ids, name="ortho_embeddings")
                # put the time dimension on axis=1
                s = tf.shape(ortho_embeddings)

                ortho_embeddings = tf.reshape(ortho_embeddings,
                                             shape=[s[0] * s[1], s[-2], self.config.dim_char])
                word_lengths = tf.reshape(self.word_lengths, shape=[s[0] * s[1]])

                # bi lstm on chars
                cell_fw = tf.contrib.rnn.LSTMCell(self.config.hidden_size_char,
                                                  state_is_tuple=True)
                cell_bw = tf.contrib.rnn.LSTMCell(self.config.hidden_size_char,
                                                  state_is_tuple=True)
                _output = tf.nn.bidirectional_dynamic_rnn(
                    cell_fw, cell_bw, ortho_embeddings,
                    sequence_length=word_lengths, dtype=tf.float32)

                # read and concat output
                _, ((_, output_fw), (_, output_bw)) = _output
                output = tf.concat([output_fw, output_bw], axis=-1)

                # shape = (batch size, max sentence length, char hidden size)
                output = tf.reshape(output,
                                    shape=[s[0], s[1], 2 * self.config.hidden_size_char])
                word_embeddings = tf.concat([word_embeddings, output], axis=-1)

            self.word_embeddings = tf.nn.dropout(word_embeddings, self.dropout)

    def add_logits_op(self):
        """Defines self.logits

        For each word in each sentence of the batch, it corresponds to a vector
        of scores, of dimension equal to the number of tags.
        """
        with tf.variable_scope("bi-lstm"):
            cell_fw = tf.contrib.rnn.LSTMCell(self.config.hidden_size_lstm)
            cell_bw = tf.contrib.rnn.LSTMCell(self.config.hidden_size_lstm)
            (output_fw, output_bw), _ = tf.nn.bidirectional_dynamic_rnn(
                    cell_fw, cell_bw, self.word_embeddings,
                    sequence_length=self.sequence_lengths, dtype=tf.float32)
            output = tf.concat([output_fw, output_bw], axis=-1)
            output = tf.nn.dropout(output, self.dropout)

        with tf.variable_scope("proj"):
            W = tf.get_variable("W", dtype=tf.float32,
                    shape=[2*self.config.hidden_size_lstm, self.config.ntags])

            b = tf.get_variable("b", shape=[self.config.ntags],
                    dtype=tf.float32, initializer=tf.zeros_initializer())

            nsteps = tf.shape(output)[1]
            output = tf.reshape(output, [-1, 2*self.config.hidden_size_lstm])
            pred = tf.matmul(output, W) + b
            self.logits = tf.reshape(pred, [-1, nsteps, self.config.ntags])

    def add_pred_op(self):
        """Defines self.labels_pred

        This op is defined only in the case where we don't use a CRF since in
        that case we can make the prediction "in the graph" (thanks to tf
        functions in other words). With theCRF, as the inference is coded
        in python and not in pure tensroflow, we have to make the prediciton
        outside the graph.
        """
        if not self.config.use_crf:
            self.labels_pred = tf.cast(tf.argmax(self.logits, axis=-1),
                    tf.int32)

    def add_loss_op(self):
        """Defines the loss"""
        if self.config.use_crf:
            log_likelihood, trans_params = tf.contrib.crf.crf_log_likelihood(
                    self.logits, self.labels, self.sequence_lengths)
            self.trans_params = trans_params # need to evaluate it for decoding
            self.loss = tf.reduce_mean(-log_likelihood)
        else:
            losses = tf.nn.sparse_softmax_cross_entropy_with_logits(
                    logits=self.logits, labels=self.labels)
            mask = tf.sequence_mask(self.sequence_lengths)
            losses = tf.boolean_mask(losses, mask)
            self.loss = tf.reduce_mean(losses)

        # for tensorboard
        tf.summary.scalar("loss", self.loss)

    def build(self):
        # NER specific functions
        self.add_placeholders()
        self.add_word_embeddings_op()
        self.add_logits_op()
        self.add_pred_op()
        self.add_loss_op()

        # Generic functions that add training op and initialize session
        self.add_train_op(self.config.lr_method, self.lr, self.loss,
                self.config.clip)
        self.initialize_session() # now self.sess is defined and vars are init

    def predict_batch(self, words, return_feed=False):
        """
        Args:
            words: list of sentences

        Returns:
            labels_pred: list of labels for each sentence
            sequence_length

        """
        fd, sequence_lengths = self.get_feed_dict(words, dropout=1.0)

        if self.config.use_crf:
            # get tag scores and transition params of CRF
            viterbi_sequences = []
            logits, trans_params = self.sess.run(
                    [self.logits, self.trans_params], feed_dict=fd)

            # iterate over the sentences because no batching in viterbi_decode
            for logit, sequence_length in zip(logits, sequence_lengths):
                logit = logit[:sequence_length] # keep only the valid steps
                viterbi_seq, viterbi_score = tf.contrib.crf.viterbi_decode(
                        logit, trans_params)
                viterbi_sequences += [viterbi_seq]

            if return_feed:
                return viterbi_sequences, sequence_lengths, fd
            return viterbi_sequences, sequence_lengths

        else:
            labels_pred = self.sess.run(self.labels_pred, feed_dict=fd)

            return labels_pred, sequence_lengths

    def run_epoch(self, train, dev, epoch):
        """Performs one complete pass over the train set and evaluate on dev

        Args:
            train: dataset that yields tuple of sentences, tags
            dev: dataset
            epoch: (int) index of the current epoch

        Returns:
            f1: (python float), score to select model on, higher is better

        """
        # progbar stuff for logging
        batch_size = self.config.batch_size
        nbatches = (len(train) + batch_size - 1) // batch_size
        prog = Progbar(target=nbatches)

        # iterate over dataset
        for i, (words, labels) in enumerate(minibatches(train, batch_size)):
            fd, _ = self.get_feed_dict(words, labels, self.config.lr,
                    self.config.dropout)

            _, train_loss, summary = self.sess.run(
                    [self.train_op, self.loss, self.merged], feed_dict=fd)

            prog.update(i + 1, [("train loss", train_loss)])

            # tensorboard
            if i % 10 == 0:
                self.file_writer.add_summary(summary, epoch*nbatches + i)

        metrics = self.run_evaluate(dev)
        msg = " - ".join(["{} {:04.2f}".format(k, v)
                for k, v in metrics.items()])
        self.logger.info(msg)

        return metrics["f1"]

    def run_evaluate(self, test, print_to_file=False):
        """Evaluates performance on test set

        Args:
            test: dataset that yields tuple of (sentences, tags)

        Returns:
            metrics: (dict) metrics["acc"] = 98.4, ...

        """
        accs = []
        correct_preds, total_correct, total_preds = 0., 0., 0.
        if print_to_file:
            idx_to_word = {idx: word for word, idx in self.config.vocab_words.items()}
        for words, labels in minibatches(test, self.config.batch_size):

            if print_to_file:
                labels_pred, sequence_lengths, fd = self.predict_batch(words, return_feed=True)
                for s_idx, sentence in enumerate(fd[self.word_ids]):
                    for w_idx, word in enumerate(sentence):
                        # Prevent index error
                        if w_idx >= sequence_lengths[s_idx]:
                            break
                        w_label = labels[s_idx][w_idx]
                        w_pred = labels_pred[s_idx][w_idx]
                        write_result(idx_to_word[word] + " " + self.idx_to_tag[w_label] + " " + self.idx_to_tag[w_pred],
                                     self.config.conll_output)
                    write_result("\n", self.config.conll_output)
            else:
                labels_pred, sequence_lengths = self.predict_batch(words)

            for lab, lab_pred, length in zip(labels, labels_pred,
                                             sequence_lengths):
                lab      = lab[:length]
                lab_pred = lab_pred[:length]
                accs    += [a==b for (a, b) in zip(lab, lab_pred)]

                lab_chunks      = set(get_chunks(lab, self.config.vocab_tags))
                lab_pred_chunks = set(get_chunks(lab_pred,
                                                 self.config.vocab_tags))

                correct_preds += len(lab_chunks & lab_pred_chunks)
                total_preds   += len(lab_pred_chunks)
                total_correct += len(lab_chunks)

        p   = correct_preds / total_preds if correct_preds > 0 else 0
        r   = correct_preds / total_correct if correct_preds > 0 else 0
        f1  = 2 * p * r / (p + r) if correct_preds > 0 else 0
        acc = np.mean(accs)

        return {"acc": 100*acc, "f1": 100*f1, "precision": p, "recall": r}

    def predict(self, words_raw):
        """Returns list of tags

        Args:
            words_raw: list of words (string), just one sentence (no batch)

        Returns:
            preds: list of tags (string), one for each word in the sentence

        """
        words = [self.config.processing_word(w) for w in words_raw]
        if type(words[0]) == tuple:
            words = zip(*words)
        pred_ids, _ = self.predict_batch([words])
        preds = [self.idx_to_tag[idx] for idx in list(pred_ids[0])]

        return preds


    def simple_save(self):
        """Saves session for tensorserving"""
        #for i in [n.name for n in tf.get_default_graph().as_graph_def().node]:
        #    print i
        tf.saved_model.simple_save(
                self.sess,
                "./serving_model",
                inputs={"labels": self.labels, "word_ids": self.word_ids, "sequence_lengths": self.sequence_lengths, "char_ids": self.char_ids, "ortho_ids": self.ortho_ids, "word_lengths": self.word_lengths, "dropout": self.dropout},
                outputs={"logits": self.logits, "trans_params": self.trans_params}
                )

    def get_fd_serving(self, words, labels=None, lr=None, dropout=None):
        """Given some data, pad it and build a feed dictionary

        Args:
            words: list of sentences. A sentence is a list of ids of a list of
                words. A word is a list of ids
            labels: list of ids
            lr: (float) learning rate
            dropout: (float) keep prob

        Returns:
            dict {placeholder: value}

        """
        # perform padding of the given data
        if self.config.use_chars:
            ortho_ids, char_ids, word_ids = zip(*words)
            word_ids, sequence_lengths = pad_sequences(word_ids, 0)
            char_ids, word_lengths = pad_sequences(char_ids, pad_tok=0,
                nlevels=2, max_len=self.config.max_len_of_word)
            ortho_ids, word_lengths = pad_sequences(ortho_ids, pad_tok=0,
                nlevels=2, max_len=self.config.max_len_of_word)
        else:
            word_ids, sequence_lengths = pad_sequences(words, 0)

        # build feed dictionary
        feed = {
            "word_ids": word_ids,
            "sequence_lengths": sequence_lengths
        }

        if self.config.use_chars:
            feed["char_ids"] = char_ids
            feed["ortho_ids"] = ortho_ids
            feed["word_lengths"] = word_lengths

        feed["labels"] = [[0 for _ in range(sequence_lengths[0])]]

        feed["dropout"] = 1.0

        return feed, sequence_lengths
