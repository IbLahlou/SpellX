import numpy as np

class CharacterTable(object):
    """This class handles the conversion between characters and one-hot encodings:
    + Encoding characters into one-hot representation as integers
    + Decoding one-hot encoding back to characters
    + Decoding a probability vector into output characters
    """
    def __init__(self, chars):
        """Initialize the character table.
        # Arguments
          chars: The characters that can appear in the input.
        """
        self.chars = sorted(set(chars))
        self.char2index = dict((c, i) for i, c in enumerate(self.chars))
        self.index2char = dict((i, c) for i, c in enumerate(self.chars))
        self.size = len(self.chars)
    
    def encode(self, C, nb_rows):
        """One-hot encode the given text C.
        # Arguments
          C: Text string to be encoded.
          nb_rows: Number of rows in the resulting one-hot encoding. This is
          used to maintain the same number of rows for each data via padding.
        """
        x = np.zeros((nb_rows, len(self.chars)), dtype=np.float32)
        for i, c in enumerate(C):
            x[i, self.char2index[c]] = 1.0
        return x

    def decode(self, x, calc_argmax=True):
        """Decode the given vector or 2D array of one-hot encodings back to characters.
        # Arguments
          x: Vector or 2D array of probabilities or one-hot encodings,
          or a vector of character indices (used with calc_argmax=False).
          calc_argmax: Whether to find the character index with the highest probability,
          default to True.
        """
        if calc_argmax:
            indices = x.argmax(axis=-1)
        else:
            indices = x
        chars = ''.join(self.index2char[ind] for ind in indices)
        return indices, chars

    def sample_multinomial(self, preds, temperature=1.0):
        """Sample the index and character output from `preds`,
        a softmax probability array with shape (1, 1, nb_chars).
        """
        # Reshape to 1D array with shape (nb_chars,).
        preds = np.reshape(preds, len(self.chars)).astype(np.float64)
        preds = np.log(preds) / temperature
        exp_preds = np.exp(preds)
        preds = exp_preds / np.sum(exp_preds)
        probs = np.random.multinomial(1, preds, 1)
        index = np.argmax(probs)
        char  = self.index2char[index]
        return index, char
