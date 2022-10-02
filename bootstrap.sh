#!/usr/bin/env bash
mkdir venv
virtualenv --python python3 venv
venv/bin/pip install -r requirements.txt