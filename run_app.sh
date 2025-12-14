#!/bin/zsh

source .venv/bin/activate
cd src
export DATABASE_URI=sqlite://///Users/nomadmot/Library/CloudStorage/Dropbox/Apps/Investing/DATA/portfolio-test.db
streamlit run app.py