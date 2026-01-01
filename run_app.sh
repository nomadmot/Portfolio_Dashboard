#!/bin/zsh

# activate Python virtual environment
source .venv/bin/activate
# set environment variables
source ./load-env.sh
# run the Streamlit app
cd src
streamlit run app.py