
# Requirement

Python3

# create a virtual env

python -m venv venv

# activate the virtual env

. ./venv/bin/activate

# install requirements

pip install -r requirements.txt

# export variables for user and auth

REONOMY_ID=&lt;user&gt;
  
REONOMY_PASSWORD=&lt;password&gt;

# run the script

python wework.py

results will be in ./results folder

# input file

each line of the input file is a polygon specification. The number of search results is hardcoded and will need to be updated.
