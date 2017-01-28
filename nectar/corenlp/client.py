"""A client for a CoreNLP Server."""
import json
import requests

class CoreNLPClient(object):
  """A client that interacts with the CoreNLPServer."""
  def __init__(self, hostname='http://localhost', port=7000):
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
    r = requests.post(url, params=params, data=data.encode('utf-8'))
    r.encoding = 'utf-8'
    return json.loads(r.text, strict=False)

  def query_pos(self, sents):
    """Standard query for getting POS tags."""
    properties = {
        'ssplit.newlineIsSentenceBreak': 'always',
        'annotators': 'tokenize,ssplit,pos',
        'outputFormat':'json'
    }
    return self.query(sents, properties)


  def query_ner(self, paragraphs):
    """Standard query for getting NERs on raw paragraphs."""
    annotators = 'tokenize,ssplit,pos,ner,entitymentions'
    properties = {
        'ssplit.newlineIsSentenceBreak': 'always',
        'annotators': annotators,
        'outputFormat':'json'
    }
    return self.query(paragraphs, properties)

  def query_depparse_ptb(self, sents, use_sd=False):
    """Standard query for getting dependency parses on PTB-tokenized input."""
    annotators = 'tokenize,ssplit,pos,depparse'
    properties = {
        'tokenize.whitespace': True,
        'ssplit.eolonly': True,
        'ssplit.newlineIsSentenceBreak': 'always',
        'annotators': annotators,
        'outputFormat':'json'
    }
    if use_sd:
      # Use Stanford Dependencies trained on PTB
      # Default is Universal Dependencies
      properties['depparse.model'] = 'edu/stanford/nlp/models/parser/nndep/english_SD.gz'
    return self.query(sents, properties)

  def query_depparse(self, sents, use_sd=False, add_ner=False):
    """Standard query for getting dependency parses on raw sentences."""
    annotators = 'tokenize,ssplit,pos,depparse'
    if add_ner:
      annotators += ',ner'
    properties = {
        'ssplit.eolonly': True,
        'ssplit.newlineIsSentenceBreak': 'always',
        'annotators': annotators,
        'outputFormat':'json'
    }
    if use_sd:
      # Use Stanford Dependencies trained on PTB
      # Default is Universal Dependencies
      properties['depparse.model'] = 'edu/stanford/nlp/models/parser/nndep/english_SD.gz'
    return self.query(sents, properties)

  def query_const_parse(self, sents, add_ner=False):
    """Standard query for getting constituency parses on raw sentences."""
    annotators = 'tokenize,ssplit,pos,parse'
    if add_ner:
      annotators += ',ner'
    properties = {
        'ssplit.eolonly': True,
        'ssplit.newlineIsSentenceBreak': 'always',
        'annotators': annotators,
        'outputFormat':'json'
    }
    return self.query(sents, properties)
