import streamlit as st
import streamlit.components.v1 as components

def inject_ga(ga_id):
    ga_js = f"""
        <script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){{dataLayer.push(arguments);}}
            gtag('js', new Date());
            gtag('config', '{ga_id}');
        </script>
    """
    # This injects the script into the app
    components.html(ga_js, height=0, width=0)