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
