#!/bin/bash
#
# Upload from ./dist to testpypi.Assumes this config in ~/.pypirc:
#
# [testpypi]
#   username = __token__
#   password = (paste here the test pypi token)
#
# Documetnation here: 
# https://packaging.python.org/en/latest/tutorials/packaging-projects/
#
# To install the test package
#  pip install --index-url https://test.pypi.org/simple/ --no-deps serial_packets 

# Abort if error
set -xe

pip install twine --upgrade
python -m twine upload --repository testpypi dist/*

