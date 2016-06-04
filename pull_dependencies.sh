#!/bin/bash
mkdir -p lib
cd lib

# CoreNLP 3.6.0
corenlp='stanford-corenlp-full-2015-12-09'
if [ ! -d "${corenlp}" ]
then
  wget "http://nlp.stanford.edu/software/${corenlp}.zip"
  unzip "${corenlp}.zip"
  ln -s "${corenlp}" stanford-corenlp
fi

cd ..
