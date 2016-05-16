"""Utilities for handling fig LispTree objects."""

def from_string(s):
  """Parse a Java fig LispTree from a string."""
  s = s.replace('(', ' ( ').replace(')', ' ) ')
  toks = [x for x in s.split(' ') if x]
  def recurse(i):
    if toks[i] == '(':
      subtrees = []
      j = i+1 
      while True:
        subtree, j = recurse(j)
        subtrees.append(subtree)
        if toks[j] == ')':
          return tuple(subtrees), j + 1 
    else:
      return toks[i], i+1 
  lisp_tree, final_ind = recurse(0)
  return lisp_tree
