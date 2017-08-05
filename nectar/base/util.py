"""General, miscellaneous utilities."""
from contextlib import contextmanager
import sys
import time

def log(msg, disappearing=False):
  if not sys.stdout.isatty():
    # Only print to stdout if it's being redirected or piped
    print msg
  if disappearing:
    # Trailing comma suppresses newline
    print >> sys.stderr, msg + '\r',
  else:
    print >> sys.stderr, msg

def log_dict(d, name):
  log('%s {' % name)
  for k in d:
    log('    %s: %s' % (k, str(d[k])))
  log('}')

def timed(func, msg, allow_overwrite=True):
  msg1 = '%s...' % msg
  log(msg1, disappearing=allow_overwrite)
  t0 = time.time()
  retval = func()
  t1 = time.time()
  msg2 = '%s (took %.2f s).' % (msg, t1 - t0)
  log(msg2)
  return retval

@contextmanager
def timer(msg, allow_overwrite=True):
  msg1 = '%s...' % msg
  log(msg1, disappearing=allow_overwrite)
  t0 = time.time()
  yield
  t1 = time.time()
  msg2 = '%s (took %.2f s).' % (msg, t1 - t0)
  log(msg2)
