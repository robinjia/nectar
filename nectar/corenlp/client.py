"""A client for a CoreNLP Server."""
import json
import requests

class CoreNLPClient(object):
  """A client that interacts with the CoreNLPServer."""
  def __init__(self, hostname='http://localhost', port=9000):
    self.hostname = hostname
    self.port = port

  def query(self, sents, properties):
    """Most general way to query the server."""
    url = '%s:%d' % (self.hostname, self.port)
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
