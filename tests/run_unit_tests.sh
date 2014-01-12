#!/bin/sh
export PYTHONPATH=`pwd`/..:`pwd`
nosetests -s -v --with-coverage --cover-package=kotocore --cover-html unit
