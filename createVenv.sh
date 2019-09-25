#!/bin/bash

# Path
export PATH=/usr/local/bin:$PATH

# Set Variables
VENV="${1}"
SOURCE_INSTALL="${2}"
FLAG="${3}"
PARAMS='--no-cache-dir'

# Create or Update Virtual Environment
if [[ ! -d "${VENV}" ]]; then
  python3.6 -m venv "${VENV}"
  source "${VENV}/bin/activate"
  pip3.6 install ${PARAMS} -U setuptools pip
  pip3.6 install ${PARAMS} ${FLAG} "${SOURCE_INSTALL}"
  deactivate
fi
