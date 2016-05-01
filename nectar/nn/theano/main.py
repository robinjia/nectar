"""Some common theano routines."""
import theano
from theano import tensor as T

def printed(var):
  return theano.printing.Print()(var)
