#!/usr/bin/env bash
mkdir venv
virtualenv --python python3 venvvenv
venv/bin/pip install -r requirements.txt