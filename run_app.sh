#!/bin/zsh

# activate Python virtual environment
source .venv/bin/activate

# run the Streamlit app
cd src
streamlit run app.py