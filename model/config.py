import os
from datetime import datetime as dt

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
        self.vocab_ortho = load_vocab(self.filename_ortho)


        self.nwords     = len(self.vocab_words)
        self.nchars     = len(self.vocab_chars)
        self.northo     = len(self.vocab_ortho)
        self.ntags      = len(self.vocab_tags)

        # 2. get processing functions that map str -> id
        self.processing_word = get_processing_word(self.vocab_words,
                self.vocab_chars, self.vocab_ortho, lowercase=False, chars=(self.use_chars is not None),
                                                   use_ortho_char=self.use_ortho_char,
                                                   replace_digits=self.replace_digits)
        self.processing_tag  = get_processing_word(self.vocab_tags,
                lowercase=False, allow_unk=False)

        # 3. get pre-trained embeddings
        self.embeddings_w2v = (get_trimmed_word_vectors(self.filename_trimmed_w2v) if "w2v" in self.use_pretrained
                               else None)
        self.embeddings_ft = (get_trimmed_word_vectors(self.filename_trimmed_ft) if "ft" in self.use_pretrained
                              else None)
        self.embeddings_m2v = (get_trimmed_word_vectors(self.filename_trimmed_m2v) if "m2v" in self.use_pretrained
                              else None)

    replace_digits = False

    # general config
    dir_output = "results/test/"
    dir_model  = dir_output + "model.weights/"
    path_log   = dir_output + "log.txt"
    now_str = dt.now().strftime('%d%m%Y_%H%M%S')
    conll_eval = "python eval/conlleval.py"
    conll_output = "results/conlleval{}.tmp".format(now_str)
    conll_score = "results/conllscore{}.tmp".format(now_str)

    # embeddings
    dim_word = 100
    dim_morph = 100
    dim_char = 100

    # ft, w2v, m2v or None (if you want to use multiple embeddings, provide them comma separated e.g. "ft,m2v"
    use_pretrained = "ft"
    #get_ft_vectors_cmd = '/home/emre/git/fastText-0.1.0/fasttext print-word-vectors /home/emre/Documents/fasttext/embeddings.bin ' \
    get_ft_vectors_cmd = '/data/duobi/fastText/fasttext print-word-vectors /data/duobi/fastText/session_wp_model.bin  ' \
              '< {} > {}'

    # pretrained files
    filename_word2vec = "data/embeddings/tr-embeddings-w2v.txt"
    filename_fasttext = "ft_session/model.vec"
    filename_morph2vec = "data/embeddings/tr-embeddings-m2v.txt"

    # trimmed embeddings (created from word2vec_filename with build_data.py)
    filename_trimmed_w2v = "data/emb.w2v.{}d.trimmed.npz".format(dim_word)
    filename_trimmed_ft = "data/emb.ft.{}d.trimmed.npz".format(dim_word)
    filename_trimmed_m2v = "data/emb.m2v.{}d.trimmed.npz".format(dim_morph)

    # dataset 
    filename_dev = "data/dev.txt"
    filename_test = "data/test.txt"
    filename_train = "data/train.txt"

    max_iter = None # if not None, max number of examples in Dataset

    # vocab (created from dataset with build_data.py)
    filename_words = "data/words.tmp"
    filename_tags = "data/tags.tmp"
    filename_chars = "data/chars.tmp"
    filename_ortho = "data/ortho.tmp"

    # training
    train_embeddings = True
    nepochs          = 30
    dropout          = 0.5
    batch_size       = 32
    lr_method        = "adam"
    lr               = 0.001
    lr_decay         = 1.0
    clip             = 5.0 # if negative, no clipping
    nepoch_no_imprv  = 999

    # model hyperparameters
    hidden_size_char = 30 # lstm on chars
    hidden_size_lstm = 200 # lstm on word embeddings

    # NOTE: if both chars and crf, only 1.6x slower on GPU
    use_crf = True # if crf, training is 1.7x slower on CPU
    use_chars = "blstm" # blstm, cnn or None
    use_ortho_char = False # use orthographic chars instead of chars
    max_len_of_word = 20  # used only when use_chars = 'cnn'
    use_deasciification = False # TODO
