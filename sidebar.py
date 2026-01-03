import streamlit as st
from src.utils.navigation import render_sidebar

# This is a convenience redirect for the sidebar component.
# The main sidebar logic resides in src/utils/navigation.py
# Use the function below in your main streamlit app.

def show_sidebar():
    render_sidebar()
