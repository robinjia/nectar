"""Run a CoreNLP Server."""
import atexit
import os
import subprocess
import sys
import time

LIB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))),
    'lib/stanford-corenlp/*')
DEVNULL = open(os.devnull, 'wb')

class CoreNLPServer(object):
  """An object that runs the CoreNLP server."""
  def __init__(self, port=9000):
    self.port = port
    self.process = None

  def start(self):
    """Start up the server on a separate process."""
    print >> sys.stderr, 'Using lib directory %s' % LIB_PATH
    p = subprocess.Popen(
        ['java', '-mx4g', '-cp', LIB_PATH, 
         'edu.stanford.nlp.pipeline.StanfordCoreNLPServer', str(self.port)],
        stderr=subprocess.PIPE, stdout=DEVNULL)
    self.process = p
    atexit.register(p.terminate)  # Terminate on exit
    # Wait until server has started up.
    while True:
      line = p.stderr.readline().rstrip()
      if not line: continue
      print >> sys.stderr, line
      if 'listening' in line: 
        break

  def stop(self):
    """Stop running the server on a separate process."""
    if self.process:
      self.process.terminate()

  def __enter__(self):
    self.start()
    return self

  def __exit__(self, type, value, traceback):
    self.stop()
