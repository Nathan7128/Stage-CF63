import streamlit as st

def func_change(key1, key2) :
    st.session_state[key1] = st.session_state[key2]