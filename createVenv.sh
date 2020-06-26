#!/bin/bash

# Path
export PATH=/usr/local/bin:$PATH

# Set Variables
VENV=".venv/tap-datadog"
SOURCE_INSTALL="."
FLAG="-e"
PARAMS='--no-cache-dir'

# Create or Update Virtual Environment
if [[ ! -d "${VENV}" ]]; then
  python3 -m venv "${VENV}"
  source "${VENV}/bin/activate"
  pip3 install ${PARAMS} -U setuptools pip
  pip3 install ${PARAMS} ${FLAG} "${SOURCE_INSTALL}"
  deactivate
fi
