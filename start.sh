#!/bin/bash

PYTHONPATH=${PWD}/src:$PYTHONPATH python ./src/mobigen/datafabric "$@"
