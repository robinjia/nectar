"""General, miscellaneous utilities."""
import sys

def log(s):
  if not sys.stdout.isatty():
    # Only print to stdout if it's being redirected or piped
    print s
  print >> sys.stderr, s
