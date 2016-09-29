"""Standard utilties for a theano model."""
import numbers
import numpy as np
import pickle
import random
import sys
import theano
import time
from Tkinter import TclError

import __init__ as ntu
from .. import log

class TheanoModel(object):
  """A generic theano model.

  This class handles some standard boilerplate.
  Current features include:
    Basic training loop
    Saving and reloading of model

  An implementing subclass must override the following methods:
    self.__init__(*args, **kwargs)
    self.init_params()
    self.setup_theano_funcs()
    self.get_objective(example)
    self.train_one(example, lr)
    self.evaluate(dataset)

  A basic self.__init__() routine is provided here, just as an example.
  Most users should override __init__() to perform additional functionality.

  See these methods for more details.
  """
  def __init__(self):
    """A minimal example of what functions must be called during initialization.

    Implementing subclasses should override this method,
    but maintain the basic functionality presented here.
    """
    # self.params and self.params_list are required by self.create_matrix()
    self.params = {}
    self.param_list = []

    # Initialize parameters
    self.init_params()

    # If desired, set up grad norm caches for momentum, AdaGrad, etc. here.
    # It must be after params are initialized but before theano functionss are created.
    # self.velocities = nt.create_grad_cache(self.param_list)

    # Set up theano functions
    self.theano_funcs = {} 
    self.setup_theano_funcs() 

  def init_params(self):
    """Initialize parameters with repeated calls to self.create_matrix()."""
    raise NotImplementedError

  def setup_theano_funcs(self):
    """Create theano.function objects for this model in self.theano_funcs."""
    raise NotImplementedError

  def get_objective(self, example):
    """Get the loss on a single example."""
    raise NotImplementedError

  def train_one(self, example, lr):
    """Run training on a single example."""
    raise NotImplementedError

  def create_matrix(self, name, shape, weight_scale):
    """A helper method that creates a parameter matrix."""
    if shape:
      value = weight_scale * np.random.uniform(-1.0, 1.0, shape).astype(
          theano.config.floatX)
    else:
      # None means it's a scalar
      dtype = np.dtype(theano.config.floatX)
      value = dtype.type(weight_scale * np.random.uniform(-1.0, 1.0))
    mat = theano.shared(name=name, value=value)
    self.params[name] = mat
    self.param_list.append(mat)

  def train(self, train_data, lr_init, epochs, dev_data=None, rng_seed=0,
            do_plot=False, plot_outfile=None):
    """Train the model.

    Args:
      train_data: A list of training examples
      lr_init: Initial learning rate
      epochs: An integer number of epochs to train, or a list of integers, 
          where we halve the learning rate after each period.
      dev_data: A list of dev examples, evaluate loss on this each epoch.
      rng_seed: Random seed for shuffling the dataset at each epoch.
      do_plot: If True, plot a learning curve.
      plot_outfile: If provided, save learning curve to file.
    """
    random.seed(rng_seed)
    train_data = list(train_data)
    lr = lr_init
    if isinstance(epochs, numbers.Number):
      lr_changes = []
      num_epochs = epochs
    else:
      lr_changes = set([sum(epochs[:i]) for i in range(1, len(epochs))])
      num_epochs = sum(epochs)
    num_epochs_digits = len(str(num_epochs))
    train_obj_list = []
    dev_obj_list = []
    len_train_obj = 0
    len_dev_obj = 0
    len_time = 0
    for epoch in range(num_epochs):
      t0 = time.time()
      random.shuffle(train_data)
      if epoch in lr_changes:
        lr *= 0.5
      train_obj = 0.0
      for ex in train_data:
        cur_obj = self.train_one(ex, lr)
        train_obj += cur_obj
      if dev_data:
        dev_obj = sum(self.get_objective(ex) for ex in dev_data)
        dev_obj_list.append(dev_obj)
      else:
        dev_obj = 0.0
      train_obj_list.append(train_obj)
      t1 = time.time()

      # Some formatting to make things align in columns
      train_obj_str = '%.2f' % train_obj
      dev_obj_str = '%.2f' % dev_obj
      time_str = '%.2f' % (t1 - t0)
      len_train_obj = max(len(train_obj_str), len_train_obj)
      len_dev_obj = max(len(dev_obj_str), len_dev_obj)
      len_time = max(len(time_str), len_time)
      dev_str = ', dev loss = %s' % dev_obj_str.rjust(len_dev_obj) if dev_data else ''
      log('Epoch %s: train loss = %s%s (lr = %.1e) (time = %s s)' % (
          str(epoch+1).rjust(num_epochs_digits), 
          train_obj_str.rjust(len_train_obj), 
          dev_str, lr, time_str.rjust(len_time)))

    if do_plot:
      plot_data = [('Train Objective', train_obj_list)]
      if dev_data:
        plot_data.append(('Dev Objective', dev_obj_list))
      try:
        ntu.plot_learning_curve(plot_data, outfile=plot_outfile)
      except TclError: 
        print >> sys.stderr, 'Encoutered error while plotting learning curve'


  def evaluate(self, dataset):
    """Evaluate the model."""
    raise NotImplementedError

  def save(self, filename):
    tf = self.theano_funcs  # save
    self.theano_funcs = None  # Don't pickle theano functions
    with open(filename, 'wb') as f:
      pickle.dump(self, f)
    self.theano_funcs = tf  # restore

  @classmethod
  def load(cls, filename):
    with open(filename, 'rb') as f:
      model = pickle.load(f)
    # Recompile theano functions
    model.theano_funcs = {}
    model.setup_theano_funcs()
    return model
