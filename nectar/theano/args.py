"""Add standard theano-related flags to an argparse.ArgumentParser."""
import theano

def add_theano_flags(parser):
  parser.add_argument('--theano-fast-compile', action='store_true', help='Run Theano in fast compile mode.')
  parser.add_argument('--theano-profile', action='store_true', help='Turn on profiling in Theano.')

def configure(opts):
  if opts.theano_fast_compile:
    theano.config.mode='FAST_COMPILE'
  else:
    theano.config.mode='FAST_RUN'
    theano.config.linker='cvm'
  if opts.theano_profile:
    theano.config.profile = True
