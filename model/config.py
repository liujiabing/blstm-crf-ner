import os


from .general_utils import get_logger
from .data_utils import get_trimmed_word_vectors, load_vocab, \
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
                self.vocab_chars, lowercase=False, chars=(self.use_chars is not None),
                                                   use_ortho_char=self.use_ortho_char)
        self.processing_tag  = get_processing_word(self.vocab_tags,
                lowercase=False, allow_unk=False)

        # 3. get pre-trained embeddings
        self.embeddings_w2v = (get_trimmed_word_vectors(self.filename_trimmed_w2v)
                if (self.use_pretrained == "w2v" or self.use_pretrained == "both") else None)
        self.embeddings_ft = (get_trimmed_word_vectors(self.filename_trimmed_ft)
                if (self.use_pretrained == "ft" or self.use_pretrained == "both") else None)

    # general config
    dir_output = "results/test/"
    dir_model  = dir_output + "model.weights/"
    path_log   = dir_output + "log.txt"

    # embeddings
    dim_word = 100
    dim_char = 25

    use_pretrained = "ft" # ft, w2v, both or None

    # pretrained files
    filename_word2vec = "data/embeddings/tr-embeddings-w2v.txt"
    filename_fasttext = "data/embeddings/tr-embeddings-ft.txt"

    # trimmed embeddings (created from word2vec_filename with build_data.py)
    filename_trimmed_w2v = "data/emb.w2v.{}d.trimmed.npz".format(dim_word)
    filename_trimmed_ft = "data/emb.ft.{}d.trimmed.npz".format(dim_word)

    # dataset 
    filename_dev = "data/wnut17/emerging.dev.conll.preproc.url"
    filename_test = "data/wnut17/emerging.test.conll.preproc.url"
    filename_train = "data/wnut17/emerging.train.conll.preproc.url"

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
    hidden_size_lstm = 100 # lstm on word embeddings

    # NOTE: if both chars and crf, only 1.6x slower on GPU
    use_crf = True # if crf, training is 1.7x slower on CPU
    use_chars = "blstm" # blstm, cnn or None
    use_ortho_char = True # use orthographic chars instead of chars
    max_len_of_word = 20  # used only when use_chars = 'cnn'
