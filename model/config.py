import os


from .general_utils import get_logger
from .data_utils import get_trimmed_word2vec_vectors, load_vocab, \
        get_processing_word


class Config():
    def __init__(self, load=True):
        """Initialize hyperparameters and load vocabs

        Args:
            load_embeddings: (bool) if True, load embeddings into
                np array, else None

        """
        # directory for training outputs
        if not os.path.exists(self.dir_output):
            os.makedirs(self.dir_output)

        # create instance of logger
        self.logger = get_logger(self.path_log)

        # load if requested (default)
        if load:
            self.load()


    def load(self):
        """Loads vocabulary, processing functions and embeddings

        Supposes that build_data.py has been run successfully and that
        the corresponding files have been created (vocab and trimmed word2vec
        vectors)

        """
        # 1. vocabulary
        self.vocab_words = load_vocab(self.filename_words)
        self.vocab_tags  = load_vocab(self.filename_tags)
        self.vocab_chars = load_vocab(self.filename_chars)

        self.nwords     = len(self.vocab_words)
        self.nchars     = len(self.vocab_chars)
        self.ntags      = len(self.vocab_tags)

        # 2. get processing functions that map str -> id
        self.processing_word = get_processing_word(self.vocab_words,
                self.vocab_chars, lowercase=False, chars=self.use_chars)
        self.processing_tag  = get_processing_word(self.vocab_tags,
                lowercase=False, allow_unk=False)

        # 3. get pre-trained embeddings
        self.embeddings = (get_trimmed_word2vec_vectors(self.filename_trimmed)
                if self.use_pretrained else None)


    # general config
    dir_output = "results/test/"
    dir_model  = dir_output + "model.weights/"
    path_log   = dir_output + "log.txt"

    # embeddings
    dim_word = 200
    dim_char = 25

    # glove files en
    # filename_word2vec = "data/embeddings/en-embeddings.txt"

    # word2vec files tr
    filename_word2vec = "data/embeddings/tr-embeddings.txt"

    # trimmed embeddings (created from word2vec_filename with build_data.py)
    filename_trimmed = "data/embeddings.{}d.trimmed.npz".format(dim_word)
    use_pretrained = True

    # dataset en
    #filename_dev = "data/conll2003/en/valid.txt"
    #filename_test = "data/conll2003/en/test.txt"
    #filename_train = "data/conll2003/en/train.txt"

    # dataset tr
    filename_dev = "data/celikkaya2013/tr.testa.iobes"
    filename_test = "data/celikkaya2013/tr.testb.iobes"
    filename_train = "data/celikkaya2013/tr.train.iobes"

    max_iter = None # if not None, max number of examples in Dataset

    # vocab (created from dataset with build_data.py)
    filename_words = "data/words.txt"
    filename_tags = "data/tags.txt"
    filename_chars = "data/chars.txt"

    # training
    train_embeddings = False
    nepochs          = 100
    dropout          = 0.5
    batch_size       = 10
    lr_method        = "sgd"
    lr               = 0.005
    lr_decay         = 1.0
    clip             = 5.0 # if negative, no clipping
    nepoch_no_imprv  = 999

    # model hyperparameters
    hidden_size_char = 25 # lstm on chars
    hidden_size_lstm = 200 # lstm on word embeddings

    # NOTE: if both chars and crf, only 1.6x slower on GPU
    use_crf = True # if crf, training is 1.7x slower on CPU
    use_chars = True # if char embedding, training is 3.5x slower on CPU
