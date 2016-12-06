"""A client for a CoreNLP Server."""
import json
import requests

class CoreNLPClient(object):
  """A client that interacts with the CoreNLPServer."""
  def __init__(self, hostname='http://localhost', port=9000):
    self.hostname = hostname
    self.port = port

  def query(self, sents, properties):
    """Most general way to query the server.
    
    Args:
      sents: Either a string or a list of strings.
      properties: CoreNLP properties to send as part of the request.
    """
    url = '%s:%d' % (self.hostname, self.port)
    params = {'properties': str(properties)}
    if isinstance(sents, list):
      data = '\n'.join(sents)
    else:
      data = sents
    r = requests.get(url, params=params, data=data.encode('utf-8'))
    r.encoding = 'utf-8'
    return json.loads(r.text, strict=False)

  def query_pos(self, sents):
    """Standard query for getting POS tags."""
    properties = {
        'annotators': 'tokenize,ssplit,pos',
        'outputFormat':'json'
    }
    return self.query(sents, properties)

  def query_depparse(self, sents):
    """Standard query for getting dependency parses on PTB-tokenized input."""
    properties = {
        'tokenize.whitespace': True,
        'annotators': 'tokenize,ssplit,pos,depparse',
        'outputFormat':'json'
    }
    return self.query(sents, properties)
