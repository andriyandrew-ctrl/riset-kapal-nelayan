import streamlit as st

# Kode untuk menyembunyikan menu GitHub
hide_github_icon = """
    <style>
    .viewerBadge_container__1QS1n {
        display: none !important;
    }
    #MainMenu {
        visibility: hidden;
    }
    footer {
        visibility: hidden;
    }
    header {
        visibility: hidden;
    }
    </style>
"""
st.markdown(hide_github_icon, unsafe_allow_html=True)
