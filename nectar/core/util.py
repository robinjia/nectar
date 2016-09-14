"""General, miscellaneous utilities."""
import sys

def log(s):
  print s
  print >> sys.stderr, s
