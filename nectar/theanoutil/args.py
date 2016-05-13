"""Add standard theano-related flags to an argparse.ArgumentParser."""
import theano

def add_nlp_flags(parser):
  """Add common neural network NLP flags.
  
  TODO: make which flags are added configurable.
  """
  # Setup
  parser.add_argument('--hidden-size', '-d', type=int, help='Dimension of hidden vectors')
  parser.add_argument('--emb-size', '-e', type=int, help='Dimension of word vectors')
  parser.add_argument('--weight-scale', '-w', type=float, default=1e-2,
                      help='Weight scale for initialization (default = 1e-2)')
  parser.add_argument( '--unk-cutoff', '-u', type=int, default=0,
                      help='Treat input words with <= this many occurrences as UNK.')
  # Training hyperparameters
  parser.add_argument('--num-epochs', '-t', default=[],
                      type=lambda s: [int(x) for x in s.split(',')], 
                      help=('Number of epochs to train (default is no training). '
                            'If comma-separated list, will run for some epochs, halve learning rate, etc.'))
  parser.add_argument('--learning-rate', '-r', type=float, default=0.1,
                      help='Initial learning rate (default = 0.1).')
  # Decoding hyperparameters
  parser.add_argument('--beam-size', '-k', type=int, default=0,
                      help='Use beam search with given beam size (default is greedy).')
  # Data
  parser.add_argument('--train-file', help='Path to training data.')
  parser.add_argument('--dev-frac', type=float, default=0.0,
                      help='Take this fraction of train data as dev data.')
  parser.add_argument('--test-file', help='Path to test data.')
  # Random seeds
  parser.add_argument('--dev-seed', type=int, default=0,
                      help='RNG seed for the train/dev splits (default = 0)')
  parser.add_argument('--model-seed', type=int, default=0,
                      help="RNG seed for the model (default = 0)")

def add_theano_flags(parser):
  parser.add_argument('--theano-fast-compile', action='store_true', help='Run Theano in fast compile mode.')
  parser.add_argument('--theano-profile', action='store_true', help='Turn on profiling in Theano.')

def configure_theano(opts):
  if opts.theano_fast_compile:
    theano.config.mode='FAST_COMPILE'
    theano.config.optimizer = 'None'
    theano.config.traceback.limit = 20
  else:
    theano.config.mode='FAST_RUN'
    theano.config.linker='cvm'
  if opts.theano_profile:
    theano.config.profile = True
