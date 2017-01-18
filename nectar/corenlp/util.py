"""CoreNLP-related utilities."""
def rejoin(tokens, sep=None):
  """Rejoin tokens into the original sentence.
  
  Args:
    tokens: a list of dicts containing 'originalText' and 'before' fields.
        All other fields will be ignored.
    sep: if provided, use the given character as a separator instead of
        the 'before' field (e.g. if you want to preserve where tokens are).
  Returns: the original sentence that generated this CoreNLP token list.
  """
  if sep is None:
    return ''.join('%s%s' % (t['before'], t['originalText']) for t in tokens)
  else:
    # Use the given separator instead
    return sep.join(t['originalText'] for t in tokens)

class ConstituencyParse(object):
  """A CoreNLP constituency parse (or a node in a parse tree).
  
  Word-level constituents have |word| set and no children.
  Phrase-level constituents have no |word| and have at least one child.
  """
  def __init__(self, tag, children=None, word=None):
    self.tag = tag
    if children:
      self.children = children
    else:
      self.children = None
    self.word = word

  @classmethod
  def _recursive_parse_corenlp(cls, tokens, i):
    orig_i = i
    print i, tokens[i]
    if tokens[i] == '(':
      tag = tokens[i + 1]
      children = []
      i = i + 2
      while True:
        child, i = cls._recursive_parse_corenlp(tokens, i)
        if isinstance(child, cls):
          children.append(child)
          if tokens[i] == ')': 
            return cls(tag, children), i + 1
        else:
          if tokens[i] != ')':
            raise ValueError('Expected ")" following leaf')
          return cls(tag, word=child), i + 1
    else:
      # Only other possibility is it's a word
      return tokens[i], i + 1

  @classmethod
  def from_corenlp(cls, s):
    """Parses the "parse" attribute returned by CoreNLP parse annotator."""
    # "parse": "(ROOT\n  (SBARQ\n    (WHNP (WDT What)\n      (NP (NN portion)\n        (PP (IN                       of)\n          (NP\n            (NP (NNS households))\n            (PP (IN in)\n              (NP (NNP             Jacksonville)))))))\n    (SQ\n      (VP (VBP have)\n        (NP (RB only) (CD one) (NN person))))\n    (. ?        )))",
    s_spaced = s.replace('\n', ' ').replace('(', ' ( ').replace(')', ' ) ')
    tokens = [t for t in s_spaced.split(' ') if t]
    print ' '.join(tokens)
    tree, index = cls._recursive_parse_corenlp(tokens, 0)
    if index != len(tokens):
      raise ValueError('Only parsed %d of %d tokens' % (index, len(tokens)))
    return tree

  def is_singleton(self):
    if self.word: return True
    if len(self.children) > 1: return False
    return self.children[0].is_singleton()
    
  def print_tree(self, indent=0):
    spaces = '  ' * indent
    if self.word:
      print '%s(%s %s)' % (spaces, self.tag, self.word)
    else:
      print '%s(%s' % (spaces, self.tag)
      for c in self.children:
        c.print_tree(indent=indent + 1)
      print '%s)' % (spaces)
