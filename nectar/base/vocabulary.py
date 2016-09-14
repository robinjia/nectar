"""A basic vocabulary class."""
import collections

UNK_TOKEN = '<UNK>'
UNK_INDEX = 0

class Vocabulary(object):
  def __init__(self, unk_threshold=0):
    """Initialize the vocabulary.

    Args:
      unk_threshold: words with <= this many counts will be considered <UNK>.
    """
    self.unk_threshold = unk_threshold
    self.counts = collections.Counter()
    self.word2index = {UNK_TOKEN: UNK_INDEX}
    self.word_list = [UNK_TOKEN]

  def add_word(self, word, count=1):
    """Add a word (may still map to UNK if it doesn't pass unk_threshold)."""
    self.counts[word] += count
    if word not in self.word2index and self.counts[word] > self.unk_threshold:
      index = len(self.word_list)
      self.word2index[word] = index
      self.word_list.append(word)

  def add_word_hard(self, word):
    """Add word, make sure it is not UNK."""
    self.add_word(word, count=(self.unk_threshold+1))

  def get_word(self, index):
    return self.word_list[index]

  def get_index(self, word):
    if word in self.word2index:
      return self.word2index[word]
    return UNK_INDEX

  def has_word(self, word):
    return word in self.word2index

  def size(self):
    # Report number of words that have been assigned an index
    return len(self.word2index)
