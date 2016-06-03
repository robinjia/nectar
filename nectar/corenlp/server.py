"""Interactions with the CoreNLP Server."""
import atexit
import json
import os
import requests
import subprocess
import sys
import time

LIB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'lib/stanford-corenlp/*')
DEVNULL = open(os.devnull, 'wb')

class CoreNLPServer(object):
  """An object that runs and interacts with the CoreNLP Server.
  
  It can either run the actual CoreNLP server in a subprocess,
  or just interact with it if it's already running.
  """
  def __init__(self, port=9000):
    self.port = port
    self.process = None

  def start(self):
    """Start up the server on a separate process."""
    p = subprocess.Popen(
        ['java', '-mx4g', '-cp', LIB_PATH, 
         'edu.stanford.nlp.pipeline.StanfordCoreNLPServer', str(self.port)],
        stderr=subprocess.PIPE, stdout=DEVNULL)
    self.process = p
    atexit.register(p.terminate)  # Terminate on exit
    # Wait until server has started up.
    while True:
      line = p.stderr.readline().rstrip()
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

  def query(self, sents, properties):
    """Most general way to query the server."""
    url = 'http://localhost:%d' % self.port
    params = {'properties': str(properties)}
    data = '\n'.join(sents)
    r = requests.get(url, params=params, data=data)
    return r.json()

  def query_depparse(self, sents):
    """Standard query for getting dependency parses."""
    properties = {
        'tokenize.whitespace': True, 
        'annotators': 'tokenize,ssplit,pos,depparse',
        'outputFormat':'json'
    }
    return self.query(sents, properties)

def main():
  """Start a REPL to interact with the server."""
  with CoreNLPServer() as s:
    print s.query_depparse(['what states border alaska'])

if __name__ == '__main__':
  main()
