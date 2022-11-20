#!/bin/bash -e
TYPE=$1
for counter in 0{0..9} {10..25} ; do
  FOLDER=./"${TYPE}"/"${counter}"
  mkdir -p ${FOLDER}
  touch "${FOLDER}"/quote.txt
  touch "${FOLDER}"/image.jpg
done
