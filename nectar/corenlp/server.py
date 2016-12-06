"""Run a CoreNLP Server."""
import atexit
import multiprocessing
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
  def __init__(self, port=9000, lib_path=LIB_PATH, flags=None, logfile=None):
    """Create the CoreNLPServer object.

    Args:
      port: Port on which to serve requests.
      flags: If provided, pass this list of additional flags to the java server.
      logfile: If provided, log stderr to this file.
      lib_path: The path to the CoreNLP *.jar files.
    """
    self.port = port
    self.lib_path = LIB_PATH
    self.process = None
    self.p_stderr = None
    if flags:
      self.flags = flags
    else:
      self.flags = []
    if logfile:
      self.logfd = open(logfile, 'wb')
    else:
      self.logfd = DEVNULL

  def start(self, flags=None):
    """Start up the server on a separate process."""
    print >> sys.stderr, 'Using lib directory %s' % self.lib_path
    if not flags:
      flags = self.flags
    p = subprocess.Popen(
        ['java', '-mx4g', '-cp', self.lib_path,
         'edu.stanford.nlp.pipeline.StanfordCoreNLPServer',
         '--port', str(self.port)] + flags,
        stderr=subprocess.PIPE, stdout=self.logfd)
    self.process = p
    atexit.register(p.terminate)  # Terminate on exit
    # Wait until server has started up.
    while True:
      line = p.stderr.readline().rstrip()
      if not line: continue
      print >> sys.stderr, line
      if 'listening' in line: 
        break

    # Start a process to write stderr to the log file
    def log_stderr():
      while True:
        line = p.stderr.readline().rstrip()
        print >> self.logfd, line
    self.p_stderr = multiprocessing.Process(target=log_stderr)
    self.p_stderr.start()

  def stop(self):
    """Stop running the server on a separate process."""
    if self.process:
      self.process.terminate()
    if self.p_stderr:
      self.p_stderr.terminate()
    if self.logfd != DEVNULL:
      self.logfd.close()

  def __enter__(self):
    self.start()
    return self

  def __exit__(self, type, value, traceback):
    self.stop()
